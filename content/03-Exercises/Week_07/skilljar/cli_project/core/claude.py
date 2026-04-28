# ─────────────────────────────────────────────────────────────
# core/claude.py — Anthropic API 호출 래퍼 (메시지 헬퍼 + Extended Thinking)
#
# 강의노트: Week_04.md (Tool Use)와 Week_06.md (Extended Thinking) 통합
# 호출 흐름: Chat.run() → Claude.chat() → Anthropic().messages.create()
# 학습 포인트:
#   1. Anthropic() 생성자는 ANTHROPIC_API_KEY 환경변수를 자동 로드
#   2. Message 객체와 dict를 모두 받도록 isinstance 분기 — API 응답·수동 메시지 호환
#   3. text_from_message: 도구 사용 블록은 제외하고 텍스트 블록만 추출
#   4. chat() 파라미터를 dict로 동적 구성 — thinking·tools·system을 옵션 처리
# ─────────────────────────────────────────────────────────────

from anthropic import Anthropic
from anthropic.types import Message


# Anthropic SDK 호출을 모듈 단위로 캡슐화한 서비스 객체
class Claude:
    def __init__(self, model: str):
        # API 키는 환경변수에서 자동 로드 — 명시 인자 없이 안전하게 초기화
        self.client = Anthropic()
        # 모델 ID(예: "claude-haiku-4-5") — 외부에서 주입해 모델 교체 용이
        self.model = model

    # user 메시지 추가 — Message 객체면 .content 추출, 아니면 그대로 사용
    def add_user_message(self, messages: list, message):
        user_message = {
            "role": "user",
            "content": message.content
            if isinstance(message, Message)
            else message,
        }
        messages.append(user_message)

    # assistant 메시지 추가 — add_user_message와 동일 패턴(역할만 다름)
    def add_assistant_message(self, messages: list, message):
        assistant_message = {
            "role": "assistant",
            "content": message.content
            if isinstance(message, Message)
            else message,
        }
        messages.append(assistant_message)

    # 응답 Message에서 type=="text" 블록만 골라 줄바꿈 결합 — tool_use 블록은 제외
    def text_from_message(self, message: Message):
        return "\n".join(
            [block.text for block in message.content if block.type == "text"]
        )

    # 메인 호출 — params dict를 동적 구성해 옵션을 깔끔하게 켜고 끔
    def chat(
        self,
        messages,
        system=None,
        temperature=1.0,
        stop_sequences=[],
        tools=None,
        thinking=False,
        thinking_budget=1024,
    ) -> Message:
        # 필수 파라미터 — 모델·최대 토큰·이력·온도·정지 시퀀스
        params = {
            "model": self.model,
            "max_tokens": 8000,
            "messages": messages,
            "temperature": temperature,
            "stop_sequences": stop_sequences,
        }

        # Extended Thinking(W06) 활성화 — budget_tokens 내에서 모델이 내부 추론 수행
        if thinking:
            params["thinking"] = {
                "type": "enabled",
                "budget_tokens": thinking_budget,
            }

        # Tool Use(W04) 활성화 — Claude API가 도구 스키마를 보고 호출을 결정
        if tools:
            params["tools"] = tools

        # 시스템 프롬프트는 옵션 — 없을 때 키 자체를 빼서 명세 깔끔히 유지
        if system:
            params["system"] = system

        # **kwargs 언팩으로 옵셔널 키만 포함된 깔끔한 호출 생성
        message = self.client.messages.create(**params)
        return message
