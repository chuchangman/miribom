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
        <div class="review-thumbnail">
          <label for="review-thumbnail">AI 카테고리 예측용 썸네일</label>
          <input
            type="file"
            accept="image/jpeg,image/png"
            name="review-thumbnail"
            id="review-thumbnail"
            @change="predictCategoryFromThumbnail"
          />
          <p v-if="isPredictingCategory">AI가 카테고리를 예측하는 중입니다.</p>
          <p v-if="categoryPredictionMessage" class="prediction-message">
            {{ categoryPredictionMessage }}
          </p>
          <p v-if="categoryPredictionErrorMessage" class="error-message">
            {{ categoryPredictionErrorMessage }}
          </p>
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
            @keydown.down.prevent="moveProductHighlight(1)"
            @keydown.up.prevent="moveProductHighlight(-1)"
            @keydown.enter.prevent="selectHighlightedProduct"
            @keydown.esc="closeProductSuggestions"
            autocomplete="off"
          />
          <p v-if="productErrorMessage" class="error-message">{{ productErrorMessage }}</p>
          <p v-else-if="!selectedProduct">선택된 제품이 없습니다.</p>
          <p v-else>선택된 제품: {{ selectedProduct.title }}</p>
          <p v-if="isSearchingProducts">제품을 검색하는 중입니다.</p>
          <ul v-else-if="productSuggestions.length > 0" class="product-suggestions">
            <li
              v-for="(product, index) in productSuggestions"
              :key="product.id"
              :ref="(element) => setProductSuggestionRef(element, index)"
              :class="{ 'product-suggestion--active': highlightedProductIndex === index }"
              @mouseenter="highlightedProductIndex = index"
              @pointerdown.prevent="handleSelect(product)"
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
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import { useUnsavedChanges } from '@/composables/useUnsavedChanges'
import { predictCategoryFromImage } from '@/services/aiApi.js'
import { createReviewFlow, fetchCategories, searchProducts } from '@/services/reviewApi.js'

const categories = ref([])
const selectedCategory = ref('')
const productSearchQuery = ref('')
const selectedProduct = ref(null)
const productSuggestions = ref([])
const productSuggestionRefs = ref([])
const highlightedProductIndex = ref(-1)
const inputVideo = ref(null)
const reviewRating = ref(null)
const reviewContent = ref('')

const isLoadingCategories = ref(false)
const isSearchingProducts = ref(false)
const isPredictingCategory = ref(false)
const isSubmitting = ref(false)
const isSubmitted = ref(false)
const { setHasUnsavedChanges } = useUnsavedChanges()

const videoErrorMessage = ref('')
const categoryErrorMessage = ref('')
const productErrorMessage = ref('')
const categoryPredictionMessage = ref('')
const categoryPredictionErrorMessage = ref('')
const ratingErrorMessage = ref('')
const contentErrorMessage = ref('')
const submitErrorMessage = ref('')

let productSearchTimer = null
let productSearchRequestId = 0

const hasUnsavedChanges = computed(
  () =>
    !isSubmitted.value &&
    Boolean(
      inputVideo.value ||
        selectedCategory.value ||
        productSearchQuery.value.trim() ||
        selectedProduct.value ||
        reviewRating.value !== null ||
        reviewContent.value.trim(),
    ),
)

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
    isSubmitted.value = true
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

const predictCategoryFromThumbnail = async (event) => {
  const thumbnail = event.target.files[0]
  categoryPredictionMessage.value = ''
  categoryPredictionErrorMessage.value = ''
  categoryErrorMessage.value = ''

  if (!thumbnail) {
    return
  }

  if (categories.value.length === 0) {
    categoryPredictionErrorMessage.value =
      '카테고리 목록을 불러온 뒤 다시 시도하거나 직접 선택해주세요.'
    return
  }

  isPredictingCategory.value = true

  try {
    const prediction = await predictCategoryFromImage(thumbnail)
    const predictedCategory = categories.value.find(
      (category) => category.ai_label === prediction.service_label,
    )

    if (!predictedCategory) {
      categoryPredictionErrorMessage.value =
        'AI 예측 결과와 일치하는 카테고리를 찾지 못했습니다. 카테고리를 직접 선택해주세요.'
      return
    }

    selectedCategory.value = predictedCategory.id
    categoryErrorMessage.value = ''
    categoryPredictionMessage.value = `AI가 ${predictedCategory.name} 카테고리를 예측했습니다. 필요하면 직접 변경할 수 있습니다.`
  } catch (error) {
    categoryPredictionErrorMessage.value =
      error.message || 'AI 카테고리 예측에 실패했습니다. 카테고리를 직접 선택해주세요.'
  } finally {
    isPredictingCategory.value = false
  }
}

const handleProductSearchInput = () => {
  if (selectedProduct.value) {
    selectedProduct.value = null
  }

  ++productSearchRequestId
  productErrorMessage.value = ''
  clearTimeout(productSearchTimer)

  if (!productSearchQuery.value.trim()) {
    productSuggestions.value = []
    highlightedProductIndex.value = -1
    return
  }

  productSearchTimer = setTimeout(() => {
    loadProductSuggestions()
  }, 300)
}

const loadProductSuggestions = async () => {
  const requestId = ++productSearchRequestId
  const searchQuery = productSearchQuery.value
  isSearchingProducts.value = true

  try {
    const products = await searchProducts({
      query: searchQuery,
      categoryId: selectedCategory.value,
    })

    if (requestId === productSearchRequestId) {
      productSuggestions.value = products
      highlightedProductIndex.value = products.length > 0 ? 0 : -1
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
  clearTimeout(productSearchTimer)
  ++productSearchRequestId
  isSearchingProducts.value = false
  selectedProduct.value = product
  productSearchQuery.value = product.title
  productSuggestions.value = []
  highlightedProductIndex.value = -1
}

const setProductSuggestionRef = (element, index) => {
  if (element) {
    productSuggestionRefs.value[index] = element
  }
}

const moveProductHighlight = (direction) => {
  if (productSuggestions.value.length === 0) {
    return
  }

  const lastIndex = productSuggestions.value.length - 1
  const nextIndex = highlightedProductIndex.value + direction

  if (nextIndex < 0) {
    highlightedProductIndex.value = lastIndex
  } else if (nextIndex > lastIndex) {
    highlightedProductIndex.value = 0
  } else {
    highlightedProductIndex.value = nextIndex
  }

  productSuggestionRefs.value[highlightedProductIndex.value]?.scrollIntoView({
    block: 'nearest',
  })
}

const selectHighlightedProduct = () => {
  const product = productSuggestions.value[highlightedProductIndex.value]

  if (product) {
    handleSelect(product)
  }
}

const closeProductSuggestions = () => {
  productSuggestions.value = []
  highlightedProductIndex.value = -1
}

const handleCategoryChange = () => {
  selectedProduct.value = null
  productSearchQuery.value = ''
  productSuggestions.value = []
  highlightedProductIndex.value = -1
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

watch(
  [
    inputVideo,
    selectedCategory,
    productSearchQuery,
    selectedProduct,
    reviewRating,
    reviewContent,
  ],
  () => {
    if (isSubmitted.value) {
      isSubmitted.value = false
    }
  },
)

watch(
  hasUnsavedChanges,
  (value) => {
    setHasUnsavedChanges(value)
  },
  { immediate: true },
)

onBeforeRouteLeave(() => {
  if (!hasUnsavedChanges.value) {
    return true
  }

  return window.confirm(
    '지금 이동하면 작성한 정보가 초기화됩니다. 정말 이동하시겠습니까?',
  )
})

onBeforeUnmount(() => {
  setHasUnsavedChanges(false)
})

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
  max-height: 210px;
  overflow-y: auto;
}
.product-suggestions li {
  min-height: 42px;
  padding: 10px 8px;
  cursor: pointer;
}
.product-suggestions li:hover,
.product-suggestion--active {
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
