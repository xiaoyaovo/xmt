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
  busy: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:open', 'confirm'])

const isOpen = computed({
  get: () => props.open,
  set: (value) => emit('update:open', value)
})

function handleConfirm() {
  emit('confirm')
}
</script>

<template>
  <DialogRoot v-model:open="isOpen">
    <DialogPortal>
      <DialogOverlay class="account-delete-dialog-overlay" />

      <DialogContent class="account-delete-dialog-content">
        <div class="account-delete-dialog-mark">!</div>

        <div class="account-delete-dialog-copy">
          <p class="account-delete-dialog-kicker">危险操作</p>
          <DialogTitle class="account-delete-dialog-title">
            删除当前账号
          </DialogTitle>
          <DialogDescription class="account-delete-dialog-description">
            删除后将移除当前账号、全部登录方式、云端同步数据、CSV 历史与已上传文件。此操作无法恢复。
          </DialogDescription>

          <p
            v-if="error"
            class="account-delete-dialog-error"
          >
            {{ error }}
          </p>
        </div>

        <div class="account-delete-dialog-actions">
          <DialogClose as-child>
            <button
              class="account-delete-dialog-secondary"
              type="button"
              :disabled="busy"
            >
              取消
            </button>
          </DialogClose>
          <button
            class="account-delete-dialog-danger"
            type="button"
            :disabled="busy"
            @click="handleConfirm"
          >
            {{ busy ? '正在删除' : '同意删除所有相关数据' }}
          </button>
        </div>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>

<style>
/* Unscoped: DialogPortal teleports dialog nodes to <body>, outside scoped selectors. */
.account-delete-dialog-overlay {
  background: rgba(8, 15, 26, 0.56);
  inset: 0;
  position: fixed;
  z-index: 70;
}

.account-delete-dialog-content {
  align-items: flex-start;
  background: #ffffff;
  border: 1px solid rgba(157, 37, 37, 0.22);
  border-radius: var(--brand-radius-lg, 22px);
  box-shadow: 0 28px 70px rgba(16, 37, 66, 0.28);
  color: var(--shell-navy, #102542);
  display: grid;
  gap: 16px;
  grid-template-columns: auto minmax(0, 1fr);
  left: 50%;
  max-width: 540px;
  outline: none;
  padding: 24px;
  position: fixed;
  top: 50%;
  transform: translate(-50%, -50%);
  width: min(92vw, 540px);
  z-index: 80;
}

.account-delete-dialog-content:focus-visible {
  box-shadow: 0 28px 70px rgba(16, 37, 66, 0.28), var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
}

.account-delete-dialog-mark {
  align-items: center;
  background: rgba(157, 37, 37, 0.1);
  border: 1px solid rgba(157, 37, 37, 0.18);
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

.account-delete-dialog-copy {
  min-width: 0;
}

.account-delete-dialog-kicker {
  color: #9d2525;
  font-size: 0.74rem;
  font-weight: 900;
  letter-spacing: 0.08em;
  margin: 0 0 8px;
  text-transform: uppercase;
}

.account-delete-dialog-title {
  color: var(--shell-navy, #102542);
  font-size: 1.35rem;
  font-weight: 900;
  letter-spacing: 0;
  line-height: 1.18;
  margin: 0;
}

.account-delete-dialog-description {
  color: rgba(15, 23, 35, 0.68);
  font-size: 0.94rem;
  line-height: 1.7;
  margin: 10px 0 0;
}

.account-delete-dialog-error {
  background: rgba(157, 37, 37, 0.08);
  border: 1px solid rgba(157, 37, 37, 0.18);
  border-radius: var(--brand-radius-md, 16px);
  color: #9d2525;
  line-height: 1.6;
  margin: 14px 0 0;
  padding: 10px 12px;
}

.account-delete-dialog-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  grid-column: 2;
  justify-content: flex-end;
  margin-top: 4px;
}

.account-delete-dialog-danger,
.account-delete-dialog-secondary {
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

.account-delete-dialog-danger {
  background: #9d2525;
  border: 1px solid #9d2525;
  color: #ffffff;
}

.account-delete-dialog-secondary {
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid var(--shell-line, rgba(16, 37, 66, 0.12));
  color: var(--shell-navy, #102542);
}

.account-delete-dialog-danger:hover:not(:disabled) {
  background: #7f1d1d;
}

.account-delete-dialog-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.94);
  border-color: rgba(16, 37, 66, 0.2);
}

.account-delete-dialog-danger:focus-visible,
.account-delete-dialog-secondary:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
}

.account-delete-dialog-danger:disabled,
.account-delete-dialog-secondary:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

@media (max-width: 520px) {
  .account-delete-dialog-content {
    grid-template-columns: 1fr;
  }

  .account-delete-dialog-actions {
    grid-column: 1;
    justify-content: stretch;
  }

  .account-delete-dialog-danger,
  .account-delete-dialog-secondary {
    width: 100%;
  }
}
</style>
