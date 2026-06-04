<template>
  <div>
    <h1>제품 후기 등록</h1>
    <section class="review-area">
      <form @submit.prevent="submitReview">
        <div class="review-video">
          <label for="review-video">영상 선택</label>
          <input
            type="file"
            accept="video/*"
            name="review-video"
            id="review-video"
            @change="uploadVideo"
          />
          <p v-if="videoErrorMessage" class="error-message">{{ videoErrorMessage }}</p>
        </div>
        <div class="review-category">
          <select v-model="selectedCategory" class="category-select">
            <option value="">선택</option>
            <option value="세탁·건조">세탁·건조</option>
            <option value="냉장고">냉장고</option>
            <option value="주방소가전">주방소가전</option>
            <option value="청소기">청소기</option>
            <option value="계절가전">계절가전</option>
            <option value="제습기·가습기">제습기·가습기</option>
            <option value="PC주변기기">PC주변기기</option>
            <option value="빔프로젝터">빔프로젝터</option>
          </select>
          <p v-if="categoryErrorMessage" class="error-message">{{ categoryErrorMessage }}</p>
        </div>
        <div class="review-product">
          <label for="review-product">제품 선택</label>
          <input type="text" name="review-product" id="review-product" v-model="productSearchQuery">
          <p v-if="productErrorMessage" class="error-message">{{ productErrorMessage }}</p>
          <p v-else-if="!selectedProduct">선택된 제품이 없습니다.</p>
          <p v-else>선택된 제품: {{ selectedProduct.name }}</p>
          <ul v-if="filteredProduct.length > 0" class="product-suggestions">
            <li v-for="product in filteredProduct" :key="product.id" @click="handleSelect(product)">
              {{ product.name }}
            </li>
          </ul>
        </div>
        <div class="review-rating">
          <label for="review-rating">별점</label>
          <input type="number" name="review-rating" id="review-rating" :min="1" :max="5" v-model.number="reviewRating">
          <p v-if="ratingErrorMessage" class="error-message">{{ ratingErrorMessage }}</p>
        </div>
        <div class="review-content">
          <label for="review-content">후기 내용</label>
          <textarea name="review-content" id="review-content" v-model="reviewContent"></textarea>
          <p v-if="contentErrorMessage" class="error-message">{{ contentErrorMessage }}</p>
        </div>
        <button type="submit">등록</button>
      </form>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import mockProducts from '@/data/mockProducts.js';
const selectedCategory = ref('')
const productSearchQuery = ref('')
const selectedProduct = ref(null)
const inputVideo = ref(null)
const reviewRating = ref(null)

const reviewContent = ref('')
const videoErrorMessage = ref('')
const categoryErrorMessage = ref('')
const productErrorMessage = ref('')
const ratingErrorMessage = ref('')
const contentErrorMessage = ref('')

const validateVideo = () => {
  if (!inputVideo.value) {
    videoErrorMessage.value = '영상을 선택해주세요.'
    return false
  }

  videoErrorMessage.value = ''
  return true
}

const validateCategory = () => {
  if (!selectedCategory.value) {
    categoryErrorMessage.value = '카테고리를 선택해주세요.'
    return false
  }

  categoryErrorMessage.value = ''
  return true
}

const validateProduct = () => {
  if (!selectedProduct.value) {
    productErrorMessage.value = '제품을 선택해주세요.'
    return false
  }

  productErrorMessage.value = ''
  return true
}

const validateRating = () => {
  if (
    reviewRating.value === null ||
    reviewRating.value < 1 ||
    reviewRating.value > 5
  ) {
    ratingErrorMessage.value = '별점은 1점에서 5점 사이로 선택해주세요.'
    return false
  }

  ratingErrorMessage.value = ''
  return true
}

const validateContent = () => {
  if (!reviewContent.value.trim()) {
    contentErrorMessage.value = '후기 내용을 입력해주세요.'
    return false
  }

  contentErrorMessage.value = ''
  return true
}

const submitReview = () => {
  const validVideo = validateVideo()
  const validCategory = validateCategory()
  const validProduct = validateProduct()
  const validRating = validateRating()
  const validContent = validateContent()

  if (
    !validVideo ||
    !validCategory ||
    !validProduct ||
    !validRating ||
    !validContent
  ) {
    return
  }

  console.log('영상:', inputVideo.value.name)
  console.log('카테고리:', selectedCategory.value)
  console.log('제품:', selectedProduct.value.name)
  console.log('별점:', reviewRating.value)
  console.log('후기 내용:', reviewContent.value)

  alert('후기 등록 입력값 확인 완료')
}

const uploadVideo = (event) => {
  const video = event.target.files[0]
  if (!video) {
    videoErrorMessage.value = '영상을 선택해주세요.'
    return
  }
  inputVideo.value = video
}

const filteredProduct = computed(() => {
  if (!productSearchQuery.value) {
    return []
  }
  return mockProducts.filter(product =>
    product.name.includes(productSearchQuery.value)
  )
})
const handleSelect = (product) => {
  selectedProduct.value = product
  productSearchQuery.value = ''
}
</script>

<style scoped>
.error-message {
  color: red;
  font-size: 0.9em;
  margin-top: 5px;
}
.category-select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.product-suggestions {
  list-style: none;
  padding: 0;
  margin: 8px 0 0;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.product-suggestions li {
  padding: 8px;
  cursor: pointer;
}
.product-suggestions li:hover {
  background-color: #f0f0f0;
}
.review-area {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background-color: #fff;
}
.review-area label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #059669;
}
.review-area input[type='text'],
.review-area input[type='number'],
.review-area textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  margin-bottom: 16px;
}
.review-area textarea {
  resize: vertical;
  min-height: 100px;
}
.review-area button {  
  width: 100%;
  padding: 14px 16px;
  border: none;
  border-radius: 10px;
  background-color: #10b981;
  color: white;
  font-weight: 700;
  cursor: pointer;
}
.review-area button:hover {
  background-color: #059669;
}
</style>