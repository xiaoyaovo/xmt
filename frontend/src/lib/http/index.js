import axios from 'axios'

import { setupInterceptors } from './interceptors'

function resolveDefaultApiBaseUrl() {
  if (typeof window === 'undefined') {
    return 'http://localhost:8000/api/v1'
  }

  return `${window.location.protocol}//${window.location.hostname}:8000/api/v1`
}

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || resolveDefaultApiBaseUrl()

export function createRequest(options = {}) {
  const instance = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000,
    ...options
  })

  setupInterceptors(instance)
  return instance
}

export const request = createRequest()
