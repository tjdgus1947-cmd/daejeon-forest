"""
게시판 CRUD API (RFP III-2)
- 회원가입/로그인 없음 (익명)
- 수정/삭제는 등록된 비밀번호와 평문 비교로만 권한 확인 (RFP III-2-나, 의도된 설계)
"""
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/posts", tags=["posts"])


def _get_post_or_404(db: Session, post_id: int) -> models.Post:
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return post


@router.get("", response_model=List[schemas.PostListOut])
def list_posts(
    gu: Optional[str] = Query(None, description="구 필터 (예: 유성구)"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    keyword: Optional[str] = Query(None, description="제목/내용 검색어"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """게시글 목록 조회 (필터 + 검색 + 페이지네이션)"""
    q = db.query(models.Post)
    if gu:
        q = q.filter(models.Post.gu == gu)
    if category:
        q = q.filter(models.Post.category == category)
    if keyword:
        like = f"%{keyword}%"
        q = q.filter(
            (models.Post.title.like(like)) | (models.Post.content.like(like))
        )
    q = q.order_by(models.Post.created_at.desc())
    return q.offset((page - 1) * size).limit(size).all()


@router.get("/{post_id}", response_model=schemas.PostDetailOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """게시글 상세 조회 (조회수 +1)"""
    post = _get_post_or_404(db, post_id)
    post.views += 1
    db.commit()
    db.refresh(post)
    return post


@router.post("", response_model=schemas.PostDetailOut, status_code=201)
def create_post(payload: schemas.PostCreate, db: Session = Depends(get_db)):
    """게시글 작성 (제목/내용/수정용 비밀번호 필수)"""
    post = models.Post(**payload.model_dump())
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.post("/{post_id}/verify")
def verify_password(post_id: int, payload: schemas.PostVerify, db: Session = Depends(get_db)):
    """수정/삭제 진입 전 비밀번호 확인 (프론트 모달용)"""
    post = _get_post_or_404(db, post_id)
    if post.password != payload.password:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
    return {"verified": True}


@router.put("/{post_id}", response_model=schemas.PostDetailOut)
def update_post(post_id: int, payload: schemas.PostUpdate, db: Session = Depends(get_db)):
    """게시글 수정 (비밀번호 일치 시에만)"""
    post = _get_post_or_404(db, post_id)
    if post.password != payload.password:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
    if payload.title is not None:
        post.title = payload.title
    if payload.content is not None:
        post.content = payload.content
    db.commit()
    db.refresh(post)
    return post


@router.delete("/{post_id}", status_code=204)
def delete_post(post_id: int, payload: schemas.PostDelete, db: Session = Depends(get_db)):
    """게시글 삭제 (비밀번호 일치 시에만)"""
    post = _get_post_or_404(db, post_id)
    if post.password != payload.password:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
    db.delete(post)
    db.commit()
    return None


@router.post("/{post_id}/comments", response_model=schemas.CommentOut, status_code=201)
def create_comment(post_id: int, payload: schemas.CommentCreate, db: Session = Depends(get_db)):
    """댓글 작성"""
    _get_post_or_404(db, post_id)
    comment = models.Comment(post_id=post_id, **payload.model_dump())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
