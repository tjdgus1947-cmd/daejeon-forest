"""
DB 연결 설정
- SQLite 파일 기반 DB (별도 DB 서버 불필요, RFP II-2 요구사항)
- DB 경로는 .env 의 DATABASE_URL 로 관리 (하드코딩 금지, RFP III-5-나)
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./localhub.db")

# SQLite는 기본적으로 단일 스레드만 허용하므로 FastAPI(멀티스레드)에서는 옵션 필요
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """요청마다 DB 세션을 열고, 끝나면 반드시 닫는다."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
