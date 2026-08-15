<template>
  <div class="dashboard">
    <h1>ChatArchive Dashboard</h1>

    <SemanticSearch />

    <h2>Sentiment Overview</h2>
    <div class="chart-wrap">
      <SentimentChart :conversations="sentimentSource" />
    </div>

    <h2>All Conversations</h2>
    <p v-if="loading">Loading...</p>
    <p v-else-if="error">{{ error }}</p>
    <ConversationList
      v-else
      :conversations="conversations"
      :page="page"
      :hasMore="hasMore"
      @change-page="changePage"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { getConversations, getConversationDetail } from "../services/api";
import ConversationList from "../components/ConversationList.vue";
import SemanticSearch from "../components/SemanticSearch.vue";
import SentimentChart from "../components/SentimentChart.vue";

const conversations = ref([]);
const page = ref(1);
const size = 10;
const total = ref(0);
const loading = ref(true);
const error = ref(null);
const sentimentSource = ref([]);

const hasMore = computed(() => page.value * size < total.value);

async function loadConversations() {
  loading.value = true;
  error.value = null;
  try {
    const res = await getConversations(page.value, size);
    conversations.value = res.data.items;
    total.value = res.data.total;
    await loadSentimentForChart();
  } catch (err) {
    error.value = "Failed to load conversations. Is the backend running?";
    console.error(err);
  } finally {
    loading.value = false;
  }
}

// Fetch sentiment for each completed conversation, for the pie chart.
// (Simple approach for this project's scale — fine for a handful of items.)
async function loadSentimentForChart() {
  const completed = conversations.value.filter((c) => c.status === "completed");
  const detailed = await Promise.all(
    completed.map((c) => getConversationDetail(c.id).then((r) => r.data))
  );
  sentimentSource.value = detailed.map((d) => ({
    sentiment: d.analysis?.insights?.sentiment,
  }));
}

function changePage(newPage) {
  page.value = newPage;
  loadConversations();
}

onMounted(loadConversations);
</script>

<style scoped>
.dashboard {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}
.chart-wrap {
  max-width: 300px;
  margin-bottom: 30px;
}
</style>