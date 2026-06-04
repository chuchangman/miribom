<template>
  <h1>좋아요페이지</h1>
  <h3>좋아요한 영상 후기만 볼 수 있습니다.</h3>
  <p v-if="likedVideos.length === 0">아직 좋아요한 영상이 없습니다.</p>
  <ul v-else>
    <li v-for="likedVideo in likedVideos" :key="likedVideo.id">
      <div @click="goShortsPage">
        <img :src="likedVideo.thumbnailUrl" :alt="likedVideo.productName" />
        <p>{{ likedVideo.productName }}</p>
        <p>{{ likedVideo.productBrand }}</p>
        <p>{{ likedVideo.rating }}</p>
        <p>{{ likedVideo.userNickname }}</p>
        <p>{{ likedVideo.reviewContent }}</p>
      </div>
    </li>
  </ul>
</template>

<script setup>
import mockVideos from '@/data/mockVideos'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const likedVideos = ref(mockVideos.filter((video) => video.isLiked))

const goShortsPage = () => {
  router.push('/shorts/')
}
</script>

<style scoped>

</style>
