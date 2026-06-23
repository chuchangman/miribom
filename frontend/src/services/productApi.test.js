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

test('product service loads recommendation options and requests recommendations', async () => {
  const productApi = await import('./productApi.js')
  const originalFetch = globalThis.fetch
  const calls = []

  globalThis.fetch = async (url, options = {}) => {
    calls.push({
      url,
      method: options.method || 'GET',
      body: options.body ? JSON.parse(options.body) : null,
    })

    return new Response(JSON.stringify({ results: [] }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  }

  try {
    await productApi.fetchRecommendationOptions()
    await productApi.fetchRecommendationQuestions([1, 3])
    await productApi.fetchProductRecommendations({
      housingType: 'villa',
      areaSize: 9,
      categoryIds: [1, 3],
      budget: '30_to_100',
    })

    assert.deepEqual(calls, [
      {
        url: 'http://localhost:8000/api/products/recommendations/',
        method: 'GET',
        body: null,
      },
      {
        url: 'http://localhost:8000/api/products/recommendations/questions/?category_ids=1%2C3',
        method: 'GET',
        body: null,
      },
      {
        url: 'http://localhost:8000/api/products/recommendations/',
        method: 'POST',
        body: {
          housing_type: 'villa',
          area_size: 9,
          category_ids: [1, 3],
          budget: '30_to_100',
          category_answers: {},
        },
      },
    ])
  } finally {
    globalThis.fetch = originalFetch
  }
})
