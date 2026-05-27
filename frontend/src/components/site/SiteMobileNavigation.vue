<script setup>
import { shallowRef, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

import { useAuthStore } from 'src/stores/auth'

defineProps({
  items: {
    type: Array,
    default: () => []
  },
  workspaceItems: {
    type: Array,
    default: () => []
  }
})

const route = useRoute()
const open = shallowRef(false)
const auth = useAuthStore()

watch(
  () => route.fullPath,
  () => {
    open.value = false
  }
)

function isRouteActive(to, exact = false) {
  if (exact) {
    return route.path === to
  }

  return route.path === to || route.path.startsWith(`${to}/`)
}

async function handleLogout() {
  await auth.logout()
  open.value = false
}
</script>

<template>
  <USlideover
    v-model:open="open"
    title="Xinming"
    description="公开前台负责表达，工具与后台负责效率。"
    side="right"
  >
    <UButton
      class="mobile-nav-trigger"
      color="primary"
      trailing-icon="i-lucide-menu"
      type="button"
      aria-label="打开站点导航"
    >
      菜单
    </UButton>

    <template #body>
      <div class="mobile-nav-shell">
        <div class="mobile-nav-group">
          <div class="mobile-nav-group-label">主导航</div>

          <RouterLink
            v-for="item in items"
            :key="item.to"
            :to="item.to"
            class="mobile-nav-link"
            :class="{ 'mobile-nav-link-active': isRouteActive(item.to, item.exact) }"
          >
            <span
              :class="item.icon"
              class="mobile-nav-link-icon"
              aria-hidden="true"
            />
            <span class="mobile-nav-link-copy">
              <span class="mobile-nav-link-title">{{ item.label }}</span>
              <span class="mobile-nav-link-caption">{{ item.caption }}</span>
            </span>
          </RouterLink>
        </div>

        <div class="mobile-nav-group">
          <div class="mobile-nav-group-label">功能分区</div>

          <RouterLink
            v-for="item in workspaceItems"
            :key="item.to"
            :to="item.to"
            class="mobile-nav-card"
            :class="{ 'mobile-nav-card-active': isRouteActive(item.to) }"
          >
            <div class="mobile-nav-card-topline">
              <span
                :class="item.icon"
                class="mobile-nav-card-icon"
                aria-hidden="true"
              />
              <span class="mobile-nav-card-label">{{ item.label }}</span>
            </div>
            <p class="mobile-nav-card-caption">{{ item.caption }}</p>
          </RouterLink>
        </div>

        <div class="mobile-nav-group">
          <div class="mobile-nav-group-label">账号</div>
          <UAlert
            v-if="!auth.initialized || auth.loading"
            color="neutral"
            title="正在检查登录状态"
            variant="soft"
            description="请稍等片刻。"
          />
          <div
            v-else-if="auth.authenticated"
            class="mobile-nav-card mobile-nav-account"
          >
            <div class="mobile-nav-card-topline">
              <UAvatar
                :alt="auth.user?.username"
                :src="auth.user?.avatar_url"
                size="sm"
                :text="auth.user?.username?.slice(0, 1)?.toUpperCase() || 'U'"
              />
              <span class="mobile-nav-card-label">{{ auth.user?.username }}</span>
            </div>
            <p class="mobile-nav-card-caption">已登录，云端存档会绑定到当前账号。</p>
            <div class="mobile-nav-account-actions">
              <UButton
                color="neutral"
                disabled
                size="sm"
                variant="subtle"
              >
                个人信息
              </UButton>
              <UButton
                color="neutral"
                size="sm"
                to="/account/security"
                variant="subtle"
                @click="open = false"
              >
                登录方式
              </UButton>
              <UButton
                color="error"
                size="sm"
                variant="soft"
                @click="handleLogout"
              >
                登出
              </UButton>
            </div>
          </div>
          <UButton
            v-else
            block
            color="primary"
            icon="i-lucide-log-in"
            type="button"
            @click="auth.openLoginPage()"
          >
            登录后使用云端存档
          </UButton>
        </div>
      </div>
    </template>
  </USlideover>
</template>

<style scoped>
.mobile-nav-trigger {
  min-height: 44px;
}

.mobile-nav-shell {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.mobile-nav-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mobile-nav-group-label {
  color: rgba(16, 37, 66, 0.56);
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.mobile-nav-link,
.mobile-nav-card {
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(16, 37, 66, 0.1);
  border-radius: var(--brand-radius-md, 16px);
  color: var(--shell-navy);
  text-decoration: none;
}

.mobile-nav-link {
  align-items: center;
  display: flex;
  gap: 12px;
  padding: 12px;
}

.mobile-nav-link-active,
.mobile-nav-card-active {
  border-color: var(--brand-color-accent, #102542);
  box-shadow: inset 3px 0 0 var(--brand-color-accent, #102542);
}

.mobile-nav-link-icon,
.mobile-nav-card-icon {
  color: var(--shell-coral);
  font-size: 1.1rem;
}

.mobile-nav-link-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.mobile-nav-link-title,
.mobile-nav-card-label {
  font-weight: 800;
}

.mobile-nav-link-caption,
.mobile-nav-card-caption {
  color: rgba(15, 23, 35, 0.58);
  font-size: 0.84rem;
  line-height: 1.5;
}

.mobile-nav-card {
  display: block;
  padding: 13px;
}

.mobile-nav-card-topline {
  align-items: center;
  display: flex;
  gap: 10px;
}

.mobile-nav-card-caption {
  margin: 6px 0 0;
}

.mobile-nav-account-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

html.dark .mobile-nav-link,
html.dark .mobile-nav-card {
  background: rgba(17, 24, 39, 0.7);
}
</style>
