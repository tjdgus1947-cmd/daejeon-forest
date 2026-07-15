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

// 💡 [핵심 변경] 처음 마운트 시 빈 Set으로 시작하여 "모든 핀이 숨겨진 상태"로 출발합니다!
const activeCategories = ref(new Set());
const locations = ref([]);
const loading = ref(false);
const errorMsg = ref("");

const CATEGORY_HEX_COLORS = {
  "관광지": "#3B82F6",
  "문화시설": "#A855F7",
  "축제공연행사": "#F59E0B",
  "여행코스": "#10B981",
  "레포츠": "#059669",
  "숙박": "#EF4444",
  "쇼핑": "#EC4899",
  "음식점": "#DC2626"
};

function kakaoSearchUrl(title, addr) {
  const q = encodeURIComponent(`${title} ${addr || ""}`.trim());
  return `https://map.kakao.com/link/search/${q}`;
}

function resolvedColor(category) {
  return CATEGORY_HEX_COLORS[category] || "#6b9080"; 
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
    if (!response.ok) throw new Error("JSON 파일을 찾지 못했거나 가져오지 못했습니다.");
    
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
        fillColor: isCurrentGu ? '#e8f5e9' : '#ffffff',
        fillOpacity: isCurrentGu ? 0.35 : 0.1
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
            fillColor: '#c8e6c9',
            fillOpacity: 0.4,
            strokeColor: '#2f5233'
          });
        }
      });

      kakao.maps.event.addListener(polygon, 'mouseout', () => {
        if (name !== props.gu) {
          polygon.setOptions({
            fillColor: '#ffffff',
            fillOpacity: 0.1,
            strokeColor: '#888888'
          });
        }
      });

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

  // 💡 사용자가 선택해서 activeCategories Set에 추가된 카테고리 핀만 필터링해서 그립니다!
  const filtered = locations.value.filter((loc) =>
    activeCategories.value.has(loc.category)
  );

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

    const pinColor = resolvedColor(loc.category);
    const position = new kakao.maps.LatLng(lat, lng);

    const markerContent = document.createElement('div');
    markerContent.style.cssText = `
      width: 16px;
      height: 16px;
      background-color: ${pinColor};
      border: 2px solid #ffffff;
      border-radius: 50%;
      box-shadow: 0 2px 4px rgba(0,0,0,0.3);
      cursor: pointer;
    `;

    const customMarker = new kakao.maps.CustomOverlay({
      position: position,
      content: markerContent,
      yAnchor: 0.5
    });
    
    customMarker.setMap(map);
    currentMarkers.push(customMarker);

    const img = loc.image_url
      ? `<img src="${loc.image_url}" alt="${loc.title}" style="width:100%; max-height:100px; object-fit:cover; border-radius:6px; margin-bottom:6px;" />`
      : "";

    const overlayContent = document.createElement('div');
    overlayContent.className = 'kakaomap-popup';
    overlayContent.style.cssText = `
      position: absolute;
      bottom: 25px;
      left: 50%;
      transform: translateX(-50%);
      background: white;
      border: 1px solid #ccc;
      border-radius: 8px;
      padding: 10px;
      min-width: 180px;
      box-shadow: 0px 2px 6px rgba(0,0,0,0.2);
      font-family: Pretendard, sans-serif;
      z-index: 10;
      display: none;
    `;
    overlayContent.innerHTML = `
      <div style="position:relative;">
        <button class="close-btn" style="position:absolute; top:-4px; right:-2px; background:none; border:none; font-size:14px; cursor:pointer; color:#999;">×</button>
        ${img}
        <strong style="font-size:13px; display:block; margin-bottom:2px;">${loc.title}</strong>
        <span style="color:${pinColor}; font-weight:600; font-size:11px; display:block; margin-bottom:2px;">${loc.category}</span>
        <span style="font-size:11px; color:#666; display:block; margin-bottom:2px;">${loc.addr || "주소 정보 없음"}</span>
        <a href="${kakaoSearchUrl(loc.title, loc.addr)}" target="_blank" rel="noopener"
           style="font-size:11px; color:#2f5233; font-weight:600; text-decoration:none; display:inline-block; margin-top:4px;">
          카카오맵에서 상세보기 →
        </a>
      </div>
    `;

    const detailOverlay = new kakao.maps.CustomOverlay({
      position: position,
      content: overlayContent,
      yAnchor: 1
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

// 💡 [카테고리 누적 선택 토글 로직]
function toggleCategory(cat) {
  const next = new Set(activeCategories.value);
  if (next.has(cat)) {
    next.delete(cat); // 이미 켜져 있다면 해제하여 핀 숨기기
  } else {
    next.add(cat);    // 꺼져 있다면 Set에 더해서 핀 보이게 하기
  }
  activeCategories.value = next;
  renderMarkers(); // 상태가 바뀔 때마다 핀 렌더링 갱신
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
    
    await drawBoundaries();
    await fetchLocations();
    renderMarkers(); // 초기 빈 Set 기반으로 마커가 하나도 없는 깨끗한 지도 렌더링
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
      <p v-if="loading" class="status">불러오는 중…</p>
      <p v-if="errorMsg" class="status error">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<style scoped>
.map-wrap {
  display: flex;
  flex-direction: column;
  gap: 12px;
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
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: var(--surface);
  font-size: var(--text-xs);
  color: var(--forest-700);
  transition: opacity 0.15s, background-color 0.15s, border-color 0.15s;
  cursor: pointer;
}

/* 💡 선택 해제된(꺼진) 카테고리: 흐리게 톤다운 */
.legend-chip.inactive {
  opacity: 0.45;
  background: #f3f4f6; 
  border-color: #e5e7eb;
  color: #9ca3af;
}

/* 💡 선택되어 활성화된 카테고리: 선명한 테두리와 숲 배경 테마 적용 */
.legend-chip:not(.inactive) {
  background-color: var(--forest-50, #f4fbf7);
  border-color: var(--forest-300, #a3d9b9);
  color: var(--forest-900, #14532d);
  font-weight: 600;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--dot);
  display: inline-block;
}

/* 꺼진 카테고리의 핀 도트는 무채색 회색으로 다운 */
.legend-chip.inactive .dot {
  background: #d1d5db !important;
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
  padding: 8px 14px;
  background-color: rgba(255, 255, 255, 0.9);
  border: 1.5px solid #2f5233;
  border-radius: 20px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
  font-family: Pretendard, sans-serif;
  pointer-events: none;
}

.tree-icon {
  font-size: 15px;
}

.gu-name {
  font-size: 14px;
  font-weight: 700;
  color: #2f5233;
}

.kakao-map-el {
  height: 420px;
  width: 100%;
  border-radius: var(--radius-md);
  border: 1px solid var(--line);
}

.status {
  position: absolute;
  top: 12px;
  left: 12px;
  background: var(--surface);
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  box-shadow: var(--shadow-soft);
  z-index: 20;
}

.status.error {
  color: var(--danger);
}
</style>