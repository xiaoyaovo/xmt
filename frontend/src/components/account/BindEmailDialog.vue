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
import { computed, onBeforeUnmount, shallowRef, watch } from 'vue'

const RESEND_COOLDOWN_SECONDS = 60

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
  },
  notice: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:open', 'requestCode', 'confirm'])

const email = shallowRef('')
const code = shallowRef('')
const password = shallowRef('')
const passwordVisible = shallowRef(false)
const cooldownLeft = shallowRef(0)

let cooldownTimer = null

const isOpen = computed({
  get: () => props.open,
  set: (value) => emit('update:open', value)
})

const emailLooksValid = computed(() => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim()))
const canRequestCode = computed(() => !props.busy && cooldownLeft.value === 0 && emailLooksValid.value)
const canConfirm = computed(
  () =>
    !props.busy &&
    emailLooksValid.value &&
    code.value.trim().length >= 4 &&
    password.value.length >= 8
)

function stopCooldown() {
  if (cooldownTimer) {
    clearInterval(cooldownTimer)
    cooldownTimer = null
  }
}

function startCooldown() {
  cooldownLeft.value = RESEND_COOLDOWN_SECONDS
  stopCooldown()
  cooldownTimer = setInterval(() => {
    if (cooldownLeft.value <= 1) {
      cooldownLeft.value = 0
      stopCooldown()
      return
    }
    cooldownLeft.value -= 1
  }, 1000)
}

function resetForm() {
  email.value = ''
  code.value = ''
  password.value = ''
  passwordVisible.value = false
  cooldownLeft.value = 0
  stopCooldown()
}

function requestCode() {
  if (!canRequestCode.value) return
  emit('requestCode', email.value.trim(), {
    onSuccess: startCooldown
  })
}

function confirmBind() {
  if (!canConfirm.value) return
  emit('confirm', {
    email: email.value.trim(),
    code: code.value.trim(),
    password: password.value
  })
}

watch(
  () => props.open,
  (value) => {
    if (!value) {
      resetForm()
    }
  }
)

onBeforeUnmount(stopCooldown)
</script>

<template>
  <DialogRoot v-model:open="isOpen">
    <DialogPortal>
      <DialogOverlay class="bind-email-dialog-overlay" />

      <DialogContent class="bind-email-dialog-content">
        <div class="bind-email-dialog-copy">
          <p class="bind-email-dialog-kicker">邮箱登录</p>
          <DialogTitle class="bind-email-dialog-title">
            绑定邮箱登录
          </DialogTitle>
          <DialogDescription class="bind-email-dialog-description">
            验证邮箱并设置密码后，可用邮箱密码登录当前账号。
          </DialogDescription>
        </div>

        <form
          class="bind-email-dialog-form"
          @submit.prevent="confirmBind"
        >
          <p
            v-if="notice"
            class="bind-email-dialog-notice"
          >
            {{ notice }}
          </p>
          <p
            v-if="error"
            class="bind-email-dialog-error"
          >
            {{ error }}
          </p>

          <label class="bind-email-dialog-field">
            <span class="bind-email-dialog-label">邮箱</span>
            <span class="bind-email-dialog-inline">
              <input
                v-model="email"
                class="bind-email-dialog-input"
                autocomplete="email"
                name="email"
                placeholder="you@example.com"
                type="email"
              >
              <button
                class="bind-email-dialog-code"
                type="button"
                :disabled="!canRequestCode"
                @click="requestCode"
              >
                {{ cooldownLeft ? `${cooldownLeft}s` : '获取验证码' }}
              </button>
            </span>
          </label>

          <label class="bind-email-dialog-field">
            <span class="bind-email-dialog-label">验证码</span>
            <input
              v-model="code"
              class="bind-email-dialog-input"
              autocomplete="one-time-code"
              inputmode="numeric"
              maxlength="6"
              name="code"
              placeholder="6 位验证码"
              type="text"
            >
          </label>

          <label class="bind-email-dialog-field">
            <span class="bind-email-dialog-label">登录密码</span>
            <span class="bind-email-dialog-inline">
              <input
                v-model="password"
                class="bind-email-dialog-input"
                autocomplete="new-password"
                name="password"
                placeholder="至少 8 位"
                :type="passwordVisible ? 'text' : 'password'"
              >
              <button
                class="bind-email-dialog-code"
                type="button"
                @click="passwordVisible = !passwordVisible"
              >
                {{ passwordVisible ? '隐藏' : '显示' }}
              </button>
            </span>
          </label>

          <div class="bind-email-dialog-actions">
            <DialogClose as-child>
              <button
                class="bind-email-dialog-secondary"
                type="button"
                :disabled="busy"
              >
                取消
              </button>
            </DialogClose>
            <button
              class="bind-email-dialog-primary"
              type="submit"
              :disabled="!canConfirm"
            >
              {{ busy ? '绑定中...' : '完成绑定' }}
            </button>
          </div>
        </form>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>

<style>
/* Unscoped: DialogPortal teleports dialog nodes to <body>, outside scoped selectors. */
.bind-email-dialog-overlay {
  background: rgba(8, 15, 26, 0.52);
  inset: 0;
  position: fixed;
  z-index: 70;
}

.bind-email-dialog-content {
  background: #ffffff;
  border: 1px solid rgba(16, 37, 66, 0.14);
  border-radius: var(--brand-radius-lg, 22px);
  box-shadow: 0 28px 70px rgba(16, 37, 66, 0.26);
  color: var(--shell-navy, #102542);
  left: 50%;
  max-width: 520px;
  outline: none;
  padding: 24px;
  position: fixed;
  top: 50%;
  transform: translate(-50%, -50%);
  width: min(92vw, 520px);
  z-index: 80;
}

.bind-email-dialog-content:focus-visible {
  box-shadow: 0 28px 70px rgba(16, 37, 66, 0.26), var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
}

.bind-email-dialog-kicker {
  color: rgba(15, 23, 35, 0.5);
  font-size: 0.74rem;
  font-weight: 900;
  letter-spacing: 0.08em;
  margin: 0 0 8px;
  text-transform: uppercase;
}

.bind-email-dialog-title {
  color: var(--shell-navy, #102542);
  font-size: 1.35rem;
  font-weight: 900;
  letter-spacing: 0;
  line-height: 1.18;
  margin: 0;
}

.bind-email-dialog-description {
  color: rgba(15, 23, 35, 0.68);
  font-size: 0.94rem;
  line-height: 1.7;
  margin: 10px 0 0;
}

.bind-email-dialog-form {
  display: grid;
  gap: 14px;
  margin-top: 18px;
}

.bind-email-dialog-notice,
.bind-email-dialog-error {
  border-radius: var(--brand-radius-md, 16px);
  line-height: 1.6;
  margin: 0;
  padding: 10px 12px;
}

.bind-email-dialog-notice {
  background: rgba(38, 194, 129, 0.08);
  border: 1px solid rgba(38, 194, 129, 0.18);
  color: #137a4d;
}

.bind-email-dialog-error {
  background: rgba(157, 37, 37, 0.08);
  border: 1px solid rgba(157, 37, 37, 0.18);
  color: #9d2525;
}

.bind-email-dialog-field {
  display: grid;
  gap: 8px;
}

.bind-email-dialog-label {
  color: rgba(15, 23, 35, 0.64);
  font-size: 0.82rem;
  font-weight: 850;
}

.bind-email-dialog-inline {
  align-items: center;
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(0, 1fr) auto;
}

.bind-email-dialog-input {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid var(--shell-line, rgba(16, 37, 66, 0.12));
  border-radius: var(--brand-radius-md, 16px);
  color: var(--shell-navy, #102542);
  font: inherit;
  min-height: 42px;
  min-width: 0;
  padding: 0 13px;
  width: 100%;
}

.bind-email-dialog-input:focus {
  border-color: rgba(16, 37, 66, 0.28);
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.12));
  outline: none;
}

.bind-email-dialog-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 4px;
}

.bind-email-dialog-primary,
.bind-email-dialog-secondary,
.bind-email-dialog-code {
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

.bind-email-dialog-primary,
.bind-email-dialog-code {
  background: var(--brand-color-accent, #102542);
  border: 1px solid var(--brand-color-accent, #102542);
  color: #ffffff;
}

.bind-email-dialog-secondary {
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid var(--shell-line, rgba(16, 37, 66, 0.12));
  color: var(--shell-navy, #102542);
}

.bind-email-dialog-primary:hover:not(:disabled),
.bind-email-dialog-code:hover:not(:disabled) {
  background: var(--brand-color-accent-hover, var(--brand-color-accent, #102542));
}

.bind-email-dialog-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.94);
  border-color: rgba(16, 37, 66, 0.2);
}

.bind-email-dialog-primary:focus-visible,
.bind-email-dialog-secondary:focus-visible,
.bind-email-dialog-code:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
}

.bind-email-dialog-primary:disabled,
.bind-email-dialog-secondary:disabled,
.bind-email-dialog-code:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

@media (max-width: 520px) {
  .bind-email-dialog-inline,
  .bind-email-dialog-actions {
    grid-template-columns: 1fr;
  }

  .bind-email-dialog-actions {
    display: grid;
  }

  .bind-email-dialog-primary,
  .bind-email-dialog-secondary,
  .bind-email-dialog-code {
    width: 100%;
  }
}
</style>
