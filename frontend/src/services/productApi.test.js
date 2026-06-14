import assert from 'node:assert/strict'
import test from 'node:test'

test('product service loads categories, searches products, and loads product details', async () => {
  const productApi = await import('./productApi.js')
  const originalFetch = globalThis.fetch
  const calls = []

  globalThis.fetch = async (url) => {
    calls.push(url)

    return new Response(JSON.stringify([]), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  }

  try {
    await productApi.fetchProductCategories()
    await productApi.fetchProducts({ query: '삼성 TV', categoryId: 2, limit: 40, offset: 80 })
    await productApi.fetchProductDetail(15)

    assert.deepEqual(calls, [
      'http://localhost:8000/api/products/categories/',
      'http://localhost:8000/api/products/?q=%EC%82%BC%EC%84%B1+TV&category=2&limit=40&offset=80',
      'http://localhost:8000/api/products/15/',
    ])
  } finally {
    globalThis.fetch = originalFetch
  }
})
