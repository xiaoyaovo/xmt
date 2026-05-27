<script setup>
import { computed, onMounted, shallowRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AccountDeleteDialog from 'src/components/account/AccountDeleteDialog.vue'
import AccountLinkResultDialog from 'src/components/account/AccountLinkResultDialog.vue'
import AuthAccountRow from 'src/components/account/AuthAccountRow.vue'
import BindEmailDialog from 'src/components/account/BindEmailDialog.vue'
import { listAuthAccounts, unlinkAuthAccount } from 'src/lib/auth'
import { useAuthStore } from 'src/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const accounts = shallowRef([])
const loading = shallowRef(false)
const actionProvider = shallowRef('')
const errorMessage = shallowRef('')
const noticeMessage = shallowRef('')
const linkResultOpen = shallowRef(false)
const deleteDialogOpen = shallowRef(false)
const deletingAccount = shallowRef(false)
const deleteError = shallowRef('')
const bindEmailOpen = shallowRef(false)
const bindingEmail = shallowRef(false)
const bindEmailError = shallowRef('')
const bindEmailNotice = shallowRef('')
const linkResult = shallowRef({
  provider: '',
  providerLabel: '第三方账号',
  status: '',
  message: ''
})

const accountCount = computed(() => accounts.value.filter((account) => account.linked).length)
const providerLabels = {
  github: 'GitHub',
  linuxdo: 'LinuxDo'
}

function providerLabel(provider) {
  return providerLabels[provider] || '第三方账号'
}

function readProviderCallback() {
  const providerStatus = typeof route.query.provider_status === 'string' ? route.query.provider_status : ''
  if (!providerStatus) return

  const provider = typeof route.query.provider === 'string' ? route.query.provider : ''
  const label = providerLabel(provider)
  const message = typeof route.query.message === 'string' ? route.query.message : ''
  linkResult.value = {
    provider,
    providerLabel: label,
    status: providerStatus,
    message
  }
  linkResultOpen.value = true

  router.replace({ path: route.path })
}

async function loadAccounts() {
  loading.value = true
  try {
    if (!auth.initialized) {
      await auth.refreshMe()
    }
    if (!auth.authenticated) {
      accounts.value = []
      return
    }

    const response = await listAuthAccounts()
    accounts.value = response.accounts || []
  } catch (error) {
    errorMessage.value = error.message || '读取绑定状态失败'
  } finally {
    loading.value = false
  }
}

async function linkProvider(provider, options = {}) {
  if (provider === 'password') {
    bindEmailError.value = ''
    bindEmailNotice.value = ''
    bindEmailOpen.value = true
    return
  }

  actionProvider.value = provider
  errorMessage.value = ''
  noticeMessage.value = ''
  try {
    await auth.linkProvider(provider, '/account/security', {
      ...options,
      selectAccount: provider === 'github' || options.selectAccount
    })
  } catch (error) {
    actionProvider.value = ''
    errorMessage.value = error.message || '无法开始绑定，请稍后重试'
  }
}

function friendlyAuthMessage(error, fallback) {
  if (!error) return fallback
  if (error.code === 429) {
    return error.message || '请求过于频繁，请稍后再试'
  }
  if (error.code === 'NETWORK_ERROR') {
    return '网络异常，请检查连接后重试'
  }
  return error.message || fallback
}

async function requestBindEmailCode(email, controls = {}) {
  bindingEmail.value = true
  bindEmailError.value = ''
  bindEmailNotice.value = ''
  try {
    await auth.requestBindEmailCode(email)
    bindEmailNotice.value = '验证码已发送，请在 10 分钟内填写。'
    controls.onSuccess?.()
  } catch (error) {
    bindEmailError.value = friendlyAuthMessage(error, '发送验证码失败，请稍后重试')
  } finally {
    bindingEmail.value = false
  }
}

async function bindEmailLogin(payload) {
  bindingEmail.value = true
  bindEmailError.value = ''
  bindEmailNotice.value = ''
  try {
    await auth.bindEmailLogin(payload)
    bindEmailOpen.value = false
    noticeMessage.value = '邮箱登录已绑定'
    await auth.refreshMe()
    await loadAccounts()
  } catch (error) {
    bindEmailError.value = friendlyAuthMessage(error, '绑定失败，请检查验证码后重试')
  } finally {
    bindingEmail.value = false
  }
}

async function unlinkProvider(provider) {
  const account = accounts.value.find((item) => item.provider === provider)
  if (!account?.can_unlink) return

  actionProvider.value = provider
  errorMessage.value = ''
  noticeMessage.value = ''
  try {
    await unlinkAuthAccount(provider)
    noticeMessage.value = '登录方式已解绑'
    await auth.refreshMe()
    await loadAccounts()
  } catch (error) {
    errorMessage.value = error.message || '解绑失败，请稍后重试'
  } finally {
    actionProvider.value = ''
  }
}

function handleDialogLogin() {
  linkResultOpen.value = false
  auth.openLoginPage('/account/security')
}

async function handleDialogRetry() {
  const provider = linkResult.value.provider
  linkResultOpen.value = false
  if (provider) {
    await linkProvider(provider)
  }
}

function openDeleteDialog() {
  deleteError.value = ''
  deleteDialogOpen.value = true
}

async function deleteAccount() {
  deletingAccount.value = true
  deleteError.value = ''
  try {
    await auth.deleteAccount()
    deleteDialogOpen.value = false
    window.location.href = '/#/login'
  } catch (error) {
    deleteError.value = error.message || '账号删除失败，请稍后重试'
  } finally {
    deletingAccount.value = false
  }
}

onMounted(async () => {
  readProviderCallback()
  await loadAccounts()
})
</script>

<template>
  <div class="account-security-page">
    <section class="account-security-shell">
      <header class="account-security-header">
        <div>
          <div class="section-kicker">Account Security</div>
          <h1 class="account-security-title">登录方式绑定</h1>
          <p class="account-security-description">
            查看当前绑定状态，并将更多第三方登录方式关联到这个账号。
          </p>
        </div>

        <div class="account-security-summary">
          <span class="account-security-summary-number">{{ accountCount }}</span>
          <span class="account-security-summary-label">已绑定</span>
        </div>
      </header>

      <div
        v-if="!auth.initialized || auth.loading || loading"
        class="account-security-state"
      >
        正在读取绑定状态
      </div>

      <p
        v-if="noticeMessage && !linkResultOpen"
        class="account-security-notice"
      >
        {{ noticeMessage }}
      </p>
      <p
        v-if="errorMessage && !linkResultOpen"
        class="account-security-error"
      >
        {{ errorMessage }}
      </p>

      <div
        v-if="auth.initialized && !auth.loading && !loading && !auth.authenticated"
        class="account-security-state"
      >
        登录后管理账号绑定。
        <UButton
          class="account-security-login"
          color="primary"
          label="登录"
          type="button"
          @click="auth.openLoginPage('/account/security')"
        />
      </div>

      <template v-if="auth.initialized && !auth.loading && !loading && auth.authenticated">
        <div class="account-security-list">
          <AuthAccountRow
            v-for="account in accounts"
            :key="account.provider"
            :account="account"
            :busy="actionProvider === account.provider"
            @link="linkProvider"
            @unlink="unlinkProvider"
          />
        </div>

        <section class="account-security-danger">
          <div>
            <h2 class="account-security-danger-title">删除账号</h2>
            <p class="account-security-danger-copy">
              删除当前账号会同时清除登录方式、云端同步数据、CSV 历史与已上传文件。
            </p>
          </div>
          <UButton
            class="account-security-danger-button"
            color="error"
            label="删除账号"
            type="button"
            variant="soft"
            @click="openDeleteDialog"
          />
        </section>
      </template>

      <AccountLinkResultDialog
        v-model:open="linkResultOpen"
        :status="linkResult.status"
        :provider-label="linkResult.providerLabel"
        :message="linkResult.message"
        @login="handleDialogLogin"
        @retry="handleDialogRetry"
      />

      <BindEmailDialog
        v-model:open="bindEmailOpen"
        :busy="bindingEmail"
        :error="bindEmailError"
        :notice="bindEmailNotice"
        @request-code="requestBindEmailCode"
        @confirm="bindEmailLogin"
      />

      <AccountDeleteDialog
        v-model:open="deleteDialogOpen"
        :busy="deletingAccount"
        :error="deleteError"
        @confirm="deleteAccount"
      />
    </section>
  </div>
</template>

<style scoped>
.account-security-page {
  min-height: calc(100vh - 64px);
  padding: 34px 18px 58px;
}

.account-security-shell {
  margin: 0 auto;
  max-width: 980px;
}

.account-security-header {
  align-items: flex-end;
  display: flex;
  gap: 22px;
  justify-content: space-between;
  margin-bottom: 22px;
}

.account-security-title {
  color: var(--shell-navy);
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 880;
  letter-spacing: 0;
  line-height: 1.02;
  margin: 12px 0 10px;
}

.account-security-description {
  color: rgba(15, 23, 35, 0.66);
  line-height: 1.7;
  margin: 0;
  max-width: 560px;
}

.account-security-summary {
  align-items: center;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(16, 37, 66, 0.1);
  border-radius: var(--brand-radius-md, 16px);
  display: inline-flex;
  gap: 10px;
  min-width: 112px;
  padding: 14px 16px;
}

.account-security-summary-number {
  color: var(--shell-navy);
  font-size: 1.7rem;
  font-weight: 900;
}

.account-security-summary-label {
  color: rgba(15, 23, 35, 0.6);
  font-size: 0.82rem;
  font-weight: 820;
}

.account-security-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.account-security-danger {
  align-items: center;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(157, 37, 37, 0.18);
  border-radius: var(--brand-radius-md, 16px);
  display: flex;
  gap: 18px;
  justify-content: space-between;
  margin-top: 18px;
  padding: 18px;
}

.account-security-danger-title {
  color: #9d2525;
  font-size: 1rem;
  font-weight: 900;
  letter-spacing: 0;
  line-height: 1.2;
  margin: 0 0 6px;
}

.account-security-danger-copy {
  color: rgba(15, 23, 35, 0.64);
  line-height: 1.7;
  margin: 0;
}

.account-security-danger-button {
  background: #9d2525;
  border: 1px solid #9d2525;
  border-radius: var(--brand-radius-md, 16px);
  color: #ffffff;
  cursor: pointer;
  flex: 0 0 auto;
  font: inherit;
  font-weight: 850;
  min-height: 40px;
  padding: 0 16px;
}

.account-security-danger-button:hover {
  background: #7f1d1d;
}

.account-security-danger-button:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.14));
  outline: none;
}

.account-security-state,
.account-security-error,
.account-security-notice {
  background: rgba(255, 255, 255, 0.84);
  border: 1px solid rgba(16, 37, 66, 0.1);
  border-radius: var(--brand-radius-md, 16px);
  color: rgba(15, 23, 35, 0.72);
  line-height: 1.7;
  margin: 0;
  padding: 18px;
}

.account-security-error {
  border-color: rgba(204, 45, 45, 0.2);
  color: #9d2525;
  margin-bottom: 14px;
}

.account-security-notice {
  border-color: rgba(38, 194, 129, 0.22);
  color: #137a4d;
  margin-bottom: 14px;
}

.account-security-login {
  background: var(--brand-color-accent, #102542);
  border: 0;
  border-radius: var(--brand-radius-md, 16px);
  color: #ffffff;
  cursor: pointer;
  font: inherit;
  font-weight: 850;
  margin-left: 10px;
  padding: 8px 14px;
}

.account-security-login:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.14));
  outline: none;
}

@media (max-width: 760px) {
  .account-security-page {
    padding: 24px 14px 42px;
  }

  .account-security-header {
    align-items: stretch;
    flex-direction: column;
  }

  .account-security-summary {
    align-self: flex-start;
  }

  .account-security-danger {
    align-items: stretch;
    flex-direction: column;
  }

  .account-security-danger-button {
    width: 100%;
  }
}
</style>
