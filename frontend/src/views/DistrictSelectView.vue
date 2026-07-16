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
      d="M 320.2 74.3 L 324.0 78.1 L 317.1 104.5 L 326.8 110.3 L 343.1 105.2 L 347.8 111.7 L 327.7 131.5 L 313.8 160.4 L 289.1 188.5 L 284.2 216.7 L 301.9 246.7 L 300.7 260.4 L 287.9 256.1 L 277.0 261.5 L 265.2 246.6 L 240.8 276.0 L 227.7 263.2 L 214.5 229.8 L 236.3 217.9 L 239.4 184.1 L 247.2 168.3 L 238.8 153.2 L 212.6 131.1 L 210.6 121.6 L 225.6 105.5 L 267.0 105.0 L 279.4 115.6 L 288.4 114.0 L 297.8 105.3 L 302.7 84.7 L 320.2 74.3 Z"
      class="map-path daedeok"
      @click="selectDistrict('대덕구')"
    />
    <text x="280" y="161" class="map-label">대덕구</text>

    <!-- 유성구 -->
    <path
      d="M 203.8 40.0 L 228.0 68.5 L 222.1 95.6 L 225.6 105.5 L 210.3 125.2 L 246.6 165.9 L 237.1 194.7 L 236.3 217.9 L 214.8 231.0 L 192.9 230.8 L 164.2 257.6 L 167.9 289.1 L 146.5 292.1 L 151.3 315.1 L 142.5 334.4 L 132.4 338.1 L 126.6 356.1 L 117.2 362.7 L 116.2 377.6 L 95.7 389.9 L 83.9 388.9 L 54.5 372.2 L 40.0 350.1 L 48.8 341.4 L 55.8 343.2 L 55.7 296.4 L 65.6 290.2 L 62.4 281.6 L 66.3 276.0 L 78.8 270.3 L 68.6 246.6 L 77.0 240.0 L 81.0 225.8 L 76.7 207.8 L 82.3 166.9 L 107.9 152.0 L 135.1 155.8 L 152.6 142.6 L 157.3 122.7 L 173.7 105.7 L 170.6 93.7 L 180.1 77.7 L 172.6 65.3 L 176.5 53.9 L 186.2 57.3 L 203.8 40.0 Z"
      class="map-path yuseong"
      @click="selectDistrict('유성구')"
    />
    <text x="139" y="221" class="map-label">유성구</text>

    <!-- 동구 -->
    <path
      d="M 333.4 130.2 L 330.4 140.5 L 344.3 175.7 L 354.9 174.3 L 359.8 155.2 L 366.2 159.2 L 371.5 153.8 L 392.9 160.0 L 396.8 175.5 L 413.7 191.2 L 406.9 196.1 L 389.3 191.7 L 372.2 207.1 L 369.8 254.5 L 343.1 278.5 L 346.0 298.8 L 335.4 318.8 L 341.2 328.3 L 331.9 341.8 L 341.2 361.8 L 329.0 377.2 L 325.8 394.2 L 333.5 429.6 L 304.1 450.8 L 306.2 462.4 L 287.7 474.6 L 289.4 483.8 L 272.1 492.7 L 249.7 473.0 L 254.3 467.7 L 251.8 443.8 L 263.4 443.7 L 274.7 427.8 L 265.7 406.8 L 255.3 404.2 L 270.3 380.8 L 255.8 350.0 L 272.8 341.4 L 278.8 341.4 L 280.5 348.5 L 293.6 347.5 L 280.9 322.8 L 271.4 318.5 L 239.4 271.7 L 248.3 271.0 L 246.4 265.2 L 265.2 246.6 L 277.0 261.5 L 288.3 256.1 L 300.2 261.2 L 301.9 246.7 L 284.2 216.7 L 289.1 188.5 L 333.4 130.2 Z"
      class="map-path dong"
      @click="selectDistrict('동구')"
    />
    <text x="311" y="304" class="map-label">동구</text>

    <!-- 중구 -->
    <path
      d="M 227.7 263.2 L 257.8 292.2 L 271.4 318.5 L 280.9 322.8 L 293.6 347.5 L 280.5 348.5 L 278.8 341.4 L 272.8 341.4 L 256.3 348.6 L 270.3 380.8 L 255.3 404.2 L 265.7 406.8 L 274.7 427.8 L 263.4 443.7 L 251.8 443.8 L 254.3 467.7 L 246.4 474.4 L 232.6 465.8 L 235.7 458.9 L 223.9 435.8 L 208.0 434.3 L 211.4 392.7 L 190.2 378.0 L 184.2 359.1 L 201.4 340.7 L 199.5 329.4 L 207.5 319.8 L 210.2 294.9 L 226.5 279.9 L 227.7 263.2 Z"
      class="map-path jung"
      @click="selectDistrict('중구')"
    />
    <text x="242" y="371" class="map-label">중구</text>

    <!-- 서구 -->
    <path
      d="M 197.3 230.0 L 217.9 234.7 L 228.6 257.8 L 227.4 275.8 L 209.0 297.8 L 200.0 343.5 L 184.6 357.6 L 189.4 380.9 L 179.7 381.5 L 174.7 392.2 L 181.4 420.3 L 175.4 445.4 L 180.3 456.9 L 162.8 473.0 L 160.5 488.6 L 144.3 510.0 L 139.3 493.6 L 143.7 484.0 L 131.2 479.4 L 129.4 465.1 L 108.8 441.0 L 106.7 452.5 L 96.0 450.7 L 94.5 440.8 L 82.0 431.9 L 78.7 406.7 L 98.6 385.0 L 116.2 377.6 L 117.2 362.7 L 126.6 356.1 L 132.4 338.1 L 142.5 334.4 L 151.3 315.1 L 146.5 292.1 L 167.9 289.1 L 163.4 258.8 L 197.3 230.0 Z"
      class="map-path seo"
      @click="selectDistrict('서구')"
    />
    <text x="154" y="379" class="map-label">서구</text>
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