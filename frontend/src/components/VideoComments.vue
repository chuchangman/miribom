<template>
  <section class="comments">
    <header class="comments-header">
      <h3>댓글</h3>
      <button type="button" :disabled="isLoading" @click="loadComments">
        새로고침
      </button>
    </header>

    <form v-if="isLogin" class="comment-form" @submit.prevent="submitComment">
      <textarea
        v-model="newComment"
        maxlength="500"
        placeholder="댓글을 입력해주세요."
      ></textarea>
      <button type="submit" :disabled="isSubmitting || !newComment.trim()">
        {{ isSubmitting ? '작성 중...' : '댓글 작성' }}
      </button>
    </form>
    <p v-else class="login-guide">
      댓글을 작성하려면 <RouterLink to="/login">로그인</RouterLink>이 필요합니다.
    </p>

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
  </section>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
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
  },
)

onMounted(loadComments)
</script>

<style scoped>
.comments {
  margin-top: 20px;
  border: 1px solid #dbe4f0;
  border-radius: 14px;
  background-color: #fff;
  padding: 14px;
}

.comments-header,
.comment-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.comments-header {
  justify-content: space-between;
}

.comments h3 {
  margin: 0;
}

.comment-form,
.comment-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.comment-form textarea,
.comment-item textarea {
  width: 100%;
  min-height: 72px;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 10px;
  resize: vertical;
}

.comment-form button,
.comments-header button,
.comment-actions button,
.load-more-comments {
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background-color: #f8fafc;
  padding: 7px 10px;
  cursor: pointer;
}

.comment-form button:disabled,
.comments-header button:disabled,
.comment-actions button:disabled,
.load-more-comments:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.login-guide a {
  color: #2563eb;
  font-weight: 700;
}

.error-message {
  color: red;
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  list-style: none;
  margin: 14px 0 0;
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
