<script setup>
import { computed } from 'vue'

import ToolSaveDialog from 'src/components/tools/ToolSaveDialog.vue'

const props = defineProps({
  versions: {
    type: Object,
    required: true
  },
  canOverwrite: {
    type: Boolean,
    default: null
  },
  saveLabel: {
    type: String,
    default: ''
  },
  saveAsLabel: {
    type: String,
    default: '另存为新版本'
  },
  showSave: {
    type: Boolean,
    default: true
  },
  showSaveAs: {
    type: Boolean,
    default: true
  },
  showHistory: {
    type: Boolean,
    default: true
  },
  saveDisabled: {
    type: Boolean,
    default: false
  },
  saveDialogTitle: {
    type: String,
    default: '保存到云端存档'
  },
  saveAsDialogTitle: {
    type: String,
    default: '另存为新版本'
  },
  dialogDescription: {
    type: String,
    default: '给这个存档取个名字，方便以后在历史里认出来。'
  }
})

const { versions } = props

const resolvedCanOverwrite = computed(() => {
  if (props.canOverwrite !== null) return props.canOverwrite
  return versions.canOverwrite?.value ?? true
})

const dialogTitle = computed(() => (
  versions.saveDialogMode.value === 'save-as-new'
    ? props.saveAsDialogTitle
    : props.saveDialogTitle
))

const resolvedSaveLabel = computed(() => props.saveLabel || versions.saveButtonLabel.value)

const isSaving = computed(() => versions.saving.value)

const saveIsDisabled = computed(() => props.saveDisabled || isSaving.value)

function handleSave() {
  versions.requestSave()
}

function handleSaveAsNew() {
  versions.requestSaveAsNew()
}

function handleSaveDialogConfirm(payload) {
  versions.handleSaveDialogConfirm(payload)
}
</script>

<template>
  <div class="tool-version-menu">
    <UButton
      v-if="showSave"
      class="tool-version-primary brand-action-button"
      color="primary"
      :label="resolvedSaveLabel"
      :loading="isSaving"
      type="button"
      :disabled="saveIsDisabled"
      @click="handleSave"
    />

    <UButton
      v-if="showSaveAs && resolvedCanOverwrite"
      class="tool-version-ghost"
      color="neutral"
      :label="saveAsLabel"
      type="button"
      variant="subtle"
      :disabled="saveIsDisabled"
      @click="handleSaveAsNew"
    />

    <UPopover
      v-if="showHistory"
      v-model:open="versions.historyOpen.value"
      :content="{ align: 'end', sideOffset: 8 }"
    >
      <UButton
        class="tool-version-ghost tool-version-history-trigger"
        color="neutral"
        type="button"
        variant="subtle"
        :disabled="versions.historyTriggerDisabled.value"
        aria-label="历史存档"
      >
        <span>{{ versions.historyTriggerLabel.value }}</span>
        <span
          class="tool-version-history-trigger-caret"
          aria-hidden="true"
        >▾</span>
      </UButton>

      <template #content>
        <div class="tool-version-history-popover">
          <div class="tool-version-history-popover-head">
            <div class="tool-version-history-popover-title">
              <div class="section-kicker">历史</div>
              <span
                v-if="versions.archiveCountText.value"
                class="tool-version-archive-count"
              >· {{ versions.archiveCountText.value }}</span>
            </div>
            <UButton
              class="tool-version-ghost tool-version-history-refresh"
              color="neutral"
              :label="versions.loading.value ? '刷新中' : '刷新'"
              :loading="versions.loading.value"
              size="sm"
              type="button"
              variant="subtle"
              :disabled="versions.loading.value"
              @click="versions.loadItems"
            />
          </div>

          <div
            v-if="versions.loading.value && !versions.items.value.length"
            class="tool-version-history-empty"
          >
            读取中
          </div>
          <div
            v-else-if="!versions.items.value.length"
            class="tool-version-history-empty"
          >
            无存档
          </div>
          <div
            v-else
            class="tool-version-archive-list"
          >
            <div
              v-for="item in versions.items.value"
              :key="item.item_key"
              class="tool-version-archive-row"
              :class="{ 'tool-version-archive-row-active': versions.activeItem.value?.item_key === item.item_key }"
            >
              <UButton
                class="tool-version-archive-open"
                color="neutral"
                type="button"
                variant="ghost"
                @click="versions.openVersion(item)"
              >
                <span class="tool-version-archive-title">{{ versions.archiveDisplayTitle(item) }}</span>
                <span class="tool-version-archive-meta">{{ versions.archiveSecondaryLine(item) }}</span>
              </UButton>
              <UButton
                class="tool-version-archive-delete"
                color="error"
                :label="versions.deletingArchiveKey.value === item.item_key ? '...' : '×'"
                size="xs"
                type="button"
                variant="ghost"
                :disabled="versions.deletingArchiveKey.value === item.item_key"
                :aria-label="`删除 ${versions.archiveDisplayTitle(item)}`"
                @click.stop="versions.removeVersion(item)"
              />
            </div>
          </div>
        </div>
      </template>
    </UPopover>

    <ToolSaveDialog
      v-model:open="versions.saveDialogOpen.value"
      :default-title="versions.saveDialogDefaults.value.title"
      :default-remark="versions.saveDialogDefaults.value.remark"
      :busy="isSaving"
      :dialog-title="dialogTitle"
      :dialog-description="dialogDescription"
      @confirm="handleSaveDialogConfirm"
    />
  </div>
</template>

<style scoped>
.tool-version-menu {
  align-items: center;
  display: contents;
}

.tool-version-primary,
.tool-version-ghost {
  align-items: center;
  background: rgba(255, 255, 255, 0.62);
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-md, 16px);
  color: var(--shell-navy);
  cursor: pointer;
  display: inline-flex;
  font: inherit;
  font-size: 0.88rem;
  font-weight: 800;
  gap: 8px;
  min-height: 38px;
  padding: 0 13px;
}

.tool-version-primary {
  background: var(--brand-color-accent, #102542);
  border-color: var(--brand-color-accent, #102542);
  color: #ffffff;
}

.tool-version-primary:disabled,
.tool-version-ghost:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

.tool-version-ghost:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(16, 37, 66, 0.18);
}

.tool-version-primary:focus-visible,
.tool-version-ghost:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
}

.tool-version-history-trigger {
  display: inline-flex;
  max-width: 320px;
}

.tool-version-history-trigger > span:first-child {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tool-version-history-trigger-caret {
  font-size: 0.78rem;
  margin-left: 2px;
}
</style>

<style>
.tool-version-history-popover {
  background: #ffffff;
  border: 1px solid rgba(16, 37, 66, 0.1);
  border-radius: var(--brand-radius-md, 16px);
  box-shadow: 0 18px 42px rgba(16, 37, 66, 0.16);
  color: var(--shell-navy, #102542);
  min-width: 320px;
  padding: 12px;
  z-index: 90;
}

.tool-version-history-popover:focus-visible {
  outline: none;
  box-shadow: 0 18px 42px rgba(16, 37, 66, 0.16), var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
}

.tool-version-history-popover-head {
  align-items: center;
  display: flex;
  gap: 12px;
  justify-content: space-between;
}

.tool-version-history-popover-title {
  align-items: baseline;
  display: flex;
  gap: 6px;
}

.tool-version-archive-count {
  color: rgba(15, 23, 35, 0.62);
  font-size: 0.88rem;
}

.tool-version-history-refresh {
  font-size: 0.82rem;
  min-height: 32px;
  padding: 0 10px;
}

.tool-version-history-empty {
  color: rgba(15, 23, 35, 0.62);
  font-size: 0.9rem;
  margin-top: 10px;
  padding: 6px 4px;
}

.tool-version-archive-list {
  background: #ffffff;
  border: 1px solid var(--shell-line, rgba(16, 37, 66, 0.12));
  border-radius: var(--brand-radius-md, 16px);
  display: flex;
  flex-direction: column;
  margin-top: 12px;
  max-height: min(60vh, 360px);
  overflow-y: auto;
  scrollbar-color: rgba(16, 37, 66, 0.24) transparent;
  scrollbar-width: thin;
}

.tool-version-archive-list::-webkit-scrollbar {
  width: 8px;
}

.tool-version-archive-list::-webkit-scrollbar-thumb {
  background: rgba(16, 37, 66, 0.2);
  border-radius: var(--brand-radius-pill, 999px);
}

.tool-version-archive-row {
  align-items: center;
  background: transparent;
  border-top: 1px solid rgba(16, 37, 66, 0.06);
  display: grid;
  gap: 8px;
  grid-template-columns: minmax(0, 1fr) auto;
  min-height: 32px;
  padding: 4px 8px 4px 10px;
  position: relative;
  transition: background 120ms ease;
}

.tool-version-archive-row:first-child {
  border-top: 0;
}

.tool-version-archive-row:hover,
.tool-version-archive-row:focus-within {
  background: rgba(16, 37, 66, 0.04);
}

.tool-version-archive-row-active {
  background: rgba(16, 37, 66, 0.06);
  box-shadow: inset 3px 0 0 0 var(--brand-color-accent, #102542);
}

.tool-version-archive-open {
  align-items: flex-start;
  background: transparent;
  border: 0;
  color: inherit;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  font: inherit;
  gap: 2px;
  min-height: 28px;
  min-width: 0;
  padding: 2px 0;
  text-align: left;
  width: 100%;
}

.tool-version-archive-open:focus-visible {
  border-radius: var(--brand-radius-sm, 8px);
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
}

.tool-version-archive-title {
  color: var(--shell-navy, #102542);
  font-size: 0.88rem;
  font-weight: 700;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tool-version-archive-meta {
  color: rgba(15, 23, 35, 0.55);
  font-size: 0.8rem;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tool-version-archive-delete {
  align-items: center;
  background: transparent;
  border: 0;
  border-radius: var(--brand-radius-pill, 999px);
  color: rgba(15, 23, 35, 0.4);
  cursor: pointer;
  display: inline-flex;
  font: inherit;
  font-size: 1.05rem;
  font-weight: 700;
  height: 24px;
  justify-content: center;
  line-height: 1;
  padding: 0;
  transition: color 120ms ease, background 120ms ease;
  width: 24px;
}

.tool-version-archive-row:hover .tool-version-archive-delete,
.tool-version-archive-row:focus-within .tool-version-archive-delete {
  color: var(--shell-coral, #ff7a59);
}

.tool-version-archive-delete:hover {
  background: rgba(255, 122, 89, 0.12);
  color: var(--shell-coral, #ff7a59);
}

.tool-version-archive-delete:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  color: var(--shell-coral, #ff7a59);
  outline: none;
}

.tool-version-archive-delete:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
