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

export const fetchRecommendationOptions = async () => {
  const response = await apiFetch(`${PRODUCTS_API_URL}/recommendations/`)
  return await parseResponse(response, '추천 선택지를 불러오지 못했습니다.')
}

export const fetchProductRecommendations = async ({
  housingType,
  areaSize = null,
  categoryIds,
  budget,
  categoryAnswers = {},
}) => {
  const response = await apiFetch(`${PRODUCTS_API_URL}/recommendations/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      housing_type: housingType,
      area_size: areaSize,
      category_ids: categoryIds,
      budget,
      category_answers: categoryAnswers,
    }),
  })

  return await parseResponse(response, '추천 제품을 불러오지 못했습니다.')
}

export const fetchRecommendationQuestions = async (categoryIds = []) => {
  const params = new URLSearchParams()
  params.set('category_ids', categoryIds.join(','))

  const response = await apiFetch(`${PRODUCTS_API_URL}/recommendations/questions/?${params}`)
  return await parseResponse(response, '추천 질문을 불러오지 못했습니다.')
}
