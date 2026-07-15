"""
의뢰사 제공 JSON(TourAPI 4.0) -> locations 테이블 적재 스크립트

사용법:
    python -m app.seed_data

주의(RFP III-1-가): 제공 JSON을 그대로 활용하며 직접 공공 API를 호출하지 않는다.
주의: 대전_충청권 JSON에는 대전 외 충남/충북 데이터도 섞여 있으므로,
      addr1이 "대전"으로 시작하는 항목만 필터링하여 적재한다.
"""
import glob
import json
import os
import re

from app.database import Base, engine, SessionLocal
from app import models

# 실제 배포/개발 환경에 맞게 .env 의 DATA_DIR 로 override 가능
DATA_DIR = os.getenv("DATA_DIR", "./data")

GU_PATTERN = re.compile(r"(\S+구)")  # 주소에서 "OO구" 패턴 추출


def parse_gu(addr1: str) -> str:
    """주소 문자열에서 대전의 '구'를 파싱. 못 찾으면 '기타'."""
    if not addr1:
        return "기타"
    match = GU_PATTERN.search(addr1)
    return match.group(1) if match else "기타"


def load_json_files():
    """DATA_DIR 내 모든 *.json 파일을 순회하며 적재"""
    files = glob.glob(os.path.join(DATA_DIR, "*.json"))
    if not files:
        print(f"[경고] {DATA_DIR} 에서 JSON 파일을 찾지 못했습니다.")
        return

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    total_loaded = 0
    total_skipped = 0

    try:
        for filepath in files:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)

            category = data.get("contentType", "기타")
            items = data.get("items", [])

            for item in items:
                addr1 = item.get("addr1", "") or ""

                # 대전광역시 데이터만 사용 (충남/충북 데이터는 제외)
                if not addr1.startswith("대전"):
                    total_skipped += 1
                    continue

                contentid = item.get("contentid")
                if not contentid:
                    continue

                # 이미 있으면 스킵 (재실행 시 중복 방지)
                exists = (
                    db.query(models.Location)
                    .filter(models.Location.contentid == contentid)
                    .first()
                )
                if exists:
                    continue

                location = models.Location(
                    contentid=contentid,
                    category=category,
                    gu=parse_gu(addr1),
                    title=item.get("title", ""),
                    addr=addr1,
                    tel=item.get("tel") or None,
                    mapx=item.get("mapx") or None,
                    mapy=item.get("mapy") or None,
                    image_url=item.get("firstimage") or None,
                )
                db.add(location)
                total_loaded += 1

            db.commit()
            print(f"[완료] {os.path.basename(filepath)} 처리 완료")

    finally:
        db.close()

    print(f"\n총 적재: {total_loaded}건 / 대전 외 지역 제외: {total_skipped}건")


if __name__ == "__main__":
    load_json_files()
