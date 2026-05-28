import { computed, ref } from 'vue'

import { createComment, listComments, listReplies, toggleLike } from 'src/lib/comments'

export function useComments({ targetType, targetId, pageSize = 10 }) {
  const items = ref([])
  const total = ref(0)
  const page = ref(0)
  const sort = ref('new')
  const loading = ref(false)
  const submitting = ref(false)
  const error = ref('')

  const hasMore = computed(() => items.value.length < total.value)

  async function fetchPage(p) {
    loading.value = true
    error.value = ''
    try {
      const res = await listComments({ targetType, targetId, sort: sort.value, page: p, pageSize })
      const incoming = (res.items || []).map((it) => ({ ...it, recent_replies: it.recent_replies || [] }))
      items.value = p === 1 ? incoming : [...items.value, ...incoming]
      total.value = res.total || 0
      page.value = p
    } catch {
      error.value = '加载失败,请稍后再试'
    } finally {
      loading.value = false
    }
  }

  async function reload() {
    await fetchPage(1)
  }

  async function loadMore() {
    if (loading.value || !hasMore.value) return
    await fetchPage(page.value + 1)
  }

  async function changeSort(next) {
    if (sort.value === next) return
    sort.value = next
    await fetchPage(1)
  }

  function mapItems(fn) {
    items.value = items.value.map((it) => {
      const updated = fn(it)
      return {
        ...updated,
        recent_replies: (updated.recent_replies || []).map(fn)
      }
    })
  }

  async function submit({ content, authorName, authorRelation, parentId, replyToId }) {
    if (!content.trim() || !authorName.trim()) {
      throw new Error('empty')
    }
    submitting.value = true
    try {
      const created = await createComment({
        target_type: targetType,
        target_id: targetId,
        parent_id: parentId || null,
        reply_to_id: replyToId || null,
        author_name: authorName.trim(),
        author_relation: authorRelation?.trim() || null,
        content: content.trim()
      })
      if (!created.parent_id) {
        items.value = [{ ...created, recent_replies: [] }, ...items.value]
        total.value += 1
      } else {
        const idx = items.value.findIndex((it) => it.id === created.parent_id)
        if (idx >= 0) {
          const parent = items.value[idx]
          const merged = {
            ...parent,
            recent_replies: [...(parent.recent_replies || []), created],
            reply_count: parent.reply_count + 1
          }
          items.value = [...items.value.slice(0, idx), merged, ...items.value.slice(idx + 1)]
        }
      }
      return created
    } finally {
      submitting.value = false
    }
  }

  async function like(commentId) {
    const res = await toggleLike(commentId)
    mapItems((c) => (c.id === commentId ? { ...c, like_count: res.like_count, liked: res.liked } : c))
    return res
  }

  async function expandReplies(commentId) {
    const res = await listReplies(commentId, { page: 1, pageSize: 50 })
    const idx = items.value.findIndex((it) => it.id === commentId)
    if (idx >= 0) {
      const replies = (res.items || []).map((it) => ({ ...it }))
      items.value = [
        ...items.value.slice(0, idx),
        { ...items.value[idx], recent_replies: replies, reply_count: res.total },
        ...items.value.slice(idx + 1)
      ]
    }
    return res
  }

  return {
    items,
    total,
    sort,
    loading,
    submitting,
    error,
    hasMore,
    reload,
    loadMore,
    changeSort,
    submit,
    like,
    expandReplies
  }
}
