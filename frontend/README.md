# 모여라 대전의 숲 - Frontend

Vue 3 + Vite 기반 SPA. 백엔드(FastAPI)와 REST API로 통신합니다.

## 화면 흐름

```
/                      랜딩 (닉네임 입력, 로그인 아님)
/districts             대전 5개 구 선택
/gu/:gu                구 상세 (지도 탭 / 게시판 탭 + 챗봇 위젯)
/gu/:gu/posts/new       게시글 작성
/gu/:gu/posts/:id       게시글 상세 (댓글, 수정/삭제)
/gu/:gu/posts/:id/edit  게시글 수정 (비밀번호 확인 후 진입)
```

## 1. 설치

```bash
npm install
```

## 2. 환경변수 설정

```bash
cp .env.example .env
# VITE_API_BASE_URL 을 로컬 백엔드 주소(기본 http://127.0.0.1:8000)로 확인/수정
```

## 3. 개발 서버 실행

백엔드(FastAPI)가 먼저 `8000` 포트에서 떠 있어야 합니다.

```bash
npm run dev
```

http://localhost:5173 에서 확인

## 4. 프로덕션 빌드

```bash
npm run build   # dist/ 폴더 생성
npm run preview # 빌드 결과 미리보기
```

## 5. 배포 (Netlify)

1. Netlify에서 New site from Git → 이 repo 연동
2. Build command: `npm run build`
3. Publish directory: `dist`
4. Environment variables에 `VITE_API_BASE_URL` = Render 백엔드 배포 URL 등록

## 6. 디자인 시스템

- 컨셉: "다섯 그루의 나무가 이룬 숲" — 대전 5개 구를 그로브(숲 구역)로 표현
- 컬러/타이포 토큰: `src/styles/tokens.css`
- 헤드라인: Noto Serif KR / 본문·UI: Pretendard
- 카테고리 8종(관광지·문화시설·축제공연행사·여행코스·레포츠·숙박·쇼핑·음식점)은 각각 고유 색상을 가지며 지도 핀·범례·게시판 태그에 공용으로 사용됩니다 (`src/composables/districts.js`)

## 7. 지도 관련 참고

- 현재는 Leaflet + OpenStreetMap(무료, API 키 불필요)으로 구현되어 있습니다.
- 카카오맵은 지도 핀 클릭 시 "카카오맵에서 상세보기" 딥링크(검색 URL)로만 연결되며, 별도 SDK 키가 필요하지 않습니다.
- 팀에서 카카오맵 SDK로 직접 지도를 그리고 싶다면 `src/components/MapPins.vue`의 Leaflet 초기화 부분만 교체하면 됩니다.

## 8. 주의사항 (RFP 필수 준수사항)

- `.env`는 절대 커밋하지 않는다 (`.gitignore`에 이미 등록됨)
- 닉네임은 `sessionStorage`에만 저장되며 회원가입/로그인이 아니다 (탭을 닫으면 사라짐)
- 게시글 비밀번호는 평문으로 서버에 전송/비교된다 (교육 목적 의도된 설계, 백엔드와 동일)
