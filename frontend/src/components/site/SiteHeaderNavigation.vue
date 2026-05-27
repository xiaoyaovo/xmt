<script setup>
import { computed, shallowRef } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

const props = defineProps({
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
const router = useRouter()
const workspaceOpen = shallowRef(false)

const workspaceActiveLabel = computed(() => {
  const activeItem = props.workspaceItems.find(item => isRouteActive(item.to))
  return activeItem?.label ?? '查看分区'
})

function isRouteActive(to, exact = false) {
  if (exact) {
    return route.path === to
  }

  return route.path === to || route.path.startsWith(`${to}/`)
}

function openWorkspace(item) {
  workspaceOpen.value = false
  router.push(item.to)
}
</script>

<template>
  <nav
    class="site-nav-root"
    aria-label="站点导航"
  >
    <div class="site-nav-list">
      <RouterLink
        v-for="item in items"
        :key="item.to"
        class="site-nav-link"
        :class="{ 'site-nav-link-active': isRouteActive(item.to, item.exact) }"
        :to="item.to"
        :aria-current="isRouteActive(item.to, item.exact) ? 'page' : undefined"
      >
        <span
          :class="item.icon"
          class="site-nav-link-icon"
          aria-hidden="true"
        />
        {{ item.label }}
      </RouterLink>

      <div class="site-nav-workspace">
        <button
          class="site-nav-trigger"
          :class="{ 'site-nav-trigger-active': workspaceActiveLabel !== '查看分区' }"
          type="button"
          :aria-expanded="workspaceOpen"
          aria-haspopup="menu"
          @click="workspaceOpen = !workspaceOpen"
        >
          <span class="site-nav-trigger-copy">
            <span class="site-nav-trigger-label">分区</span>
            <span class="site-nav-trigger-meta">{{ workspaceActiveLabel }}</span>
          </span>
          <span
            class="site-nav-trigger-chevron"
            aria-hidden="true"
          >▾</span>
        </button>

        <div
          v-if="workspaceOpen"
          class="site-nav-workspace-panel"
          role="menu"
        >
          <button
            v-for="item in workspaceItems"
            :key="item.to"
            class="site-nav-workspace-item"
            :class="{ 'site-nav-workspace-item-active': isRouteActive(item.to) }"
            type="button"
            role="menuitem"
            @click="openWorkspace(item)"
          >
            <span
              :class="item.icon"
              class="site-nav-workspace-icon"
              aria-hidden="true"
            />
            <span class="site-nav-workspace-copy">
              <span class="site-nav-workspace-title">{{ item.label }}</span>
              <span class="site-nav-workspace-caption">{{ item.caption }}</span>
            </span>
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.site-nav-root {
  position: relative;
}

.site-nav-list {
  align-items: center;
  display: flex;
  gap: 8px;
}

.site-nav-link {
  align-items: center;
  border-radius: var(--brand-radius-pill, 999px);
  color: rgba(16, 37, 66, 0.78);
  display: inline-flex;
  font-size: 0.94rem;
  font-weight: 750;
  gap: 8px;
  min-height: 42px;
  padding: 0 14px;
  text-decoration: none;
  transition:
    background-color 160ms ease,
    color 160ms ease;
}

.site-nav-link:hover,
.site-nav-link:focus-visible {
  background: rgba(255, 255, 255, 0.76);
  color: var(--brand-color-accent, #102542);
  outline: none;
}

.site-nav-link-icon {
  color: var(--shell-coral);
  display: inline-block;
  flex: 0 0 auto;
  font-size: 1rem;
}

.site-nav-link-active,
.site-nav-trigger-active {
  background: var(--brand-color-accent, #102542);
  color: #f8fbff;
}

.site-nav-trigger {
  align-items: center;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(16, 37, 66, 0.1);
  border-radius: var(--brand-radius-pill, 999px);
  color: rgba(16, 37, 66, 0.78);
  cursor: pointer;
  display: inline-flex;
  gap: 10px;
  font: inherit;
  min-height: 46px;
  padding: 0 14px;
}

.site-nav-workspace {
  position: relative;
}

.site-nav-trigger-copy {
  display: flex;
  flex-direction: column;
  gap: 1px;
  line-height: 1.05;
  text-align: left;
}

.site-nav-trigger-label {
  font-weight: 750;
  letter-spacing: 0;
}

.site-nav-trigger-meta {
  color: currentColor;
  font-size: 0.72rem;
  font-weight: 600;
  opacity: 0.64;
}

.site-nav-trigger-chevron {
  color: currentColor;
  font-size: 0.8rem;
  opacity: 0.64;
}

.site-nav-workspace-panel {
  background: #ffffff;
  border: 1px solid rgba(16, 37, 66, 0.1);
  border-radius: var(--brand-radius-md, 16px);
  box-shadow: 0 18px 42px rgba(16, 37, 66, 0.16);
  display: grid;
  gap: 6px;
  min-width: 260px;
  padding: 8px;
  position: absolute;
  right: 0;
  top: calc(100% + 10px);
  z-index: 50;
}

.site-nav-workspace-item {
  align-items: center;
  background: transparent;
  border: 0;
  border-radius: var(--brand-radius-sm, 8px);
  color: var(--shell-navy);
  cursor: pointer;
  display: flex;
  gap: 10px;
  padding: 10px;
  text-align: left;
}

.site-nav-workspace-item:hover,
.site-nav-workspace-item-active {
  background: rgba(16, 37, 66, 0.07);
}

.site-nav-workspace-icon {
  color: var(--shell-coral);
  flex: 0 0 auto;
}

.site-nav-workspace-copy {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.site-nav-workspace-title {
  font-size: 0.9rem;
  font-weight: 800;
}

.site-nav-workspace-caption {
  color: rgba(15, 23, 35, 0.58);
  font-size: 0.78rem;
  line-height: 1.45;
}

html.dark .site-nav-workspace-panel {
  background: #111827;
  border-color: rgba(148, 163, 184, 0.2);
}
</style>
