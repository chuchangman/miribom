import { VIDEOS_API_URL, apiFetch } from '../config/api.js'

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

export const fetchLikedVideos = async ({ cursor = null } = {}) => {
  const params = new URLSearchParams()

  if (cursor) {
    params.set('cursor', cursor)
  }

  const queryString = params.toString()
  const url = queryString
    ? `${VIDEOS_API_URL}/liked/?${queryString}`
    : `${VIDEOS_API_URL}/liked/`
  const response = await apiFetch(url)
  return await parseResponse(response, '좋아요한 영상 목록을 불러오지 못했습니다.')
}

export const toggleVideoLike = async (videoId) => {
  const response = await apiFetch(`${VIDEOS_API_URL}/${videoId}/like/`, {
    method: 'POST',
  })
  return await parseResponse(response, '좋아요 상태를 변경하지 못했습니다.')
}

export const fetchVideoComments = async (videoId, { cursor = null } = {}) => {
  const params = new URLSearchParams()

  if (cursor) {
    params.set('cursor', cursor)
  }

  const queryString = params.toString()
  const url = queryString
    ? `${VIDEOS_API_URL}/${videoId}/comments/?${queryString}`
    : `${VIDEOS_API_URL}/${videoId}/comments/`
  const response = await apiFetch(url)
  return await parseResponse(response, '댓글을 불러오지 못했습니다.')
}

export const createVideoComment = async (videoId, content) => {
  const response = await apiFetch(`${VIDEOS_API_URL}/${videoId}/comments/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  })
  return await parseResponse(response, '댓글을 작성하지 못했습니다.')
}

export const updateVideoComment = async (videoId, commentId, content) => {
  const response = await apiFetch(`${VIDEOS_API_URL}/${videoId}/comments/${commentId}/`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  })
  return await parseResponse(response, '댓글을 수정하지 못했습니다.')
}

export const deleteVideoComment = async (videoId, commentId) => {
  const response = await apiFetch(`${VIDEOS_API_URL}/${videoId}/comments/${commentId}/`, {
    method: 'DELETE',
  })
  return await parseResponse(response, '댓글을 삭제하지 못했습니다.')
}

export const mapVideoFeedItem = (videoItem) => ({
  id: videoItem.id,
  videoUrl: videoItem.video_url,
  thumbnailUrl: videoItem.thumbnail_url || videoItem.thumbnailUrl || videoItem.product_image || '',
  productId: videoItem.product_id,
  productName: videoItem.product_title,
  productImage: videoItem.product_image,
  productPrice: videoItem.product_lprice || 0,
  userNickname: videoItem.user_nickname,
  likeCount: videoItem.like_count || 0,
  isLiked: Boolean(videoItem.is_liked),
  review: null,
  isReviewLoaded: false,
})
