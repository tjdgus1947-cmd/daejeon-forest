<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import client from "../api/client";
import PasswordModal from "../components/PasswordModal.vue";

const props = defineProps({
  gu: { type: String, required: true },
  id: { type: String, required: true },
});

const router = useRouter();

const post = ref(null);
const loading = ref(true);
const commentNickname = ref("");
const commentText = ref("");
const commentPassword = ref(""); // 💡 댓글 등록용 비밀번호 변수 추가!

const showDeleteModal = ref(false);
const deleteModalRef = ref(null);

// 💡 댓글 수정/삭제용 상태 관리 변수 추가
const activeCommentId = ref(null);         // 현재 작업 중인 댓글 ID
const commentActionType = ref("");         // "edit" | "delete"
const showCommentModal = ref(false);       // 댓글 비밀번호 모달 표시 여부
const commentModalRef = ref(null);
const editingCommentText = ref("");        // 댓글 수정 시 입력 필드 제어용

async function load() {
  loading.value = true;
  const { data } = await client.get(`/api/boards/${props.id}`);
  post.value = data;
  loading.value = false;
}

async function confirmDelete(password) {
  try {
    await client.delete(`/api/boards/${props.id}`, { data: { board_password: password } });
    router.push({ name: "district", params: { gu: props.gu } });
  } catch (e) {
    deleteModalRef.value?.showError("비밀번호가 일치하지 않습니다.");
  }
}

// 💡 댓글 작성 시 비밀번호 유효성 검사 추가 (4자 이상 필수)
async function submitComment() {
  const text = commentText.value.trim();
  const password = commentPassword.value.trim();
  if (!text) return;
  if (!password || password.length < 4) {
    alert("댓글 수정/삭제용 비밀번호를 4자 이상 입력해 주세요!");
    return;
  }
  
  await client.post(`/api/boards/${props.id}/comments`, {
    content: text,
    writer: commentNickname.value.trim() || "익명",
    comment_password: password, // 💡 사용자가 입력한 비밀번호 적용
  });
  
  commentText.value = "";
  commentNickname.value = "";
  commentPassword.value = "";
  await load();
}

const commentModalTitle = ref("");

// 💡 댓글 수정/삭제 버튼 클릭 시 호출
function openCommentAction(commentId, action, currentText = "") {
  activeCommentId.value = commentId;
  commentActionType.value = action;
  
  if (action === "edit") {
    editingCommentText.value = currentText;
    commentModalTitle.value = "수정하려면 댓글 비밀번호를 입력해주세요"; // 💡 수정 클릭 시
  } else if (action === "delete") {
    commentModalTitle.value = "삭제하려면 댓글 비밀번호를 입력해주세요"; // 💡 삭제 클릭 시
  }
  
  showCommentModal.value = true;
}

// 💡 댓글 비밀번호 모달 최종 검증 및 전송
async function handleCommentConfirm(password) {
  try {
    if (commentActionType.value === "edit") {
      const newContent = prompt("수정할 댓글 내용을 입력하세요:", editingCommentText.value);
      if (newContent === null) {
        showCommentModal.value = false;
        return;
      }
      if (!newContent.trim()) {
        alert("내용을 입력해 주세요.");
        return;
      }
      
      await client.put(`/api/boards/${props.id}/comments/${activeCommentId.value}`, {
        content: newContent,
        comment_password: password,
      });
      alert("댓글이 수정되었습니다.");
    } else if (commentActionType.value === "delete") {
      await client.delete(`/api/boards/${props.id}/comments/${activeCommentId.value}`, {
        data: { comment_password: password },
      });
      alert("댓글이 삭제되었습니다.");
    }
    showCommentModal.value = false;
    await load();
  } catch (e) {
    commentModalRef.value?.showError("비밀번호가 일치하지 않습니다.");
  }
}

function formatDate(iso) {
  return iso ? new Date(iso).toLocaleString("ko-KR") : "";
}

onMounted(load);
</script>

<template>
  <main class="detail-page">
    <div class="container" v-if="!loading && post">
      <button class="back-btn" @click="router.push({ name: 'district', params: { gu } })">
        ← 목록으로
      </button>

      <article class="meta">
        <header>
          <span class="meta">
            <span>{{ post.writer }}</span>
            <span>{{ formatDate(post.created_at) }}</span>
            <span>조회 {{ post.view_count }}</span>
          </span>
          <h1>{{ post.title }}</h1>
        </header>

        <p class="content">{{ post.content }}</p>

        <div class="post-actions">
          <button class="btn btn-ghost" @click="goEdit">수정</button>
          <button class="btn btn-danger" @click="showDeleteModal = true">
            삭제
          </button>
        </div>
      </article>

      <section class="comments card">
        <h2>댓글 {{ post.comments.length }}</h2>
        <ul>
          <li v-for="c in post.comments" :key="c.comment_id" class="comment">
            <div class="comment-content-wrap">
              <strong>{{ c.writer }}</strong>
              <span class="comment-body">{{ c.content }}</span>
              <time>{{ formatDate(c.created_at) }}</time>
            </div>
            <div class="comment-actions">
              <button class="action-link" @click="openCommentAction(c.comment_id, 'edit', c.content)">수정</button>
              <button class="action-link delete" @click="openCommentAction(c.comment_id, 'delete')">삭제</button>
            </div>
          </li>
        </ul>

        <div class="comment-form">
          <input
            v-model="commentNickname"
            type="text"
            class="comment-nick"
            placeholder="닉네임"
            maxlength="12"
          />
          <input
            v-model="commentPassword"
            type="password"
            class="comment-pass"
            placeholder="비밀번호(4자 이상)"
            maxlength="20"
          />
          <input
            v-model="commentText"
            type="text"
            class="comment-text"
            placeholder="따뜻한 댓글을 남겨주세요"
            @keyup.enter="submitComment"
          />
          <button class="btn btn-primary" @click="submitComment">등록</button>
        </div>
      </section>
    </div>

    <PasswordModal
      v-if="showDeleteModal"
      ref="deleteModalRef"
      title="삭제하려면 비밀번호를 확인해주세요"
      @confirm="confirmDelete"
      @cancel="showDeleteModal = false"
    />

    <PasswordModal
      v-if="showCommentModal"
      ref="commentModalRef"
      title="댓글 비밀번호를 입력해주세요"
      @confirm="handleCommentConfirm"
      @cancel="showCommentModal = false"
    />
  </main>
</template>

<style scoped>
.detail-page {
  padding: 32px 0 64px;
}

.back-btn {
  background: none;
  border: none;
  color: var(--forest-700);
  font-size: var(--text-sm);
  font-weight: 600;
  margin-bottom: 16px;
  padding: 0;
}

.post-card {
  padding: 28px;
  margin-bottom: 20px;
}

.category-tag {
  display: inline-block;
  font-size: var(--text-xs);
  background: var(--surface-alt);
  color: var(--forest-700);
  padding: 4px 10px;
  border-radius: 999px;
  margin-bottom: 8px;
}

.meta {
  display: flex;
  gap: 12px;
  font-size: var(--text-xs);
  color: var(--moss-400);
  margin-top: 8px;
}

.content {
  white-space: pre-wrap;
  margin-top: 20px;
  line-height: 1.8;
}

.post-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 24px;
}

.comments {
  padding: 24px;
}

.comments ul {
  list-style: none;
  padding: 0;
  margin: 16px 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comment {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--line);
  padding-bottom: 12px;
}

.comment-content-wrap {
  display: flex;
  gap: 12px;
  align-items: baseline;
  font-size: var(--text-sm);
  flex: 1;
}

.comment-body {
  word-break: break-all;
}

.comment strong {
  color: var(--forest-700);
}

.comment time {
  margin-left: auto;
  font-size: var(--text-xs);
  color: var(--moss-400);
  padding-right: 16px;
}

/* 💡 댓글 조작 스타일 추가 */
.comment-actions {
  display: flex;
  gap: 8px;
}

.action-link {
  background: none;
  border: none;
  color: var(--moss-400);
  font-size: var(--text-xs);
  cursor: pointer;
  padding: 2px 4px;
}

.action-link:hover {
  color: var(--forest-700);
  text-decoration: underline;
}

.action-link.delete:hover {
  color: var(--danger);
}

.comment-form {
  display: flex;
  gap: 8px;
}

.comment-nick {
  width: 96px;
  flex-shrink: 0;
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
}

/* 💡 비밀번호 인풋 스타일 추가 */
.comment-pass {
  width: 124px;
  flex-shrink: 0;
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
}

.comment-text {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
}
</style>