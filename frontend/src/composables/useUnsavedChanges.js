import { ref } from 'vue'

const hasUnsavedChanges = ref(false)
const navigationMessage =
  '지금 이동하면 작성한 정보가 초기화됩니다. 정말 이동하시겠습니까?'

export const useUnsavedChanges = () => {
  const setHasUnsavedChanges = (value) => {
    hasUnsavedChanges.value = Boolean(value)
  }

  const confirmUnsavedNavigation = () => {
    if (!hasUnsavedChanges.value) {
      return true
    }

    return window.confirm(navigationMessage)
  }

  return {
    confirmUnsavedNavigation,
    setHasUnsavedChanges,
  }
}
