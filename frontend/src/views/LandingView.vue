<script setup>
import { useRouter } from "vue-router";
import { ref } from "vue";
import LeafDivider from "../components/LeafDivider.vue";

const router = useRouter();
const showDistricts = ref(false); // 구 선택 카드 섹션 표시 여부

const districts = [
  { name: "동구", desc: "대전역과 원도심을 품은 숲", emoji: "🌲" },
  { name: "중구", desc: "문화와 역사가 살아 숨 쉬는 숲", emoji: "🌳" },
  { name: "서구", desc: "번화가와 주거가 함께 자란 숲", emoji: "🌿" },
  { name: "유성구", desc: "과학과 온천이 흐르는 활기찬 숲", emoji: "🍁" },
  { name: "대덕구", desc: "자연과 산업이 어우러진 푸른 숲", emoji: "🌱" },
];

function enter() {
  showDistricts.value = true;
  
  setTimeout(() => {
    const el = document.getElementById("district-selector");
    if (el) el.scrollIntoView({ behavior: "smooth" });
  }, 100);
}

function selectDistrict(guName) {
  router.push({ name: "district", params: { gu: guName } });
}
</script>

<template>
  <main class="landing">
    <!-- 🌿 히어로 섹션 그라데이션 및 정렬 고도화 -->
    <section class="hero">
      <!-- 🍃 감성 충만! 배경에 휘날리는 나뭇잎 파티클 잎사귀들 -->
      <div class="falling-leaves-container">
        <div class="leaf"></div>
        <div class="leaf"></div>
        <div class="leaf"></div>
        <div class="leaf"></div>
        <div class="leaf"></div>
        <div class="leaf"></div>
        <div class="leaf"></div>
        <div class="leaf"></div>
      </div>

      <div class="hero-inner">
        <p class="eyebrow">대전, 다섯 그루의 나무가 이룬 숲</p>
        <h1 class="headline">모여라<br />대전의 숲</h1>
        <p class="sub">
          가입도, 로그인도 없이.<br />궁금한 동네 이야기를 바로 나눠요.
        </p>
      </div>
    </section>

    <LeafDivider class="divider" />

    <section class="entry">
      <div class="entry-inner">
        <p class="note">
          글을 쓸 때 닉네임과 비밀번호만 함께 남기면 돼요.<br />
          비밀번호는 나중에 내 글을 수정하거나 지울 때 확인용으로 쓰여요.
        </p>
        
        <button 
          v-if="!showDistricts" 
          class="btn btn-primary enter-btn" 
          @click="enter"
        >
          숲으로 들어가기
        </button>

        <div 
          v-else 
          id="district-selector" 
          class="selector-area animate-fade-in"
        >
          <h3 class="selector-title">어느 동네 숲으로 갈까요?</h3>
          <div class="district-grid">
            <div 
              v-for="dist in districts" 
              :key="dist.name"
              class="district-card"
              @click="selectDistrict(dist.name)"
            >
              <span class="dist-emoji">{{ dist.emoji }}</span>
              <div class="dist-info">
                <strong class="dist-name">{{ dist.name }}</strong>
                <p class="dist-desc">{{ dist.desc }}</p>
              </div>
              <span class="chevron">→</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
.landing {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg);
}

.hero {
  background: linear-gradient(160deg, var(--forest-700) 0%, var(--forest-900) 100%);
  color: white;
  padding: 104px 24px 64px;
  text-align: center;
  position: relative;
  overflow: hidden; /* 흘러가는 잎사귀들이 히어로 영역 밖으로 안 튀어나가게 방어 */
}

/* 🍃 나뭇잎이 흔들리며 떨어지는 애니메이션 전용 컨테이너 */
.falling-leaves-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none; /* 마우스 클릭 등이 통과하게 처리 */
  z-index: 1;
}

/* 🍃 나뭇잎 개별 스타일 정의 */
.leaf {
  position: absolute;
  width: 15px;
  height: 8px;
  background: rgba(223, 148, 41, 0.2); /* 은은한 주황빛 가을 잎 */
  border-radius: 50% 0; /* 잎사귀 모양의 유선형 */
  animation: fall 12s linear infinite, swing 3s ease-in-out infinite alternate;
}

/* 초록초록한 봄여름 잎사귀 믹스 */
.leaf:nth-child(even) {
  background: rgba(107, 144, 128, 0.25); /* 살짝 투명한 모스 그린 */
  width: 12px;
  height: 6px;
}

/* 자연스러운 움직임을 위해 무작위로 위치, 크기, 애니메이션 딜레이 설정 */
.leaf:nth-child(1) { left: 10%; animation-delay: 0s; animation-duration: 10s; }
.leaf:nth-child(2) { left: 25%; animation-delay: 2s; animation-duration: 14s; }
.leaf:nth-child(3) { left: 40%; animation-delay: 4s; animation-duration: 11s; }
.leaf:nth-child(4) { left: 55%; animation-delay: 1s; animation-duration: 13s; }
.leaf:nth-child(5) { left: 70%; animation-delay: 5s; animation-duration: 9s; }
.leaf:nth-child(6) { left: 85%; animation-delay: 3s; animation-duration: 15s; }
.leaf:nth-child(7) { left: 95%; animation-delay: 0.5s; animation-duration: 12s; }
.leaf:nth-child(8) { left: 15%; animation-delay: 6s; animation-duration: 16s; }

/* 🍃 떨어지면서 대각선으로 흘러가는 키프레임 */
@keyframes fall {
  0% {
    top: -5%;
    transform: rotate(0deg);
  }
  100% {
    top: 105%;
    left: calc(100% + 10%); /* 대각선 바람 타고 흘러가는 모션 */
    transform: rotate(360deg);
  }
}

/* 좌우로 살랑살랑 흔들리는 스윙 키프레임 */
@keyframes swing {
  0% {
    margin-left: 0px;
  }
  100% {
    margin-left: 24px;
  }
}

.hero-inner {
  max-width: 600px;
  margin: 0 auto;
  position: relative;
  z-index: 2; /* 잎사귀 배경 뒤에 묻히지 않게 앞으로 정렬 */
}

.eyebrow {
  font-size: var(--text-sm);
  letter-spacing: 0.08em;
  color: var(--sun-500);
  font-weight: 700;
  margin-bottom: 14px;
}

.headline {
  font-size: clamp(2.5rem, 8vw, var(--text-3xl));
  color: white;
  margin-bottom: 20px;
  font-weight: 900;
  line-height: 1.25;
}

.sub {
  color: rgba(255, 255, 255, 0.85);
  font-size: var(--text-lg);
  line-height: 1.6;
  margin: 0;
}

.divider {
  color: var(--surface);
  margin-top: -1px;
}

.entry {
  flex: 1;
  background: var(--surface);
  width: 100%;
  margin-top: -2px;
  padding: 40px 24px 80px;
}

.entry-inner {
  max-width: 640px;
  margin: 0 auto;
  text-align: center;
}

.note {
  font-size: var(--text-sm);
  color: var(--moss-400);
  line-height: 1.75;
  margin-bottom: 32px;
  font-weight: 500;
}

.enter-btn {
  width: 100%;
  max-width: 380px;
  font-size: var(--text-lg);
  padding: 16px;
  box-shadow: var(--shadow-soft);
}

.selector-area {
  margin-top: 16px;
  text-align: left;
}

.selector-title {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  color: var(--forest-900);
  margin-bottom: 24px;
  text-align: center;
  font-weight: 800;
}

.district-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

@media (min-width: 580px) {
  .district-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.district-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--surface);
  border: 1.5px solid var(--line);
  border-radius: var(--radius-md);
  padding: 18px 20px;
  cursor: pointer;
  transition: all 0.25s var(--ease-leaf);
  position: relative;
}

.district-card:hover {
  transform: translateY(-3px);
  border-color: var(--forest-600);
  box-shadow: var(--shadow-lift);
}

.dist-emoji {
  font-size: 28px;
  transition: transform 0.2s var(--ease-leaf);
}

.district-card:hover .dist-emoji {
  transform: scale(1.15) rotate(4deg);
}

.dist-info {
  flex: 1;
}

.dist-name {
  display: block;
  font-size: var(--text-base);
  color: var(--forest-900);
  font-weight: 700;
  margin-bottom: 4px;
}

.dist-desc {
  font-size: var(--text-xs);
  color: var(--moss-400);
  margin: 0;
  line-height: 1.4;
  font-weight: 500;
}

.chevron {
  font-size: 16px;
  color: var(--line);
  font-weight: 700;
  transition: all 0.2s var(--ease-leaf);
}

.district-card:hover .chevron {
  color: var(--forest-600);
  transform: translateX(3px);
}

.animate-fade-in {
  animation: fadeIn 0.5s var(--ease-leaf) forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>