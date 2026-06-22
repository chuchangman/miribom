import assert from 'node:assert/strict'
import test from 'node:test'

test('predictCategoryFromImage sends an image file to the AI API', async () => {
  const aiApi = await import('./aiApi.js')
  const originalFetch = globalThis.fetch
  const imageFile = new File(['image'], 'thumbnail.png', { type: 'image/png' })
  const calls = []

  globalThis.fetch = async (url, options) => {
    calls.push({ url, options })

    return new Response(
      JSON.stringify({
        fine_label: 'dryer',
        service_label: 'washer_dryer',
        confidence: 0.95,
        top3: [],
      }),
      {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      },
    )
  }

  try {
    const result = await aiApi.predictCategoryFromImage(imageFile)

    assert.equal(result.service_label, 'washer_dryer')
    assert.equal(calls[0].url, 'http://localhost:8001/api/predict-image/')
    assert.equal(calls[0].options.method, 'POST')
    assert.ok(calls[0].options.body instanceof FormData)
    assert.equal(calls[0].options.body.get('file'), imageFile)
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('predictCategoryFromImage throws the AI API error message', async () => {
  const aiApi = await import('./aiApi.js')
  const originalFetch = globalThis.fetch

  globalThis.fetch = async () =>
    new Response(JSON.stringify({ detail: '지원하지 않는 파일 형식입니다.' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    })

  try {
    await assert.rejects(
      () =>
        aiApi.predictCategoryFromImage(
          new File(['text'], 'thumbnail.txt', { type: 'text/plain' }),
        ),
      /지원하지 않는 파일 형식입니다\./,
    )
  } finally {
    globalThis.fetch = originalFetch
  }
})
