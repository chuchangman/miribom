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
