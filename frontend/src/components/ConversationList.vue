<template>
  <div class="conv-list-container">
    <div v-if="conversations.length === 0" class="empty-state">
      <div class="empty-state-icon">💬</div>
      <h4>No conversations ingested yet</h4>
      <p>Use the "Ingest Chat" button in the navigation bar to send your first customer dialogue!</p>
    </div>

    <div v-else class="table-wrapper">
      <table class="conv-table">
        <thead>
          <tr>
            <th>Conversation ID</th>
            <th>Date & Time</th>
            <th>Messages</th>
            <th>NLP Status</th>
            <th class="text-right">Action</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in conversations"
            :key="item.id"
            @click="goToDetail(item.id)"
            class="conv-row"
          >
            <td class="id-cell">
              <div class="id-wrapper" @click.stop>
                <code class="id-text">{{ item.id.slice(0, 10) }}...{{ item.id.slice(-4) }}</code>
                <button
                  class="copy-btn"
                  @click="copyId(item.id)"
                  :title="copiedId === item.id ? 'Copied!' : 'Copy UUID'"
                >
                  <span v-if="copiedId === item.id" class="copied-check">✓</span>
                  <svg v-else width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                  </svg>
                </button>
              </div>
            </td>
            <td class="date-cell">
              <span class="formatted-date">{{ formatDate(item.created_at) }}</span>
            </td>
            <td class="count-cell">
              <span class="msg-pill">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                {{ item.message_count }}
              </span>
            </td>
            <td class="status-cell">
              <span :class="['status-badge', item.status]">
                {{ item.status }}
              </span>
            </td>
            <td class="text-right action-cell">
              <span class="details-link">
                Inspect
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="9 18 15 12 9 6"></polyline>
                </svg>
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination Controls -->
    <div v-if="conversations.length > 0" class="pagination-bar">
      <div class="pagination-info">
        <span>Showing page <strong>{{ page }}</strong></span>
      </div>
      <div class="pagination-buttons">
        <button
          class="btn btn-secondary btn-sm"
          :disabled="page <= 1"
          @click="$emit('change-page', page - 1)"
        >
          &larr; Previous
        </button>
        <span class="page-indicator">{{ page }}</span>
        <button
          class="btn btn-secondary btn-sm"
          :disabled="!hasMore"
          @click="$emit('change-page', page + 1)"
        >
          Next &rarr;
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const props = defineProps({
  conversations: { type: Array, default: () => [] },
  page: { type: Number, default: 1 },
  hasMore: { type: Boolean, default: false },
});

defineEmits(["change-page"]);

const router = useRouter();
const copiedId = ref(null);

function goToDetail(id) {
  router.push({ name: "conversation-detail", params: { id } });
}

function formatDate(dateStr) {
  if (!dateStr) return "-";
  const d = new Date(dateStr);
  return d.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

async function copyId(id) {
  try {
    await navigator.clipboard.writeText(id);
    copiedId.value = id;
    setTimeout(() => {
      if (copiedId.value === id) copiedId.value = null;
    }, 2000);
  } catch (err) {
    console.error("Failed to copy:", err);
  }
}
</script>

<style scoped>
.conv-list-container {
  width: 100%;
}

.table-wrapper {
  overflow-x: auto;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
}

.conv-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 0.88rem;
}

.conv-table th {
  background: rgba(13, 19, 31, 0.95);
  color: var(--text-dim);
  font-weight: 600;
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-subtle);
  text-align: left;
}

.conv-table td {
  padding: 14px 16px;
  border-bottom: 1px solid var(--border-subtle);
  color: var(--text-main);
  vertical-align: middle;
}

.conv-row {
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.conv-row:hover {
  background: rgba(255, 255, 255, 0.035);
}

.conv-row:last-child td {
  border-bottom: none;
}

.id-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.id-text {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: #c7d2fe;
}

.copy-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--text-dim);
  padding: 3px 5px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: all 0.15s ease;
}

.copy-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-main);
}

.copied-check {
  color: #10b981;
  font-weight: bold;
  font-size: 0.75rem;
}

.date-cell {
  color: var(--text-muted);
  font-size: 0.82rem;
  white-space: nowrap;
}

.msg-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  padding: 3px 8px;
  border-radius: var(--radius-full);
  font-size: 0.78rem;
  color: var(--text-muted);
}

.text-right {
  text-align: right;
}

.details-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--accent-primary);
  opacity: 0.8;
  transition: opacity 0.15s ease;
}

.conv-row:hover .details-link {
  opacity: 1;
}

.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 18px;
  padding: 4px 2px;
}

.pagination-info {
  font-size: 0.82rem;
  color: var(--text-dim);
}

.pagination-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.8rem;
}

.page-indicator {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: var(--radius-sm);
  color: var(--text-bright);
}

.empty-state {
  text-align: center;
  padding: 48px 24px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-md);
  border: 1px dashed var(--border-subtle);
}

.empty-state-icon {
  font-size: 2.5rem;
  margin-bottom: 12px;
}

.empty-state h4 {
  font-size: 1.1rem;
  margin-bottom: 6px;
  color: var(--text-bright);
}

.empty-state p {
  font-size: 0.88rem;
  color: var(--text-dim);
  max-width: 400px;
  margin: 0 auto;
}
</style>