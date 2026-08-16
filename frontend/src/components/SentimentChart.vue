<template>
  <Pie v-if="hasData" :data="chartData" :options="chartOptions" />
  <p v-else>No completed conversations yet to chart.</p>
</template>

<script setup>
import { computed } from "vue";
import { Pie } from "vue-chartjs";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from "chart.js";

ChartJS.register(Title, Tooltip, Legend, ArcElement);

const props = defineProps({
  conversations: { type: Array, default: () => [] },
});

const sentimentCounts = computed(() => {
  const counts = { Positive: 0, Negative: 0, Neutral: 0 };
  props.conversations.forEach((c) => {
    if (c.sentiment && counts[c.sentiment] !== undefined) {
      counts[c.sentiment]++;
    }
  });
  return counts;
});

const hasData = computed(() =>
  Object.values(sentimentCounts.value).some((v) => v > 0)
);

const chartData = computed(() => ({
  labels: Object.keys(sentimentCounts.value),
  datasets: [
    {
      backgroundColor: ["#22c55e", "#ef4444", "#94a3b8"],
      data: Object.values(sentimentCounts.value),
    },
  ],
}));

const chartOptions = { responsive: true };
</script>