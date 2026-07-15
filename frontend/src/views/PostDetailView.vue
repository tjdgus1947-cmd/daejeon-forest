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
  <main class="detail-page animate-fade-in">
    <div class="container container-sm" v-if="!loading && post">
      <button class="back-btn" @click="router.push({ name: 'district', params: { gu } })">
        ← {{ gu }} 이야기 목록으로
      </button>

      <article class="card post-card">
        <header class="post-header">
          <div class="meta">
            <span class="writer-tag">👤 {{ post.writer }}</span>
            <span class="date-tag">{{ formatDate(post.created_at) }}</span>
            <span class="view-tag">👀 조회 {{ post.view_count }}</span>
          </div>
          <h1 class="post-title">{{ post.title }}</h1>
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
        <div class="comments-header">
          <h2 class="comments-title">💬 이웃들의 댓글 <span class="count">{{ post.comments.length }}</span></h2>
        </div>
        
        <ul class="comment-list">
          <li v-for="c in post.comments" :key="c.comment_id" class="comment-bubble-item">
            <div class="avatar">🌳</div>
            
            <div class="bubble-content-area">
              <div class="bubble-info">
                <strong class="comment-writer">{{ c.writer }}</strong>
                <time class="comment-time">{{ formatDate(c.created_at) }}</time>
              </div>
              
              <div class="speech-bubble">
                <span class="comment-body">{{ c.content }}</span>
              </div>
              
              <div class="comment-actions">
                <button class="action-link" @click="openCommentAction(c.comment_id, 'edit', c.content)">
                  ✏️ 수정
                </button>
                <button class="action-link delete" @click="openCommentAction(c.comment_id, 'delete')">
                  🗑️ 삭제
                </button>
              </div>
            </div>
          </li>
          
          <li v-if="post.comments.length === 0" class="empty-comments">
            아직 따뜻한 댓글이 없어요. 첫 마디를 건네보세요! 🌱
          </li>
        </ul>

        <div class="comment-form-wrap">
          <div class="comment-meta-inputs">
            <input
              v-model="commentNickname"
              type="text"
              class="comment-input comment-nick"
              placeholder="닉네임"
              maxlength="12"
            />
            <input
              v-model="commentPassword"
              type="password"
              class="comment-input comment-pass"
              placeholder="비밀번호(4자 이상)"
              maxlength="20"
            />
          </div>
          <div class="comment-main-input-row">
            <input
              v-model="commentText"
              type="text"
              class="comment-input comment-text"
              placeholder="따뜻한 이야기를 댓글로 이어가 주세요."
              @keyup.enter="submitComment"
            />
            <button class="btn btn-primary submit-comment-btn" @click="submitComment">댓글 달기 💬</button>
          </div>
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
      :title="commentModalTitle"
      @confirm="handleCommentConfirm"
      @cancel="showCommentModal = false"
    />
  </main>
</template>

<style scoped>
.detail-page {
  padding: 40px 0 80px;
  background: var(--bg);
  min-height: 100vh;
}

.container-sm {
  max-width: 680px;
}

.back-btn {
  background: none;
  border: none;
  color: var(--forest-600);
  font-size: var(--text-sm, 14px);
  font-weight: 700;
  margin-bottom: 20px;
  padding: 0;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.back-btn:hover {
  transform: translateX(-3px);
  color: var(--forest-700);
}

/* 🌿 본문 카드 세련되게 정돈 */
.post-card {
  padding: 32px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft);
  margin-bottom: 24px;
}

.post-header {
  border-bottom: 1px dashed var(--line);
  padding-bottom: 20px;
  margin-bottom: 24px;
}

.post-title {
  font-size: var(--text-2xl, 24px);
  color: var(--forest-900);
  margin: 12px 0 0 0;
  font-weight: 800;
  letter-spacing: -0.02em;
  line-height: 1.35;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: var(--text-xs, 12px);
}

.writer-tag {
  color: var(--forest-700);
  font-weight: 700;
}

.date-tag, .view-tag {
  color: var(--moss-400);
  font-weight: 500;
}

.content {
  color: var(--text-main);
  white-space: pre-wrap;
  font-size: var(--text-base, 16px);
  line-height: 1.8;
  margin: 0;
}

.post-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 32px;
}

/* 🌿 댓글 세션 (메신저 말풍선 테마 UX 개편) */
.comments {
  padding: 32px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft);
}

.comments-header {
  border-bottom: 1.5px solid var(--line);
  padding-bottom: 16px;
  margin-bottom: 24px;
}

.comments-title {
  font-size: var(--text-lg, 18px);
  font-weight: 800;
  color: var(--forest-900);
  margin: 0;
}

.comments-title .count {
  color: var(--forest-600);
  font-size: var(--text-base);
  margin-left: 4px;
}

.comment-list {
  list-style: none;
  padding: 0;
  margin: 0 0 32px 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 💬 말풍선 아이템 스타일 */
.comment-bubble-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--surface-alt);
  border: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
  box-shadow: var(--shadow-soft);
}

.bubble-content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.bubble-info {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.comment-writer {
  font-size: var(--text-sm, 14px);
  color: var(--forest-900);
  font-weight: 700;
}

.comment-time {
  font-size: 10px;
  color: var(--moss-400);
  font-weight: 500;
}

/* 💬 실제 말풍선 영역 */
.speech-bubble {
  background: var(--surface-alt);
  color: var(--text-main);
  padding: 10px 16px;
  border-radius: 0 16px 16px 16px; /* 대화방 스타일의 둥근 테두리 처리 */
  display: inline-block;
  align-self: flex-start; /* 글씨 길이에 맞춤 */
  max-width: 90%;
  border: 1px solid var(--line);
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.comment-body {
  font-size: var(--text-sm, 14px);
  line-height: 1.5;
  word-break: break-all;
  white-space: pre-wrap;
}

/* ⚙️ 댓글 조작 영역 */
.comment-actions {
  display: flex;
  gap: 12px;
  margin-top: 2px;
  padding-left: 4px;
}

.action-link {
  background: none;
  border: none;
  color: var(--moss-400);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s ease;
}

.action-link:hover {
  color: var(--forest-600);
  text-decoration: underline;
}

.action-link.delete:hover {
  color: var(--danger);
}

.empty-comments {
  text-align: center;
  padding: 40px 0;
  font-size: var(--text-sm, 14px);
  color: var(--moss-400);
  font-weight: 500;
  border: 1.5px dashed var(--line);
  border-radius: var(--radius-md);
}

/* 🌿 댓글 등록 카드 폼 디자인 업그레이드 */
.comment-form-wrap {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: var(--surface-alt);
  padding: 18px;
  border-radius: var(--radius-md);
  border: 1px solid var(--line);
}

.comment-input {
  background: var(--surface);
  color: var(--text-main);
  border: 1.5px solid var(--line);
  transition: all 0.25s var(--ease-leaf);
}

.comment-input:focus {
  border-color: var(--forest-600);
  outline: none;
  box-shadow: 0 0 0 3px rgba(44, 92, 50, 0.12);
}

.comment-meta-inputs {
  display: flex;
  gap: 8px;
}

.comment-nick, .comment-pass {
  width: 50%;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  font-size: var(--text-sm, 14px);
}

.comment-main-input-row {
  display: flex;
  gap: 8px;
}

.comment-text {
  flex: 1;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  font-size: var(--text-sm, 14px);
}

.submit-comment-btn {
  white-space: nowrap;
  font-size: var(--text-sm, 14px);
  font-weight: 700;
  padding: 10px 16px;
  border-radius: var(--radius-sm);
}

/* 진입 모션 */
.animate-fade-in {
  animation: fadeIn 0.4s var(--ease-leaf) forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 580px) {
  .comment-main-input-row {
    flex-direction: column;
  }
  .submit-comment-btn {
    width: 100%;
  }
  .speech-bubble {
    max-width: 100%;
  }
}
</style>