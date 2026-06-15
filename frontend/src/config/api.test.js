import assert from 'node:assert/strict'
import test from 'node:test'
import * as api from './api.js'

test('apiFetch retries the request once after a successful token refresh', async () => {
  assert.equal(typeof api.apiFetch, 'function')

  const originalFetch = globalThis.fetch
  const calls = []

  globalThis.fetch = async (url, options) => {
    calls.push({ url, options })

    if (calls.length === 1) {
      return new Response(null, { status: 401 })
    }

    if (calls.length === 2) {
      return new Response(null, { status: 200 })
    }

    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  }

  try {
    const response = await api.apiFetch(`${api.API_BASE_URL}/protected/`)

    assert.equal(response.status, 200)
    assert.deepEqual(
      calls.map(({ url }) => url),
      [
        `${api.API_BASE_URL}/protected/`,
        `${api.AUTH_API_URL}/refresh/`,
        `${api.API_BASE_URL}/protected/`,
      ],
    )
    assert.ok(calls.every(({ options }) => options.credentials === 'include'))
  } finally {
    globalThis.fetch = originalFetch
  }
})
