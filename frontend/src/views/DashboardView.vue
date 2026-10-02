<template>
  <div class="dashboard-page">
    <Navbar
      :isHealthy="isEngineHealthy"
      :refreshing="refreshing"
      @refresh="handleManualRefresh"
      @open-ingest="showIngestModal = true"
    />

    <main class="dashboard-content">
      <!-- Toast Alert -->
      <transition name="toast-fade">
        <div v-if="toastMessage" class="toast-banner">
          <span>✨ {{ toastMessage }}</span>
          <button class="toast-close" @click="toastMessage = null">&times;</button>
        </div>
      </transition>

      <!-- KPI Summary Cards -->
      <section class="kpi-grid">
        <div class="kpi-card glass-card">
          <div class="kpi-icon-wrap indigo">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
          </div>
          <div class="kpi-data">
            <span class="kpi-label">Total Ingested</span>
            <div class="kpi-value-row">
              <span class="kpi-value">{{ total }}</span>
              <span class="kpi-subtag">Conversations</span>
            </div>
          </div>
        </div>

        <div class="kpi-card glass-card">
          <div class="kpi-icon-wrap emerald">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
          </div>
          <div class="kpi-data">
            <span class="kpi-label">Analyzed by AI</span>
            <div class="kpi-value-row">
              <span class="kpi-value">{{ completedCount }}</span>
              <span class="kpi-badge emerald">{{ completionPct }}% done</span>
            </div>
          </div>
        </div>

        <div class="kpi-card glass-card">
          <div class="kpi-icon-wrap blue">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
          </div>
          <div class="kpi-data">
            <span class="kpi-label">Worker Queue</span>
            <div class="kpi-value-row">
              <span class="kpi-value">{{ pendingOrProcessingCount }}</span>
              <span v-if="pendingOrProcessingCount > 0" class="kpi-badge amber pulse">Processing</span>
              <span v-else class="kpi-badge gray">Idle</span>
            </div>
          </div>
        </div>

        <div class="kpi-card glass-card">
          <div class="kpi-icon-wrap violet">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
              <polyline points="2 17 12 22 22 17"></polyline>
              <polyline points="2 12 12 17 22 12"></polyline>
            </svg>
          </div>
          <div class="kpi-data">
            <span class="kpi-label">Vector Storage</span>
            <div class="kpi-value-row">
              <span class="kpi-value">384-D</span>
              <span class="kpi-subtag">Qdrant Index</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Semantic Search Section -->
      <SemanticSearch />

      <!-- Main Content Split: Left (Table) | Right (Sentiment Chart) -->
      <div class="content-split-layout">
        <section class="left-section glass-card">
          <div class="section-card-header">
            <div>
              <h3>All Conversations</h3>
              <p class="section-subtext">Historical logs, message volumes, and analysis progress</p>
            </div>
            <div class="header-actions">
              <span class="count-tag">{{ total }} items</span>
            </div>
          </div>

          <div v-if="loading && !refreshing" class="loading-state">
            <div class="spin-icon">⏳</div>
            <p>Loading conversations from PostgreSQL...</p>
          </div>

          <div v-else-if="error" class="error-state">
            <p>⚠️ {{ error }}</p>
            <button class="btn btn-secondary btn-sm" @click="loadConversations">Retry Connection</button>
          </div>

          <ConversationList
            v-else
            :conversations="conversations"
            :page="page"
            :hasMore="hasMore"
            @change-page="changePage"
          />
        </section>

        <!-- Right: Sentiment Intelligence Card -->
        <aside class="right-section glass-card">
          <div class="section-card-header">
            <div>
              <h3>Sentiment Pulse</h3>
              <p class="section-subtext">VADER polarity aggregated across threads</p>
            </div>
          </div>

          <SentimentChart :conversations="sentimentSource" />
        </aside>
      </div>
    </main>

    <!-- Ingestion Modal -->
    <IngestModal
      :isOpen="showIngestModal"
      @close="showIngestModal = false"
      @success="handleIngestSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from "vue";
import { getConversations, getConversationDetail, checkHealth } from "../services/api";
import Navbar from "../components/Navbar.vue";
import ConversationList from "../components/ConversationList.vue";
import SemanticSearch from "../components/SemanticSearch.vue";
import SentimentChart from "../components/SentimentChart.vue";
import IngestModal from "../components/IngestModal.vue";

const conversations = ref([]);
const page = ref(1);
const size = 15;
const total = ref(0);
const loading = ref(true);
const refreshing = ref(false);
const error = ref(null);
const sentimentSource = ref([]);
const isEngineHealthy = ref(true);
const showIngestModal = ref(false);
const toastMessage = ref(null);

let pollInterval = null;

const hasMore = computed(() => page.value * size < total.value);

const completedCount = computed(() => {
  return conversations.value.filter((c) => c.status === "completed").length;
});

const pendingOrProcessingCount = computed(() => {
  return conversations.value.filter(
    (c) => c.status === "pending" || c.status === "processing"
  ).length;
});

const completionPct = computed(() => {
  if (!total.value) return 0;
  return Math.round((completedCount.value / Math.min(total.value, conversations.value.length)) * 100);
});

async function checkEngineHealth() {
  try {
    const res = await checkHealth();
    isEngineHealthy.value = res.data?.status === "ok";
  } catch {
    isEngineHealthy.value = false;
  }
}

async function loadConversations(isSilent = false) {
  if (!isSilent) loading.value = true;
  error.value = null;

  try {
    const res = await getConversations(page.value, size);
    conversations.value = res.data.items || [];
    total.value = res.data.total || 0;
    await loadSentimentForChart();
  } catch (err) {
    error.value = "Failed to load conversations. Ensure FastAPI is running.";
    console.error(err);
  } finally {
    loading.value = false;
    refreshing.value = false;
  }
}

async function loadSentimentForChart() {
  const completed = conversations.value.filter((c) => c.status === "completed");
  if (!completed.length) {
    sentimentSource.value = [];
    return;
  }

  try {
    const detailed = await Promise.all(
      completed.slice(0, 15).map((c) =>
        getConversationDetail(c.id)
          .then((r) => r.data)
          .catch(() => null)
      )
    );
    sentimentSource.value = detailed
      .filter(Boolean)
      .map((d) => ({
        sentiment: d.analysis?.insights?.sentiment,
      }));
  } catch (err) {
    console.warn("Could not fetch detailed sentiments for chart:", err);
  }
}

function handleManualRefresh() {
  refreshing.value = true;
  loadConversations(true);
  checkEngineHealth();
}

function changePage(newPage) {
  page.value = newPage;
  loadConversations();
}

function handleIngestSuccess(data) {
  toastMessage.value = `Conversation ${data.conversation_id.slice(0, 8)}... sent to Celery!`;
  setTimeout(() => {
    toastMessage.value = null;
  }, 4000);
  loadConversations(true);
}

onMounted(() => {
  checkEngineHealth();
  loadConversations();

  // Gentle background poll every 6 seconds to update processing tasks
  pollInterval = setInterval(() => {
    if (pendingOrProcessingCount.value > 0) {
      loadConversations(true);
    }
  }, 6000);
});

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval);
});
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.dashboard-content {
  flex: 1;
  max-width: var(--max-width);
  width: 100%;
  margin: 0 auto;
  padding: 24px;
}

.toast-banner {
  background: var(--accent-gradient);
  color: #fff;
  padding: 12px 20px;
  border-radius: var(--radius-md);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 500;
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
}

.toast-close {
  background: none;
  border: none;
  color: #fff;
  font-size: 1.2rem;
  cursor: pointer;
}

.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: all 0.3s ease;
}
.toast-fade-enter-from,
.toast-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* KPI Cards Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.kpi-card {
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.kpi-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.kpi-icon-wrap.indigo {
  background: rgba(99, 102, 241, 0.12);
  color: #818cf8;
  border: 1px solid rgba(99, 102, 241, 0.25);
}

.kpi-icon-wrap.emerald {
  background: rgba(16, 185, 129, 0.12);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.25);
}

.kpi-icon-wrap.blue {
  background: rgba(59, 130, 246, 0.12);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.25);
}

.kpi-icon-wrap.violet {
  background: rgba(139, 92, 246, 0.12);
  color: #a78bfa;
  border: 1px solid rgba(139, 92, 246, 0.25);
}

.kpi-data {
  display: flex;
  flex-direction: column;
}

.kpi-label {
  font-size: 0.74rem;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
}

.kpi-value-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-top: 2px;
}

.kpi-value {
  font-family: var(--font-heading);
  font-size: 1.45rem;
  font-weight: 800;
  color: var(--text-bright);
}

.kpi-subtag {
  font-size: 0.76rem;
  color: var(--text-dim);
}

.kpi-badge {
  font-size: 0.7rem;
  padding: 2px 7px;
  border-radius: var(--radius-full);
  font-weight: 600;
}

.kpi-badge.emerald {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
}

.kpi-badge.amber {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
}

.kpi-badge.gray {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-dim);
}

/* Content Split Layout */
.content-split-layout {
  display: grid;
  grid-template-columns: 2.2fr 1fr;
  gap: 24px;
}

.left-section,
.right-section {
  padding: 22px;
}

.section-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 18px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-subtle);
}

.section-subtext {
  font-size: 0.8rem;
  color: var(--text-dim);
  margin-top: 2px;
}

.count-tag {
  font-size: 0.76rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  padding: 3px 10px;
  border-radius: var(--radius-full);
  color: var(--text-muted);
}

.loading-state,
.error-state {
  text-align: center;
  padding: 40px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

@media (max-width: 1024px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .content-split-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  .dashboard-content {
    padding: 16px;
  }
}
</style>