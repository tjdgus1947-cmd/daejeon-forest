<script setup>
import { useRouter } from "vue-router";
import { ref } from "vue";
import LeafDivider from "../components/LeafDivider.vue";

const router = useRouter();
const showDistricts = ref(false); // 구 선택 카드 섹션 표시 여부

// 대전 5개 구의 감성 테마와 카카오맵 포커싱용 중심 좌표 정의
const districts = [
  { name: "동구", desc: "대전역과 원도심을 품은 숲", emoji: "🌲" },
  { name: "중구", desc: "문화와 역사가 살아 숨 쉬는 숲", emoji: "🌳" },
  { name: "서구", desc: "번화가와 주거가 함께 자란 숲", emoji: "🌿" },
  { name: "유성구", desc: "과학과 온천이 흐르는 활기찬 숲", emoji: "🍁" },
  { name: "대덕구", desc: "자연과 산업이 어우러진 푸른 숲", emoji: "🌱" },
];

function enter() {
  // '숲으로 들어가기'를 누르면 구 선택 카드가 아래로 부드럽게 나타납니다.
  showDistricts.value = true;
  
  // 자연스럽게 아래 카드 영역으로 스크롤 이동
  setTimeout(() => {
    const el = document.getElementById("district-selector");
    if (el) el.scrollIntoView({ behavior: "smooth" });
  }, 100);
}

function selectDistrict(guName) {
  // 선택한 구 이름에 맞춰 구별 지도 상세 페이지로 라우팅합니다.
  router.push({ name: "district", params: { gu: guName } });
}
</script>

<template>
  <main class="landing">
    <section class="hero">
      <p class="eyebrow">대전, 다섯 그루의 나무가 이룬 숲</p>
      <h1 class="headline">모여라<br />대전의 숲</h1>
      <p class="sub">
        가입도, 로그인도 없이. 궁금한 동네 이야기를 바로 나눠요.
      </p>
    </section>

    <LeafDivider class="divider" />

    <section class="entry">
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
            <strong class="dist-name">{{ dist.name }}</strong>
            <p class="dist-desc">{{ dist.desc }}</p>
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
}

.hero {
  background: linear-gradient(160deg, var(--forest-600), var(--forest-700));
  color: white;
  padding: 96px 24px 56px;
  text-align: center;
}

.eyebrow {
  font-size: var(--text-sm);
  letter-spacing: 0.06em;
  color: var(--sun-500);
  font-weight: 600;
  margin-bottom: 12px;
}

.headline {
  font-family: 'Cafe24Surround', var(--font-display);
  font-weight: 800;
  font-size: clamp(2.25rem, 7vw, var(--text-3xl));
  color: white;
  text-shadow: 2px 2px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 16px;
}

.sub {
  color: rgba(255, 255, 255, 0.82);
  max-width: 600px;
  margin: 0 auto;
  font-size: var(--text-lg);
}

 @media (max-width: 480px) {
  .sub {
    white-space: normal;
  }
}

.divider {
  color: var(--surface);
}

.entry {
  flex: 1;
  background: var(--surface);
  max-width: 460px; /* 구 카드가 이쁘게 정렬되도록 살짝 너비 확장 */
  width: 100%;
  margin: -4px auto 0;
  padding: 32px 24px 64px;
  text-align: center;
}

.note {
  font-size: var(--text-sm);
  color: var(--moss-400);
  line-height: 1.7;
  margin-bottom: 24px;
}

.enter-btn {
  width: 100%;
  font-size: var(--text-lg);
  padding: 14px;
  cursor: pointer;
}

/* 💡 추가된 대전 5개 구 선택 카드 스타일 */
.selector-area {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
}

.selector-title {
  display: inline-flex;
  align-self: center;
  font-family: 'Cafe24Surround', var(--font-display);
  font-size: 1.1rem;
  color: var(--surface);
  background: var(--forest-600);
  padding: 8px 20px;
  border-radius: 999px;
  margin: 0 auto 16px;
  font-weight: 700;
  box-shadow: var(--shadow-soft);
}

.district-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  text-align: left;
}

.district-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  box-shadow: var(--shadow-soft);
}

.district-card:hover {
  transform: translateY(-2px);
  border-color: var(--moss-400);
  background: var(--surface-alt);
  box-shadow: var(--shadow-lift);
}

.dist-emoji {
  font-size: 24px;
}

.dist-name {
  font-size: var(--text-lg);
  color: var(--forest-900);
  min-width: 50px;
}

.dist-desc {
  font-size: var(--text-xs, 12px);
  color: var(--moss-400);
  margin: 0;
  line-height: 1.4;
}

/* 부드러운 노출 애니메이션 효과 */
.animate-fade-in {
  animation: fadeIn 0.4s ease-out forwards;
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