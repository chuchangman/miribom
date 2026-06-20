<template>
  <section>
    <h1>좋아요페이지</h1>
    <h3>좋아요한 영상 후기만 볼 수 있습니다.</h3>
    <p v-if="isLoading">좋아요한 영상을 불러오는 중입니다.</p>
    <p v-else-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    <p v-else-if="likedVideos.length === 0">좋아요한 영상이 없습니다.</p>
    <template v-else>
      <div class="liked-video-grid">
        <LikedVideoCard
          v-for="video in likedVideos"
          :key="video.id"
          :video="video"
          :is-like-pending="pendingVideoId === video.id"
          @toggle-like="handleToggleLike(video)"
          @open-product="goProductDetail(video.productId)"
        />
      </div>
      <button
        v-if="hasMoreVideos"
        type="button"
        class="load-more-button"
        :disabled="isLoadingMore"
        @click="loadMoreLikedVideos"
      >
        {{ isLoadingMore ? '불러오는 중...' : '더보기' }}
      </button>
    </template>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import LikedVideoCard from '@/components/LikedVideoCard.vue'
import { fetchLikedVideos, mapVideoFeedItem, toggleVideoLike } from '@/services/videoApi.js'

const router = useRouter()
const likedVideos = ref([])
const isLoading = ref(false)
const isLoadingMore = ref(false)
const hasMoreVideos = ref(true)
const errorMessage = ref('')
const pendingVideoId = ref(null)

const mapLikedVideo = (videoItem) => ({
  ...mapVideoFeedItem(videoItem),
  isLiked: true,
})

const loadLikedVideos = async ({ cursor = null, append = false } = {}) => {
  if (append) {
    isLoadingMore.value = true
  } else {
    isLoading.value = true
  }
  errorMessage.value = ''

  try {
    const videos = await fetchLikedVideos({ cursor })
    const mappedVideos = videos.map(mapLikedVideo)
    likedVideos.value = append ? [...likedVideos.value, ...mappedVideos] : mappedVideos
    hasMoreVideos.value = videos.length === 20
  } catch (error) {
    errorMessage.value = error.message || '좋아요한 영상을 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
    isLoadingMore.value = false
  }
}

const loadMoreLikedVideos = async () => {
  if (!hasMoreVideos.value || isLoadingMore.value) {
    return
  }

  await loadLikedVideos({
    cursor: likedVideos.value.at(-1)?.id,
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

const goProductDetail = (productId) => {
  router.push(`/products/${productId}`)
}

onMounted(loadLikedVideos)
</script>

<style scoped>
.error-message {
  color: red;
}

.liked-video-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
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
