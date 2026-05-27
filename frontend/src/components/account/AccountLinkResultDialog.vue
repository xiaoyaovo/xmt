<script setup>
import { computed } from 'vue'

const props = defineProps({
  open: {
    type: Boolean,
    default: false
  },
  status: {
    type: String,
    default: ''
  },
  providerLabel: {
    type: String,
    default: '第三方账号'
  },
  message: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:open', 'login', 'retry'])

const isOpen = computed({
  get: () => props.open,
  set: (value) => emit('update:open', value)
})

const isSuccess = computed(() => props.status === 'linked')
const isConflict = computed(() => props.status === 'conflict')
const needsLogin = computed(() => props.status === 'auth_required')
const alertColor = computed(() => (isSuccess.value ? 'success' : 'warning'))
const alertIcon = computed(() => (isSuccess.value ? 'i-lucide-circle-check' : 'i-lucide-circle-alert'))

const dialogTitle = computed(() => {
  if (isSuccess.value) return `${props.providerLabel} 已绑定`
  if (props.status === 'conflict') return `${props.providerLabel} 无法绑定`
  if (needsLogin.value) return '需要重新登录'
  return '绑定没有完成'
})

const dialogDescription = computed(() => {
  if (props.message) return props.message
  if (isSuccess.value) return `${props.providerLabel} 已经可以用于登录当前账号。`
  if (props.status === 'conflict') {
    return `${props.providerLabel} 已经绑定到另一个账号。请先登录那个账号解绑，或换一个账号继续绑定。`
  }
  if (needsLogin.value) return '登录状态已失效，请重新登录后再绑定账号。'
  return `${props.providerLabel} 绑定没有完成，请稍后重试。`
})

function handleLogin() {
  emit('login')
}

function handleRetry() {
  emit('retry')
}
</script>

<template>
  <UModal
    v-model:open="isOpen"
    :title="dialogTitle"
    :description="dialogDescription"
    :ui="{ content: 'max-w-lg' }"
  >
    <template #body>
      <UAlert
        :color="alertColor"
        :icon="alertIcon"
        title="登录方式绑定"
        variant="soft"
        :description="dialogDescription"
      />
    </template>

    <template #footer>
      <div class="account-link-dialog-actions">
        <UButton
          v-if="needsLogin"
          color="primary"
          type="button"
          @click="handleLogin"
        >
          重新登录
        </UButton>
        <UButton
          v-else-if="isConflict"
          color="primary"
          type="button"
          @click="handleRetry"
        >
          换一个账号绑定
        </UButton>
        <UButton
          color="neutral"
          type="button"
          variant="ghost"
          @click="isOpen = false"
        >
          知道了
        </UButton>
      </div>
    </template>
  </UModal>
</template>

<style scoped>
.account-link-dialog-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
  width: 100%;
}

@media (max-width: 520px) {
  .account-link-dialog-actions {
    flex-direction: column;
  }
}
</style>
