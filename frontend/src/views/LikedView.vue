<template>
  <h1>좋아요페이지</h1>
  <h3>좋아요한 영상 후기만 볼 수 있습니다.</h3>
  <p v-if="likedVideos.length === 0">아직 좋아요한 영상이 없습니다.</p>
  <ul v-else class="video-grid">
    <li v-for="likedVideo in likedVideos" :key="likedVideo.id">
      <VideoCard :video="likedVideo" />
    </li>
  </ul>
</template>

<script setup>
import mockVideos from '@/data/mockVideos'
import { ref } from 'vue'
import VideoCard from '@/components/VideoCard.vue'

const likedVideos = ref(mockVideos.filter((video) => video.isLiked))
</script>

<style scoped>
.video-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  list-style: none;
  padding: 0;
}

.video-grid li {
  min-width: 0;
}
</style>
