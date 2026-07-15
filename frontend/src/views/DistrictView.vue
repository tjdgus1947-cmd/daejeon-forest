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
    <header class="top">
      <div class="container top-inner">
        <!-- 💡 뒤로 가기 핸들러 함수 적용 -->
        <button class="back-btn" @click="goBack">
          ← 다른 구 보기
        </button>
        <h1>{{ gu }}</h1>
        <p class="blurb">{{ district.blurb }}</p>
      </div>
    </header>

    <div class="container">
      <nav class="tabs">
        <button
          class="tab"
          :class="{ active: tab === 'map' }"
          @click="tab = 'map'"
        >
          🗺️ 지도
        </button>
        <button
          class="tab"
          :class="{ active: tab === 'board' }"
          @click="tab = 'board'"
        >
          📋 게시판
        </button>
      </nav>

      <section v-show="tab === 'map'">
        <!-- 💡 MapPins에 해당 구의 위경도 좌표를 그대로 전달해 줌으로써 카카오맵이 정확히 줌인 및 이펙트 이동하도록 지원 -->
        <MapPins :gu="gu" :center="{ lat: district.lat, lng: district.lng }" />
      </section>

      <section v-show="tab === 'board'">
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

.top {
  background: var(--forest-900);
  color: white;
  padding: 32px 0 24px;
}

.back-btn {
  background: none;
  border: none;
  color: var(--sun-500);
  font-size: var(--text-sm);
  font-weight: 600;
  padding: 0;
  margin-bottom: 8px;
  cursor: pointer;
}

.top-inner h1 {
  color: white;
  margin-bottom: 4px;
}

.blurb {
  color: rgba(255, 255, 255, 0.75);
  font-size: var(--text-sm);
  margin: 0;
}

.tabs {
  display: flex;
  gap: 8px;
  margin: 20px 0;
}

.tab {
  padding: 10px 18px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: var(--surface);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--forest-700);
  cursor: pointer;
}

.tab.active {
  background: var(--forest-600);
  color: white;
  border-color: var(--forest-600);
}
</style>