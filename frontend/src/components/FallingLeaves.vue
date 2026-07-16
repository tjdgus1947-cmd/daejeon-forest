<template>
  <div class="falling-leaves-container" aria-hidden="true">
    <div
      v-for="leaf in leaves"
      :key="leaf.id"
      class="leaf"
      :style="{
        left: leaf.left + '%',
        animationDelay: leaf.delay + 's',
        animationDuration: leaf.duration + 's',
        transform: `scale(${leaf.scale}) rotate(${leaf.rotation}deg)`,
        opacity: leaf.opacity
      }"
    >
      🍃
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const leaves = ref([]);

// 🌳 화면 배경에서 살랑살랑 떨어질 나뭇잎 15개 랜덤 생성
onMounted(() => {
  const leafCount = 15;
  const tempLeaves = [];
  
  for (let i = 0; i < leafCount; i++) {
    tempLeaves.push({
      id: i,
      left: Math.random() * 100,            // 가로 시작 위치 (0% ~ 100%)
      delay: Math.random() * -15,           // 애니메이션 자연스러운 연결을 위해 음수 딜레이 사용
      duration: Math.random() * 8 + 8,      // 떨어지는 속도 (8초 ~ 16초 사이 랜덤)
      scale: Math.random() * 0.4 + 0.5,     // 크기 랜덤 (0.5배 ~ 0.9배)
      rotation: Math.random() * 360,        // 시작 회전 각도
      opacity: Math.random() * 0.3 + 0.3,   // 너무 튀지 않게 은은한 투명도 처리 (0.3 ~ 0.6)
    });
  }
  leaves.value = tempLeaves;
});
</script>

<style scoped>
.falling-leaves-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  pointer-events: none; /* 💡 중요: 이 효과 뒤의 버튼이나 카드가 정상 클릭되도록 설정 */
  z-index: 1;           /* 💡 중요: 배경보다는 위, 카드 콘텐츠보다는 뒤에 위치하도록 설정 */
}

.leaf {
  position: absolute;
  top: -10%;
  font-size: 1.2rem;
  user-select: none;
  animation-name: fall-and-sway;
  animation-iteration-count: infinite;
  animation-timing-function: linear;
}

/* 🍃 나뭇잎이 좌우로 살랑거리며 우아하게 내려오는 애니메이션 */
@keyframes fall-and-sway {
  0% {
    top: -10%;
    transform: translateX(0) rotate(0deg);
  }
  50% {
    transform: translateX(60px) rotate(180deg);
  }
  100% {
    top: 110%;
    transform: translateX(-20px) rotate(360deg);
  }
}
</style>