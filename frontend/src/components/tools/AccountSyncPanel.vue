<script setup>
import { githubLoginUrl } from 'src/lib/auth'

defineProps({
  authenticated: {
    type: Boolean,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  label: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  actionLabel: {
    type: String,
    default: '使用 GitHub 登录'
  }
})

const emit = defineEmits(['login'])
</script>

<template>
  <section
    v-if="!authenticated"
    class="account-sync-panel"
  >
    <div>
      <div class="account-sync-label">{{ label }}</div>
      <p
        v-if="description"
        class="account-sync-description"
      >
        {{ description }}
      </p>
    </div>

    <div class="account-sync-actions">
      <button
        class="account-sync-button"
        type="button"
        :disabled="loading"
        @click="emit('login')"
      >
        {{ loading ? '正在跳转...' : actionLabel }}
      </button>
      <a
        class="account-sync-link"
        :href="githubLoginUrl()"
      >
        打开登录页
      </a>
    </div>
  </section>
</template>

<style scoped>
.account-sync-panel {
  align-items: center;
  background: rgba(16, 37, 66, 0.06);
  border: 1px solid rgba(16, 37, 66, 0.08);
  border-radius: var(--brand-radius-md, 16px);
  display: grid;
  gap: 12px;
  grid-template-columns: minmax(0, 1fr) auto;
  margin-top: 14px;
  padding: 13px 15px;
}

.account-sync-label {
  color: var(--shell-navy);
  font-size: 0.9rem;
  font-weight: 800;
}

.account-sync-description {
  color: rgba(15, 23, 35, 0.66);
  font-size: 0.88rem;
  line-height: 1.55;
  margin: 5px 0 0;
}

.account-sync-actions {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
}

.account-sync-button,
.account-sync-link {
  align-items: center;
  border-radius: var(--brand-radius-pill, 999px);
  display: inline-flex;
  font: inherit;
  font-size: 0.86rem;
  font-weight: 800;
  min-height: 36px;
  padding: 0 12px;
  text-decoration: none;
}

.account-sync-button {
  background: var(--brand-color-accent, var(--shell-navy));
  border: 0;
  color: #ffffff;
  cursor: pointer;
}

.account-sync-button:focus-visible,
.account-sync-link:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
}

.account-sync-button:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

.account-sync-link {
  background: rgba(255, 255, 255, 0.66);
  border: 1px solid var(--shell-line);
  color: var(--shell-navy);
}

@media (max-width: 599px) {
  .account-sync-panel {
    align-items: flex-start;
    grid-template-columns: 1fr;
  }

  .account-sync-actions {
    justify-content: flex-start;
  }
}
</style>
