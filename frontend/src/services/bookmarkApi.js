import { PRODUCTS_API_URL, apiFetch } from '../config/api.js'

const parseResponse = async (response, fallbackMessage) => {
  if (response.ok) {
    if (response.status === 204) {
      return null
    }
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

export const fetchBookmarks = async () => {
  const response = await apiFetch(`${PRODUCTS_API_URL}/bookmarks/`)
  return await parseResponse(response, '즐겨찾기 목록을 불러오지 못했습니다.')
}

export const createBookmark = async (productId) => {
  const response = await apiFetch(`${PRODUCTS_API_URL}/bookmarks/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: productId }),
  })
  return await parseResponse(response, '즐겨찾기에 추가하지 못했습니다.')
}

export const deleteBookmark = async (bookmarkId) => {
  const response = await apiFetch(`${PRODUCTS_API_URL}/bookmarks/${bookmarkId}/`, {
    method: 'DELETE',
  })
  return await parseResponse(response, '즐겨찾기를 삭제하지 못했습니다.')
}
