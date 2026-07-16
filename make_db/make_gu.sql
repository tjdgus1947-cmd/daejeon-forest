-- 컬럼 추가
ALTER TABLE location ADD COLUMN gu VARCHAR(20);

-- addr1에서 구 이름 추출해서 채우기 ("OO구" 패턴 추출)
UPDATE location
SET gu = substring(addr1 FROM '(\S+구)');

-- 인덱스 추가
CREATE INDEX idx_location_gu ON location(gu);


SELECT DISTINCT gu FROM location ORDER BY gu;


ALTER TABLE board ADD COLUMN gu VARCHAR(20) NOT NULL;
-- 실제 운영 시엔 DEFAULT 없이 매번 값 넣는 게 맞지만,
-- 기존 데이터가 있다면 임시 기본값 필요. 없으면 DEFAULT 절 빼도 됨.

CREATE INDEX idx_board_gu ON board(gu);