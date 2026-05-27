<script setup>
import { computed, reactive, shallowRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AuthProviderButton from 'src/components/site/AuthProviderButton.vue'
import { githubLoginUrl, linuxdoLoginUrl } from 'src/lib/auth'
import { useAuthStore } from 'src/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const formState = reactive({
  email: '',
  password: ''
})
const passwordVisible = shallowRef(false)
const loading = shallowRef(false)
const providerLoading = shallowRef('')
const errorMessage = shallowRef('')
const noticeMessage = shallowRef(
  route.query.reset === '1' ? '密码已重置，请用新密码登录。' : ''
)

const targetPath = computed(() => {
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
  if (redirect.startsWith('/') && !redirect.startsWith('//')) {
    return redirect
  }

  return '/tools'
})

const hasCredentials = computed(() => formState.email.trim() && formState.password)
const canSubmit = computed(() => !loading.value)

function validatePasswordLogin(state) {
  const errors = []

  if (!state.email?.trim()) {
    errors.push({ name: 'email', message: '请输入邮箱' })
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(state.email.trim())) {
    errors.push({ name: 'email', message: '邮箱格式不正确' })
  }

  if (!state.password) {
    errors.push({ name: 'password', message: '请输入密码' })
  }

  return errors
}

async function submitPasswordLogin() {
  if (!hasCredentials.value) {
    errorMessage.value = '请输入邮箱和密码'
    return
  }

  loading.value = true
  errorMessage.value = ''
  try {
    await auth.loginWithPassword({
      email: formState.email.trim(),
      password: formState.password
    })
    await router.replace(targetPath.value)
  } catch (error) {
    errorMessage.value = error.message || '登录失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

function startProviderLogin(provider) {
  providerLoading.value = provider
  if (provider === 'github') {
    window.location.href = githubLoginUrl(targetPath.value)
    return
  }

  window.location.href = linuxdoLoginUrl(targetPath.value)
}
</script>

<template>
  <div class="login-page">
    <section class="login-shell">
      <div class="login-copy">
        <div class="section-kicker">Xinming Account</div>
        <h1 class="login-title">登录后继续保存你的工具工作流</h1>
        <p class="login-description">
          本地编辑仍然可以直接使用；登录只用于云端存档、跨设备历史和后续账号能力。
        </p>
      </div>

      <div class="login-panel">
        <UForm
          :state="formState"
          :validate="validatePasswordLogin"
          class="login-form"
          @submit="submitPasswordLogin"
        >
          <div class="login-form-head">
            <div>
              <div class="section-kicker">账号密码</div>
              <h2 class="login-form-title">本地账号</h2>
            </div>
            <UBadge
              color="primary"
              label="JWT"
              variant="soft"
            />
          </div>

          <UFormField
            label="邮箱"
            name="email"
            required
          >
            <UInput
              v-model="formState.email"
              class="login-input"
              autocomplete="email"
              name="email"
              placeholder="输入邮箱"
              type="email"
            />
          </UFormField>

          <UFormField
            label="密码"
            name="password"
            required
          >
            <UInput
              v-model="formState.password"
              autocomplete="current-password"
              name="password"
              placeholder="输入密码"
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

          <UButton
            block
            color="primary"
            type="submit"
            :disabled="!canSubmit"
            :label="loading ? '登录中...' : '登录'"
            :loading="loading"
          />

          <div class="login-aux">
            <UButton
              color="neutral"
              label="还没有账号？注册"
              size="sm"
              to="/register"
              variant="link"
            />
            <UButton
              color="neutral"
              label="忘记密码？"
              size="sm"
              to="/forgot-password"
              variant="link"
            />
          </div>
        </UForm>

        <div class="login-divider">
          <span>或使用第三方账号</span>
        </div>

        <div class="login-providers">
          <AuthProviderButton
            label="GitHub"
            caption="使用 GitHub OAuth 授权登录"
            mark="GH"
            :busy="providerLoading === 'github'"
            @select="startProviderLogin('github')"
          />
          <AuthProviderButton
            label="LinuxDo"
            caption="使用 LinuxDo Connect 授权登录"
            mark="LD"
            :busy="providerLoading === 'linuxdo'"
            @select="startProviderLogin('linuxdo')"
          />
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.login-page {
  min-height: calc(100vh - 64px);
  padding: 34px 20px 56px;
}

.login-shell {
  align-items: stretch;
  display: grid;
  gap: 28px;
  grid-template-columns: minmax(0, 0.95fr) minmax(360px, 0.78fr);
  margin: 0 auto;
  max-width: 1080px;
}

.login-copy {
  align-self: center;
  padding: 28px 0;
}

.login-title {
  color: var(--shell-navy);
  font-family: "Georgia", "Times New Roman", serif;
  font-size: clamp(2.4rem, 5vw, 4.9rem);
  font-weight: 600;
  line-height: 1;
  margin: 18px 0;
  max-width: 680px;
}

.login-description {
  color: rgba(15, 23, 35, 0.68);
  font-size: 1rem;
  line-height: 1.8;
  margin: 0;
  max-width: 560px;
}

.login-panel {
  background: var(--shell-panel);
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: var(--brand-radius-lg, 24px);
  box-shadow: var(--brand-shadow-card, var(--shell-shadow));
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 22px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.login-form-head {
  align-items: flex-start;
  display: flex;
  gap: 12px;
  justify-content: space-between;
  margin-bottom: 2px;
}

.login-form-title {
  color: var(--shell-navy);
  font-size: 1.28rem;
  font-weight: 850;
  line-height: 1.25;
  margin: 4px 0 0;
}

.login-input {
  width: 100%;
}

.login-aux {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: space-between;
  margin-top: 2px;
}

.login-divider {
  align-items: center;
  color: rgba(15, 23, 35, 0.54);
  display: grid;
  font-size: 0.8rem;
  font-weight: 800;
  gap: 12px;
  grid-template-columns: 1fr auto 1fr;
}

.login-divider::before,
.login-divider::after {
  background: var(--shell-line);
  content: '';
  height: 1px;
}

.login-providers {
  display: grid;
  gap: 10px;
}

@media (max-width: 899px) {
  .login-shell {
    grid-template-columns: 1fr;
  }

  .login-copy {
    padding: 6px 0 0;
  }
}

@media (max-width: 599px) {
  .login-page {
    min-height: calc(100vh - 60px);
    padding: 24px 14px 42px;
  }

  .login-panel {
    border-radius: var(--brand-radius-md, 16px);
    padding: 16px;
  }
}
</style>
