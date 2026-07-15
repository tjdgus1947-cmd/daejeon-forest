"""
챗봇 API (RFP III-3)
- POST /api/chat: 제공 JSON(=DB에 적재된 locations/posts) 기반 자연어 지역 정보 질의응답
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
    """아주 단순한 키워드 기반 검색 (title/addr/category에 매칭)"""
    like = f"%{query}%"
    results = (
        db.query(models.Location)
        .filter(
            (models.Location.title.like(like))
            | (models.Location.addr.like(like))
            | (models.Location.category.like(like))
        )
        .limit(limit)
        .all()
    )
    # 매칭이 없으면 카테고리 키워드로 폭넓게 재시도 (예: "맛집" -> "음식점")
    if not results:
        keyword_map = {
            "맛집": "음식점", "밥집": "음식점", "식당": "음식점",
            "축제": "축제공연행사", "행사": "축제공연행사",
            "숙소": "숙박", "호텔": "숙박",
            "놀거리": "레포츠", "액티비티": "레포츠",
            "구경": "관광지", "여행": "관광지",
        }
        for kw, cat in keyword_map.items():
            if kw in query:
                results = (
                    db.query(models.Location)
                    .filter(models.Location.category == cat)
                    .limit(limit)
                    .all()
                )
                break
    return results


def _search_posts(db: Session, query: str, limit: int = 5):
    """커뮤니티 게시글 검색 (RFP III-3-나 '커뮤니티 게시글 검색' 대응)"""
    like = f"%{query}%"
    return (
        db.query(models.Post)
        .filter((models.Post.title.like(like)) | (models.Post.content.like(like)))
        .order_by(models.Post.created_at.desc())
        .limit(limit)
        .all()
    )


def _build_context(locations, posts) -> str:
    lines = []
    if locations:
        lines.append("[장소 정보]")
        for loc in locations:
            lines.append(f"- {loc.title} | {loc.category} | {loc.addr} | 전화: {loc.tel or '정보없음'}")
    if posts:
        lines.append("[관련 게시글]")
        for p in posts:
            lines.append(f"- 제목: {p.title} / 내용요약: {p.content[:60]}")
    if not lines:
        lines.append("검색된 데이터가 없습니다. 사용자에게 다른 키워드로 질문해달라고 안내하세요.")
    return "\n".join(lines)


@router.post("", response_model=schemas.ChatResponse)
def chat(payload: schemas.ChatRequest, db: Session = Depends(get_db)):
    locations = _search_locations(db, payload.message)
    posts = _search_posts(db, payload.message)
    context = _build_context(locations, posts)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    # 대화 히스토리 유지 (RFP III-3-다)
    messages.extend(payload.history[-6:])  # 최근 6턴만 유지 (토큰/비용 관리)
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
        model="gpt-4o-mini",  # 비용 절감을 위해 mini 모델 사용 (예산 제약, RFP II-2)
        messages=messages,
        temperature=0.3,
        max_tokens=400,
    )
    reply = response.choices[0].message.content
    return schemas.ChatResponse(reply=reply)
