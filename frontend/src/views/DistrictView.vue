<script setup>
import { ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import MapPins from "../components/MapPins.vue";
import BoardList from "../components/BoardList.vue";
import { getDistrictCenter } from "../composables/districts";

const route = useRoute();
const router = useRouter();

// 1. URL 파라미터에서 'gu'(예: 유성구, 동구)를 가져옵니다.
const gu = ref(route.params.gu || "동구");
const center = ref(getDistrictCenter(gu.value) || { lat: 36.3504, lng: 127.3845 });

// 🚀 [탭 연동 핵심] 주소창에 ?tab=board가 있으면 'board'(게시판)를 띄우고, 없으면 'map'(지도)을 기본값으로 설정합니다.
const activeTab = ref(route.query.tab || "map");

// 2. 탭 전환 함수: 클릭 시 메모리의 activeTab만 바꾸는 것이 아니라, URL의 쿼리 스트링도 함께 업데이트합니다.
function changeTab(tabName) {
  activeTab.value = tabName;
  router.replace({
    query: { ...route.query, tab: tabName }
  });
}

// 3. 사용자가 브라우저 '뒤로가기'를 누르거나 라우터가 바뀔 때, URL의 쿼리를 감시해서 탭 상태를 실시간 동기화합니다.
watch(
  () => route.query.tab,
  (newTab) => {
    if (newTab) {
      activeTab.value = newTab;
    } else {
      activeTab.value = "map"; // 쿼리가 없으면 기본 탭인 지도로 지정
    }
  }
);

// 4. 구(District)가 바뀔 때 센터 정보도 업데이트하는 기존 로직 유지
watch(
  () => route.params.gu,
  (newGu) => {
    if (newGu) {
      gu.value = newGu;
      center.value = getDistrictCenter(newGu);
    }
  }
);
</script>

<template>
  <div class="district-page">
    <div class="tab-header">
      <div class="tab-buttons">
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'map' }"
          @click="changeTab('map')"
        >
          🗺️ 지도
        </button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'board' }"
          @click="changeTab('board')"
        >
          📝 게시판
        </button>
      </div>
    </div>
    <div class="tab-content">
      <div v-show="activeTab === 'map'">
        <MapPins :gu="gu" :center="center" />
      </div>

      <div v-show="activeTab === 'board'">
        <BoardList :gu="gu" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.district-page {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
.tab-header {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 2px solid #e2e8f0;
}
.tab-buttons {
  display: flex;
  gap: 12px;
}
.tab-btn {
  padding: 10px 20px;
  font-size: 16px;
  font-weight: bold;
  background: none;
  border: none;
  cursor: pointer;
  color: #718096;
  border-bottom: 3px solid transparent;
  transition: all 0.2s ease;
}
.tab-btn.active {
  color: #2f5233;
  border-bottom-color: #2f5233;
}
.tab-content {
  margin-top: 15px;
}
</style>
