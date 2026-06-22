<template>
  <article class="liked-video-card">
    <button
      type="button"
      class="like-button"
      :class="{ 'like-button--active': video.isLiked }"
      :disabled="isLikePending"
      @click="$emit('toggle-like')"
    >
      {{ video.isLiked ? '♥' : '♡' }}
      <span>{{ video.likeCount }}</span>
    </button>
    <video
      :src="video.videoUrl"
      :poster="video.thumbnailUrl || video.productImage || ''"
      class="video-preview"
      controls
      playsinline
      preload="metadata"
    ></video>
    <button type="button" class="product-summary" @click="$emit('open-product')">
      <img v-if="video.productImage" :src="video.productImage" :alt="video.productName" />
      <span>
        <strong>{{ video.productName }}</strong>
        <small>{{ video.productPrice.toLocaleString() }}원</small>
      </span>
    </button>
  </article>
</template>

<script setup>
defineProps({
  video: {
    type: Object,
    required: true,
  },
  isLikePending: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['toggle-like', 'open-product'])
</script>

<style scoped>
.liked-video-card {
  position: relative;
  overflow: hidden;
  border: 1px solid #dbe4f0;
  border-radius: 16px;
  background-color: #fff;
  box-shadow: 0 10px 24px rgb(15 23 42 / 8%);
}

.like-button {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid #fecdd3;
  border-radius: 999px;
  background-color: rgb(255 255 255 / 92%);
  color: #be123c;
  padding: 7px 10px;
  font-weight: 700;
  cursor: pointer;
}

.like-button--active {
  background-color: #fff1f2;
}

.like-button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.video-preview {
  width: 100%;
  aspect-ratio: 9 / 16;
  display: block;
  background-color: #0f172a;
  object-fit: contain;
}

.product-summary {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  border: 0;
  border-top: 1px solid #e5e7eb;
  background-color: #f8fafc;
  padding: 12px;
  text-align: left;
  cursor: pointer;
}

.product-summary:hover {
  background-color: #eff6ff;
}

.product-summary img {
  width: 52px;
  height: 52px;
  flex-shrink: 0;
  border-radius: 10px;
  background-color: #fff;
  object-fit: contain;
}

.product-summary span {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.product-summary strong {
  display: -webkit-box;
  overflow: hidden;
  line-height: 1.35;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.product-summary small {
  color: #2563eb;
  font-weight: 700;
}
</style>
