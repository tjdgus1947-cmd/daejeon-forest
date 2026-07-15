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

router = APIRouter(prefix="/api/boards", tags=["board"])


def _get_board_or_404(db: Session, board_id: int) -> models.Board:
    board = db.query(models.Board).filter(models.Board.board_id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return board


@router.get("", response_model=List[schemas.BoardListOut])
def list_boards(
    gu: Optional[str] = Query(None, description="구 필터 (예: 유성구)"),
    keyword: Optional[str] = Query(None, description="제목/내용 검색어"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """게시글 목록 조회 (필터 + 검색 + 페이지네이션)"""
    q = db.query(models.Board)
    if gu:
        q = q.filter(models.Board.gu == gu)
    if keyword:
        like = f"%{keyword}%"
        q = q.filter(
            (models.Board.title.like(like)) | (models.Board.content.like(like))
        )
    q = q.order_by(models.Board.created_at.desc())
    return q.offset((page - 1) * size).limit(size).all()


@router.get("/{board_id}", response_model=schemas.BoardDetailOut)
def get_board(board_id: int, db: Session = Depends(get_db)):
    """게시글 상세 조회 (조회수 +1)"""
    board = _get_board_or_404(db, board_id)
    board.view_count += 1
    db.commit()
    db.refresh(board)
    return board


@router.post("", response_model=schemas.BoardDetailOut, status_code=201)
def create_board(payload: schemas.BoardCreate, db: Session = Depends(get_db)):
    """게시글 작성 (제목/내용/수정용 비밀번호 필수)"""
    board = models.Board(**payload.model_dump())
    db.add(board)
    db.commit()
    db.refresh(board)
    return board


@router.post("/{board_id}/verify")
def verify_password(board_id: int, payload: schemas.BoardVerify, db: Session = Depends(get_db)):
    """수정/삭제 진입 전 비밀번호 확인 (프론트 모달용)"""
    board = _get_board_or_404(db, board_id)
    if board.board_password != payload.board_password:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
    return {"verified": True}


@router.put("/{board_id}", response_model=schemas.BoardDetailOut)
def update_board(board_id: int, payload: schemas.BoardUpdate, db: Session = Depends(get_db)):
    """게시글 수정 (비밀번호 일치 시에만)"""
    board = _get_board_or_404(db, board_id)
    if board.board_password != payload.board_password:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
    if payload.title is not None:
        board.title = payload.title
    if payload.content is not None:
        board.content = payload.content
    db.commit()
    db.refresh(board)
    return board


@router.delete("/{board_id}", status_code=204)
def delete_board(board_id: int, payload: schemas.BoardDelete, db: Session = Depends(get_db)):
    """게시글 삭제 (비밀번호 일치 시에만)"""
    board = _get_board_or_404(db, board_id)
    if board.board_password != payload.board_password:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
    db.delete(board)
    db.commit()
    return None


@router.post("/{board_id}/comments", response_model=schemas.CommentOut, status_code=201)
def create_comment(board_id: int, payload: schemas.CommentCreate, db: Session = Depends(get_db)):
    """댓글 작성"""
    _get_board_or_404(db, board_id)
    comment = models.Comment(board_id=board_id, **payload.model_dump())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment