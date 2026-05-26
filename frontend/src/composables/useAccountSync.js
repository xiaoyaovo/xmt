import { computed, shallowRef } from 'vue'

import { deleteSyncItem, getSyncItem, listSyncItems, saveSyncItem } from 'src/lib/accountSync'
import { useAuthStore } from 'src/stores/auth'

export function useAccountSync(toolKey, { itemKey = 'default' } = {}) {
  const auth = useAuthStore()
  const items = shallowRef([])
  const activeItem = shallowRef(null)
  const loading = shallowRef(false)
  const saving = shallowRef(false)
  const deleting = shallowRef(false)
  const errorMessage = shallowRef('')

  const authenticated = computed(() => auth.authenticated)
  const initialized = computed(() => auth.initialized)
  const canSync = computed(() => initialized.value && authenticated.value)
  const syncLabel = computed(() => {
    if (!initialized.value || auth.loading) return '正在检查登录'
    return authenticated.value ? '已启用账户同步' : '登录后启用同步'
  })

  function login() {
    auth.openLoginPage()
  }

  async function ensureAuth() {
    if (!auth.initialized) {
      await auth.refreshMe()
    }
    return auth.authenticated
  }

  async function loadItems() {
    if (!(await ensureAuth())) return []

    loading.value = true
    errorMessage.value = ''
    try {
      const response = await listSyncItems(toolKey)
      items.value = response.items || []
      return items.value
    } catch (error) {
      errorMessage.value = error.message
      return []
    } finally {
      loading.value = false
    }
  }

  async function loadItem(nextItemKey = itemKey) {
    if (!(await ensureAuth())) return null

    loading.value = true
    errorMessage.value = ''
    try {
      const item = await getSyncItem(toolKey, nextItemKey)
      activeItem.value = item
      return item
    } catch (error) {
      if (error.code !== 404) {
        errorMessage.value = error.message
      }
      activeItem.value = null
      return null
    } finally {
      loading.value = false
    }
  }

  async function saveItem({ title = null, payload = {}, nextItemKey = itemKey } = {}) {
    if (!(await ensureAuth())) {
      login()
      return null
    }

    saving.value = true
    errorMessage.value = ''
    try {
      const item = await saveSyncItem(toolKey, nextItemKey, { title, payload })
      activeItem.value = item
      await loadItems()
      return item
    } catch (error) {
      errorMessage.value = error.message
      return null
    } finally {
      saving.value = false
    }
  }

  async function deleteItem(nextItemKey = itemKey) {
    if (!(await ensureAuth())) return false

    deleting.value = true
    errorMessage.value = ''
    try {
      await deleteSyncItem(toolKey, nextItemKey)
      if (activeItem.value?.item_key === nextItemKey) {
        activeItem.value = null
      }
      await loadItems()
      return true
    } catch (error) {
      errorMessage.value = error.message
      return false
    } finally {
      deleting.value = false
    }
  }

  return {
    auth,
    items,
    activeItem,
    initialized,
    authenticated,
    canSync,
    syncLabel,
    loading,
    saving,
    deleting,
    errorMessage,
    login,
    ensureAuth,
    loadItems,
    loadItem,
    saveItem,
    deleteItem
  }
}
