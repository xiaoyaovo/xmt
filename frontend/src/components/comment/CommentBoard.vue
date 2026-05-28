<script setup>
import { onMounted, ref, watch } from 'vue'

import CommentInput from 'src/components/comment/CommentInput.vue'
import CommentItem from 'src/components/comment/CommentItem.vue'
import { useComments } from 'src/composables/useComments'
import { avatarColorFor, avatarInitial } from 'src/lib/commentUtils'

const props = defineProps({
  targetType: { type: String, required: true },
  targetId: { type: String, default: 'default' },
  title: { type: String, default: '祝福留言' },
  subtitle: { type: String, default: '' },
  pageSize: { type: Number, default: 10 },
  inputPlaceholder: { type: String, default: '说点祝福的话吧 ……' }
})

const {
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
} = useComments({ targetType: props.targetType, targetId: props.targetId, pageSize: props.pageSize })

const inputError = ref('')
const pendingName = ref('')
const pendingAvatarColor = ref(avatarColorFor(''))
const pendingAvatarInitial = ref(avatarInitial(''))

watch(pendingName, (v) => {
  pendingAvatarColor.value = avatarColorFor(v)
  pendingAvatarInitial.value = avatarInitial(v)
})

async function onTopSubmit(payload) {
  inputError.value = ''
  pendingName.value = payload.authorName
  try {
    await submit(payload)
  } catch (e) {
    if (e?.response?.status === 400) {
      inputError.value = '内容不合法,请检查后再试'
    } else {
      inputError.value = '发送失败,请稍后再试'
    }
  }
}

async function onReplySubmit(payload) {
  pendingName.value = payload.authorName || pendingName.value
  try {
    await submit(payload)
  } catch {
    // surface via inline error inside the item? For MVP show in top bar
    inputError.value = '回复失败,请稍后再试'
  }
}

onMounted(() => {
  reload()
})
</script>

<template>
  <section
    class="cmt-board"
    aria-label="留言板"
  >
    <header class="cmt-board-head">
      <div class="cmt-board-title-block">
        <h3 class="cmt-board-title">{{ title }}</h3>
        <p
          v-if="subtitle"
          class="cmt-board-subtitle"
        >{{ subtitle }}</p>
      </div>
      <div class="cmt-board-meta">
        <span class="cmt-board-count">{{ total }} 条</span>
        <div class="cmt-board-sort">
          <button
            type="button"
            :class="{ active: sort === 'new' }"
            @click="changeSort('new')"
          >
            最新
          </button>
          <button
            type="button"
            :class="{ active: sort === 'hot' }"
            @click="changeSort('hot')"
          >
            最热
          </button>
        </div>
      </div>
    </header>

    <CommentInput
      :avatar-color="pendingAvatarColor"
      :avatar-initial="pendingAvatarInitial"
      :placeholder="inputPlaceholder"
      :busy="submitting"
      :error-text="inputError"
      @submit="onTopSubmit"
    />

    <div
      v-if="loading && items.length === 0"
      class="cmt-board-state"
    >
      正在载入留言…
    </div>

    <div
      v-else-if="items.length === 0"
      class="cmt-board-state"
    >
      还没有留言,第一句祝福从你开始吧。
    </div>

    <div
      v-else
      class="cmt-board-list"
    >
      <CommentItem
        v-for="c in items"
        :key="c.id"
        :comment="c"
        :busy="submitting"
        @like="like"
        @reply-submit="onReplySubmit"
        @expand-replies="expandReplies"
      />
    </div>

    <div
      v-if="hasMore"
      class="cmt-board-foot"
    >
      <button
        type="button"
        class="cmt-board-more"
        :disabled="loading"
        @click="loadMore"
      >
        {{ loading ? '加载中…' : '加载更多' }}
      </button>
    </div>

    <p
      v-if="error"
      class="cmt-board-error"
    >{{ error }}</p>
  </section>
</template>

<style scoped>
.cmt-board {
  /* Theme defaults — host page can override these vars at any ancestor level */
  --cmt-surface: var(--cmt-host-surface, #ffffff);
  --cmt-surface-soft: var(--cmt-host-surface-soft, rgba(0, 0, 0, 0.03));
  --cmt-border: var(--cmt-host-border, rgba(0, 0, 0, 0.08));
  --cmt-ink: var(--cmt-host-ink, #2a1f19);
  --cmt-ink-soft: var(--cmt-host-ink-soft, #5b4538);
  --cmt-muted: var(--cmt-host-muted, #8b6f5d);
  --cmt-accent: var(--cmt-host-accent, #c9967a);
  --cmt-accent-soft: var(--cmt-host-accent-soft, rgba(201, 150, 122, 0.14));
  --cmt-on-accent: var(--cmt-host-on-accent, #ffffff);
  --cmt-radius: var(--cmt-host-radius, 12px);
  --cmt-font-serif: var(--cmt-host-font-serif, 'Cormorant Garamond', Georgia, serif);
  --cmt-font-cn: var(--cmt-host-font-cn, 'Noto Serif SC', serif);
}
.cmt-board-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.cmt-board-title {
  font-family: var(--cmt-font-serif);
  font-weight: 500;
  font-size: 1.5rem;
  color: var(--cmt-ink);
  margin: 0;
}
.cmt-board-subtitle {
  margin: 4px 0 0;
  color: var(--cmt-muted);
  font-size: 0.86rem;
}
.cmt-board-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}
.cmt-board-count {
  font-size: 0.82rem;
  color: var(--cmt-muted);
  letter-spacing: 0.06em;
}
.cmt-board-sort {
  display: inline-flex;
  background: var(--cmt-surface-soft);
  border-radius: 999px;
  padding: 4px;
}
.cmt-board-sort button {
  border: none;
  background: transparent;
  color: var(--cmt-muted);
  font-family: inherit;
  font-size: 0.82rem;
  padding: 6px 14px;
  border-radius: 999px;
  cursor: pointer;
  transition: background 160ms ease, color 160ms ease;
}
.cmt-board-sort button.active {
  background: var(--cmt-on-accent);
  color: var(--cmt-accent);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
.cmt-board-list {
  margin-top: 12px;
}
.cmt-board-state {
  padding: 28px 0;
  text-align: center;
  color: var(--cmt-muted);
  font-family: var(--cmt-font-cn);
  font-size: 0.96rem;
}
.cmt-board-foot {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}
.cmt-board-more {
  background: transparent;
  border: 1px solid var(--cmt-border);
  color: var(--cmt-muted);
  padding: 10px 24px;
  font-family: inherit;
  font-size: 0.86rem;
  border-radius: 999px;
  cursor: pointer;
  transition: background 160ms ease, color 160ms ease, border-color 160ms ease;
}
.cmt-board-more:hover:not(:disabled) {
  color: var(--cmt-accent);
  border-color: var(--cmt-accent);
}
.cmt-board-more:disabled { opacity: 0.6; cursor: progress; }
.cmt-board-error {
  margin-top: 12px;
  text-align: center;
  color: #b94d4d;
  font-size: 0.86rem;
}
</style>
