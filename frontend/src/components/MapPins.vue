<script setup>
import { onMounted, onBeforeUnmount, watch, ref, nextTick } from "vue";
import { useRouter } from "vue-router";
import client from "../api/client";
import { CATEGORIES, categoryColor } from "../composables/districts";

const props = defineProps({
  gu: { type: String, required: true },
  center: { type: Object, required: true }, // { lat, lng }
});

const router = useRouter();
const mapEl = ref(null);
let map = null;
let currentMarkers = [];
let currentCustomOverlays = [];
const polygons = ref([]); 

// 처음 마운트 시 빈 Set으로 시작하여 "모든 핀이 숨겨진 상태"로 출발합니다!
const activeCategories = ref(new Set());
const locations = ref([]);
const loading = ref(false);
const errorMsg = ref("");

// 💡 백엔드 공공데이터 분류 코드(contenttypeid)를 한글 카테고리로 매핑
const CODE_TO_CATEGORY = {
  "12": "관광지",
  "14": "문화시설",
  "15": "축제공연행사",
  "28": "레포츠",
  "32": "숙박",
  "38": "쇼핑",
  "39": "음식점"
};

function kakaoSearchUrl(title, addr) {
  const q = encodeURIComponent(`${title} ${addr || ""}`.trim());
  return `https://map.kakao.com/link/search/${q}`;
}

function resolvedColor(category) {
  return categoryColor(category) || "#6b9080"; 
}

// 특정 좌표가 폴리곤 내부인지 판단 (Ray-Casting 알고리즘)
function isPointInPolygon(lat, lng, polygonPath) {
  let inside = false;
  const x = lng;
  const y = lat;

  for (let i = 0, j = polygonPath.length - 1; i < polygonPath.length; j = i++) {
    const xi = polygonPath[i].getLng(), yi = polygonPath[i].getLat();
    const xj = polygonPath[j].getLng(), yj = polygonPath[j].getLat();

    const intersect = ((yi > y) !== (yj > y))
        && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
    if (intersect) inside = !inside;
  }

  return inside;
}

function clearMarkers() {
  currentMarkers.forEach((m) => m.setMap(null));
  currentCustomOverlays.forEach((o) => o.setMap(null));
  currentMarkers = [];
  currentCustomOverlays = [];
}

function clearPolygons() {
  polygons.value.forEach((p) => p.polygonObj.setMap(null));
  polygons.value = [];
}

// 카카오맵 행정구역 경계선 그리기
async function drawBoundaries() {
  clearPolygons();
  try {
    const response = await fetch('/daejeon-boundary.json');
    if (!response.ok) throw new Error("JSON 파일을 찾지 못했습니다.");
    
    const geoData = await response.json();

    geoData.features.forEach((feature) => {
      const coordinates = feature.geometry.coordinates[0];
      const name = feature.properties.name;

      const path = coordinates.map(coord => new kakao.maps.LatLng(coord[1], coord[0]));
      const isCurrentGu = name === props.gu;

      const polygon = new kakao.maps.Polygon({
        path: path,
        strokeWeight: isCurrentGu ? 3 : 1.5,
        strokeColor: isCurrentGu ? '#2f5233' : '#888888',
        strokeOpacity: 0.8,
        fillColor: isCurrentGu ? '#e9f2eb' : '#ffffff',
        fillOpacity: isCurrentGu ? 0.3 : 0.1
      });

      polygon.setMap(map);
      
      polygons.value.push({
        guName: name,
        polygonObj: polygon
      });

      // 마우스 이벤트 바인딩
      kakao.maps.event.addListener(polygon, 'mouseover', () => {
        if (name !== props.gu) {
          polygon.setOptions({
            fillColor: '#d6edd8',
            fillOpacity: 0.4,
            strokeColor: '#2f5233'
          });
        }
      });

      // 마우스 아웃
      kakao.maps.event.addListener(polygon, 'mouseout', () => {
        if (name !== props.gu) {
          polygon.setOptions({
            fillColor: '#ffffff',
            fillOpacity: 0.1,
            strokeColor: '#888888'
          });
        }
      });

      // 클릭 시 해당 구로 이동
      kakao.maps.event.addListener(polygon, 'click', () => {
        if (name !== props.gu) {
          router.push({ name: 'district', params: { gu: name } });
        }
      });
    });

  } catch (e) {
    console.error("행정구역 데이터를 불러오지 못했습니다.", e);
  }
}

// 핀 렌더링 함수
function renderMarkers() {
  if (!map) return;
  clearMarkers();

  const filtered = locations.value.filter((loc) => {
    const hangulCategory = CODE_TO_CATEGORY[loc.contenttypeid] || "기타";
    return activeCategories.value.has(hangulCategory);
  });

  const activePolygonWrap = polygons.value.find(p => p.guName === props.gu);

  filtered.forEach((loc) => {
    const lat = parseFloat(loc.mapy);
    const lng = parseFloat(loc.mapx);
    if (Number.isNaN(lat) || Number.isNaN(lng)) return;

    if (activePolygonWrap) {
      const path = activePolygonWrap.polygonObj.getPath();
      const isInside = isPointInPolygon(lat, lng, path);
      if (!isInside) return;
    }

    const hangulCategory = CODE_TO_CATEGORY[loc.contenttypeid] || "기타";
    const pinColor = resolvedColor(hangulCategory);
    const position = new kakao.maps.LatLng(lat, lng);

    const markerContent = document.createElement('div');
    markerContent.style.cssText = `
      width: 18px;
      height: 18px;
      background-color: ${pinColor};
      border: 2.5px solid #ffffff;
      border-radius: 50%;
      box-shadow: 0 3px 6px rgba(0,0,0,0.22);
      cursor: pointer;
      transition: transform 0.2s ease;
    `;
    
    // 마우스 호버 시 핀 크기 업 이펙트
    markerContent.addEventListener('mouseenter', () => {
      markerContent.style.transform = 'scale(1.25)';
    });
    markerContent.addEventListener('mouseleave', () => {
      markerContent.style.transform = 'scale(1)';
    });

    const customMarker = new kakao.maps.CustomOverlay({
      position: position,
      content: markerContent,
      yAnchor: 0.5
    });
    
    customMarker.setMap(map);
    currentMarkers.push(customMarker);

    const img = loc.firstimage
      ? `<div class="popup-img-wrap"><img src="${loc.firstimage}" alt="${loc.title}" /></div>`
      : "";

    const overlayContent = document.createElement('div');
    overlayContent.className = 'kakaomap-popup';
    
    // 💡 [디자인 혁신] 인라인 style.cssText를 과감히 제거하고 전용 스코프 스타일 클래스로 대체합니다!
    overlayContent.innerHTML = `
      <div class="popup-box">
        <button class="close-btn">×</button>
        ${img}
        <div class="popup-body">
          <span class="popup-cat" style="color: ${pinColor};">${hangulCategory}</span>
          <strong class="popup-title">${loc.title}</strong>
          <span class="popup-addr">${loc.addr1 || "주소 정보 없음"}</span>
          <a href="${kakaoSearchUrl(loc.title, loc.addr1)}" target="_blank" class="popup-link">
            카카오맵으로 자세히 보기 →
          </a>
        </div>
      </div>
    `;

    const detailOverlay = new kakao.maps.CustomOverlay({
      position: position,
      content: overlayContent,
      yAnchor: 1.05 // 핀의 바로 윗 공간에 정렬되도록 오프셋 조절
    });

    detailOverlay.setMap(map);
    currentCustomOverlays.push(detailOverlay);

    markerContent.addEventListener('click', () => {
      document.querySelectorAll('.kakaomap-popup').forEach(el => el.style.display = 'none');
      overlayContent.style.display = 'block';
    });

    overlayContent.querySelector('.close-btn').addEventListener('click', () => {
      overlayContent.style.display = 'none';
    });
  });
}

async function fetchLocations() {
  loading.value = true;
  errorMsg.value = "";
  try {
    const { data } = await client.get("/api/locations", {
      params: { gu: props.gu },
    });
    locations.value = data;
  } catch (e) {
    errorMsg.value = "장소 데이터를 불러오지 못했어요. 잠시 후 다시 시도해주세요.";
  } finally {
    loading.value = false;
  }
}

// 카테고리 누적 선택 토글 로직
function toggleCategory(cat) {
  const next = new Set(activeCategories.value);
  if (next.has(cat)) {
    next.delete(cat); 
  } else {
    next.add(cat);    
  }
  activeCategories.value = next;
  renderMarkers(); 
}

onMounted(async () => {
  await nextTick();
  
  if (typeof kakao !== 'undefined' && kakao.maps) {
    const container = mapEl.value;
    const options = {
      center: new kakao.maps.LatLng(props.center.lat, props.center.lng),
      level: 5
    };
    
    map = new kakao.maps.Map(container, options);
    
    kakao.maps.event.addListener(map, 'click', () => {
      document.querySelectorAll('.kakaomap-popup').forEach(el => el.style.display = 'none');
    });
    
    await drawBoundaries();
    await fetchLocations();
    renderMarkers(); 
  } else {
    errorMsg.value = "카카오 지도 API가 로드되지 않았습니다. index.html 설정을 확인해 주세요.";
  }
});

onBeforeUnmount(() => {
  clearMarkers();
  clearPolygons();
});

watch(
  () => props.gu,
  async () => {
    if (map && props.center) {
      const moveLatLon = new kakao.maps.LatLng(props.center.lat, props.center.lng);
      map.panTo(moveLatLon);
      map.setLevel(5); 
      
      await drawBoundaries();
      await fetchLocations();
      renderMarkers();
    }
  }
);
</script>

<template>
  <div class="map-wrap">
    <div class="legend">
      <button
        v-for="cat in CATEGORIES"
        :key="cat"
        class="legend-chip"
        :class="{ inactive: !activeCategories.has(cat) }"
        :style="{ '--dot': categoryColor(cat) }"
        @click="toggleCategory(cat)"
      >
        <span class="dot"></span>{{ cat }}
      </button>
    </div>

    <div class="map-area">
      <div class="current-gu-badge">
        <span class="tree-icon">🌲</span>
        <span class="gu-name">{{ props.gu }}</span>
      </div>

      <div ref="mapEl" class="kakao-map-el"></div>
      <p v-if="loading" class="status">숲 구석구석을 둘러보는 중…</p>
      <p v-if="errorMsg" class="status error">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<style>
/* 🌿 카카오 오버레이 전용 스타일 (상위 scoped 스코프 제약을 해제하여 맵 내부에 안전하게 전파) */
.kakaomap-popup {
  display: none;
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
}

.popup-box {
  position: relative;
  background: white;
  border-radius: var(--radius-md, 14px);
  width: 200px;
  box-shadow: 0 10px 24px rgba(18, 33, 22, 0.16);
  border: 1px solid var(--line, #dbe4d8);
  overflow: hidden;
  animation: popupScale 0.25s var(--ease-leaf, cubic-bezier(0.16, 1, 0.3, 1));
}

@keyframes popupScale {
  from {
    opacity: 0;
    transform: translateY(6px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 팝업 하단 말풍선 삼각 꼬리말 제작 */
.popup-box::after {
  content: "";
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%) rotate(45deg);
  width: 12px;
  height: 12px;
  background: white;
  border-right: 1px solid var(--line, #dbe4d8);
  border-bottom: 1px solid var(--line, #dbe4d8);
}

.popup-box .close-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 22px;
  height: 22px;
  background: rgba(255, 255, 255, 0.85);
  border-radius: 50%;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #777;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1);
  transition: all 0.15s;
}

.popup-box .close-btn:hover {
  background: var(--forest-900, #122116);
  color: white;
}

.popup-img-wrap {
  width: 100%;
  height: 96px;
  overflow: hidden;
  background: #f3f5f3;
}

.popup-img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.popup-body {
  padding: 12px 14px 14px;
  display: flex;
  flex-direction: column;
}

.popup-cat {
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 3px;
}

.popup-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--forest-900, #122116);
  margin-bottom: 4px;
  line-height: 1.35;
}

.popup-addr {
  font-size: 11px;
  color: var(--moss-400, #557b6b);
  line-height: 1.4;
  margin-bottom: 8px;
}

.popup-link {
  font-size: 11px;
  font-weight: 700;
  color: var(--forest-600, #25442a) !important;
  text-decoration: none;
  transition: transform 0.2s;
}

.popup-link:hover {
  text-decoration: underline;
  transform: translateX(1px);
}
</style>

<style scoped>
.map-wrap {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.legend-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 999px;
  border: 1.5px solid var(--line);
  background: var(--surface);
  font-size: var(--text-xs);
  color: var(--forest-700);
  transition: all 0.2s var(--ease-leaf);
  cursor: pointer;
  font-weight: 700;
}

/* 🌿 비활성화 상태의 모던한 그레이시-아웃 처리 */
.legend-chip.inactive {
  opacity: 0.55;
  background: #f1f3f0; 
  border-color: #dbe0da;
  color: #8c968a;
}

/* 🌿 선택 시 싱그러운 카테고리별 포인트 입체감 확보 */
.legend-chip:not(.inactive) {
  background-color: #f3f9f5;
  border-color: var(--forest-600);
  color: var(--forest-900);
  box-shadow: 0 4px 10px rgba(37, 68, 42, 0.06);
  transform: translateY(-1px);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--dot);
  display: inline-block;
}

.legend-chip.inactive .dot {
  background: #9fa89d !important;
}

.map-area {
  position: relative;
}

.current-gu-badge {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background-color: rgba(255, 255, 255, 0.94);
  border: 1.5px solid var(--forest-600);
  border-radius: 999px;
  box-shadow: var(--shadow-lift);
  pointer-events: none;
}

.tree-icon {
  font-size: 15px;
}

.gu-name {
  font-size: 13px;
  font-weight: 800;
  color: var(--forest-600);
}

.kakao-map-el {
  height: 440px;
  width: 100%;
  border-radius: var(--radius-lg);
  border: 1.5px solid var(--line);
  box-shadow: var(--shadow-soft);
}

.status {
  position: absolute;
  top: 12px;
  left: 12px;
  background: var(--surface);
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  box-shadow: var(--shadow-soft);
  z-index: 20;
  font-weight: 600;
  color: var(--forest-700);
}

.status.error {
  color: var(--danger);
  border-left: 4px solid var(--danger);
}
</style>