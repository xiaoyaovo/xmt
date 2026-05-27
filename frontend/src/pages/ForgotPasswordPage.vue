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
const newPassword = shallowRef('')
const confirmPassword = shallowRef('')
const passwordVisible = shallowRef(false)
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

const passwordsMatch = computed(
  () => newPassword.value.length > 0 && newPassword.value === confirmPassword.value
)

const canSubmitReset = computed(
  () =>
    !loading.value &&
    code.value.trim().length >= 4 &&
    newPassword.value.length >= 8 &&
    passwordsMatch.value
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
    // 后端统一返回成功(防邮箱枚举),无论邮箱是否存在都进入下一步
    await auth.requestPasswordResetCode(email.value.trim())
    step.value = 2
    noticeMessage.value = '若该邮箱已注册，验证码将在 10 分钟内有效。请检查收件箱与垃圾箱。'
    startCooldown()
  } catch (error) {
    errorMessage.value = pickFriendlyMessage(error, '发送失败，请稍后重试')
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
    await auth.requestPasswordResetCode(email.value.trim())
    noticeMessage.value = '验证码已重新发送。'
    startCooldown()
  } catch (error) {
    errorMessage.value = pickFriendlyMessage(error, '重新发送失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

async function submitReset() {
  if (newPassword.value.length < 8) {
    errorMessage.value = '密码至少 8 位'
    return
  }
  if (!passwordsMatch.value) {
    errorMessage.value = '两次输入的密码不一致'
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
    await auth.resetPassword({
      email: email.value.trim(),
      code: code.value.trim(),
      new_password: newPassword.value
    })
    await router.replace({
      path: '/login',
      query: { reset: '1' }
    })
  } catch (error) {
    errorMessage.value = pickFriendlyMessage(error, '重置失败，请检查验证码后重试')
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
  <div class="forgot-page">
    <section class="forgot-shell">
      <div class="forgot-copy">
        <div class="section-kicker">Reset Password</div>
        <h1 class="forgot-title">重置你的密码</h1>
        <p class="forgot-description">
          输入注册邮箱以接收 6 位验证码，使用验证码与新密码完成重置。
          出于安全考虑，无论邮箱是否注册都会显示相同的提示。
        </p>
      </div>

      <div class="forgot-panel">
        <div class="forgot-form-head">
          <div>
            <div class="section-kicker">{{ step === 1 ? '第 1 步' : '第 2 步' }}</div>
            <h2 class="forgot-form-title">
              {{ step === 1 ? '验证邮箱' : '设置新密码' }}
            </h2>
          </div>
          <span class="forgot-form-badge">RESET</span>
        </div>

        <p
          v-if="noticeMessage"
          class="forgot-notice"
        >
          {{ noticeMessage }}
        </p>
        <p
          v-if="errorMessage"
          class="forgot-error"
        >
          {{ errorMessage }}
        </p>

        <form
          v-if="step === 1"
          class="forgot-form"
          @submit.prevent="submitEmailStep"
        >
          <label class="forgot-field">
            <span class="forgot-field-label">邮箱</span>
            <input
              v-model="email"
              class="forgot-input"
              autocomplete="email"
              name="email"
              placeholder="you@example.com"
              type="email"
            >
          </label>

          <button
            class="forgot-submit"
            type="submit"
            :disabled="loading || !emailLooksValid"
          >
            {{ loading ? '发送中...' : '发送验证码' }}
          </button>
        </form>

        <form
          v-else
          class="forgot-form"
          @submit.prevent="submitReset"
        >
          <p class="forgot-hint">
            若 <strong>{{ email }}</strong> 已注册，验证码已发送，10 分钟内有效。
          </p>

          <label class="forgot-field">
            <span class="forgot-field-label">验证码</span>
            <input
              v-model="code"
              class="forgot-input"
              autocomplete="one-time-code"
              inputmode="numeric"
              maxlength="6"
              name="code"
              placeholder="6 位数字"
              type="text"
            >
          </label>

          <label class="forgot-field">
            <span class="forgot-field-label">新密码</span>
            <span class="forgot-password-wrap">
              <input
                v-model="newPassword"
                class="forgot-input forgot-password-input"
                autocomplete="new-password"
                name="new-password"
                placeholder="至少 8 位"
                :type="passwordVisible ? 'text' : 'password'"
              >
              <button
                class="forgot-password-toggle"
                type="button"
                @click="passwordVisible = !passwordVisible"
              >
                {{ passwordVisible ? '隐藏' : '显示' }}
              </button>
            </span>
          </label>

          <label class="forgot-field">
            <span class="forgot-field-label">确认密码</span>
            <input
              v-model="confirmPassword"
              class="forgot-input"
              autocomplete="new-password"
              name="confirm-password"
              placeholder="再次输入新密码"
              :type="passwordVisible ? 'text' : 'password'"
            >
          </label>

          <button
            class="forgot-submit"
            type="submit"
            :disabled="!canSubmitReset"
          >
            {{ loading ? '提交中...' : '重置密码' }}
          </button>

          <div class="forgot-aux">
            <button
              class="forgot-aux-button"
              type="button"
              :disabled="!canRequestCode"
              @click="resendCode"
            >
              {{ cooldownLeft > 0 ? `重新发送（${cooldownLeft}s）` : '重新发送验证码' }}
            </button>
            <button
              class="forgot-aux-button"
              type="button"
              :disabled="loading"
              @click="backToEmailStep"
            >
              修改邮箱
            </button>
          </div>
        </form>

        <div class="forgot-footer">
          <RouterLink
            class="forgot-aux-link"
            to="/login"
          >
            返回登录
          </RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.forgot-page {
  min-height: calc(100vh - 64px);
  padding: 34px 20px 56px;
}

.forgot-shell {
  align-items: stretch;
  display: grid;
  gap: 28px;
  grid-template-columns: minmax(0, 0.95fr) minmax(360px, 0.78fr);
  margin: 0 auto;
  max-width: 1080px;
}

.forgot-copy {
  align-self: center;
  padding: 28px 0;
}

.forgot-title {
  color: var(--shell-navy);
  font-family: "Georgia", "Times New Roman", serif;
  font-size: clamp(2.4rem, 5vw, 4.9rem);
  font-weight: 600;
  line-height: 1;
  margin: 18px 0;
  max-width: 680px;
}

.forgot-description {
  color: rgba(15, 23, 35, 0.68);
  font-size: 1rem;
  line-height: 1.8;
  margin: 0;
  max-width: 560px;
}

.forgot-panel {
  background: var(--shell-panel);
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: var(--brand-radius-lg, 24px);
  box-shadow: var(--brand-shadow-card, var(--shell-shadow));
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 22px;
}

.forgot-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.forgot-form-head {
  align-items: flex-start;
  display: flex;
  gap: 12px;
  justify-content: space-between;
  margin-bottom: 2px;
}

.forgot-form-title {
  color: var(--shell-navy);
  font-size: 1.28rem;
  font-weight: 850;
  line-height: 1.25;
  margin: 4px 0 0;
}

.forgot-form-badge {
  background: rgba(198, 255, 106, 0.42);
  border: 1px solid rgba(16, 37, 66, 0.08);
  border-radius: var(--brand-radius-pill, 999px);
  color: var(--shell-navy);
  font-size: 0.72rem;
  font-weight: 900;
  padding: 6px 9px;
}

.forgot-field {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.forgot-field-label {
  color: rgba(16, 37, 66, 0.72);
  font-size: 0.82rem;
  font-weight: 800;
}

.forgot-input {
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-md, 16px);
  color: var(--shell-ink);
  font: inherit;
  min-height: 46px;
  padding: 0 13px;
  width: 100%;
}

.forgot-input:focus {
  border-color: rgba(16, 37, 66, 0.28);
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.14));
  outline: none;
}

.forgot-password-wrap {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  position: relative;
}

.forgot-password-input {
  padding-right: 66px;
}

.forgot-password-toggle {
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

.forgot-hint {
  color: rgba(15, 23, 35, 0.7);
  font-size: 0.88rem;
  line-height: 1.6;
  margin: 0;
}

.forgot-error {
  background: rgba(255, 122, 89, 0.1);
  border: 1px solid rgba(255, 122, 89, 0.22);
  border-radius: var(--brand-radius-md, 16px);
  color: #9f2f17;
  font-size: 0.86rem;
  line-height: 1.55;
  margin: 0;
  padding: 10px 12px;
}

.forgot-notice {
  background: rgba(38, 194, 129, 0.12);
  border: 1px solid rgba(38, 194, 129, 0.24);
  border-radius: var(--brand-radius-md, 16px);
  color: #137a4d;
  font-size: 0.86rem;
  line-height: 1.55;
  margin: 0;
  padding: 10px 12px;
}

.forgot-submit {
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

.forgot-submit:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
}

.forgot-submit:disabled {
  cursor: not-allowed;
  opacity: 0.58;
}

.forgot-aux {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: space-between;
}

.forgot-aux-button {
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

.forgot-aux-button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.forgot-footer {
  border-top: 1px dashed var(--shell-line);
  display: flex;
  justify-content: center;
  margin-top: 4px;
  padding-top: 12px;
}

.forgot-aux-link {
  color: rgba(15, 23, 35, 0.66);
  font-size: 0.82rem;
  font-weight: 800;
  text-decoration: none;
}

.forgot-aux-link:hover,
.forgot-aux-link:focus-visible {
  color: var(--shell-navy);
  text-decoration: underline;
}

@media (max-width: 899px) {
  .forgot-shell {
    grid-template-columns: 1fr;
  }

  .forgot-copy {
    padding: 6px 0 0;
  }
}

@media (max-width: 599px) {
  .forgot-page {
    min-height: calc(100vh - 60px);
    padding: 24px 14px 42px;
  }

  .forgot-panel {
    border-radius: var(--brand-radius-md, 16px);
    padding: 16px;
  }
}
</style>
