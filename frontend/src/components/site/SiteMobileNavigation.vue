<script setup>
import {
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
  DialogTrigger
} from 'reka-ui'
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
  <DialogRoot v-model:open="open">
    <DialogTrigger as-child>
      <button
        class="mobile-nav-trigger"
        type="button"
        aria-label="打开站点导航"
      >
        <span class="mobile-nav-trigger-copy">
          <span class="mobile-nav-trigger-label">菜单</span>
          <span class="mobile-nav-trigger-meta">导航</span>
        </span>
        <span
          class="mobile-nav-trigger-mark"
          aria-hidden="true"
        >
          +
        </span>
      </button>
    </DialogTrigger>

    <DialogPortal>
      <DialogOverlay class="mobile-nav-overlay" />

      <DialogContent class="mobile-nav-content">
        <div class="mobile-nav-shell">
          <div class="mobile-nav-topline">Xinming</div>
          <DialogTitle class="mobile-nav-title">
            公开前台负责表达，工具与后台负责效率。
          </DialogTitle>
          <DialogDescription class="mobile-nav-description">
            移动端现在改用更有前台气质的对话框菜单，而不是后台式抽屉，但整体路由分层仍然保持不变。
          </DialogDescription>

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
            <button
              v-if="!auth.initialized || auth.loading"
              class="mobile-nav-card mobile-nav-account"
              type="button"
              disabled
            >
              <div class="mobile-nav-card-topline">
                <span class="mobile-nav-card-label">正在检查登录状态</span>
              </div>
              <p class="mobile-nav-card-caption">请稍等片刻。</p>
            </button>
            <div
              v-else-if="auth.authenticated"
              class="mobile-nav-card mobile-nav-account"
            >
              <div class="mobile-nav-card-topline">
                <img
                  v-if="auth.user?.avatar_url"
                  class="mobile-nav-avatar"
                  :src="auth.user.avatar_url"
                  :alt="auth.user.username"
                >
                <span class="mobile-nav-card-label">{{ auth.user?.username }}</span>
              </div>
              <p class="mobile-nav-card-caption">已登录，云端存档会绑定到当前账号。</p>
              <div class="mobile-nav-account-actions">
                <span class="mobile-nav-account-action mobile-nav-account-action-disabled">
                  个人信息
                  <small>占位符</small>
                </span>
                <RouterLink
                  class="mobile-nav-account-action"
                  to="/account/security"
                  @click="open = false"
                >
                  登录方式
                  <small>绑定管理</small>
                </RouterLink>
                <span
                  class="mobile-nav-account-action mobile-nav-account-action-danger"
                  role="button"
                  tabindex="0"
                  @click.stop="handleLogout"
                  @keydown.enter.stop.prevent="handleLogout"
                  @keydown.space.stop.prevent="handleLogout"
                >
                  登出
                  <small>结束会话</small>
                </span>
              </div>
            </div>
            <button
              v-else
              class="mobile-nav-card mobile-nav-account"
              type="button"
              @click="auth.openLoginPage()"
            >
              <div class="mobile-nav-card-topline">
                <span class="mobile-nav-card-label">登录</span>
              </div>
              <p class="mobile-nav-card-caption">登录后使用云端存档。</p>
            </button>
          </div>

          <DialogClose as-child>
            <button
              class="mobile-nav-close"
              type="button"
              aria-label="关闭站点导航"
            >
              <span aria-hidden="true">×</span>
            </button>
          </DialogClose>
        </div>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>

<style scoped>
.mobile-nav-trigger {
  align-items: center;
  background: var(--brand-color-accent, #102542);
  border: 0;
  border-radius: var(--brand-radius-pill, 999px);
  box-shadow: 0 18px 34px rgba(16, 37, 66, 0.18);
  color: #f7fbff;
  cursor: pointer;
  display: inline-flex;
  gap: 14px;
  min-height: 48px;
  padding: 0 14px 0 18px;
}

.mobile-nav-trigger-copy {
  display: flex;
  flex-direction: column;
  gap: 1px;
  text-align: left;
}

.mobile-nav-trigger-label {
  font-size: 0.94rem;
  font-weight: 700;
}

.mobile-nav-trigger-meta {
  color: rgba(255, 255, 255, 0.62);
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.mobile-nav-trigger-mark {
  color: var(--shell-lime);
  font-size: 1.2rem;
  font-weight: 700;
}

.mobile-nav-overlay {
  background: rgba(8, 15, 26, 0.56);
  inset: 0;
  position: fixed;
  z-index: 50;
}

.mobile-nav-content {
  inset: 0;
  outline: none;
  position: fixed;
  z-index: 60;
}

.mobile-nav-shell {
  backdrop-filter: blur(24px);
  background: rgba(250, 252, 255, 0.94);
  border-left: 1px solid rgba(16, 37, 66, 0.08);
  display: flex;
  flex-direction: column;
  gap: 18px;
  height: 100%;
  margin-left: auto;
  max-width: 420px;
  overflow-y: auto;
  padding: 28px 22px 22px;
  position: relative;
  width: min(92vw, 420px);
}

.mobile-nav-content[data-state='open'] .mobile-nav-shell {
  animation: mobile-nav-enter 220ms ease;
}

.mobile-nav-content[data-state='closed'] .mobile-nav-shell {
  animation: mobile-nav-exit 180ms ease;
}

.mobile-nav-topline,
.mobile-nav-group-label {
  color: rgba(16, 37, 66, 0.58);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.mobile-nav-title {
  color: var(--shell-navy);
  font-family: "Georgia", "Times New Roman", serif;
  font-size: clamp(1.55rem, 6.4vw, 2.1rem);
  font-weight: 600;
  line-height: 1.05;
  margin: 0;
  max-width: 16ch;
}

.mobile-nav-description {
  color: rgba(15, 23, 35, 0.74);
  font-size: 0.95rem;
  line-height: 1.68;
  margin: 0;
}

.mobile-nav-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mobile-nav-link,
.mobile-nav-card {
  color: inherit;
  text-decoration: none;
}

.mobile-nav-link {
  align-items: center;
  background: rgba(255, 255, 255, 0.66);
  border: 1px solid rgba(16, 37, 66, 0.08);
  border-radius: var(--brand-radius-md, 16px);
  display: grid;
  gap: 12px;
  grid-template-columns: auto 1fr;
  padding: 14px;
  transition:
    border-color 180ms ease,
    box-shadow 180ms ease,
    transform 180ms ease;
}

.mobile-nav-link-active,
.mobile-nav-link:hover,
.mobile-nav-card-active,
.mobile-nav-card:hover {
  border-color: rgba(16, 37, 66, 0.16);
  box-shadow: 0 18px 36px rgba(16, 37, 66, 0.1);
  transform: translateY(-2px);
}

.mobile-nav-link-icon,
.mobile-nav-card-icon {
  color: var(--shell-coral);
  display: inline-block;
  font-size: 1rem;
}

.mobile-nav-link-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mobile-nav-link-title,
.mobile-nav-card-label {
  color: var(--shell-navy);
  font-size: 1rem;
  font-weight: 700;
}

.mobile-nav-link-caption,
.mobile-nav-card-caption {
  color: rgba(15, 23, 35, 0.66);
  line-height: 1.55;
}

.mobile-nav-card {
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(16, 37, 66, 0.08);
  border-radius: var(--brand-radius-md, 16px);
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 14px;
  text-align: left;
}

.mobile-nav-account {
  font: inherit;
}

.mobile-nav-card-topline {
  align-items: center;
  display: flex;
  gap: 10px;
}

.mobile-nav-account-actions {
  display: grid;
  gap: 8px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-top: 2px;
}

.mobile-nav-account-action {
  background: rgba(16, 37, 66, 0.05);
  border-radius: var(--brand-radius-sm, 12px);
  color: var(--shell-navy);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  font-size: 0.82rem;
  font-weight: 800;
  gap: 2px;
  min-width: 0;
  padding: 10px 8px;
  text-decoration: none;
}

.mobile-nav-account-action:hover,
.mobile-nav-account-action:focus-visible {
  background: rgba(16, 37, 66, 0.08);
  outline: none;
}

.mobile-nav-account-action small {
  color: rgba(15, 23, 35, 0.52);
  font-size: 0.68rem;
  font-weight: 700;
}

.mobile-nav-account-action-disabled {
  cursor: default;
  opacity: 0.58;
}

.mobile-nav-account-action-danger {
  cursor: pointer;
}

.mobile-nav-account-action-danger:hover,
.mobile-nav-account-action-danger:focus-visible {
  background: rgba(211, 77, 61, 0.1);
  color: #9b2f25;
  outline: none;
}

.mobile-nav-avatar {
  border-radius: 999px;
  height: 28px;
  width: 28px;
}

.mobile-nav-close {
  align-items: center;
  background: rgba(16, 37, 66, 0.06);
  border: 0;
  border-radius: var(--brand-radius-pill, 999px);
  color: var(--shell-navy);
  cursor: pointer;
  display: inline-flex;
  font-size: 1.6rem;
  font-weight: 400;
  height: 42px;
  justify-content: center;
  position: absolute;
  right: 18px;
  top: 18px;
  width: 42px;
}

@keyframes mobile-nav-enter {
  from {
    opacity: 0;
    transform: translateX(24px);
  }

  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes mobile-nav-exit {
  from {
    opacity: 1;
    transform: translateX(0);
  }

  to {
    opacity: 0;
    transform: translateX(20px);
  }
}
</style>
