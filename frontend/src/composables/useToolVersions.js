import { computed, shallowRef } from 'vue'

import { useAccountSync } from 'src/composables/useAccountSync'

function defaultFormatArchiveDate(value) {
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(value))
}

function defaultArchiveKey() {
  const timestamp = new Date().toISOString().replace(/[-:.TZ]/g, '').slice(0, 14)
  const suffix = Math.random().toString(36).slice(2, 8)
  return `archive-${timestamp}-${suffix}`
}

export function useToolVersions(toolKey, {
  defaultTitlePrefix = '存档',
  updatedFrom = `${toolKey}-editor`,
  buildPayload,
  applyPayload,
  formatArchiveDate = defaultFormatArchiveDate,
  createArchiveKey = defaultArchiveKey,
  saveStrategy = null
} = {}) {
  if (typeof buildPayload !== 'function') {
    throw new Error('[useToolVersions] buildPayload is required')
  }
  if (typeof applyPayload !== 'function') {
    throw new Error('[useToolVersions] applyPayload is required')
  }

  const sync = useAccountSync(toolKey)

  const saveDialogOpen = shallowRef(false)
  const saveDialogMode = shallowRef('save')
  const saveDialogDefaults = shallowRef({ title: '', remark: '' })
  const historyOpen = shallowRef(false)
  const deletingArchiveKey = shallowRef('')

  const canOverwrite = computed(() => Boolean(sync.activeItem.value))

  const syncStatusText = computed(() => {
    if (sync.saving.value) return '同步中'
    if (sync.loading.value) return '读取中'
    return ''
  })

  const archiveCountText = computed(() => {
    if (sync.loading.value) return '读取中'
    return sync.items.value.length ? String(sync.items.value.length) : ''
  })

  const historyTriggerLabel = computed(() => {
    if (!sync.auth.initialized || sync.auth.loading) return '检查登录中'
    if (!sync.auth.authenticated) return '未登录 · 登录后同步'
    if (sync.loading.value) return '读取中'
    const active = sync.activeItem.value
    if (active) {
      const activeLabel = (active.title || '').trim() || formatArchiveDate(active.updated_at)
      return `历史 · ${activeLabel}`
    }
    if (!sync.items.value.length) return '无存档'
    return `历史存档 · ${sync.items.value.length}`
  })

  const historyTriggerDisabled = computed(() => {
    if (!sync.auth.initialized || sync.auth.loading) return true
    if (!sync.auth.authenticated) return true
    if (sync.loading.value) return false
    return !sync.items.value.length
  })

  const saveButtonLabel = computed(() => {
    if (sync.saving.value) return '保存中...'
    if (!sync.auth.authenticated) return '登录后保存'
    return canOverwrite.value ? '覆盖保存' : '保存'
  })

  function createArchiveTitle() {
    return `${defaultTitlePrefix} ${formatArchiveDate(new Date())}`
  }

  function archiveDisplayTitle(item) {
    return (item?.title || '').trim() || `${defaultTitlePrefix} ${formatArchiveDate(item.updated_at)}`
  }

  function archiveSecondaryLine(item) {
    const remark = (item?.payload?.remark || '').trim()
    const stamp = formatArchiveDate(item.updated_at)
    return remark ? `${remark} · ${stamp}` : stamp
  }

  async function ensureAuthOrLogin() {
    if (sync.auth.authenticated) return true
    const ok = await sync.ensureAuth()
    if (!ok) {
      sync.login()
      return false
    }
    return true
  }

  function openSaveDialog(mode = 'save') {
    saveDialogMode.value = mode
    if (mode === 'save') {
      const active = sync.activeItem.value
      saveDialogDefaults.value = {
        title: active?.title || '',
        remark: active?.payload?.remark || ''
      }
    } else {
      saveDialogDefaults.value = { title: '', remark: '' }
    }
    saveDialogOpen.value = true
  }

  function closeSaveDialog() {
    saveDialogOpen.value = false
  }

  async function requestSave() {
    if (!(await ensureAuthOrLogin())) return
    openSaveDialog('save')
  }

  async function requestSaveAsNew() {
    if (!(await ensureAuthOrLogin())) return
    openSaveDialog('save-as-new')
  }

  async function persist({ forceNew = false, title = '', remark = '' } = {}) {
    const activeItemKey = sync.activeItem.value?.item_key
    const nextItemKey = forceNew || !activeItemKey ? createArchiveKey() : activeItemKey
    const isNewArchive = nextItemKey !== activeItemKey
    const trimmedTitle = (title || '').trim()
    const fallbackTitle = isNewArchive
      ? createArchiveTitle()
      : sync.activeItem.value?.title || createArchiveTitle()
    const payload = await buildPayload({
      archiveKey: nextItemKey,
      remark: (remark || '').trim(),
      updatedFrom
    })
    return sync.saveItem({
      title: trimmedTitle || fallbackTitle,
      nextItemKey,
      payload
    })
  }

  async function handleSaveDialogConfirm({ title, remark }) {
    const forceNew = saveDialogMode.value === 'save-as-new'
    closeSaveDialog()
    if (typeof saveStrategy === 'function') {
      return saveStrategy({ forceNew, title, remark, persist })
    }
    return persist({ forceNew, title, remark })
  }

  function openVersion(item) {
    if (!item?.payload) {
      sync.errorMessage.value = '存档内容为空'
      return false
    }
    const result = applyPayload(item.payload, item)
    if (result === false) return false
    sync.activeItem.value = item
    historyOpen.value = false
    sync.errorMessage.value = ''
    return true
  }

  async function removeVersion(item) {
    if (!item?.item_key) return false
    deletingArchiveKey.value = item.item_key
    const deleted = await sync.deleteItem(item.item_key)
    deletingArchiveKey.value = ''
    return deleted
  }

  async function loadInitial() {
    await sync.auth.refreshMe()
    if (sync.auth.authenticated) {
      await sync.loadItems()
    }
  }

  return {
    // raw sync
    sync,
    auth: sync.auth,
    items: sync.items,
    activeItem: sync.activeItem,
    loading: sync.loading,
    saving: sync.saving,
    errorMessage: sync.errorMessage,
    syncLabel: sync.syncLabel,
    login: sync.login,
    ensureAuth: sync.ensureAuth,
    loadItems: sync.loadItems,

    // dialog & history state
    saveDialogOpen,
    saveDialogMode,
    saveDialogDefaults,
    historyOpen,
    deletingArchiveKey,

    // computed labels
    canOverwrite,
    syncStatusText,
    archiveCountText,
    historyTriggerLabel,
    historyTriggerDisabled,
    saveButtonLabel,

    // helpers
    formatArchiveDate,
    createArchiveKey,
    createArchiveTitle,
    archiveDisplayTitle,
    archiveSecondaryLine,

    // actions
    requestSave,
    requestSaveAsNew,
    openSaveDialog,
    closeSaveDialog,
    handleSaveDialogConfirm,
    persist,
    openVersion,
    removeVersion,
    loadInitial
  }
}
