import { defineStore } from 'pinia'

import {
  clearAccessToken,
  createOAuthLinkUrl,
  getAccessToken,
  getCurrentUser,
  githubLoginUrl,
  listAuthAccounts,
  linuxdoLoginUrl,
  loginPageUrl,
  logout as requestLogout,
  passwordLogin,
  registerWithCode,
  requestPasswordResetCode,
  requestRegisterCode,
  resetPassword,
  setAccessToken
} from 'src/lib/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: getAccessToken(),
    user: null,
    loading: false,
    initialized: false
  }),

  getters: {
    authenticated: (state) => Boolean(state.user)
  },

  actions: {
    async refreshMe() {
      const tokenAtRequestStart = getAccessToken()
      this.loading = true
      try {
        const response = await getCurrentUser()
        if (getAccessToken() !== tokenAtRequestStart) {
          return
        }

        this.user = response?.authenticated ? response.user : null
        if (!this.user) {
          this.accessToken = null
          clearAccessToken()
        } else {
          this.accessToken = tokenAtRequestStart
        }
      } catch {
        if (getAccessToken() !== tokenAtRequestStart) {
          return
        }

        this.user = null
        this.accessToken = null
        clearAccessToken()
      } finally {
        this.loading = false
        this.initialized = true
      }
    },

    async acceptAccessToken(token) {
      this.accessToken = token
      setAccessToken(token)
      await this.refreshMe()
    },

    async loginWithPassword(credentials) {
      const response = await passwordLogin(credentials)
      this.user = response.user || null
      this.accessToken = response.access_token
      setAccessToken(response.access_token)
      return response
    },

    async requestRegisterCode(email) {
      return requestRegisterCode(email)
    },

    async register({ email, code, password, username }) {
      const response = await registerWithCode({ email, code, password, username })
      this.user = response.user || null
      this.accessToken = response.access_token
      setAccessToken(response.access_token)
      return response
    },

    async requestPasswordResetCode(email) {
      return requestPasswordResetCode(email)
    },

    async resetPassword(payload) {
      return resetPassword(payload)
    },

    openLoginPage(redirect) {
      window.location.href = loginPageUrl(redirect)
    },

    loginWithGitHub() {
      window.location.href = githubLoginUrl()
    },

    loginWithLinuxDo(redirect) {
      window.location.href = linuxdoLoginUrl(redirect)
    },

    async linkProvider(provider, redirect = '/account/security', options = {}) {
      const response = await createOAuthLinkUrl(provider, redirect, options)
      window.location.href = response.url
    },

    async listAccounts() {
      return listAuthAccounts()
    },

    async logout() {
      await requestLogout()
      this.user = null
      this.accessToken = null
      clearAccessToken()
    }
  }
})
