from pathlib import Path
import os

import chainlit as cl
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS


# =========================================================
# 기본 경로
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


# =========================================================
# OpenAI API Key 확인
# =========================================================

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY를 찾을 수 없습니다.")


# =========================================================
# Embedding 모델
# =========================================================

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)


# =========================================================
# Vector DB 불러오기
# =========================================================

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

LOCAL_DB_PATH = Path("C:/RAG_DB/article_faiss")
SERVER_DB_PATH = BASE_DIR / "vectordb" / "article_faiss"

if LOCAL_DB_PATH.exists():
    VECTOR_DB_PATH = LOCAL_DB_PATH
else:
    VECTOR_DB_PATH = SERVER_DB_PATH


# =========================================================
# GPT 모델
# =========================================================

llm = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0
)


# =========================================================
# 헤리티전트 페르소나
# =========================================================

PERSONA = """
당신은 '불국사 헤리티전트'입니다.

당신은 불국사 관련 언론 기사 데이터를 분석하는
문화유산 담론 분석 AI입니다.

반드시 다음 규칙을 따르세요.

1. 제공된 기사 자료를 최우선 근거로 사용합니다.
2. 기사 자료에 없는 사실은 임의로 만들어내지 않습니다.
3. 여러 기사에서 반복되는 주제를 주요 담론으로 분석합니다.
4. 서로 다른 관점이 있다면 구분해서 설명합니다.
5. 문화유산 보존, 활용, 관광, 역사적 가치,
   장소성, 사회적 인식 등의 관점에서 분석합니다.
6. 연구 발표에 사용할 수 있도록 명확하게 답변합니다.
7. 가능하면 답변 근거가 되는 기사 번호를 표시합니다.
"""


# =========================================================
# 검색된 기사 정리
# =========================================================

def make_context(docs):
    parts = []

    for i, doc in enumerate(docs, start=1):
        metadata = doc.metadata

        parts.append(
            f"""
[기사 {i}]

제목: {metadata.get("제목", "")}
언론사: {metadata.get("언론사", "")}
일자: {metadata.get("일자", "")}
URL: {metadata.get("URL", "")}

기사 내용:
{doc.page_content}
"""
        )

    return "\n".join(parts)


# =========================================================
# 처음 접속했을 때
# =========================================================

@cl.on_chat_start
async def start():
    await cl.Message(
        content="""
# 🏛️ 불국사 헤리티전트

안녕하세요.

저는 **불국사 관련 기사 데이터를 기반으로 답변하는 문화유산 담론 분석 AI**입니다.

불국사의 보존, 관광, 활용, 역사적 가치,
시기별 언론 담론 등에 대해 질문해주세요.

예시 질문:

**2001~2005년 불국사 관련 기사에서 주요 담론은 무엇이야?**
"""
    ).send()


# =========================================================
# 질문 처리
# =========================================================

@cl.on_message
async def main(message: cl.Message):

    question = message.content

    # 1. 관련 기사 검색
    docs = vectorstore.similarity_search(
        question,
        k=10
    )

    # 2. 검색 자료 정리
    context = make_context(docs)

    # 3. GPT 프롬프트
    prompt = f"""
{PERSONA}

아래 기사 자료만을 근거로 사용자의 질문에 답하세요.

========================
사용자 질문
========================

{question}


========================
검색된 기사 자료
========================

{context}


========================
답변 규칙
========================

- 검색된 기사 내용을 중심으로 답하세요.
- 기사에 없는 내용을 사실처럼 추가하지 마세요.
- 주요 담론을 묻는 경우 반복적으로 나타나는 주제와 특징을 정리하세요.
- 서로 다른 관점이 있으면 구분해서 설명하세요.
- 근거가 부족하면
  '현재 검색된 기사만으로는 충분히 판단하기 어렵습니다.'
  라고 말하세요.
"""

    # 4. GPT 답변 생성
    response = await llm.ainvoke(prompt)
    answer = response.content

    # 5. 중복 기사 제거
    sources = []
    seen = set()

    for doc in docs:
        metadata = doc.metadata

        title = str(metadata.get("제목", ""))
        url = str(metadata.get("URL", ""))

        key = (title, url)

        if key in seen:
            continue

        seen.add(key)
        sources.append(metadata)

    # 6. 근거 기사 표시
    source_text = "\n\n---\n\n## 📚 검색된 근거 기사\n"

    for i, source in enumerate(sources, start=1):
        title = source.get("제목", "")
        press = source.get("언론사", "")
        date = source.get("일자", "")
        url = source.get("URL", "")

        source_text += (
            f"\n**{i}. {title}**  \n"
            f"{press} | {date}  \n"
        )

        if url and str(url).lower() != "nan":
            source_text += f"{url}\n"

    # 7. Chainlit 화면에 출력
    await cl.Message(
        content=answer + source_text
    ).send()