<template>
  <article class="video-card" @click="goShortsPage">
    <button class="like-button" type="button" @click.stop="toggleLiked">
      {{ isLiked ? '♥' : '♡' }}
    </button>
    <img :src="props.video.thumbnailUrl" :alt="props.video.productName" />
    <h2>{{ props.video.productName }}</h2>
    <p>{{ props.video.productBrand }}</p>
    <p>평점 {{ props.video.rating }} / 5</p>
    <p>{{ props.video.userNickname }}</p>
    <p>{{ props.video.reviewContent }}</p>
  </article>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  video: {
    type: Object,
    required: true,
  },
})

const router = useRouter()
const isLiked = ref(props.video.isLiked)

const toggleLiked = () => {
  isLiked.value = !isLiked.value
}

const goShortsPage = () => {
  router.push('/shorts')
}
</script>

<style scoped>
.video-card {
  position: relative;
  height: 100%;
  box-sizing: border-box;
  border: 1px solid #ccc;
  padding: 16px;
  cursor: pointer;
}

.video-card:hover {
  background-color: #f9f9f9;
}

.video-card img {
  width: 100%;
  height: auto;
  display: block;
}

.video-card h2 {
  margin: 8px 0;
}

.video-card p {
  margin: 4px 0;
}

.like-button {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background-color: white;
  cursor: pointer;
  font-size: 18px;
}

.like-button:hover {
  background-color: #f0f0f0;
}
</style>
