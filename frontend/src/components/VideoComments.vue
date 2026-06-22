<template>
  <section class="comments">
    <header class="comments-header">
      <h3>댓글</h3>
    </header>

    <div class="comments-body">
      <p v-if="isLoading">댓글을 불러오는 중입니다.</p>
      <p v-else-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      <p v-else-if="comments.length === 0">아직 댓글이 없습니다.</p>

      <ul v-else class="comment-list">
        <li v-for="comment in comments" :key="comment.id" class="comment-item">
          <div class="comment-meta">
            <strong>{{ comment.user_nickname }}</strong>
            <span>{{ formatDate(comment.created_at) }}</span>
          </div>

          <template v-if="editingCommentId === comment.id">
            <textarea v-model="editingContent" maxlength="500"></textarea>
            <div class="comment-actions">
              <button
                type="button"
                :disabled="pendingCommentId === comment.id || !editingContent.trim()"
                @click="saveEdit(comment)"
              >
                저장
              </button>
              <button type="button" @click="cancelEdit">취소</button>
            </div>
          </template>

          <template v-else>
            <p>{{ comment.content }}</p>
            <div v-if="isMyComment(comment)" class="comment-actions">
              <button type="button" @click="startEdit(comment)">수정</button>
              <button
                type="button"
                :disabled="pendingCommentId === comment.id"
                @click="removeComment(comment)"
              >
                삭제
              </button>
            </div>
          </template>
        </li>
      </ul>
      <button
        v-if="hasMoreComments"
        type="button"
        class="load-more-comments"
        :disabled="isLoadingMore"
        @click="loadMoreComments"
      >
        {{ isLoadingMore ? '불러오는 중...' : '댓글 더보기' }}
      </button>
    </div>

    <form v-if="isLogin" class="comment-form" @submit.prevent="submitComment">
      <textarea
        ref="commentInput"
        v-model="newComment"
        rows="1"
        maxlength="500"
        placeholder="댓글을 입력해주세요."
        @input="resizeCommentInput"
      ></textarea>
      <button type="submit" :disabled="isSubmitting || !newComment.trim()">
        {{ isSubmitting ? '작성 중...' : '작성' }}
      </button>
    </form>
    <p v-else class="login-guide">
      댓글을 작성하려면 <RouterLink to="/login">로그인</RouterLink>이 필요합니다.
    </p>
  </section>
</template>

<script setup>
import { nextTick, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import {
  createVideoComment,
  deleteVideoComment,
  fetchVideoComments,
  updateVideoComment,
} from '@/services/videoApi.js'

const props = defineProps({
  videoId: {
    type: Number,
    required: true,
  },
})

const { isLogin, user } = useAuth()
const comments = ref([])
const isLoading = ref(false)
const isLoadingMore = ref(false)
const hasMoreComments = ref(true)
const isSubmitting = ref(false)
const errorMessage = ref('')
const newComment = ref('')
const commentInput = ref(null)
const editingCommentId = ref(null)
const editingContent = ref('')
const pendingCommentId = ref(null)

const loadComments = async ({ cursor = null, append = false } = {}) => {
  if (!props.videoId) {
    comments.value = []
    hasMoreComments.value = false
    return
  }

  if (append) {
    isLoadingMore.value = true
  } else {
    isLoading.value = true
  }
  errorMessage.value = ''

  try {
    const commentItems = await fetchVideoComments(props.videoId, { cursor })
    comments.value = append ? [...comments.value, ...commentItems] : commentItems
    hasMoreComments.value = commentItems.length === 20
  } catch (error) {
    errorMessage.value = error.message || '댓글을 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
    isLoadingMore.value = false
  }
}

const loadMoreComments = async () => {
  if (!hasMoreComments.value || isLoadingMore.value) {
    return
  }

  await loadComments({
    cursor: comments.value.at(-1)?.id,
    append: true,
  })
}

const resizeCommentInput = () => {
  const textarea = commentInput.value
  if (!textarea) {
    return
  }

  textarea.style.height = 'auto'
  textarea.style.height = `${Math.min(textarea.scrollHeight, 112)}px`
}

const submitComment = async () => {
  const content = newComment.value.trim()
  if (!content || isSubmitting.value) {
    return
  }

  isSubmitting.value = true
  errorMessage.value = ''

  try {
    const comment = await createVideoComment(props.videoId, content)
    comments.value = [comment, ...comments.value]
    newComment.value = ''
    await nextTick()
    resizeCommentInput()
  } catch (error) {
    errorMessage.value = error.message || '댓글을 작성하지 못했습니다.'
  } finally {
    isSubmitting.value = false
  }
}

const isMyComment = (comment) => {
  return isLogin.value && user.value?.id === comment.user_id
}

const startEdit = (comment) => {
  editingCommentId.value = comment.id
  editingContent.value = comment.content
}

const cancelEdit = () => {
  editingCommentId.value = null
  editingContent.value = ''
}

const saveEdit = async (comment) => {
  const content = editingContent.value.trim()
  if (!content || pendingCommentId.value !== null) {
    return
  }

  pendingCommentId.value = comment.id
  errorMessage.value = ''

  try {
    const updatedComment = await updateVideoComment(props.videoId, comment.id, content)
    Object.assign(comment, updatedComment)
    cancelEdit()
  } catch (error) {
    errorMessage.value = error.message || '댓글을 수정하지 못했습니다.'
  } finally {
    pendingCommentId.value = null
  }
}

const removeComment = async (comment) => {
  if (pendingCommentId.value !== null) {
    return
  }

  pendingCommentId.value = comment.id
  errorMessage.value = ''

  try {
    await deleteVideoComment(props.videoId, comment.id)
    comments.value = comments.value.filter((item) => item.id !== comment.id)
  } catch (error) {
    errorMessage.value = error.message || '댓글을 삭제하지 못했습니다.'
  } finally {
    pendingCommentId.value = null
  }
}

const formatDate = (dateText) => {
  if (!dateText) {
    return ''
  }

  return new Date(dateText).toLocaleString()
}

watch(
  () => props.videoId,
  () => {
    newComment.value = ''
    cancelEdit()
    loadComments()
    nextTick(resizeCommentInput)
  },
)

watch(newComment, () => {
  nextTick(resizeCommentInput)
})

onMounted(() => {
  loadComments()
  nextTick(resizeCommentInput)
})
</script>

<style scoped>
.comments {
  flex: 1;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #fff;
}

.comments-header,
.comment-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.comments-header {
  flex-shrink: 0;
  justify-content: space-between;
  padding-bottom: 8px;
}

.comments h3 {
  margin: 0;
}

.comments-body {
  flex: 1 1 0;
  min-height: 0;
  overflow-y: auto;
  padding: 8px 2px 12px;
}

.comment-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.comment-item textarea {
  width: 100%;
  min-height: 72px;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 10px;
  resize: vertical;
}

.comment-form button,
.comment-actions button,
.load-more-comments {
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background-color: #f8fafc;
  padding: 7px 10px;
  cursor: pointer;
}

.comment-form button:disabled,
.comment-actions button:disabled,
.load-more-comments:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.comment-form {
  flex-shrink: 0;
  display: flex;
  align-items: flex-end;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
}

.comment-form textarea {
  flex: 1;
  min-height: 42px;
  max-height: 112px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 11px 14px;
  resize: none;
  overflow-y: auto;
  line-height: 1.4;
}

.comment-form button {
  min-width: 54px;
  min-height: 42px;
  border-radius: 8px;
  background-color: var(--color-primary);
  color: #fff;
  font-weight: 800;
}

.login-guide a {
  color: #2563eb;
  font-weight: 700;
}

.login-guide {
  flex-shrink: 0;
  margin: 12px 0 0;
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
}

.error-message {
  color: red;
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  list-style: none;
  margin: 0;
  padding: 0;
}

.comment-item {
  border-top: 1px solid #e5e7eb;
  padding-top: 12px;
}

.comment-meta {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: #64748b;
  font-size: 0.9rem;
}

.comment-meta strong {
  color: #0f172a;
}

.comment-item p {
  margin: 0;
  line-height: 1.5;
}

.load-more-comments {
  display: block;
  margin: 14px auto 0;
}
</style>
