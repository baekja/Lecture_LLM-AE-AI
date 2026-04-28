# ─────────────────────────────────────────────────────────────
# core/cli.py — prompt-toolkit 기반 CLI UI (자동완성·키바인딩·메인 루프)
#
# 강의노트: Week_07.md §1.3 (라인 ~437, 프로젝트 셋업)
#           Week_07.md §2.5 (라인 ~1330, / 슬래시 명령 UX)
# 호출 흐름: main.py → CliApp(agent) → initialize() → run()
# 학습 포인트:
#   1. UnifiedCompleter: @ 멘션 / 슬래시 명령 / 명령 인자 자동완성을 한 클래스로 통합
#   2. KeyBindings: @·/·스페이스 입력 즉시 자동완성 팝업 트리거 (UX 핵심)
#   3. CommandAutoSuggest: /format 입력 시 첫 인자 힌트(인라인 회색 텍스트)
#   4. 비동기 입력 루프: session.prompt_async()로 메인 스레드를 블로킹하지 않음
# ─────────────────────────────────────────────────────────────

from typing import List, Optional
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
from prompt_toolkit.document import Document
from prompt_toolkit.buffer import Buffer

from core.cli_chat import CliChat


# /명령 입력 시 첫 인자(예: "/format" → " plan.md")를 회색으로 미리 보여주는 Suggester
class CommandAutoSuggest(AutoSuggest):
    def __init__(self, prompts: List):
        self.prompts = prompts
        # 이름→Prompt 객체 매핑으로 O(1) 조회 (수업 시 prompts 개수가 늘어도 빠름)
        self.prompt_dict = {prompt.name: prompt for prompt in prompts}

    def get_suggestion(
        self, buffer: Buffer, document: Document
    ) -> Optional[Suggestion]:
        text = document.text

        # 슬래시로 시작하는 입력에만 인자 힌트 제공
        if not text.startswith("/"):
            return None

        # "/format" → parts=["format"]
        parts = text[1:].split()

        if len(parts) == 1:
            cmd = parts[0]

            # 등록된 명령이면 첫 번째 인자 이름을 회색 힌트로 노출
            if cmd in self.prompt_dict:
                prompt = self.prompt_dict[cmd]
                return Suggestion(f" {prompt.arguments[0].name}")

        return None


# @ 멘션·/ 명령·명령 인자를 모두 처리하는 통합 자동완성기
class UnifiedCompleter(Completer):
    def __init__(self):
        # MCP 서버에서 받아온 프롬프트·리소스 목록을 캐싱 (자동완성 응답성 향상)
        self.prompts = []
        self.prompt_dict = {}
        self.resources = []

    # 외부에서 프롬프트 목록 갱신 (CliApp.refresh_prompts에서 호출)
    def update_prompts(self, prompts: List):
        self.prompts = prompts
        self.prompt_dict = {prompt.name: prompt for prompt in prompts}

    # 외부에서 리소스(문서 ID) 목록 갱신
    def update_resources(self, resources: List):
        self.resources = resources

    # prompt-toolkit이 매 키 입력마다 호출 — 후보 yield 방식으로 스트리밍
    def get_completions(self, document, complete_event):
        text = document.text
        text_before_cursor = document.text_before_cursor

        # ── 분기 1: @ 멘션 자동완성 ─────────────────────────────
        if "@" in text_before_cursor:
            # rfind로 가장 최근 @ 위치 추출 → 복수 멘션(@a @b) 동시 지원
            last_at_pos = text_before_cursor.rfind("@")
            prefix = text_before_cursor[last_at_pos + 1 :]

            # prefix로 시작하는 리소스 ID만 필터링 (대소문자 무시)
            for resource_id in self.resources:
                if resource_id.lower().startswith(prefix.lower()):
                    yield Completion(
                        resource_id,
                        start_position=-len(prefix),
                        display=resource_id,
                        display_meta="Resource",
                    )
            return

        # ── 분기 2: / 슬래시 명령 자동완성 ───────────────────────
        if text.startswith("/"):
            parts = text[1:].split()

            # "/" 또는 "/for" 단계: 명령 이름 후보 노출
            if len(parts) <= 1 and not text.endswith(" "):
                cmd_prefix = parts[0] if parts else ""

                for prompt in self.prompts:
                    if prompt.name.startswith(cmd_prefix):
                        yield Completion(
                            prompt.name,
                            start_position=-len(cmd_prefix),
                            display=f"/{prompt.name}",
                            display_meta=prompt.description or "",
                        )
                return

            # "/format " (스페이스 직후): 인자(문서 ID) 후보 노출
            if len(parts) == 1 and text.endswith(" "):
                cmd = parts[0]

                if cmd in self.prompt_dict:
                    for id in self.resources:
                        yield Completion(
                            id,
                            start_position=0,
                            display=id,
                        )
                return

            # "/format plan" 단계: 부분 매칭으로 인자 후보 좁히기
            if len(parts) >= 2:
                doc_prefix = parts[-1]

                for resource in self.resources:
                    if "id" in resource and resource["id"].lower().startswith(
                        doc_prefix.lower()
                    ):
                        yield Completion(
                            resource["id"],
                            start_position=-len(doc_prefix),
                            display=resource["id"],
                        )
                return


# CLI 메인 애플리케이션 — 키바인딩·세션·메인 루프를 한곳에 묶음
class CliApp:
    def __init__(self, agent: CliChat):
        # CliChat 인스턴스 — 실제 AI 호출은 모두 이 agent에 위임
        self.agent = agent
        self.resources = []
        self.prompts = []

        self.completer = UnifiedCompleter()

        # 빈 상태로 먼저 생성 후 refresh_prompts에서 실제 데이터로 교체
        self.command_autosuggester = CommandAutoSuggest([])

        # ── 키바인딩: 특정 키 입력 즉시 자동완성 팝업을 띄우는 UX ──
        self.kb = KeyBindings()

        # "/" 입력: 빈 줄 시작이면 명령 후보 메뉴 즉시 오픈
        @self.kb.add("/")
        def _(event):
            buffer = event.app.current_buffer
            if buffer.document.is_cursor_at_the_end and not buffer.text:
                buffer.insert_text("/")
                buffer.start_completion(select_first=False)
            else:
                buffer.insert_text("/")

        # "@" 입력: 커서가 줄 끝이면 리소스 후보 메뉴 즉시 오픈
        @self.kb.add("@")
        def _(event):
            buffer = event.app.current_buffer
            buffer.insert_text("@")
            if buffer.document.is_cursor_at_the_end:
                buffer.start_completion(select_first=False)

        # 스페이스 입력: 명령 직후라면 인자 후보 메뉴 자동 오픈
        @self.kb.add(" ")
        def _(event):
            buffer = event.app.current_buffer
            text = buffer.text

            buffer.insert_text(" ")

            if text.startswith("/"):
                parts = text[1:].split()

                # "/format " 직후 → 첫 인자 후보 표시
                if len(parts) == 1:
                    buffer.start_completion(select_first=False)
                # 인자에 doc/file/id 키워드 포함 시 두 번째 인자도 자동완성
                elif len(parts) == 2:
                    arg = parts[1]
                    if (
                        "doc" in arg.lower()
                        or "file" in arg.lower()
                        or "id" in arg.lower()
                    ):
                        buffer.start_completion(select_first=False)

        # 입력 이력은 메모리 보관 — 종료 시 사라짐 (영속화는 FileHistory로 대체 가능)
        self.history = InMemoryHistory()
        self.session = PromptSession(
            completer=self.completer,
            history=self.history,
            key_bindings=self.kb,
            # 다크 테마 색상 — 터미널 가독성 향상
            style=Style.from_dict(
                {
                    "prompt": "#aaaaaa",
                    "completion-menu.completion": "bg:#222222 #ffffff",
                    "completion-menu.completion.current": "bg:#444444 #ffffff",
                }
            ),
            complete_while_typing=True,
            complete_in_thread=True,  # I/O 블로킹 방지: 자동완성을 별도 스레드에서 계산
            auto_suggest=self.command_autosuggester,
        )

    # MCP 서버에서 리소스·프롬프트를 끌어와 자동완성 캐시를 채움
    async def initialize(self):
        await self.refresh_resources()
        await self.refresh_prompts()

    # 문서 ID 목록 새로고침 — 서버에 새 문서가 추가되면 다시 호출 가능
    async def refresh_resources(self):
        try:
            self.resources = await self.agent.list_docs_ids()
            self.completer.update_resources(self.resources)
        except Exception as e:
            print(f"Error refreshing resources: {e}")

    # 프롬프트 목록 새로고침 — completer와 autosuggester 양쪽 모두 갱신
    async def refresh_prompts(self):
        try:
            self.prompts = await self.agent.list_prompts()
            self.completer.update_prompts(self.prompts)
            self.command_autosuggester = CommandAutoSuggest(self.prompts)
            self.session.auto_suggest = self.command_autosuggester
        except Exception as e:
            print(f"Error refreshing prompts: {e}")

    # 메인 입력 루프 — Ctrl+C로 종료할 때까지 사용자 질의 반복
    async def run(self):
        while True:
            try:
                # 비동기 prompt: 자동완성·키바인딩이 같은 이벤트 루프에서 동작
                user_input = await self.session.prompt_async("> ")
                if not user_input.strip():
                    continue

                # CliChat.run()으로 위임 → @멘션·/명령 처리 후 Tool Use 루프 진입
                response = await self.agent.run(user_input)
                print(f"\nResponse:\n{response}")

            except KeyboardInterrupt:
                break
