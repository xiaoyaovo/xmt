<script setup>
import { computed, onBeforeUnmount, onMounted, shallowRef } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps({
  user: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['logout'])

const open = shallowRef(false)
const fallbackName = computed(() => props.user.username?.slice(0, 1)?.toUpperCase() || 'U')

function closeMenu(event) {
  if (!event.target.closest?.('.site-user-menu')) {
    open.value = false
  }
}

function handleLogout() {
  open.value = false
  emit('logout')
}

onMounted(() => {
  document.addEventListener('click', closeMenu)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', closeMenu)
})
</script>

<template>
  <div class="site-user-menu">
    <button
      class="site-user-trigger"
      type="button"
      aria-label="打开账号菜单"
      :aria-expanded="open"
      @click.stop="open = !open"
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
        {{ fallbackName }}
      </span>
      <span class="site-user-name">{{ props.user.username }}</span>
      <span
        class="site-user-chevron"
        aria-hidden="true"
      >▾</span>
    </button>

    <div
      v-if="open"
      class="site-user-panel"
      role="menu"
    >
      <div class="site-user-label">
        <span class="site-user-label-kicker">当前账号</span>
        <span class="site-user-label-name">{{ props.user.username }}</span>
      </div>

      <div class="site-user-separator" />

      <RouterLink
        class="site-user-item"
        to="/account/security"
        role="menuitem"
        @click="open = false"
      >
        <span class="site-user-item-title">登录方式绑定</span>
        <span class="site-user-item-caption">管理 GitHub / LinuxDo 登录</span>
      </RouterLink>

      <button
        class="site-user-item site-user-item-disabled"
        type="button"
        disabled
        role="menuitem"
      >
        <span class="site-user-item-title">设置</span>
        <span class="site-user-item-caption">占位符，后续接偏好配置</span>
      </button>

      <div class="site-user-separator" />

      <button
        class="site-user-item site-user-item-danger"
        type="button"
        role="menuitem"
        @click="handleLogout"
      >
        <span class="site-user-item-title">登出</span>
        <span class="site-user-item-caption">结束当前登录会话</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.site-user-menu {
  position: relative;
}

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
}

.site-user-trigger:hover,
.site-user-trigger:focus-visible {
  background: #ffffff;
  border-color: rgba(16, 37, 66, 0.18);
  outline: none;
}

.site-user-avatar {
  aspect-ratio: 1;
  border-radius: var(--brand-radius-pill, 999px);
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
  font-size: 0.82rem;
}

.site-user-panel {
  background: rgba(250, 252, 255, 0.98);
  border: 1px solid rgba(16, 37, 66, 0.1);
  border-radius: var(--brand-radius-md, 16px);
  box-shadow: 0 18px 42px rgba(16, 37, 66, 0.16);
  color: var(--shell-navy);
  display: flex;
  flex-direction: column;
  min-width: 240px;
  padding: 8px;
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  z-index: 60;
}

.site-user-label {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px;
}

.site-user-label-kicker {
  color: rgba(16, 37, 66, 0.5);
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.site-user-label-name {
  font-weight: 850;
}

.site-user-separator {
  background: rgba(16, 37, 66, 0.08);
  height: 1px;
  margin: 4px 0;
}

.site-user-item {
  background: transparent;
  border: 0;
  border-radius: var(--brand-radius-sm, 8px);
  color: inherit;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  font: inherit;
  gap: 3px;
  padding: 10px;
  text-align: left;
  text-decoration: none;
}

.site-user-item:hover,
.site-user-item:focus-visible {
  background: rgba(16, 37, 66, 0.07);
  outline: none;
}

.site-user-item-title {
  font-size: 0.9rem;
  font-weight: 800;
}

.site-user-item-caption {
  color: rgba(15, 23, 35, 0.58);
  font-size: 0.78rem;
}

.site-user-item-disabled {
  cursor: not-allowed;
  opacity: 0.58;
}

.site-user-item-danger {
  color: #9b2f25;
}

html.dark .site-user-trigger,
html.dark .site-user-panel {
  background: rgba(17, 24, 39, 0.92);
  border-color: rgba(148, 163, 184, 0.2);
}
</style>
