<script setup>
import mockVideos from '@/data/mockVideos'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const currentIndex = ref(0)
const videos = ref(mockVideos.map((video) => ({ ...video })))
const video = computed(() => {
  if (videos.value.length === 0) {
    return null
  }
  return videos.value[currentIndex.value]
})

const toggleLiked = () => {
  if (video.value.isLiked === false) {
    videos.value[currentIndex.value].likeCount += 1
  } else {
    if (videos.value[currentIndex.value].likeCount > 0) {
      videos.value[currentIndex.value].likeCount -= 1
    }
  }
  videos.value[currentIndex.value].isLiked = !videos.value[currentIndex.value].isLiked
}
const goNextVideo = () => {
  currentIndex.value = (currentIndex.value + 1) % videos.value.length
}
const goPrevVideo = () => {
  currentIndex.value = (currentIndex.value - 1 + videos.value.length) % videos.value.length
}
const goProductDetail = (productId) => {
  router.push(`/products/${productId}`)
}
</script>

<template>
  <h1>쇼츠페이지</h1>
  <p v-if="!video">등록된 영상 후기가 없습니다.</p>
  <section class="shorts-layout" v-else>
    <div class="video-area">
      <div class="video-frame">
        <img :src="video.thumbnailUrl" :alt="video.productName" />
      </div>
      <div class="video-actions">
        <button type="button" @click="goPrevVideo">이전</button>
        <button type="button" @click="goNextVideo">다음</button>
        <p class="like-count">좋아요 : {{ video.likeCount }}개</p>
        <button type="button" @click="toggleLiked">{{ video.isLiked ? '♥' : '♡' }}</button>
        <p>{{ currentIndex + 1 }} / {{ videos.length }}</p>
      </div>
    </div>
    <div class="video-info">
      <div class="product-info" @click="goProductDetail(video.productId)">
        <p>제품명 : {{ video.productName }}</p>
        <p>제조사 : {{ video.productBrand }}</p>
        <p>카테고리 : {{ video.category }}</p>
      </div>
      <div class="review-info">
        <p>평점 : {{ video.rating }} / 5</p>
        <p>작성자 : {{ video.userNickname }}</p>
        <p>작성자 정보 : {{ video.userHousingType }} / {{ video.userAreaSize }}평</p>
        <p>후기내용 : {{ video.reviewContent }}</p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.shorts-layout {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.video-area {
  display: flex;
  flex-direction: row;
  align-items: center;
  flex: 0.8;
  justify-content: space-around;
  flex-shrink: 0;
}
.video-frame {
  width: 360px;
  aspect-ratio: 9 / 16;
  overflow: hidden;
  background-color: #eee;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 10px;
  max-height: 70vh;
}
.video-frame img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.video-actions {
  width: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.like-count {
  width: 90%;
  text-align: center;
  margin: 10px 0;
}
.video-info {
  margin-top: 20px;
  flex-shrink: 0;
  width: 300px;
}
.product-info {
  border: 1px solid #ccc;
  padding: 10px;
  border-radius: 10px;
  margin-bottom: 20px;
  cursor: pointer;
}
.product-info:hover {
  background-color: #f9f9f9;
}
.review-info {
  border: 1px solid #ccc;
  padding: 10px;
  border-radius: 10px;
}
</style>
