# pip install openai
"""
===============================================================================
주의: 이 파일은 ChatGPT 보강(후처리) 로직입니다. 팀 작업 시 API 키/모델명 외
로직 변경을 금지합니다. (AI 팀 승인 없이 수정 금지)

사용 가이드
- is_weak(answer): 형사법 LLM 초안 품질 판정
- refine_with_chatgpt(question, answer): ChatGPT로 보강한 최종 답변 생성

환경변수 (.env 지원)
- OPENAI_API_KEY: 필수, OpenAI API 키
- OPENAI_MODEL: 선택, 기본 "gpt-4o" (비용/속도 고려해 gpt-4o-mini 권장 가능)

문의: 보강 프롬프트/품질 기준 수정을 원하면 AI 담당자에게 요청하세요.
===============================================================================
"""

from openai import OpenAI
import os
from dotenv import load_dotenv

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # 필요 시 gpt-4o-mini 권장

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        load_dotenv()  # .env 파일 지원
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY 환경변수가 필요합니다.")
        _client = OpenAI(api_key=api_key)
    return _client


# [수정 금지] 품질 판정 규칙 — 변경 시 보강 트리거/비용/일관성 영향
def is_weak(law_answer: str) -> bool:
    if not law_answer: 
        return True
    if len(law_answer) < 300: 
        return True
    bad_end = ["...", "…", "중략", "미완", "계속", "to be continued"]
    if any(law_answer.strip().endswith(x) for x in bad_end):
        return True
    weak_markers = ["잘 모르겠습니다", "응답이 중단", "토큰", "제한으로 인해"]
    if any(x in law_answer for x in weak_markers):
        return True
    return False

# [수정 금지] 보강 프롬프트/파라미터 — 응답 톤/구성/비용에 직접 영향
def refine_with_chatgpt(user_question: str, law_answer: str) -> str:
    system_prompt = (
        "당신은 형사법 도메인 답변을 사용자의 이해에 맞게 보강하는 편집자입니다. "
        "초안의 법률적 의미를 바꾸지 말고, 누락된 핵심 논점을 보태고, 중간에 끊긴 문장을 복구하고, "
        "개요→핵심 쟁점→관련 조문/요건→주의사항(법률 자문 아님) 순서로 정리하세요. "
        "한국어로 간결하고 정확하게 작성하세요."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"[사용자 질문]\n{user_question}"},
        {"role": "assistant", "content": f"[형사법 LLM 초안]\n{law_answer}"},
        {"role": "user", "content": "위 초안을 보강·정돈해 최종 답변을 작성하세요. "
                                    "불명확하거나 끊긴 부분은 자연스럽게 복구하고, 빠진 요건/예외가 있으면 추가 설명하세요. "
                                    "마지막에 '※ 본 답변은 일반 정보이며 법률 자문이 아닙니다.'를 붙이세요."}
    ]
    client = _get_client()
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=800
    )
    return resp.choices[0].message.content
