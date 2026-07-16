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
        "안녕하세요! 대전의 숲 챗봇이에요 🌲 맛집, 축제 일정, 관광지 추천, 게시글 검색까지 편하게 물어보세요.",
    },
  ]);
  const scrollEl = ref(null);

  function toggle() {
    open.value = !open.value;
    if (open.value) {
      scrollToBottom();
    }
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
      <div v-if="open" class="panel card animate-pop-up">
        <header class="panel-header">
          <div class="header-title">
            <span class="bot-icon">🌳</span>
            <span class="title-text">대전의 숲 가이드</span>
          </div>
          <button class="close-btn" aria-label="닫기" @click="toggle">×</button>
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
        <span class="fab-icon">{{ open ? "×" : "💬" }}</span>
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

  /* 🌿 둥글고 생동감 넘치는 호버 모션이 들어간 FAB */
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
    transform: translateY(-4px) scale(1.05); /* 콩콩 뛰어오르는 듯한 이펙트 */
    box-shadow: 0 16px 32px rgba(18, 33, 22, 0.24);
  }

  .fab:active {
    transform: translateY(-1px) scale(0.98);
  }

  .fab.active {
    background: var(--forest-900);
  }

  .fab.active:hover {
    background: #111e14;
  }

  /* 🌿 대화창 패널 프리미엄 화화 */
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

  .panel-header {
    background: linear-gradient(135deg, var(--forest-900) 0%, #1e3a24 100%);
    color: white;
    padding: 16px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2.5px solid var(--sun-500);
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
  }

  .close-btn {
    background: none;
    border: none;
    color: rgba(255, 255, 255, 0.7);
    font-size: 24px;
    line-height: 1;
    cursor: pointer;
    transition: color 0.15s;
  }

  .close-btn:hover {
    color: white;
  }

  .messages {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    background: #f4f7f2; /* 가독성을 위해 살짝 톤다운된 세이지 그린 */
  }

  /* 🌿 숲 가이드 전용 말풍선 설계 */
  .bubble {
    max-width: 82%;
    padding: 10px 14px;
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    line-height: 1.55;
    position: relative;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
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
    border-bottom-left-radius: 2px; /* 살짝 꼬리모양 느낌 */
  }

  .bubble.user {
    background: var(--forest-600);
    color: white;
    align-self: flex-end;
    border-bottom-right-radius: 2px;
  }

  /* 🌿 실시간 타이핑 맥박 애니메이션 */
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

  /* 🌿 글쓰기 입력창(Composer) */
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

  /* 부드럽게 솟구쳐 오르는 열기 모션 */
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