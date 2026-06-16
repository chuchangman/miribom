<template>
  <h1>당신의 생활환경을 입력해주세요.</h1>
  <h3>비슷한 환경의 자취생 후기를 우선 보여드려요</h3>
  <div class="housing-options">
    <button
      type="button"
      class="housing-card"
      :class="{ selected: housingType === '원룸' }"
      @click="housingType = '원룸'"
    >
      원룸
    </button>

    <button
      type="button"
      class="housing-card"
      :class="{ selected: housingType === '투룸' }"
      @click="housingType = '투룸'"
    >
      투룸
    </button>

    <button
      type="button"
      class="housing-card"
      :class="{ selected: housingType === '아파트' }"
      @click="housingType = '아파트'"
    >
      아파트
    </button>

    <button
      type="button"
      class="housing-card"
      :class="{ selected: housingType === '오피스텔' }"
      @click="housingType = '오피스텔'"
    >
      오피스텔
    </button>

    <button
      type="button"
      class="housing-card"
      :class="{ selected: housingType === '기숙사' }"
      @click="housingType = '기숙사'"
    >
      기숙사
    </button>
  </div>
  <div class="area-header">
    <label for="area-size">평수</label>
    <strong>{{ areaSize }}평</strong>
  </div>

  <input id="area-size" type="range" min="1" max="40" v-model="areaSize" />

  <div class="range-labels">
    <span>1평</span>
    <span>15평</span>
    <span>30평</span>
    <span>40평+</span>
  </div>
  <button type="button" class="save-button" @click="saveLivingProfile">저장하기</button>

  <div v-if="housingTypeError" class="error-message">{{ housingTypeError }}</div>
  <div v-if="areaSizeError" class="error-message">{{ areaSizeError }}</div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { onBeforeRouteLeave, useRouter } from 'vue-router'

const router = useRouter()
const housingType = ref('')
const areaSize = ref(1)
const isSaved = ref(false)

const housingTypeError = ref('')
const areaSizeError = ref('')

const hasUnsavedChanges = computed(
  () => !isSaved.value && Boolean(housingType.value || Number(areaSize.value) !== 1),
)

function saveLivingProfile() {
  housingTypeError.value = ''
  areaSizeError.value = ''

  if (!housingType.value) {
    housingTypeError.value = '주거형태를 선택해주세요.'
  }

  if (!areaSize.value || Number(areaSize.value) < 1) {
    areaSizeError.value = '평수는 1 이상이어야 합니다.'
  }

  if (housingTypeError.value || areaSizeError.value) {
    return
  }

  isSaved.value = true
  router.push('/mypage')
}

onBeforeRouteLeave(() => {
  if (!hasUnsavedChanges.value) {
    return true
  }

  return window.confirm(
    '지금 이동하면 작성한 정보가 초기화됩니다. 정말 이동하시겠습니까?',
  )
})
</script>

<style scoped>
.housing-options {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.housing-card {
  height: 72px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background-color: #fff;
  cursor: pointer;
  font-weight: 600;
}

.housing-card.selected {
  border-color: #10b981;
  background-color: #ecfdf5;
  color: #059669;
}

.area-header {
  display: flex;
  justify-content: space-between;
  margin-top: 24px;
  margin-bottom: 8px;
}

.area-header strong {
  color: #059669;
}

input[type='range'] {
  width: 100%;
  accent-color: #10b981;
}

.range-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: #6b7280;
}

.save-button {
  width: 100%;
  margin-top: 24px;
  padding: 14px 16px;
  border: none;
  border-radius: 10px;
  background-color: #10b981;
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.save-button:hover {
  background-color: #059669;
}

.error-message {
  margin-top: 8px;
  color: #ef4444;
  font-size: 14px;
}
</style>
