<script setup>
import {
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle
} from 'reka-ui'
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
      titleRef.value?.focus()
      titleRef.value?.select?.()
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
  <DialogRoot v-model:open="isOpen">
    <DialogPortal>
      <DialogOverlay class="tool-save-dialog-overlay" />

      <DialogContent class="tool-save-dialog-content">
        <DialogTitle class="tool-save-dialog-title">
          {{ dialogTitle }}
        </DialogTitle>
        <DialogDescription class="tool-save-dialog-description">
          {{ dialogDescription }}
        </DialogDescription>

        <div class="tool-save-dialog-field">
          <label
            for="tool-save-dialog-title-input"
            class="tool-save-dialog-label"
          >
            名称
          </label>
          <input
            id="tool-save-dialog-title-input"
            ref="titleInputEl"
            v-model="titleInput"
            class="tool-save-dialog-input"
            type="text"
            maxlength="100"
            autocomplete="off"
            placeholder="给这次保存起个名字"
            @keydown="handleTitleKeydown"
          >
          <p class="tool-save-dialog-hint">留空将使用默认名称</p>
        </div>

        <div class="tool-save-dialog-field">
          <label
            for="tool-save-dialog-remark-input"
            class="tool-save-dialog-label"
          >
            备注
          </label>
          <textarea
            id="tool-save-dialog-remark-input"
            v-model="remarkInput"
            class="tool-save-dialog-textarea"
            rows="3"
            maxlength="500"
            placeholder="记录这个版本的修改要点（可选）"
          />
          <p class="tool-save-dialog-hint">可选，记录这个版本的修改要点</p>
        </div>

        <div class="tool-save-dialog-footer">
          <DialogClose as-child>
            <button
              class="tool-save-dialog-ghost"
              type="button"
              @click="handleCancel"
            >
              取消
            </button>
          </DialogClose>
          <button
            class="tool-save-dialog-primary"
            type="button"
            :disabled="busy"
            @click="handleConfirm"
          >
            {{ busy ? '保存中...' : '保存' }}
          </button>
        </div>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>

<style>
/* Unscoped: DialogPortal teleports DialogContent to <body>, so scoped
   selectors with data-v-XXX attributes do not reliably reach the
   portal-mounted subtree. Class names are namespaced to avoid leakage. */
.tool-save-dialog-overlay {
  background: rgba(8, 15, 26, 0.48);
  inset: 0;
  position: fixed;
  z-index: 70;
}

.tool-save-dialog-content {
  background: #ffffff;
  border: 1px solid rgba(16, 37, 66, 0.1);
  border-radius: var(--brand-radius-lg, 20px);
  box-shadow: 0 24px 56px rgba(16, 37, 66, 0.22);
  color: var(--shell-navy, #102542);
  display: flex;
  flex-direction: column;
  gap: 14px;
  left: 50%;
  max-width: 440px;
  outline: none;
  padding: 22px 22px 18px;
  position: fixed;
  top: 50%;
  transform: translate(-50%, -50%);
  width: min(92vw, 440px);
  z-index: 80;
}

.tool-save-dialog-content:focus-visible {
  box-shadow: 0 24px 56px rgba(16, 37, 66, 0.22), var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
}

.tool-save-dialog-title {
  color: var(--shell-navy, #102542);
  font-family: "Georgia", "Times New Roman", serif;
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
}

.tool-save-dialog-description {
  color: rgba(15, 23, 35, 0.66);
  font-size: 0.9rem;
  line-height: 1.55;
  margin: 0;
}

.tool-save-dialog-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.tool-save-dialog-label {
  color: var(--shell-navy, #102542);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.tool-save-dialog-input,
.tool-save-dialog-textarea {
  background: #fafcff;
  border: 1px solid var(--shell-line, rgba(16, 37, 66, 0.12));
  border-radius: var(--brand-radius-md, 12px);
  color: var(--shell-navy, #102542);
  font: inherit;
  font-size: 0.92rem;
  outline: none;
  padding: 10px 12px;
  transition: border-color 120ms ease, box-shadow 120ms ease;
  width: 100%;
}

.tool-save-dialog-textarea {
  font-family: inherit;
  line-height: 1.55;
  resize: vertical;
}

.tool-save-dialog-input:focus-visible,
.tool-save-dialog-textarea:focus-visible {
  border-color: var(--brand-color-accent, #102542);
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
}

.tool-save-dialog-hint {
  color: rgba(15, 23, 35, 0.52);
  font-size: 0.78rem;
  margin: 0;
}

.tool-save-dialog-footer {
  align-items: center;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 6px;
}

.tool-save-dialog-primary,
.tool-save-dialog-ghost {
  align-items: center;
  border-radius: var(--brand-radius-pill, 999px);
  cursor: pointer;
  display: inline-flex;
  font: inherit;
  font-size: 0.88rem;
  font-weight: 800;
  justify-content: center;
  min-height: 38px;
  padding: 0 16px;
}

.tool-save-dialog-primary {
  background: var(--brand-color-accent, #102542);
  border: 1px solid var(--brand-color-accent, #102542);
  color: #ffffff;
}

.tool-save-dialog-primary:hover {
  background: var(--brand-color-accent-hover, var(--brand-color-accent, #102542));
}

.tool-save-dialog-primary:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

.tool-save-dialog-ghost {
  background: rgba(255, 255, 255, 0.62);
  border: 1px solid var(--shell-line, rgba(16, 37, 66, 0.12));
  color: var(--shell-navy, #102542);
}

.tool-save-dialog-ghost:hover {
  background: rgba(255, 255, 255, 0.92);
  border-color: rgba(16, 37, 66, 0.2);
}

.tool-save-dialog-primary:focus-visible,
.tool-save-dialog-ghost:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
}
</style>
