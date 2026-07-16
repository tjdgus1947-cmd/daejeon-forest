import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from openai import OpenAI

from app.database import get_db
from app import schemas, models


router = APIRouter(
    prefix="/api/chat",
    tags=["chat"]
)


# =========================
# OpenAI Client Lazy Init
# =========================

_client = None


def get_openai_client():
    global _client

    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY가 설정되어 있지 않습니다."
            )

        _client = OpenAI(api_key=api_key)

    return _client



# =========================
# Chatbot 검색 설정
# =========================

TYPE_MAP = {
    "12": "관광지",
    "14": "문화시설",
    "15": "축제행사",
    "32": "숙박",
    "38": "쇼핑",
    "39": "음식점",
}


CATEGORY_KEYWORD_MAP = {
    "39": [
        "맛집",
        "식당",
        "카페",
        "음식",
        "먹을"
    ],

    "12": [
        "관광",
        "명소",
        "볼거리"
    ],

    "15": [
        "축제",
        "행사",
        "공연"
    ],

    "32": [
        "숙박",
        "호텔",
        "모텔",
        "펜션"
    ],

    "38": [
        "쇼핑",
        "시장",
        "백화점"
    ],

    "14": [
        "박물관",
        "미술관",
        "전시"
    ]
}


JOSA_LIST = [
    "에게서",
    "으로써",
    "으로서",
    "에서는",
    "에게",
    "한테",
    "까지",
    "부터",
    "은",
    "는",
    "이",
    "가",
    "을",
    "를",
    "의",
    "도",
    "만",
    "와",
    "과",
    "로",
    "에"
]


def strip_josa(word: str):

    for josa in JOSA_LIST:

        if word.endswith(josa) and len(word) - len(josa) >= 2:
            return word[:-len(josa)]

    return word



# =========================
# DB 검색(RAG)
# =========================


def format_results(results):

    if not results:
        return "조회된 관련 대전 정보가 없습니다."


    lines = []

    for loc in results:

        category = TYPE_MAP.get(
            loc.contenttypeid,
            "추천장소"
        )

        text = (
            f"- {loc.title} "
            f"({category}) "
            f"| 주소: {loc.addr1}"
        )

        if loc.tel:
            text += f" | 전화: {loc.tel}"


        lines.append(text)


    return "\n".join(lines)



def retrieve_chatbot_context(
        query: str,
        db: Session
):

    districts = [
        "유성구",
        "서구",
        "중구",
        "동구",
        "대덕구"
    ]


    target_district = None

    for district in districts:

        if district in query:
            target_district = district
            break



    target_type = None

    category_words = set()


    for tid, words in CATEGORY_KEYWORD_MAP.items():

        category_words.update(words)

        if any(word in query for word in words):

            target_type = tid



    stopwords = {

        "주소",
        "알려줘",
        "알려주세요",
        "어디",
        "위치",
        "추천",
        "추천해줘",
        "궁금",
        "있어",
        "해주세요"

    } | category_words



    keywords = []


    for word in query.split():

        if len(word) < 2:
            continue


        if word in districts:
            continue


        word = strip_josa(word)


        if word in stopwords:
            continue


        keywords.append(word)



    keywords = list(dict.fromkeys(keywords))



    query_builder = db.query(
        models.ChatbotLocation
    )



    if target_district:

        query_builder = query_builder.filter(
            models.ChatbotLocation.addr1.ilike(
                f"%{target_district}%"
            )
        )


    if target_type:

        query_builder = query_builder.filter(
            models.ChatbotLocation.contenttypeid
            == target_type
        )



    if keywords:

        conditions = []

        for kw in keywords:

            conditions.append(
                func.replace(
                    models.ChatbotLocation.title,
                    " ",
                    ""
                )
                .ilike(
                    f"%{kw.replace(' ','')}%"
                )
            )


        query_builder = query_builder.filter(
            or_(*conditions)
        )



    results = query_builder.limit(5).all()


    print(
        "[CHATBOT SEARCH RESULT]",
        len(results)
    )


    return format_results(results)



# =========================
# Chat API
# =========================


@router.post(
    "",
    response_model=schemas.ChatResponse
)
def chat(
    payload: schemas.ChatRequest,
    db: Session = Depends(get_db)
):


    try:

        context = retrieve_chatbot_context(
            payload.message,
            db
        )



        system_instruction = f"""
너는 대전광역시 AI 관광가이드 '성심이'야.

규칙:

- 항상 답변 첫 문장은
"안녕하세요 꿈돌이입니다!"
로 시작한다.

- 충청도 사투리를 자연스럽게 섞는다.
(~해유, ~했슈)

- 친절하고 짧게 설명한다.

- 사용자의 질문은 아래 대전 정보 기반으로 답한다.

- 없는 정보는 만들어내지 않는다.

- 정보가 없으면
"해당 질문은 잘 모르겠어유. 다른 질문도 물어봐주세유!"
라고 답한다.


[대전 지역 정보]

{context}

"""



        messages = [
            {
                "role": "system",
                "content": system_instruction
            }
        ]



        for msg in payload.history[-6:]:

            messages.append(
                {
                    "role": msg.get(
                        "role",
                        "user"
                    ),

                    "content": msg.get(
                        "content",
                        ""
                    )
                }
            )



        messages.append(
            {
                "role": "user",
                "content": payload.message
            }
        )



        client = get_openai_client()



        response = client.chat.completions.create(

            model="gpt-5-mini",

            messages=messages,

            max_completion_tokens=1000

        )


        reply = response.choices[0].message.content



        if not reply:

            reply = (
                "앗 답변 준비 중 문제가 생겼어유. "
                "다시 한번 물어봐주세유!"
            )



        return schemas.ChatResponse(
            reply=reply
        )



    except Exception as e:

        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )