# backend/app/models.py
"""
SQLAlchemy 모델
- Board: 익명 게시판 글 (RFP III-2)
- Location: 제공 JSON(TourAPI) 기반 장소 데이터, 지도 핀 표시용
- Comment / ChatbotLocation: 연관 데이터 모델
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Numeric, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Location(Base):
    """제공 JSON(TourAPI 4.0)에서 적재되는 장소 데이터"""
    __tablename__ = "location"

    location_id = Column(Integer, primary_key=True, index=True)
    contentid = Column(String(50), unique=True)
    contenttypeid = Column(String(20))
    title = Column(String(255))
    addr1 = Column(String(255))
    addr2 = Column(String(255))
    gu = Column(String(20), index=True)
    areacode = Column(String(10))
    sigungucode = Column(String(10))
    zipcode = Column(String(10))
    tel = Column(String(50))
    cat1 = Column(String(20))
    cat2 = Column(String(20))
    cat3 = Column(String(20))
    firstimage = Column(Text)
    firstimage2 = Column(Text)
    cpyrhtDivCd = Column("cpyrhtdivcd", String(20))
    mapx = Column(Numeric(15, 12))
    mapy = Column(Numeric(15, 12))
    mlevel = Column(Integer)
    lDongRegnCd = Column("ldongregncd", String(10))
    lDongSignguCd = Column("ldongsigngucd", String(10))
    lclsSystm1 = Column("lclssystm1", String(20))
    lclsSystm2 = Column("lclssystm2", String(20))
    lclsSystm3 = Column("lclssystm3", String(20))
    createdtime = Column(String(20))
    modifiedtime = Column(String(20))
    created_at = Column(TIMESTAMP, server_default=func.now())

    boards = relationship("Board", back_populates="location")
    chatbot_entries = relationship("ChatbotLocation", back_populates="location")


class Board(Base):
    """익명 게시판 글 모델"""
    __tablename__ = "board"

    board_id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("location.location_id", ondelete="SET NULL"))
    gu = Column(String(20), nullable=False, index=True)
    writer = Column(String(100), nullable=False)
    board_password = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    view_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now())

    location = relationship("Location", back_populates="boards")
    comments = relationship("Comment", back_populates="board", cascade="all, delete")


class Comment(Base):
    """게시글 댓글 모델"""
    __tablename__ = "comment"

    comment_id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("board.board_id", ondelete="CASCADE"), nullable=False)
    writer = Column(String(100), nullable=False)
    comment_password = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now())

    board = relationship("Board", back_populates="comments")


class ChatbotLocation(Base):
    """챗봇(RAG)용 location 스냅샷 테이블"""
    __tablename__ = "chatbot_location"

    chatbot_location_id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("location.location_id", ondelete="SET NULL"))
    contentid = Column(String(50))
    contenttypeid = Column(String(20))
    title = Column(String(255))
    addr1 = Column(String(255))
    tel = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())

    location = relationship("Location", back_populates="chatbot_entries")