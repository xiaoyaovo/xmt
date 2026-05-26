<script setup>
import { computed, shallowRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AuthProviderButton from 'src/components/site/AuthProviderButton.vue'
import { githubLoginUrl, linuxdoLoginUrl } from 'src/lib/auth'
import { useAuthStore } from 'src/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const username = shallowRef('')
const password = shallowRef('')
const passwordVisible = shallowRef(false)
const loading = shallowRef(false)
const providerLoading = shallowRef('')
const errorMessage = shallowRef('')

const targetPath = computed(() => {
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
  if (redirect.startsWith('/') && !redirect.startsWith('//')) {
    return redirect
  }

  return '/tools'
})

const hasCredentials = computed(() => username.value.trim() && password.value)
const canSubmit = computed(() => !loading.value)

async function submitPasswordLogin() {
  if (!hasCredentials.value) {
    errorMessage.value = '请输入账号和密码'
    return
  }

  loading.value = true
  errorMessage.value = ''
  try {
    await auth.loginWithPassword({
      username: username.value,
      password: password.value
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
        <form
          class="login-form"
          @submit.prevent="submitPasswordLogin"
        >
          <div class="login-form-head">
            <div>
              <div class="section-kicker">账号密码</div>
              <h2 class="login-form-title">本地账号</h2>
            </div>
            <span class="login-form-badge">JWT</span>
          </div>

          <label class="login-field">
            <span class="login-field-label">账号</span>
            <input
              v-model="username"
              class="login-input"
              autocomplete="username"
              name="username"
              placeholder="输入账号"
              type="text"
            >
          </label>

          <label class="login-field">
            <span class="login-field-label">密码</span>
            <span class="login-password-wrap">
              <input
                v-model="password"
                class="login-input login-password-input"
                autocomplete="current-password"
                name="password"
                placeholder="输入密码"
                :type="passwordVisible ? 'text' : 'password'"
              >
              <button
                class="login-password-toggle"
                type="button"
                @click="passwordVisible = !passwordVisible"
              >
                {{ passwordVisible ? '隐藏' : '显示' }}
              </button>
            </span>
          </label>

          <p
            v-if="errorMessage"
            class="login-error"
          >
            {{ errorMessage }}
          </p>

          <button
            class="login-submit"
            type="submit"
            :disabled="!canSubmit"
          >
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>

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

.login-form-badge {
  background: rgba(198, 255, 106, 0.42);
  border: 1px solid rgba(16, 37, 66, 0.08);
  border-radius: var(--brand-radius-pill, 999px);
  color: var(--shell-navy);
  font-size: 0.72rem;
  font-weight: 900;
  padding: 6px 9px;
}

.login-field {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.login-field-label {
  color: rgba(16, 37, 66, 0.72);
  font-size: 0.82rem;
  font-weight: 800;
}

.login-input {
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-md, 16px);
  color: var(--shell-ink);
  font: inherit;
  min-height: 46px;
  padding: 0 13px;
  width: 100%;
}

.login-input:focus {
  border-color: rgba(16, 37, 66, 0.28);
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.14));
  outline: none;
}

.login-password-wrap {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  position: relative;
}

.login-password-input {
  padding-right: 66px;
}

.login-password-toggle {
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

.login-error {
  background: rgba(255, 122, 89, 0.1);
  border: 1px solid rgba(255, 122, 89, 0.22);
  border-radius: var(--brand-radius-md, 16px);
  color: #9f2f17;
  font-size: 0.86rem;
  line-height: 1.55;
  margin: 0;
  padding: 10px 12px;
}

.login-submit {
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

.login-submit:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
}

.login-submit:disabled {
  cursor: not-allowed;
  opacity: 0.58;
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
