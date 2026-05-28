<script setup>
import { computed, ref } from 'vue'

import CommentInput from 'src/components/comment/CommentInput.vue'
import { avatarColorFor, avatarInitial, formatRelativeTime } from 'src/lib/commentUtils'

const props = defineProps({
  comment: { type: Object, required: true },
  level: { type: Number, default: 0 },
  busy: { type: Boolean, default: false }
})

const emit = defineEmits(['like', 'reply-submit', 'expand-replies'])

const replyingTo = ref(null) // null = not replying; otherwise the target sub-comment (or self)
const expanded = ref(false)

const avatarBg = computed(() => props.comment.author?.avatar ? null : avatarColorFor(props.comment.author?.name))
const avatarText = computed(() => avatarInitial(props.comment.author?.name))
const timeText = computed(() => formatRelativeTime(props.comment.created_at))

const recentReplies = computed(() => props.comment.recent_replies || [])
const hiddenReplies = computed(() => Math.max(0, (props.comment.reply_count || 0) - recentReplies.value.length))

function startReplyTo(target) {
  // Top-level reply (no specific sub) when target === null
  replyingTo.value = target ? { id: target.id, name: target.author?.name } : { id: null, name: null }
}

function cancelReply() {
  replyingTo.value = null
}

async function onReplySubmit(payload) {
  emit('reply-submit', {
    ...payload,
    parentId: props.comment.id,
    replyToId: replyingTo.value?.id || null
  })
  replyingTo.value = null
}

function onLike() {
  emit('like', props.comment.id)
}

function onLikeReply(replyId) {
  emit('like', replyId)
}

function onExpandReplies() {
  if (hiddenReplies.value === 0) {
    expanded.value = !expanded.value
    return
  }
  emit('expand-replies', props.comment.id)
  expanded.value = true
}
</script>

<template>
  <article
    class="cmt-item"
    :class="{ 'cmt-item-reply': level > 0 }"
  >
    <div
      class="cmt-avatar"
      :style="avatarBg ? { background: avatarBg } : null"
    >
      <img
        v-if="comment.author?.avatar"
        :src="comment.author.avatar"
        :alt="comment.author.name"
      />
      <span v-else>{{ avatarText }}</span>
    </div>

    <div class="cmt-body">
      <header class="cmt-head">
        <span class="cmt-name">{{ comment.author?.name }}</span>
        <span
          v-if="comment.author?.relation"
          class="cmt-relation"
        >{{ comment.author.relation }}</span>
        <span class="cmt-time">{{ timeText }}</span>
      </header>
      <p class="cmt-content">
        <span
          v-if="comment.reply_to_name && level > 0"
          class="cmt-reply-mention"
        >@{{ comment.reply_to_name }}</span>
        {{ comment.content }}
      </p>
      <div class="cmt-actions">
        <button
          type="button"
          class="cmt-action"
          :class="{ liked: comment.liked }"
          @click="onLike"
        >
          <svg viewBox="0 0 24 24" :fill="comment.liked ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round">
            <path d="M12 21s-7-4.6-9.3-9.2C1.5 9 2.6 5.5 5.7 4.4 8.1 3.5 10.6 4.7 12 6.7 13.4 4.7 15.9 3.5 18.3 4.4 21.4 5.5 22.5 9 21.3 11.8 19 16.4 12 21 12 21z" />
          </svg>
          <span>{{ comment.like_count || 0 }}</span>
        </button>
        <button
          type="button"
          class="cmt-action"
          @click="startReplyTo(level > 0 ? comment : null)"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 11.5a8.4 8.4 0 0 1-1.4 4.6 8.6 8.6 0 0 1-7.1 3.9 8.4 8.4 0 0 1-3.9-.9L3 21l1.9-5.6A8.5 8.5 0 1 1 21 11.5z" />
          </svg>
          <span>回复</span>
        </button>
      </div>

      <!-- Inline reply input -->
      <div
        v-if="replyingTo"
        class="cmt-reply-input"
      >
        <CommentInput
          :avatar-color="avatarColorFor('')"
          :avatar-initial="'@'"
          compact
          cancelable
          :busy="busy"
          :placeholder="replyingTo.name ? `回复 @${replyingTo.name}: ` : '说点什么…'"
          @submit="onReplySubmit"
          @cancel="cancelReply"
        />
      </div>

      <!-- Nested replies (only at level 0) -->
      <div
        v-if="level === 0 && (recentReplies.length > 0 || hiddenReplies > 0)"
        class="cmt-replies"
      >
        <CommentItem
          v-for="r in recentReplies"
          :key="r.id"
          :comment="r"
          :level="1"
          :busy="busy"
          @like="onLikeReply"
          @reply-submit="(p) => emit('reply-submit', { ...p, parentId: comment.id, replyToId: p.replyToId || r.id })"
        />
        <button
          v-if="hiddenReplies > 0 && !expanded"
          type="button"
          class="cmt-expand"
          @click="onExpandReplies"
        >
          展开剩余 {{ hiddenReplies }} 条回复 ↓
        </button>
      </div>
    </div>
  </article>
</template>

<style scoped>
.cmt-item {
  display: flex;
  gap: 14px;
  padding: 18px 0;
  border-top: 1px solid var(--cmt-border, rgba(0, 0, 0, 0.08));
}
.cmt-item:first-child { border-top: none; }
.cmt-item-reply {
  padding: 12px 0;
  border-top: none;
}
.cmt-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-family: var(--cmt-font-serif, Georgia, serif);
  font-weight: 600;
  font-size: 1.05rem;
  flex: 0 0 auto;
  overflow: hidden;
}
.cmt-item-reply .cmt-avatar {
  width: 30px;
  height: 30px;
  font-size: 0.85rem;
}
.cmt-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.cmt-body {
  flex: 1;
  min-width: 0;
}
.cmt-head {
  display: flex;
  gap: 10px;
  align-items: baseline;
  flex-wrap: wrap;
}
.cmt-name {
  font-family: var(--cmt-font-serif, Georgia, serif);
  font-size: 1rem;
  font-weight: 500;
  color: var(--cmt-ink, #2a1f19);
}
.cmt-relation {
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  color: var(--cmt-accent, #c9967a);
  background: var(--cmt-accent-soft, rgba(201, 150, 122, 0.14));
  padding: 2px 8px;
  border-radius: 999px;
}
.cmt-time {
  font-size: 0.78rem;
  color: var(--cmt-muted, #8b6f5d);
  margin-left: auto;
}
.cmt-content {
  font-family: var(--cmt-font-cn, 'Noto Serif SC', serif);
  font-size: 0.96rem;
  line-height: 1.85;
  color: var(--cmt-ink-soft, #5b4538);
  margin: 8px 0 10px;
  white-space: pre-wrap;
  word-break: break-word;
}
.cmt-reply-mention {
  color: var(--cmt-accent, #c9967a);
  font-weight: 500;
  margin-right: 6px;
}
.cmt-actions {
  display: flex;
  gap: 16px;
  margin-bottom: 4px;
}
.cmt-action {
  background: transparent;
  border: none;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.82rem;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: var(--cmt-muted, #8b6f5d);
  padding: 4px 6px;
  border-radius: 6px;
  transition: color 160ms ease, background 160ms ease;
}
.cmt-action:hover { color: var(--cmt-accent, #c9967a); }
.cmt-action.liked { color: var(--cmt-accent, #c9967a); }
.cmt-action svg { width: 16px; height: 16px; }
.cmt-reply-input {
  margin: 12px 0;
}
.cmt-replies {
  margin-top: 12px;
  padding-left: 16px;
  border-left: 1px solid var(--cmt-border, rgba(0, 0, 0, 0.06));
}
.cmt-expand {
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--cmt-accent, #c9967a);
  font-family: inherit;
  font-size: 0.84rem;
  letter-spacing: 0.04em;
  padding: 6px 0;
}
.cmt-expand:hover { text-decoration: underline; }
</style>
