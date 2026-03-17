"""건축공학 질문을 Claude API로 보내는 예제"""

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

# 시스템 프롬프트: 구조공학 전문가 역할 부여
SYSTEM_PROMPT = """당신은 한국 건축구조기준(KBC 2016)을 숙지한 구조공학 전문가입니다.
건축공학 대학원생의 질문에 정확하고 교육적으로 답변합니다.
수식이 필요하면 LaTeX 형식으로, 단위는 SI 단위계를 사용합니다."""


def ask_structural_question(question: str) -> str:
    """구조공학 질문을 Claude에게 전달"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        temperature=0.2,  # 공학 계산은 낮은 temperature
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": question}
        ]
    )

    # 토큰 사용량 출력
    print(f"📊 토큰 사용: 입력 {message.usage.input_tokens}"
          f" + 출력 {message.usage.output_tokens}"
          f" = 총 {message.usage.input_tokens + message.usage.output_tokens}")

    return message.content[0].text


# 실행 예시
if __name__ == "__main__":
    # 예시 1: 기본 구조 질문
    answer = ask_structural_question(
        "RC 보의 전단설계에서 콘크리트의 전단강도 Vc를 구하는 "
        "간편식을 KBC 기준으로 설명해주세요."
    )
    print("\n📝 답변:")
    print(answer)

    # 예시 2: 설계 검토 질문
    answer2 = ask_structural_question(
        "폭 400mm, 유효깊이 550mm인 RC 보에 전단력 Vu=280kN이 작용합니다. "
        "fck=27MPa일 때 전단철근이 필요한지 검토해주세요."
    )
    print("\n📝 답변:")
    print(answer2)
