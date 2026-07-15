-- ============================================
-- 01_create_tables.sql
-- 커뮤니티 웹사이트 DB 테이블 생성
-- ============================================

-- 1. location 테이블
CREATE TABLE location (
    location_id SERIAL PRIMARY KEY,
    contentid VARCHAR(50) UNIQUE,
    contenttypeid VARCHAR(20),
    title VARCHAR(255),
    addr1 VARCHAR(255),
    addr2 VARCHAR(255),
    areacode VARCHAR(10),
    sigungucode VARCHAR(10),
    zipcode VARCHAR(10),
    tel VARCHAR(50),
    cat1 VARCHAR(20),
    cat2 VARCHAR(20),
    cat3 VARCHAR(20),
    firstimage TEXT,
    firstimage2 TEXT,
    cpyrhtDivCd VARCHAR(20),
    mapx NUMERIC(15, 12),
    mapy NUMERIC(15, 12),
    mlevel INTEGER,
    lDongRegnCd VARCHAR(10),
    lDongSignguCd VARCHAR(10),
    lclsSystm1 VARCHAR(20),
    lclsSystm2 VARCHAR(20),
    lclsSystm3 VARCHAR(20),
    createdtime VARCHAR(20),
    modifiedtime VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. board 테이블 (location 참조)
CREATE TABLE board (
    board_id SERIAL PRIMARY KEY,
    location_id INTEGER,
    writer VARCHAR(100) NOT NULL,
    board_password VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_location
        FOREIGN KEY (location_id)
        REFERENCES location(location_id)
        ON DELETE SET NULL
);

-- 3. comment 테이블 (board 참조)
CREATE TABLE comment (
    comment_id SERIAL PRIMARY KEY,
    board_id INTEGER NOT NULL,
    writer VARCHAR(100) NOT NULL,
    comment_password VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_board
        FOREIGN KEY (board_id)
        REFERENCES board(board_id)
        ON DELETE CASCADE
);

-- 4. 인덱스
CREATE INDEX idx_board_location ON board(location_id);
CREATE INDEX idx_comment_board ON comment(board_id);
CREATE INDEX idx_board_created_at ON board(created_at DESC);