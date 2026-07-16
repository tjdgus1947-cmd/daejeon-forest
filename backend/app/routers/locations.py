"""
지도 핀 표시용 장소 데이터 조회 API
- 프론트에서 "구 선택 -> 카테고리별 색상 핀" 화면을 그리기 위한 엔드포인트
"""
from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/locations", tags=["locations"])


@router.get("", response_model=List[schemas.LocationOut])
def list_locations(
    gu: Optional[str] = Query(None, description="구 필터 (예: 유성구)"),
    category: Optional[str] = Query(None, description="카테고리 필터 (contenttypeid, 예: 39)"),
    db: Session = Depends(get_db),
):
    """구/카테고리로 필터링된 장소 목록 (지도 핀 렌더링용)"""
    q = db.query(models.Location)
    if gu:
        q = q.filter(models.Location.gu == gu)
    if category:
        q = q.filter(models.Location.contenttypeid == category)
    return q.all()


@router.get("/gu-list")
def list_gu(db: Session = Depends(get_db)):
    """DB에 존재하는 구 목록 (대전 지도 클릭용 셀렉트 박스)"""
    rows = db.query(models.Location.gu).distinct().all()
    return sorted({r[0] for r in rows if r[0]})


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    """카테고리 목록 (범례/필터용)"""
    rows = db.query(models.Location.contenttypeid).distinct().all()
    return sorted({r[0] for r in rows if r[0]})