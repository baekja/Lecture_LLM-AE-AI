# ─────────────────────────────────────────────────────────────
# core/cli_chat.py — @멘션·/슬래시 명령을 처리하는 CLI 전용 Chat
#
# 강의노트: Week_07.md §2.3 (라인 ~1100, @ 멘션 주입)
#           Week_07.md §2.5 (라인 ~1330, / 슬래시 명령 라우팅)
# 호출 흐름: main.py → CliApp.run() → CliChat.run() → _process_query()
# 학습 포인트:
#   1. Chat 클래스를 상속해 _process_query만 오버라이드 (Template Method)
#   2. @멘션 → MCP Resource 주입 / /명령 → MCP Prompt 호출로 분리
#   3. doc_client(리소스/프롬프트 전용) vs clients(도구 다중 서버) 역할 구분
#   4. mcp.types.PromptMessage → Anthropic MessageParam 호환 변환 계층
# ─────────────────────────────────────────────────────────────

from typing import List, Tuple
from mcp.types import Prompt, PromptMessage
from anthropic.types import MessageParam

from core.chat import Chat
from core.claude import Claude
from mcp_client import MCPClient


# CLI 환경에서 @ 멘션·/ 명령을 추가로 처리하는 Chat 서브클래스
class CliChat(Chat):
    def __init__(
        self,
        doc_client: MCPClient,
        clients: dict[str, MCPClient],
        claude_service: Claude,
    ):
        # 부모 Chat에 도구용 다중 클라이언트 dict와 Claude 서비스 전달
        super().__init__(clients=clients, claude_service=claude_service)

        # 리소스(docs://...)·프롬프트(/format 등) 호출 전용 단일 클라이언트
        self.doc_client: MCPClient = doc_client

    # MCP 서버에 등록된 모든 프롬프트(@mcp.prompt) 목록 조회 — UI 자동완성에서 사용
    async def list_prompts(self) -> list[Prompt]:
        return await self.doc_client.list_prompts()

    # MCP 서버의 docs://documents 리소스에서 문서 ID 목록을 받아옴
    async def list_docs_ids(self) -> list[str]:
        return await self.doc_client.read_resource("docs://documents")

    # 특정 문서 ID의 본문 텍스트를 docs://documents/{id} 리소스에서 읽어옴
    async def get_doc_content(self, doc_id: str) -> str:
        return await self.doc_client.read_resource(f"docs://documents/{doc_id}")

    # 슬래시 명령(/format 등)에 매핑된 MCP Prompt를 인자와 함께 호출
    async def get_prompt(
        self, command: str, doc_id: str
    ) -> list[PromptMessage]:
        return await self.doc_client.get_prompt(command, {"doc_id": doc_id})

    # @멘션 추출 → 해당 문서 본문을 XML 형식으로 묶어 컨텍스트 문자열 반환
    async def _extract_resources(self, query: str) -> str:
        # 공백 split 기반 단순 파싱: 토큰 단위로 안전하게 @ID만 골라냄 (정규식 X)
        mentions = [word[1:] for word in query.split() if word.startswith("@")]

        # 서버에 존재하는 실제 문서 ID 목록을 받아 화이트리스트로 사용
        doc_ids = await self.list_docs_ids()
        mentioned_docs: list[Tuple[str, str]] = []

        for doc_id in doc_ids:
            # 사용자가 멘션한 ID가 실제로 존재하는 경우에만 본문 로드 (순차 I/O)
            if doc_id in mentions:
                content = await self.get_doc_content(doc_id)
                mentioned_docs.append((doc_id, content))

        # Anthropic 권장 패턴: <document id="..."> 태그로 컨텍스트 명확히 분리
        return "".join(
            f'\n<document id="{doc_id}">\n{content}\n</document>\n'
            for doc_id, content in mentioned_docs
        )

    # /명령 라우팅: 명령이면 MCP Prompt 호출 후 True, 아니면 False 반환
    async def _process_command(self, query: str) -> bool:
        # 슬래시로 시작하지 않으면 명령이 아니므로 즉시 종료(조기 반환)
        if not query.startswith("/"):
            return False

        # "/format plan.md" → words=["/format","plan.md"], command="format"
        words = query.split()
        command = words[0].replace("/", "")

        # words[1] 인자 추출 — 인자 누락 시 IndexError 가능 (학생 개선 과제)
        messages = await self.doc_client.get_prompt(
            command, {"doc_id": words[1]}
        )

        # MCP PromptMessage → Anthropic MessageParam으로 변환 후 대화 이력에 누적
        self.messages += convert_prompt_messages_to_message_params(messages)
        return True

    # 메인 진입점 오버라이드: 우선순위는 명령 처리 → 명령 아니면 멘션 추출
    async def _process_query(self, query: str):
        # 1) 슬래시 명령이면 여기서 끝 — 부모 Chat의 도구 루프로 즉시 진입
        if await self._process_command(query):
            return

        # 2) 일반 질의: @멘션 문서 본문을 XML 컨텍스트로 결합
        added_resources = await self._extract_resources(query)

        # @ 표기를 모델이 도구 호출로 오해하지 않도록 명시적 안내 포함
        prompt = f"""
        The user has a question:
        <query>
        {query}
        </query>

        The following context may be useful in answering their question:
        <context>
        {added_resources}
        </context>

        Note the user's query might contain references to documents like "@report.docx". The "@" is only
        included as a way of mentioning the doc. The actual name of the document would be "report.docx".
        If the document content is included in this prompt, you don't need to use an additional tool to read the document.
        Answer the user's question directly and concisely. Start with the exact information they need.
        Don't refer to or mention the provided context in any way - just use it to inform your answer.
        """

        # 가공된 프롬프트를 user 메시지로 추가 → 부모 Chat.run()의 while 루프가 처리
        self.messages.append({"role": "user", "content": prompt})


# MCP PromptMessage 1건을 Anthropic MessageParam dict로 변환하는 호환성 계층
def convert_prompt_message_to_message_param(
    prompt_message: "PromptMessage",
) -> MessageParam:
    # MCP는 user/assistant 외 role을 가질 수 있으므로 안전하게 정규화
    role = "user" if prompt_message.role == "user" else "assistant"

    content = prompt_message.content

    # Check if content is a dict-like object with a "type" field
    # dict이거나 pydantic 모델 객체 모두 처리 (MCP SDK 버전 호환)
    if isinstance(content, dict) or hasattr(content, "__dict__"):
        content_type = (
            content.get("type", None)
            if isinstance(content, dict)
            else getattr(content, "type", None)
        )
        # 단일 텍스트 블록 → content를 평문 문자열로 평탄화
        if content_type == "text":
            content_text = (
                content.get("text", "")
                if isinstance(content, dict)
                else getattr(content, "text", "")
            )
            return {"role": role, "content": content_text}

    # 멀티 블록(list) 형태 → text 블록만 골라 Anthropic content 배열 형식으로 보존
    if isinstance(content, list):
        text_blocks = []
        for item in content:
            # Check if item is a dict-like object with a "type" field
            if isinstance(item, dict) or hasattr(item, "__dict__"):
                item_type = (
                    item.get("type", None)
                    if isinstance(item, dict)
                    else getattr(item, "type", None)
                )
                if item_type == "text":
                    item_text = (
                        item.get("text", "")
                        if isinstance(item, dict)
                        else getattr(item, "text", "")
                    )
                    text_blocks.append({"type": "text", "text": item_text})

        if text_blocks:
            return {"role": role, "content": text_blocks}

    # 알 수 없는 형식이면 빈 문자열로 폴백 — 대화 흐름이 끊기지 않도록 방어 코드
    return {"role": role, "content": ""}


# 여러 PromptMessage를 한 번에 변환하는 배치 헬퍼
def convert_prompt_messages_to_message_params(
    prompt_messages: List[PromptMessage],
) -> List[MessageParam]:
    return [
        convert_prompt_message_to_message_param(msg) for msg in prompt_messages
    ]
