"""
insert_location_data.py

관광지/숙박/음식점/레포츠/문화시설/쇼핑/축제공연행사 등
여러 종류의 관광 JSON 데이터를 PostgreSQL location 테이블에 삽입하는 스크립트.

파일마다 카테고리(관광지, 숙박, 음식점 등)는 다르지만 필드 구조는 동일함을
확인했음. 혹시 특정 파일에 필드가 빠져 있어도 에러 없이 동작하도록
(item.get() 방식) 방어적으로 작성함.

사용법 (파일 하나씩):
    python insert_location_data.py new_대전_충청권_관광지.json

사용법 (여러 파일 한 번에 - 추천, 쉘의 와일드카드 사용):
    python insert_location_data.py new_대전_충청권_*.json

또는 파일명 직접 나열:
    python insert_location_data.py 관광지.json 숙박.json 음식점.json 레포츠.json 문화시설.json 쇼핑.json 축제공연행사.json

(terminal에 작성)
python 02_insert_data.py new_대전_충청권_관광지.json new_대전_충청권_숙박.json new_대전_충청권_음식점.json new_대전_충청권_레포츠.json new_대전_충청권_문화시설.json new_대전_충청권_쇼핑.json new_대전_충청권_축제공연행사.json
    """

import json
import sys
import psycopg2

# ------------------------------------------------------------------
# DB 접속 정보 - 본인 환경에 맞게 수정하세요
# ------------------------------------------------------------------
DB_CONFIG = {
    "host": "dpg-d9c5mqbbc2fs73bbgehg-a.singapore-postgres.render.com",
    "port": 5432,
    "dbname": "mydb_hq60",
    "user": "dbuser",
    "password": "8YockEZ12Kl81FGQc1OrgvmqSRBB0P7K",
}

# location 테이블 컬럼 (JSON 필드명과 동일)
COLUMNS = [
    "contentid",
    "contenttypeid",
    "title",
    "addr1",
    "addr2",
    "areacode",
    "sigungucode",
    "zipcode",
    "tel",
    "cat1",
    "cat2",
    "cat3",
    "firstimage",
    "firstimage2",
    "cpyrhtDivCd",
    "mapx",
    "mapy",
    "mlevel",
    "lDongRegnCd",
    "lDongSignguCd",
    "lclsSystm1",
    "lclsSystm2",
    "lclsSystm3",
    "createdtime",
    "modifiedtime",
]


def clean_value(value, is_numeric=False):
    """빈 문자열/None -> NULL. 숫자 필드는 float로 변환."""
    if value is None or value == "":
        return None
    if is_numeric:
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    return value


def build_row(item):
    """item(dict)을 COLUMNS 순서에 맞는 tuple로 변환.
    필드가 없는 파일이 있어도 item.get()이라 에러 없이 None 처리됨."""
    row = []
    for col in COLUMNS:
        raw = item.get(col)
        if col in ("mapx", "mapy"):
            row.append(clean_value(raw, is_numeric=True))
        elif col == "mlevel":
            v = clean_value(raw)
            try:
                row.append(int(v) if v is not None else None)
            except (ValueError, TypeError):
                row.append(None)
        else:
            row.append(clean_value(raw))
    return tuple(row)


def load_data(filepath):
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def main(filepaths):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    col_list = ", ".join(COLUMNS)
    placeholders = ", ".join(["%s"] * len(COLUMNS))

    insert_sql = f"""
        INSERT INTO location ({col_list})
        VALUES ({placeholders})
        ON CONFLICT (contentid) DO NOTHING
    """
    # contentid가 UNIQUE라서, 이미 있는 데이터는 건너뛰고(중복 방지)
    # 새 데이터만 추가됨. 관광지/숙박/음식점 등 여러 카테고리 파일을
    # 순서 상관없이, 여러 번 실행해도 안전함.

    total_inserted = 0
    total_skipped = 0

    for filepath in filepaths:
        data = load_data(filepath)
        items = data.get("items", [])
        region = data.get("region", "?")
        content_type = data.get("contentType", "?")
        print(f"[{filepath}] region={region}, contentType={content_type}, {len(items)}건 로드")

        file_inserted = 0
        file_skipped = 0
        for item in items:
            row = build_row(item)
            cur.execute(insert_sql, row)
            if cur.rowcount == 1:
                file_inserted += 1
            else:
                file_skipped += 1

        conn.commit()
        total_inserted += file_inserted
        total_skipped += file_skipped
        print(f"  -> 삽입 {file_inserted}건 / 중복 스킵 {file_skipped}건")

    cur.close()
    conn.close()

    print("\n=== 전체 결과 ===")
    print(f"총 삽입: {total_inserted}건 / 중복 스킵: {total_skipped}건")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python insert_location_data.py <json파일1> [json파일2 ...]")
        sys.exit(1)

    main(sys.argv[1:])