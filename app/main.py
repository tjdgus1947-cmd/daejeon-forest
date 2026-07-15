"""
FastAPI 앱 진입점
실행: uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import posts, locations, chat

# 최초 실행 시 테이블 자동 생성 (SQLite 파일 기반, 별도 서버/마이그레이션 불필요)
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

app.include_router(posts.router)
app.include_router(locations.router)
app.include_router(chat.router)


@app.get("/")
def health_check():
    """배포 후 살아있는지 확인용 (Render 콜드스타트 확인에도 사용)"""
    return {"status": "ok", "service": "localhub-daejeon-backend"}
