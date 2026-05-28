<script setup>
import { computed, onBeforeUnmount, reactive, shallowRef, watch } from 'vue'

const RESEND_COOLDOWN_SECONDS = 60

const props = defineProps({
  open: {
    type: Boolean,
    default: false
  },
  busy: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  notice: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:open', 'requestCode', 'confirm'])

const formState = reactive({
  email: '',
  code: '',
  password: ''
})
const passwordVisible = shallowRef(false)
const cooldownLeft = shallowRef(0)

let cooldownTimer = null

const isOpen = computed({
  get: () => props.open,
  set: (value) => emit('update:open', value)
})

const emailLooksValid = computed(() => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formState.email.trim()))
const canRequestCode = computed(() => !props.busy && cooldownLeft.value === 0 && emailLooksValid.value)
const canConfirm = computed(
  () =>
    !props.busy &&
    emailLooksValid.value &&
    formState.code.trim().length >= 4 &&
    formState.password.length >= 8
)

function validate(state) {
  const errors = []

  if (!state.email.trim()) {
    errors.push({ name: 'email', message: '请输入邮箱地址' })
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(state.email.trim())) {
    errors.push({ name: 'email', message: '请输入有效的邮箱地址' })
  }

  if (!state.code.trim()) {
    errors.push({ name: 'code', message: '请输入邮箱验证码' })
  } else if (state.code.trim().length < 4) {
    errors.push({ name: 'code', message: '验证码长度不正确' })
  }

  if (!state.password) {
    errors.push({ name: 'password', message: '请设置登录密码' })
  } else if (state.password.length < 8) {
    errors.push({ name: 'password', message: '密码至少需要 8 位' })
  }

  return errors
}

function stopCooldown() {
  if (cooldownTimer) {
    clearInterval(cooldownTimer)
    cooldownTimer = null
  }
}

function startCooldown() {
  cooldownLeft.value = RESEND_COOLDOWN_SECONDS
  stopCooldown()
  cooldownTimer = setInterval(() => {
    if (cooldownLeft.value <= 1) {
      cooldownLeft.value = 0
      stopCooldown()
      return
    }
    cooldownLeft.value -= 1
  }, 1000)
}

function resetForm() {
  formState.email = ''
  formState.code = ''
  formState.password = ''
  passwordVisible.value = false
  cooldownLeft.value = 0
  stopCooldown()
}

function requestCode() {
  if (!canRequestCode.value) return
  emit('requestCode', formState.email.trim(), {
    onSuccess: startCooldown
  })
}

function confirmBind() {
  if (!canConfirm.value) return
  emit('confirm', {
    email: formState.email.trim(),
    code: formState.code.trim(),
    password: formState.password
  })
}

watch(
  () => props.open,
  (value) => {
    if (!value) {
      resetForm()
    }
  }
)

onBeforeUnmount(stopCooldown)
</script>

<template>
  <UModal
    v-model:open="isOpen"
    title="绑定邮箱登录"
    description="验证邮箱并设置密码后，可用邮箱密码登录当前账号。"
    :ui="{ content: 'max-w-[512px]' }"
  >
    <template #body>
      <div class="bind-email-dialog-copy">
        <UBadge
          color="primary"
          variant="subtle"
        >
          邮箱登录
        </UBadge>
      </div>

      <UAlert
        v-if="notice"
        class="bind-email-dialog-alert"
        color="success"
        variant="soft"
        :description="notice"
      />
      <UAlert
        v-if="error"
        class="bind-email-dialog-alert"
        color="error"
        variant="soft"
        :description="error"
      />

      <UForm
        class="bind-email-dialog-form"
        :state="formState"
        :validate="validate"
        @submit="confirmBind"
      >
        <UFormField
          label="邮箱"
          name="email"
          required
        >
          <div class="bind-email-dialog-inline">
            <UInput
              v-model="formState.email"
              class="bind-email-dialog-grow"
              autocomplete="email"
              name="email"
              placeholder="you@example.com"
              type="email"
            />
            <UButton
              color="neutral"
              type="button"
              variant="subtle"
              :disabled="!canRequestCode"
              @click="requestCode"
            >
              {{ cooldownLeft ? `${cooldownLeft}s` : '获取验证码' }}
            </UButton>
          </div>
        </UFormField>

        <UFormField
          label="验证码"
          name="code"
          required
        >
          <UInput
            v-model="formState.code"
            autocomplete="one-time-code"
            inputmode="numeric"
            maxlength="6"
            name="code"
            placeholder="6 位验证码"
            type="text"
          />
        </UFormField>

        <UFormField
          label="登录密码"
          name="password"
          required
        >
          <div class="bind-email-dialog-inline">
            <UInput
              v-model="formState.password"
              class="bind-email-dialog-grow"
              autocomplete="new-password"
              name="password"
              placeholder="至少 8 位"
              :type="passwordVisible ? 'text' : 'password'"
            />
            <UButton
              color="neutral"
              type="button"
              variant="subtle"
              @click="passwordVisible = !passwordVisible"
            >
              {{ passwordVisible ? '隐藏' : '显示' }}
            </UButton>
          </div>
        </UFormField>

        <div class="bind-email-dialog-actions">
          <UButton
            color="neutral"
            type="button"
            variant="ghost"
            :disabled="busy"
            @click="isOpen = false"
          >
            取消
          </UButton>
          <UButton
            color="primary"
            type="submit"
            :disabled="!canConfirm"
            :loading="busy"
          >
            完成绑定
          </UButton>
        </div>
      </UForm>
    </template>
  </UModal>
</template>

<style scoped>
.bind-email-dialog-copy {
  margin-bottom: 14px;
}

.bind-email-dialog-alert {
  margin-bottom: 12px;
}

.bind-email-dialog-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.bind-email-dialog-inline {
  display: flex;
  gap: 10px;
}

.bind-email-dialog-grow {
  flex: 1 1 auto;
  min-width: 0;
}

.bind-email-dialog-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding-top: 4px;
}

@media (max-width: 520px) {
  .bind-email-dialog-inline,
  .bind-email-dialog-actions {
    flex-direction: column;
  }
}
</style>
