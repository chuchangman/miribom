<template>
  <button type="button" class="back-button" aria-label="이전으로" @click="goBack">
    <svg
      class="back-button__icon"
      viewBox="0 0 24 24"
      aria-hidden="true"
      focusable="false"
    >
      <path
        d="M15 19 8 12l7-7"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
  </button>
  <p v-if="isLoading">제품 정보를 불러오는 중입니다.</p>
  <div v-else-if="errorMessage">
    <h1>{{ errorMessage }}</h1>
  </div>
  <div v-else-if="!product">
    <h1>제품을 찾을 수 없습니다.</h1>
  </div>
  <div v-else class="product-detail">
    <section class="product-hero">
      <div class="image">
        <img :src="product.image" :alt="product.title" />
      </div>
      <div class="info">
        <p class="category-badge">{{ product.category?.name }}</p>
        <h1>{{ product.title }}</h1>
        <p class="brand">{{ product.brand }}</p>
        <p class="price">{{ (product.lprice || 0).toLocaleString() }}원</p>
        <a :href="product.link" target="_blank" rel="noopener noreferrer">네이버 상품 보기</a>
        <button
          type="button"
          class="bookmark-button"
          :disabled="isBookmarkPending"
          @click="toggleBookmark"
        >
          {{ bookmarkId ? '즐겨찾기 해제' : '즐겨찾기 추가' }}
        </button>
        <p v-if="bookmarkErrorMessage" class="error-message">{{ bookmarkErrorMessage }}</p>
      </div>
    </section>

    <section class="stats-grid">
      <article class="stat-card stat-card--rating">
        <span class="stat-label">평균 리뷰 평점</span>
        <strong>{{ averageRatingText }}</strong>
        <div class="rating-stars" aria-hidden="true">
          <div class="rating-stars__base">{{ starRow }}</div>
          <div class="rating-stars__fill" :style="{ width: averageStarWidth }">{{ starRow }}</div>
        </div>
        <p>{{ reviewCountText }}</p>
      </article>
      <article class="stat-card">
        <span class="stat-label">등록된 리뷰</span>
        <strong>{{ reviewCount }}</strong>
      </article>
    </section>

    <section class="product-reviews">
      <div class="section-header">
        <div>
          <h2>리뷰</h2>
          <p>{{ reviewCountText }}</p>
        </div>
      </div>

      <p v-if="isLoadingReviews">리뷰를 불러오는 중입니다.</p>
      <p v-else-if="reviewErrorMessage" class="error-message">{{ reviewErrorMessage }}</p>
      <p v-else-if="reviews.length === 0" class="empty-message">아직 등록된 리뷰가 없습니다.</p>
      <ul v-else class="review-list">
        <li v-for="review in reviews" :key="review.id">
          <div class="review-card" @click="openReviewModal(review)">
            <div class="review-card__video">
              <button
                type="button"
                class="review-like-button"
                :class="{ 'review-like-button--active': review.isLiked }"
                :disabled="likePendingVideoId === review.video_id"
                @click.stop="handleToggleLike(review)"
              >
                {{ review.isLiked ? '♥' : '♡' }}
                <span>{{ review.likeCount }}</span>
              </button>
              <video
                :src="review.videoUrl"
                :poster="review.thumbnailUrl || review.productImage || product.image"
                preload="metadata"
                muted
                playsinline
              ></video>
            </div>
            <div class="review-card__content">
              <div class="review-card__header">
                <strong>{{ review.user_nickname }}</strong>
              </div>
              <div class="review-card__stars" aria-hidden="true">
                <div class="rating-stars rating-stars--small">
                  <div class="rating-stars__base">{{ starRow }}</div>
                  <div class="rating-stars__fill" :style="{ width: getStarWidth(review.rating) }">
                    {{ starRow }}
                  </div>
                </div>
              </div>
              <p>{{ review.content }}</p>
              <small>클릭해서 영상과 후기를 크게 볼 수 있어요.</small>
            </div>
          </div>
        </li>
      </ul>
    </section>
  </div>

  <div v-if="selectedReview" class="review-modal" @click.self="closeReviewModal">
    <div class="review-modal__panel">
      <button type="button" class="review-modal__close" @click="closeReviewModal">닫기</button>
      <div class="review-modal__layout">
        <div class="review-modal__video-area">
          <div class="review-modal__video-frame">
            <video
              :src="selectedReview.videoUrl"
              :poster="selectedReview.thumbnailUrl || selectedReview.productImage || product?.image || ''"
              controls
              playsinline
              preload="metadata"
            ></video>
          </div>
        </div>
        <div class="review-modal__info">
          <div class="product-chip">
            <img :src="selectedReview.productImage || product?.image || ''" :alt="selectedReview.productTitle" />
            <div>
              <strong>{{ selectedReview.productTitle }}</strong>
              <p>{{ (selectedReview.productPrice || 0).toLocaleString() }}원</p>
            </div>
          </div>
          <div class="review-modal__summary">
            <div class="review-modal__summary-head">
              <strong>{{ selectedReview.user_nickname }}</strong>
              <div class="review-modal__summary-actions">
                <button
                  type="button"
                  class="review-like-button"
                  :class="{ 'review-like-button--active': selectedReview.isLiked }"
                  :disabled="likePendingVideoId === selectedReview.video_id"
                  @click="handleToggleLike(selectedReview)"
                >
                  {{ selectedReview.isLiked ? '♥' : '♡' }}
                  <span>{{ selectedReview.likeCount }}</span>
                </button>
                <span>{{ selectedReview.rating }} / 5</span>
              </div>
            </div>
            <div class="rating-stars" aria-hidden="true">
              <div class="rating-stars__base">{{ starRow }}</div>
              <div class="rating-stars__fill" :style="{ width: getStarWidth(selectedReview.rating) }">
                {{ starRow }}
              </div>
            </div>
            <form
              v-if="isReviewEditMode"
              class="modal-review-edit-form"
              @submit.prevent="handleUpdateSelectedReview"
            >
              <label>
                평점
                <select v-model.number="reviewEditForm.rating">
                  <option v-for="score in ratingOptions" :key="score" :value="score">
                    {{ score }}점
                  </option>
                </select>
              </label>
              <label>
                후기 내용
                <textarea
                  v-model="reviewEditForm.content"
                  maxlength="1000"
                  rows="7"
                  placeholder="실제 사용 경험을 적어주세요."
                ></textarea>
              </label>
              <p v-if="reviewActionMessage" class="review-action-message">
                {{ reviewActionMessage }}
              </p>
              <div class="modal-review-actions">
                <button type="button" class="modal-outline-button" @click="cancelReviewEdit">
                  취소
                </button>
                <button type="submit" class="modal-primary-button" :disabled="isSavingReview">
                  {{ isSavingReview ? '저장 중...' : '저장' }}
                </button>
              </div>
            </form>
            <p v-else>{{ selectedReview.content }}</p>
            <div v-if="canManageSelectedReview && !isReviewEditMode" class="modal-review-actions">
              <button type="button" class="modal-outline-button" @click="startReviewEdit">
                수정
              </button>
              <button
                type="button"
                class="modal-danger-button"
                :disabled="isDeletingReview"
                @click="handleDeleteSelectedReview"
              >
                {{ isDeletingReview ? '삭제 중...' : '삭제' }}
              </button>
            </div>
            <p v-if="reviewActionMessage && !isReviewEditMode" class="review-action-message">
              {{ reviewActionMessage }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createBookmark, deleteBookmark, fetchBookmarks } from '@/services/bookmarkApi.js'
import { useAuth } from '@/composables/useAuth.js'
import { fetchProductDetail } from '@/services/productApi.js'
import {
  deleteVideoReview,
  fetchVideoReviews,
  fetchVideos,
  toggleVideoLike,
  updateVideoReview,
} from '@/services/videoApi.js'

const route = useRoute()
const router = useRouter()
const { isAuthInitialized, isLogin, user } = useAuth()
const product = ref(null)
const videos = ref([])
const reviews = ref([])
const selectedReview = ref(null)
const isReviewEditMode = ref(false)
const isLoading = ref(false)
const isLoadingReviews = ref(false)
const errorMessage = ref('')
const reviewErrorMessage = ref('')
const reviewActionMessage = ref('')
const bookmarkId = ref(null)
const isBookmarkPending = ref(false)
const bookmarkErrorMessage = ref('')
const likePendingVideoId = ref(null)
const isSavingReview = ref(false)
const isDeletingReview = ref(false)
const starRow = '★★★★★'
const ratingOptions = [5, 4, 3, 2, 1]
const reviewEditForm = reactive({
  rating: 5,
  content: '',
})

const reviewCount = computed(() => reviews.value.length)
const averageRating = computed(() => {
  if (reviews.value.length === 0) {
    return 0
  }

  const total = reviews.value.reduce((sum, review) => sum + review.rating, 0)
  return total / reviews.value.length
})
const averageRatingText = computed(() =>
  reviews.value.length === 0 ? '-' : averageRating.value.toFixed(1),
)
const averageStarWidth = computed(() => `${(averageRating.value / 5) * 100}%`)
const reviewCountText = computed(() =>
  reviews.value.length === 0 ? '아직 리뷰가 없습니다.' : `총 ${reviews.value.length}개의 리뷰`,
)
const canManageSelectedReview = computed(() => {
  if (!selectedReview.value || !user.value?.id) {
    return false
  }

  return Number(selectedReview.value.user_id) === Number(user.value.id)
})

const getStarWidth = (rating) => `${(rating / 5) * 100}%`

const loadAllProductVideos = async (productId) => {
  const allVideos = []
  let cursor = null

  while (true) {
    const page = await fetchVideos({ productId, cursor })
    allVideos.push(...page)

    if (page.length < 20) {
      break
    }

    cursor = page.at(-1)?.id
    if (!cursor) {
      break
    }
  }

  return allVideos
}

const loadReviewSummary = async (productId) => {
  isLoadingReviews.value = true
  reviewErrorMessage.value = ''
  reviews.value = []
  videos.value = []

  try {
    const productVideos = await loadAllProductVideos(productId)
    videos.value = productVideos
    const videoMap = new Map(productVideos.map((video) => [video.id, video]))

    const reviewPages = await Promise.all(productVideos.map((video) => fetchVideoReviews(video.id)))

    reviews.value = reviewPages
      .flat()
      .map((review) => {
        const video = videoMap.get(review.video_id)
        return {
          ...review,
          videoUrl: video?.video_url || '',
          thumbnailUrl: video?.thumbnail_url || video?.thumbnailUrl || video?.product_image || product.value?.image || '',
          productImage: video?.product_image || product.value?.image || '',
          productTitle: video?.product_title || product.value?.title || '',
          productPrice: video?.product_lprice || product.value?.lprice || 0,
          isLiked: video?.is_liked ?? false,
          likeCount: video?.like_count ?? 0,
        }
      })
      .sort((left, right) => new Date(right.created_at) - new Date(left.created_at))
  } catch (error) {
    reviewErrorMessage.value = error.message || '리뷰 정보를 불러오지 못했습니다.'
  } finally {
    isLoadingReviews.value = false
  }
}

const loadProduct = async () => {
  isLoading.value = true
  errorMessage.value = ''
  bookmarkId.value = null
  bookmarkErrorMessage.value = ''
  selectedReview.value = null

  try {
    product.value = await fetchProductDetail(route.params.id)
    await loadReviewSummary(route.params.id)
  } catch (error) {
    product.value = null
    videos.value = []
    reviews.value = []
    errorMessage.value = error.message || '제품 상세 정보를 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

const goBack = () => {
  if (window.history.state?.back) {
    router.back()
    return
  }

  router.push({ name: 'ProductSearch' })
}

const loadBookmarkState = async () => {
  bookmarkErrorMessage.value = ''

  if (!isAuthInitialized.value || !isLogin.value || !product.value) {
    bookmarkId.value = null
    return
  }

  try {
    const bookmarks = await fetchBookmarks()
    const bookmark = bookmarks.find((item) => item.product.id === Number(product.value.id))
    bookmarkId.value = bookmark?.id || null
  } catch (error) {
    bookmarkErrorMessage.value = error.message || '즐겨찾기 상태를 불러오지 못했습니다.'
  }
}

const toggleBookmark = async () => {
  if (!isLogin.value) {
    router.push({ name: 'Login' })
    return
  }

  if (isBookmarkPending.value) {
    return
  }

  isBookmarkPending.value = true
  bookmarkErrorMessage.value = ''

  try {
    if (bookmarkId.value) {
      await deleteBookmark(bookmarkId.value)
      bookmarkId.value = null
    } else {
      const bookmark = await createBookmark(Number(product.value.id))
      bookmarkId.value = bookmark.id
    }
  } catch (error) {
    bookmarkErrorMessage.value = error.message || '즐겨찾기 상태를 변경하지 못했습니다.'
  } finally {
    isBookmarkPending.value = false
  }
}

const handleToggleLike = async (review) => {
  if (!isLogin.value) {
    router.push({ name: 'Login' })
    return
  }

  if (likePendingVideoId.value !== null) return

  likePendingVideoId.value = review.video_id

  try {
    const result = await toggleVideoLike(review.video_id)
    review.isLiked = result.liked
    review.likeCount = result.like_count
  } catch {
    // ignore
  } finally {
    likePendingVideoId.value = null
  }
}

const openReviewModal = (review) => {
  selectedReview.value = review
  isReviewEditMode.value = false
  reviewActionMessage.value = ''
  document.body.style.overflow = 'hidden'
}

const closeReviewModal = () => {
  selectedReview.value = null
  isReviewEditMode.value = false
  reviewActionMessage.value = ''
  document.body.style.overflow = ''
}

const startReviewEdit = () => {
  if (!canManageSelectedReview.value) {
    return
  }

  reviewEditForm.rating = selectedReview.value.rating
  reviewEditForm.content = selectedReview.value.content
  reviewActionMessage.value = ''
  isReviewEditMode.value = true
}

const cancelReviewEdit = () => {
  isReviewEditMode.value = false
  reviewActionMessage.value = ''
}

const handleUpdateSelectedReview = async () => {
  if (!selectedReview.value || isSavingReview.value) {
    return
  }

  const content = reviewEditForm.content.trim()
  if (!content) {
    reviewActionMessage.value = '후기 내용을 입력해주세요.'
    return
  }

  isSavingReview.value = true
  reviewActionMessage.value = ''

  try {
    const updatedReview = await updateVideoReview(
      selectedReview.value.video_id,
      selectedReview.value.id,
      {
        rating: reviewEditForm.rating,
        content,
      },
    )
    Object.assign(selectedReview.value, {
      rating: updatedReview.rating,
      content: updatedReview.content,
    })
    isReviewEditMode.value = false
  } catch (error) {
    reviewActionMessage.value = error.message || '리뷰를 수정하지 못했습니다.'
  } finally {
    isSavingReview.value = false
  }
}

const handleDeleteSelectedReview = async () => {
  if (!selectedReview.value || isDeletingReview.value) {
    return
  }

  const isConfirmed = window.confirm('이 리뷰를 삭제할까요? 삭제한 리뷰는 되돌릴 수 없습니다.')
  if (!isConfirmed) {
    return
  }

  const reviewId = selectedReview.value.id
  const videoId = selectedReview.value.video_id
  isDeletingReview.value = true
  reviewActionMessage.value = ''

  try {
    await deleteVideoReview(videoId, reviewId)
    reviews.value = reviews.value.filter((review) => review.id !== reviewId)
    closeReviewModal()
  } catch (error) {
    reviewActionMessage.value = error.message || '리뷰를 삭제하지 못했습니다.'
  } finally {
    isDeletingReview.value = false
  }
}

const handleKeydown = (event) => {
  if (event.key === 'Escape' && selectedReview.value) {
    closeReviewModal()
  }
}

watch(() => route.params.id, loadProduct, { immediate: true })
watch([isAuthInitialized, isLogin, product], loadBookmarkState)

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.product-detail {
  display: grid;
  gap: 24px;
}

.error-message {
  color: var(--color-danger);
}

.back-button {
  margin-bottom: 20px;
  border: none;
  border-radius: 999px;
  background: #fff;
  padding: 8px;
  color: #2563eb;
  cursor: pointer;
  line-height: 0;
  box-shadow: 0 8px 18px rgb(37 99 235 / 10%);
}

.back-button:hover {
  background-color: #eff6ff;
}

.back-button__icon {
  width: 24px;
  height: 24px;
}

.product-hero {
  display: flex;
  gap: 32px;
  align-items: flex-start;
  border: 1px solid var(--color-border);
  border-radius: 24px;
  background-color: #fff;
  padding: 28px;
}

.image {
  width: 300px;
  height: 300px;
  border-radius: 20px;
  background-color: #f3f7ff;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info h1,
.info p {
  margin: 0;
}

.category-badge {
  align-self: flex-start;
  border-radius: 999px;
  background-color: var(--color-primary-light);
  padding: 6px 10px;
  color: var(--color-primary-600);
  font-size: var(--font-size-caption);
  font-weight: 700;
}

.brand {
  color: var(--color-text-secondary);
}

.price {
  font-size: 1.6rem;
  font-weight: 800;
}

.info a {
  align-self: flex-start;
  color: #2563eb;
  font-weight: 700;
  text-decoration: none;
}

.bookmark-button {
  align-self: flex-start;
  border: 1px solid #2563eb;
  border-radius: 12px;
  background-color: white;
  padding: 10px 14px;
  color: #2563eb;
  cursor: pointer;
}

.bookmark-button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.stat-card {
  border: 1px solid var(--color-border);
  border-radius: 20px;
  background-color: #fff;
  padding: 20px;
}

.stat-card strong {
  display: block;
  margin-top: 10px;
  font-size: 2rem;
}

.stat-card p {
  margin: 10px 0 0;
  color: var(--color-text-secondary);
}

.stat-card--rating strong {
  margin-bottom: 10px;
}

.stat-label {
  color: var(--color-text-tertiary);
  font-size: var(--font-size-caption);
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.rating-stars {
  position: relative;
  width: fit-content;
  font-size: 1.6rem;
  line-height: 1;
}

.rating-stars--small {
  font-size: 1rem;
}

.rating-stars__base,
.rating-stars__fill {
  letter-spacing: 0.12em;
  white-space: nowrap;
}

.rating-stars__base {
  color: #d1d5db;
}

.rating-stars__fill {
  position: absolute;
  inset: 0 auto 0 0;
  overflow: hidden;
  color: #facc15;
}

.product-reviews {
  border: 1px solid var(--color-border);
  border-radius: 24px;
  background-color: #fff;
  padding: 24px;
  box-shadow: var(--shadow-md);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.section-header h2,
.section-header p {
  margin: 0;
}

.section-header p,
.empty-message {
  color: var(--color-text-secondary);
}

.review-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
}

.review-card {
  width: 100%;
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
  border: 1px solid var(--gray-200);
  border-radius: 20px;
  background-color: #fff;
  padding: 10px;
  text-align: left;
  cursor: pointer;
  transition:
    border-color var(--transition-fast),
    box-shadow var(--transition-fast),
    transform var(--transition-fast);
}

.review-card:hover {
  border-color: var(--color-primary-200);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.review-card__video {
  position: relative;
  overflow: hidden;
  border-radius: 14px;
  background-color: #0f172a;
  aspect-ratio: 4 / 4.6;
}

.review-like-button {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  border: 1px solid #fecdd3;
  border-radius: 999px;
  background-color: rgb(255 255 255 / 92%);
  color: #be123c;
  padding: 5px 9px;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  backdrop-filter: blur(2px);
}

.review-like-button--active {
  background-color: #fff1f2;
}

.review-like-button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.review-card__video video {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
}

.review-card__content {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.review-card__header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.review-card__content p {
  margin: 0;
  line-height: 1.4;
  font-size: 0.84rem;
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.review-card__content small {
  color: var(--color-text-secondary);
  font-size: 0.72rem;
}

.review-modal {
  position: fixed;
  inset: 0;
  z-index: 30;
  display: grid;
  place-items: center;
  background-color: rgb(15 23 42 / 72%);
  padding: 24px;
}

.review-modal__panel {
  width: min(1100px, 100%);
  border-radius: 28px;
  background-color: #fff;
  padding: 20px;
  box-shadow: 0 30px 70px rgb(15 23 42 / 28%);
}

.review-modal__close {
  display: block;
  margin-left: auto;
  margin-bottom: 14px;
  border: none;
  background: none;
  color: var(--color-text-secondary);
  font-weight: 700;
  cursor: pointer;
}

.review-modal__layout {
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(300px, 0.65fr);
  gap: 20px;
  align-items: start;
}

.review-modal__video-frame {
  overflow: hidden;
  border-radius: 24px;
  background-color: #0f172a;
  aspect-ratio: 9 / 16;
  max-height: 72vh;
}

.review-modal__video-frame video {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: contain;
}

.review-modal__info {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.product-chip {
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid var(--color-border);
  border-radius: 18px;
  background-color: var(--gray-50);
  padding: 12px;
}

.product-chip img {
  width: 72px;
  height: 72px;
  border-radius: 14px;
  background-color: #fff;
  object-fit: contain;
}

.product-chip strong,
.product-chip p,
.review-modal__summary p {
  margin: 0;
}

.product-chip p {
  margin-top: 4px;
  color: var(--color-primary-600);
  font-weight: 700;
}

.review-modal__summary {
  display: grid;
  gap: 10px;
  border: 1px solid var(--color-border);
  border-radius: 20px;
  background-color: #fff;
  padding: 16px;
}

.review-modal__summary-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.review-modal__summary-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.review-modal__summary-actions span {
  color: var(--color-primary-600);
  font-weight: 700;
}

.review-modal__summary .review-like-button {
  position: static;
}

.review-modal__summary p {
  line-height: 1.7;
}

.modal-review-edit-form {
  display: grid;
  gap: 12px;
}

.modal-review-edit-form label {
  display: grid;
  gap: 7px;
  color: var(--color-text);
  font-size: 0.9rem;
  font-weight: 800;
}

.modal-review-edit-form select,
.modal-review-edit-form textarea {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: 14px;
  background-color: #fff;
  padding: 11px 12px;
  color: var(--color-text);
  font: inherit;
}

.modal-review-edit-form textarea {
  resize: vertical;
}

.modal-review-actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.modal-primary-button,
.modal-outline-button,
.modal-danger-button {
  border-radius: 14px;
  padding: 11px 14px;
  font-weight: 800;
  cursor: pointer;
}

.modal-primary-button {
  border: 1px solid var(--color-primary-600);
  background: var(--color-primary-600);
  color: #fff;
}

.modal-outline-button {
  border: 1px solid #93c5fd;
  background: #fff;
  color: var(--color-primary-600);
}

.modal-danger-button {
  border: 1px solid #fecdd3;
  background: #fff1f2;
  color: #be123c;
}

.modal-primary-button:disabled,
.modal-outline-button:disabled,
.modal-danger-button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.review-action-message {
  color: var(--color-danger);
  font-weight: 700;
}

@media (max-width: 980px) {
  .product-hero {
    flex-direction: column;
  }

  .image {
    width: 100%;
    height: auto;
    aspect-ratio: 1;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .review-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .review-card {
    grid-template-columns: 1fr;
  }

  .review-card__video {
    aspect-ratio: 16 / 10;
  }

  .review-modal__layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .review-list {
    grid-template-columns: 1fr;
  }
}
</style>
