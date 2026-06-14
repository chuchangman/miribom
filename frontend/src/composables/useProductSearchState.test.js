import assert from 'node:assert/strict'
import test from 'node:test'
import { useProductSearchState } from './useProductSearchState.js'

test('product search state restores only the matching search URL', () => {
  const { clearSearchState, restoreSearchState, saveSearchState } = useProductSearchState()
  clearSearchState()

  saveSearchState({
    routeKey: '/products?category=4',
    products: [{ id: '1' }],
    nextOffset: 40,
    hasNext: true,
    scrollY: 1200,
  })

  assert.deepEqual(restoreSearchState('/products?category=4'), {
    products: [{ id: '1' }],
    nextOffset: 40,
    hasNext: true,
    scrollY: 1200,
  })
  assert.equal(restoreSearchState('/products?category=2'), null)
})
