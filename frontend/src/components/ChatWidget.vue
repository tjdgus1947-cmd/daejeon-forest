<script setup>
import { ref, nextTick, onMounted, onBeforeUnmount } from "vue";
import client from "../api/client";

const open = ref(false);
const input = ref("");
const sending = ref(false);
const messages = ref([
  {
    role: "assistant",
    content:
      "안녕하세요! 대전의 숲 챗봇이에요 🌲 맛집, 축제 일정, 관광지 추천, 게시글 검색까지 편하게 물어보세요.",
  },
]);
const scrollEl = ref(null);
const widgetRef = ref(null);

function toggle() {
  open.value = !open.value;
  if (open.value) {
    scrollToBottom();
  }
}

// 위젯(패널+FAB버튼) 바깥을 클릭하면 패널 닫기
function handleClickOutside(event) {
  if (open.value && widgetRef.value && !widgetRef.value.contains(event.target)) {
    open.value = false;
  }
}

onMounted(() => {
  document.addEventListener("mousedown", handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener("mousedown", handleClickOutside);
});

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
  <div class="chat-widget" ref="widgetRef">
    <div v-if="open" class="panel card animate-pop-up">
      <header class="panel-header">
        <div class="header-title">
          <span class="bot-icon">🌳</span>
          <span class="title-text">대전의 숲 가이드</span>
        </div>
        <button class="close-btn" aria-label="닫기" @click="toggle">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none">
            <path d="M6 6L18 18M18 6L6 18" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" />
          </svg>
        </button>
      </header>

      <div ref="scrollEl" class="messages">
        <div
          v-for="(m, i) in messages"
          :key="i"
          class="bubble"
          :class="m.role"
        >
          <span v-if="m.role === 'assistant'" class="bubble-tag">숲의 가이드</span>
          <div class="bubble-content">{{ m.content }}</div>
        </div>

        <div v-if="sending" class="bubble assistant typing">
          <span class="dot-pulse"></span>
          <span class="dot-pulse"></span>
          <span class="dot-pulse"></span>
        </div>
      </div>

      <div class="composer">
        <input
          v-model="input"
          type="text"
          placeholder="유성구 맛집 알려줘!"
          @keyup.enter="send"
        />
        <button class="btn btn-primary send-btn" @click="send">전송</button>
      </div>
    </div>

    <button class="fab" :class="{ active: open }" aria-label="챗봇 열기" @click="toggle">
      <svg v-if="open" viewBox="0 0 24 24" width="20" height="20" fill="none" class="fab-icon">
        <path d="M6 6L18 18M18 6L6 18" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" />
      </svg>
      <span v-else class="fab-icon">💬</span>
    </button>
  </div>
</template>

<style scoped>
.chat-widget {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 1000; /* 카카오맵 팝업보다 항상 앞서게 제어 */
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 16px;
  font-family: 'Cafe24Surround', var(--font-body);
}

.fab {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: none;
  background: var(--forest-600);
  color: white;
  box-shadow: var(--shadow-lift);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s var(--ease-leaf);
}

.fab-icon {
  font-size: 24px;
  line-height: 1;
  display: inline-block;
  transition: transform 0.25s var(--ease-leaf);
}

.fab:hover {
  background: var(--forest-700);
  transform: translateY(-4px) scale(1.05);
  box-shadow: 0 16px 32px rgba(18, 33, 22, 0.24);
}

.fab:active {
  transform: translateY(-1px) scale(0.98);
}

.fab.active {
  background: #16281c;
}

.fab.active:hover {
  background: #111e14;
}

.panel {
  width: min(350px, 90vw);
  height: 480px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  box-shadow: var(--shadow-lift);
}

/* 헤더 배경: var(--forest-900) 대신 고정 그라데이션 사용 (다크모드에서 해당 변수가
   거의 흰색으로 재정의되어 배경으로 쓰면 하얗게 뒤집히는 문제 회피).
   다크모드 전용 톤은 아래 :global(html[data-theme="dark"]) 규칙으로 별도 지정. */
.panel-header {
  background: linear-gradient(135deg, #16281c 0%, #2f5233 100%);
  color: white;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2.5px solid var(--sun-500);
}

:global(html[data-theme="dark"]) .panel-header {
  background: linear-gradient(135deg, #0d1a0f 0%, #16281c 100%);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.bot-icon {
  font-size: 18px;
}

.title-text {
  font-weight: 800;
  font-size: var(--text-sm);
  letter-spacing: -0.01em;
  color: white;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  background: rgba(255, 255, 255, 0.14);
  border: none;
  border-radius: 50%;
  color: #ffffff;
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  transition: background 0.15s, transform 0.15s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.28);
  transform: scale(1.08);
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: var(--bg);
}

.bubble {
  max-width: 82%;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  line-height: 1.55;
  position: relative;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
  color: var(--text-main);
}

.bubble-tag {
  display: block;
  font-size: 9px;
  font-weight: 800;
  color: var(--moss-400);
  margin-bottom: 3px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.bubble.assistant {
  background: var(--surface);
  border: 1px solid var(--line);
  align-self: flex-start;
  border-bottom-left-radius: 2px;
}

.bubble.user {
  background: var(--forest-600);
  color: white;
  align-self: flex-end;
  border-bottom-right-radius: 2px;
}

.bubble.typing {
  align-self: flex-start;
  background: var(--surface);
  border: 1px solid var(--line);
  padding: 12px 16px;
  display: flex;
  gap: 4px;
  align-items: center;
}

.dot-pulse {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--moss-400);
  animation: pulse 1s infinite ease-in-out;
}

.dot-pulse:nth-child(2) { animation-delay: 0.2s; }
.dot-pulse:nth-child(3) { animation-delay: 0.4s; }

@keyframes pulse {
  0%, 100% { transform: scale(0.8); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 1; }
}

.composer {
  display: flex;
  gap: 8px;
  padding: 14px 16px;
  border-top: 1px solid var(--line);
  background: var(--surface);
}

.composer input {
  flex: 1;
  padding: 10px 14px;
  border: 1.5px solid var(--line);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  transition: all 0.2s var(--ease-leaf);
  background: var(--surface);
  color: var(--text-main);
}

.composer input:focus {
  border-color: var(--moss-400);
  box-shadow: 0 0 0 3px rgba(85, 123, 107, 0.1);
}

.send-btn {
  padding: 10px 18px;
  font-size: var(--text-sm);
  border-radius: var(--radius-sm);
}

.animate-pop-up {
  animation: popUp 0.3s var(--ease-leaf) forwards;
  transform-origin: bottom right;
}

@keyframes popUp {
  from {
    opacity: 0;
    transform: scale(0.85) translateY(24px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@media (max-width: 480px) {
  .panel {
    width: calc(100vw - 40px);
    height: 70vh;
  }
  .chat-widget {
    right: 20px;
    bottom: 20px;
  }
}
</style>