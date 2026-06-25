<template>
  <section>
    <h3>내가 올린 영상 후기만 볼 수 있습니다.</h3>
    <p v-if="isLoading">내가 올린 영상을 불러오는 중입니다.</p>
    <p v-else-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    <p v-else-if="myVideos.length === 0">내가 올린 영상이 없습니다.</p>
    <template v-else>
      <div class="my-video-grid">
        <div v-for="video in myVideos" :key="video.id" class="my-video-item">
          <LikedVideoCard
            :video="video"
            :is-like-pending="pendingVideoId === video.id"
            @toggle-like="handleToggleLike(video)"
            @open-product="goProductDetail(video.productId)"
          />

          <div class="my-review-panel">
            <form
              v-if="editingVideoId === video.id"
              class="review-edit-form"
              @submit.prevent="handleUpdateReview(video)"
            >
              <label>
                평점
                <select v-model.number="editForm.rating">
                  <option v-for="score in ratingOptions" :key="score" :value="score">
                    {{ score }}점
                  </option>
                </select>
              </label>
              <label>
                후기 내용
                <textarea
                  v-model="editForm.content"
                  maxlength="1000"
                  rows="5"
                  placeholder="실제 사용 경험을 적어주세요."
                ></textarea>
              </label>
              <p v-if="actionMessage" class="error-message">{{ actionMessage }}</p>
              <div class="review-edit-actions">
                <button type="button" class="outline-button" @click="cancelEdit">취소</button>
                <button
                  type="submit"
                  class="primary-button"
                  :disabled="pendingReviewId === video.review?.id"
                >
                  {{ pendingReviewId === video.review?.id ? '저장 중...' : '저장' }}
                </button>
              </div>
            </form>

            <template v-else>
              <div v-if="video.review" class="review-summary">
                <div class="review-summary__head">
                  <strong>{{ video.review.rating }}점</strong>
                  <span>{{ formatDate(video.review.created_at) }}</span>
                </div>
                <p>{{ video.review.content }}</p>
              </div>
              <p v-else class="review-empty">연결된 후기 정보를 찾지 못했습니다.</p>

              <div class="review-actions">
                <button
                  type="button"
                  class="outline-button"
                  :disabled="!video.review || pendingDeleteVideoId === video.id"
                  @click="startEdit(video)"
                >
                  수정
                </button>
                <button
                  type="button"
                  class="danger-button"
                  :disabled="pendingDeleteVideoId === video.id"
                  @click="handleDeleteVideo(video)"
                >
                  {{ pendingDeleteVideoId === video.id ? '삭제 중...' : '영상 삭제' }}
                </button>
              </div>
            </template>
          </div>
        </div>
      </div>
      <button
        v-if="hasMoreVideos"
        type="button"
        class="load-more-button"
        :disabled="isLoadingMore"
        @click="loadMoreMyVideos"
      >
        {{ isLoadingMore ? '불러오는 중...' : '더보기' }}
      </button>
    </template>
  </section>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import LikedVideoCard from '@/components/LikedVideoCard.vue'
import {
  deleteVideo,
  fetchMyReviews,
  fetchMyVideos,
  mapVideoFeedItem,
  toggleVideoLike,
  updateVideoReview,
} from '@/services/videoApi.js'

const router = useRouter()
const myVideos = ref([])
const isLoading = ref(false)
const isLoadingMore = ref(false)
const hasMoreVideos = ref(true)
const errorMessage = ref('')
const actionMessage = ref('')
const pendingVideoId = ref(null)
const pendingReviewId = ref(null)
const pendingDeleteVideoId = ref(null)
const editingVideoId = ref(null)
const ratingOptions = [5, 4, 3, 2, 1]
const editForm = reactive({
  rating: 5,
  content: '',
})

const fetchReviewsForVideos = async (videoIds) => {
  const missingVideoIds = new Set(videoIds.map(Number))
  const reviewByVideoId = new Map()
  let cursor = null

  while (missingVideoIds.size > 0) {
    const reviews = await fetchMyReviews({ cursor })

    reviews.forEach((review) => {
      const videoId = Number(review.video_id)
      if (missingVideoIds.has(videoId)) {
        reviewByVideoId.set(videoId, review)
        missingVideoIds.delete(videoId)
      }
    })

    if (reviews.length < 20) {
      break
    }

    cursor = reviews.at(-1)?.id
    if (!cursor) {
      break
    }
  }

  return reviewByVideoId
}

const attachReviews = async (videos) => {
  if (videos.length === 0) {
    return videos
  }

  const reviewByVideoId = await fetchReviewsForVideos(videos.map((video) => video.id))
  return videos.map((video) => ({
    ...video,
    review: reviewByVideoId.get(Number(video.id)) || null,
    isReviewLoaded: true,
  }))
}

const loadMyVideos = async ({ cursor = null, append = false } = {}) => {
  if (append) {
    isLoadingMore.value = true
  } else {
    isLoading.value = true
  }
  errorMessage.value = ''

  try {
    const videos = await fetchMyVideos({ cursor })
    const mappedVideos = await attachReviews(videos.map(mapVideoFeedItem))
    myVideos.value = append ? [...myVideos.value, ...mappedVideos] : mappedVideos
    hasMoreVideos.value = videos.length === 20
  } catch (error) {
    errorMessage.value = error.message || '내가 올린 영상을 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
    isLoadingMore.value = false
  }
}

const loadMoreMyVideos = async () => {
  if (!hasMoreVideos.value || isLoadingMore.value) {
    return
  }

  await loadMyVideos({
    cursor: myVideos.value.at(-1)?.id,
    append: true,
  })
}

const handleToggleLike = async (video) => {
  if (pendingVideoId.value !== null) {
    return
  }

  pendingVideoId.value = video.id
  errorMessage.value = ''

  try {
    const result = await toggleVideoLike(video.id)
    video.isLiked = result.liked
    video.likeCount = result.like_count
  } catch (error) {
    errorMessage.value = error.message || '좋아요 상태를 변경하지 못했습니다.'
  } finally {
    pendingVideoId.value = null
  }
}

const startEdit = (video) => {
  if (!video.review) {
    return
  }

  actionMessage.value = ''
  editingVideoId.value = video.id
  editForm.rating = video.review.rating
  editForm.content = video.review.content
}

const cancelEdit = () => {
  editingVideoId.value = null
  actionMessage.value = ''
}

const handleUpdateReview = async (video) => {
  if (!video.review || pendingReviewId.value !== null) {
    return
  }

  const content = editForm.content.trim()
  if (!content) {
    actionMessage.value = '후기 내용을 입력해주세요.'
    return
  }

  pendingReviewId.value = video.review.id
  actionMessage.value = ''

  try {
    const updatedReview = await updateVideoReview(video.id, video.review.id, {
      rating: editForm.rating,
      content,
    })
    video.review = {
      ...video.review,
      ...updatedReview,
    }
    editingVideoId.value = null
  } catch (error) {
    actionMessage.value = error.message || '후기를 수정하지 못했습니다.'
  } finally {
    pendingReviewId.value = null
  }
}

const handleDeleteVideo = async (video) => {
  if (pendingDeleteVideoId.value !== null) {
    return
  }

  const isConfirmed = window.confirm('이 영상 후기를 삭제할까요? 삭제한 영상은 되돌릴 수 없습니다.')
  if (!isConfirmed) {
    return
  }

  pendingDeleteVideoId.value = video.id
  actionMessage.value = ''
  errorMessage.value = ''

  try {
    await deleteVideo(video.id)
    myVideos.value = myVideos.value.filter((item) => item.id !== video.id)
    if (editingVideoId.value === video.id) {
      editingVideoId.value = null
    }
  } catch (error) {
    errorMessage.value = error.message || '영상을 삭제하지 못했습니다.'
  } finally {
    pendingDeleteVideoId.value = null
  }
}

const goProductDetail = (productId) => {
  router.push(`/products/${productId}`)
}

const formatDate = (dateText) => {
  if (!dateText) {
    return ''
  }

  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date(dateText))
}

onMounted(loadMyVideos)
</script>

<style scoped>
.error-message {
  color: var(--color-danger, #ef4444);
}

.my-video-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.my-video-item {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 12px;
}

.my-review-panel {
  display: grid;
  gap: 12px;
  border: 1px solid #dbe4f0;
  border-radius: 16px;
  background: #fff;
  padding: 14px;
  box-shadow: 0 10px 24px rgb(15 23 42 / 6%);
}

.review-summary {
  display: grid;
  gap: 8px;
}

.review-summary__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  color: #2563eb;
  font-size: 0.9rem;
  font-weight: 700;
}

.review-summary__head span {
  color: #64748b;
  font-size: 0.78rem;
}

.review-summary p,
.review-empty {
  margin: 0;
  color: #334155;
  font-size: 0.9rem;
  line-height: 1.5;
}

.review-summary p {
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.review-empty {
  color: #94a3b8;
}

.review-actions,
.review-edit-actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.review-edit-form {
  display: grid;
  gap: 10px;
}

.review-edit-form label {
  display: grid;
  gap: 6px;
  color: #0f172a;
  font-size: 0.86rem;
  font-weight: 700;
}

.review-edit-form select,
.review-edit-form textarea {
  width: 100%;
  border: 1px solid #dbe4f0;
  border-radius: 12px;
  background: #fff;
  padding: 10px 12px;
  color: #0f172a;
  font: inherit;
}

.review-edit-form textarea {
  resize: vertical;
}

.primary-button,
.outline-button,
.danger-button {
  border-radius: 12px;
  padding: 10px 12px;
  font-weight: 800;
  cursor: pointer;
}

.primary-button {
  border: 1px solid #2563eb;
  background: #2563eb;
  color: #fff;
}

.outline-button {
  border: 1px solid #93c5fd;
  background: #fff;
  color: #2563eb;
}

.danger-button {
  border: 1px solid #fecdd3;
  background: #fff1f2;
  color: #be123c;
}

.primary-button:disabled,
.outline-button:disabled,
.danger-button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

@media (max-width: 768px) {
  .my-video-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.load-more-button {
  display: block;
  margin: 24px auto 0;
  border: 1px solid #cbd5e1;
  border-radius: 999px;
  background-color: #fff;
  padding: 10px 18px;
  font-weight: 700;
  cursor: pointer;
}

.load-more-button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
