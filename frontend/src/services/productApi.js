import { PRODUCTS_API_URL, apiFetch } from '../config/api.js'

const parseResponse = async (response, fallbackMessage) => {
  if (response.ok) {
    return await response.json()
  }

  let message = fallbackMessage

  try {
    const data = await response.json()
    message = data.detail || data.error || message
  } catch {
    // Keep the fallback message when the response has no JSON body.
  }

  throw new Error(message)
}

export const fetchProductCategories = async () => {
  const response = await apiFetch(`${PRODUCTS_API_URL}/categories/`)
  return await parseResponse(response, '카테고리를 불러오지 못했습니다.')
}

export const fetchProducts = async ({
  query = '',
  categoryId = null,
  limit = 40,
  offset = 0,
} = {}) => {
  const params = new URLSearchParams()

  if (query.trim()) {
    params.set('q', query.trim())
  }

  if (categoryId) {
    params.set('category', categoryId)
  }

  params.set('limit', limit)
  params.set('offset', offset)

  const queryString = params.toString()
  const url = queryString ? `${PRODUCTS_API_URL}/?${queryString}` : `${PRODUCTS_API_URL}/`
  const response = await apiFetch(url)
  return await parseResponse(response, '제품을 불러오지 못했습니다.')
}

export const fetchProductDetail = async (productId) => {
  const response = await apiFetch(`${PRODUCTS_API_URL}/${productId}/`)
  return await parseResponse(response, '제품 상세 정보를 불러오지 못했습니다.')
}
