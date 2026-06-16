import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { parse } from '@vue/compiler-sfc'

const readView = async (filename) => {
  const source = await readFile(new URL(filename, import.meta.url), 'utf8')
  const { descriptor, errors } = parse(source, { filename })

  assert.deepEqual(errors, [])
  return { descriptor, source }
}

test('LivingProfileView warns only after the user changes the form', async () => {
  const { source } = await readView('./LivingProfileView.vue')

  assert.match(source, /onBeforeRouteLeave/)
  assert.match(source, /housingType\.value \|\| Number\(areaSize\.value\) !== 1/)
  assert.match(source, /window\.confirm/)
  assert.match(source, /isSaved\.value = true/)
})

test('ReviewCreateView warns for entered review data and clears the warning after success', async () => {
  const { descriptor, source } = await readView('./ReviewCreateView.vue')

  assert.match(descriptor.template.content, /@pointerdown\.prevent="handleSelect\(product\)"/)
  assert.match(
    source,
    /const handleProductSearchInput = \(\) => \{(?:(?!const loadProductSuggestions)[\s\S])*\+\+productSearchRequestId/,
  )
  const productSearchInputBeforeEmptyCheck = source.match(
    /const handleProductSearchInput = \(\) => \{[\s\S]*?(?= {2}if \(!productSearchQuery\.value\.trim\(\)\))/,
  )?.[0]
  assert.ok(productSearchInputBeforeEmptyCheck)
  assert.doesNotMatch(productSearchInputBeforeEmptyCheck, /productSuggestions\.value = \[\]/)
  assert.match(source, /clearTimeout\(productSearchTimer\)/)
  assert.match(source, /\+\+productSearchRequestId/)
  assert.match(source, /useUnsavedChanges/)
  assert.match(source, /watch\(\s*hasUnsavedChanges,[\s\S]*setHasUnsavedChanges\(value\)/)
  assert.match(source, /onBeforeRouteLeave/)
  assert.match(source, /inputVideo\.value/)
  assert.match(source, /productSearchQuery\.value\.trim\(\)/)
  assert.match(source, /reviewContent\.value\.trim\(\)/)
  assert.match(source, /window\.confirm/)
  assert.match(source, /isSubmitted\.value = true/)
})

test('ReviewCreateView supports keyboard product selection in a five-row scroll area', async () => {
  const { descriptor, source } = await readView('./ReviewCreateView.vue')
  const template = descriptor.template.content

  assert.doesNotMatch(template, /@compositionstart=/)
  assert.doesNotMatch(template, /@compositionend=/)
  assert.match(template, /@keydown\.down\.prevent="moveProductHighlight\(1\)"/)
  assert.match(template, /@keydown\.up\.prevent="moveProductHighlight\(-1\)"/)
  assert.match(template, /@keydown\.enter\.prevent="selectHighlightedProduct"/)
  assert.match(template, /@keydown\.esc="closeProductSuggestions"/)
  assert.match(template, /product-suggestion--active/)
  assert.match(source, /scrollIntoView/)
  assert.match(source, /max-height:\s*210px/)
  assert.match(source, /overflow-y:\s*auto/)
  assert.doesNotMatch(source, /console\.debug/)
})
