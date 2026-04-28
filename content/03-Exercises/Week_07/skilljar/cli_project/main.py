# ─────────────────────────────────────────────────────────────
# main.py — CLI 진입점 (Claude + MCPClient + CliChat 결합)
#
# 강의노트: Week_07.md §1.3 (라인 ~437-535, 프로젝트 셋업),
#           §2.5 (라인 ~1330-1410, 클라이언트에서 프롬프트 사용)
# 실행 시점: 학생이 직접 실행 — `uv run main.py` 또는
#            `python main.py [extra_server.py ...]`.
#            강의 후반부에 @plan.md, /format plan.md 등 체험.
# 의존: mcp_client.MCPClient (서버 프로세스 생명주기),
#       core.claude.Claude (Anthropic API 래퍼),
#       core.cli_chat.CliChat / core.cli.CliApp (UI 계층).
#
# 학습 포인트:
#   1. AsyncExitStack 으로 다수 MCPClient 컨텍스트를 일괄 관리 —
#      stack 종료 시 enter_async_context 된 모든 컨텍스트가 역순 정리.
#   2. sys.argv[1:] 로 추가 서버 스크립트를 받아 multi-server 패턴 →
#      한 채팅에서 여러 MCP 서버를 동시 사용 가능.
#   3. .env 의 키 누락은 assert 로 즉시 fail-fast → 디버깅 용이.
# ─────────────────────────────────────────────────────────────

import asyncio
import sys
import os
from dotenv import load_dotenv
from contextlib import AsyncExitStack

from mcp_client import MCPClient
from core.claude import Claude

from core.cli_chat import CliChat
from core.cli import CliApp

# .env 파일 로드 — ANTHROPIC_API_KEY, CLAUDE_MODEL 등을 환경변수로 주입
load_dotenv()

# Anthropic Config
# Anthropic 설정 — .env 에서 모델명·API 키 읽기
claude_model = os.getenv("CLAUDE_MODEL", "")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")


# fail-fast 검증 — 키 누락 시 명시적 에러로 즉시 종료
assert claude_model, "Error: CLAUDE_MODEL cannot be empty. Update .env"
assert anthropic_api_key, (
    "Error: ANTHROPIC_API_KEY cannot be empty. Update .env"
)


# 메인 비동기 진입점
async def main():
    # Claude 서비스 인스턴스 — Anthropic API 호출 래퍼
    claude_service = Claude(model=claude_model)

    # CLI 인자에서 추가 MCP 서버 스크립트 수집 (multi-server 패턴)
    server_scripts = sys.argv[1:]
    clients = {}

    # USE_UV 환경변수로 실행기 분기 — uv run vs python 직접 실행
    command, args = (
        ("uv", ["run", "mcp_server.py"])
        if os.getenv("USE_UV", "0") == "1"
        else ("python", ["mcp_server.py"])
    )

    # AsyncExitStack — 모든 MCPClient 컨텍스트 진입을 한 곳에 누적,
    # stack 종료 시 모든 서브프로세스가 역순으로 자동 정리됨 (핵심 패턴)
    async with AsyncExitStack() as stack:
        # 기본 문서 서버 클라이언트 — 항상 존재
        doc_client = await stack.enter_async_context(
            MCPClient(command=command, args=args)
        )
        clients["doc_client"] = doc_client

        # 추가 서버들 — sys.argv[1:] 로 받은 스크립트 각각을 별도 클라이언트로 등록
        for i, server_script in enumerate(server_scripts):
            client_id = f"client_{i}_{server_script}"
            client = await stack.enter_async_context(
                MCPClient(command="uv", args=["run", server_script])
            )
            clients[client_id] = client

        # 채팅 컨텍스트 구성 — doc_client 는 특별 취급(@mention, /명령), 나머지는 보조
        chat = CliChat(
            doc_client=doc_client,
            clients=clients,
            claude_service=claude_service,
        )

        # CLI 앱 진입 — initialize 로 도구·프롬프트 카탈로그 캐시 후 run 으로 REPL
        cli = CliApp(chat)
        await cli.initialize()
        await cli.run()


if __name__ == "__main__":
    # Windows 에서 서브프로세스 띄우려면 Proactor 루프 필수
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
