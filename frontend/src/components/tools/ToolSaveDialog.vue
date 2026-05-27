<script setup>
import { computed, nextTick, shallowRef, useTemplateRef, watch } from 'vue'

const props = defineProps({
  open: {
    type: Boolean,
    default: false
  },
  defaultTitle: {
    type: String,
    default: ''
  },
  defaultRemark: {
    type: String,
    default: ''
  },
  dialogTitle: {
    type: String,
    default: '保存到云端存档'
  },
  dialogDescription: {
    type: String,
    default: '给这个存档取个名字，方便以后在历史里认出来。'
  },
  busy: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:open', 'confirm', 'cancel'])

const titleInput = shallowRef('')
const remarkInput = shallowRef('')
const titleRef = useTemplateRef('titleInputEl')

const isOpen = computed({
  get: () => props.open,
  set: (value) => emit('update:open', value)
})

watch(
  () => props.open,
  async (value) => {
    if (value) {
      titleInput.value = props.defaultTitle || ''
      remarkInput.value = props.defaultRemark || ''
      await nextTick()
      titleRef.value?.inputRef?.focus?.()
      titleRef.value?.inputRef?.select?.()
    }
  }
)

function handleConfirm() {
  if (props.busy) return
  emit('confirm', {
    title: titleInput.value.trim(),
    remark: remarkInput.value.trim()
  })
}

function handleCancel() {
  emit('cancel')
  isOpen.value = false
}

function handleTitleKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleConfirm()
  }
}
</script>

<template>
  <UModal
    v-model:open="isOpen"
    :title="dialogTitle"
    :description="dialogDescription"
    :ui="{ content: 'max-w-md' }"
  >
    <template #body>
      <div class="tool-save-dialog-form">
        <UFormField
          label="名称"
          help="留空将使用默认名称"
        >
          <UInput
            id="tool-save-dialog-title-input"
            ref="titleInputEl"
            v-model="titleInput"
            autocomplete="off"
            maxlength="100"
            placeholder="给这次保存起个名字"
            @keydown="handleTitleKeydown"
          />
        </UFormField>

        <UFormField
          label="备注"
          help="可选，记录这个版本的修改要点"
        >
          <UTextarea
            id="tool-save-dialog-remark-input"
            v-model="remarkInput"
            autoresize
            :rows="3"
            maxlength="500"
            placeholder="记录这个版本的修改要点（可选）"
          />
        </UFormField>
      </div>
    </template>

    <template #footer>
      <div class="tool-save-dialog-footer">
        <UButton
          color="neutral"
          type="button"
          variant="ghost"
          @click="handleCancel"
        >
          取消
        </UButton>
        <UButton
          color="primary"
          type="button"
          :loading="busy"
          @click="handleConfirm"
        >
          保存
        </UButton>
      </div>
    </template>
  </UModal>
</template>

<style scoped>
.tool-save-dialog-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tool-save-dialog-footer {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  width: 100%;
}

@media (max-width: 520px) {
  .tool-save-dialog-footer {
    flex-direction: column;
  }
}
</style>
