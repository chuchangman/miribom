import { AUTH_API_URL, apiFetch } from '../config/api.js'

const parseResponse = async (response, fallbackMessage) => {
  if (response.ok) {
    return await response.json()
  }

  let message = fallbackMessage

  try {
    const data = await response.json()
    message = data.detail || data.error || data.nickname?.[0] || message
  } catch {
    // Keep the fallback message when the response has no JSON body.
  }

  throw new Error(message)
}

export const updateMyProfile = async ({ nickname }) => {
  const response = await apiFetch(`${AUTH_API_URL}/me/`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nickname }),
  })

  return await parseResponse(response, '프로필을 수정하지 못했습니다.')
}

export const fetchMyLivingProfile = async () => {
  const response = await apiFetch(`${AUTH_API_URL}/me/living/`)
  return await parseResponse(response, '생활환경 정보를 불러오지 못했습니다.')
}

export const updateMyLivingProfile = async ({ housingType, areaSize }) => {
  const response = await apiFetch(`${AUTH_API_URL}/me/living/`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      housing_type: housingType,
      area_size: areaSize,
    }),
  })

  return await parseResponse(response, '생활환경 정보를 저장하지 못했습니다.')
}
