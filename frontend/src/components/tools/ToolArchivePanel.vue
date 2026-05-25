<script setup>
defineProps({
  initialized: {
    type: Boolean,
    required: true
  },
  authenticated: {
    type: Boolean,
    required: true
  },
  authLoading: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  hasItems: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '云端存档'
  },
  loadingDescription: {
    type: String,
    default: '本地功能可直接使用，登录状态只影响云端存档。'
  },
  loginDescription: {
    type: String,
    default: '登录后可把当前内容保存为云端存档，后续继续查看和编辑。'
  },
  emptyText: {
    type: String,
    default: '还没有云端存档。'
  }
})

const emit = defineEmits(['login', 'refresh'])
</script>

<template>
  <article class="tool-archive-panel">
    <template v-if="!initialized || authLoading">
      <div class="section-kicker">登录状态</div>
      <h2 class="bench-title">正在检查 GitHub 登录</h2>
      <p class="tool-archive-helper">
        {{ loadingDescription }}
      </p>
    </template>

    <template v-else-if="!authenticated">
      <div class="section-kicker">{{ title }}</div>
      <h2 class="bench-title">登录后启用{{ title }}</h2>
      <p class="tool-archive-helper">
        {{ loginDescription }}
      </p>
      <button
        class="tool-archive-primary-action tool-archive-auth-action"
        type="button"
        :disabled="authLoading"
        @click="emit('login')"
      >
        {{ authLoading ? '正在跳转...' : '使用 GitHub 登录' }}
      </button>
    </template>

    <template v-else>
      <div class="tool-archive-panel-topline">
        <div>
          <div class="section-kicker">{{ title }}</div>
          <h2 class="bench-title">{{ title }}</h2>
        </div>
        <button
          class="tool-archive-ghost-action"
          type="button"
          :disabled="loading"
          @click="emit('refresh')"
        >
          {{ loading ? '刷新中' : '刷新' }}
        </button>
      </div>

      <div
        v-if="!hasItems && !loading"
        class="tool-archive-empty"
      >
        {{ emptyText }}
      </div>

      <slot />
    </template>
  </article>
</template>

<style scoped>
.tool-archive-panel {
  background: var(--shell-panel);
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-radius: var(--brand-radius-lg, 24px);
  box-shadow: var(--brand-shadow-card, var(--shell-shadow));
  max-height: 560px;
  min-width: 0;
  overflow: auto;
  padding: 22px;
}

.tool-archive-panel-topline {
  align-items: center;
  display: flex;
  gap: 12px;
  justify-content: space-between;
}

.tool-archive-helper,
.tool-archive-empty {
  color: rgba(15, 23, 35, 0.62);
  font-size: 0.9rem;
}

.tool-archive-helper {
  line-height: 1.6;
  margin: 14px 0 0;
}

.tool-archive-empty {
  background: rgba(255, 255, 255, 0.54);
  border: 1px dashed rgba(16, 37, 66, 0.16);
  border-radius: var(--brand-radius-md, 16px);
  margin-top: 14px;
  padding: 16px;
}

.tool-archive-primary-action,
.tool-archive-ghost-action {
  align-items: center;
  border-radius: var(--brand-radius-pill, 999px);
  cursor: pointer;
  display: inline-flex;
  font: inherit;
  font-size: 0.88rem;
  font-weight: 800;
  justify-content: center;
}

.tool-archive-primary-action {
  background: var(--brand-color-accent, #102542);
  border: 0;
  color: #ffffff;
  min-height: 46px;
  padding: 0 18px;
}

.tool-archive-ghost-action {
  background: rgba(255, 255, 255, 0.62);
  border: 1px solid var(--shell-line);
  color: var(--shell-navy);
  gap: 8px;
  min-height: 38px;
  padding: 0 13px;
}

.tool-archive-ghost-action:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(16, 37, 66, 0.18);
}

.tool-archive-primary-action:disabled,
.tool-archive-ghost-action:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

.tool-archive-auth-action {
  margin-top: 16px;
  width: 100%;
}

@media (max-width: 599px) {
  .tool-archive-panel {
    padding: 18px;
  }

  .tool-archive-panel-topline {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
