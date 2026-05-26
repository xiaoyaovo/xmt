import { request } from './http'
import { API_BASE_URL } from './http'

export const AUTH_TOKEN_STORAGE_KEY = 'xinming_access_token'

export function getCurrentUser() {
  return request.get('/auth/me')
}

export function logout() {
  return request.post('/auth/logout')
}

export function passwordLogin({ username, password }) {
  return request.post('/auth/login', { username, password })
}

export function listAuthAccounts() {
  return request.get('/auth/accounts')
}

export function unlinkAuthAccount(provider) {
  return request.delete(`/auth/accounts/${encodeURIComponent(provider)}`)
}

export function createOAuthLinkUrl(provider, redirect = '/account/security') {
  const search = new URLSearchParams()
  if (redirect) {
    search.set('redirect', redirect)
  }
  if (window.location.origin) {
    search.set('frontend_origin', window.location.origin)
  }

  return request.get(`/auth/${provider}/link?${search.toString()}`)
}

export function currentRouteRedirect() {
  if (typeof window === 'undefined') {
    return '/tools'
  }

  return window.location.hash.replace(/^#/, '') || '/tools'
}

export function loginPageUrl(redirect = currentRouteRedirect()) {
  const search = new URLSearchParams()
  if (redirect) {
    search.set('redirect', redirect)
  }

  return `/#/login${search.toString() ? `?${search.toString()}` : ''}`
}

export function oauthLoginUrl(provider, redirect = currentRouteRedirect()) {
  const search = new URLSearchParams()
  if (redirect) {
    search.set('redirect', redirect)
  }
  if (window.location.origin) {
    search.set('frontend_origin', window.location.origin)
  }

  return `${API_BASE_URL.replace(/\/$/, '')}/auth/${provider}/login?${search.toString()}`
}

export function githubLoginUrl(redirect = currentRouteRedirect()) {
  return oauthLoginUrl('github', redirect)
}

export function linuxdoLoginUrl(redirect = currentRouteRedirect()) {
  return oauthLoginUrl('linuxdo', redirect)
}

export function getAccessToken() {
  return window.localStorage?.getItem(AUTH_TOKEN_STORAGE_KEY) || null
}

export function setAccessToken(token) {
  if (!token) {
    window.localStorage?.removeItem(AUTH_TOKEN_STORAGE_KEY)
    return
  }

  window.localStorage?.setItem(AUTH_TOKEN_STORAGE_KEY, token)
}

export function clearAccessToken() {
  window.localStorage?.removeItem(AUTH_TOKEN_STORAGE_KEY)
}
