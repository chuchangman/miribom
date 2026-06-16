import assert from 'node:assert/strict'
import test from 'node:test'

test('bookmark service loads, creates, and deletes bookmarks through the API', async () => {
  const bookmarkApi = await import('./bookmarkApi.js')
  const originalFetch = globalThis.fetch
  const calls = []

  globalThis.fetch = async (url, options = {}) => {
    calls.push({ url, options })

    if (calls.length === 1) {
      return new Response(JSON.stringify([{ id: 7, product: { id: 3 } }]), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    if (calls.length === 2) {
      return new Response(JSON.stringify({ id: 8, product: { id: 4 } }), {
        status: 201,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    return new Response(null, { status: 204 })
  }

  try {
    const bookmarks = await bookmarkApi.fetchBookmarks()
    const createdBookmark = await bookmarkApi.createBookmark(4)
    await bookmarkApi.deleteBookmark(7)

    assert.equal(bookmarks[0].id, 7)
    assert.equal(createdBookmark.id, 8)
    assert.deepEqual(
      calls.map(({ url }) => url),
      [
        'http://localhost:8000/api/products/bookmarks/',
        'http://localhost:8000/api/products/bookmarks/',
        'http://localhost:8000/api/products/bookmarks/7/',
      ],
    )
    assert.equal(calls[1].options.method, 'POST')
    assert.equal(calls[1].options.headers['Content-Type'], 'application/json')
    assert.equal(calls[1].options.body, JSON.stringify({ product_id: 4 }))
    assert.equal(calls[2].options.method, 'DELETE')
  } finally {
    globalThis.fetch = originalFetch
  }
})
