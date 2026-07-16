<script setup>
import { computed, ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import ChatWidget from "./components/ChatWidget.vue";
// 🍃 [추가] 새로 제작한 흩날리는 나뭇잎 효과 컴포넌트 불러오기
import FallingLeaves from "./components/FallingLeaves.vue";

const route = useRoute();
const router = useRouter();

// 💡 메인 랜딩 페이지가 아닐 때만 챗봇 위젯을 보여주는 기존 로직 보존!
const showChat = computed(() => route.name !== "landing");

// 💡 왼쪽 위 숲 로고를 누르면 언제든 첫 랜딩 페이지로 이동합니다.
function goHome() {
  router.push("/");
}

// 🌙 야간 숲(다크 모드) 상태 제어
const isDarkMode = ref(false);

function toggleDarkMode() {
  isDarkMode.value = !isDarkMode.value;
  const theme = isDarkMode.value ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("forest-theme", theme);
}

// 초기화 시 로컬스토리지나 시스템 테마 상태 읽기
onMounted(() => {
  const savedTheme = localStorage.getItem("forest-theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  
  if (savedTheme === "dark" || (!savedTheme && prefersDark)) {
    isDarkMode.value = true;
    document.documentElement.setAttribute("data-theme", "dark");
  } else {
    isDarkMode.value = false;
    document.documentElement.setAttribute("data-theme", "light");
  }
});
</script>

<template>
  <div class="app-container">
    <FallingLeaves />

    <header class="global-header">
      <div class="logo-area" @click="goHome">
        <span class="forest-logo">🌳</span>
        <span class="logo-text">대전의 숲</span>
      </div>

      <button class="theme-toggle-btn" @click="toggleDarkMode" :aria-label="isDarkMode ? '낮의 숲 테마로 변경' : '야간 숲 테마로 변경'">
        <span class="toggle-icon" :class="{ 'is-dark': isDarkMode }">
          {{ isDarkMode ? '☀️' : '🌙' }}
        </span>
        <span class="toggle-text">{{ isDarkMode ? '낮의 숲' : '야간 숲' }}</span>
      </button>
    </header>

    <main class="main-content">
      <router-view />
    </main>

    <ChatWidget v-if="showChat" />
  </div>
</template>

<style>
/* 🌿 글로벌 테마 색상 변수 디자인 정의 (낮과 밤의 감성 숲 톤앤매너) */
/* ==========================================
   🌿 글로벌 테마 색상 변수 디자인 정의
   ========================================== */
:root {
  /* 낮의 숲 (Light Mode) */
  --bg: #f5f7f5;
  --surface: #ffffff;
  --surface-alt: #edf2ed;
  --line: #e1e7e1;
  --text-main: #202c21;
  --text-muted: #5a6e5d;
  
  --forest-900: #132715;
  --forest-700: #1f3e23;
  --forest-600: #2c5c32;
  --moss-400: #6b826f;
  --sun-500: #e09f3e;
  --danger: #cf5b5b;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 18px;
  --shadow-soft: 0 4px 18px rgba(31, 62, 35, 0.05);
  --shadow-lift: 0 8px 24px rgba(31, 62, 35, 0.08);
  --ease-leaf: cubic-bezier(0.25, 0.8, 0.25, 1);
}

/* 🌙 html[data-theme="dark"]와 :root[data-theme="dark"]를 모두 잡아 확실하게 다크 모드 속성 주입 */
html[data-theme="dark"],
:root[data-theme="dark"] {
  /* 야간 숲 (Dark Mode) */
  --bg: #111a12 !important; 
  --surface: #19251a !important; 
  --surface-alt: #233324 !important;
  --line: #2d3f2f !important;
  --text-main: #f0f4f0 !important;
  --text-muted: #95a596 !important;
  
  --forest-900: #f0f4f0 !important;
  --forest-700: #cce3cd !important;
  --forest-600: #5cb86b !important; 
  --moss-400: #8da490 !important;
  --sun-500: #ffc466 !important;
  --danger: #ff7676 !important;
}

/* ==========================================
   🚨 강력한 전역 강제 스타일 주입 (모든 스크린 덮어쓰기)
   ========================================== */
html,
body, 
#app, 
.app-container,
main,
section {
  background-color: var(--bg) !important;
  color: var(--text-main) !important;
  transition: background-color 0.3s var(--ease-leaf), color 0.3s var(--ease-leaf);
}

/* 모든 뷰의 카드, 글상자, 댓글 박스 강제 동기화 */
.card, 
.post-card, 
.comments,
article {
  background-color: var(--surface) !important;
  border-color: var(--line) !important;
  color: var(--text-main) !important;
}

/* 인풋 및 텍스트 에어리어 강제 동기화 */
input, 
textarea,
select {
  background-color: var(--surface) !important;
  color: var(--text-main) !important;
  border-color: var(--line) !important;
}

/* ==========================================
   🤖 챗봇(ChatWidget) 야간 모드 전용 정밀 스타일 보완
   ========================================== */
/* 1. 챗봇 본체 배경 및 메인 프레임 어둡게 전환 */
html[data-theme="dark"] .chat-window,
html[data-theme="dark"] div[class*="chat-window"],
html[data-theme="dark"] .chat-container,
html[data-theme="dark"] div[class*="chat-container"] {
  background-color: var(--surface) !important;
  background: var(--surface) !important;
  border-color: var(--line) !important;
}

/* 2. 대화 내역이 쌓이는 스크롤 바디 및 하단 입력 필드 영역을 한 단계 더 어둡게 격리 */
html[data-theme="dark"] .chat-body,
html[data-theme="dark"] div[class*="chat-body"],
html[data-theme="dark"] .chat-footer,
html[data-theme="dark"] div[class*="chat-footer"] {
  background-color: var(--bg) !important;
  background: var(--bg) !important;
}

/* 3. 우측 하단 동그란 챗봇 토글 열기/닫기 버튼 야간 대응 */
html[data-theme="dark"] button[class*="toggle"],
html[data-theme="dark"] .chat-toggle-btn {
  background-color: var(--surface) !important;
  background: var(--surface) !important;
  border: 1px solid var(--line) !important;
}

/* 💡 상단 헤더 스타일 (기존 상단 다크그린 띠와 일치하는 테마) */
.global-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 24px;
  background-color: #1b351e !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  position: sticky;
  top: 0;
  z-index: 999;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.forest-logo {
  font-size: 22px;
  transition: transform 0.2s ease-in-out;
}

.logo-area:hover .forest-logo {
  transform: scale(1.2) rotate(5deg);
}

.logo-text {
  font-family: 'Cafe24Surround', 'Noto Serif KR', serif;
  font-weight: 700;
  font-size: 1.15rem;
  color: #ffffff !important;
  letter-spacing: -0.02em;
  text-shadow: 1px 1px 0 rgba(0, 0, 0, 0.12);
}

.theme-toggle-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.08) !important;
  border: 1px solid rgba(255, 255, 255, 0.15) !important;
  padding: 6px 14px;
  border-radius: 999px;
  cursor: pointer;
  color: #ffffff !important;
  font-size: 12px;
  font-weight: 600;
}

.theme-toggle-btn:hover {
  background: rgba(255, 255, 255, 0.89) !important;
  border-color: rgba(255, 255, 255, 0.3) !important;
}

.toggle-icon {
  display: inline-block;
  transition: transform 0.4s var(--ease-leaf);
}

.theme-toggle-btn:hover .toggle-icon {
  transform: rotate(15deg) scale(1.1);
}

.main-content {
  min-height: calc(100vh - 56px);
}
</style>