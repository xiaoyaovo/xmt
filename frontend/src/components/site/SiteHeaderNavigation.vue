<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

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

const workspaceActiveLabel = computed(() => {
  const activeItem = props.workspaceItems.find(item => isRouteActive(item.to))
  return activeItem?.label ?? '查看分区'
})

const workspaceMenuItems = computed(() => [
  props.workspaceItems.map(item => ({
    label: item.label,
    description: item.caption,
    icon: item.icon,
    to: item.to,
    active: isRouteActive(item.to)
  }))
])

function isRouteActive(to, exact = false) {
  if (exact) {
    return route.path === to
  }

  return route.path === to || route.path.startsWith(`${to}/`)
}
</script>

<template>
  <nav
    class="site-nav-root"
    aria-label="站点导航"
  >
    <div class="site-nav-list">
      <UButton
        v-for="item in items"
        :key="item.to"
        class="site-nav-link"
        :active="isRouteActive(item.to, item.exact)"
        :active-color="'primary'"
        :active-variant="'solid'"
        color="neutral"
        :icon="item.icon"
        :label="item.label"
        :to="item.to"
        variant="ghost"
        :aria-current="isRouteActive(item.to, item.exact) ? 'page' : undefined"
      />

      <UDropdownMenu
        :items="workspaceMenuItems"
        :content="{ align: 'end', sideOffset: 10 }"
      >
        <UButton
          class="site-nav-trigger"
          :active="workspaceActiveLabel !== '查看分区'"
          active-color="primary"
          active-variant="solid"
          color="neutral"
          trailing-icon="i-lucide-chevron-down"
          type="button"
          variant="subtle"
        >
          <span class="site-nav-trigger-copy">
            <span class="site-nav-trigger-label">分区</span>
            <span class="site-nav-trigger-meta">{{ workspaceActiveLabel }}</span>
          </span>
        </UButton>
      </UDropdownMenu>
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
  min-height: 42px;
}

.site-nav-link[aria-current='page'] {
  background: var(--brand-color-accent);
  color: var(--ui-text-inverted, #ffffff);
}

.site-nav-link[aria-current='page']:hover,
.site-nav-link[aria-current='page']:focus-visible {
  background: var(--brand-color-accent-hover, var(--brand-color-accent));
}

.site-nav-trigger {
  min-height: 46px;
}

.site-nav-trigger[aria-pressed='true'],
.site-nav-trigger[data-state='open'] {
  background: var(--brand-color-accent);
  color: var(--ui-text-inverted, #ffffff);
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
}

.site-nav-trigger-meta {
  color: currentColor;
  font-size: 0.72rem;
  font-weight: 600;
  opacity: 0.72;
}
</style>
