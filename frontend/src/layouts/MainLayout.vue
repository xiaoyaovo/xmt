<template>
  <div class="app-shell">
    <header class="site-shell-header">
      <div class="site-shell-bar">
        <UButton
          to="/"
          class="site-brand"
          color="neutral"
          variant="ghost"
        >
          <span class="site-brand-mark">XM</span>
          <span class="site-brand-copy">
            <span class="site-brand-title">Xinming</span>
          </span>
        </UButton>

        <div class="gt-sm site-shell-nav">
          <SiteHeaderNavigation
            :items="primaryNavItems"
            :workspace-items="workspaceNavItems"
          />
        </div>

        <div class="site-shell-actions">
          <div class="gt-sm">
            <SiteThemeSwitcher />
          </div>

          <div class="site-auth gt-sm">
            <UButton
              v-if="!auth.initialized || auth.loading"
              class="site-auth-button"
              color="neutral"
              label="检查登录"
              loading
              type="button"
              disabled
            />
            <SiteUserMenu
              v-else-if="auth.authenticated"
              :user="auth.user"
              @logout="auth.logout"
            />
            <UButton
              v-else
              class="site-auth-button site-auth-login"
              color="primary"
              label="登录"
              type="button"
              @click="auth.openLoginPage()"
            />
          </div>

          <div
            v-if="isMobileNavigationMounted"
            class="lt-md"
          >
            <SiteMobileNavigation
              :items="primaryNavItems"
              :workspace-items="workspaceNavItems"
            />
          </div>
        </div>
      </div>
    </header>

    <main class="site-shell-main">
      <router-view v-slot="{ Component, route }">
        <transition
          name="page-fade"
          mode="out-in"
        >
          <component
            :is="Component"
            :key="route.path"
          />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import SiteHeaderNavigation from 'src/components/site/SiteHeaderNavigation.vue'
import SiteMobileNavigation from 'src/components/site/SiteMobileNavigation.vue'
import SiteThemeSwitcher from 'src/components/site/SiteThemeSwitcher.vue'
import SiteUserMenu from 'src/components/site/SiteUserMenu.vue'
import { primaryNavItems, workspaceNavItems } from 'src/lib/siteNavigation'
import { useAuthStore } from 'src/stores/auth'
import { onMounted, shallowRef } from 'vue'

const auth = useAuthStore()
const isMobileNavigationMounted = shallowRef(false)

onMounted(() => {
  auth.refreshMe()
  isMobileNavigationMounted.value = window.matchMedia('(max-width: 1023px)').matches
})
</script>

<style scoped>
.site-shell-header {
  background: rgba(247, 250, 253, 0.88);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(16, 37, 66, 0.08);
  left: 0;
  position: sticky;
  right: 0;
  top: 0;
  z-index: 40;
}

.site-shell-main {
  min-height: calc(100vh - 64px);
}

.site-shell-bar {
  align-items: center;
  display: grid;
  gap: 22px;
  grid-template-columns: auto 1fr auto;
  margin: 0 auto;
  max-width: 1220px;
  min-height: 64px;
  padding: 0 20px;
  position: relative;
}

.site-brand {
  gap: 12px;
  min-width: 0;
}

.site-brand-mark {
  align-items: center;
  aspect-ratio: 1;
  background: var(--brand-color-accent);
  border-radius: var(--brand-radius-md, 16px);
  box-shadow: 0 10px 24px rgba(16, 37, 66, 0.16);
  color: var(--brand-color-highlight, #ffffff);
  display: inline-flex;
  flex: 0 0 auto;
  font-size: 0.78rem;
  font-weight: 800;
  height: 36px;
  justify-content: center;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  width: 36px;
}

.site-brand-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.site-brand-title {
  color: var(--shell-navy);
  font-size: 0.98rem;
  font-weight: 700;
  letter-spacing: 0.01em;
  white-space: nowrap;
}

.site-shell-nav {
  justify-self: center;
}

.site-shell-actions {
  align-items: center;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.site-auth-button {
  min-height: 36px;
}

@media (max-width: 1023px) {
  .site-shell-bar {
    grid-template-columns: 1fr auto;
  }
}

@media (max-width: 699px) {
  .site-shell-bar {
    min-height: 60px;
    padding: 0 16px;
  }

  .site-brand-title {
    font-size: 0.92rem;
  }
}
</style>

<style>
/* Global so transition applies to teleported route content */
.page-fade-enter-active {
  transition:
    opacity 180ms cubic-bezier(0.22, 0.61, 0.36, 1),
    transform 180ms cubic-bezier(0.22, 0.61, 0.36, 1);
}

.page-fade-leave-active {
  transition:
    opacity 120ms cubic-bezier(0.22, 0.61, 0.36, 1),
    transform 120ms cubic-bezier(0.22, 0.61, 0.36, 1);
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (prefers-reduced-motion: reduce) {
  .page-fade-enter-active,
  .page-fade-leave-active {
    transition: none;
  }

  .page-fade-enter-from,
  .page-fade-leave-to {
    opacity: 1;
    transform: none;
  }
}
</style>
