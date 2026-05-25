<template>
  <div class="app-shell">
    <header class="site-shell-header">
      <div class="site-shell-bar brand-floating-grid">
        <RouterLink
          to="/"
          class="site-brand"
        >
          <span class="site-brand-mark">XM</span>
          <span class="site-brand-copy">
            <span class="site-brand-kicker">Xinming</span>
            <span class="site-brand-title">个人站与工具平台</span>
          </span>
        </RouterLink>

        <div class="gt-sm">
          <SiteHeaderNavigation
            :items="primaryNavItems"
            :workspace-items="workspaceNavItems"
          />
        </div>

        <div class="site-shell-actions">
          <div class="site-shell-status gt-sm brand-panel-inset">
            <span class="site-shell-status-label">{{ shellStatus.label }}</span>
            <span class="site-shell-status-value">{{ shellStatus.value }}</span>
          </div>

          <div class="gt-sm">
            <SiteThemeSwitcher />
          </div>

          <div class="site-auth gt-sm">
            <button
              v-if="!auth.initialized || auth.loading"
              class="site-auth-button"
              type="button"
              disabled
            >
              检查登录
            </button>
            <SiteUserMenu
              v-else-if="auth.authenticated"
              :user="auth.user"
              @logout="auth.logout"
            />
            <button
              v-else
              class="site-auth-button site-auth-login"
              type="button"
              @click="auth.loginWithGitHub"
            >
              GitHub 登录
            </button>
          </div>

          <div class="lt-md">
            <SiteMobileNavigation
              :items="primaryNavItems"
              :workspace-items="workspaceNavItems"
            />
          </div>
        </div>
      </div>
    </header>

    <main class="site-shell-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import SiteHeaderNavigation from 'src/components/site/SiteHeaderNavigation.vue'
import SiteMobileNavigation from 'src/components/site/SiteMobileNavigation.vue'
import SiteThemeSwitcher from 'src/components/site/SiteThemeSwitcher.vue'
import SiteUserMenu from 'src/components/site/SiteUserMenu.vue'
import { primaryNavItems, shellStatus, workspaceNavItems } from 'src/lib/siteNavigation'
import { useAuthStore } from 'src/stores/auth'
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'

const auth = useAuthStore()

onMounted(() => {
  auth.refreshMe()
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
  min-height: calc(100vh - 78px);
}

.site-shell-bar {
  align-items: center;
  display: grid;
  gap: 22px;
  grid-template-columns: auto 1fr auto;
  margin: 0 auto;
  max-width: 1220px;
  min-height: 78px;
  padding: 0 20px;
  position: relative;
}

.site-brand {
  align-items: center;
  color: inherit;
  display: inline-flex;
  gap: 14px;
  min-width: 0;
  text-decoration: none;
}

.site-brand-mark {
  align-items: center;
  aspect-ratio: 1;
  background: var(--brand-color-accent);
  border-radius: var(--brand-radius-lg, 24px);
  box-shadow: 0 18px 34px rgba(16, 37, 66, 0.18);
  color: var(--brand-color-highlight, #ffffff);
  display: inline-flex;
  flex: 0 0 auto;
  font-size: 0.84rem;
  font-weight: 800;
  height: 44px;
  justify-content: center;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  width: 44px;
}

.site-brand-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.site-brand-kicker,
.site-shell-status-label {
  color: rgba(16, 37, 66, 0.54);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.site-brand-title {
  color: var(--shell-navy);
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.01em;
  white-space: nowrap;
}

.site-shell-actions {
  align-items: center;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.site-shell-status {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 158px;
  padding: 9px 13px;
}

.site-shell-status-value {
  color: var(--shell-navy);
  font-size: 0.94rem;
  font-weight: 700;
}

.site-auth-button {
  align-items: center;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid var(--brand-color-border, rgba(16, 37, 66, 0.12));
  border-radius: var(--brand-radius-pill, 999px);
  color: var(--shell-navy);
  cursor: pointer;
  display: inline-flex;
  font: inherit;
  font-size: 0.88rem;
  font-weight: 700;
  gap: 8px;
  min-height: 40px;
  padding: 0 13px;
}

.site-auth-login {
  background: var(--brand-color-accent, #102542);
  color: #ffffff;
}

@media (max-width: 1023px) {
  .site-shell-bar {
    grid-template-columns: 1fr auto;
  }
}

@media (max-width: 699px) {
  .site-shell-bar {
    min-height: 74px;
    padding: 0 16px;
  }

  .site-brand-title {
    font-size: 0.92rem;
  }
}
</style>
