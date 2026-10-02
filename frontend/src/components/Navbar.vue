<template>
  <header class="app-navbar">
    <div class="navbar-container">
      <div class="brand-group">
        <router-link to="/" class="brand-link">
          <div class="brand-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              <path d="M8 9h8"></path>
              <path d="M8 13h5"></path>
            </svg>
          </div>
          <div class="brand-text">
            <span class="brand-name">ChatArchive</span>
            <span class="brand-tag">Intelligence Platform</span>
          </div>
        </router-link>
      </div>

      <div class="navbar-center">
        <div class="system-status-pill" :class="{ connected: isHealthy }">
          <span class="status-indicator"></span>
          <span class="status-label">{{ isHealthy ? 'Engine Connected' : 'Checking Engine...' }}</span>
        </div>
        <div class="tech-badge">
          <span class="tech-dot"></span>
          <span>Qdrant MiniLM-L6</span>
        </div>
      </div>

      <div class="navbar-actions">
        <button class="btn btn-secondary btn-icon" @click="$emit('refresh')" title="Refresh Data">
          <svg :class="{ 'spin-icon': refreshing }" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.19"/>
          </svg>
          <span>Refresh</span>
        </button>

        <button class="btn btn-primary" @click="$emit('open-ingest')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          <span>Ingest Chat</span>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
defineProps({
  isHealthy: { type: Boolean, default: true },
  refreshing: { type: Boolean, default: false }
});

defineEmits(['refresh', 'open-ingest']);
</script>

<style scoped>
.app-navbar {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(10, 14, 23, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border-subtle);
  padding: 12px 0;
}

.navbar-container {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.brand-group {
  display: flex;
  align-items: center;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
}

.brand-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-family: var(--font-heading);
  font-size: 1.2rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-tag {
  font-size: 0.72rem;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 600;
}

.navbar-center {
  display: flex;
  align-items: center;
  gap: 12px;
}

.system-status-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  padding: 6px 14px;
  border-radius: var(--radius-full);
  font-size: 0.78rem;
  color: var(--text-muted);
}

.status-indicator {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #f59e0b;
}

.system-status-pill.connected .status-indicator {
  background: #10b981;
  box-shadow: 0 0 8px #10b981;
}

.tech-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.2);
  padding: 5px 12px;
  border-radius: var(--radius-full);
  font-size: 0.76rem;
  color: #a5b4fc;
  font-weight: 500;
}

.tech-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #818cf8;
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

@media (max-width: 768px) {
  .navbar-center {
    display: none;
  }
}
</style>
