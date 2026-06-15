import assert from 'node:assert/strict'
import test from 'node:test'

test('video service loads the feed and reviews with cursor parameters', async () => {
  const videoApi = await import('./videoApi.js')
  const originalFetch = globalThis.fetch
  const calls = []

  globalThis.fetch = async (url) => {
    calls.push(url)

    return new Response(JSON.stringify(calls.length === 1 ? [{ id: 9 }] : [{ id: 4 }]), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  }

  try {
    const videos = await videoApi.fetchVideos({ cursor: 10 })
    const reviews = await videoApi.fetchVideoReviews(9)

    assert.equal(videos[0].id, 9)
    assert.equal(reviews[0].id, 4)
    assert.deepEqual(calls, [
      'http://localhost:8000/api/videos/?cursor=10',
      'http://localhost:8000/api/videos/9/reviews/',
    ])
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('mapVideoFeedItem creates a video item without waiting for review data', async () => {
  const videoApi = await import('./videoApi.js')

  const video = videoApi.mapVideoFeedItem({
    id: 9,
    video_url: 'https://example.com/video.mp4',
    product_id: 3,
    product_title: '테스트 제품',
    product_lprice: 10000,
    user_nickname: 'tester',
  })

  assert.deepEqual(video, {
    id: 9,
    videoUrl: 'https://example.com/video.mp4',
    productId: 3,
    productName: '테스트 제품',
    productPrice: 10000,
    userNickname: 'tester',
    review: null,
    isReviewLoaded: false,
  })
})
