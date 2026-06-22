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
        <button type="button" @click="goPrevVideo">이전</button>
        <button type="button" :disabled="isLoadingMore" @click="goNextVideo">
          {{ isLoadingMore ? '불러오는 중...' : '다음' }}
        </button>
      </div>
    </div>
    <aside class="watch-panel">
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
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
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

onMounted(loadInitialVideos)
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
.video-actions > button:not(.shorts-action) {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: 14px;
  background-color: #fff;
  padding: 11px 12px;
  color: var(--color-text);
  font-weight: 700;
  cursor: pointer;
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
.video-actions button:disabled,
.shorts-action:disabled {
  cursor: not-allowed;
  opacity: 0.6;
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
  .video-area {
    grid-template-columns: 1fr;
  }
  .video-frame {
    border-radius: 22px;
  }
  .watch-panel {
    max-width: none;
  }
}
</style>
