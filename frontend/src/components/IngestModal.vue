<template>
  <div v-if="isOpen" class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-dialog glass-card">
      <div class="modal-header">
        <div class="modal-title-group">
          <div class="modal-badge-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="12" y1="18" x2="12" y2="12"></line>
              <line x1="9" y1="15" x2="15" y2="15"></line>
            </svg>
          </div>
          <div>
            <h3>Ingest Conversation</h3>
            <p class="subtitle">Dispatches chat to Redis queue & Celery NLP pipeline</p>
          </div>
        </div>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>

      <div class="modal-body">
        <div class="preset-selector">
          <label class="section-label">Quick Presets</label>
          <div class="preset-buttons">
            <button
              v-for="(preset, idx) in presets"
              :key="idx"
              type="button"
              class="preset-btn"
              :class="{ active: selectedPreset === idx }"
              @click="loadPreset(idx)"
            >
              <span class="preset-tag" :class="preset.type">{{ preset.type }}</span>
              <span class="preset-name">{{ preset.title }}</span>
            </button>
          </div>
        </div>

        <div class="messages-editor">
          <div class="editor-header">
            <label class="section-label">Dialogue Sequence ({{ messages.length }} messages)</label>
            <button class="btn-text" type="button" @click="addMessage">+ Add Message</button>
          </div>

          <div class="messages-list">
            <div
              v-for="(msg, index) in messages"
              :key="index"
              class="message-row"
            >
              <div class="message-meta">
                <select v-model="msg.sender" class="sender-select">
                  <option value="customer">Customer</option>
                  <option value="agent">Agent</option>
                  <option value="system">System</option>
                </select>
                <button
                  type="button"
                  class="delete-msg-btn"
                  @click="removeMessage(index)"
                  :disabled="messages.length <= 1"
                  title="Remove message"
                >
                  &times;
                </button>
              </div>
              <textarea
                v-model="msg.text"
                rows="2"
                class="message-textarea"
                placeholder="Message text..."
              ></textarea>
            </div>
          </div>
        </div>

        <div v-if="submitError" class="error-banner">
          {{ submitError }}
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" @click="$emit('close')" :disabled="submitting">
          Cancel
        </button>
        <button class="btn btn-primary" @click="handleSubmit" :disabled="submitting || !isValid">
          <span v-if="submitting" class="spin-icon">⏳</span>
          <span v-else>🚀</span>
          <span>{{ submitting ? 'Ingesting...' : 'Ingest & Trigger NLP' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { createConversation } from "../services/api";

const props = defineProps({
  isOpen: { type: Boolean, default: false },
});

const emit = defineEmits(["close", "success"]);

const submitting = ref(false);
const submitError = ref(null);
const selectedPreset = ref(0);

const presets = [
  {
    title: "Cracked Laptop Screen",
    type: "Negative",
    messages: [
      {
        sender: "customer",
        timestamp: new Date().toISOString(),
        text: "I received my Dell XPS laptop yesterday, but the screen is completely shattered! I am extremely upset and need a full refund or immediate replacement.",
      },
      {
        sender: "agent",
        timestamp: new Date(Date.now() + 60000).toISOString(),
        text: "I apologize deeply for the condition of your delivery. I will generate a prepaid return label and process a full refund right now.",
      },
    ],
  },
  {
    title: "FedEx Delivery Inquiry",
    type: "Neutral",
    messages: [
      {
        sender: "customer",
        timestamp: new Date().toISOString(),
        text: "Hello, could you please verify where my shipment is? The FedEx tracking code shows it has been sitting in Memphis for 3 days.",
      },
      {
        sender: "agent",
        timestamp: new Date(Date.now() + 60000).toISOString(),
        text: "Hi there! Let me review the manifest with logistics. The flight was delayed due to weather, but your parcel is scheduled for delivery tomorrow afternoon.",
      },
    ],
  },
  {
    title: "Praise for Agent Support",
    type: "Positive",
    messages: [
      {
        sender: "customer",
        timestamp: new Date().toISOString(),
        text: "I just wanted to say thank you so much! Sarah from Apple customer care solved my cloud account issue in under five minutes. Outstanding support!",
      },
      {
        sender: "agent",
        timestamp: new Date(Date.now() + 60000).toISOString(),
        text: "You are so very welcome! I'll make sure Sarah gets recognition for her great work. Have a wonderful week!",
      },
    ],
  },
];

const messages = ref(JSON.parse(JSON.stringify(presets[0].messages)));

function loadPreset(index) {
  selectedPreset.value = index;
  messages.value = JSON.parse(JSON.stringify(presets[index].messages));
}

function addMessage() {
  const lastSender = messages.value[messages.value.length - 1]?.sender;
  const nextSender = lastSender === "customer" ? "agent" : "customer";
  messages.value.push({
    sender: nextSender,
    timestamp: new Date().toISOString(),
    text: "",
  });
}

function removeMessage(index) {
  if (messages.value.length > 1) {
    messages.value.splice(index, 1);
  }
}

const isValid = computed(() => {
  return messages.value.length > 0 && messages.value.every((m) => m.text.trim().length > 0);
});

async function handleSubmit() {
  if (!isValid.value) return;
  submitting.value = true;
  submitError.value = null;

  try {
    const payload = messages.value.map((m) => ({
      sender: m.sender,
      timestamp: m.timestamp || new Date().toISOString(),
      text: m.text.trim(),
    }));

    const res = await createConversation(payload);
    emit("success", res.data);
    emit("close");
  } catch (err) {
    console.error("Ingest failed:", err);
    submitError.value = err.response?.data?.detail || "Failed to ingest conversation. Check backend connection.";
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(5, 8, 15, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-dialog {
  width: 100%;
  max-width: 640px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: #111827;
  border-radius: var(--radius-lg);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
}

.modal-header {
  padding: 20px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-subtle);
}

.modal-title-group {
  display: flex;
  align-items: center;
  gap: 14px;
}

.modal-badge-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--accent-gradient-subtle);
  border: 1px solid var(--border-glow);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-primary);
}

.subtitle {
  font-size: 0.8rem;
  color: var(--text-dim);
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 1.6rem;
  line-height: 1;
  cursor: pointer;
  padding: 4px;
  border-radius: var(--radius-sm);
}

.close-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
}

.modal-body {
  padding: 20px 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-dim);
  margin-bottom: 8px;
}

.preset-buttons {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.preset-btn {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 10px;
  text-align: left;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 4px;
  transition: all 0.2s ease;
}

.preset-btn:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: var(--border-hover);
}

.preset-btn.active {
  background: rgba(99, 102, 241, 0.12);
  border-color: var(--accent-primary);
}

.preset-tag {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.preset-tag.Negative { color: #fb7185; }
.preset-tag.Neutral { color: #38bdf8; }
.preset-tag.Positive { color: #34d399; }

.preset-name {
  font-size: 0.82rem;
  color: var(--text-main);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.btn-text {
  background: none;
  border: none;
  color: var(--accent-primary);
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}
.btn-text:hover {
  text-decoration: underline;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 250px;
  overflow-y: auto;
  padding-right: 4px;
}

.message-row {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sender-select {
  background: #1e293b;
  color: var(--text-main);
  border: 1px solid var(--border-subtle);
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  font-size: 0.82rem;
  font-weight: 600;
}

.delete-msg-btn {
  background: none;
  border: none;
  color: var(--text-dim);
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0 4px;
}
.delete-msg-btn:hover:not(:disabled) {
  color: #fb7185;
}

.message-textarea {
  width: 100%;
  background: #0d131f;
  color: var(--text-main);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 8px 10px;
  font-size: 0.86rem;
  font-family: inherit;
  resize: vertical;
}

.message-textarea:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.error-banner {
  background: var(--status-negative-bg);
  border: 1px solid var(--status-negative-border);
  color: #fb7185;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--border-subtle);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 600px) {
  .preset-buttons {
    grid-template-columns: 1fr;
  }
}
</style>
