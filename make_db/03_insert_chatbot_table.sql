-- ============================================
-- 03_populate_chatbot_table.sql
-- location 테이블 데이터를 chatbot_location으로 복사(스냅샷)
-- ============================================

INSERT INTO chatbot_location (location_id, contentid, contenttypeid, title, addr1, tel)
SELECT location_id, contentid, contenttypeid, title, addr1, tel
FROM location;