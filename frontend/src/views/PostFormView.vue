<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import client from "../api/client";
import { POST_CATEGORIES } from "../composables/districts";
import PasswordModal from "../components/PasswordModal.vue";

const props = defineProps({
  gu: { type: String, required: true },
  id: { type: String, default: null },
});

const route = useRoute();
const router = useRouter();

const isEdit = computed(() => route.name === "post-edit");

const category = ref(POST_CATEGORIES[0]);
const nickname = ref("");
const title = ref("");
const content = ref("");
const password = ref("");
const loading = ref(false);
const errorMsg = ref("");

// 수정 모드에서는 비밀번호를 먼저 확인해야 폼이 열린다.
const verifying = ref(false);
const verifiedPassword = ref("");
const passwordModalRef = ref(null);

async function loadForEdit() {
  const { data } = await client.get(`/api/boards/${props.id}`);
  title.value = data.title;
  content.value = data.content;
}

async function handleVerify(pw) {
  try {
    await client.post(`/api/boards/${props.id}/verify`, { board_password: pw });
    verifiedPassword.value = pw;
    verifying.value = false;
    await loadForEdit();
  } catch (e) {
    passwordModalRef.value?.showError("비밀번호가 일치하지 않습니다.");
  }
}

async function submit() {
  if (!title.value.trim() || !content.value.trim()) {
    errorMsg.value = "제목과 내용을 모두 입력해주세요.";
    return;
  }
  if (!isEdit.value && password.value.length < 4) {
    errorMsg.value = "비밀번호는 4자 이상 입력해주세요.";
    return;
  }

  loading.value = true;
  errorMsg.value = "";
  try {
    if (isEdit.value) {
      await client.put(`/api/boards/${props.id}`, {
        title: title.value,
        content: content.value,
        board_password: verifiedPassword.value,
      });
      router.push({ name: "post-detail", params: { gu: props.gu, id: props.id } });
    } else {
      const { data } = await client.post("/api/boards", {
        gu: props.gu,
        title: title.value,
        content: content.value,
        board_password: password.value,
        writer: nickname.value.trim() || "익명",
        category: category.value, // 카테고리 누락된 바인딩 보완
      });
      router.push({ name: "post-detail", params: { gu: props.gu, id: data.board_id } });
    }
  } catch (e) {
    errorMsg.value = "저장에 실패했어요. 잠시 후 다시 시도해주세요.";
  } finally {
    loading.value = false;
  }
}

function cancel() {
  router.back();
}

onMounted(() => {
  if (isEdit.value) {
    verifying.value = true;
  }
});
</script>

<template>
  <main class="form-page animate-fade-in">
    <div class="container container-sm">
      <h1 class="page-title">{{ isEdit ? "✍️ 이야기 수정" : "🌱 새로운 이야기 작성" }}</h1>

      <div v-if="!verifying" class="card form-card">
        <!-- 닉네임 · 비밀번호 -->
        <div v-if="!isEdit" class="id-row">
          <div class="field id-field">
            <label for="nickname">닉네임</label>
            <input
              id="nickname"
              v-model="nickname"
              type="text"
              maxlength="12"
              placeholder="익명"
            />
          </div>
          <div class="field id-field">
            <label for="password">비밀번호</label>
            <input
              id="password"
              v-model="password"
              type="password"
              placeholder="4자 이상 입력"
            />
          </div>
        </div>
       
        <!-- 제목 -->
        <div class="field">
          <label for="title">제목</label>
          <input
            id="title"
            v-model="title"
            type="text"
            maxlength="100"
            placeholder="동네 사람들과 나눌 따뜻한 제목을 입력해 주세요."
          />
        </div>

        <!-- 내용 -->
        <div class="field">
          <label for="content">내용</label>
          <textarea 
            id="content" 
            v-model="content" 
            rows="10" 
            placeholder="비방, 비난 없는 따뜻한 대전의 이야기를 채워주세요."
          ></textarea>
        </div>

        <div class="form-footer">
          <p v-if="!isEdit" class="hint">
            ※ 비밀번호 분실 시 글을 수정하거나 삭제하기 어렵습니다.
          </p>
          <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
        </div>

        <!-- 하단 액션 버튼 그룹 -->
        <div class="actions">
          <button class="btn btn-ghost" @click="cancel">취소</button>
          <button class="btn btn-primary" :disabled="loading" @click="submit">
            {{ loading ? "저장 중…" : (isEdit ? "수정 완료" : "올리기 🌱") }}
          </button>
        </div>
      </div>
    </div>

    <!-- 수정 모달 로직 적용 -->
    <PasswordModal
      v-if="verifying"
      ref="passwordModalRef"
      title="게시글을 수정하려면 비밀번호를 입력해주세요"
      @confirm="handleVerify"
      @cancel="cancel"
    />
  </main>
</template>

<style scoped>
.form-page {
  padding: 48px 0 80px;
  background: var(--bg);
  min-height: calc(100vh - 60px);
}

.container-sm {
  max-width: 680px; /* 🌿 폼 입력 가독성을 위한 슬림 너비 배치 */
}

.page-title {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 800;
  color: var(--forest-900);
  margin-bottom: 24px;
  letter-spacing: -0.01em;
}

.form-card {
  padding: 32px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  box-shadow: var(--shadow-soft);
  display: flex;
  flex-direction: column;
  gap: 24px; /* 구성 요소 간 시각적 여백 확보 */
}

.id-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.id-field {
  margin-bottom: 0;
}

.tag-selection {
  border-top: 1px dashed var(--line);
  border-bottom: 1px dashed var(--line);
  padding: 18px 0;
}

.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 6px;
}

.tag-btn {
  padding: 8px 16px;
  border-radius: 999px;
  border: 1.5px solid var(--line);
  background: var(--surface);
  font-size: var(--text-sm);
  font-weight: 700;
  color: var(--forest-700);
  transition: all 0.25s var(--ease-leaf);
}

.tag-btn:hover {
  border-color: var(--forest-600);
  background: var(--surface-alt);
}

.tag-btn.active {
  background: var(--forest-600);
  color: white;
  border-color: var(--forest-600);
  box-shadow: 0 4px 10px rgba(37, 68, 42, 0.12);
  transform: translateY(-1px);
}

.form-card textarea {
  padding: 12px 16px;
  border: 1.5px solid var(--line);
  border-radius: var(--radius-sm);
  resize: vertical;
  line-height: 1.6;
}

.form-footer {
  margin-top: -8px;
}

.hint {
  font-size: var(--text-xs);
  color: var(--moss-400);
  margin: 0;
  font-weight: 500;
}

.error {
  color: var(--danger);
  font-size: var(--text-sm);
  font-weight: 700;
  margin: 8px 0 0 0;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  border-top: 1px solid var(--line);
  padding-top: 20px;
}

.btn {
  min-width: 90px;
}

/* 진입 페이드인 모션 */
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

@media (max-width: 480px) {
  .id-row {
    grid-template-columns: 1fr;
  }
  .form-card {
    padding: 20px;
  }
}
</style>