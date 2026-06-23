<template>
  <section class="review-page">
    <div class="review-shell">
      <section class="review-area">
        <form class="review-form" @submit.prevent="submitReview">
          <div class="form-grid">
            <section class="review-card review-card--media">
              <div class="section-heading">
                <h2>영상 업로드</h2>
                <p>세로형, 가로형 모두 가능해요. 영상이 멈춰 있을 때는 제품 이미지가 썸네일로 보입니다.</p>
              </div>

              <div class="upload-field" @dragover.prevent @drop.prevent="handleVideoDrop">
                <div class="upload-field__header">
                  <span class="upload-field__title">영상 선택</span>
                  <button type="button" class="upload-field__button" @click="openVideoPicker">
                    파일 고르기
                  </button>
                </div>

                <input
                  ref="videoInputRef"
                  id="review-video"
                  type="file"
                  accept="video/mp4,video/quicktime,video/webm"
                  name="review-video"
                  @change="uploadVideo"
                />

                <div v-if="!videoPreviewUrl" class="upload-field__dropzone upload-field__body">
                  <strong>영상을 여기로 드래그해 올려주세요</strong>
                  <span>(MP4, MOV, WEBM)</span>
                </div>

                <div
                  v-else
                  class="video-preview upload-field__body"
                  :style="{ aspectRatio: videoPreviewAspectRatio }"
                >
                  <video :src="videoPreviewUrl" controls playsinline preload="metadata"></video>
                </div>
              </div>

              <p v-if="videoErrorMessage" class="error-message">{{ videoErrorMessage }}</p>
            </section>

            <section class="review-card review-card--thumbnail">
              <div class="section-heading">
                <h2>썸네일 업로드</h2>
                <p>AI 카테고리 예측에 사용할 이미지를 선택해주세요.</p>
              </div>

              <div class="thumbnail-block">
                <div
                  class="upload-field upload-field--secondary"
                  @dragover.prevent
                  @drop.prevent="handleThumbnailDrop"
                >
                  <div class="upload-field__header">
                    <span class="upload-field__title">AI 카테고리 예측용 이미지</span>
                    <button
                      type="button"
                      class="upload-field__button upload-field__button--secondary"
                      @click="openThumbnailPicker"
                    >
                      이미지 고르기
                    </button>
                  </div>

                  <input
                    ref="thumbnailInputRef"
                    id="review-thumbnail"
                    type="file"
                    accept="image/jpeg,image/png"
                    name="review-thumbnail"
                    @change="predictCategoryFromThumbnail"
                  />

                  <div
                    v-if="!thumbnailPreviewUrl"
                    class="upload-field__dropzone upload-field__dropzone--secondary upload-field__body"
                  >
                    <strong>이미지를 여기로 드래그해 올려주세요</strong>
                    <span>(JPEG, PNG)</span>
                  </div>

                  <div
                    v-else
                    class="thumbnail-preview upload-field__body"
                    :style="{ aspectRatio: thumbnailPreviewAspectRatio }"
                  >
                    <img :src="thumbnailPreviewUrl" alt="썸네일 미리보기" />
                  </div>
                </div>
              </div>

              <p v-if="isPredictingCategory" class="status-message">
                AI가 카테고리를 예측하는 중입니다.
              </p>
              <p v-if="categoryPredictionMessage" class="prediction-message">
                {{ categoryPredictionMessage }}
              </p>
              <p v-if="categoryPredictionErrorMessage" class="error-message">
                {{ categoryPredictionErrorMessage }}
              </p>
            </section>

            <section class="review-card review-card--form">
              <div class="section-heading">
                <h2>후기 정보</h2>
                <p>카테고리, 제품, 평점, 후기를 입력하면 등록이 완료됩니다.</p>
              </div>

              <div class="field-group">
                <label for="review-category">카테고리</label>
                <select
                  id="review-category"
                  v-model="selectedCategory"
                  class="category-select"
                  @change="handleCategoryChange"
                >
                  <option value="">선택</option>
                  <option v-for="category in categories" :key="category.id" :value="category.id">
                    {{ category.name }}
                  </option>
                </select>
                <p v-if="isLoadingCategories" class="status-message">카테고리를 불러오는 중입니다.</p>
                <p v-if="categoryErrorMessage" class="error-message">{{ categoryErrorMessage }}</p>
              </div>

              <div class="field-group">
                <label for="review-product">제품 선택</label>
                <input
                  id="review-product"
                  type="text"
                  name="review-product"
                  v-model="productSearchQuery"
                  placeholder="제품명이나 브랜드를 검색하세요"
                  @input="handleProductSearchInput"
                  @keydown.down.prevent="moveProductHighlight(1)"
                  @keydown.up.prevent="moveProductHighlight(-1)"
                  @keydown.enter.prevent="selectHighlightedProduct"
                  @keydown.esc="closeProductSuggestions"
                  autocomplete="off"
                />
                <p v-if="productErrorMessage" class="error-message">{{ productErrorMessage }}</p>
                <p v-else-if="!selectedProduct" class="help-text">선택된 제품이 없습니다.</p>
                <p v-else class="selected-product">
                  <strong>{{ selectedProduct.title }}</strong>
                  <span v-if="selectedProduct.brand">{{ selectedProduct.brand }}</span>
                </p>
                <p v-if="isSearchingProducts" class="status-message">제품을 검색하는 중입니다.</p>
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

              <div class="field-group">
                <label for="review-rating">평점</label>
                <div class="rating-picker">
                  <div
                    class="star-rating"
                    role="slider"
                    aria-label="평점 선택"
                    aria-valuemin="0"
                    aria-valuemax="5"
                    :aria-valuenow="reviewRating || 0"
                  >
                    <div class="star-rating__base" aria-hidden="true">{{ starRow }}</div>
                    <div class="star-rating__fill" :style="{ width: starFillWidth }" aria-hidden="true">
                      {{ starRow }}
                    </div>
                    <input
                      id="review-rating"
                      class="star-rating__range"
                      type="range"
                      min="0"
                      max="5"
                      step="1"
                      :value="reviewRating ?? 0"
                      @input="handleRatingInput"
                    />
                  </div>
                  <div class="rating-summary">
                    <strong>{{ ratingDisplayText }}</strong>
                    <span>별을 드래그해서 평점을 조절할 수 있어요.</span>
                  </div>
                </div>
                <p v-if="ratingErrorMessage" class="error-message">{{ ratingErrorMessage }}</p>
              </div>

              <div class="field-group">
                <label for="review-content">후기 내용</label>
                <textarea
                  id="review-content"
                  name="review-content"
                  v-model="reviewContent"
                  maxlength="1000"
                  placeholder="소음, 크기, 공간감, 만족도처럼 실제 사용감을 중심으로 적어보세요."
                ></textarea>
                <div class="content-meta">
                  <span>솔직한 사용 경험일수록 좋아요.</span>
                  <strong>{{ reviewContent.length }}/1000</strong>
                </div>
                <p v-if="contentErrorMessage" class="error-message">{{ contentErrorMessage }}</p>
              </div>

              <p v-if="submitErrorMessage" class="error-message">{{ submitErrorMessage }}</p>

              <button class="submit-button" type="submit" :disabled="isSubmitting">
                {{ isSubmitting ? '등록 중...' : '후기 등록하기' }}
              </button>
            </section>
          </div>
        </form>
      </section>
    </div>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { onBeforeRouteLeave, useRouter } from 'vue-router'
import { useUnsavedChanges } from '@/composables/useUnsavedChanges'
import { predictCategoryFromImage } from '@/services/aiApi.js'
import { createReviewFlow, fetchCategories, searchProducts } from '@/services/reviewApi.js'

const router = useRouter()
const { setHasUnsavedChanges } = useUnsavedChanges()

const categories = ref([])
const selectedCategory = ref('')
const productSearchQuery = ref('')
const selectedProduct = ref(null)
const productSuggestions = ref([])
const productSuggestionRefs = ref([])
const highlightedProductIndex = ref(-1)

const videoInputRef = ref(null)
const thumbnailInputRef = ref(null)
const inputVideo = ref(null)
const thumbnailFile = ref(null)
const videoPreviewUrl = ref('')
const thumbnailPreviewUrl = ref('')
const videoPreviewAspectRatio = ref('16 / 9')
const thumbnailPreviewAspectRatio = ref('4 / 3')
const reviewRating = ref(null)
const reviewContent = ref('')

const isLoadingCategories = ref(false)
const isSearchingProducts = ref(false)
const isPredictingCategory = ref(false)
const isSubmitting = ref(false)
const isSubmitted = ref(false)

const videoErrorMessage = ref('')
const categoryErrorMessage = ref('')
const productErrorMessage = ref('')
const categoryPredictionMessage = ref('')
const categoryPredictionErrorMessage = ref('')
const ratingErrorMessage = ref('')
const contentErrorMessage = ref('')
const submitErrorMessage = ref('')

const starRow = '★★★★★'
let productSearchTimer = null
let productSearchRequestId = 0

const selectedVideoName = computed(() => inputVideo.value?.name || '')
const selectedThumbnailName = computed(() => thumbnailFile.value?.name || '')
const ratingDisplayText = computed(() =>
  reviewRating.value === null ? '평점을 선택해주세요' : `${reviewRating.value.toFixed(1)}점`,
)
const starFillWidth = computed(() => `${((reviewRating.value || 0) / 5) * 100}%`)
const hasUnsavedChanges = computed(
  () =>
    !isSubmitted.value &&
    Boolean(
      inputVideo.value ||
        thumbnailFile.value ||
        selectedCategory.value ||
        productSearchQuery.value.trim() ||
        selectedProduct.value ||
        reviewRating.value !== null ||
        reviewContent.value.trim(),
    ),
)

const revokePreviewUrl = (previewRef) => {
  if (previewRef.value) {
    URL.revokeObjectURL(previewRef.value)
    previewRef.value = ''
  }
}

const readVideoAspectRatio = (fileUrl) =>
  new Promise((resolve) => {
    const probeVideo = document.createElement('video')
    probeVideo.preload = 'metadata'
    probeVideo.onloadedmetadata = () => {
      const width = probeVideo.videoWidth || 16
      const height = probeVideo.videoHeight || 9
      resolve(`${width} / ${height}`)
    }
    probeVideo.onerror = () => resolve('16 / 9')
    probeVideo.src = fileUrl
  })

const readImageAspectRatio = (fileUrl) =>
  new Promise((resolve) => {
    const image = new Image()
    image.onload = () => {
      const width = image.naturalWidth || 4
      const height = image.naturalHeight || 3
      resolve(`${width} / ${height}`)
    }
    image.onerror = () => resolve('4 / 3')
    image.src = fileUrl
  })

const getFirstFile = (source) => {
  if (!source) {
    return null
  }

  if (source instanceof File) {
    return source
  }

  return source.target?.files?.[0] || source.dataTransfer?.files?.[0] || null
}

const isAllowedVideoFile = (file) =>
  ['video/mp4', 'video/quicktime', 'video/webm'].includes(file.type)

const isAllowedThumbnailFile = (file) => ['image/jpeg', 'image/png'].includes(file.type)

const openVideoPicker = () => {
  videoInputRef.value?.click()
}

const openThumbnailPicker = () => {
  thumbnailInputRef.value?.click()
}

const handleVideoDrop = (event) => {
  const file = getFirstFile(event)
  if (file) {
    uploadVideo(file)
  }
}

const handleThumbnailDrop = (event) => {
  const file = getFirstFile(event)
  if (file) {
    predictCategoryFromThumbnail(file)
  }
}

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
  if (reviewRating.value === null || reviewRating.value < 1 || reviewRating.value > 5) {
    ratingErrorMessage.value = '평점은 1점에서 5점 사이로 선택해주세요.'
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

const handleRatingInput = (event) => {
  reviewRating.value = Number(event.target.value)
  ratingErrorMessage.value = ''
}

const submitReview = async () => {
  const validVideo = validateVideo()
  const validCategory = validateCategory()
  const validProduct = validateProduct()
  const validRating = validateRating()
  const validContent = validateContent()

  if (!validVideo || !validCategory || !validProduct || !validRating || !validContent) {
    return
  }

  submitErrorMessage.value = ''
  isSubmitting.value = true

  try {
    await createReviewFlow({
      file: inputVideo.value,
      thumbnailFile: thumbnailFile.value || null,
      productId: selectedProduct.value.id,
      rating: reviewRating.value,
      content: reviewContent.value.trim(),
    })
    isSubmitted.value = true
    router.push({ name: 'ProductDetail', params: { id: selectedProduct.value.id } })
  } catch (error) {
    submitErrorMessage.value = error.message || '후기 등록에 실패했습니다.'
  } finally {
    isSubmitting.value = false
  }
}

const uploadVideo = (source) => {
  const video = getFirstFile(source)
  revokePreviewUrl(videoPreviewUrl)

  if (!video) {
    inputVideo.value = null
    videoErrorMessage.value = '영상을 선택해주세요.'
    return
  }

  if (!isAllowedVideoFile(video)) {
    inputVideo.value = null
    videoErrorMessage.value = 'MP4, MOV, WEBM 형식의 영상만 등록할 수 있어요.'
    return
  }

  inputVideo.value = video
  videoPreviewUrl.value = URL.createObjectURL(video)
  readVideoAspectRatio(videoPreviewUrl.value).then((ratio) => {
    videoPreviewAspectRatio.value = ratio
  })
  videoErrorMessage.value = ''
}

const predictCategoryFromThumbnail = async (source) => {
  const thumbnail = getFirstFile(source)
  categoryPredictionMessage.value = ''
  categoryPredictionErrorMessage.value = ''
  categoryErrorMessage.value = ''
  revokePreviewUrl(thumbnailPreviewUrl)

  if (!thumbnail) {
    thumbnailFile.value = null
    return
  }

  if (!isAllowedThumbnailFile(thumbnail)) {
    thumbnailFile.value = null
    categoryPredictionErrorMessage.value = 'JPEG, PNG 형식의 이미지만 등록할 수 있어요.'
    return
  }

  thumbnailFile.value = thumbnail
  thumbnailPreviewUrl.value = URL.createObjectURL(thumbnail)
  readImageAspectRatio(thumbnailPreviewUrl.value).then((ratio) => {
    thumbnailPreviewAspectRatio.value = ratio
  })

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
    thumbnailFile,
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

  return window.confirm('지금 이동하면 작성한 정보가 초기화됩니다. 정말 이동하시겠습니까?')
})

onBeforeUnmount(() => {
  clearTimeout(productSearchTimer)
  revokePreviewUrl(videoPreviewUrl)
  revokePreviewUrl(thumbnailPreviewUrl)
  setHasUnsavedChanges(false)
})

onMounted(loadCategories)
</script>

<style scoped>
.review-page {
  padding-bottom: var(--space-6);
}

.review-shell {
  max-width: 1480px;
  margin: 0 auto;
}

.review-area {
  border: 1px solid color-mix(in srgb, var(--color-primary) 10%, var(--color-border));
  border-radius: 28px;
  background:
    radial-gradient(circle at top right, rgb(59 130 246 / 10%), transparent 30%),
    linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  box-shadow: var(--shadow-lg);
  padding: clamp(22px, 3.4vw, 34px);
}

.review-form {
  display: block;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 22px;
  align-items: stretch;
}

.review-card {
  border: 1px solid var(--color-border);
  border-radius: 24px;
  background-color: rgb(255 255 255 / 88%);
  padding: 24px;
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.review-card--media,
.review-card--thumbnail {
  min-width: 0;
}

.review-card--media .upload-field,
.review-card--thumbnail .upload-field {
  flex: 1;
  height: 100%;
  min-height: 0;
}

.review-card--form {
  justify-content: space-between;
}

.section-heading {
  margin-bottom: var(--space-5);
}

.section-heading h2 {
  margin: 0 0 var(--space-2);
  font-size: 1.34rem;
}

.section-heading p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 0.96rem;
}

.upload-field {
  display: grid;
  grid-template-rows: auto 1fr;
  gap: 12px;
  width: 100%;
  height: 100%;
  margin-bottom: var(--space-3);
  padding: 16px;
  border: 1px dashed var(--color-primary-200);
  border-radius: 18px;
  background-color: var(--color-primary-light);
  overflow: hidden;
}

.upload-field--secondary {
  margin-bottom: 0;
  background-color: var(--gray-50);
  border-color: var(--color-border-strong);
}

.upload-field__header {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 48px;
}

.upload-field__title {
  font-weight: 700;
}

.upload-field__button {
  width: fit-content;
  border: none;
  border-radius: 999px;
  background-color: var(--color-primary);
  padding: 10px 14px;
  color: #fff;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 12px 22px -18px rgb(37 99 235 / 80%);
}

.upload-field__button--secondary {
  background-color: #0f766e;
  box-shadow: 0 12px 22px -18px rgb(15 118 110 / 80%);
}

.upload-field__dropzone {
  display: flex;
  flex: 1;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  flex: 1;
  min-height: 300px;
  border: 1px dashed rgb(59 130 246 / 22%);
  border-radius: 16px;
  background: rgb(255 255 255 / 54%);
  color: var(--color-text-secondary);
  text-align: center;
  padding: 24px;
  justify-items: center;
}

.upload-field__dropzone strong {
  color: var(--color-text);
  font-size: 1.04rem;
  line-height: 1.3;
  margin: 0;
}

.upload-field__dropzone span {
  font-size: 0.92rem;
  line-height: 1.25;
  margin: 0;
}

.upload-field__dropzone--secondary {
  background: rgb(249 250 251 / 92%);
}

.upload-field input {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.video-preview,
.thumbnail-preview {
  display: flex;
  flex: 1;
  min-height: 300px;
  overflow: hidden;
  border: 1px solid var(--color-border);
  border-radius: 16px;
  background-color: #0f172a;
}

.upload-field__body {
  flex: 1;
  width: 100%;
  height: 100%;
  min-height: 0;
}

.video-preview {
  width: 100%;
  max-height: none;
}

.video-preview video,
.thumbnail-preview img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
}

.thumbnail-block {
  flex: 1;
  display: flex;
  width: 100%;
}

.thumbnail-preview {
  background-color: #fff;
  width: 100%;
  max-height: none;
}

.field-group + .field-group {
  margin-top: var(--space-5);
}

.field-group label {
  display: block;
  margin-bottom: 10px;
  font-weight: 700;
  color: var(--color-text);
}

.field-group input[type='text'],
.field-group select,
.field-group textarea {
  width: 100%;
  border: 1px solid var(--color-border-strong);
  border-radius: 14px;
  background-color: #fff;
  padding: 14px 16px;
  color: var(--color-text);
}

.field-group input[type='text']:focus,
.field-group select:focus,
.field-group textarea:focus {
  outline: 2px solid rgb(59 130 246 / 18%);
  border-color: var(--color-primary);
}

.field-group textarea {
  min-height: 156px;
  resize: vertical;
}

.product-suggestions {
  list-style: none;
  padding: 0;
  margin: 8px 0 0;
  border: 1px solid var(--color-border-strong);
  border-radius: 14px;
  max-height: 210px;
  overflow-y: auto;
  background-color: #fff;
}

.product-suggestions li {
  min-height: 42px;
  padding: 10px 12px;
  cursor: pointer;
}

.product-suggestions li:hover,
.product-suggestion--active {
  background-color: var(--gray-50);
}

.selected-product {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 10px 0 0;
  padding: 8px 12px;
  border-radius: 999px;
  background-color: var(--color-primary-light);
  color: var(--color-primary-600);
}

.rating-picker {
  display: grid;
  gap: 12px;
  padding: 2px 0 4px;
}

.star-rating {
  position: relative;
  width: fit-content;
  font-size: clamp(2.2rem, 5vw, 3rem);
  line-height: 1;
}

.star-rating__base,
.star-rating__fill {
  letter-spacing: 0.12em;
  user-select: none;
  white-space: nowrap;
}

.star-rating__base {
  color: #d1d5db;
}

.star-rating__fill {
  position: absolute;
  inset: 0 auto 0 0;
  overflow: hidden;
  color: #facc15;
  text-shadow: 0 0 12px rgb(250 204 21 / 18%);
  pointer-events: none;
}

.star-rating__range {
  position: absolute;
  inset: 0;
  width: 100%;
  margin: 0;
  opacity: 0;
  cursor: ew-resize;
}

.rating-summary {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.rating-summary strong {
  color: var(--color-text);
  font-size: 1rem;
}

.rating-summary span {
  color: var(--color-text-secondary);
  font-size: var(--font-size-caption);
}

.content-meta {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-top: 8px;
  color: var(--color-text-secondary);
  font-size: var(--font-size-caption);
}

.help-text,
.status-message,
.prediction-message,
.error-message {
  margin: 10px 0 0;
  font-size: 0.94rem;
}

.selected-file {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 0.86rem;
  font-weight: 600;
}

.help-text,
.status-message {
  color: var(--color-text-secondary);
}

.prediction-message {
  color: var(--color-accent-600);
}

.error-message {
  color: var(--color-danger);
}

.submit-button {
  width: 100%;
  margin-top: var(--space-6);
  border: none;
  border-radius: 16px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-hover) 100%);
  padding: 16px 18px;
  color: #fff;
  font-weight: 800;
  font-size: 1rem;
  cursor: pointer;
  box-shadow: 0 18px 30px -20px rgb(37 99 235 / 65%);
}

.submit-button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

@media (max-width: 980px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .video-preview,
  .thumbnail-preview {
    max-height: 220px;
  }
}

@media (max-width: 720px) {
  .review-area,
  .review-card {
    border-radius: 20px;
  }

  .upload-field__header {
    align-items: flex-start;
    flex-direction: column;
  }

  .content-meta {
    flex-direction: column;
  }
}
</style>
