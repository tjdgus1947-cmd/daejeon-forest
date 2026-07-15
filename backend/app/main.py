"""
FastAPI 앱 진입점
실행: uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import board, locations, chat

# PostgreSQL 사용 (은아 DB). 테이블은 이미 01_create_tables.sql로 생성되어 있으므로
# create_all은 누락된 테이블만 보완 생성하는 역할 (기존 테이블/데이터는 영향 없음)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="모여라 대전의 숲 API",
    description="LocalHub - 대전 지역 정보 공유 커뮤니티 백엔드",
    version="0.1.0",
)

# Netlify(프론트)와 Render(백엔드)가 다른 도메인이므로 CORS 허용 필요
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 배포 시 실제 Netlify 도메인으로 제한 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(board.router)
app.include_router(locations.router)
app.include_router(chat.router)


@app.get("/")
def health_check():
    """배포 후 살아있는지 확인용 (Render 콜드스타트 확인에도 사용)"""
    return {"status": "ok", "service": "localhub-daejeon-backend"}