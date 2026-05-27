<script setup>
import { computed } from 'vue'

const props = defineProps({
  account: {
    type: Object,
    required: true
  },
  busy: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['link', 'unlink'])

const providerMeta = {
  password: {
    label: '账号密码',
    mark: 'P',
    caption: '用于本地账号直接登录',
    unlinkedCaption: '绑定邮箱并设置密码后可直接登录'
  },
  github: {
    label: 'GitHub',
    mark: 'GH',
    caption: '使用 GitHub OAuth 登录当前账号',
    unlinkedCaption: '绑定后可用 GitHub 登录同一个账号'
  },
  linuxdo: {
    label: 'LinuxDo',
    mark: 'LD',
    caption: '使用 LinuxDo Connect 登录当前账号',
    unlinkedCaption: '绑定后可用 LinuxDo 登录同一个账号'
  }
}

const meta = computed(() => providerMeta[props.account.provider] || {
  label: props.account.provider,
  mark: props.account.provider?.slice(0, 2)?.toUpperCase() || '?',
  caption: '第三方登录方式',
  unlinkedCaption: '绑定后可用于登录'
})

const displayName = computed(() => {
  if (!props.account.linked) return meta.value.unlinkedCaption

  return props.account.provider_username || props.account.provider_email || props.account.provider_user_id || '已绑定'
})

const caption = computed(() => {
  if (!props.account.linked) return meta.value.unlinkedCaption
  if (props.account.provider_email && props.account.provider_email !== displayName.value) {
    return props.account.provider_email
  }

  return meta.value.caption
})

const actionLabel = computed(() => {
  if (props.busy) return '处理中...'
  if (!props.account.linked) return props.account.provider === 'password' ? '绑定邮箱登录' : '绑定'
  return props.account.can_unlink ? '解绑' : '已绑定'
})

const actionDisabled = computed(() => {
  if (props.busy) return true
  if (!props.account.linked) return false
  return !props.account.can_unlink
})

function handleAction() {
  if (actionDisabled.value) return
  emit(props.account.linked ? 'unlink' : 'link', props.account.provider)
}
</script>

<template>
  <article
    class="auth-account-row"
    :class="{ 'auth-account-row-linked': account.linked }"
  >
    <div class="auth-account-mark">
      <img
        v-if="account.avatar_url"
        class="auth-account-avatar"
        :src="account.avatar_url"
        :alt="meta.label"
      >
      <span v-else>{{ meta.mark }}</span>
    </div>

    <div class="auth-account-copy">
      <div class="auth-account-title-line">
        <h2 class="auth-account-title">{{ meta.label }}</h2>
        <span
          class="auth-account-badge"
          :class="{ 'auth-account-badge-linked': account.linked }"
        >
          {{ account.linked ? '已绑定' : '未绑定' }}
        </span>
      </div>
      <p class="auth-account-name">{{ displayName }}</p>
      <p class="auth-account-caption">{{ caption }}</p>
    </div>

    <UButton
      class="auth-account-action"
      :class="{ 'auth-account-action-danger': account.linked && account.can_unlink }"
      :color="account.linked && account.can_unlink ? 'error' : 'primary'"
      :label="actionLabel"
      :loading="busy"
      :variant="account.linked && account.can_unlink ? 'soft' : 'solid'"
      type="button"
      :disabled="actionDisabled"
      @click="handleAction"
    />
  </article>
</template>

<style scoped>
.auth-account-row {
  align-items: center;
  background: rgba(255, 255, 255, 0.84);
  border: 1px solid rgba(16, 37, 66, 0.1);
  border-radius: var(--brand-radius-md, 16px);
  display: grid;
  gap: 18px;
  grid-template-columns: auto minmax(0, 1fr) auto;
  min-height: 112px;
  padding: 18px;
}

.auth-account-row-linked {
  background: rgba(255, 255, 255, 0.94);
}

.auth-account-mark {
  align-items: center;
  background: rgba(16, 37, 66, 0.08);
  border-radius: 18px;
  color: var(--shell-navy);
  display: inline-flex;
  font-size: 0.82rem;
  font-weight: 900;
  height: 58px;
  justify-content: center;
  overflow: hidden;
  width: 58px;
}

.auth-account-avatar {
  height: 100%;
  object-fit: cover;
  width: 100%;
}

.auth-account-copy {
  min-width: 0;
}

.auth-account-title-line {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.auth-account-title {
  color: var(--shell-navy);
  font-size: 1.05rem;
  font-weight: 860;
  line-height: 1.2;
  margin: 0;
}

.auth-account-badge {
  background: rgba(15, 23, 35, 0.07);
  border-radius: var(--brand-radius-pill, 999px);
  color: rgba(16, 37, 66, 0.66);
  font-size: 0.75rem;
  font-weight: 850;
  padding: 4px 9px;
}

.auth-account-badge-linked {
  background: rgba(38, 194, 129, 0.16);
  color: #137a4d;
}

.auth-account-name,
.auth-account-caption {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.auth-account-name {
  color: var(--shell-ink);
  font-size: 0.95rem;
  font-weight: 760;
  margin: 10px 0 0;
}

.auth-account-caption {
  color: rgba(15, 23, 35, 0.58);
  font-size: 0.86rem;
  margin: 7px 0 0;
}

.auth-account-action {
  background: #ffffff;
  border: 1px solid rgba(16, 37, 66, 0.12);
  border-radius: var(--brand-radius-pill, 999px);
  color: var(--shell-navy);
  cursor: pointer;
  font: inherit;
  font-size: 0.84rem;
  font-weight: 850;
  min-width: 88px;
  padding: 10px 14px;
}

.auth-account-action:hover,
.auth-account-action:focus-visible {
  border-color: rgba(16, 37, 66, 0.22);
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.12));
  outline: none;
}

.auth-account-action-danger:hover,
.auth-account-action-danger:focus-visible {
  border-color: rgba(204, 45, 45, 0.28);
  color: #a52626;
}

.auth-account-action:disabled {
  cursor: not-allowed;
  opacity: 0.52;
}

@media (max-width: 620px) {
  .auth-account-row {
    align-items: flex-start;
    grid-template-columns: auto minmax(0, 1fr);
  }

  .auth-account-action {
    grid-column: 2;
    justify-self: start;
  }
}
</style>
