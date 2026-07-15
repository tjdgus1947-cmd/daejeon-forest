-- 1) 컬럼 추가
ALTER TABLE location ADD COLUMN gu VARCHAR(20);

-- 2) addr1(대전광역시 유성구...)에서 '유성구' 같은 'OO구' 패턴만 추출해서 gu에 채우기
UPDATE location
SET gu = substring(addr1 FROM '(\S+구)');

-- 3) 검색 속도 향상을 위한 인덱스 걸기
CREATE INDEX idx_location_gu ON location(gu);

SELECT DISTINCT gu FROM location ORDER BY gu;

-- board 테이블에 gu 컬럼 추가 (비어있을 때 기준)
ALTER TABLE board ADD COLUMN gu VARCHAR(20) NOT NULL;

-- board용 구 인덱스 추가
CREATE INDEX idx_board_gu ON board(gu);