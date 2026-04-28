# ─────────────────────────────────────────────────────────────
# core/chat.py — Tool Use 루프를 추상화한 Chat 베이스 클래스
#
# 강의노트: Week_07.md §2.1 (라인 ~800, 클라이언트 구현)
#           Week_04.md (Tool Use 패턴 — 본 클래스의 원형)
# 호출 흐름: CliChat.run() ← Chat.run() (상속) → Claude.chat() ↔ ToolManager
# 학습 포인트:
#   1. _process_query는 Template Method — 서브클래스가 오버라이드 (CliChat이 사용)
#   2. while True Tool Use 루프: stop_reason="tool_use"가 아닐 때까지 반복
#   3. ToolManager.get_all_tools로 다중 MCP 서버 도구를 매 라운드 동적 수집
#   4. 프로덕션에서는 max_iterations로 무한 루프 방어 필요 (학생 개선 과제)
# ─────────────────────────────────────────────────────────────

from core.claude import Claude
from mcp_client import MCPClient
from core.tools import ToolManager
from anthropic.types import MessageParam


# 모든 Chat 변형(Cli, Web 등)이 공유하는 기본 대화 + Tool Use 루프
class Chat:
    def __init__(self, claude_service: Claude, clients: dict[str, MCPClient]):
        # Anthropic API 호출 래퍼 — 실제 모델 응답은 모두 여기서 생성
        self.claude_service: Claude = claude_service
        # 이름→MCPClient 매핑 (멀티 서버 지원). 도구 수집·실행 시 모든 값 순회
        self.clients: dict[str, MCPClient] = clients
        # Anthropic API에 그대로 전달할 대화 이력 누적 버퍼
        self.messages: list[MessageParam] = []

    # 기본 구현은 단순 user 메시지 추가 — CliChat이 오버라이드해 @멘션·/명령 처리
    async def _process_query(self, query: str):
        self.messages.append({"role": "user", "content": query})

    # 메인 진입점: 사용자 질의 1건을 받아 최종 텍스트 응답을 반환
    async def run(
        self,
        query: str,
    ) -> str:
        final_text_response = ""

        # 1) 입력 전처리(서브클래스가 컨텍스트 주입할 수 있는 훅)
        await self._process_query(query)

        # 2) Tool Use 루프 — Claude가 도구 호출을 멈출 때까지 반복
        while True:
            # 매 라운드 모든 MCP 서버에서 도구 목록을 다시 수집 (서버 핫리로드 대응)
            response = self.claude_service.chat(
                messages=self.messages,
                tools=await ToolManager.get_all_tools(self.clients),
            )

            # assistant 응답을 이력에 누적 (다음 라운드에 컨텍스트로 사용)
            self.claude_service.add_assistant_message(self.messages, response)

            # 도구 호출 요청이면 실행 → 결과를 user role 메시지로 다시 주입
            if response.stop_reason == "tool_use":
                # 도구 사용 전 모델의 자연어 설명을 화면에 출력 (UX)
                print(self.claude_service.text_from_message(response))
                tool_result_parts = await ToolManager.execute_tool_requests(
                    self.clients, response
                )

                # tool_result 블록은 Anthropic 규약상 user role로 반환해야 함
                self.claude_service.add_user_message(
                    self.messages, tool_result_parts
                )
            else:
                # end_turn 등 종료 사유 → 최종 텍스트만 추출하고 루프 탈출
                final_text_response = self.claude_service.text_from_message(
                    response
                )
                break

        return final_text_response
