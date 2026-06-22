<template>
  <h1>쇼츠페이지</h1>
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
          class="like-action"
          :class="{ 'like-action--active': video.isLiked }"
          :disabled="isLikePending"
          @click="handleToggleLike"
        >
          {{ video.isLiked ? '♥ 좋아요' : '♡ 좋아요' }}
          <span>{{ video.likeCount }}</span>
        </button>
        <button type="button" @click="goPrevVideo">이전</button>
        <button type="button" :disabled="isLoadingMore" @click="goNextVideo">
          {{ isLoadingMore ? '불러오는 중...' : '다음' }}
        </button>
        <p>{{ currentIndex + 1 }} / {{ videos.length }}</p>
      </div>
    </div>
    <div class="video-info">
      <div class="product-info" @click="goProductDetail(video.productId)">
        <p>제품명 : {{ video.productName }}</p>
        <p>가격 : {{ video.productPrice.toLocaleString() }}원</p>
      </div>
      <p v-if="isReviewLoading">후기 내용을 불러오는 중입니다.</p>
      <p v-else-if="reviewErrorMessage" class="error-message">{{ reviewErrorMessage }}</p>
      <div v-else-if="video.review" class="review-info">
        <p>평점 : {{ video.review.rating }} / 5</p>
        <p>작성자 : {{ video.review.userNickname }}</p>
        <p>후기내용 : {{ video.review.content }}</p>
      </div>
      <p v-else-if="video.isReviewLoaded">등록된 리뷰 내용이 없습니다.</p>
      <VideoComments :video-id="video.id" />
    </div>
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
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 28px;
  align-items: start;
}
.video-area {
  display: grid;
  grid-template-columns: minmax(280px, 420px) 96px;
  align-items: center;
  justify-content: center;
  gap: 18px;
  min-width: 0;
}
.video-frame {
  position: relative;
  width: min(100%, 420px);
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
  max-height: 78vh;
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
.like-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: 1px solid #fecdd3;
  border-radius: 999px;
  background-color: #fff;
  color: #be123c;
  padding: 9px 12px;
  font-weight: 700;
  cursor: pointer;
}
.like-action--active {
  background-color: #fff1f2;
}
.video-actions button:not(.like-action) {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: 14px;
  background-color: #fff;
  padding: 10px 12px;
  color: var(--color-text);
  font-weight: 700;
  cursor: pointer;
}
.video-actions p {
  margin: 6px 0 0;
  color: var(--color-text-secondary);
  font-weight: 700;
}
.video-info {
  min-width: 0;
  width: 100%;
  display: grid;
  gap: 16px;
}
.product-info {
  border: 1px solid var(--color-border);
  padding: 16px;
  border-radius: 20px;
  background: linear-gradient(180deg, #fff 0%, #f8fbff 100%);
  box-shadow: var(--shadow-md);
  cursor: pointer;
}
.product-info p {
  margin: 0;
}
.product-info p + p {
  margin-top: 6px;
}
.product-info:hover {
  border-color: var(--color-primary-200);
}
.review-info {
  border: 1px solid var(--color-border);
  padding: 16px;
  border-radius: 20px;
  background-color: #fff;
  box-shadow: var(--shadow-md);
}
.review-info p {
  margin: 0;
}
.review-info p + p {
  margin-top: 8px;
}
.video-actions button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
@media (max-width: 1080px) {
  .shorts-layout {
    grid-template-columns: 1fr;
  }
  .video-info {
    max-width: 420px;
  }
}
@media (max-width: 720px) {
  .video-area {
    grid-template-columns: 1fr;
  }
  .video-frame {
    border-radius: 22px;
  }
  .video-info {
    max-width: none;
  }
}
</style>
