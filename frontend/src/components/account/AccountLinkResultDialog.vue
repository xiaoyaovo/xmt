<script setup>
import {
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle
} from 'reka-ui'
import { computed } from 'vue'

const props = defineProps({
  open: {
    type: Boolean,
    default: false
  },
  status: {
    type: String,
    default: ''
  },
  providerLabel: {
    type: String,
    default: '第三方账号'
  },
  message: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:open', 'login', 'retry'])

const isOpen = computed({
  get: () => props.open,
  set: (value) => emit('update:open', value)
})

const isSuccess = computed(() => props.status === 'linked')
const isConflict = computed(() => props.status === 'conflict')
const needsLogin = computed(() => props.status === 'auth_required')
const dialogTitle = computed(() => {
  if (isSuccess.value) return `${props.providerLabel} 已绑定`
  if (props.status === 'conflict') return `${props.providerLabel} 无法绑定`
  if (needsLogin.value) return '需要重新登录'
  return '绑定没有完成'
})

const dialogDescription = computed(() => {
  if (props.message) return props.message
  if (isSuccess.value) return `${props.providerLabel} 已经可以用于登录当前账号。`
  if (props.status === 'conflict') {
    return `${props.providerLabel} 已经绑定到另一个账号。请先登录那个账号解绑，或换一个账号继续绑定。`
  }
  if (needsLogin.value) return '登录状态已失效，请重新登录后再绑定账号。'
  return `${props.providerLabel} 绑定没有完成，请稍后重试。`
})

function handleLogin() {
  emit('login')
}

function handleRetry() {
  emit('retry')
}
</script>

<template>
  <DialogRoot v-model:open="isOpen">
    <DialogPortal>
      <DialogOverlay class="account-link-dialog-overlay" />

      <DialogContent
        class="account-link-dialog-content"
        :class="{ 'account-link-dialog-success': isSuccess }"
      >
        <div class="account-link-dialog-mark">
          {{ isSuccess ? '✓' : '!' }}
        </div>
        <div class="account-link-dialog-copy">
          <p class="account-link-dialog-kicker">登录方式绑定</p>
          <DialogTitle class="account-link-dialog-title">
            {{ dialogTitle }}
          </DialogTitle>
          <DialogDescription class="account-link-dialog-description">
            {{ dialogDescription }}
          </DialogDescription>
        </div>

        <div class="account-link-dialog-actions">
          <button
            v-if="needsLogin"
            class="account-link-dialog-primary"
            type="button"
            @click="handleLogin"
          >
            重新登录
          </button>
          <button
            v-else-if="isConflict"
            class="account-link-dialog-primary"
            type="button"
            @click="handleRetry"
          >
            换一个账号绑定
          </button>
          <DialogClose as-child>
            <button
              class="account-link-dialog-secondary"
              type="button"
            >
              知道了
            </button>
          </DialogClose>
        </div>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>

<style>
/* Unscoped: DialogPortal teleports dialog nodes to <body>, outside scoped selectors. */
.account-link-dialog-overlay {
  background: rgba(8, 15, 26, 0.52);
  inset: 0;
  position: fixed;
  z-index: 70;
}

.account-link-dialog-content {
  align-items: flex-start;
  background: #ffffff;
  border: 1px solid rgba(157, 37, 37, 0.16);
  border-radius: var(--brand-radius-lg, 22px);
  box-shadow: 0 28px 70px rgba(16, 37, 66, 0.26);
  color: var(--shell-navy, #102542);
  display: grid;
  gap: 16px;
  grid-template-columns: auto minmax(0, 1fr);
  left: 50%;
  max-width: 500px;
  outline: none;
  padding: 24px;
  position: fixed;
  top: 50%;
  transform: translate(-50%, -50%);
  width: min(92vw, 500px);
  z-index: 80;
}

.account-link-dialog-success {
  border-color: rgba(19, 122, 77, 0.18);
}

.account-link-dialog-content:focus-visible {
  box-shadow: 0 28px 70px rgba(16, 37, 66, 0.26), var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
}

.account-link-dialog-mark {
  align-items: center;
  background: rgba(157, 37, 37, 0.1);
  border: 1px solid rgba(157, 37, 37, 0.16);
  border-radius: 50%;
  color: #9d2525;
  display: inline-flex;
  font-size: 1.25rem;
  font-weight: 900;
  height: 42px;
  justify-content: center;
  line-height: 1;
  width: 42px;
}

.account-link-dialog-success .account-link-dialog-mark {
  background: rgba(19, 122, 77, 0.1);
  border-color: rgba(19, 122, 77, 0.16);
  color: #137a4d;
}

.account-link-dialog-copy {
  min-width: 0;
}

.account-link-dialog-kicker {
  color: rgba(15, 23, 35, 0.5);
  font-size: 0.74rem;
  font-weight: 900;
  letter-spacing: 0.08em;
  margin: 0 0 8px;
  text-transform: uppercase;
}

.account-link-dialog-title {
  color: var(--shell-navy, #102542);
  font-size: 1.35rem;
  font-weight: 900;
  letter-spacing: 0;
  line-height: 1.18;
  margin: 0;
}

.account-link-dialog-description {
  color: rgba(15, 23, 35, 0.68);
  font-size: 0.94rem;
  line-height: 1.7;
  margin: 10px 0 0;
}

.account-link-dialog-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  grid-column: 2;
  justify-content: flex-end;
  margin-top: 4px;
}

.account-link-dialog-primary,
.account-link-dialog-secondary {
  align-items: center;
  border-radius: var(--brand-radius-pill, 999px);
  cursor: pointer;
  display: inline-flex;
  font: inherit;
  font-size: 0.9rem;
  font-weight: 850;
  justify-content: center;
  min-height: 40px;
  padding: 0 16px;
}

.account-link-dialog-primary {
  background: var(--brand-color-accent, #102542);
  border: 1px solid var(--brand-color-accent, #102542);
  color: #ffffff;
}

.account-link-dialog-secondary {
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid var(--shell-line, rgba(16, 37, 66, 0.12));
  color: var(--shell-navy, #102542);
}

.account-link-dialog-primary:hover {
  background: var(--brand-color-accent-hover, var(--brand-color-accent, #102542));
}

.account-link-dialog-secondary:hover {
  background: rgba(255, 255, 255, 0.94);
  border-color: rgba(16, 37, 66, 0.2);
}

.account-link-dialog-primary:focus-visible,
.account-link-dialog-secondary:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
}

@media (max-width: 520px) {
  .account-link-dialog-content {
    grid-template-columns: 1fr;
    padding: 22px;
  }

  .account-link-dialog-actions {
    grid-column: 1;
    justify-content: stretch;
  }

  .account-link-dialog-primary,
  .account-link-dialog-secondary {
    flex: 1;
  }
}
</style>
