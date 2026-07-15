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
  <main class="form-page">
    <div class="container">
      <h1>{{ isEdit ? "게시글 수정" : "게시글 작성" }}</h1>

      <div v-if="!verifying" class="card form-card">
        <!-- 닉네임 · 비밀번호: 새 글 작성 시에만 입력 (수정은 원 작성자 정보 유지) -->
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
              placeholder="수정·삭제 확인용"
            />
          </div>
        </div>

        <!-- 말머리 -->
        <div v-if="!isEdit" class="field">
          <label>말머리</label>
          <div class="tag-group">
            <button
              v-for="cat in POST_CATEGORIES"
              :key="cat"
              type="button"
              class="tag-btn"
              :class="{ active: category === cat }"
              @click="category = cat"
            >
              {{ cat }}
            </button>
          </div>
        </div>

        <div class="field">
          <label for="title">제목</label>
          <input
            id="title"
            v-model="title"
            type="text"
            maxlength="100"
            placeholder="제목을 입력해 주세요."
          />
        </div>

        <div class="field">
          <label for="content">내용</label>
          <textarea id="content" v-model="content" rows="10"></textarea>
        </div>

        <p v-if="!isEdit" class="hint">
          ※ 쉬운 비밀번호를 입력하면 타인이 글을 수정·삭제할 수 있어요.
        </p>
        <p v-if="errorMsg" class="error">{{ errorMsg }}</p>

        <div class="actions">
          <button class="btn btn-ghost" @click="cancel">취소</button>
          <button class="btn btn-primary" :disabled="loading" @click="submit">
            {{ loading ? "저장 중…" : "등록" }}
          </button>
        </div>
      </div>
    </div>

    <PasswordModal
      v-if="verifying"
      ref="passwordModalRef"
      title="수정하려면 비밀번호를 확인해주세요"
      @confirm="handleVerify"
      @cancel="cancel"
    />
  </main>
</template>

<style scoped>
.form-page {
  padding: 32px 0 64px;
}

.form-card {
  padding: 24px;
}

.id-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.id-field {
  margin-bottom: 0;
}

.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-btn {
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: var(--surface);
  font-size: var(--text-sm);
  color: var(--forest-700);
}

.tag-btn.active {
  background: var(--forest-600);
  color: white;
  border-color: var(--forest-600);
}

.form-card textarea {
  padding: 10px 14px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  resize: vertical;
}

.hint {
  font-size: var(--text-xs);
  color: var(--moss-400);
  margin: 0 0 12px;
}

.error {
  color: var(--danger);
  font-size: var(--text-sm);
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 12px;
}

@media (max-width: 480px) {
  .id-row {
    grid-template-columns: 1fr;
  }
}
</style>
