<template>
  <div class="home-layout">
    <section class="home-main">
      <h1>구매 전, 실제 사용 영상으로 <span class="highlight">미리 봄</span></h1>
      <h3>크기 · 작동음 · 공간 배치를 짧은 영상으로 확인하세요</h3>

      <form class="search-form" @submit.prevent="search">
        <input
          v-model.trim="searchQuery"
          type="text"
          class="search-input"
          placeholder="제품명, 카테고리로 검색하세요"
        />
        <button type="submit" class="text-button">검색</button>
      </form>

      <hr />

      <section class="category-section">
        <h2>카테고리</h2>
        <p>원하는 가전을 골라보세요</p>
        <p v-if="isLoadingCategories">카테고리를 불러오는 중입니다.</p>
        <p v-else-if="categoryErrorMessage" class="error-message">
          {{ categoryErrorMessage }}
        </p>
        <div v-else class="category-list">
          <CategoryCard
            v-for="category in displayedCategories"
            :key="category.id"
            :category="category"
          />
        </div>
      </section>

      <section class="recommendation-section">
        <div class="recommendation-header">
          <div>
            <h2>생활환경에 맞는 가전 추천</h2>
            <p>입력해둔 생활환경과 관심 카테고리를 바탕으로 제품을 추천해드려요.</p>
          </div>
        </div>

        <div v-if="!isLogin" class="recommendation-login-card">
          <div class="recommendation-login-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24">
              <path
                fill-rule="evenodd"
                d="M9 4.5a.75.75 0 0 1 1.43 0l.58 1.74a4.5 4.5 0 0 0 2.84 2.84l1.74.58a.75.75 0 0 1 0 1.43l-1.74.58a4.5 4.5 0 0 0-2.84 2.84l-.58 1.74a.75.75 0 0 1-1.43 0l-.58-1.74a4.5 4.5 0 0 0-2.84-2.84l-1.74-.58a.75.75 0 0 1 0-1.43l1.74-.58a4.5 4.5 0 0 0 2.84-2.84L9 4.5Zm8.25 9a.75.75 0 0 1 .7.48l.34.9a2.25 2.25 0 0 0 1.33 1.33l.9.34a.75.75 0 0 1 0 1.4l-.9.34a2.25 2.25 0 0 0-1.33 1.33l-.34.9a.75.75 0 0 1-1.4 0l-.34-.9a2.25 2.25 0 0 0-1.33-1.33l-.9-.34a.75.75 0 0 1 0-1.4l.9-.34a2.25 2.25 0 0 0 1.33-1.33l.34-.9a.75.75 0 0 1 .7-.48Z"
                clip-rule="evenodd"
              />
            </svg>
          </div>
          <div class="recommendation-login-copy">
            <strong>내 환경에 맞는 가전, AI가 추천</strong>
            <p>주거형태 · 평수를 등록하면 비슷한 환경의 자취생 후기가 우선 보여요.</p>
          </div>
          <RouterLink to="/login">로그인하고 추천받기</RouterLink>
        </div>

        <div v-else class="recommendation-panel">
          <aside class="recommendation-controls">
            <div v-if="!hasLivingProfile" class="recommendation-empty">
              <strong>생활환경을 먼저 입력해주세요.</strong>
              <p>주거 형태와 평수를 입력하면 더 잘 맞는 추천을 받을 수 있어요.</p>
              <button type="button" @click="goLivingProfile">생활환경 입력하기</button>
            </div>

            <template v-else>
              <template v-if="recommendationStep === 'intro'">
                <div class="living-summary">
                  <span>내 생활환경</span>
                  <strong>{{ recommendationLivingSummary }}</strong>
                </div>
              </template>

              <template v-else-if="recommendationStep === 'budget'">
                <div class="survey-heading">
                  <span>1단계</span>
                  <strong>예산을 선택해주세요.</strong>
                </div>
                <label class="control-group">
                  <span>예산</span>
                  <select v-model="selectedRecommendationBudget">
                    <option value="" disabled>예산을 선택해주세요</option>
                    <option
                      v-for="option in recommendationBudgetOptions"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </option>
                  </select>
                </label>
              </template>

              <template v-else-if="recommendationStep === 'categories'">
                <div class="survey-heading">
                  <span>2단계</span>
                  <strong>관심 카테고리를 선택해주세요.</strong>
                  <p>추천받고 싶은 카테고리를 하나만 선택해주세요.</p>
                </div>

                <div class="recommendation-category-list">
                  <button
                    v-for="category in recommendationCategories"
                    :key="category.id"
                    type="button"
                    class="recommendation-category"
                    :class="{ selected: isRecommendationCategorySelected(category.id) }"
                    @click="toggleRecommendationCategory(category.id)"
                  >
                    {{ category.name }}
                  </button>
                </div>
              </template>

              <template v-else-if="currentRecommendationQuestion">
                <div class="survey-heading">
                  <span>{{ currentRecommendationQuestionIndex + 3 }}단계</span>
                  <strong>{{ currentRecommendationQuestion.text }}</strong>
                  <p>하나만 선택해주세요.</p>
                </div>

                <div class="recommendation-option-list">
                  <button
                    v-for="option in currentRecommendationQuestion.options"
                    :key="option.value"
                    type="button"
                    class="recommendation-option"
                    :class="{
                      selected: isRecommendationOptionSelected(
                        currentRecommendationQuestion,
                        option.value,
                      ),
                    }"
                    @click="selectRecommendationAnswer(currentRecommendationQuestion, option.value)"
                  >
                    {{ option.label }}
                  </button>
                </div>
              </template>

              <p v-if="recommendationErrorMessage" class="error-message">
                {{ recommendationErrorMessage }}
              </p>

              <div class="recommendation-step-actions">
                <button
                  v-if="recommendationStep !== 'intro'"
                  type="button"
                  class="recommendation-back"
                  :disabled="isLoadingRecommendationQuestions || isLoadingRecommendations"
                  @click="goPreviousRecommendationStep"
                >
                  이전
                </button>
                <button
                  v-if="recommendationStep === 'intro'"
                  type="button"
                  class="recommendation-submit"
                  :disabled="isLoadingRecommendationOptions"
                  @click="startRecommendationSurvey"
                >
                  시작하기
                </button>
                <button
                  v-else-if="recommendationStep === 'budget'"
                  type="button"
                  class="recommendation-submit"
                  :disabled="!selectedRecommendationBudget || isLoadingRecommendationOptions"
                  @click="goFromBudgetToCategories"
                >
                  다음
                </button>
                <button
                  v-else-if="recommendationStep === 'categories'"
                  type="button"
                  class="recommendation-submit"
                  :disabled="
                    selectedRecommendationCategoryIds.length === 0 ||
                    isLoadingRecommendationQuestions
                  "
                  @click="loadRecommendationQuestions"
                >
                  {{ isLoadingRecommendationQuestions ? '질문 불러오는 중...' : '다음' }}
                </button>
                <button
                  v-else
                  type="button"
                  class="recommendation-submit"
                  :disabled="!isCurrentRecommendationQuestionAnswered || isLoadingRecommendations"
                  @click="goNextRecommendationQuestion"
                >
                  {{
                    isLoadingRecommendations
                      ? '추천 받는 중...'
                      : currentRecommendationQuestionIndex === recommendationQuestionSteps.length - 1
                        ? '추천받기'
                        : '다음'
                  }}
                </button>
              </div>
            </template>
          </aside>

          <div class="recommendation-results">
            <p v-if="!hasLivingProfile" class="recommendation-placeholder">
              생활환경 입력을 완료하면 이곳에 추천 제품이 표시됩니다.
            </p>
            <p v-else-if="isLoadingRecommendationOptions" class="recommendation-placeholder">
              추천 선택지를 불러오는 중입니다.
            </p>
            <p v-else-if="recommendationResults.length === 0" class="recommendation-placeholder">
              관심 카테고리와 예산을 선택한 뒤 추천 받기를 눌러주세요.
            </p>
            <div v-else class="recommendation-result-list">
              <article
                v-for="result in recommendationResults"
                :key="result.category.id"
                class="recommendation-result-group"
              >
                <div class="result-heading">
                  <div>
                    <span>{{ result.category.name }}</span>
                    <h3>{{ result.reason || '생활환경에 어울리는 카테고리예요.' }}</h3>
                  </div>
                </div>
                <div class="recommendation-products">
                  <ProductCard
                    v-for="product in result.products"
                    :key="product.id"
                    :product="mapRecommendedProduct(product, result.category)"
                  />
                </div>
              </article>
            </div>
          </div>
        </div>
      </section>
    </section>

    <aside class="favorite-panel">
      <div class="favorite-header">
        <h2>즐겨찾기한 제품</h2>
        <RouterLink v-if="isLogin" to="/favorites">전체 보기</RouterLink>
      </div>

      <p v-if="!isLogin" class="favorite-message">
        <RouterLink to="/login">로그인</RouterLink>이 필요한 서비스입니다.
      </p>
      <p v-else-if="isLoadingFavorites" class="favorite-message">
        즐겨찾기를 불러오는 중입니다.
      </p>
      <p v-else-if="favoriteErrorMessage" class="favorite-message error-message">
        {{ favoriteErrorMessage }}
      </p>
      <p v-else-if="favoriteProducts.length === 0" class="favorite-message">
        즐겨찾기한 제품이 없습니다.
      </p>
      <div v-else class="favorite-list">
        <HomeFavoriteItem
          v-for="product in favoriteProducts"
          :key="product.id"
          :product="product"
        />
      </div>
    </aside>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import CategoryCard from '@/components/CategoryCard.vue'
import HomeFavoriteItem from '@/components/HomeFavoriteItem.vue'
import ProductCard from '@/components/ProductCard.vue'
import { useAuth } from '@/composables/useAuth.js'
import { fetchBookmarks } from '@/services/bookmarkApi.js'
import {
  fetchProductCategories,
  fetchProductRecommendations,
  fetchRecommendationQuestions,
  fetchRecommendationOptions,
} from '@/services/productApi.js'

const router = useRouter()
const { hasLivingProfile, isAuthInitialized, isLogin, user } = useAuth()

const searchQuery = ref('')
const categories = ref([])
const isLoadingCategories = ref(false)
const categoryErrorMessage = ref('')
const favoriteProducts = ref([])
const isLoadingFavorites = ref(false)
const favoriteErrorMessage = ref('')
const recommendationOptions = ref(null)
const selectedRecommendationBudget = ref('')
const selectedRecommendationCategoryIds = ref([])
const recommendationStep = ref('intro')
const recommendationQuestionGroups = ref([])
const recommendationAnswers = ref({})
const currentRecommendationQuestionIndex = ref(0)
const recommendationResults = ref([])
const isLoadingRecommendationOptions = ref(false)
const isLoadingRecommendationQuestions = ref(false)
const isLoadingRecommendations = ref(false)
const recommendationErrorMessage = ref('')

const displayedCategories = computed(() => categories.value.slice(0, 8))
const recommendationCategories = computed(
  () => recommendationOptions.value?.categories || categories.value,
)
const recommendationBudgetOptions = computed(
  () => recommendationOptions.value?.budget_options || [],
)
const recommendationLivingSummary = computed(() => {
  const housingType = recommendationOptions.value?.housing_type || user.value?.housing_type || ''
  const areaSize = recommendationOptions.value?.area_size || user.value?.area_size
  const housingLabel =
    {
      apartment: '아파트',
      villa: '빌라',
      officetel: '오피스텔',
      detached: '단독주택',
      dormitory: '기숙사',
    }[housingType] || housingType || '주거 형태 미입력'

  return areaSize ? `${housingLabel} · ${areaSize}평` : housingLabel
})
const canRequestRecommendations = computed(
  () =>
    isLogin.value &&
    hasLivingProfile.value &&
    selectedRecommendationBudget.value &&
    selectedRecommendationCategoryIds.value.length > 0,
)
const selectedRecommendationCategories = computed(() =>
  recommendationCategories.value.filter((category) =>
    isRecommendationCategorySelected(category.id),
  ),
)
const recommendationQuestionSteps = computed(() => {
  const steps = []

  const appendQuestion = (categoryId, question) => {
    steps.push({
      ...question,
      categoryId: String(categoryId),
      key: `${categoryId}:${question.id}`,
    })

    const answer = recommendationAnswers.value[String(categoryId)]?.[question.id]
    const selectedValues = Array.isArray(answer) ? answer : answer ? [answer] : []

    question.options?.forEach((option) => {
      if (!selectedValues.includes(option.value)) {
        return
      }

      option.follow_up?.forEach((followUpQuestion) => {
        appendQuestion(categoryId, followUpQuestion)
      })
    })
  }

  recommendationQuestionGroups.value.forEach((group) => {
    group.questions?.forEach((question) => {
      appendQuestion(group.category_id, question)
    })
  })

  return steps
})
const currentRecommendationQuestion = computed(
  () => recommendationQuestionSteps.value[currentRecommendationQuestionIndex.value] || null,
)
const currentRecommendationQuestionNumber = computed(
  () =>
    Math.min(
      currentRecommendationQuestionIndex.value + 1,
      recommendationQuestionSteps.value.length || 1,
    ),
)
const isCurrentRecommendationQuestionAnswered = computed(() => {
  const question = currentRecommendationQuestion.value

  if (!question) {
    return true
  }

  const answer = recommendationAnswers.value[question.categoryId]?.[question.id]
  return Array.isArray(answer) ? answer.length > 0 : Boolean(answer)
})

function search() {
  router.push({
    name: 'ProductSearch',
    query: searchQuery.value ? { search: searchQuery.value } : {},
  })
}

const loadCategories = async () => {
  isLoadingCategories.value = true
  categoryErrorMessage.value = ''

  try {
    categories.value = await fetchProductCategories()
  } catch (error) {
    categoryErrorMessage.value = error.message || '카테고리를 불러오지 못했습니다.'
  } finally {
    isLoadingCategories.value = false
  }
}

const mapBookmarkProduct = (bookmark) => ({
  id: String(bookmark.product.id),
  name: bookmark.product.title,
  imageUrl: bookmark.product.image,
  price: bookmark.product.lprice || 0,
})

const loadFavorites = async () => {
  favoriteErrorMessage.value = ''

  if (!isLogin.value) {
    favoriteProducts.value = []
    return
  }

  isLoadingFavorites.value = true

  try {
    const bookmarks = await fetchBookmarks()
    favoriteProducts.value = bookmarks.slice(0, 4).map(mapBookmarkProduct)
  } catch (error) {
    favoriteErrorMessage.value = error.message || '즐겨찾기를 불러오지 못했습니다.'
  } finally {
    isLoadingFavorites.value = false
  }
}

const goLivingProfile = () => {
  router.push({ name: 'LivingProfile', query: { mode: 'onboarding' } })
}

const syncRecommendationDefaults = () => {
  selectedRecommendationBudget.value = ''
}

const resetRecommendationSurvey = ({ keepResults = true } = {}) => {
  recommendationStep.value = 'intro'
  selectedRecommendationBudget.value = ''
  selectedRecommendationCategoryIds.value = []
  recommendationQuestionGroups.value = []
  recommendationAnswers.value = {}
  currentRecommendationQuestionIndex.value = 0

  if (!keepResults) {
    recommendationResults.value = []
  }
}

const loadRecommendationOptions = async () => {
  recommendationErrorMessage.value = ''
  recommendationResults.value = []

  if (!isLogin.value || !hasLivingProfile.value) {
    recommendationOptions.value = null
    selectedRecommendationBudget.value = ''
    resetRecommendationSurvey({ keepResults: false })
    return
  }

  isLoadingRecommendationOptions.value = true

  try {
    recommendationOptions.value = await fetchRecommendationOptions()
    syncRecommendationDefaults()
  } catch (error) {
    recommendationErrorMessage.value = error.message || '추천 선택지를 불러오지 못했습니다.'
  } finally {
    isLoadingRecommendationOptions.value = false
  }
}

const startRecommendationSurvey = () => {
  recommendationErrorMessage.value = ''
  recommendationResults.value = []
  selectedRecommendationBudget.value = ''
  recommendationStep.value = 'budget'
}

const goFromBudgetToCategories = () => {
  recommendationErrorMessage.value = ''
  recommendationStep.value = 'categories'
}

const isRecommendationCategorySelected = (categoryId) =>
  selectedRecommendationCategoryIds.value.some((selectedId) => String(selectedId) === String(categoryId))

const toggleRecommendationCategory = (categoryId) => {
  if (isRecommendationCategorySelected(categoryId)) {
    selectedRecommendationCategoryIds.value = []
    return
  }

  selectedRecommendationCategoryIds.value = [categoryId]
}

const loadRecommendationQuestions = async () => {
  if (selectedRecommendationCategoryIds.value.length === 0 || isLoadingRecommendationQuestions.value) {
    recommendationErrorMessage.value = '관심 카테고리를 하나 이상 선택해주세요.'
    return
  }

  recommendationErrorMessage.value = ''
  recommendationAnswers.value = {}
  recommendationQuestionGroups.value = []
  currentRecommendationQuestionIndex.value = 0
  isLoadingRecommendationQuestions.value = true

  try {
    const response = await fetchRecommendationQuestions(selectedRecommendationCategoryIds.value)
    recommendationQuestionGroups.value = response.categories || []

    if (recommendationQuestionSteps.value.length === 0) {
      await loadRecommendations()
      return
    }

    recommendationStep.value = 'questions'
  } catch (error) {
    recommendationErrorMessage.value = error.message || '추천 질문을 불러오지 못했습니다.'
  } finally {
    isLoadingRecommendationQuestions.value = false
  }
}

const isRecommendationOptionSelected = (question, optionValue) => {
  const answer = recommendationAnswers.value[question.categoryId]?.[question.id]
  return Array.isArray(answer) ? answer.includes(optionValue) : answer === optionValue
}

const selectRecommendationAnswer = (question, optionValue) => {
  const categoryAnswers = {
    ...(recommendationAnswers.value[question.categoryId] || {}),
  }

  categoryAnswers[question.id] = optionValue

  recommendationAnswers.value = {
    ...recommendationAnswers.value,
    [question.categoryId]: categoryAnswers,
  }
}

const goPreviousRecommendationQuestion = () => {
  if (currentRecommendationQuestionIndex.value > 0) {
    currentRecommendationQuestionIndex.value -= 1
    return
  }

  recommendationStep.value = 'categories'
}

const goPreviousRecommendationStep = () => {
  if (recommendationStep.value === 'budget') {
    selectedRecommendationBudget.value = ''
    recommendationStep.value = 'intro'
  } else if (recommendationStep.value === 'categories') {
    recommendationStep.value = 'budget'
  } else {
    goPreviousRecommendationQuestion()
  }
}

const goNextRecommendationQuestion = async () => {
  if (!isCurrentRecommendationQuestionAnswered.value) {
    recommendationErrorMessage.value = '선택지를 하나 이상 골라주세요.'
    return
  }

  recommendationErrorMessage.value = ''
  const nextIndex = currentRecommendationQuestionIndex.value + 1

  if (nextIndex < recommendationQuestionSteps.value.length) {
    currentRecommendationQuestionIndex.value = nextIndex
    return
  }

  await loadRecommendations()
}

const mapRecommendedProduct = (product, category) => ({
  id: String(product.id),
  name: product.title,
  imageUrl: product.image,
  price: product.lprice || 0,
  category: product.category?.name || category?.name || '',
})

const buildRecommendationAnswerPayload = () => {
  const payload = {}

  recommendationQuestionSteps.value.forEach((question) => {
    const answer = recommendationAnswers.value[question.categoryId]?.[question.id]

    if (!answer || (Array.isArray(answer) && answer.length === 0)) {
      return
    }

    payload[question.categoryId] = {
      ...(payload[question.categoryId] || {}),
      [question.id]: answer,
    }
  })

  return payload
}

const loadRecommendations = async () => {
  if (!canRequestRecommendations.value || isLoadingRecommendations.value) {
    return
  }

  recommendationErrorMessage.value = ''
  isLoadingRecommendations.value = true

  try {
    const response = await fetchProductRecommendations({
      housingType: recommendationOptions.value?.housing_type || user.value?.housing_type,
      areaSize: recommendationOptions.value?.area_size || user.value?.area_size || null,
      categoryIds: selectedRecommendationCategoryIds.value,
      budget: selectedRecommendationBudget.value,
      categoryAnswers: buildRecommendationAnswerPayload(),
    })

    recommendationResults.value = response.results || []
    resetRecommendationSurvey({ keepResults: true })
  } catch (error) {
    recommendationErrorMessage.value = error.message || '추천 제품을 불러오지 못했습니다.'
  } finally {
    isLoadingRecommendations.value = false
  }
}

watch(
  [isAuthInitialized, isLogin, hasLivingProfile],
  ([isInitialized]) => {
    if (isInitialized) {
      loadFavorites()
      loadRecommendationOptions()
    }
  },
  { immediate: true },
)

onMounted(loadCategories)
</script>

<style scoped>
.home-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 28px;
  align-items: start;
}

.home-main {
  min-width: 0;
}

h1 {
  margin: 0 0 0.5em;
  font-size: 2em;
}

h3 {
  margin-bottom: 1em;
  color: #64748b;
  font-size: 1.05em;
  font-weight: 500;
}

.highlight {
  color: #2563eb;
  white-space: nowrap;
}

.search-form {
  display: flex;
  justify-content: space-between;
  gap: 0.5em;
  margin-bottom: 1em;
  border: 1px solid #cbd5e1;
  border-radius: 999px;
  background-color: white;
  padding: 0.5em 0.75em;
}

.search-input {
  min-width: 0;
  flex: 1;
  border: 0;
  background-color: transparent;
  padding: 0.5em;
  outline: none;
  font-size: 1em;
}

.text-button {
  border: none;
  background: none;
  color: #2563eb;
  cursor: pointer;
}

.favorite-header a:hover,
.favorite-message a:hover {
  text-decoration: underline;
}

hr {
  margin: 28px 0;
  border: 0;
  border-top: 1px solid #e2e8f0;
}

.category-section > h2 {
  margin-bottom: 6px;
}

.category-section > p {
  margin-top: 0;
  color: #64748b;
}

.category-list {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.category-list :deep(.category-card) {
  box-sizing: border-box;
  width: 100%;
  min-height: 124px;
  border-color: #e2e8f0;
  border-radius: 18px;
}

.recommendation-section {
  margin-top: 34px;
}

.recommendation-header {
  margin-bottom: 16px;
}

.recommendation-header h2 {
  margin: 0 0 6px;
  font-size: 1.45rem;
}

.recommendation-header p {
  margin: 0;
  color: #64748b;
}

.recommendation-panel {
  display: grid;
  grid-template-columns: minmax(260px, 2fr) minmax(0, 3fr);
  gap: 18px;
  align-items: stretch;
}

.recommendation-login-card {
  min-height: 112px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  border: 1px solid #93c5fd;
  border-radius: 18px;
  background:
    linear-gradient(135deg, rgb(37 99 235 / 9%) 0%, rgb(29 78 216 / 15%) 100%),
    #fff;
  padding: 20px 24px;
  box-shadow: 0 12px 28px rgb(37 99 235 / 10%);
}

.recommendation-login-icon {
  width: 58px;
  height: 58px;
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 48%, #1e40af 100%);
  color: #fff;
  box-shadow: 0 14px 26px rgb(37 99 235 / 28%);
}

.recommendation-login-icon svg {
  width: 30px;
  height: 30px;
  fill: currentColor;
}

.recommendation-login-copy {
  flex: 1;
}

.recommendation-login-card strong {
  color: var(--color-text);
  font-size: 1.08rem;
}

.recommendation-login-card p {
  margin: 6px 0 0;
  color: #64748b;
}

.recommendation-login-card a {
  flex: 0 0 auto;
  color: var(--color-text);
  font-size: 0.9rem;
  font-weight: 900;
  text-decoration: none;
}

.recommendation-login-card a:hover {
  text-decoration: underline;
}

.recommendation-controls,
.recommendation-results {
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  background-color: #fff;
  box-shadow: 0 10px 26px rgb(15 23 42 / 5%);
}

.recommendation-controls {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 20px;
}

.living-summary {
  display: grid;
  gap: 6px;
  border: 1px solid var(--color-primary-200);
  border-radius: 14px;
  background-color: var(--color-primary-light);
  padding: 16px;
}

.living-summary span,
.control-group > span {
  color: #64748b;
  font-size: 0.84rem;
  font-weight: 800;
}

.living-summary strong {
  color: var(--color-text);
  font-size: 1.08rem;
}

.control-group {
  display: grid;
  gap: 10px;
}

.control-group select {
  width: 100%;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  background-color: #fff;
  padding: 12px 14px;
  color: var(--color-text);
  font-weight: 700;
}

.survey-heading {
  display: grid;
  gap: 7px;
}

.survey-heading span {
  color: var(--color-primary-600);
  font-size: 0.82rem;
  font-weight: 900;
}

.survey-heading strong {
  color: var(--color-text);
  font-size: 1.08rem;
  line-height: 1.45;
}

.survey-heading p {
  margin: 0;
  color: #64748b;
  font-size: 0.9rem;
  line-height: 1.5;
}

.recommendation-category-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.recommendation-option-list {
  display: grid;
  gap: 10px;
}

.recommendation-category,
.recommendation-option {
  border: 1px solid #cbd5e1;
  border-radius: 999px;
  background-color: #fff;
  padding: 9px 12px;
  color: #475569;
  font-weight: 800;
  cursor: pointer;
}

.recommendation-option {
  width: 100%;
  border-radius: 12px;
  padding: 12px 14px;
  text-align: left;
}

.recommendation-category.selected,
.recommendation-option.selected {
  border-color: var(--color-primary);
  background-color: var(--color-primary-light);
  color: var(--color-primary-600);
}

.recommendation-submit,
.recommendation-back,
.recommendation-empty a,
.recommendation-empty button {
  border-radius: 14px;
  padding: 14px 16px;
  font-weight: 900;
  text-align: center;
  text-decoration: none;
  cursor: pointer;
}

.recommendation-submit {
  border: none;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-hover) 100%);
  color: #fff;
}

.recommendation-empty a,
.recommendation-empty button {
  border: none;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-hover) 100%);
  color: #fff;
}

.recommendation-back {
  border: 1px solid var(--color-primary);
  background-color: #fff;
  color: var(--color-primary-600);
}

.recommendation-step-actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: auto;
}

.recommendation-step-actions .recommendation-submit:only-child {
  grid-column: 1 / -1;
}

.recommendation-submit:disabled,
.recommendation-back:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.recommendation-empty {
  min-height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 10px;
  text-align: center;
}

.recommendation-empty strong {
  font-size: 1.05rem;
}

.recommendation-empty p {
  margin: 0;
  color: #64748b;
  line-height: 1.5;
}

.recommendation-results {
  min-height: 420px;
  padding: 20px;
}

.recommendation-placeholder {
  min-height: 360px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0;
  color: #64748b;
  text-align: center;
}

.recommendation-result-list {
  display: grid;
  gap: 22px;
}

.recommendation-result-group {
  display: grid;
  gap: 14px;
}

.result-heading span {
  color: var(--color-primary-600);
  font-size: 0.82rem;
  font-weight: 900;
}

.result-heading h3 {
  margin: 4px 0 0;
  color: var(--color-text);
  font-size: 1rem;
  line-height: 1.45;
}

.recommendation-products {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 2px 2px 12px;
  scroll-snap-type: x mandatory;
}

.recommendation-products :deep(.product-card) {
  flex: 0 0 220px;
  height: 320px;
  scroll-snap-align: start;
}

.recommendation-products :deep(.product-image-area) {
  height: 168px;
}

.favorite-panel {
  min-height: 340px;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background-color: #fff;
  padding: 22px;
  box-shadow: 0 8px 24px rgb(15 23 42 / 6%);
}

.favorite-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.favorite-header h2 {
  margin: 0;
  font-size: 1.1rem;
}

.favorite-header a,
.favorite-message a {
  color: #2563eb;
  font-size: 0.85rem;
  font-weight: 700;
  text-decoration: none;
}

.favorite-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.favorite-message {
  min-height: 210px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0;
  color: #64748b;
  text-align: center;
}

.error-message {
  color: #dc2626;
}

@media (max-width: 1000px) {
  .home-layout {
    grid-template-columns: 1fr;
  }

  .favorite-panel {
    width: auto;
  }

  .recommendation-panel {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .category-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .recommendation-login-card {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
