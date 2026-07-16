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

// 🎯 현재 위치 마커를 추적하기 위한 변수
let myLocationMarker = null;

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

      // 💡 현재 선택된 구라면, 그 구의 경계 전체가 화면에 딱 맞게 보이도록 지도 범위 조정
      if (isCurrentGu) {
        const bounds = new kakao.maps.LatLngBounds();
        path.forEach((latlng) => bounds.extend(latlng));
        map.setBounds(bounds, 0,0,0,0);
      }


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
    
    overlayContent.innerHTML = `
      <div class="popup-box">
        <button class="close-btn">×</button>
        ${img}
        <div class="popup-body">
          <span class="popup-cat" style="color: ${pinColor};">${hangulCategory}</span>
          <strong class="popup-title">${loc.title}</strong>
          <span class="popup-addr">${loc.addr1 || "주소 정보 없음"}</span>
          <a href="${kakaoSearchUrl(loc.title, loc.addr1)}" target="_blank" rel="noopener noreferrer" class="popup-link">
            카카오맵으로 자세히 보기 →
          </a>
        </div>
      </div>
    `;

    const detailOverlay = new kakao.maps.CustomOverlay({
      position: position,
      content: overlayContent,
      yAnchor: 1.05
    });

    detailOverlay.setMap(map);
    currentCustomOverlays.push(detailOverlay);

    overlayContent.addEventListener('click', (e) => {
      e.stopPropagation();
    });
    overlayContent.addEventListener('touchstart', (e) => {
      e.stopPropagation();
    }, { passive: true });

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

function moveToCurrentLocation() {
  if (navigator.geolocation) {
    loading.value = true;
    
    const geoOptions = {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0
    };

    navigator.geolocation.getCurrentPosition(
      (position) => {
        loading.value = false;
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;

        const locPosition = new kakao.maps.LatLng(lat, lon);

        if (map) {
          if (myLocationMarker) {
            myLocationMarker.setMap(null);
          }

          const markerContent = document.createElement('div');
          markerContent.style.cssText = `
            width: 20px;
            height: 20px;
            background-color: #2e7d32;
            border: 3px solid #ffffff;
            border-radius: 50%;
            box-shadow: 0 0 10px rgba(46, 125, 50, 0.6);
            position: relative;
          `;
          
          const pulseRing = document.createElement('div');
          pulseRing.style.cssText = `
            position: absolute;
            top: -3px;
            left: -3px;
            width: 20px;
            height: 20px;
            border: 3px solid #2e7d32;
            border-radius: 50%;
            animation: gpsPulse 1.8s infinite ease-out;
            pointer-events: none;
          `;
          markerContent.appendChild(pulseRing);

          myLocationMarker = new kakao.maps.CustomOverlay({
            position: locPosition,
            content: markerContent,
            yAnchor: 0.5
          });

          myLocationMarker.setMap(map);
          map.panTo(locPosition);
          map.setLevel(4, { animate: true });
        }
      },
      (error) => {
        loading.value = false;
        console.error("위치 획득 실패:", error);
        alert("현재 위치 정보를 정확하게 가져올 수 없어유. 브라우저의 GPS가 켜져 있는지 확인해 보셔유!");
      },
      geoOptions
    );
  } else {
    alert("이 브라우저에서는 GPS 위치 서비스를 지원하지 않아유.");
  }
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
  if (myLocationMarker) {
    myLocationMarker.setMap(null);
  }
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
    <div class="map-header-bar">
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

      <button class="current-location-btn-outer" @click="moveToCurrentLocation" aria-label="현재 위치로 이동">
        <span class="gps-icon">🎯</span>
        <span class="gps-text">현재 위치</span>
      </button>
    </div>

    <div class="map-area">
      <div class="current-gu-badge">
        <span class="tree-icon">🌲</span>
        <span class="gu-name">{{ props.gu }}</span>
      </div>

      <div ref="mapEl" class="kakao-map-el"></div>
      <p v-if="loading" class="status">위치를 파악하고 있슈… 🌲</p>
      <p v-if="errorMsg" class="status error">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<style>
@keyframes gpsPulse {
  0% { transform: scale(1); opacity: 0.8; }
  100% { transform: scale(2.8); opacity: 0; }
}

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
  from { opacity: 0; transform: translateY(6px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

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
  top: 8px; right: 8px; width: 22px; height: 22px;
  background: rgba(255, 255, 255, 0.85);
  border-radius: 50%; border: none; font-size: 16px;
  cursor: pointer; color: #777;
  display: flex; align-items: center; justify-content: center;
  z-index: 10; box-shadow: 0 1px 4px rgba(0,0,0,0.1);
  transition: all 0.15s;
}

.popup-box .close-btn:hover {
  background: var(--forest-900, #122116);
  color: white;
}

.popup-img-wrap { width: 100%; height: 96px; overflow: hidden; background: #f3f5f3; }
.popup-img-wrap img { width: 100%; height: 100%; object-fit: cover; }
.popup-body { padding: 12px 14px 14px; display: flex; flex-direction: column; }
.popup-cat { font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 3px; }
.popup-title { font-size: 13px; font-weight: 700; color: var(--forest-900, #122116); margin-bottom: 4px; line-height: 1.35; }
.popup-addr { font-size: 11px; color: var(--moss-400, #557b6b); line-height: 1.4; margin-bottom: 8px; }
.popup-link { font-size: 11px; font-weight: 700; color: var(--forest-600, #25442a) !important; text-decoration: none; transition: transform 0.2s; }
.popup-link:hover { text-decoration: underline; transform: translateX(1px); }
</style>

<style scoped>
.map-wrap { display: flex; flex-direction: column; gap: 16px; }
.map-header-bar { display: flex; align-items: center; justify-content: space-between; gap: 12px; width: 100%; }
.legend { display: flex; flex-wrap: wrap; gap: 8px; flex: 1; }

.legend-chip {
  display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px;
  border-radius: 999px; border: 1.5px solid var(--line); background: var(--surface);
  font-size: var(--text-xs); color: var(--forest-700);
  transition: all 0.2s var(--ease-leaf); cursor: pointer; font-weight: 700;
}

.legend-chip.inactive {
  opacity: 0.55; background: #f1f3f0; border-color: #dbe0da; color: #8c968a;
}

.legend-chip:not(.inactive) {
  background-color: #f3f9f5; border-color: var(--forest-600); color: var(--forest-900);
  box-shadow: 0 4px 10px rgba(37, 68, 42, 0.06); transform: translateY(-1px);
}

html[data-theme="dark"] .legend-chip:not(.inactive) {
  background-color: var(--forest-600) !important; color: var(--surface) !important; border-color: var(--forest-600) !important;
}

html[data-theme="dark"] .legend-chip.inactive {
  background: var(--surface-alt) !important; border-color: var(--line) !important; color: var(--text-muted) !important;
}

.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--dot); display: inline-block; }
.legend-chip.inactive .dot { background: #9fa89d !important; }
.map-area { position: relative; }

.current-gu-badge {
  position: absolute; top: 16px; left: 16px; z-index: 10;
  display: flex; align-items: center; gap: 6px; padding: 8px 16px;
  background-color: rgba(255, 255, 255, 0.94); border: 1.5px solid var(--forest-600);
  border-radius: 999px; box-shadow: var(--shadow-lift); pointer-events: none;
}

/* 🌙 [추가] 야간 모드일 때 구 이름 배지 스타일 보완 */
html[data-theme="dark"] .current-gu-badge {
  background-color: var(--surface) !important;
  border-color: var(--line) !important;
}
html[data-theme="dark"] .gu-name {
  color: var(--text-main) !important;
}

.current-location-btn-outer {
  display: inline-flex; align-items: center; white-space: nowrap; gap: 6px; padding: 8px 16px;
  background-color: var(--surface); border: 1.5px solid var(--line); border-radius: 999px;
  box-shadow: var(--shadow-soft); font-family: 'Cafe24Surround', var(--font-body);
  font-size: 13px; font-weight: 800; color: var(--forest-700); cursor: pointer;
  transition: all 0.2s var(--ease-leaf);
}

.current-location-btn-outer:hover {
  transform: translateY(-1px); background-color: #f3f9f5; border-color: var(--forest-600); color: var(--forest-900);
  box-shadow: 0 4px 10px rgba(37, 68, 42, 0.06);
}

html[data-theme="dark"] .current-location-btn-outer:hover {
  background-color: var(--surface-alt) !important; color: var(--forest-600) !important;
}

.current-location-btn-outer:active { transform: translateY(0); }
.tree-icon, .gps-icon { font-size: 15px; }
.gu-name, .gps-text { font-size: 13px; font-weight: 800; }
.kakao-map-el { height: 440px; width: 100%; border-radius: var(--radius-lg); border: 1.5px solid var(--line); box-shadow: var(--shadow-soft); }

.status {
  position: absolute; top: 12px; left: 12px; background: var(--surface); padding: 8px 14px;
  border-radius: var(--radius-sm); font-size: var(--text-sm); box-shadow: var(--shadow-soft);
  z-index: 20; font-weight: 600; color: var(--forest-700);
}
.status.error { color: var(--danger); border-left: 4px solid var(--danger); }
</style>