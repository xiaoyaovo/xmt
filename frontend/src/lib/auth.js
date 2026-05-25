import { request } from './http'
import { API_BASE_URL } from './http'

export const AUTH_TOKEN_STORAGE_KEY = 'xinming_access_token'

export function getCurrentUser() {
  return request.get('/auth/me')
}

export function logout() {
  return request.post('/auth/logout')
}

export function githubLoginUrl(redirect = window.location.hash.replace(/^#/, '') || '/tools') {
  const search = new URLSearchParams()
  if (redirect) {
    search.set('redirect', redirect)
  }
  if (window.location.origin) {
    search.set('frontend_origin', window.location.origin)
  }

  return `${API_BASE_URL.replace(/\/$/, '')}/auth/github/login?${search.toString()}`
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
