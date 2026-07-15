/**
 * 대전 5개 구 — 구별 대표 좌표는 시청/구청 인근 근사치입니다.
 * (지도 초기 중심점 용도이며, 실제 핀은 locations API 데이터 좌표를 사용합니다)
 */
export const DISTRICTS = [
  { name: "동구", lat: 36.3115, lng: 127.4547, blurb: "대전역과 원도심을 품은 숲" },
  { name: "중구", lat: 36.3253, lng: 127.4148, blurb: "행정과 시장이 어우러진 자리" },
  { name: "서구", lat: 36.3555, lng: 127.3838, blurb: "번화가와 주거가 함께 자란 곳" },
  { name: "유성구", lat: 36.3623, lng: 127.3560, blurb: "과학과 온천이 만나는 숲" },
  { name: "대덕구", lat: 36.3466, lng: 127.4149, blurb: "대덕특구를 품은 조용한 구역" },
];

export const CATEGORIES = [
  "관광지",
  "문화시설",
  "축제공연행사",
  "여행코스",
  "레포츠",
  "숙박",
  "쇼핑",
  "음식점",
];

/** 게시판 글의 말머리(카테고리). 장소 카테고리(CATEGORIES)와는 별개입니다. */
export const POST_CATEGORIES = ["자유", "질문", "정보", "동네소식", "모임"];

export function categoryColor(category) {
  const map = {
    관광지: "var(--cat-관광지)",
    문화시설: "var(--cat-문화시설)",
    축제공연행사: "var(--cat-축제공연행사)",
    여행코스: "var(--cat-여행코스)",
    레포츠: "var(--cat-레포츠)",
    숙박: "var(--cat-숙박)",
    쇼핑: "var(--cat-쇼핑)",
    음식점: "var(--cat-음식점)",
  };
  return map[category] || "var(--moss-400)";
}
