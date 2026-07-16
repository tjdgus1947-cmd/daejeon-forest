"""
챗봇 API (RFP III-3)
- POST /api/chat: 제공 JSON(=DB에 적재된 locations/boards) 기반 자연어 지역 정보 질의응답
- 주요 질의 유형: 관광지/맛집 추천, 축제 일정, 모범음식점 위치, 커뮤니티 게시글 검색
- 정확한 최신 데이터 답변을 위해 "DB 검색 결과를 컨텍스트로 넣고 LLM이 자연어로 정리"하는
  간단한 RAG(검색 증강 생성) 구조를 사용한다. (임베딩 없이 키워드 매칭으로 단순화 — 3일 일정 고려)
"""
import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from openai import OpenAI

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/chat", tags=["chat"])

_client: OpenAI | None = None

# TourAPI contenttypeid 코드 -> 한글 키워드 매핑 (실제 데이터 값 확인 후 조정 필요)
CATEGORY_MAP = {
    "맛집": "39", "밥집": "39", "식당": "39",
    "축제": "15", "행사": "15",
    "숙소": "32", "호텔": "32",
    "놀거리": "28", "액티비티": "28",
    "구경": "12", "여행": "12",
}


def get_openai_client() -> OpenAI:
    """OpenAI 클라이언트를 요청 시점에 생성(lazy init).
    모듈 임포트 시점에 생성하면 .env 로딩 전이거나 키가 없을 때 서버 전체가 뜨지 않는 문제가 있어 회피."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY가 .env에 설정되어 있지 않습니다.")
        _client = OpenAI(api_key=api_key)
    return _client

SYSTEM_PROMPT = """당신은 '모여라 대전의 숲' 서비스의 지역 정보 안내 챗봇입니다.
아래 규칙을 반드시 지키세요.
1. 반드시 제공된 [검색된 데이터] 안의 정보만 근거로 답변하세요. 모르면 모른다고 답하세요.
2. 장소를 추천할 때는 이름과 주소를 함께 안내하세요.
3. 친근한 존댓말로, 3~5문장 이내로 간결하게 답변하세요.
"""


def _search_locations(db: Session, query: str, limit: int = 5):
    """아주 단순한 키워드 기반 검색 (title/addr1/contenttypeid에 매칭)"""
    like = f"%{query}%"
    results = (
        db.query(models.Location)
        .filter(
            (models.Location.title.like(like))
            | (models.Location.addr1.like(like))
        )
        .limit(limit)
        .all()
    )
    # 매칭이 없으면 카테고리 키워드로 폭넓게 재시도 (예: "맛집" -> contenttypeid "39")
    if not results:
        for kw, code in CATEGORY_MAP.items():
            if kw in query:
                results = (
                    db.query(models.Location)
                    .filter(models.Location.contenttypeid == code)
                    .limit(limit)
                    .all()
                )
                break
    return results


def _search_boards(db: Session, query: str, limit: int = 5):
    """커뮤니티 게시글 검색 (RFP III-3-나 '커뮤니티 게시글 검색' 대응)"""
    like = f"%{query}%"
    return (
        db.query(models.Board)
        .filter((models.Board.title.like(like)) | (models.Board.content.like(like)))
        .order_by(models.Board.created_at.desc())
        .limit(limit)
        .all()
    )


def _build_context(locations, boards) -> str:
    lines = []
    if locations:
        lines.append("[장소 정보]")
        for loc in locations:
            lines.append(f"- {loc.title} | {loc.addr1} | 전화: {loc.tel or '정보없음'}")
    if boards:
        lines.append("[관련 게시글]")
        for b in boards:
            lines.append(f"- 제목: {b.title} / 내용요약: {b.content[:60]}")
    if not lines:
        lines.append("검색된 데이터가 없습니다. 사용자에게 다른 키워드로 질문해달라고 안내하세요.")
    return "\n".join(lines)


@router.post("", response_model=schemas.ChatResponse)
def chat(payload: schemas.ChatRequest, db: Session = Depends(get_db)):
    locations = _search_locations(db, payload.message)
    boards = _search_boards(db, payload.message)
    context = _build_context(locations, boards)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(payload.history[-6:])
    messages.append(
        {
            "role": "user",
            "content": f"[검색된 데이터]\n{context}\n\n[사용자 질문]\n{payload.message}",
        }
    )

    try:
        client = get_openai_client()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=400,
    )
    reply = response.choices[0].message.content
    return schemas.ChatResponse(reply=reply)