<script setup>
import { computed } from 'vue'

const props = defineProps({
  user: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['logout'])

const fallbackName = computed(() => props.user.username?.slice(0, 1)?.toUpperCase() || 'U')
const menuItems = computed(() => [
  [
    {
      type: 'label',
      label: props.user.username || '当前账号'
    },
    {
      label: '登录方式绑定',
      description: '管理 GitHub / LinuxDo 登录',
      icon: 'i-lucide-shield-check',
      to: '/account/security'
    },
    {
      label: '设置',
      description: '占位符，后续接偏好配置',
      icon: 'i-lucide-settings',
      disabled: true
    }
  ],
  [
    {
      label: '登出',
      description: '结束当前登录会话',
      icon: 'i-lucide-log-out',
      color: 'error',
      onSelect: () => emit('logout')
    }
  ]
])
</script>

<template>
  <UDropdownMenu
    :items="menuItems"
    :content="{ align: 'end', sideOffset: 8 }"
  >
    <UButton
      class="site-user-trigger"
      color="neutral"
      type="button"
      variant="subtle"
      trailing-icon="i-lucide-chevron-down"
      aria-label="打开账号菜单"
    >
      <UAvatar
        :alt="props.user.username"
        :src="props.user.avatar_url"
        size="xs"
        :text="fallbackName"
      />
      <span class="site-user-name">{{ props.user.username }}</span>
    </UButton>
  </UDropdownMenu>
</template>

<style scoped>
.site-user-trigger {
  min-height: 42px;
}

.site-user-name {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
