<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import ChatWidget from "./components/ChatWidget.vue";

const route = useRoute();
const router = useRouter();

// 💡 메인 랜딩 페이지가 아닐 때만 챗봇 위젯을 보여주는 기존 로직 보존!
const showChat = computed(() => route.name !== "landing");

// 💡 왼쪽 위 숲 로고를 누르면 언제든 첫 랜딩 페이지로 이동합니다.
function goHome() {
  router.push("/");
}
</script>

<template>
  <div class="app-container">
    <header class="global-header">
      <div class="logo-area" @click="goHome">
        <span class="forest-logo">🌳</span>
        <span class="logo-text">대전의 숲</span>
      </div>
    </header>

    <main class="main-content">
      <router-view />
    </main>

    <ChatWidget v-if="showChat" />
  </div>
</template>

<style>
/* 전역 기본 마진 초기화 및 변수 세팅 */
body {
  margin: 0;
  padding: 0;
  background-color: var(--bg, #fcfdfc);
}

/* 💡 상단 헤더 스타일 (기존 상단 다크그린 띠와 일치하는 테마) */
.global-header {
  display: flex;
  align-items: center;
  padding: 14px 24px;
  background-color: #1b351e; /* 숲의 묵직한 시그니처 다크 그린 */
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  position: sticky;
  top: 0;
  z-index: 999;
}

/* 로고 영역 스타일 */
.logo-area {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

/* 🌳 숲 로고 마우스 오버 애니메이션 */
.forest-logo {
  font-size: 22px;
  transition: transform 0.2s ease-in-out;
}

.logo-area:hover .forest-logo {
  transform: scale(1.2) rotate(5deg);
}

/* 로고 텍스트 */
.logo-text {
  font-family: 'Noto Serif KR', serif;
  font-weight: 700;
  font-size: 1.15rem;
  color: #ffffff; /* 어두운 배경 위에서 돋보이도록 흰색 글씨 적용 */
  letter-spacing: -0.02em;
}

/* 헤더 높이를 제외한 나머지 콘텐츠 높이 자동 연산 */
.main-content {
  min-height: calc(100vh - 56px);
}
</style>