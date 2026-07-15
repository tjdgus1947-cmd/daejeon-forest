<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
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
const showDeleteModal = ref(false);
const deleteModalRef = ref(null);

async function load() {
  loading.value = true;
  const { data } = await client.get(`/api/posts/${props.id}`);
  post.value = data;
  loading.value = false;
}

function goEdit() {
  router.push({ name: "post-edit", params: { gu: props.gu, id: props.id } });
}

async function confirmDelete(password) {
  try {
    await client.delete(`/api/posts/${props.id}`, { data: { password } });
    router.push({ name: "district", params: { gu: props.gu } });
  } catch (e) {
    deleteModalRef.value?.showError("비밀번호가 일치하지 않습니다.");
  }
}

async function submitComment() {
  const text = commentText.value.trim();
  if (!text) return;
  await client.post(`/api/posts/${props.id}/comments`, {
    content: text,
    nickname: commentNickname.value.trim() || "익명",
  });
  commentText.value = "";
  await load();
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

      <article class="card post-card">
        <header>
          <span class="category-tag">{{ post.category }}</span>
          <h1>{{ post.title }}</h1>
          <div class="meta">
            <span>{{ post.nickname }}</span>
            <span>{{ formatDate(post.created_at) }}</span>
            <span>조회 {{ post.views }}</span>
          </div>
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
          <li v-for="c in post.comments" :key="c.id" class="comment">
            <strong>{{ c.nickname }}</strong>
            <span>{{ c.content }}</span>
            <time>{{ formatDate(c.created_at) }}</time>
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
  gap: 8px;
  align-items: baseline;
  font-size: var(--text-sm);
  border-bottom: 1px solid var(--line);
  padding-bottom: 12px;
}

.comment strong {
  color: var(--forest-700);
}

.comment time {
  margin-left: auto;
  font-size: var(--text-xs);
  color: var(--moss-400);
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

.comment-text {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
}
</style>
