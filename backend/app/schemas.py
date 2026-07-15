"""
Pydantic 스키마 (요청/응답 검증)
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# ---------- Board ----------
class BoardCreate(BaseModel):
    gu: str = Field(..., examples=["유성구"])
    location_id: Optional[int] = None
    title: str
    content: str
    board_password: str = Field(..., min_length=4, description="수정/삭제용 비밀번호 (평문)")
    writer: str = Field(default="익명")


class BoardUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    board_password: str  # 수정 시에도 기존 비밀번호 확인 필요


class BoardDelete(BaseModel):
    board_password: str


class BoardVerify(BaseModel):
    """게시글 수정/삭제 전 비밀번호 확인용"""
    board_password: str


class CommentCreate(BaseModel):
    content: str
    writer: str = Field(default="익명")
    comment_password: str = Field(..., min_length=4, description="댓글 수정/삭제용 비밀번호")


class CommentOut(BaseModel):
    comment_id: int
    content: str
    writer: str
    created_at: datetime

    class Config:
        from_attributes = True


class BoardListOut(BaseModel):
    """목록 조회 시에는 비밀번호/본문 노출 안 함"""
    board_id: int
    gu: str
    title: str
    writer: str
    view_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class BoardDetailOut(BaseModel):
    board_id: int
    gu: str
    location_id: Optional[int] = None
    title: str
    content: str
    writer: str
    view_count: int
    created_at: datetime
    updated_at: datetime
    comments: List[CommentOut] = []

    class Config:
        from_attributes = True


# ---------- Location ----------
class LocationOut(BaseModel):
    location_id: int
    contentid: str
    contenttypeid: Optional[str] = None
    gu: Optional[str] = None
    title: str
    addr1: str
    tel: Optional[str] = None
    mapx: Optional[float] = None
    mapy: Optional[float] = None
    firstimage: Optional[str] = None

    class Config:
        from_attributes = True


# ---------- Chat ----------
class ChatRequest(BaseModel):
    message: str
    history: List[dict] = Field(default_factory=list)  # [{"role": "user"/"assistant", "content": "..."}]


class ChatResponse(BaseModel):
    reply: str

class CommentUpdate(BaseModel):
    content: str
    comment_password: str

class CommentDelete(BaseModel):
    comment_password: str
