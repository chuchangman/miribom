import { AI_API_URL } from '../config/api.js'

export const predictCategoryFromImage = async (imageFile) => {
  const formData = new FormData()
  formData.append('file', imageFile)

  const response = await fetch(`${AI_API_URL}/api/predict-image/`, {
    method: 'POST',
    body: formData,
  })

  if (response.ok) {
    return await response.json()
  }

  let message = 'AI 카테고리 예측에 실패했습니다.'

  try {
    const data = await response.json()
    message = data.detail || data.error || message
  } catch {
    // Keep the fallback message when the response has no JSON body.
  }

  throw new Error(message)
}
