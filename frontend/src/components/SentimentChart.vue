<template>
  <div class="sentiment-widget">
    <div v-if="hasData" class="sentiment-content">
      <div class="chart-container">
        <Doughnut :data="chartData" :options="chartOptions" />
        <div class="chart-center-stat">
          <span class="center-total">{{ totalCompleted }}</span>
          <span class="center-label">Analyzed</span>
        </div>
      </div>

      <div class="sentiment-legend">
        <div class="legend-row">
          <div class="legend-info">
            <span class="legend-dot positive"></span>
            <span class="legend-name">Positive</span>
          </div>
          <div class="legend-metrics">
            <span class="legend-count">{{ sentimentCounts.Positive }}</span>
            <span class="legend-pct">{{ getPct(sentimentCounts.Positive) }}%</span>
          </div>
        </div>

        <div class="legend-row">
          <div class="legend-info">
            <span class="legend-dot neutral"></span>
            <span class="legend-name">Neutral</span>
          </div>
          <div class="legend-metrics">
            <span class="legend-count">{{ sentimentCounts.Neutral }}</span>
            <span class="legend-pct">{{ getPct(sentimentCounts.Neutral) }}%</span>
          </div>
        </div>

        <div class="legend-row">
          <div class="legend-info">
            <span class="legend-dot negative"></span>
            <span class="legend-name">Negative</span>
          </div>
          <div class="legend-metrics">
            <span class="legend-count">{{ sentimentCounts.Negative }}</span>
            <span class="legend-pct">{{ getPct(sentimentCounts.Negative) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="empty-chart">
      <div class="empty-icon">📊</div>
      <p class="empty-title">No completed conversations yet</p>
      <p class="empty-sub">Ingest conversations above to watch real-time sentiment distribution populate here.</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { Doughnut } from "vue-chartjs";
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

const totalCompleted = computed(() => {
  return (
    sentimentCounts.value.Positive +
    sentimentCounts.value.Neutral +
    sentimentCounts.value.Negative
  );
});

const hasData = computed(() => totalCompleted.value > 0);

function getPct(count) {
  if (!totalCompleted.value) return 0;
  return Math.round((count / totalCompleted.value) * 100);
}

const chartData = computed(() => ({
  labels: ["Positive", "Neutral", "Negative"],
  datasets: [
    {
      backgroundColor: ["#10b981", "#0ea5e9", "#f43f5e"],
      borderColor: "#111827",
      borderWidth: 3,
      hoverOffset: 6,
      data: [
        sentimentCounts.value.Positive,
        sentimentCounts.value.Neutral,
        sentimentCounts.value.Negative,
      ],
    },
  ],
}));

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: "74%",
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      backgroundColor: "#1e293b",
      titleColor: "#f8fafc",
      bodyColor: "#cbd5e1",
      borderColor: "rgba(255,255,255,0.1)",
      borderWidth: 1,
      padding: 10,
      cornerRadius: 8,
      callbacks: {
        label: function (context) {
          const val = context.raw || 0;
          const pct = getPct(val);
          return ` ${context.label}: ${val} (${pct}%)`;
        },
      },
    },
  },
};
</script>

<style scoped>
.sentiment-widget {
  width: 100%;
  height: 100%;
}

.sentiment-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.chart-container {
  position: relative;
  width: 180px;
  height: 180px;
}

.chart-center-stat {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  pointer-events: none;
}

.center-total {
  font-family: var(--font-heading);
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--text-bright);
  line-height: 1;
}

.center-label {
  font-size: 0.72rem;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-top: 4px;
}

.sentiment-legend {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.legend-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
}

.legend-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.legend-dot.positive { background: #10b981; }
.legend-dot.neutral { background: #0ea5e9; }
.legend-dot.negative { background: #f43f5e; }

.legend-name {
  font-size: 0.82rem;
  color: var(--text-main);
  font-weight: 500;
}

.legend-metrics {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-count {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-bright);
}

.legend-pct {
  font-size: 0.75rem;
  color: var(--text-dim);
}

.empty-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 30px 16px;
}

.empty-icon {
  font-size: 2.2rem;
  margin-bottom: 10px;
  opacity: 0.7;
}

.empty-title {
  font-weight: 600;
  color: var(--text-main);
  font-size: 0.95rem;
  margin-bottom: 6px;
}

.empty-sub {
  font-size: 0.8rem;
  color: var(--text-dim);
  max-width: 240px;
}
</style>