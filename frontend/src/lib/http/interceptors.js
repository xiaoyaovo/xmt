export function setupInterceptors(instance) {
  instance.interceptors.request.use(
    (config) => {
      const accessToken = window.localStorage?.getItem('xinming_access_token')
      if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`
      }

      return config
    },
    (error) => Promise.reject(error)
  )

  instance.interceptors.response.use(
    (response) => response.data,
    (error) => {
      const message =
        error?.response?.data?.message ||
        error?.response?.data?.detail ||
        error?.message ||
        'Request failed'

      return Promise.reject({
        code: error?.response?.status || 'NETWORK_ERROR',
        message,
        error
      })
    }
  )
}
