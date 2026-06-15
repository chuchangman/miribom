export const API_BASE_URL = 'http://localhost:8000/api'
export const AUTH_API_URL = `${API_BASE_URL}/auth`
export const PRODUCTS_API_URL = `${API_BASE_URL}/products`
export const VIDEOS_API_URL = `${API_BASE_URL}/videos`

export const apiFetch = async (url, options = {}) => {
  const requestOptions = {
    ...options,
    credentials: 'include',
  }

  let response = await fetch(url, requestOptions)

  if (response.status !== 401) {
    return response
  }

  const refreshResponse = await fetch(`${AUTH_API_URL}/refresh/`, {
    method: 'POST',
    credentials: 'include',
  })

  if (!refreshResponse.ok) {
    return response
  }

  response = await fetch(url, requestOptions)
  return response
}
