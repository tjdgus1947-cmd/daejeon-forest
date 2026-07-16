<script setup>
import { useRouter } from "vue-router";
import { DISTRICTS } from "../composables/districts";

const router = useRouter();

function selectDistrict(name) {
  router.push({ name: "district", params: { gu: name } });
}
</script>

<template>
  <main class="select-page">
    <header class="top">
      <div class="container top-inner">
        <div>
          <p class="greeting">숲을 산책해볼까요</p>
          <h1>어느 구의 숲으로 갈까요?</h1>
        </div>
      </div>
    </header>
<div class="container content-wrap">
  <!-- 💡 대전시 실제 비율의 행정경계 SVG 지도 (클릭 및 호버 액션 지원) -->
  <div class="map-svg-container">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 550" class="daejeon-svg">
      <!-- 대덕구 -->
      <path
        d="M 285 45
           Q 320 40 335 45
           Q 355 60 358 82
           Q 362 120 338 155
           Q 315 178 292 188
           Q 268 170 252 148
           Q 245 122 252 100
           Q 262 65 285 45 Z"
        class="map-path daedeok"
        @click="selectDistrict('대덕구')"
      />
      <text x="305" y="112" class="map-label">대덕구</text>

      <!-- 유성구 -->
      <path
        d="M 130 122
           Q 190 108 250 100
           Q 248 128 252 148
           Q 268 170 292 188
           Q 265 222 232 258
           Q 226 320 222 380
           Q 165 355 112 322
           Q 85 260 72 202
           Q 90 155 130 122 Z"
        class="map-path yuseong"
        @click="selectDistrict('유성구')"
      />
      <text x="165" y="212" class="map-label">유성구</text>

      <!-- 서구 -->
      <path
        d="M 112 322
           Q 165 355 222 380
           Q 228 398 230 420
           Q 224 470 212 518
           Q 178 522 150 512
           Q 122 458 112 402
           Q 108 360 112 322 Z"
        class="map-path seo"
        @click="selectDistrict('서구')"
      />
      <text x="160" y="422" class="map-label">서구</text>

      <!-- 중구 -->
      <path
        d="M 222 380
           Q 255 358 290 342
           Q 302 415 310 488
           Q 280 502 250 510
           Q 228 516 212 518
           Q 224 470 230 420
           Q 228 398 222 380 Z"
        class="map-path jung"
        @click="selectDistrict('중구')"
      />
      <text x="255" y="442" class="map-label">중구</text>

      <!-- 동구 -->
      <path
        d="M 292 188
           Q 315 178 338 155
           Q 362 120 358 82
           Q 405 118 440 178
           Q 430 280 420 378
           Q 365 435 310 488
           Q 302 415 290 342
           Q 255 358 222 380
           Q 232 320 265 222
           Q 280 202 292 188 Z"
        class="map-path dong"
        @click="selectDistrict('동구')"
      />
      <text x="345" y="300" class="map-label">동구</text>
    </svg>
  </div>

  <!-- 기존 그로브 타일 격자도 함께 유지하여 뛰어난 반응성 제공 -->
  <div class="grove-grid">
    <button
      v-for="d in DISTRICTS"
      :key="d.name"
      class="grove-tile"
      @click="selectDistrict(d.name)"
    >
    
      <span class="grove-icon">{{ d.emoji }}🌲</span>
      <span class="grove-name">{{ d.name }}</span>
      <span class="grove-blurb">{{ d.blurb }}</span>
    </button>
  </div>
</div>
  </main>
</template>

<style scoped>
.select-page {
  min-height: 100%;
  background: var(--bg);
}

.top {
  background: var(--forest-600);
  color: white;
  padding: 40px 0;
}

.top-inner h1 {
  font-family: 'Cafe24Surround', var(--font-display);
  color: white;
  font-size: var(--text-2xl);
  margin: 4px 0 0;
}

.greeting {
  color: var(--sun-500);
  font-size: var(--text-sm);
  font-weight: 600;
  margin: 0;
}

.content-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  padding: 32px 0 64px;
}

/* 💡 SVG 행정구역 디자인 스타일 */
.map-svg-container {
  width: 100%;
  max-width: 320px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-soft);
}

.daejeon-svg {
  width: 100%;
  height: auto;
}

.map-path {
  fill: var(--surface-alt);
  stroke: var(--line);
  stroke-width: 3px;
  stroke-linejoin: round;
  stroke-linecap: round;
  cursor: pointer;
  transition: fill 0.2s ease, stroke 0.2s ease, transform 0.2s ease;
}

/* 각 구별 마우스 호버 시 포인트 컬러 디자인 */
.map-path:hover {
  fill: var(--moss-400);
  stroke: var(--forest-600);
}

.map-label {
  fill: var(--forest-900);
  font-size: 14px;
  font-weight: 700;
  text-anchor: middle;
  pointer-events: none; /* 텍스트가 클릭/호버 가리는 현상 방지 */
}

.grove-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
  width: 100%;
}

.grove-tile {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 28px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 8px;
  transition: transform 0.2s var(--ease-leaf), box-shadow 0.2s var(--ease-leaf),
    border-color 0.2s var(--ease-leaf);
}

.grove-tile:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lift);
  border-color: var(--moss-400);
}

.grove-icon {
  font-size: 2rem;
}

.grove-name {
  font-family: 'Cafe24Surround', var(--font-display);
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--forest-900);
}

.grove-blurb {
  font-size: var(--text-xs);
  color: var(--moss-400);
}
</style>