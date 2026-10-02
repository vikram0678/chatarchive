<template>
  <div class="detail-page">
    <header class="detail-header-bar">
      <div class="header-container">
        <router-link to="/" class="back-link">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          <span>Back to Dashboard</span>
        </router-link>

        <div v-if="conversation" class="header-meta">
          <div class="uuid-badge">
            <span class="uuid-label">Thread:</span>
            <code class="uuid-val">{{ conversation.id }}</code>
            <button class="copy-btn" @click="copyUuid" :title="copied ? 'Copied!' : 'Copy UUID'">
              <span v-if="copied" class="copied-text">✓ Copied</span>
              <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="detail-content">
      <!-- Loading State -->
      <div v-if="loading" class="detail-loading glass-card">
        <div class="spin-icon">⏳</div>
        <p>Retrieving conversation and NLP insights...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="detail-error glass-card">
        <p>⚠️ {{ error }}</p>
        <router-link to="/" class="btn btn-secondary">Return to Dashboard</router-link>
      </div>

      <!-- Main Split View -->
      <div v-else-if="conversation" class="split-view-grid">
        <!-- Left: Chat Transcript Messenger -->
        <section class="transcript-pane glass-card">
          <div class="pane-header">
            <div class="pane-title-group">
              <div class="pane-icon indigo">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
              </div>
              <div>
                <h3>Dialogue Transcript</h3>
                <p class="pane-subtitle">{{ conversation.messages.length }} messages exchanged</p>
              </div>
            </div>
          </div>

          <!-- Message Bubbles Container -->
          <div class="chat-thread">
            <div
              v-for="msg in conversation.messages"
              :key="msg.id"
              :class="['message-bubble-wrapper', isCustomer(msg.sender) ? 'from-customer' : 'from-agent']"
            >
              <div class="sender-avatar">
                <span v-if="isCustomer(msg.sender)">👤</span>
                <span v-else>🎧</span>
              </div>

              <div class="bubble-content">
                <div class="bubble-meta">
                  <span class="bubble-sender">{{ formatSender(msg.sender) }}</span>
                  <span class="bubble-time">{{ formatTime(msg.timestamp) }}</span>
                </div>
                <div class="bubble-text">
                  {{ msg.text }}
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Right: AI Intelligence Hub -->
        <aside class="insights-pane glass-card">
          <div class="pane-header">
            <div class="pane-title-group">
              <div class="pane-icon violet">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
                </svg>
              </div>
              <div>
                <h3>AI Insights & Intelligence</h3>
                <p class="pane-subtitle">spaCy, VADER & MiniLM embeddings</p>
              </div>
            </div>
            <span :class="['status-badge', conversation.analysis?.status || 'pending']">
              {{ conversation.analysis?.status || 'pending' }}
            </span>
          </div>

          <!-- Completed NLP State -->
          <div v-if="conversation.analysis?.status === 'completed' && conversation.analysis?.insights" class="insights-stack">
            <!-- 1. Executive Summary -->
            <div class="insight-card">
              <div class="insight-card-title">
                <span>📝 Extractive Summary</span>
                <button class="copy-small-btn" @click="copySummary" title="Copy Summary">Copy</button>
              </div>
              <blockquote class="summary-quote">
                "{{ conversation.analysis.insights.summary }}"
              </blockquote>
            </div>

            <!-- 2. Sentiment Polarity -->
            <div class="insight-card">
              <div class="insight-card-title">
                <span>❤️ Sentiment Analysis</span>
              </div>
              <div class="sentiment-box">
                <span :class="['sentiment-pill', conversation.analysis.insights.sentiment]">
                  {{ conversation.analysis.insights.sentiment }}
                </span>
                <span class="sentiment-note">Evaluated via VADER compound score</span>
              </div>
            </div>

            <!-- 3. Named Entities (NER) -->
            <div class="insight-card">
              <div class="insight-card-title">
                <span>🏷️ Named Entities (NER)</span>
              </div>
              <div v-if="conversation.analysis.insights.entities?.length" class="tag-cloud">
                <span
                  v-for="ent in conversation.analysis.insights.entities"
                  :key="ent"
                  class="entity-chip"
                >
                  {{ ent }}
                </span>
              </div>
              <p v-else class="no-items-text">No distinct organizations, persons, or products detected.</p>
            </div>

            <!-- 4. Key Phrases -->
            <div class="insight-card">
              <div class="insight-card-title">
                <span>🔑 Key Phrases & Topics</span>
              </div>
              <div v-if="conversation.analysis.insights.key_phrases?.length" class="tag-cloud">
                <span
                  v-for="phrase in conversation.analysis.insights.key_phrases"
                  :key="phrase"
                  class="phrase-chip"
                >
                  {{ phrase }}
                </span>
              </div>
              <p v-else class="no-items-text">No noun phrases detected.</p>
            </div>

            <!-- 5. Qdrant Vector Status -->
            <div class="vector-status-card">
              <div class="vector-icon">⚡</div>
              <div class="vector-text">
                <span class="vector-title">Vector Indexed in Qdrant</span>
                <span class="vector-sub">384-dimensional vector embedding ready for semantic similarity search.</span>
              </div>
            </div>
          </div>

          <!-- Processing State -->
          <div v-else-if="conversation.analysis?.status === 'processing' || conversation.analysis?.status === 'pending'" class="pending-box">
            <div class="spin-icon large">⚙️</div>
            <h4>Background NLP in progress...</h4>
            <p>Celery is extracting sentiment, entities, and generating vector embeddings. This view refreshes automatically.</p>
          </div>

          <!-- Failed State -->
          <div v-else class="failed-box">
            <div class="failed-icon">❌</div>
            <h4>Analysis Failed</h4>
            <p>An unexpected error occurred during NLP task execution. Check Celery worker logs for details.</p>
          </div>
        </aside>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { getConversationDetail } from "../services/api";

const props = defineProps({
  id: { type: String, required: true },
});

const conversation = ref(null);
const loading = ref(true);
const error = ref(null);
const copied = ref(false);
let refreshTimer = null;

function isCustomer(sender) {
  return sender.toLowerCase().includes("customer") || sender.toLowerCase().includes("user");
}

function formatSender(sender) {
  if (isCustomer(sender)) return "Customer";
  if (sender.toLowerCase().includes("agent")) return "Support Agent";
  return sender;
}

function formatTime(timestamp) {
  if (!timestamp) return "";
  const d = new Date(timestamp);
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

async function loadDetail(silent = false) {
  if (!silent) loading.value = true;
  error.value = null;

  try {
    const res = await getConversationDetail(props.id);
    conversation.value = res.data;
  } catch (err) {
    console.error("Detail error:", err);
    error.value = "Unable to load conversation thread. It may not exist.";
  } finally {
    loading.value = false;
  }
}

async function copyUuid() {
  try {
    await navigator.clipboard.writeText(conversation.value.id);
    copied.value = true;
    setTimeout(() => {
      copied.value = false;
    }, 2000);
  } catch (err) {
    console.error(err);
  }
}

async function copySummary() {
  const summary = conversation.value?.analysis?.insights?.summary;
  if (summary) {
    await navigator.clipboard.writeText(summary);
  }
}

onMounted(() => {
  loadDetail();

  // If still processing, check every 3 seconds until completed
  refreshTimer = setInterval(() => {
    const status = conversation.value?.analysis?.status;
    if (status === "pending" || status === "processing") {
      loadDetail(true);
    }
  }, 3000);
});

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer);
});
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.detail-header-bar {
  background: rgba(10, 14, 23, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border-subtle);
  padding: 14px 0;
  position: sticky;
  top: 0;
  z-index: 40;
}

.header-container {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--text-muted);
  font-size: 0.88rem;
  font-weight: 600;
  text-decoration: none;
}
.back-link:hover {
  color: var(--accent-primary);
}

.uuid-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  padding: 5px 12px;
  border-radius: var(--radius-full);
}

.uuid-label {
  font-size: 0.76rem;
  color: var(--text-dim);
}

.uuid-val {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  color: #c7d2fe;
}

.copy-btn {
  background: none;
  border: none;
  color: var(--text-dim);
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 2px 4px;
}
.copy-btn:hover {
  color: var(--text-main);
}

.copied-text {
  color: #10b981;
  font-size: 0.75rem;
  font-weight: bold;
}

.detail-content {
  flex: 1;
  max-width: var(--max-width);
  width: 100%;
  margin: 0 auto;
  padding: 24px;
}

.detail-loading,
.detail-error {
  padding: 48px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.split-view-grid {
  display: grid;
  grid-template-columns: 1.35fr 1fr;
  gap: 24px;
  align-items: start;
}

.transcript-pane,
.insights-pane {
  padding: 22px;
}

.pane-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-subtle);
}

.pane-title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pane-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}
.pane-icon.indigo {
  background: rgba(99, 102, 241, 0.12);
  color: #818cf8;
  border: 1px solid rgba(99, 102, 241, 0.25);
}
.pane-icon.violet {
  background: rgba(139, 92, 246, 0.12);
  color: #a78bfa;
  border: 1px solid rgba(139, 92, 246, 0.25);
}

.pane-subtitle {
  font-size: 0.78rem;
  color: var(--text-dim);
}

/* Chat Thread Bubbles */
.chat-thread {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 650px;
  overflow-y: auto;
  padding-right: 6px;
}

.message-bubble-wrapper {
  display: flex;
  gap: 12px;
  max-width: 82%;
}

.message-bubble-wrapper.from-customer {
  align-self: flex-start;
}

.message-bubble-wrapper.from-agent {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.sender-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  flex-shrink: 0;
}

.from-agent .sender-avatar {
  background: rgba(99, 102, 241, 0.2);
  border-color: rgba(99, 102, 241, 0.4);
}

.bubble-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.bubble-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.74rem;
}

.from-agent .bubble-meta {
  justify-content: flex-end;
}

.bubble-sender {
  font-weight: 600;
  color: var(--text-dim);
}

.bubble-time {
  color: var(--text-dim);
}

.bubble-text {
  padding: 12px 16px;
  border-radius: 14px;
  font-size: 0.9rem;
  line-height: 1.5;
}

.from-customer .bubble-text {
  background: #1a2234;
  color: var(--text-main);
  border: 1px solid var(--border-subtle);
  border-top-left-radius: 2px;
}

.from-agent .bubble-text {
  background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
  color: #ffffff;
  border-top-right-radius: 2px;
  box-shadow: 0 4px 14px rgba(79, 70, 229, 0.25);
}

/* Insights Stack */
.insights-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.insight-card {
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.insight-card-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--text-bright);
}

.copy-small-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-subtle);
  color: var(--text-dim);
  font-size: 0.72rem;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  cursor: pointer;
}
.copy-small-btn:hover {
  color: var(--text-main);
  background: rgba(255, 255, 255, 0.1);
}

.summary-quote {
  font-style: italic;
  font-size: 0.88rem;
  color: #e2e8f0;
  line-height: 1.6;
  border-left: 3px solid var(--accent-primary);
  padding-left: 12px;
  margin: 0;
}

.sentiment-box {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sentiment-note {
  font-size: 0.76rem;
  color: var(--text-dim);
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.entity-chip {
  background: rgba(139, 92, 246, 0.12);
  border: 1px solid rgba(139, 92, 246, 0.3);
  color: #c4b5fd;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: 0.78rem;
  font-weight: 500;
}

.phrase-chip {
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.25);
  color: #a5b4fc;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: 0.78rem;
}

.vector-status-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(16, 185, 129, 0.06);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: var(--radius-md);
  padding: 12px 14px;
}

.vector-icon {
  font-size: 1.2rem;
}

.vector-text {
  display: flex;
  flex-direction: column;
}

.vector-title {
  font-size: 0.82rem;
  font-weight: 600;
  color: #34d399;
}

.vector-sub {
  font-size: 0.74rem;
  color: var(--text-dim);
}

.no-items-text {
  font-size: 0.8rem;
  color: var(--text-dim);
  font-style: italic;
}

.pending-box,
.failed-box {
  text-align: center;
  padding: 32px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.spin-icon.large {
  font-size: 2rem;
}

.failed-icon {
  font-size: 2rem;
}

@media (max-width: 900px) {
  .split-view-grid {
    grid-template-columns: 1fr;
  }
}
</style>