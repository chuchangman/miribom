<template>
  <div>
    <h1>제품 후기 등록</h1>
    <section class="review-area">
      <form @submit.prevent="submitReview">
        <div class="review-video">
          <label for="review-video">영상 선택</label>
          <input
            type="file"
            accept="video/mp4,video/quicktime,video/webm"
            name="review-video"
            id="review-video"
            @change="uploadVideo"
          />
          <p v-if="videoErrorMessage" class="error-message">{{ videoErrorMessage }}</p>
        </div>
        <div class="review-category">
          <select v-model="selectedCategory" class="category-select" @change="handleCategoryChange">
            <option value="">선택</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>
          <p v-if="isLoadingCategories">카테고리를 불러오는 중입니다.</p>
          <p v-if="categoryErrorMessage" class="error-message">{{ categoryErrorMessage }}</p>
        </div>
        <div class="review-product">
          <label for="review-product">제품 선택</label>
          <input
            type="text"
            name="review-product"
            id="review-product"
            v-model="productSearchQuery"
            @input="handleProductSearchInput"
            autocomplete="off"
          />
          <p v-if="productErrorMessage" class="error-message">{{ productErrorMessage }}</p>
          <p v-else-if="!selectedProduct">선택된 제품이 없습니다.</p>
          <p v-else>선택된 제품: {{ selectedProduct.title }}</p>
          <p v-if="isSearchingProducts">제품을 검색하는 중입니다.</p>
          <ul v-else-if="productSuggestions.length > 0" class="product-suggestions">
            <li
              v-for="product in productSuggestions"
              :key="product.id"
              @click="handleSelect(product)"
            >
              {{ product.title }}<span v-if="product.brand"> · {{ product.brand }}</span>
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
          <textarea
            name="review-content"
            id="review-content"
            v-model="reviewContent"
            maxlength="1000"
          ></textarea>
          <p v-if="contentErrorMessage" class="error-message">{{ contentErrorMessage }}</p>
        </div>
        <p v-if="submitErrorMessage" class="error-message">{{ submitErrorMessage }}</p>
        <button type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? '등록 중...' : '등록' }}
        </button>
      </form>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { createReviewFlow, fetchCategories, searchProducts } from '@/services/reviewApi.js'

const categories = ref([])
const selectedCategory = ref('')
const productSearchQuery = ref('')
const selectedProduct = ref(null)
const productSuggestions = ref([])
const inputVideo = ref(null)
const reviewRating = ref(null)
const reviewContent = ref('')

const isLoadingCategories = ref(false)
const isSearchingProducts = ref(false)
const isSubmitting = ref(false)

const videoErrorMessage = ref('')
const categoryErrorMessage = ref('')
const productErrorMessage = ref('')
const ratingErrorMessage = ref('')
const contentErrorMessage = ref('')
const submitErrorMessage = ref('')

let productSearchTimer = null
let productSearchRequestId = 0

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

const submitReview = async () => {
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

  submitErrorMessage.value = ''
  isSubmitting.value = true

  try {
    await createReviewFlow({
      file: inputVideo.value,
      productId: selectedProduct.value.id,
      rating: reviewRating.value,
      content: reviewContent.value.trim(),
    })
    alert('후기가 등록되었습니다.')
  } catch (error) {
    submitErrorMessage.value = error.message || '후기 등록에 실패했습니다.'
  } finally {
    isSubmitting.value = false
  }
}

const uploadVideo = (event) => {
  const video = event.target.files[0]
  if (!video) {
    inputVideo.value = null
    videoErrorMessage.value = '영상을 선택해주세요.'
    return
  }

  inputVideo.value = video
  videoErrorMessage.value = ''
}

const handleProductSearchInput = () => {
  if (selectedProduct.value) {
    selectedProduct.value = null
  }

  productErrorMessage.value = ''
  productSuggestions.value = []
  clearTimeout(productSearchTimer)

  if (!productSearchQuery.value.trim()) {
    return
  }

  productSearchTimer = setTimeout(() => {
    loadProductSuggestions()
  }, 300)
}

const loadProductSuggestions = async () => {
  const requestId = ++productSearchRequestId
  isSearchingProducts.value = true

  try {
    const products = await searchProducts({
      query: productSearchQuery.value,
      categoryId: selectedCategory.value,
    })

    if (requestId === productSearchRequestId) {
      productSuggestions.value = products
    }
  } catch (error) {
    if (requestId === productSearchRequestId) {
      productErrorMessage.value = error.message || '제품 검색에 실패했습니다.'
    }
  } finally {
    if (requestId === productSearchRequestId) {
      isSearchingProducts.value = false
    }
  }
}

const handleSelect = (product) => {
  selectedProduct.value = product
  productSearchQuery.value = product.title
  productSuggestions.value = []
}

const handleCategoryChange = () => {
  selectedProduct.value = null
  productSearchQuery.value = ''
  productSuggestions.value = []
  categoryErrorMessage.value = ''
}

const loadCategories = async () => {
  isLoadingCategories.value = true

  try {
    categories.value = await fetchCategories()
  } catch (error) {
    categoryErrorMessage.value = error.message || '카테고리를 불러오지 못했습니다.'
  } finally {
    isLoadingCategories.value = false
  }
}

onMounted(loadCategories)
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
.review-area button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
