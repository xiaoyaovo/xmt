<script setup>
import {
  HoverCardContent,
  HoverCardPortal,
  HoverCardRoot,
  HoverCardTrigger
} from 'reka-ui'
import { shallowRef } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps({
  user: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['logout'])

const open = shallowRef(false)

function toggleMenu() {
  open.value = !open.value
}

function handleLogout() {
  open.value = false
  emit('logout')
}
</script>

<template>
  <HoverCardRoot
    v-model:open="open"
    :open-delay="80"
    :close-delay="260"
  >
    <HoverCardTrigger as-child>
      <button
        class="site-user-trigger"
        :class="{ 'site-user-trigger-open': open }"
        type="button"
        aria-label="打开账号菜单"
        :aria-expanded="open"
        @click="toggleMenu"
      >
        <img
          v-if="props.user.avatar_url"
          class="site-user-avatar"
          :src="props.user.avatar_url"
          :alt="props.user.username"
        >
        <span
          v-else
          class="site-user-avatar site-user-avatar-fallback"
          aria-hidden="true"
        >
          {{ props.user.username?.slice(0, 1)?.toUpperCase() || 'U' }}
        </span>
        <span class="site-user-name">{{ props.user.username }}</span>
        <span
          class="site-user-chevron"
          aria-hidden="true"
        >
          /
        </span>
      </button>
    </HoverCardTrigger>

    <HoverCardPortal>
      <HoverCardContent
        class="site-user-panel"
        align="end"
        :side-offset="8"
        :collision-padding="16"
      >
        <div class="site-user-panel-bridge" />

        <div class="site-user-label">
          <span class="site-user-label-kicker">当前账号</span>
          <span class="site-user-label-name">{{ props.user.username }}</span>
        </div>

        <div class="site-user-separator" />

        <RouterLink
          class="site-user-item"
          to="/account/security"
          @click="open = false"
        >
          <span class="site-user-item-copy">
            <span class="site-user-item-title">登录方式绑定</span>
            <span class="site-user-item-caption">管理 GitHub / LinuxDo 登录</span>
          </span>
        </RouterLink>

        <button
          class="site-user-item site-user-item-disabled"
          type="button"
          disabled
        >
          <span class="site-user-item-copy">
            <span class="site-user-item-title">设置</span>
            <span class="site-user-item-caption">占位符，后续接偏好配置</span>
          </span>
        </button>

        <div class="site-user-separator" />

        <button
          class="site-user-item site-user-item-danger"
          type="button"
          @click="handleLogout"
        >
          <span class="site-user-item-copy">
            <span class="site-user-item-title">登出</span>
            <span class="site-user-item-caption">结束当前登录会话</span>
          </span>
        </button>
      </HoverCardContent>
    </HoverCardPortal>
  </HoverCardRoot>
</template>

<style scoped>
.site-user-trigger {
  align-items: center;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid var(--brand-color-border, rgba(16, 37, 66, 0.12));
  border-radius: var(--brand-radius-pill, 999px);
  color: var(--shell-navy);
  cursor: pointer;
  display: inline-flex;
  font: inherit;
  font-size: 0.88rem;
  font-weight: 800;
  gap: 9px;
  min-height: 42px;
  padding: 0 12px 0 8px;
  transition:
    background-color 180ms ease,
    border-color 180ms ease,
    box-shadow 180ms ease;
}

.site-user-trigger:hover,
.site-user-trigger:focus-visible,
.site-user-trigger-open {
  background: #ffffff;
  border-color: rgba(16, 37, 66, 0.18);
  box-shadow: 0 18px 34px rgba(16, 37, 66, 0.12);
  outline: none;
}

.site-user-avatar {
  aspect-ratio: 1;
  border: 2px solid rgba(255, 255, 255, 0.86);
  border-radius: var(--brand-radius-pill, 999px);
  box-shadow: 0 8px 18px rgba(16, 37, 66, 0.14);
  flex: 0 0 auto;
  height: 28px;
  object-fit: cover;
  width: 28px;
}

.site-user-avatar-fallback {
  align-items: center;
  background: var(--brand-color-accent, #102542);
  color: #ffffff;
  display: inline-flex;
  font-size: 0.8rem;
  justify-content: center;
}

.site-user-name {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.site-user-chevron {
  color: rgba(16, 37, 66, 0.42);
  font-weight: 900;
  transition: transform 180ms ease;
}

.site-user-trigger-open .site-user-chevron {
  transform: rotate(22deg);
}
</style>

<style>
.site-user-panel {
  backdrop-filter: blur(20px);
  background: rgba(250, 252, 255, 0.97);
  border: 1px solid rgba(16, 37, 66, 0.1);
  border-radius: var(--brand-radius-lg, 24px);
  box-shadow: 0 24px 60px rgba(16, 37, 66, 0.18);
  color: var(--shell-navy);
  display: flex;
  flex-direction: column;
  min-width: 240px;
  outline: none;
  overflow: visible;
  padding: 10px;
  z-index: 80;
}

.site-user-panel-bridge {
  height: 12px;
  left: 0;
  position: absolute;
  right: 0;
  top: -12px;
}

.site-user-panel[data-state='open'] {
  animation: site-user-panel-enter 150ms ease;
}

.site-user-label {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 11px;
}

.site-user-label-kicker {
  color: rgba(16, 37, 66, 0.5);
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.site-user-label-name {
  color: var(--shell-navy);
  font-size: 0.96rem;
  font-weight: 800;
}

.site-user-separator {
  background: rgba(16, 37, 66, 0.08);
  height: 1px;
  margin: 8px 4px;
}

.site-user-item {
  background: transparent;
  border: 0;
  border-radius: var(--brand-radius-md, 16px);
  color: var(--shell-navy);
  cursor: pointer;
  display: flex;
  font: inherit;
  padding: 10px 11px;
  text-decoration: none;
  text-align: left;
  transition:
    background-color 160ms ease,
    color 160ms ease;
  width: 100%;
}

.site-user-item:hover,
.site-user-item:focus-visible {
  background: rgba(16, 37, 66, 0.06);
  outline: none;
}

.site-user-item-disabled {
  cursor: default;
  opacity: 0.62;
}

.site-user-item-disabled:hover {
  background: transparent;
}

.site-user-item-danger:hover,
.site-user-item-danger:focus-visible {
  background: rgba(211, 77, 61, 0.1);
  color: #9b2f25;
}

.site-user-item-copy {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.site-user-item-title {
  color: inherit;
  font-size: 0.9rem;
  font-weight: 800;
}

.site-user-item-caption {
  color: rgba(15, 23, 35, 0.58);
  font-size: 0.74rem;
  line-height: 1.45;
}

@keyframes site-user-panel-enter {
  from {
    opacity: 0;
    transform: translateY(-4px) scale(0.99);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
</style>
