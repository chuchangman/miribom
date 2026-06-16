import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { parse } from '@vue/compiler-sfc'

const readComponent = async (filename) => {
  const source = await readFile(new URL(filename, import.meta.url), 'utf8')
  const { descriptor, errors } = parse(source, { filename })

  assert.deepEqual(errors, [])
  return { descriptor, source }
}

test('App keeps the sidebar beside the page and renders actions inside the page header', async () => {
  const { descriptor } = await readComponent('../App.vue')
  const template = descriptor.template.content

  assert.match(template, /class="app-layout"/)
  assert.match(template, /<AppSidebar[\s\S]*class="page-content"[\s\S]*class="page-header"/)
})

test('AppHeaderActions only provides authentication navigation', async () => {
  const { descriptor, source } = await readComponent('./AppHeaderActions.vue')

  assert.doesNotMatch(descriptor.template.content, /class="global-search"/)
  assert.match(descriptor.template.content, /class="login-actions"/)
  assert.match(descriptor.template.content, /class="guest-actions"/)
  assert.doesNotMatch(source, /miribomLogo/)
})

test('AppSidebar selects a category only when its query matches the current route', async () => {
  const { descriptor, source } = await readComponent('./AppSidebar.vue')

  assert.match(descriptor.template.content, /isCategorySelected\(category\.id\)/)
  assert.match(source, /useRoute/)
  assert.match(source, /String\(route\.query\.category\) === String\(categoryId\)/)
  assert.match(source, /var\(--color-primary-light\)/)
})

test('AppSidebar keeps the active text color while hovering the selected link', async () => {
  const { source } = await readComponent('./AppSidebar.vue')

  assert.match(
    source,
    /\.sidebar-link--active:hover\s*\{[\s\S]*color:\s*var\(--color-primary-600\)/,
  )
})

test('AppSidebar reloads when the current sidebar destination is selected again', async () => {
  const { descriptor, source } = await readComponent('./AppSidebar.vue')

  assert.match(descriptor.template.content, /@click="handleNavigationClick/)
  assert.match(source, /route\.fullPath === router\.resolve\(target\)\.fullPath/)
  assert.match(source, /confirmUnsavedNavigation\(\)/)
  assert.match(source, /window\.location\.reload\(\)/)
})
