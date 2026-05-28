<script setup>
import { computed } from 'vue'

const props = defineProps({
  open: {
    type: Boolean,
    default: false
  },
  busy: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:open', 'confirm'])

const isOpen = computed({
  get: () => props.open,
  set: (value) => emit('update:open', value)
})

function handleConfirm() {
  emit('confirm')
}
</script>

<template>
  <UModal
    v-model:open="isOpen"
    title="删除当前账号"
    description="删除后将移除当前账号、全部登录方式、云端同步数据、CSV 历史与已上传文件。此操作无法恢复。"
    :ui="{ content: 'max-w-[512px]' }"
  >
    <template #body>
      <UAlert
        color="error"
        icon="i-lucide-triangle-alert"
        title="危险操作"
        variant="soft"
        description="请确认你同意删除所有相关数据。"
      />
      <UAlert
        v-if="error"
        class="account-delete-dialog-error"
        color="error"
        variant="subtle"
        :description="error"
      />
    </template>

    <template #footer>
      <div class="account-delete-dialog-actions">
        <UButton
          color="neutral"
          type="button"
          variant="ghost"
          :disabled="busy"
          @click="isOpen = false"
        >
          取消
        </UButton>
        <UButton
          color="error"
          type="button"
          :loading="busy"
          @click="handleConfirm"
        >
          同意删除所有相关数据
        </UButton>
      </div>
    </template>
  </UModal>
</template>

<style scoped>
.account-delete-dialog-error {
  margin-top: 12px;
}

.account-delete-dialog-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
  width: 100%;
}

@media (max-width: 520px) {
  .account-delete-dialog-actions {
    flex-direction: column;
  }
}
</style>
