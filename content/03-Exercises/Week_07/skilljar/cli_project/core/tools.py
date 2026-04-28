# ─────────────────────────────────────────────────────────────
# core/tools.py — 다중 MCP 서버 도구 수집 + Claude 호환 변환 + 실행
#
# 강의노트: Week_07.md §2.1 (라인 ~800, 클라이언트 구현)
# 호출 흐름: Chat.run() → ToolManager.get_all_tools() → Claude.chat()
#           Chat.run() → ToolManager.execute_tool_requests() → MCPClient.call_tool()
# 학습 포인트:
#   1. MCP의 inputSchema → Anthropic의 input_schema 키 이름 변환 (호환성 핵심)
#   2. _find_client_with_tool: 도구 이름으로 어느 MCP 서버인지 라우팅
#   3. tool_use 블록만 골라 실행 — 다른 블록(text 등)은 무시
#   4. CallToolResult.content에서 TextContent만 추출해 JSON 직렬화
# ─────────────────────────────────────────────────────────────

import json
from typing import Optional, Literal, List
from mcp.types import CallToolResult, Tool, TextContent
from mcp_client import MCPClient
from anthropic.types import Message, ToolResultBlockParam


# 다중 MCP 클라이언트 도구를 통합 관리하는 정적 메서드 모음
class ToolManager:
    @classmethod
    async def get_all_tools(cls, clients: dict[str, MCPClient]) -> list[Tool]:
        """Gets all tools from the provided clients."""
        # 모든 서버의 도구를 단일 리스트로 평탄화 — Claude는 출처 구분 없이 받음
        tools = []
        for client in clients.values():
            tool_models = await client.list_tools()
            # MCP Tool 객체 → Anthropic API가 요구하는 dict 스키마로 변환
            tools += [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.inputSchema,  # MCP는 inputSchema, Anthropic은 input_schema
                }
                for t in tool_models
            ]
        return tools

    @classmethod
    async def _find_client_with_tool(
        cls, clients: list[MCPClient], tool_name: str
    ) -> Optional[MCPClient]:
        """Finds the first client that has the specified tool."""
        # 도구 이름으로 어느 MCP 서버에 속하는지 탐색 — 첫 매치 반환
        for client in clients:
            tools = await client.list_tools()
            tool = next((t for t in tools if t.name == tool_name), None)
            if tool:
                return client
        return None

    @classmethod
    def _build_tool_result_part(
        cls,
        tool_use_id: str,
        text: str,
        status: Literal["success"] | Literal["error"],
    ) -> ToolResultBlockParam:
        """Builds a tool result part dictionary."""
        # Anthropic ToolResultBlockParam 규약: tool_use_id로 어떤 호출에 대한 결과인지 매칭
        return {
            "tool_use_id": tool_use_id,
            "type": "tool_result",
            "content": text,
            "is_error": status == "error",
        }

    @classmethod
    async def execute_tool_requests(
        cls, clients: dict[str, MCPClient], message: Message
    ) -> List[ToolResultBlockParam]:
        """Executes a list of tool requests against the provided clients."""
        # Claude 응답에서 tool_use 블록만 골라 실행 대상으로 추림
        tool_requests = [
            block for block in message.content if block.type == "tool_use"
        ]
        tool_result_blocks: list[ToolResultBlockParam] = []
        for tool_request in tool_requests:
            # 호출 식별자·이름·인자 추출 — 하나의 응답에 여러 호출이 올 수 있음
            tool_use_id = tool_request.id
            tool_name = tool_request.name
            tool_input = tool_request.input

            # 이 도구를 보유한 MCP 서버 라우팅
            client = await cls._find_client_with_tool(
                list(clients.values()), tool_name
            )

            # 어떤 서버에도 없는 도구면 에러 결과로 응답해 다음 라운드 진행
            if not client:
                tool_result_part = cls._build_tool_result_part(
                    tool_use_id, "Could not find that tool", "error"
                )
                tool_result_blocks.append(tool_result_part)
                continue

            try:
                # 실제 MCP 도구 호출 — 네트워크/IPC 비용 발생 지점
                tool_output: CallToolResult | None = await client.call_tool(
                    tool_name, tool_input
                )
                items = []
                if tool_output:
                    items = tool_output.content
                # 결과 블록 중 TextContent만 추출(이미지 등 다른 타입은 본 예제에서 제외)
                content_list = [
                    item.text for item in items if isinstance(item, TextContent)
                ]
                # 리스트를 JSON 문자열로 직렬화해 Anthropic content 필드에 주입
                content_json = json.dumps(content_list)
                tool_result_part = cls._build_tool_result_part(
                    tool_use_id,
                    content_json,
                    "error"
                    if tool_output and tool_output.isError
                    else "success",
                )
            except Exception as e:
                # 예외 발생 시 메시지를 결과로 포함 — 모델이 인지하고 재시도 가능
                error_message = f"Error executing tool '{tool_name}': {e}"
                print(error_message)
                tool_result_part = cls._build_tool_result_part(
                    tool_use_id,
                    json.dumps({"error": error_message}),
                    "error"
                    if tool_output and tool_output.isError
                    else "success",
                )

            tool_result_blocks.append(tool_result_part)
        return tool_result_blocks
