<script setup>
import { ref } from "vue";

const props = defineProps({
  title: { type: String, default: "비밀번호 확인" },
});
const emit = defineEmits(["confirm", "cancel"]);

const password = ref("");
const error = ref("");

function submit() {
  if (!password.value) {
    error.value = "비밀번호를 입력해주세요.";
    return;
  }
  emit("confirm", password.value);
}

defineExpose({
  showError(msg) {
    error.value = msg;
  },
});
</script>

<template>
  <div class="overlay" @click.self="emit('cancel')">
    <div class="modal card">
      <h3>{{ title }}</h3>
      <input
        v-model="password"
        type="password"
        placeholder="수정용 비밀번호 입력"
        autofocus
        @keyup.enter="submit"
      />
      <p v-if="error" class="error">{{ error }}</p>
      <div class="actions">
        <button class="btn btn-ghost" @click="emit('cancel')">취소</button>
        <button class="btn btn-primary" @click="submit">확인</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(22, 40, 28, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.modal {
  width: 320px;
  padding: 24px;
  text-align: center;
}

.modal h3 {
  margin-bottom: 16px;
}

.modal input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  text-align: center;
}

.error {
  color: var(--danger);
  font-size: var(--text-sm);
  margin: 8px 0 0;
}

.actions {
  display: flex;
  gap: 8px;
  margin-top: 20px;
}

.actions .btn {
  flex: 1;
}
</style>
