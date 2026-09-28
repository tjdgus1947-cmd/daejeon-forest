# 모여라 대전의 숲

대전 5개 구의 관광지·음식점·축제 정보를 지도에서 보고, 장소별로 글을 남기고, 챗봇에게 물어볼 수 있는 지역 커뮤니티입니다.

SSAFY 16기 스타트캠프 팀 프로젝트 (2026.07.14 ~ 07.16, 3인)

## 주요 기능

- **구별 지도**: 대전 5개 구를 고르면 카테고리(관광지·음식점·축제 등)별 장소가 지도 핀으로 표시됩니다.
- **게시판**: 로그인 없이 비밀번호로 작성·수정·삭제하는 장소 후기 게시판과 댓글
- **지역 챗봇**: 질문에서 카테고리와 키워드를 뽑아 DB에서 장소를 찾고, 그 결과만 근거로 GPT가 답합니다.

## 기술 스택

| 영역 | 사용 기술 |
|---|---|
| Backend | FastAPI, SQLAlchemy, PostgreSQL |
| Frontend | Vue 3, Vite, Vue Router, 카카오맵 JS SDK |
| AI | OpenAI API |
| 배포 | Render(백엔드), Netlify(프론트) |

## 데이터 흐름

```
TourAPI 대전·충청권 JSON (8종)
  → 주소가 "대전"으로 시작하는 항목만 필터링, 구 이름 파싱
  → PostgreSQL location 테이블 적재
  → 지도 핀 API / 챗봇 검색에 사용
```

- 테이블 생성: `make_db/01_create_tables.sql` (location, board, comment, 챗봇 테이블)
- 적재 스크립트: `make_db/02_insert_data.py`, `backend/app/seed_data.py`

### 챗봇 동작

1. 질문에서 조사를 떼고, 키워드를 카테고리로 매핑합니다 (예: "맛집" → 음식점).
2. 구·카테고리·키워드로 location 테이블을 검색해 최대 5건을 가져옵니다.
3. 검색 결과만 시스템 프롬프트에 넣어 GPT에 답변을 요청합니다. DB에 없는 장소를 지어내지 않게 하기 위해서입니다.

## 폴더 구조

```
backend/     FastAPI 서버 (routers: board, locations, chat)
frontend/    Vue 3 앱 (구 선택 → 지도 → 게시판, 챗봇 위젯)
make_db/     테이블 생성 SQL, 데이터 적재 스크립트
data_og/     TourAPI 원본 JSON
```

## 실행

```bash
# 백엔드
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # DATABASE_URL, OPENAI_API_KEY 입력
uvicorn app.main:app --reload    # http://127.0.0.1:8000/docs

# 프론트엔드
cd frontend
npm install
npm run dev
```

API 목록은 `backend/README.md`에 있습니다.

## 팀 구성

| 이름 | 역할 |
|---|---|
| 김성현 | 장소 API, 게시판 API 일부, 프론트 지도·목록 화면, 챗봇 연동, 배포, 저장소 관리 |
| 조은아 | DB 설계·데이터 적재, 게시판 API·모델, 프론트 디자인, 챗봇 UI |
| 신현준 | 챗봇 로직(`backend/app/routers/chat.py`) |

## 알려진 한계

- 게시글 비밀번호는 과제 요구사항(RFP)에 따라 평문으로 저장합니다. 실서비스라면 해시로 저장해야 합니다.
- CORS가 전체 허용(`*`)입니다. 배포 도메인으로 제한해야 합니다.
- 챗봇 검색은 키워드 일치 기반이라 표현이 조금만 달라도 결과가 비어 있을 수 있습니다.
