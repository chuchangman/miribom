<template>
  <p v-if="isLoading">영상 후기를 불러오는 중입니다.</p>
  <p v-else-if="errorMessage" class="error-message">{{ errorMessage }}</p>
  <p v-else-if="!video">등록된 영상 후기가 없습니다.</p>
  <section class="shorts-layout" v-else>
    <div class="video-area" @wheel.prevent="handleWheel">
      <div class="video-frame">
        <p v-if="isVideoLoading" class="video-loading">영상을 불러오는 중입니다.</p>
        <video
          :key="video.id"
          :src="video.videoUrl"
          :poster="video.thumbnailUrl || video.productImage || ''"
          controls
          autoplay
          muted
          playsinline
          preload="metadata"
          @loadstart="isVideoLoading = true"
          @waiting="isVideoLoading = true"
          @canplay="isVideoLoading = false"
          @playing="isVideoLoading = false"
          @error="handleVideoError"
        ></video>
        <video
          v-if="nextVideo"
          :key="`preload-${nextVideo.id}`"
          :src="nextVideo.videoUrl"
          class="preload-video"
          preload="metadata"
          muted
          playsinline
        ></video>
      </div>
      <div class="video-actions">
        <button
          type="button"
          class="shorts-action"
          :class="{ 'shorts-action--active': video.isLiked }"
          :disabled="isLikePending"
          @click="handleToggleLike"
        >
          <span>{{ video.isLiked ? '♥' : '♡' }}</span>
          <strong>{{ video.likeCount }}</strong>
        </button>
        <button
          type="button"
          class="shorts-action"
          :class="{ 'shorts-action--active': isCommentPanelOpen }"
          @click="toggleCommentPanel"
        >
          <span>💬</span>
          <strong>댓글</strong>
        </button>
        <button type="button" class="shorts-action" @click="handleShare">
          <span>↗</span>
          <strong>공유</strong>
        </button>
      </div>
    </div>
    <aside v-if="!isMobile" class="watch-panel">
      <div class="product-info" @click="goProductDetail(video.productId)">
        <p class="product-info__label">제품 정보</p>
        <p class="product-info__name">{{ video.productName }}</p>
        <p class="product-info__price">{{ video.productPrice.toLocaleString() }}원</p>
      </div>

      <div class="review-panel-section">
        <p v-if="isReviewLoading">후기 내용을 불러오는 중입니다.</p>
        <p v-else-if="reviewErrorMessage" class="error-message">{{ reviewErrorMessage }}</p>
        <div v-else-if="video.review" class="review-info">
          <p>평점 : {{ video.review.rating }} / 5</p>
          <p>작성자 : {{ video.review.userNickname }}</p>
          <p>후기내용 : {{ video.review.content }}</p>
        </div>
        <p v-else-if="video.isReviewLoaded">등록된 리뷰 내용이 없습니다.</p>
      </div>

      <div v-if="isCommentPanelOpen" class="comments-panel-section">
        <VideoComments :video-id="video.id" />
      </div>
    </aside>

    <template v-if="isMobile">
      <Transition name="overlay-fade">
        <div
          v-if="isCommentPanelOpen"
          class="mobile-comment-overlay"
          @click="toggleCommentPanel"
        />
      </Transition>
      <Transition name="drawer-slide">
        <div v-if="isCommentPanelOpen" class="mobile-comment-drawer">
          <div class="mobile-comment-drawer__header">
            <strong>댓글</strong>
            <button type="button" class="mobile-comment-drawer__close" @click="toggleCommentPanel">✕</button>
          </div>
          <div class="mobile-comment-drawer__product" @click="goProductDetail(video.productId)">
            <div class="mobile-drawer-product-info">
              <p class="product-info__label">제품 정보</p>
              <p class="product-info__name">{{ video.productName }}</p>
              <p class="product-info__price">{{ video.productPrice.toLocaleString() }}원</p>
            </div>
            <div v-if="video.review" class="mobile-drawer-review">
              <span class="mobile-review-rating">★ {{ video.review.rating }}</span>
              <span class="mobile-review-author">{{ video.review.userNickname }}</span>
              <p class="mobile-review-content">{{ video.review.content }}</p>
            </div>
            <p v-else-if="isReviewLoading" class="mobile-review-loading">후기 불러오는 중...</p>
            <p v-else-if="video.isReviewLoaded" class="mobile-review-loading">등록된 리뷰가 없습니다.</p>
          </div>
          <div class="mobile-comment-drawer__body">
            <VideoComments :video-id="video.id" />
          </div>
        </div>
      </Transition>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import VideoComments from '@/components/VideoComments.vue'
import { useAuth } from '@/composables/useAuth'
import {
  fetchVideoReviews,
  fetchVideos,
  mapVideoFeedItem,
  toggleVideoLike,
} from '@/services/videoApi.js'

const router = useRouter()
const { isLogin } = useAuth()
const isScrolling = ref(false)
const currentIndex = ref(0)
const videos = ref([])
const isLoading = ref(false)
const isLoadingMore = ref(false)
const isLikePending = ref(false)
const hasMoreVideos = ref(true)
const errorMessage = ref('')
const isVideoLoading = ref(true)
const isReviewLoading = ref(false)
const isCommentPanelOpen = ref(false)
const reviewErrorMessage = ref('')
let reviewRequestId = 0

const windowWidth = ref(window.innerWidth)
const handleWindowResize = () => { windowWidth.value = window.innerWidth }
const isMobile = computed(() => windowWidth.value <= 720)

const video = computed(() => {
  if (videos.value.length === 0) {
    return null
  }
  return videos.value[currentIndex.value]
})

const nextVideo = computed(() => {
  if (videos.value.length < 2) {
    return null
  }

  return videos.value[(currentIndex.value + 1) % videos.value.length]
})

const loadVideos = async ({ cursor = null, append = false } = {}) => {
  const videoItems = await fetchVideos({ cursor })
  const mappedVideos = videoItems.map(mapVideoFeedItem)

  videos.value = append ? [...videos.value, ...mappedVideos] : mappedVideos
  hasMoreVideos.value = videoItems.length === 20
}

const loadCurrentReview = async (currentVideo) => {
  if (!currentVideo || currentVideo.isReviewLoaded) {
    return
  }

  const requestId = ++reviewRequestId
  isReviewLoading.value = true
  reviewErrorMessage.value = ''

  try {
    const reviews = await fetchVideoReviews(currentVideo.id)

    if (requestId !== reviewRequestId) {
      return
    }

    const review = reviews[0] || null
    currentVideo.review = review
      ? {
          id: review.id,
          rating: review.rating,
          content: review.content,
          userNickname: review.user_nickname,
        }
      : null
    currentVideo.isReviewLoaded = true
  } catch (error) {
    if (requestId === reviewRequestId) {
      reviewErrorMessage.value = error.message || '후기 내용을 불러오지 못했습니다.'
    }
  } finally {
    if (requestId === reviewRequestId) {
      isReviewLoading.value = false
    }
  }
}

const loadInitialVideos = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    await loadVideos()
  } catch (error) {
    errorMessage.value = error.message || '영상 후기를 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

const handleToggleLike = async () => {
  if (!video.value || isLikePending.value) {
    return
  }

  if (!isLogin.value) {
    router.push('/login')
    return
  }

  isLikePending.value = true
  errorMessage.value = ''

  try {
    const result = await toggleVideoLike(video.value.id)
    video.value.isLiked = result.liked
    video.value.likeCount = result.like_count
  } catch (error) {
    errorMessage.value = error.message || '좋아요 상태를 변경하지 못했습니다.'
  } finally {
    isLikePending.value = false
  }
}

const toggleCommentPanel = () => {
  isCommentPanelOpen.value = !isCommentPanelOpen.value
}

const handleShare = () => {
  alert('공유 기능은 준비 중입니다.')
}

const handleWheel = async (event) => {
  if (isScrolling.value) {
    return
  }

  if (event.deltaY > 0) {
    await goNextVideo()
  } else if (event.deltaY < 0) {
    goPrevVideo()
  }

  isScrolling.value = true
  setTimeout(() => {
    isScrolling.value = false
  }, 500)
}

const goNextVideo = async () => {
  if (currentIndex.value < videos.value.length - 1) {
    currentIndex.value += 1
    return
  }

  if (!hasMoreVideos.value || isLoadingMore.value) {
    currentIndex.value = 0
    return
  }

  isLoadingMore.value = true
  errorMessage.value = ''

  try {
    const previousLength = videos.value.length
    const cursor = videos.value.at(-1)?.id
    await loadVideos({ cursor, append: true })

    if (videos.value.length > previousLength) {
      currentIndex.value += 1
    }
  } catch (error) {
    errorMessage.value = error.message || '다음 영상을 불러오지 못했습니다.'
  } finally {
    isLoadingMore.value = false
  }
}

const goPrevVideo = () => {
  currentIndex.value = (currentIndex.value - 1 + videos.value.length) % videos.value.length
}

const goProductDetail = (productId) => {
  router.push(`/products/${productId}`)
}

const handleVideoError = () => {
  isVideoLoading.value = false
  errorMessage.value = '영상을 재생하지 못했습니다.'
}

watch(
  video,
  (currentVideo) => {
    isVideoLoading.value = true
    isCommentPanelOpen.value = false
    loadCurrentReview(currentVideo)
  },
  { immediate: true },
)

onMounted(() => {
  loadInitialVideos()
  window.addEventListener('resize', handleWindowResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleWindowResize)
})
</script>

<style scoped>
.error-message {
  margin: 0;
  color: var(--color-danger);
}
.shorts-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 28px;
  align-items: start;
}
.video-area {
  display: grid;
  grid-template-columns: minmax(320px, min(48vw, 520px)) 96px;
  align-items: center;
  justify-content: center;
  gap: 18px;
  min-width: 0;
}
.video-frame {
  position: relative;
  width: min(100%, 520px);
  aspect-ratio: 9 / 16;
  overflow: hidden;
  border: 1px solid rgb(15 23 42 / 8%);
  border-radius: 28px;
  background:
    radial-gradient(circle at top, rgb(59 130 246 / 18%), transparent 30%),
    #020617;
  box-shadow: var(--shadow-lg);
  display: flex;
  justify-content: center;
  align-items: center;
  height: min(86vh, 820px);
  max-height: 86vh;
}
.video-loading {
  position: absolute;
  z-index: 1;
  margin: 0;
  padding: 10px 14px;
  border-radius: 8px;
  background-color: rgba(0, 0, 0, 0.65);
  color: white;
}
.video-frame video {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.preload-video {
  position: absolute;
  width: 1px !important;
  height: 1px !important;
  opacity: 0;
  pointer-events: none;
}
.video-actions {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}
.shorts-action {
  width: 62px;
  min-height: 62px;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  border: 1px solid transparent;
  border-radius: 50%;
  background-color: #f1f5f9;
  color: var(--color-text);
  padding: 8px;
  font-weight: 800;
  cursor: pointer;
  transition:
    background-color 0.15s ease,
    border-color 0.15s ease,
    color 0.15s ease,
    transform 0.15s ease;
}
.shorts-action:hover:not(:disabled) {
  border-color: var(--color-primary-200);
  background-color: #eaf2ff;
  transform: translateY(-1px);
}
.shorts-action span {
  font-size: 1.28rem;
  line-height: 1;
}
.shorts-action strong {
  font-size: 0.72rem;
  line-height: 1.15;
}
.shorts-action--active {
  border-color: #fecdd3;
  background-color: #fff1f2;
  color: #be123c;
}
.watch-panel {
  min-width: 0;
  width: 100%;
  height: min(86vh, 820px);
  min-height: 0;
  max-height: 86vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--color-border);
  border-radius: 24px;
  background-color: #fff;
  color: var(--color-text);
  box-shadow: var(--shadow-md);
}
.product-info {
  padding: 18px;
  border-bottom: 1px solid var(--color-border);
  cursor: pointer;
}
.product-info p {
  margin: 0;
}
.product-info__label {
  color: var(--color-text-secondary);
  font-size: 0.78rem;
  font-weight: 700;
  margin-bottom: 6px !important;
}
.product-info__name {
  font-size: 0.98rem;
  font-weight: 800;
  line-height: 1.4;
}
.product-info__price {
  margin-top: 8px !important;
  font-size: 1rem;
  font-weight: 800;
}
.product-info:hover {
  background-color: var(--gray-50);
}
.review-panel-section {
  padding: 16px 18px;
  border-bottom: 1px solid var(--color-border);
}
.review-info {
  display: grid;
  gap: 8px;
}
.review-info p {
  margin: 0;
}
.comments-panel-section {
  flex: 1 1 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 16px 18px;
}
.shorts-action:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

/* Mobile drawer product/review section */
.mobile-comment-drawer__product {
  flex-shrink: 0;
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border);
  background: #f8fafc;
  cursor: pointer;
  user-select: none;
}
.mobile-drawer-product-info {
  margin-bottom: 8px;
}
.mobile-drawer-review {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}
.mobile-review-rating {
  font-weight: 700;
  color: #f59e0b;
  font-size: 0.9rem;
}
.mobile-review-author {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}
.mobile-review-content {
  width: 100%;
  margin: 4px 0 0;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.mobile-review-loading {
  margin: 0;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

/* Mobile comment overlay & drawer */
.mobile-comment-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: rgb(0 0 0 / 45%);
}
.mobile-comment-drawer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 201;
  height: 62vh;
  background: #fff;
  border-radius: 20px 20px 0 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 -4px 24px rgb(0 0 0 / 12%);
}
.mobile-comment-drawer__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}
.mobile-comment-drawer__header strong {
  font-size: 1rem;
}
.mobile-comment-drawer__close {
  border: none;
  background: none;
  font-size: 1.1rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 4px 8px;
}
.mobile-comment-drawer__body {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
}

/* Transitions */
.overlay-fade-enter-active,
.overlay-fade-leave-active {
  transition: opacity 0.22s ease;
}
.overlay-fade-enter-from,
.overlay-fade-leave-to {
  opacity: 0;
}
.drawer-slide-enter-active,
.drawer-slide-leave-active {
  transition: transform 0.28s cubic-bezier(0.32, 0.72, 0, 1);
}
.drawer-slide-enter-from,
.drawer-slide-leave-to {
  transform: translateY(100%);
}

@media (max-width: 1080px) {
  .shorts-layout {
    grid-template-columns: 1fr;
  }
  .watch-panel {
    max-width: 520px;
    min-height: auto;
    max-height: none;
  }
}
@media (max-width: 720px) {
  .shorts-layout {
    gap: 0;
  }
  .video-area {
    display: block;
    position: relative;
  }
  .video-frame {
    width: 100%;
    border-radius: 22px;
  }
  .video-actions {
    position: absolute;
    right: 12px;
    bottom: 24px;
    width: auto;
    gap: 16px;
  }
  .shorts-action {
    background-color: rgb(0 0 0 / 40%);
    color: #fff;
    border-color: rgb(255 255 255 / 20%);
    backdrop-filter: blur(4px);
  }
  .shorts-action:hover:not(:disabled) {
    background-color: rgb(0 0 0 / 55%);
  }
  .shorts-action--active {
    background-color: rgb(190 18 60 / 60%);
    border-color: rgb(254 205 211 / 40%);
    color: #fff;
  }
  .watch-panel {
    max-width: none;
  }
}
</style>
