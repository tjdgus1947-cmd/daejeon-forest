<script setup>
import { ref } from "vue";

// 💡 부모 컴포넌트로부터 title을 props로 안전하게 전달받습니다.
const props = defineProps({
  title: {
    type: String,
    default: "비밀번호를 입력해주세요"
  }
});

const emit = defineEmits(["confirm", "cancel"]);
const password = ref("");
const errorMessage = ref("");

function handleConfirm() {
  const pass = password.value.trim();
  if (!pass) {
    errorMessage.value = "비밀번호를 입력해주세요.";
    return;
  }
  emit("confirm", pass);
  password.value = ""; // 입력값 초기화
}

function handleCancel() {
  emit("cancel");
  password.value = "";
  errorMessage.value = "";
}

// 💡 부모 컴포넌트(PostDetailView)에서 에러가 발생했을 때 호출할 수 있는 함수 노출
function showError(msg) {
  errorMessage.value = msg;
}

defineExpose({
  showError
});
</script>

<template>
  <div class="modal-backdrop" @click.self="handleCancel">
    <div class="modal-content">
      <h3 class="modal-title">{{ props.title }}</h3>
      
      <input
        v-model="password"
        type="password"
        class="modal-input"
        :placeholder="props.title.includes('수정') ? '비밀번호 입력' : '비밀번호 입력'"
        @keyup.enter="handleConfirm"
        autofocus
      />

      <p v-if="errorMessage" class="error-msg">{{ errorMessage }}</p>
      
      <div class="modal-actions">
        <button class="btn btn-ghost" @click="handleCancel">취소</button>
        <button class="btn btn-primary" @click="handleConfirm">확인</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 24px;
  border-radius: 16px;
  width: 320px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
  text-align: center;
}

.modal-title {
  font-size: 16px;
  font-weight: 700;
  color: #2f5233;
  margin-bottom: 16px;
  line-height: 1.4;
}

.modal-input {
  width: 100%;
  padding: 12px;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 12px;
  box-sizing: border-box;
  text-align: center;
  font-size: 14px;
  transition: border-color 0.15s;
}

.modal-input:focus {
  outline: none;
  border-color: #2f5233;
}

.error-msg {
  color: #ef4444;
  font-size: 12px;
  margin: -4px 0 12px;
  text-align: center;
}

.modal-actions {
  display: flex;
  gap: 8px;
}

.modal-actions button {
  flex: 1;
  padding: 10px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: none;
}

.btn-ghost {
  background: #f3f4f6;
  color: #4b5563;
}

.btn-primary {
  background: #2f5233;
  color: white;
}
</style>