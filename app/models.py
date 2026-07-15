"""
SQLAlchemy 모델
- Post: 익명 게시판 글 (III-2). 비밀번호는 평문 저장/비교 — 교육 목적 의도된 설계(III-2-나)
- Comment: 게시글 댓글 (RFP III-5-가 스키마 예시에 포함)
- Location: 제공 JSON(TourAPI) 기반 장소 데이터, 지도 핀 표시용
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    gu = Column(String(20), index=True, nullable=False)       # 대전 내 구 (예: 유성구)
    category = Column(String(20), index=True, default="자유")   # 게시판 카테고리
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    password = Column(String(100), nullable=False)  # 평문 저장 (RFP III-2-나 의도된 설계)
    nickname = Column(String(50), default="익명")
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    comments = relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan"
    )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    content = Column(Text, nullable=False)
    nickname = Column(String(50), default="익명")
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="comments")


class Location(Base):
    """제공 JSON(TourAPI 4.0)에서 적재되는 장소 데이터. 읽기 전용 성격."""

    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    contentid = Column(String(20), unique=True, index=True)
    category = Column(String(20), index=True)   # 관광지/음식점/숙박 등
    gu = Column(String(20), index=True)          # addr1에서 파싱한 구
    title = Column(String(200), nullable=False)
    addr = Column(String(300))
    tel = Column(String(50))
    mapx = Column(String(30))  # 경도
    mapy = Column(String(30))  # 위도
    image_url = Column(String(500))
