<script setup>
import { computed, onBeforeUnmount, reactive, shallowRef } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from 'src/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const RESEND_COOLDOWN_SECONDS = 60

const step = shallowRef(1)
const formState = reactive({
  email: '',
  code: '',
  password: '',
  username: ''
})
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

const emailLooksValid = computed(() => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formState.email.trim()))

const canRequestCode = computed(
  () => !loading.value && cooldownLeft.value === 0 && emailLooksValid.value
)

const canSubmitRegister = computed(
  () =>
    !loading.value &&
    formState.code.trim().length >= 4 &&
    formState.password.length >= 8
)

function validateEmailStep(state) {
  const errors = []
  if (!state.email?.trim()) {
    errors.push({ name: 'email', message: '请输入邮箱' })
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(state.email.trim())) {
    errors.push({ name: 'email', message: '邮箱格式不正确' })
  }
  return errors
}

function validateRegisterStep(state) {
  const errors = []
  if (!state.code?.trim()) {
    errors.push({ name: 'code', message: '请输入验证码' })
  } else if (state.code.trim().length < 4) {
    errors.push({ name: 'code', message: '验证码长度不正确' })
  }
  if (!state.password) {
    errors.push({ name: 'password', message: '请输入密码' })
  } else if (state.password.length < 8) {
    errors.push({ name: 'password', message: '密码至少 8 位' })
  }
  return errors
}

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
    await auth.requestRegisterCode(formState.email.trim())
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
    await auth.requestRegisterCode(formState.email.trim())
    noticeMessage.value = '验证码已重新发送。'
    startCooldown()
  } catch (error) {
    errorMessage.value = pickFriendlyMessage(error, '重新发送失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

async function submitRegister() {
  if (formState.password.length < 8) {
    errorMessage.value = '密码至少 8 位'
    return
  }
  if (!formState.code.trim()) {
    errorMessage.value = '请输入验证码'
    return
  }

  loading.value = true
  errorMessage.value = ''
  noticeMessage.value = ''
  try {
    await auth.register({
      email: formState.email.trim(),
      code: formState.code.trim(),
      password: formState.password,
      username: formState.username.trim() || undefined
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

        <UAlert
          v-if="noticeMessage"
          color="success"
          variant="soft"
          :description="noticeMessage"
        />
        <UAlert
          v-if="errorMessage"
          color="error"
          variant="soft"
          :description="errorMessage"
        />

        <UForm
          v-if="step === 1"
          :state="formState"
          :validate="validateEmailStep"
          class="register-form"
          @submit="submitEmailStep"
        >
          <UFormField
            label="邮箱"
            name="email"
            required
          >
            <UInput
              v-model="formState.email"
              autocomplete="email"
              name="email"
              placeholder="you@example.com"
              type="email"
            />
          </UFormField>

          <UButton
            block
            color="primary"
            :disabled="loading || !emailLooksValid"
            :label="loading ? '发送中...' : '获取验证码'"
            :loading="loading"
            type="submit"
          />
        </UForm>

        <UForm
          v-else
          :state="formState"
          :validate="validateRegisterStep"
          class="register-form"
          @submit="submitRegister"
        >
          <p class="register-hint">
            已向 <strong>{{ formState.email }}</strong> 发送 6 位验证码，10 分钟内有效。
          </p>

          <UFormField
            label="验证码"
            name="code"
            required
          >
            <UInput
              v-model="formState.code"
              autocomplete="one-time-code"
              inputmode="numeric"
              maxlength="6"
              name="code"
              placeholder="6 位数字"
              type="text"
            />
          </UFormField>

          <UFormField
            label="密码"
            name="password"
            required
          >
            <UInput
              v-model="formState.password"
              autocomplete="new-password"
              name="new-password"
              placeholder="至少 8 位"
              :type="passwordVisible ? 'text' : 'password'"
            >
              <template #trailing>
                <UButton
                  color="neutral"
                  size="xs"
                  type="button"
                  variant="ghost"
                  :label="passwordVisible ? '隐藏' : '显示'"
                  @click="passwordVisible = !passwordVisible"
                />
              </template>
            </UInput>
          </UFormField>

          <UFormField
            label="用户名（可选）"
            name="username"
          >
            <UInput
              v-model="formState.username"
              autocomplete="username"
              name="username"
              placeholder="留空则用邮箱前缀"
              type="text"
            />
          </UFormField>

          <UButton
            block
            color="primary"
            :disabled="!canSubmitRegister"
            :label="loading ? '注册中...' : '完成注册'"
            :loading="loading"
            type="submit"
          />

          <div class="register-aux">
            <UButton
              color="neutral"
              size="sm"
              type="button"
              variant="subtle"
              :disabled="!canRequestCode"
              :label="cooldownLeft > 0 ? `重新发送（${cooldownLeft}s）` : '重新发送验证码'"
              @click="resendCode"
            />
            <UButton
              color="neutral"
              label="修改邮箱"
              size="sm"
              type="button"
              variant="subtle"
              :disabled="loading"
              @click="backToEmailStep"
            />
          </div>
        </UForm>

        <div class="register-footer">
          <UButton
            color="neutral"
            label="已有账号？去登录"
            size="sm"
            to="/login"
            variant="link"
          />
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

.register-hint {
  color: rgba(15, 23, 35, 0.7);
  font-size: 0.88rem;
  line-height: 1.6;
  margin: 0;
}

.register-aux {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: space-between;
}

.register-footer {
  border-top: 1px dashed var(--shell-line);
  display: flex;
  justify-content: center;
  margin-top: 4px;
  padding-top: 12px;
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
