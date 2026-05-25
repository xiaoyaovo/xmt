<script setup>
import {
  NavigationMenuContent,
  NavigationMenuIndicator,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuRoot,
  NavigationMenuTrigger,
  TooltipContent,
  TooltipPortal,
  TooltipProvider,
  TooltipRoot,
  TooltipTrigger
} from 'reka-ui'
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

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

function isRouteActive(to, exact = false) {
  if (exact) {
    return route.path === to
  }

  return route.path === to || route.path.startsWith(`${to}/`)
}
</script>

<template>
  <TooltipProvider :delay-duration="120">
    <NavigationMenuRoot
      class="site-nav-root"
      :delay-duration="90"
      :skip-delay-duration="180"
    >
      <NavigationMenuList class="site-nav-list">
        <NavigationMenuItem
          v-for="item in items"
          :key="item.to"
          class="site-nav-item"
        >
          <TooltipRoot>
            <TooltipTrigger as-child>
              <NavigationMenuLink
                as-child
                :active="isRouteActive(item.to, item.exact)"
              >
                <RouterLink
                  :to="item.to"
                  class="site-nav-link"
                  :aria-current="isRouteActive(item.to, item.exact) ? 'page' : undefined"
                >
                  <span
                    :class="item.icon"
                    class="site-nav-link-icon"
                    aria-hidden="true"
                  />
                  <span>{{ item.label }}</span>
                </RouterLink>
              </NavigationMenuLink>
            </TooltipTrigger>

            <TooltipPortal>
              <TooltipContent
                class="site-nav-tooltip"
                side="bottom"
                :side-offset="14"
              >
                {{ item.caption }}
              </TooltipContent>
            </TooltipPortal>
          </TooltipRoot>
        </NavigationMenuItem>

        <NavigationMenuItem
          value="workspaces"
          class="site-nav-item"
        >
          <NavigationMenuTrigger
            class="site-nav-trigger"
            :class="{ 'site-nav-trigger-active': workspaceActiveLabel !== '查看分区' }"
          >
            <span class="site-nav-trigger-copy">
              <span class="site-nav-trigger-label">分区</span>
              <span class="site-nav-trigger-meta">{{ workspaceActiveLabel }}</span>
            </span>
            <span
              class="site-nav-trigger-chevron"
              aria-hidden="true"
            >
              /
            </span>
          </NavigationMenuTrigger>

          <NavigationMenuContent class="site-nav-panel">
            <div class="site-nav-panel-copy">
              <div class="site-nav-panel-kicker">结构分层</div>
              <h2 class="site-nav-panel-title">公开前台负责表达，工具与后台负责效率。</h2>
              <p class="site-nav-panel-text">
                公开页面现在使用更适合品牌化表达的无样式交互原语，而工具区和后台区继续保留它们真正受益的应用型壳层。
              </p>
            </div>

            <div class="site-nav-panel-grid">
              <NavigationMenuLink
                v-for="item in workspaceItems"
                :key="item.to"
                as-child
                :active="isRouteActive(item.to)"
              >
                <RouterLink
                  :to="item.to"
                  class="site-nav-card"
                  :aria-current="isRouteActive(item.to) ? 'page' : undefined"
                >
                  <div class="site-nav-card-topline">
                    <span
                      :class="item.icon"
                      class="site-nav-card-icon"
                      aria-hidden="true"
                    />
                    <span class="site-nav-card-label">{{ item.label }}</span>
                  </div>
                  <p class="site-nav-card-caption">{{ item.caption }}</p>
                  <p class="site-nav-card-detail">{{ item.detail }}</p>
                </RouterLink>
              </NavigationMenuLink>
            </div>
          </NavigationMenuContent>
        </NavigationMenuItem>

        <NavigationMenuIndicator class="site-nav-indicator" />
      </NavigationMenuList>
    </NavigationMenuRoot>
  </TooltipProvider>
</template>

<style>
.site-nav-root {
  position: relative;
}

.site-nav-list {
  align-items: center;
  display: flex;
  gap: 8px;
  list-style: none;
  margin: 0;
  padding: 0;
  position: relative;
}

.site-nav-item {
  position: relative;
}

.site-nav-link,
.site-nav-trigger {
  align-items: center;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid transparent;
  border-radius: var(--brand-radius-pill, 999px);
  color: rgba(16, 37, 66, 0.78);
  cursor: pointer;
  display: inline-flex;
  font-size: 0.94rem;
  font-weight: 700;
  gap: 10px;
  min-height: 46px;
  padding: 0 16px;
  text-decoration: none;
  transition:
    background-color 180ms ease,
    border-color 180ms ease,
    color 180ms ease,
    transform 180ms ease,
    box-shadow 180ms ease;
}

.site-nav-link:hover,
.site-nav-trigger:hover,
.site-nav-link:focus-visible,
.site-nav-trigger:focus-visible {
  background: rgba(255, 255, 255, 0.88);
  border-color: rgba(16, 37, 66, 0.1);
  color: var(--brand-color-accent, #102542);
  outline: none;
  transform: translateY(-1px);
}

.site-nav-link[data-active],
.site-nav-trigger-active {
  background: var(--brand-color-accent, #102542);
  box-shadow: 0 18px 36px rgba(16, 37, 66, 0.18);
  color: #f8fbff;
}

.site-nav-link[data-active] .site-nav-link-icon,
.site-nav-trigger-active .site-nav-trigger-meta,
.site-nav-trigger-active .site-nav-trigger-chevron {
  color: rgba(255, 255, 255, 0.78);
}

.site-nav-link-icon {
  color: var(--shell-coral);
  display: inline-block;
  flex: 0 0 auto;
  font-size: 1rem;
}

.site-nav-trigger-copy {
  display: flex;
  flex-direction: column;
  gap: 1px;
  line-height: 1.05;
  text-align: left;
}

.site-nav-trigger-label {
  letter-spacing: 0.02em;
}

.site-nav-trigger-meta {
  color: rgba(16, 37, 66, 0.48);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.site-nav-trigger-chevron {
  color: rgba(16, 37, 66, 0.44);
  font-size: 1rem;
  margin-left: 2px;
  transition: transform 180ms ease;
}

.site-nav-trigger[data-state='open'] .site-nav-trigger-chevron {
  transform: rotate(22deg);
}

.site-nav-panel {
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(16, 37, 66, 0.08);
  border-radius: var(--brand-radius-lg, 24px);
  box-shadow: 0 24px 80px rgba(16, 37, 66, 0.18);
  display: grid;
  gap: 22px;
  grid-template-columns: minmax(230px, 0.82fr) minmax(360px, 1.18fr);
  left: 50%;
  margin-top: 18px;
  min-width: 760px;
  padding: 24px;
  position: absolute;
  top: 100%;
  transform: translateX(-50%);
  z-index: 30;
}

.site-nav-panel[data-motion='from-start'] {
  animation: site-nav-slide-in-left 220ms ease;
}

.site-nav-panel[data-motion='from-end'] {
  animation: site-nav-slide-in-right 220ms ease;
}

.site-nav-panel-copy {
  border-right: 1px solid rgba(16, 37, 66, 0.08);
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-right: 18px;
}

.site-nav-panel-kicker {
  color: rgba(16, 37, 66, 0.56);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.site-nav-panel-title {
  color: var(--shell-navy);
  font-family: "Georgia", "Times New Roman", serif;
  font-size: 1.72rem;
  font-weight: 600;
  line-height: 1.08;
  margin: 0;
}

.site-nav-panel-text {
  color: rgba(15, 23, 35, 0.72);
  line-height: 1.72;
  margin: 0;
}

.site-nav-panel-grid {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.site-nav-card {
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(16, 37, 66, 0.08);
  border-radius: var(--brand-radius-md, 16px);
  color: inherit;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 220px;
  padding: 18px;
  text-decoration: none;
  transition:
    border-color 180ms ease,
    box-shadow 180ms ease,
    transform 180ms ease;
}

.site-nav-card:hover,
.site-nav-card:focus-visible,
.site-nav-card[data-active] {
  border-color: rgba(16, 37, 66, 0.18);
  box-shadow: 0 18px 42px rgba(16, 37, 66, 0.12);
  outline: none;
  transform: translateY(-4px);
}

.site-nav-card-topline {
  align-items: center;
  display: flex;
  gap: 10px;
}

.site-nav-card-icon {
  color: var(--shell-coral);
  display: inline-block;
  font-size: 1rem;
}

.site-nav-card-label {
  color: var(--shell-navy);
  font-size: 1.06rem;
  font-weight: 700;
}

.site-nav-card-caption,
.site-nav-card-detail {
  line-height: 1.65;
  margin: 0;
}

.site-nav-card-caption {
  color: rgba(15, 23, 35, 0.76);
}

.site-nav-card-detail {
  color: rgba(16, 37, 66, 0.54);
  font-size: 0.92rem;
}

.site-nav-indicator {
  background: var(--brand-color-accent2, var(--shell-coral));
  border-radius: var(--brand-radius-pill, 999px);
  bottom: -8px;
  height: 3px;
  left: 0;
  position: absolute;
  transform: translateX(var(--reka-navigation-menu-indicator-position));
  transition:
    width 220ms ease,
    transform 220ms ease,
    opacity 180ms ease;
  width: var(--reka-navigation-menu-indicator-size);
}

.site-nav-indicator[data-state='hidden'] {
  opacity: 0;
}

.site-nav-tooltip {
  background: rgba(16, 37, 66, 0.96);
  border-radius: var(--brand-radius-sm, 8px);
  color: #edf4ff;
  font-size: 0.8rem;
  line-height: 1.4;
  max-width: 240px;
  padding: 9px 12px;
}

@keyframes site-nav-slide-in-left {
  from {
    opacity: 0;
    transform: translateX(calc(-50% + 18px)) translateY(8px);
  }

  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

@keyframes site-nav-slide-in-right {
  from {
    opacity: 0;
    transform: translateX(calc(-50% - 18px)) translateY(8px);
  }

  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}
</style>
