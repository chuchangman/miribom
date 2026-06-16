import { PRODUCTS_API_URL, VIDEOS_API_URL, apiFetch } from '../config/api.js'

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

export const fetchCategories = async () => {
  const response = await apiFetch(`${PRODUCTS_API_URL}/categories/`)
  return await parseResponse(response, '카테고리를 불러오지 못했습니다.')
}

export const searchProducts = async ({ query = '', categoryId = null } = {}) => {
  const params = new URLSearchParams()

  if (query.trim()) {
    params.set('q', query.trim())
  }

  if (categoryId) {
    params.set('category', categoryId)
  }

  params.set('limit', 40)
  params.set('offset', 0)

  const queryString = params.toString()
  const url = queryString ? `${PRODUCTS_API_URL}/?${queryString}` : `${PRODUCTS_API_URL}/`
  const response = await apiFetch(url)
  const data = await parseResponse(response, '제품을 불러오지 못했습니다.')
  return data.results
}

export const createReviewFlow = async ({ file, productId, rating, content }) => {
  const presignedResponse = await apiFetch(`${VIDEOS_API_URL}/presigned-url/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      filename: file.name,
      content_type: file.type,
      file_size: file.size,
    }),
  })
  const presigned = await parseResponse(
    presignedResponse,
    '영상 업로드 주소를 발급받지 못했습니다.',
  )

  const uploadResponse = await fetch(presigned.presigned_url, {
    method: 'PUT',
    headers: { 'Content-Type': file.type },
    body: file,
  })

  if (!uploadResponse.ok) {
    throw new Error('영상 파일 업로드에 실패했습니다.')
  }

  const completeResponse = await apiFetch(
    `${VIDEOS_API_URL}/${presigned.video_upload_id}/complete/`,
    {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ r2_key: presigned.r2_key }),
    },
  )
  await parseResponse(completeResponse, '영상 업로드 완료 처리에 실패했습니다.')

  const videoResponse = await apiFetch(`${VIDEOS_API_URL}/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      video_upload_id: presigned.video_upload_id,
      product_id: productId,
    }),
  })
  const video = await parseResponse(videoResponse, '영상을 등록하지 못했습니다.')

  const reviewResponse = await apiFetch(`${VIDEOS_API_URL}/${video.id}/reviews/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rating, content }),
  })

  return await parseResponse(reviewResponse, '리뷰를 등록하지 못했습니다.')
}
