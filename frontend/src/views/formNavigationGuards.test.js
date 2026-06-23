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
  assert.match(source, /initialHousingType/)
  assert.match(source, /initialAreaSize/)
  assert.match(source, /housingType\.value !== initialHousingType\.value/)
  assert.match(source, /Number\(areaSize\.value\) !== Number\(initialAreaSize\.value\)/)
  assert.match(source, /window\.confirm/)
  assert.match(source, /isSaved\.value = true/)
  assert.match(source, /route\.query\.mode === 'onboarding'/)
  assert.match(source, /router\.push\(\{ name: isOnboardingMode\.value \? 'Home' : 'MyPage' \}\)/)
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

test('ReviewCreateView predicts category from a separate thumbnail image', async () => {
  const { descriptor, source } = await readView('./ReviewCreateView.vue')
  const template = descriptor.template.content

  assert.match(template, /id="review-thumbnail"/)
  assert.match(template, /accept="image\/jpeg,image\/png"/)
  assert.match(template, /@change="predictCategoryFromThumbnail"/)
  assert.match(source, /predictCategoryFromImage/)
  assert.match(source, /prediction\.service_label/)
  assert.match(source, /category\.ai_label === prediction\.service_label/)
  assert.match(source, /selectedCategory\.value = predictedCategory\.id/)
  assert.match(source, /카테고리를 직접 선택해주세요/)
  assert.match(source, /필요하면 직접 변경할 수 있습니다/)
})

test('ProfileEditView saves nickname through auth state', async () => {
  const { descriptor, source } = await readView('./ProfileEditView.vue')
  const template = descriptor.template.content

  assert.match(template, /@submit\.prevent="saveProfile"/)
  assert.match(source, /updateProfile/)
  assert.match(source, /router\.push\('\/mypage'\)/)
  assert.doesNotMatch(source, /console\.log/)
  assert.doesNotMatch(source, /프로필 저장 API 연결 전/)
})
