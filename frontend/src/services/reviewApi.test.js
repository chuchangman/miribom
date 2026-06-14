import assert from 'node:assert/strict'
import test from 'node:test'

test('searchProducts returns paginated product results', async () => {
  const reviewApi = await import('./reviewApi.js')
  const originalFetch = globalThis.fetch

  globalThis.fetch = async () =>
    new Response(JSON.stringify({ results: [{ id: 3, title: '테스트 제품' }] }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })

  try {
    const products = await reviewApi.searchProducts({ query: '테스트', categoryId: 1 })

    assert.deepEqual(products, [{ id: 3, title: '테스트 제품' }])
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('createReviewFlow completes the upload and review requests in order', async () => {
  const reviewApi = await import('./reviewApi.js')

  assert.equal(typeof reviewApi.createReviewFlow, 'function')

  const originalFetch = globalThis.fetch
  const calls = []
  const responses = [
    {
      video_upload_id: 11,
      presigned_url: 'https://r2.example.com/upload',
      r2_key: 'videos/1/test.mp4',
    },
    null,
    { video_upload_id: 11, status: 'uploaded' },
    { id: 22, product_id: 33 },
    { id: 44, rating: 5, content: '좋아요' },
  ]

  globalThis.fetch = async (url, options = {}) => {
    const responseBody = responses[calls.length]
    calls.push({ url, options })

    return new Response(responseBody ? JSON.stringify(responseBody) : null, {
      status: calls.length === 2 ? 200 : 201,
      headers: responseBody ? { 'Content-Type': 'application/json' } : {},
    })
  }

  try {
    const result = await reviewApi.createReviewFlow({
      file: { name: 'review.mp4', type: 'video/mp4', size: 1024 },
      productId: 33,
      rating: 5,
      content: '좋아요',
    })

    assert.equal(result.id, 44)
    assert.deepEqual(
      calls.map(({ url }) => url),
      [
        'http://localhost:8000/api/videos/presigned-url/',
        'https://r2.example.com/upload',
        'http://localhost:8000/api/videos/11/complete/',
        'http://localhost:8000/api/videos/',
        'http://localhost:8000/api/videos/22/reviews/',
      ],
    )
    assert.equal(calls[1].options.method, 'PUT')
  } finally {
    globalThis.fetch = originalFetch
  }
})
