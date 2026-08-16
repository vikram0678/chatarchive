<template>
  <div class="search-box">
    <input
      v-model="query"
      @keyup.enter="runSearch"
      placeholder="Search by meaning, e.g. 'money back issue'"
    />
    <button @click="runSearch" :disabled="loading">
      {{ loading ? "Searching..." : "Search" }}
    </button>

    <ul v-if="results.length" class="results-list">
      <li v-for="r in results" :key="r.conversation_id" @click="goToDetail(r.conversation_id)">
        <span>{{ r.conversation_id.slice(0, 8) }}...</span>
        <span class="score">score: {{ r.score.toFixed(2) }}</span>
        <span :class="['status-badge', r.status]">{{ r.status }}</span>
      </li>
    </ul>
    <p v-else-if="searched && !loading">No matches found.</p>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { searchConversations } from "../services/api";

const query = ref("");
const results = ref([]);
const loading = ref(false);
const searched = ref(false);
const router = useRouter();

async function runSearch() {
  if (!query.value.trim()) return;
  loading.value = true;
  searched.value = true;
  try {
    const res = await searchConversations(query.value, 5);
    results.value = res.data.results;
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
.search-box {
  margin-bottom: 20px;
}
input {
  padding: 8px;
  width: 300px;
  margin-right: 8px;
}
.results-list {
  list-style: none;
  padding: 0;
  margin-top: 10px;
}
.results-list li {
  padding: 8px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  display: flex;
  gap: 15px;
}
.results-list li:hover {
  background: #f5f5f5;
}
.score {
  color: #666;
}
</style>