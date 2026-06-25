import assert from 'node:assert/strict'
import test from 'node:test'

test('auth service updates my profile through the me endpoint', async () => {
  const authApi = await import('./authApi.js')
  const originalFetch = globalThis.fetch
  const calls = []

  globalThis.fetch = async (url, options = {}) => {
    calls.push({ url, options })

    return new Response(JSON.stringify({ id: 1, nickname: '새닉네임' }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  }

  try {
    const user = await authApi.updateMyProfile({ nickname: '새닉네임' })

    assert.equal(user.nickname, '새닉네임')
    assert.equal(calls[0].url, 'http://localhost:8000/api/auth/me/')
    assert.equal(calls[0].options.method, 'PATCH')
    assert.equal(calls[0].options.headers['Content-Type'], 'application/json')
    assert.equal(calls[0].options.body, JSON.stringify({ nickname: '새닉네임' }))
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('auth service changes password through the me password endpoint', async () => {
  const authApi = await import('./authApi.js')
  const originalFetch = globalThis.fetch
  const calls = []

  globalThis.fetch = async (url, options = {}) => {
    calls.push({ url, options })

    return new Response(null, {
      status: 200,
    })
  }

  try {
    const result = await authApi.changeMyPassword({
      currentPassword: 'old-password',
      newPassword: 'new-password',
    })

    assert.equal(result, null)
    assert.equal(calls[0].url, 'http://localhost:8000/api/auth/me/password/')
    assert.equal(calls[0].options.method, 'PATCH')
    assert.equal(calls[0].options.headers['Content-Type'], 'application/json')
    assert.equal(
      calls[0].options.body,
      JSON.stringify({
        current_password: 'old-password',
        new_password: 'new-password',
      }),
    )
  } finally {
    globalThis.fetch = originalFetch
  }
})
