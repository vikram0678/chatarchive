<template>
  <div>
    <table class="conv-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Created</th>
          <th>Messages</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="item in conversations"
          :key="item.id"
          @click="goToDetail(item.id)"
          class="conv-row"
        >
          <td>{{ item.id.slice(0, 8) }}...</td>
          <td>{{ formatDate(item.created_at) }}</td>
          <td>{{ item.message_count }}</td>
          <td>
            <span :class="['status-badge', item.status]">{{ item.status }}</span>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="pagination">
      <button :disabled="page <= 1" @click="$emit('change-page', page - 1)">Prev</button>
      <span>Page {{ page }}</span>
      <button :disabled="!hasMore" @click="$emit('change-page', page + 1)">Next</button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";

const props = defineProps({
  conversations: { type: Array, default: () => [] },
  page: { type: Number, default: 1 },
  hasMore: { type: Boolean, default: false },
});

defineEmits(["change-page"]);

const router = useRouter();

function goToDetail(id) {
  router.push({ name: "conversation-detail", params: { id } });
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString();
}
</script>

<style scoped>
.conv-table {
  width: 100%;
  border-collapse: collapse;
}
.conv-table th, .conv-table td {
  padding: 10px;
  border-bottom: 1px solid #ddd;
  text-align: left;
}
.conv-row {
  cursor: pointer;
}
.conv-row:hover {
  background: #f5f5f5;
}
.status-badge {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 0.85em;
  color: white;
}
.status-badge.completed { background: #22c55e; }
.status-badge.pending { background: #eab308; }
.status-badge.processing { background: #3b82f6; }
.status-badge.failed { background: #ef4444; }
.pagination {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-top: 15px;
}
</style>