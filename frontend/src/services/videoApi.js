import { VIDEOS_API_URL, apiFetch } from '../config/api.js'

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

export const fetchVideos = async ({ cursor = null, productId = null } = {}) => {
  const params = new URLSearchParams()

  if (cursor) {
    params.set('cursor', cursor)
  }

  if (productId) {
    params.set('product_id', productId)
  }

  const queryString = params.toString()
  const url = queryString ? `${VIDEOS_API_URL}/?${queryString}` : `${VIDEOS_API_URL}/`
  const response = await apiFetch(url)
  return await parseResponse(response, '영상 목록을 불러오지 못했습니다.')
}

export const fetchVideoReviews = async (videoId) => {
  const response = await apiFetch(`${VIDEOS_API_URL}/${videoId}/reviews/`)
  return await parseResponse(response, '영상 리뷰를 불러오지 못했습니다.')
}

export const mapVideoFeedItem = (videoItem) => ({
  id: videoItem.id,
  videoUrl: videoItem.video_url,
  productId: videoItem.product_id,
  productName: videoItem.product_title,
  productPrice: videoItem.product_lprice || 0,
  userNickname: videoItem.user_nickname,
  review: null,
  isReviewLoaded: false,
})
