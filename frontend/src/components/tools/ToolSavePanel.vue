<script setup>
import AccountSyncPanel from './AccountSyncPanel.vue'

defineProps({
  title: {
    type: String,
    required: true
  },
  kicker: {
    type: String,
    default: '保存'
  },
  status: {
    type: String,
    default: ''
  },
  saveLabel: {
    type: String,
    default: '保存'
  },
  saveAsLabel: {
    type: String,
    default: ''
  },
  saveDisabled: {
    type: Boolean,
    default: false
  },
  saveAsDisabled: {
    type: Boolean,
    default: false
  },
  helper: {
    type: String,
    default: ''
  },
  authenticated: {
    type: Boolean,
    required: true
  },
  authLoading: {
    type: Boolean,
    default: false
  },
  syncLabel: {
    type: String,
    required: true
  },
  syncDescription: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['save', 'save-as', 'login'])
</script>

<template>
  <article class="tool-save-panel">
    <div class="tool-save-panel-topline">
      <div class="tool-save-heading">
        <div class="section-kicker">{{ kicker }}</div>
        <h2 class="bench-title">{{ title }}</h2>
      </div>
      <span
        v-if="status"
        class="tool-save-status"
      >
        {{ status }}
      </span>
    </div>

    <slot />

    <div class="tool-save-actions">
      <button
        class="tool-save-primary-action"
        type="button"
        :disabled="saveDisabled"
        @click="emit('save')"
      >
        {{ saveLabel }}
      </button>
      <button
        v-if="saveAsLabel"
        class="tool-save-ghost-action"
        type="button"
        :disabled="saveAsDisabled"
        @click="emit('save-as')"
      >
        {{ saveAsLabel }}
      </button>
      <slot name="actions" />
    </div>

    <p
      v-if="helper"
      class="tool-save-helper"
    >
      {{ helper }}
    </p>

    <AccountSyncPanel
      :authenticated="authenticated"
      :loading="authLoading"
      :label="syncLabel"
      :description="syncDescription"
      @login="emit('login')"
    />
  </article>
</template>

<style scoped>
.tool-save-panel {
  background: var(--shell-panel);
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-radius: var(--brand-radius-lg, 24px);
  box-shadow: var(--brand-shadow-card, var(--shell-shadow));
  min-width: 0;
  padding: 22px;
}

.tool-save-panel-topline {
  align-items: center;
  display: flex;
  gap: 12px;
  justify-content: space-between;
}

.tool-save-heading {
  flex: 1 1 auto;
  min-width: 7rem;
}

.tool-save-heading .section-kicker,
.tool-save-heading .bench-title {
  word-break: keep-all;
}

.tool-save-heading .bench-title {
  display: inline-block;
  line-height: 1.2;
  min-width: 0;
  margin: 8px 0 0;
  white-space: nowrap;
}

.tool-save-status,
.tool-save-helper {
  color: rgba(15, 23, 35, 0.62);
  font-size: 0.9rem;
}

.tool-save-status {
  flex: 0 1 auto;
  max-width: 52%;
  text-align: right;
}

.tool-save-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
}

.tool-save-primary-action,
.tool-save-ghost-action {
  align-items: center;
  border-radius: var(--brand-radius-pill, 999px);
  cursor: pointer;
  display: inline-flex;
  font: inherit;
  font-weight: 800;
  justify-content: center;
}

.tool-save-primary-action {
  background: var(--brand-color-accent, #102542);
  border: 0;
  color: #ffffff;
  min-height: 46px;
  padding: 0 18px;
}

.tool-save-ghost-action {
  background: rgba(255, 255, 255, 0.62);
  border: 1px solid var(--shell-line);
  color: var(--shell-navy);
  font-size: 0.88rem;
  gap: 8px;
  min-height: 38px;
  padding: 0 13px;
  text-decoration: none;
}

.tool-save-ghost-action:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(16, 37, 66, 0.18);
}

.tool-save-primary-action:disabled,
.tool-save-ghost-action:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

.tool-save-helper {
  line-height: 1.6;
  margin: 14px 0 0;
}

@media (max-width: 599px) {
  .tool-save-panel {
    padding: 18px;
  }

  .tool-save-panel-topline {
    align-items: flex-start;
    flex-direction: column;
  }

  .tool-save-status {
    max-width: none;
    text-align: left;
  }
}
</style>
