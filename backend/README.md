# 모여라 대전의 숲 - Backend

FastAPI + PostgreSQL + SQLAlchemy 기반 백엔드

## 1. 설치

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. 환경변수 설정

```bash
cp .env.example .env
# .env 파일 열어서 OPENAI_API_KEY 채우기
```

## 3. 데이터 적재 (최초 1회)

제공받은 대전_충청권 JSON 파일들을 `data/` 폴더에 넣은 뒤 실행합니다. (이미 8개 파일 포함되어 있음)

```bash
python -m app.seed_data
```

실행하면 `localhub.db` 파일이 생성되고, 대전광역시 데이터만 필터링되어 `locations` 테이블에 적재됩니다.

## 4. 서버 실행

```bash
uvicorn app.main:app --reload
```

- API 문서(Swagger): http://127.0.0.1:8000/docs
- 헬스체크: http://127.0.0.1:8000/

## 5. 주요 엔드포인트

| Method | URL | 설명 |
|---|---|---|
| GET | `/api/posts` | 게시글 목록 (gu, category, keyword, page, size 쿼리 지원) |
| GET | `/api/posts/{id}` | 게시글 상세 (조회수 +1) |
| POST | `/api/posts` | 게시글 작성 |
| POST | `/api/posts/{id}/verify` | 수정/삭제 전 비밀번호 확인 |
| PUT | `/api/posts/{id}` | 게시글 수정 (password 필요) |
| DELETE | `/api/posts/{id}` | 게시글 삭제 (password 필요) |
| POST | `/api/posts/{id}/comments` | 댓글 작성 |
| GET | `/api/locations` | 장소 목록 (gu, category 필터) — 지도 핀용 |
| GET | `/api/locations/gu-list` | 구 목록 |
| GET | `/api/locations/categories` | 카테고리 목록 |
| POST | `/api/chat` | 챗봇 질의응답 |

## 6. 배포 (Render)

1. Render에서 New Web Service → 이 repo 연동
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Environment Variables에 `OPENAI_API_KEY`, `DATABASE_URL` 등록 (`.env` 파일 자체는 올리지 않음)
5. 배포 후 최초 1회 `python -m app.seed_data` 를 Render Shell에서 실행하거나, 배포 전 로컬에서 만든 `localhub.db`를 함께 커밋(단, RFP 산출물 제출 규정상 DB 파일은 별도 제출이므로 레포에는 미포함 권장)

## 7. 주의사항 (RFP 필수 준수사항)

- `.env` 파일은 절대 커밋하지 않는다 (`.gitignore`에 이미 등록됨)
- 게시글 비밀번호는 의도적으로 평문 저장/비교한다 (실서비스 패턴 아님, 교육 목적 설계)
- 회원가입/로그인 기능은 구현하지 않는다
