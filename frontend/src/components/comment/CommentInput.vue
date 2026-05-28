<script setup>
import { computed, ref, watch } from 'vue'

const EMOJI = [
  '🤍', '💕', '💐', '🌸', '🌹', '🌷', '🌻', '🍾', '🥂', '🎉',
  '✨', '💍', '👰', '🤵', '💑', '👫', '🥰', '😊', '😍', '😘',
  '🥺', '😭', '🤗', '👏', '🙌', '🙏', '💯', '🔥', '⭐', '🎊'
]

const props = defineProps({
  avatarName: { type: String, default: '' },
  avatarColor: { type: String, default: '#a98467' },
  avatarInitial: { type: String, default: '?' },
  defaultName: { type: String, default: '' },
  showNameInput: { type: Boolean, default: true },
  compact: { type: Boolean, default: false },
  placeholder: { type: String, default: '说点祝福的话吧 ……' },
  cancelable: { type: Boolean, default: false },
  busy: { type: Boolean, default: false },
  errorText: { type: String, default: '' }
})

const emit = defineEmits(['submit', 'cancel'])

const content = ref('')
const name = ref(props.defaultName)
const relation = ref('')
const showEmoji = ref(false)
const textarea = ref(null)

watch(
  () => props.defaultName,
  (v) => {
    if (!name.value) name.value = v
  }
)

const canSubmit = computed(() => content.value.trim().length > 0 && name.value.trim().length > 0 && !props.busy)

function insertEmoji(emoji) {
  const el = textarea.value
  if (!el) {
    content.value += emoji
    return
  }
  const start = el.selectionStart ?? content.value.length
  const end = el.selectionEnd ?? content.value.length
  content.value = content.value.slice(0, start) + emoji + content.value.slice(end)
  // Re-position cursor after insertion on next tick
  requestAnimationFrame(() => {
    el.focus()
    const pos = start + emoji.length
    el.setSelectionRange(pos, pos)
  })
}

function onSubmit() {
  if (!canSubmit.value) return
  emit('submit', {
    content: content.value,
    authorName: name.value,
    authorRelation: relation.value || null
  })
  content.value = ''
  showEmoji.value = false
}

function onCancel() {
  content.value = ''
  showEmoji.value = false
  emit('cancel')
}
</script>

<template>
  <div
    class="cmt-input"
    :class="{ 'cmt-input-compact': compact }"
  >
    <div
      class="cmt-input-avatar"
      :style="{ background: avatarColor }"
    >
      {{ avatarInitial }}
    </div>
    <div class="cmt-input-body">
      <div
        v-if="showNameInput"
        class="cmt-input-meta"
      >
        <input
          v-model="name"
          class="cmt-input-name"
          :placeholder="compact ? '回复用的名字' : '您的名字'"
          maxlength="32"
        />
        <input
          v-model="relation"
          class="cmt-input-relation"
          placeholder="关系(可选, 如 大学同学)"
          maxlength="32"
        />
      </div>
      <textarea
        ref="textarea"
        v-model="content"
        class="cmt-input-area"
        :placeholder="placeholder"
        :rows="compact ? 2 : 3"
        maxlength="2000"
        @keydown.ctrl.enter.prevent="onSubmit"
        @keydown.meta.enter.prevent="onSubmit"
      />
      <div class="cmt-input-toolbar">
        <button
          type="button"
          class="cmt-tool-btn"
          :class="{ active: showEmoji }"
          aria-label="表情"
          @click="showEmoji = !showEmoji"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round">
            <circle cx="12" cy="12" r="9.5" />
            <circle cx="9" cy="10" r="0.8" fill="currentColor" stroke="none" />
            <circle cx="15" cy="10" r="0.8" fill="currentColor" stroke="none" />
            <path d="M8.5 14.5c1 1.4 2.2 2 3.5 2s2.5-0.6 3.5-2" />
          </svg>
        </button>
        <span
          v-if="errorText"
          class="cmt-input-error"
        >{{ errorText }}</span>
        <div class="cmt-input-actions">
          <button
            v-if="cancelable"
            type="button"
            class="cmt-btn cmt-btn-ghost"
            @click="onCancel"
          >
            取消
          </button>
          <button
            type="button"
            class="cmt-btn cmt-btn-primary"
            :disabled="!canSubmit"
            @click="onSubmit"
          >
            {{ busy ? '发送中…' : (compact ? '回复' : '送出祝福') }}
          </button>
        </div>
      </div>
      <div
        v-if="showEmoji"
        class="cmt-emoji"
      >
        <button
          v-for="e in EMOJI"
          :key="e"
          type="button"
          class="cmt-emoji-btn"
          @click="insertEmoji(e)"
        >
          {{ e }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cmt-input {
  display: flex;
  gap: 14px;
  padding: 18px;
  background: var(--cmt-surface, #ffffff);
  border: 1px solid var(--cmt-border, rgba(0, 0, 0, 0.08));
  border-radius: var(--cmt-radius, 12px);
}
.cmt-input-compact {
  padding: 12px;
  gap: 10px;
  border: 1px dashed var(--cmt-border, rgba(0, 0, 0, 0.12));
  background: var(--cmt-surface-soft, rgba(0, 0, 0, 0.02));
}
.cmt-input-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 600;
  font-family: var(--cmt-font-serif, Georgia, serif);
  font-size: 1.1rem;
  flex: 0 0 auto;
}
.cmt-input-compact .cmt-input-avatar {
  width: 32px;
  height: 32px;
  font-size: 0.95rem;
}
.cmt-input-body {
  flex: 1;
  min-width: 0;
}
.cmt-input-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}
.cmt-input-name,
.cmt-input-relation {
  flex: 1;
  min-width: 0;
  background: transparent;
  border: none;
  border-bottom: 1px solid var(--cmt-border, rgba(0, 0, 0, 0.1));
  padding: 4px 0;
  font-size: 0.85rem;
  font-family: inherit;
  color: var(--cmt-ink, #2a1f19);
  outline: none;
  transition: border-color 200ms ease;
}
.cmt-input-name { max-width: 180px; }
.cmt-input-relation { max-width: 220px; }
.cmt-input-name:focus,
.cmt-input-relation:focus {
  border-bottom-color: var(--cmt-accent, #c9967a);
}
.cmt-input-area {
  width: 100%;
  resize: vertical;
  background: transparent;
  border: 1px solid var(--cmt-border, rgba(0, 0, 0, 0.12));
  border-radius: 8px;
  padding: 10px 12px;
  font-family: inherit;
  font-size: 0.95rem;
  line-height: 1.7;
  color: var(--cmt-ink, #2a1f19);
  outline: none;
  transition: border-color 200ms ease;
}
.cmt-input-area:focus {
  border-color: var(--cmt-accent, #c9967a);
}
.cmt-input-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
}
.cmt-tool-btn {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: var(--cmt-muted, #8b6f5d);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 160ms ease, color 160ms ease;
}
.cmt-tool-btn:hover,
.cmt-tool-btn.active {
  background: var(--cmt-accent-soft, rgba(201, 150, 122, 0.16));
  color: var(--cmt-accent, #c9967a);
}
.cmt-tool-btn svg { width: 20px; height: 20px; }
.cmt-input-error {
  font-size: 0.82rem;
  color: #b94d4d;
}
.cmt-input-actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
}
.cmt-btn {
  cursor: pointer;
  border: none;
  font-family: inherit;
  font-size: 0.88rem;
  font-weight: 500;
  padding: 8px 18px;
  border-radius: 999px;
  transition: background 160ms ease, color 160ms ease, transform 160ms ease;
}
.cmt-btn-ghost {
  background: transparent;
  color: var(--cmt-muted, #8b6f5d);
}
.cmt-btn-ghost:hover { background: var(--cmt-accent-soft, rgba(201, 150, 122, 0.12)); }
.cmt-btn-primary {
  background: var(--cmt-accent, #c9967a);
  color: var(--cmt-on-accent, #ffffff);
}
.cmt-btn-primary:hover:not(:disabled) { transform: translateY(-1px); }
.cmt-btn-primary:disabled { opacity: 0.55; cursor: not-allowed; }
.cmt-emoji {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(34px, 1fr));
  gap: 4px;
  padding: 10px;
  margin-top: 10px;
  background: var(--cmt-surface-soft, rgba(0, 0, 0, 0.03));
  border-radius: 8px;
  max-height: 160px;
  overflow-y: auto;
}
.cmt-emoji-btn {
  border: none;
  background: transparent;
  font-size: 1.2rem;
  padding: 4px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 120ms ease;
}
.cmt-emoji-btn:hover {
  background: var(--cmt-accent-soft, rgba(201, 150, 122, 0.18));
}
</style>
