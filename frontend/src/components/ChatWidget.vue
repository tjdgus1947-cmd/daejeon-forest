<script setup>
import { ref, nextTick } from "vue";
import client from "../api/client";

const open = ref(false);
const input = ref("");
const sending = ref(false);
const messages = ref([
  {
    role: "assistant",
    content:
      "안녕하세요! 대전의 숲 챗봇이에요 🌲 맛집, 축제 일정, 관광지 추천, 게시글 검색까지 물어보세요.",
  },
]);
const scrollEl = ref(null);

function toggle() {
  open.value = !open.value;
}

async function scrollToBottom() {
  await nextTick();
  if (scrollEl.value) {
    scrollEl.value.scrollTop = scrollEl.value.scrollHeight;
  }
}

async function send() {
  const text = input.value.trim();
  if (!text || sending.value) return;

  messages.value.push({ role: "user", content: text });
  input.value = "";
  sending.value = true;
  scrollToBottom();

  try {
    // 최근 대화 히스토리를 함께 전달해 맥락을 유지 (RFP III-3-다)
    const history = messages.value
      .slice(0, -1)
      .map(({ role, content }) => ({ role, content }));

    const { data } = await client.post("/api/chat", {
      message: text,
      history,
    });
    messages.value.push({ role: "assistant", content: data.reply });
  } catch (e) {
    messages.value.push({
      role: "assistant",
      content: "앗, 답변을 가져오지 못했어요. 잠시 후 다시 시도해주세요.",
    });
  } finally {
    sending.value = false;
    scrollToBottom();
  }
}
</script>

<template>
  <div class="chat-widget">
    <div v-if="open" class="panel card">
      <header class="panel-header">
        <span>대전의 숲 챗봇</span>
        <button class="close-btn" aria-label="닫기" @click="toggle">×</button>
      </header>

      <div ref="scrollEl" class="messages">
        <div
          v-for="(m, i) in messages"
          :key="i"
          class="bubble"
          :class="m.role"
        >
          {{ m.content }}
        </div>
        <div v-if="sending" class="bubble assistant typing">…</div>
      </div>

      <div class="composer">
        <input
          v-model="input"
          type="text"
          placeholder="예: 유성구 맛집 추천해줘"
          @keyup.enter="send"
        />
        <button class="btn btn-primary send-btn" @click="send">전송</button>
      </div>
    </div>

    <button class="fab" aria-label="챗봇 열기" @click="toggle">
      {{ open ? "×" : "💬" }}
    </button>
  </div>
</template>

<style scoped>
.chat-widget {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 60;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

.fab {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  background: var(--forest-600);
  color: white;
  font-size: 1.4rem;
  box-shadow: var(--shadow-lift);
}

.panel {
  width: min(320px, 86vw);
  height: 420px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  background: var(--forest-900);
  color: white;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.2rem;
  line-height: 1;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: var(--bg);
}

.bubble {
  max-width: 80%;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  line-height: 1.5;
}

.bubble.assistant {
  background: var(--surface);
  border: 1px solid var(--line);
  align-self: flex-start;
}

.bubble.user {
  background: var(--forest-600);
  color: white;
  align-self: flex-end;
}

.bubble.typing {
  color: var(--moss-400);
}

.composer {
  display: flex;
  gap: 6px;
  padding: 10px;
  border-top: 1px solid var(--line);
  background: var(--surface);
}

.composer input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
}

.send-btn {
  padding: 8px 14px;
}

@media (max-width: 480px) {
  .panel {
    width: 92vw;
    height: 70vh;
  }
}
</style>
