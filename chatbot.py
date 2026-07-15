import os
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from openai import OpenAI

# 1. 환경 변수 로드 및 OpenAI 클라이언트 초기화
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ .env 파일에 OPENAI_API_KEY가 누락되었습니다!")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

# 2. PostgreSQL 설정
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ .env 파일에 DATABASE_URL이 누락되었습니다!")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 🌟 실제 DB 테이블(chatbot_location)에 맞춘 모델
class ChatbotLocation(Base):
    __tablename__ = "chatbot_location"  # DB에 만든 실제 테이블명 (단수)

    chatbot_location_id = Column(Integer, primary_key=True, index=True)  # 실제 PK
    location_id = Column(Integer, nullable=True)  # location 테이블 FK
    contentid = Column(String(50), index=True)
    contenttypeid = Column(String(20), nullable=False, index=True)  # 12: 관광지, 39: 음식점 등
    title = Column(String(255), nullable=False)
    addr1 = Column(String(255), nullable=False, index=True)  # 구 검색용 인덱스 유지
    tel = Column(String(50), nullable=True)
    created_at = Column(DateTime, nullable=True)


# DB 세션 디펜던시
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 3. Pydantic 요청/응답 스키마 (Stateless 대화내역 관리)
class ChatMessage(BaseModel):
    role: str      # "user" 또는 "assistant"
    content: str   # 대화 내용

class ChatRequest(BaseModel):
    history: List[ChatMessage] = []  # Vue 메모리용 과거 대화 리스트
    current_message: str            # 유저의 최신 질문


app = FastAPI()


# 4. 챗봇 전용 테이블 기반 RAG 조회 함수
def retrieve_chatbot_context(query: str, db: Session) -> str:
    """
    사용자 질문에서 '구' 키워드와 '카테고리'를 파악해
    chatbot_location 테이블에서 관련 정보를 조회합니다.
    """
    districts = ["유성구", "서구", "중구", "동구", "대덕구"]
    target_district = None
    for dist in districts:
        if dist in query:
            target_district = dist
            break

    target_type = None
    if any(keyword in query for keyword in ["맛집", "식당", "카페", "먹을", "음식"]):
        target_type = "39"
    elif any(keyword in query for keyword in ["볼거리", "관광", "명소", "구경"]):
        target_type = "12"
    elif any(keyword in query for keyword in ["축제", "행사", "공연"]):
        target_type = "15"

    sql_query = db.query(ChatbotLocation)

    if target_district:
        sql_query = sql_query.filter(ChatbotLocation.addr1.like(f"%{target_district}%"))
    if target_type:
        sql_query = sql_query.filter(ChatbotLocation.contenttypeid == target_type)

    # 🌟 질문에서 의미 없는 단어(불용어) 제외하고 키워드만 추출
    stopwords = ["주소", "알려줘", "알려주세요", "어디", "위치", "위치를",
                 "궁금해", "궁금", "좀", "해줘", "알려", "가는", "가는법", "가는길"]
    keywords = [
        w for w in query.split()
        if len(w) >= 2
        and w not in districts
        and "추천" not in w
        and w not in stopwords
    ]

    # 🌟 공백 무시 + OR 조건으로 매칭 (띄어쓰기 차이로 인한 검색 실패 방지)
    if keywords:
        conditions = [
            func.replace(ChatbotLocation.title, ' ', '').like(f"%{kw.replace(' ', '')}%")
            for kw in keywords
        ]
        sql_query = sql_query.filter(or_(*conditions))

    # 토큰 요금 절약을 위해 상위 5개 상호만 가져오기
    results = sql_query.limit(5).all()

    if not results:
        return "조회된 관련 대전 정보가 없습니다."

    context_lines = []
    type_map = {"12": "관광지", "14": "문화시설", "15": "축제행사", "32": "숙박", "38": "쇼핑", "39": "음식점"}
    for loc in results:
        category = type_map.get(loc.contenttypeid, "추천장소")
        tel_num = loc.tel if loc.tel else "정보 없음"
        context_lines.append(
            f"- {loc.title} ({category}) | 주소: {loc.addr1} | 전화: {tel_num}"
        )

    return "\n".join(context_lines)


# 5. 챗봇 대답 생성 API 엔드포인트
@app.post("/api/chat")
async def chat_with_sungsim(payload: ChatRequest, db: Session = Depends(get_db)):
    try:
        # Step 1. chatbot_location 테이블에서 필요한 텍스트 컨텍스트만 SELECT (Read)
        context = retrieve_chatbot_context(payload.current_message, db)

        # Step 2. 시스템 페르소나 지시문 작성
        system_instruction = (
            "너는 대전광역시의 친절하고 위트 넘치는 AI 가이드 '성심이'야.\n"
            "반드시 충청도 사투리(~해유, ~했슈, 그랬시유, ~랴)를 걸게 섞어서 정감 가고 친절하게 대답해야 해.\n"
            "답변 맨 앞에 항상 '안녕하세요 꿈돌이입니다!'로 시작해.\n"
            "사용자의 질문에 답할 때, 아래 제공되는 [대전 지역 정보]를 최우선으로 참고해서 추천해줘.\n"
            "매우 중요한 규칙:\n"
            "- [대전 지역 정보]에 없는 내용(예: 관람시간, 주차 정보, 길찾기, 실시간 혼잡도, 날씨 등)은 "
            "절대로 답변하거나 제안하지 마.\n"
            "- 추가로 알려줄 수 있다는 식의 제안('길 안내해드릴게유' 등)도 하지 마.\n"
            "- [대전 지역 정보]가 '조회된 관련 대전 정보가 없습니다'라면, 길게 설명하지 말고 "
            "'해당 질문은 잘 모르겠어유. 다른 질문이 또 있을까요?' 라는 취지로 짧게만 답해.\n\n"
            f"[대전 지역 정보]\n{context}"
        )

        # Step 3. OpenAI에 보낼 메세지 묶음 조립 (System + 과거 대화내역 + 최신 질문)
        openai_messages = [{"role": "system", "content": system_instruction}]

        for msg in payload.history:
            openai_messages.append({"role": msg.role, "content": msg.content})

        openai_messages.append({"role": "user", "content": payload.current_message})

        # Step 4. OpenAI API 호출
        response = openai_client.chat.completions.create(
            model="gpt-5-mini",
            messages=openai_messages,
            #max_completion_tokens=1500
        )

        ai_reply = response.choices[0].message.content
        return {"reply": ai_reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"챗봇 오류가 발생했슈: {str(e)}")