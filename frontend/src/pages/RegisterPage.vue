<script setup>
import { computed, onBeforeUnmount, shallowRef } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from 'src/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const RESEND_COOLDOWN_SECONDS = 60

const step = shallowRef(1)
const email = shallowRef('')
const code = shallowRef('')
const password = shallowRef('')
const passwordVisible = shallowRef(false)
const username = shallowRef('')
const loading = shallowRef(false)
const errorMessage = shallowRef('')
const noticeMessage = shallowRef('')
const cooldownLeft = shallowRef(0)

let cooldownTimer = null

function startCooldown() {
  cooldownLeft.value = RESEND_COOLDOWN_SECONDS
  if (cooldownTimer) {
    clearInterval(cooldownTimer)
  }
  cooldownTimer = setInterval(() => {
    if (cooldownLeft.value <= 1) {
      cooldownLeft.value = 0
      clearInterval(cooldownTimer)
      cooldownTimer = null
      return
    }
    cooldownLeft.value -= 1
  }, 1000)
}

onBeforeUnmount(() => {
  if (cooldownTimer) {
    clearInterval(cooldownTimer)
    cooldownTimer = null
  }
})

const emailLooksValid = computed(() => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim()))

const canRequestCode = computed(
  () => !loading.value && cooldownLeft.value === 0 && emailLooksValid.value
)

const canSubmitRegister = computed(
  () =>
    !loading.value &&
    code.value.trim().length >= 4 &&
    password.value.length >= 8
)

function pickFriendlyMessage(error, fallback) {
  if (!error) return fallback
  if (error.code === 429) {
    return error.message || '请求过于频繁，请稍后再试'
  }
  if (error.code === 'NETWORK_ERROR') {
    return '网络异常，请检查连接后重试'
  }
  return error.message || fallback
}

async function submitEmailStep() {
  if (!emailLooksValid.value) {
    errorMessage.value = '请输入有效的邮箱地址'
    return
  }

  loading.value = true
  errorMessage.value = ''
  noticeMessage.value = ''
  try {
    await auth.requestRegisterCode(email.value.trim())
    step.value = 2
    noticeMessage.value = '验证码已发送，请在 10 分钟内填写。若未收到请检查垃圾箱。'
    startCooldown()
  } catch (error) {
    errorMessage.value = pickFriendlyMessage(error, '发送验证码失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

async function resendCode() {
  if (!canRequestCode.value) return

  loading.value = true
  errorMessage.value = ''
  noticeMessage.value = ''
  try {
    await auth.requestRegisterCode(email.value.trim())
    noticeMessage.value = '验证码已重新发送。'
    startCooldown()
  } catch (error) {
    errorMessage.value = pickFriendlyMessage(error, '重新发送失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

async function submitRegister() {
  if (password.value.length < 8) {
    errorMessage.value = '密码至少 8 位'
    return
  }
  if (!code.value.trim()) {
    errorMessage.value = '请输入验证码'
    return
  }

  loading.value = true
  errorMessage.value = ''
  noticeMessage.value = ''
  try {
    await auth.register({
      email: email.value.trim(),
      code: code.value.trim(),
      password: password.value,
      username: username.value.trim() || undefined
    })
    await router.replace('/tools')
  } catch (error) {
    errorMessage.value = pickFriendlyMessage(error, '注册失败，请检查验证码后重试')
  } finally {
    loading.value = false
  }
}

function backToEmailStep() {
  step.value = 1
  errorMessage.value = ''
  noticeMessage.value = ''
}
</script>

<template>
  <div class="register-page">
    <section class="register-shell">
      <div class="register-copy">
        <div class="section-kicker">Create Account</div>
        <h1 class="register-title">注册一个本地账号</h1>
        <p class="register-description">
          使用邮箱注册以启用云端存档与跨设备能力。如果你更熟悉 GitHub 或 LinuxDo，
          也可以直接在登录页使用 OAuth 一键登录。
        </p>
      </div>

      <div class="register-panel">
        <div class="register-form-head">
          <div>
            <div class="section-kicker">{{ step === 1 ? '第 1 步' : '第 2 步' }}</div>
            <h2 class="register-form-title">
              {{ step === 1 ? '验证邮箱' : '完成注册' }}
            </h2>
          </div>
          <span class="register-form-badge">EMAIL</span>
        </div>

        <p
          v-if="noticeMessage"
          class="register-notice"
        >
          {{ noticeMessage }}
        </p>
        <p
          v-if="errorMessage"
          class="register-error"
        >
          {{ errorMessage }}
        </p>

        <form
          v-if="step === 1"
          class="register-form"
          @submit.prevent="submitEmailStep"
        >
          <label class="register-field">
            <span class="register-field-label">邮箱</span>
            <input
              v-model="email"
              class="register-input"
              autocomplete="email"
              name="email"
              placeholder="you@example.com"
              type="email"
            >
          </label>

          <button
            class="register-submit"
            type="submit"
            :disabled="loading || !emailLooksValid"
          >
            {{ loading ? '发送中...' : '获取验证码' }}
          </button>
        </form>

        <form
          v-else
          class="register-form"
          @submit.prevent="submitRegister"
        >
          <p class="register-hint">
            已向 <strong>{{ email }}</strong> 发送 6 位验证码，10 分钟内有效。
          </p>

          <label class="register-field">
            <span class="register-field-label">验证码</span>
            <input
              v-model="code"
              class="register-input"
              autocomplete="one-time-code"
              inputmode="numeric"
              maxlength="6"
              name="code"
              placeholder="6 位数字"
              type="text"
            >
          </label>

          <label class="register-field">
            <span class="register-field-label">密码</span>
            <span class="register-password-wrap">
              <input
                v-model="password"
                class="register-input register-password-input"
                autocomplete="new-password"
                name="new-password"
                placeholder="至少 8 位"
                :type="passwordVisible ? 'text' : 'password'"
              >
              <button
                class="register-password-toggle"
                type="button"
                @click="passwordVisible = !passwordVisible"
              >
                {{ passwordVisible ? '隐藏' : '显示' }}
              </button>
            </span>
          </label>

          <label class="register-field">
            <span class="register-field-label">用户名（可选）</span>
            <input
              v-model="username"
              class="register-input"
              autocomplete="username"
              name="username"
              placeholder="留空则用邮箱前缀"
              type="text"
            >
          </label>

          <button
            class="register-submit"
            type="submit"
            :disabled="!canSubmitRegister"
          >
            {{ loading ? '注册中...' : '完成注册' }}
          </button>

          <div class="register-aux">
            <button
              class="register-aux-button"
              type="button"
              :disabled="!canRequestCode"
              @click="resendCode"
            >
              {{ cooldownLeft > 0 ? `重新发送（${cooldownLeft}s）` : '重新发送验证码' }}
            </button>
            <button
              class="register-aux-button"
              type="button"
              :disabled="loading"
              @click="backToEmailStep"
            >
              修改邮箱
            </button>
          </div>
        </form>

        <div class="register-footer">
          <RouterLink
            class="register-aux-link"
            to="/login"
          >
            已有账号？去登录
          </RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.register-page {
  min-height: calc(100vh - 64px);
  padding: 34px 20px 56px;
}

.register-shell {
  align-items: stretch;
  display: grid;
  gap: 28px;
  grid-template-columns: minmax(0, 0.95fr) minmax(360px, 0.78fr);
  margin: 0 auto;
  max-width: 1080px;
}

.register-copy {
  align-self: center;
  padding: 28px 0;
}

.register-title {
  color: var(--shell-navy);
  font-family: "Georgia", "Times New Roman", serif;
  font-size: clamp(2.4rem, 5vw, 4.9rem);
  font-weight: 600;
  line-height: 1;
  margin: 18px 0;
  max-width: 680px;
}

.register-description {
  color: rgba(15, 23, 35, 0.68);
  font-size: 1rem;
  line-height: 1.8;
  margin: 0;
  max-width: 560px;
}

.register-panel {
  background: var(--shell-panel);
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: var(--brand-radius-lg, 24px);
  box-shadow: var(--brand-shadow-card, var(--shell-shadow));
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 22px;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.register-form-head {
  align-items: flex-start;
  display: flex;
  gap: 12px;
  justify-content: space-between;
  margin-bottom: 2px;
}

.register-form-title {
  color: var(--shell-navy);
  font-size: 1.28rem;
  font-weight: 850;
  line-height: 1.25;
  margin: 4px 0 0;
}

.register-form-badge {
  background: rgba(198, 255, 106, 0.42);
  border: 1px solid rgba(16, 37, 66, 0.08);
  border-radius: var(--brand-radius-pill, 999px);
  color: var(--shell-navy);
  font-size: 0.72rem;
  font-weight: 900;
  padding: 6px 9px;
}

.register-field {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.register-field-label {
  color: rgba(16, 37, 66, 0.72);
  font-size: 0.82rem;
  font-weight: 800;
}

.register-input {
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-md, 16px);
  color: var(--shell-ink);
  font: inherit;
  min-height: 46px;
  padding: 0 13px;
  width: 100%;
}

.register-input:focus {
  border-color: rgba(16, 37, 66, 0.28);
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.14));
  outline: none;
}

.register-password-wrap {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  position: relative;
}

.register-password-input {
  padding-right: 66px;
}

.register-password-toggle {
  align-self: center;
  background: transparent;
  border: 0;
  color: rgba(16, 37, 66, 0.62);
  cursor: pointer;
  font: inherit;
  font-size: 0.8rem;
  font-weight: 800;
  margin-right: 10px;
  padding: 6px;
  position: absolute;
  right: 0;
}

.register-hint {
  color: rgba(15, 23, 35, 0.7);
  font-size: 0.88rem;
  line-height: 1.6;
  margin: 0;
}

.register-error {
  background: rgba(255, 122, 89, 0.1);
  border: 1px solid rgba(255, 122, 89, 0.22);
  border-radius: var(--brand-radius-md, 16px);
  color: #9f2f17;
  font-size: 0.86rem;
  line-height: 1.55;
  margin: 0;
  padding: 10px 12px;
}

.register-notice {
  background: rgba(38, 194, 129, 0.12);
  border: 1px solid rgba(38, 194, 129, 0.24);
  border-radius: var(--brand-radius-md, 16px);
  color: #137a4d;
  font-size: 0.86rem;
  line-height: 1.55;
  margin: 0;
  padding: 10px 12px;
}

.register-submit {
  align-items: center;
  background: var(--brand-color-accent, var(--shell-navy));
  border: 0;
  border-radius: var(--brand-radius-pill, 999px);
  color: #ffffff;
  cursor: pointer;
  display: inline-flex;
  font: inherit;
  font-weight: 850;
  justify-content: center;
  min-height: 46px;
  padding: 0 16px;
}

.register-submit:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
}

.register-submit:disabled {
  cursor: not-allowed;
  opacity: 0.58;
}

.register-aux {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: space-between;
}

.register-aux-button {
  background: rgba(255, 255, 255, 0.66);
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-pill, 999px);
  color: var(--shell-navy);
  cursor: pointer;
  font: inherit;
  font-size: 0.82rem;
  font-weight: 800;
  min-height: 36px;
  padding: 0 14px;
}

.register-aux-button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.register-footer {
  border-top: 1px dashed var(--shell-line);
  display: flex;
  justify-content: center;
  margin-top: 4px;
  padding-top: 12px;
}

.register-aux-link {
  color: rgba(15, 23, 35, 0.66);
  font-size: 0.82rem;
  font-weight: 800;
  text-decoration: none;
}

.register-aux-link:hover,
.register-aux-link:focus-visible {
  color: var(--shell-navy);
  text-decoration: underline;
}

@media (max-width: 899px) {
  .register-shell {
    grid-template-columns: 1fr;
  }

  .register-copy {
    padding: 6px 0 0;
  }
}

@media (max-width: 599px) {
  .register-page {
    min-height: calc(100vh - 60px);
    padding: 24px 14px 42px;
  }

  .register-panel {
    border-radius: var(--brand-radius-md, 16px);
    padding: 16px;
  }
}
</style>
