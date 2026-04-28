# ─────────────────────────────────────────────────────────────
# mcp_client.py — MCPClient (stdio 서브프로세스 클라이언트)
#
# 강의노트: Week_07.md §1.2 (라인 ~312-435, Client Architecture·시퀀스),
#           §2.1 (라인 ~800-895, 클라이언트 구현)
# 실행 시점: main.py 가 MCPClient(command="uv", args=[...]) 로
#            인스턴스화 → async with 진입에서 자동 connect.
#            단독 테스트는 `python mcp_client.py` 로 list_tools 확인.
# 의존: mcp SDK 의 ClientSession / stdio_client. main.py 가 사용.
#
# 학습 포인트:
#   1. AsyncExitStack 으로 중첩된 async 컨텍스트를 한 곳에서 관리 →
#      cleanup() 한 번에 stdio·session 모두 정리.
#   2. initialize() 핸드셰이크가 MCP 프로토콜의 시작점 — 서버 능력
#      (capabilities) 협상 후 list_tools/call_tool 사용 가능.
#   3. read_resource 의 MIME type 분기는 직접 파싱이 필요 →
#      application/json 은 json.loads, 평문은 그대로 반환.
# ─────────────────────────────────────────────────────────────

import sys
import asyncio
import json
from pydantic import AnyUrl
from typing import Optional, Any
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client


# MCP 서버 1대를 stdio 서브프로세스로 띄우고 통신하는 비동기 클라이언트
class MCPClient:
    # 생성자 — 실제 서브프로세스는 connect() 에서 spawn (지연 초기화)
    def __init__(
        self,
        command: str,           # 실행 명령 (예: "uv", "python")
        args: list[str],        # 인자 (예: ["run", "mcp_server.py"])
        env: Optional[dict] = None,
    ):
        self._command = command
        self._args = args
        self._env = env
        self._session: Optional[ClientSession] = None  # ← 늦은 할당, connect 후에만 유효
        self._exit_stack: AsyncExitStack = AsyncExitStack()  # ← 컨텍스트 누적용

    # 서버 연결 — stdio 서브프로세스 spawn → ClientSession 생성 → 핸드셰이크
    async def connect(self):
        # 1) 서브프로세스 spec 정의 (아직 실행 X)
        server_params = StdioServerParameters(
            command=self._command,
            args=self._args,
            env=self._env,
        )
        # 2) stdio_client 컨텍스트 진입 → 실제 서브프로세스 spawn,
        #    (read, write) 파이프 핸들 반환
        stdio_transport = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        _stdio, _write = stdio_transport
        # 3) ClientSession 컨텍스트 — 파이프 위에 JSON-RPC 세션 구축
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(_stdio, _write)
        )
        # 4) MCP 핸드셰이크 — 서버와 capabilities 협상
        await self._session.initialize()

    # 게으른 접근 헬퍼 — connect 전 호출 시 명시적 에러
    def session(self) -> ClientSession:
        if self._session is None:
            raise ConnectionError(
                "Client session not initialized or cache not populated. Call connect_to_server first."
            )
        return self._session

    # 서버가 노출한 도구 카탈로그 조회
    async def list_tools(self) -> list[types.Tool]:
        # TODO: Return a list of tools defined by the MCP server
        result = await self.session().list_tools()
        return result.tools  # ← ListToolsResult 의 tools 필드만 추출

    # 특정 도구 호출 — Claude 가 tool_use 블록을 만들 때 이 메서드가 호출됨
    async def call_tool(
        self, tool_name: str, tool_input: dict
    ) -> types.CallToolResult | None:
        # TODO: Call a particular tool and return the result
        return await self.session().call_tool(tool_name, tool_input)

    # 서버가 노출한 프롬프트 카탈로그 조회 (슬래시 명령 후보)
    async def list_prompts(self) -> list[types.Prompt]:
        # TODO: Return a list of prompts defined by the MCP server
        result = await self.session().list_prompts()
        return result.prompts

    # 특정 프롬프트 가져오기 — 인자(args) 채워서 Message 리스트로 받기
    async def get_prompt(self, prompt_name, args: dict[str, str]):
        # TODO: Get a particular prompt defined by the MCP server
        result = await self.session().get_prompt(prompt_name, args)
        return result.messages

    # 리소스 읽기 — URI 로 직접/템플릿 리소스 모두 처리
    async def read_resource(self, uri: str) -> Any:
        # TODO: Read a resource, parse the contents and return it
        result = await self.session().read_resource(AnyUrl(uri))
        resource = result.contents[0]
        # MIME type 분기가 핵심 — 서버가 선언한 mime_type 에 맞춰 파싱
        if isinstance(resource, types.TextResourceContents):
            if resource.mimeType == "application/json":
                return json.loads(resource.text)  # ← JSON 은 dict/list 로 파싱

            return resource.text  # ← 평문은 문자열 그대로

    # 정리 — exit_stack.aclose() 한 번에 session·stdio 서브프로세스 모두 정리
    async def cleanup(self):
        await self._exit_stack.aclose()
        self._session = None

    # async with 표준 프로토콜 — 진입 시 자동 connect
    async def __aenter__(self):
        await self.connect()
        return self

    # 종료 시 자동 cleanup — 예외 발생해도 서브프로세스 누수 없음
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()


# For testing
# 단독 테스트용 — 서버 띄우고 도구 목록만 출력 후 종료
async def main():
    async with MCPClient(
        # If using Python without UV, update command to 'python' and remove "run" from args.
        command="uv",
        args=["run", "mcp_server.py"],
    ) as _client:
        result = await _client.list_tools()
        print(result)


if __name__ == "__main__":
    # Windows 호환성 — Proactor 이벤트 루프 (서브프로세스 지원)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
