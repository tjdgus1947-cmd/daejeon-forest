"""
Pydantic 스키마 (요청/응답 검증)
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# ---------- Post ----------
class PostCreate(BaseModel):
    gu: str = Field(..., examples=["유성구"])
    category: str = Field(default="자유")
    title: str
    content: str
    password: str = Field(..., min_length=4, description="수정/삭제용 비밀번호 (평문)")
    nickname: str = Field(default="익명")


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    password: str  # 수정 시에도 기존 비밀번호 확인 필요


class PostDelete(BaseModel):
    password: str


class PostVerify(BaseModel):
    """게시글 수정/삭제 전 비밀번호 확인용"""
    password: str


class CommentCreate(BaseModel):
    content: str
    nickname: str = Field(default="익명")


class CommentOut(BaseModel):
    id: int
    content: str
    nickname: str
    created_at: datetime

    class Config:
        from_attributes = True


class PostListOut(BaseModel):
    """목록 조회 시에는 비밀번호/본문 노출 안 함"""
    id: int
    gu: str
    category: str
    title: str
    nickname: str
    views: int
    created_at: datetime

    class Config:
        from_attributes = True


class PostDetailOut(BaseModel):
    id: int
    gu: str
    category: str
    title: str
    content: str
    nickname: str
    views: int
    created_at: datetime
    updated_at: datetime
    comments: List[CommentOut] = []

    class Config:
        from_attributes = True


# ---------- Location ----------
class LocationOut(BaseModel):
    id: int
    contentid: str
    category: str
    gu: str
    title: str
    addr: str
    tel: Optional[str] = None
    mapx: Optional[str] = None
    mapy: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


# ---------- Chat ----------
class ChatRequest(BaseModel):
    message: str
    history: List[dict] = Field(default_factory=list)  # [{"role": "user"/"assistant", "content": "..."}]


class ChatResponse(BaseModel):
    reply: str
