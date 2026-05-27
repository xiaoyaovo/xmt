<script setup>
import { computed, onMounted, shallowRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { loginPageUrl } from 'src/lib/auth'
import { useAuthStore } from 'src/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const status = shallowRef('checking')
const errorMessage = shallowRef('')

const targetPath = computed(() => {
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
  if (redirect.startsWith('/') && !redirect.startsWith('//')) {
    return redirect
  }

  return '/tools'
})

onMounted(async () => {
  if (typeof route.query.provider_status === 'string') {
    const nextQuery = {
      provider_status: route.query.provider_status
    }
    if (typeof route.query.provider === 'string') {
      nextQuery.provider = route.query.provider
    }
    if (typeof route.query.message === 'string') {
      nextQuery.message = route.query.message
    }

    await router.replace({ path: targetPath.value, query: nextQuery })
    return
  }

  const token = typeof route.query.access_token === 'string' ? route.query.access_token : ''
  if (!token) {
    status.value = 'error'
    errorMessage.value = '登录回调缺少 access_token，请重新登录。'
    return
  }

  await auth.acceptAccessToken(token)
  if (!auth.authenticated) {
    status.value = 'error'
    errorMessage.value = '登录令牌已收到，但无法确认账号状态。请确认后端服务可访问，且该账号仍存在。'
    return
  }

  status.value = 'success'
  await router.replace(targetPath.value)
})

function retryLogin() {
  window.location.href = loginPageUrl(targetPath.value)
}
</script>

<template>
  <div class="auth-callback-page">
    <section class="auth-callback-card">
      <div class="section-kicker">账号登录</div>
      <h1 class="content-title">
        {{ status === 'error' ? '登录确认失败' : '正在确认登录状态' }}
      </h1>
      <p class="section-text">
        {{ status === 'error' ? errorMessage : '登录完成后会自动回到工具工作台。' }}
      </p>
      <div
        v-if="status === 'error'"
        class="auth-callback-actions"
      >
        <UButton
          class="auth-callback-button"
          color="primary"
          label="重新登录"
          type="button"
          @click="retryLogin"
        />
        <UButton
          class="auth-callback-link"
          color="neutral"
          label="返回工具区"
          to="/tools"
          variant="subtle"
        />
      </div>
    </section>
  </div>
</template>

<style scoped>
.auth-callback-page {
  display: grid;
  min-height: 55vh;
  padding: 32px 20px;
  place-items: center;
}

.auth-callback-card {
  background: var(--shell-panel);
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-radius: var(--brand-radius-lg, 24px);
  box-shadow: var(--brand-shadow-card, var(--shell-shadow));
  max-width: 520px;
  padding: 28px;
  width: 100%;
}

.auth-callback-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 22px;
}

.auth-callback-button,
.auth-callback-link {
  align-items: center;
  border-radius: var(--brand-radius-pill, 999px);
  display: inline-flex;
  font: inherit;
  font-weight: 800;
  min-height: 42px;
  padding: 0 16px;
  text-decoration: none;
}

.auth-callback-button {
  background: var(--brand-color-accent, var(--shell-navy));
  border: 0;
  color: #ffffff;
  cursor: pointer;
}

.auth-callback-link {
  background: rgba(255, 255, 255, 0.66);
  border: 1px solid var(--shell-line);
  color: var(--shell-navy);
}
</style>
