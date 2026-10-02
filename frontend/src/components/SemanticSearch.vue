<template>
  <div class="search-section glass-card">
    <div class="search-header">
      <div class="search-title-wrap">
        <div class="search-icon-badge">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
        </div>
        <div>
          <h3>Semantic Vector Search</h3>
          <p class="search-desc">Query conversations by meaning via Qdrant 384-dim embeddings</p>
        </div>
      </div>
      <span class="engine-tag">sentence-transformers/all-MiniLM-L6-v2</span>
    </div>

    <!-- Search Input Bar -->
    <div class="search-input-wrapper">
      <svg class="input-search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8"></circle>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
      </svg>
      <input
        v-model="query"
        @keyup.enter="runSearch"
        type="text"
        placeholder="Try searching 'money back issue' or 'delayed shipment parcel'..."
        class="search-input"
      />
      <button v-if="query" class="clear-btn" @click="clearSearch" title="Clear search">
        &times;
      </button>
      <button class="btn btn-primary search-submit-btn" @click="runSearch" :disabled="loading || !query.trim()">
        <span v-if="loading" class="spin-icon">🔄</span>
        <span v-else>Search</span>
      </button>
    </div>

    <!-- Quick Query Suggestions -->
    <div class="quick-prompts">
      <span class="prompt-label">Try asking:</span>
      <button
        v-for="prompt in suggestedPrompts"
        :key="prompt"
        type="button"
        class="prompt-chip"
        @click="applyPrompt(prompt)"
      >
        {{ prompt }}
      </button>
    </div>

    <!-- Results Section -->
    <div v-if="loading" class="results-loading">
      <div class="skeleton-card" v-for="n in 2" :key="n"></div>
    </div>

    <div v-else-if="results.length > 0" class="results-container">
      <div class="results-meta">
        <span>Found <strong>{{ results.length }}</strong> semantic matches for "<em>{{ lastQuery }}</em>"</span>
      </div>

      <div class="results-grid">
        <div
          v-for="r in results"
          :key="r.conversation_id"
          class="result-card"
          @click="goToDetail(r.conversation_id)"
        >
          <div class="result-top">
            <div class="conv-id-wrap">
              <span class="id-label">ID:</span>
              <code class="conv-id">{{ r.conversation_id.slice(0, 13) }}...</code>
            </div>
            <span :class="['status-badge', r.status]">{{ r.status }}</span>
          </div>

          <!-- Similarity Score Meter -->
          <div class="similarity-section">
            <div class="score-row">
              <span class="score-label">Similarity Match</span>
              <span class="score-value">{{ (r.score * 100).toFixed(1) }}%</span>
            </div>
            <div class="score-bar-bg">
              <div
                class="score-bar-fill"
                :style="{ width: `${Math.min(100, Math.max(10, r.score * 100))}%` }"
              ></div>
            </div>
          </div>

          <div class="result-bottom">
            <span class="msg-count-tag">
              💬 {{ r.message_count }} {{ r.message_count === 1 ? 'message' : 'messages' }}
            </span>
            <span class="view-link">View Thread &rarr;</span>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="searched && !loading" class="no-results">
      <p>🔍 No semantic matches found for "<em>{{ lastQuery }}</em>". Try different terms or ingest more conversations.</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { searchConversations } from "../services/api";

const router = useRouter();

const query = ref("");
const lastQuery = ref("");
const results = ref([]);
const loading = ref(false);
const searched = ref(false);

const suggestedPrompts = [
  "money back issue",
  "broken damaged screen",
  "shipping tracking delay",
  "helpful customer service"
];

function applyPrompt(prompt) {
  query.value = prompt;
  runSearch();
}

function clearSearch() {
  query.value = "";
  results.value = [];
  searched.value = false;
  lastQuery.value = "";
}

async function runSearch() {
  if (!query.value.trim()) return;
  loading.value = true;
  searched.value = true;
  lastQuery.value = query.value.trim();

  try {
    const res = await searchConversations(query.value.trim(), 6);
    results.value = res.data.results || [];
  } catch (err) {
    console.error("Search failed:", err);
    results.value = [];
  } finally {
    loading.value = false;
  }
}

function goToDetail(id) {
  router.push({ name: "conversation-detail", params: { id } });
}
</script>

<style scoped>
.search-section {
  padding: 24px;
  margin-bottom: 28px;
}

.search-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  gap: 16px;
}

.search-title-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-icon-badge {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  background: var(--accent-gradient-subtle);
  border: 1px solid var(--border-glow);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-primary);
}

.search-desc {
  font-size: 0.82rem;
  color: var(--text-dim);
}

.engine-tag {
  font-size: 0.72rem;
  font-family: var(--font-mono);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  padding: 4px 10px;
  border-radius: var(--radius-full);
  color: var(--text-dim);
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
}

.input-search-icon {
  position: absolute;
  left: 14px;
  color: var(--text-dim);
  pointer-events: none;
}

.search-input {
  flex: 1;
  background: rgba(13, 19, 31, 0.9);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 13px 44px;
  font-size: 0.95rem;
  color: var(--text-main);
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}

.clear-btn {
  position: absolute;
  right: 125px;
  background: none;
  border: none;
  color: var(--text-dim);
  font-size: 1.4rem;
  line-height: 1;
  cursor: pointer;
  padding: 4px 8px;
}
.clear-btn:hover {
  color: var(--text-main);
}

.search-submit-btn {
  padding: 13px 22px;
}

.quick-prompts {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.prompt-label {
  font-size: 0.76rem;
  color: var(--text-dim);
  font-weight: 500;
}

.prompt-chip {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-full);
  padding: 4px 12px;
  font-size: 0.76rem;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.prompt-chip:hover {
  background: rgba(99, 102, 241, 0.1);
  border-color: rgba(99, 102, 241, 0.35);
  color: #c7d2fe;
}

.results-loading {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
  margin-top: 20px;
}

.skeleton-card {
  height: 110px;
  background: linear-gradient(90deg, rgba(255,255,255,0.02) 25%, rgba(255,255,255,0.06) 50%, rgba(255,255,255,0.02) 75%);
  background-size: 200% 100%;
  animation: skeleton-glow 1.5s infinite;
  border-radius: var(--radius-md);
}

@keyframes skeleton-glow {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.results-container {
  margin-top: 22px;
}

.results-meta {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 14px;
}

.result-card {
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--border-glow);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

.result-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.conv-id-wrap {
  display: flex;
  align-items: center;
  gap: 6px;
}

.id-label {
  font-size: 0.74rem;
  color: var(--text-dim);
}

.conv-id {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  color: #c7d2fe;
}

.similarity-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.score-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.78rem;
}

.score-label {
  color: var(--text-dim);
}

.score-value {
  font-weight: 700;
  color: #34d399;
}

.score-bar-bg {
  height: 6px;
  width: 100%;
  background: rgba(255, 255, 255, 0.06);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.score-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1 0%, #10b981 100%);
  border-radius: var(--radius-full);
  transition: width 0.4s ease;
}

.result-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 10px;
}

.msg-count-tag {
  font-size: 0.76rem;
  color: var(--text-muted);
}

.view-link {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--accent-primary);
}

.no-results {
  margin-top: 20px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-md);
  text-align: center;
  font-size: 0.88rem;
}

@media (max-width: 640px) {
  .search-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .clear-btn {
    right: 110px;
  }
}
</style>