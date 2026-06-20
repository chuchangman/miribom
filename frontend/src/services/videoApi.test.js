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

test('video service calls like and comment APIs', async () => {
  const videoApi = await import('./videoApi.js')
  const originalFetch = globalThis.fetch
  const calls = []

  globalThis.fetch = async (url, options = {}) => {
    calls.push({ url, options })

    if (calls.length === 1) {
      return new Response(JSON.stringify([{ id: 9 }]), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    if (calls.length === 2) {
      return new Response(JSON.stringify({ liked: true, like_count: 3 }), {
        status: 201,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    if (calls.length === 3) {
      return new Response(JSON.stringify([{ id: 11, content: '댓글' }]), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    if (calls.length === 4) {
      return new Response(JSON.stringify({ id: 12, content: '새 댓글' }), {
        status: 201,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    if (calls.length === 5) {
      return new Response(JSON.stringify({ id: 12, content: '수정 댓글' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    return new Response(null, { status: 204 })
  }

  try {
    const likedVideos = await videoApi.fetchLikedVideos({ cursor: 7 })
    const likeResult = await videoApi.toggleVideoLike(9)
    const comments = await videoApi.fetchVideoComments(9, { cursor: 5 })
    const createdComment = await videoApi.createVideoComment(9, '새 댓글')
    const updatedComment = await videoApi.updateVideoComment(9, 12, '수정 댓글')
    const deletedComment = await videoApi.deleteVideoComment(9, 12)

    assert.equal(likedVideos[0].id, 9)
    assert.equal(likeResult.liked, true)
    assert.equal(comments[0].id, 11)
    assert.equal(createdComment.content, '새 댓글')
    assert.equal(updatedComment.content, '수정 댓글')
    assert.equal(deletedComment, null)
    assert.deepEqual(
      calls.map(({ url }) => url),
      [
        'http://localhost:8000/api/videos/liked/?cursor=7',
        'http://localhost:8000/api/videos/9/like/',
        'http://localhost:8000/api/videos/9/comments/?cursor=5',
        'http://localhost:8000/api/videos/9/comments/',
        'http://localhost:8000/api/videos/9/comments/12/',
        'http://localhost:8000/api/videos/9/comments/12/',
      ],
    )
    assert.equal(calls[1].options.method, 'POST')
    assert.equal(calls[3].options.method, 'POST')
    assert.equal(calls[3].options.body, JSON.stringify({ content: '새 댓글' }))
    assert.equal(calls[4].options.method, 'PATCH')
    assert.equal(calls[4].options.body, JSON.stringify({ content: '수정 댓글' }))
    assert.equal(calls[5].options.method, 'DELETE')
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
    product_image: 'https://example.com/product.jpg',
    product_lprice: 10000,
    user_nickname: 'tester',
    like_count: 2,
  })

  assert.deepEqual(video, {
    id: 9,
    videoUrl: 'https://example.com/video.mp4',
    productId: 3,
    productName: '테스트 제품',
    productImage: 'https://example.com/product.jpg',
    productPrice: 10000,
    userNickname: 'tester',
    likeCount: 2,
    isLiked: false,
    review: null,
    isReviewLoaded: false,
  })
})
