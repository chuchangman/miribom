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

test('BaseButton exposes reusable variants, sizes, and loading state', async () => {
  const { descriptor, source } = await readComponent('./BaseButton.vue')

  assert.match(descriptor.template.content, /<button/)
  assert.match(source, /variant/)
  assert.match(source, /size/)
  assert.match(source, /loading/)
  assert.match(source, /disabled/)
  assert.match(descriptor.template.content, /v-if="loading">\{\{ loadingLabel \}\}/)
})

test('BaseCard supports padding and interactive presentation', async () => {
  const { descriptor, source } = await readComponent('./BaseCard.vue')

  assert.match(descriptor.template.content, /<component/)
  assert.match(source, /padding/)
  assert.match(source, /interactive/)
})

test('BaseInput supports labels, validation messages, and v-model updates', async () => {
  const { descriptor, source } = await readComponent('./BaseInput.vue')

  assert.match(descriptor.template.content, /<input/)
  assert.match(source, /modelValue/)
  assert.match(source, /errorMessage/)
  assert.match(source, /update:modelValue/)
})
