<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { DISTRICTS } from "../composables/districts";
import MapPins from "../components/MapPins.vue";
import PostList from "../components/PostList.vue";

const props = defineProps({
  gu: { type: String, required: true },
});

const router = useRouter();
const tab = ref("map"); // 'map' | 'board'

const district = computed(
  () => DISTRICTS.find((d) => d.name === props.gu) || DISTRICTS[0]
);

// 💡 메인 숲 구 선택 화면으로 정확히 되돌아가는 로직
function goBack() {
  router.push({ name: "districts" }); 
}
</script>

<template>
  <main class="district-page">
    <!-- 🌿 깊은 밤의 숲을 담은 프리미엄 그라데이션 헤더 -->
    <header class="top">
      <div class="container top-inner">
        <button class="back-btn" @click="goBack">
          <span class="arrow">←</span> 다른 구 보기
        </button>
        <h1 class="district-title">{{ gu }}</h1>
        <p class="blurb">{{ district.blurb }}</p>
      </div>
    </header>

    <div class="container">
      <!-- 🌿 감각적인 라운드 칩 스타일 탭 메뉴 -->
      <nav class="tabs">
        <button
          class="tab"
          :class="{ active: tab === 'map' }"
          @click="tab = 'map'"
        >
          <span class="tab-icon">🗺️</span> 지도 탐색
        </button>
        <button
          class="tab"
          :class="{ active: tab === 'board' }"
          @click="tab = 'board'"
        >
          <span class="tab-icon">📋</span> 동네 게시판
        </button>
      </nav>

      <!-- 🌿 탭 콘텐츠 페이드인 애니메이션 영역 -->
      <section v-show="tab === 'map'" class="tab-content">
        <MapPins :gu="gu" :center="{ lat: district.lat, lng: district.lng }" />
      </section>

      <section v-show="tab === 'board'" class="tab-content">
        <PostList :gu="gu" />
      </section>
    </div>
  </main>
</template>

<style scoped>
.district-page {
  min-height: 100%;
  padding-bottom: 80px;
}

/* 🌿 20년 차 디자인 감성을 채워 넣은 헤더 그라데이션 */
.top {
  background: linear-gradient(135deg, var(--forest-900) 0%, #1e3a24 100%);
  color: white;
  padding: 40px 0 32px;
  border-bottom: 4px solid var(--sun-500);
  box-shadow: var(--shadow-soft);
  position: relative;
  overflow: hidden;
}

/* 숲 조명이 은은하게 투과되는 듯한 스팟 백그라운드 */
.top::before {
  content: "";
  position: absolute;
  top: -50%;
  right: -10%;
  width: 280px;
  height: 280px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(223, 148, 41, 0.08) 0%, transparent 70%);
  pointer-events: none;
}

.top-inner {
  position: relative;
  z-index: 2;
}

.back-btn {
  background: none;
  border: none;
  color: var(--sun-500);
  font-size: var(--text-sm);
  font-weight: 700;
  padding: 0;
  margin-bottom: 12px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: transform 0.2s var(--ease-leaf), color 0.2s var(--ease-leaf);
}

.back-btn .arrow {
  display: inline-block;
  transition: transform 0.2s var(--ease-leaf);
}

.back-btn:hover {
  color: white;
}

.back-btn:hover .arrow {
  transform: translateX(-4px);
}

.district-title {
  color: white;
  font-size: var(--text-3xl);
  font-weight: 800;
  margin: 0 0 6px 0;
  letter-spacing: -0.02em;
}

.blurb {
  color: rgba(255, 255, 255, 0.8);
  font-size: var(--text-sm);
  margin: 0;
  font-weight: 500;
}

/* 🌿 탭 바 정돈 */
.tabs {
  display: flex;
  gap: 10px;
  margin: 28px 0 20px;
}

.tab {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  border-radius: 999px;
  border: 1.5px solid var(--line);
  background: var(--surface);
  font-size: var(--text-sm);
  font-weight: 700;
  color: var(--forest-700);
  cursor: pointer;
  transition: all 0.2s var(--ease-leaf);
}

.tab-icon {
  font-size: 15px;
  transition: transform 0.2s var(--ease-leaf);
}

.tab:hover {
  border-color: var(--forest-600);
  background: var(--surface-alt);
  color: var(--forest-900);
}

.tab:hover .tab-icon {
  transform: scale(1.15);
}

.tab.active {
  background: var(--forest-600);
  color: white;
  border-color: var(--forest-600);
  box-shadow: 0 4px 12px rgba(37, 68, 42, 0.15);
}

.tab-content {
  animation: fadeIn 0.4s var(--ease-leaf);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>