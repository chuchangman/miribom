<template>
  <section class="living-profile-page">
    <div class="living-profile-shell">
      <header class="living-profile-header">
        <h1>{{ pageTitle }}</h1>
        <p>{{ pageDescription }}</p>
      </header>

      <form class="living-profile-form" @submit.prevent="saveLivingProfile">
        <section class="living-section">
          <div class="section-heading">
            <h2>주거 형태</h2>
            <p>제품을 실제로 둘 공간과 가장 가까운 환경을 선택해주세요.</p>
          </div>

          <div class="housing-options">
            <button
              v-for="option in housingOptions"
              :key="option.value"
              type="button"
              class="housing-card"
              :class="{ selected: housingType === option.value }"
              @click="housingType = option.value"
            >
              <strong>{{ option.label }}</strong>
              <span>{{ option.description }}</span>
            </button>
          </div>
          <p v-if="housingTypeError" class="error-message">{{ housingTypeError }}</p>
        </section>

        <section class="living-section">
          <div class="area-header">
            <div>
              <h2>평수</h2>
              <p>대략적인 생활 공간 크기를 알려주세요.</p>
            </div>
            <strong>{{ areaSize }}평</strong>
          </div>

          <input id="area-size" v-model="areaSize" type="range" min="1" max="60" />

          <div class="range-labels">
            <span>1평</span>
            <span>20평</span>
            <span>40평</span>
            <span>60평</span>
          </div>
          <p v-if="areaSizeError" class="error-message">{{ areaSizeError }}</p>
        </section>

        <p v-if="saveErrorMessage" class="error-message">{{ saveErrorMessage }}</p>

        <div class="form-actions">
          <button
            v-if="!isOnboardingMode"
            type="button"
            class="secondary-button"
            :disabled="isSaving"
            @click="router.push({ name: 'MyPage' })"
          >
            취소
          </button>
          <button type="submit" class="save-button" :disabled="isSaving">
            {{ isSaving ? '저장 중...' : submitLabel }}
          </button>
        </div>
      </form>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { onBeforeRouteLeave, useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const route = useRoute()
const router = useRouter()
const { hasLivingProfile, updateLivingProfile, user } = useAuth()

const housingOptions = [
  {
    value: 'apartment',
    label: '아파트',
    description: '일반적인 가족 주거 공간',
  },
  {
    value: 'villa',
    label: '빌라',
    description: '중소형 주거 공간',
  },
  {
    value: 'officetel',
    label: '오피스텔',
    description: '1인 또는 소형 공간',
  },
  {
    value: 'detached',
    label: '단독주택',
    description: '층간/공간 분리가 있는 주거',
  },
  {
    value: 'dormitory',
    label: '기숙사',
    description: '개인 공간 중심의 생활',
  },
]

const housingType = ref('')
const areaSize = ref(10)
const initialHousingType = ref('')
const initialAreaSize = ref(10)
const isSaved = ref(false)
const isSaving = ref(false)

const housingTypeError = ref('')
const areaSizeError = ref('')
const saveErrorMessage = ref('')

const isOnboardingMode = computed(
  () => route.query.mode === 'onboarding' || !hasLivingProfile.value,
)

const pageTitle = computed(() =>
  isOnboardingMode.value ? '생활환경을 먼저 입력해주세요' : '생활환경 정보 수정',
)

const pageDescription = computed(() =>
  isOnboardingMode.value
    ? '처음 한 번만 입력하면 홈에서 더 잘 맞는 가전제품 추천을 받을 수 있어요.'
    : '공간이 바뀌었다면 생활환경을 다시 맞춰 추천 기준을 업데이트할 수 있어요.',
)

const submitLabel = computed(() => (isOnboardingMode.value ? '시작하기' : '수정 완료'))

const hasUnsavedChanges = computed(() => {
  if (isSaved.value) {
    return false
  }

  return (
    housingType.value !== initialHousingType.value ||
    Number(areaSize.value) !== Number(initialAreaSize.value)
  )
})

const syncLivingProfile = () => {
  const nextHousingType = user.value?.housing_type || ''
  const nextAreaSize = user.value?.area_size || 10

  housingType.value = nextHousingType
  areaSize.value = nextAreaSize
  initialHousingType.value = nextHousingType
  initialAreaSize.value = nextAreaSize
}

const validateLivingProfile = () => {
  housingTypeError.value = ''
  areaSizeError.value = ''
  saveErrorMessage.value = ''

  if (!housingType.value) {
    housingTypeError.value = '주거 형태를 선택해주세요.'
  }

  if (!areaSize.value || Number(areaSize.value) < 1) {
    areaSizeError.value = '평수는 1 이상이어야 합니다.'
  }

  return !housingTypeError.value && !areaSizeError.value
}

const saveLivingProfile = async () => {
  if (isSaving.value || !validateLivingProfile()) {
    return
  }

  isSaving.value = true

  try {
    await updateLivingProfile({
      housingType: housingType.value,
      areaSize: Number(areaSize.value),
    })
    isSaved.value = true

    router.push({ name: isOnboardingMode.value ? 'Home' : 'MyPage' })
  } catch (error) {
    saveErrorMessage.value = error.message || '생활환경 정보를 저장하지 못했습니다.'
  } finally {
    isSaving.value = false
  }
}

watch(user, syncLivingProfile, { immediate: true })

onBeforeRouteLeave(() => {
  if (!hasUnsavedChanges.value) {
    return true
  }

  return window.confirm('지금 이동하면 입력한 생활환경 정보가 초기화됩니다. 정말 이동하시겠습니까?')
})
</script>

<style scoped>
.living-profile-page {
  min-height: calc(100vh - 120px);
  padding: clamp(28px, 4vw, 52px) clamp(28px, 5vw, 72px) 64px;
}

.living-profile-shell {
  width: 100%;
  max-width: 1480px;
  margin-inline: auto;
}

.living-profile-header {
  margin-bottom: 30px;
}

.living-profile-header h1 {
  margin: 0;
  color: var(--color-text);
  font-size: 2.5rem;
  line-height: 1.15;
}

.living-profile-header p:last-child {
  margin: 10px 0 0;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.living-profile-form {
  display: grid;
  gap: 34px;
  border: 1px solid var(--color-border);
  border-radius: 24px;
  background-color: #fff;
  padding: clamp(28px, 4vw, 44px);
  box-shadow: var(--shadow-md);
}

.living-section {
  display: grid;
  gap: 20px;
}

.section-heading h2,
.area-header h2 {
  margin: 0;
  font-size: 1.35rem;
}

.section-heading p,
.area-header p {
  margin: 6px 0 0;
  color: var(--color-text-secondary);
}

.housing-options {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 16px;
}

.housing-card {
  min-height: 132px;
  display: grid;
  align-content: center;
  gap: 10px;
  border: 1px solid var(--color-border);
  border-radius: 14px;
  background-color: #fff;
  padding: 18px 20px;
  color: var(--color-text);
  cursor: pointer;
  text-align: center;
}

.housing-card strong {
  display: block;
  font-size: 1.04rem;
  line-height: 1.25;
}

.housing-card span {
  display: block;
  color: var(--color-text-secondary);
  font-size: 0.88rem;
  font-weight: 600;
  line-height: 1.35;
  word-break: keep-all;
}

.housing-card.selected {
  border-color: var(--color-primary);
  background-color: var(--color-primary-light);
  color: var(--color-primary-600);
}

.area-header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
}

.area-header strong {
  color: var(--color-primary-600);
  font-size: 1.6rem;
}

input[type='range'] {
  width: 100%;
  min-height: 34px;
  accent-color: var(--color-primary);
}

.range-labels {
  display: flex;
  justify-content: space-between;
  color: var(--color-text-secondary);
  font-size: 0.84rem;
}

.form-actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.save-button,
.secondary-button {
  width: 100%;
  min-width: 0;
  border: 1px solid transparent;
  border-radius: 14px;
  padding: 16px 20px;
  font-weight: 800;
  cursor: pointer;
}

.save-button {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-hover) 100%);
  color: #fff;
  box-shadow: 0 14px 26px -20px rgb(37 99 235 / 70%);
}

.secondary-button {
  border-color: var(--color-primary);
  background-color: #fff;
  color: var(--color-primary-600);
  box-shadow: none;
}

.save-button:disabled,
.secondary-button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.error-message {
  margin: 0;
  color: var(--color-danger);
  font-size: 0.92rem;
}

@media (max-width: 900px) {
  .housing-options {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .living-profile-page {
    padding-inline: 14px;
  }

  .living-profile-form {
    border-radius: 20px;
    padding: 18px;
  }

  .housing-options {
    grid-template-columns: 1fr;
  }

  .form-actions {
    grid-template-columns: 1fr;
  }
}
</style>
