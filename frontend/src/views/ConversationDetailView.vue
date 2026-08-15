<template>
  <div class="detail-view">
    <router-link to="/">&larr; Back to Dashboard</router-link>

    <p v-if="loading">Loading...</p>
    <p v-else-if="error">{{ error }}</p>

    <div v-else class="split-pane">
      <!-- Left: raw transcript -->
      <div class="pane transcript">
        <h2>Transcript</h2>
        <div v-for="msg in conversation.messages" :key="msg.id" class="message">
          <strong>{{ msg.sender }}:</strong> {{ msg.text }}
        </div>
      </div>

      <!-- Right: insights -->
      <div class="pane insights">
        <h2>Insights</h2>

        <div class="card">
          <h3>Status</h3>
          <span :class="['status-badge', conversation.analysis.status]">
            {{ conversation.analysis.status }}
          </span>
        </div>

        <template v-if="conversation.analysis.status === 'completed'">
          <div class="card">
            <h3>Summary</h3>
            <p>{{ conversation.analysis.insights.summary }}</p>
          </div>

          <div class="card">
            <h3>Sentiment</h3>
            <span :class="['sentiment-badge', conversation.analysis.insights.sentiment]">
              {{ conversation.analysis.insights.sentiment }}
            </span>
          </div>

          <div class="card">
            <h3>Entities</h3>
            <span
              v-for="e in conversation.analysis.insights.entities"
              :key="e"
              class="tag"
            >
              {{ e }}
            </span>
          </div>

          <div class="card">
            <h3>Key Phrases</h3>
            <span
              v-for="p in conversation.analysis.insights.key_phrases"
              :key="p"
              class="tag"
            >
              {{ p }}
            </span>
          </div>
        </template>

        <p v-else-if="conversation.analysis.status === 'failed'">
          Analysis failed for this conversation.
        </p>
        <p v-else>Analysis is still processing — check back shortly.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getConversationDetail } from "../services/api";

const props = defineProps({ id: String });

const conversation = ref(null);
const loading = ref(true);
const error = ref(null);

async function loadDetail() {
  loading.value = true;
  error.value = null;
  try {
    const res = await getConversationDetail(props.id);
    conversation.value = res.data;
  } catch (err) {
    error.value = "Conversation not found.";
    console.error(err);
  } finally {
    loading.value = false;
  }
}

onMounted(loadDetail);
</script>

<style scoped>
.detail-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}
.split-pane {
  display: flex;
  gap: 30px;
  margin-top: 20px;
}
.pane {
  flex: 1;
}
.transcript {
  border-right: 1px solid #ddd;
  padding-right: 20px;
}
.message {
  margin-bottom: 10px;
}
.card {
  margin-bottom: 20px;
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 8px;
}
.tag {
  display: inline-block;
  background: #eef2ff;
  padding: 4px 10px;
  border-radius: 12px;
  margin: 3px;
  font-size: 0.9em;
}
.sentiment-badge {
  padding: 4px 12px;
  border-radius: 12px;
  color: white;
}
.sentiment-badge.Positive { background: #22c55e; }
.sentiment-badge.Negative { background: #ef4444; }
.sentiment-badge.Neutral { background: #94a3b8; }
.status-badge {
  padding: 3px 10px;
  border-radius: 12px;
  color: white;
}
.status-badge.completed { background: #22c55e; }
.status-badge.pending { background: #eab308; }
.status-badge.processing { background: #3b82f6; }
.status-badge.failed { background: #ef4444; }
</style>