# ─────────────────────────────────────────────────────────────
# mcp_server.py — DocumentMCP 서버 (FastMCP 기반)
#
# 강의노트: Week_07.md §1.4 (라인 ~537-665, 도구 정의),
#           §2.2 (라인 ~1000-1050, 리소스),
#           §2.4 (라인 ~1230-1300, 프롬프트)
# 실행 시점: 단독 실행 → `python mcp_server.py` 또는
#            `mcp dev mcp_server.py` (Inspector). main.py 가
#            stdio 서브프로세스로 자동 기동.
# 의존: FastMCP (mcp SDK). main.py 와 mcp_client.py 가 이 서버를 사용.
#
# 학습 포인트:
#   1. @mcp.tool / @mcp.resource / @mcp.prompt 데코레이터로
#      MCP 서버의 3대 능력(Tools·Resources·Prompts)을 선언한다.
#   2. Pydantic Field 의 description 이 곧 Claude 의 도구 선택 근거가
#      되므로 자연어 설명 품질이 핵심이다.
#   3. transport="stdio" 는 서버를 stdin/stdout JSON-RPC 로 운용 →
#      서브프로세스 형태로 클라이언트가 spawn 한다.
# ─────────────────────────────────────────────────────────────

from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

# FastMCP 인스턴스 생성 — 서버 이름은 "DocumentMCP".
# log_level="ERROR" 가 핵심: stdio 통신은 stdout 을 사용하므로
# print() 나 INFO 로그가 끼어들면 JSON-RPC 메시지가 깨진다 → 잡음 차단.
mcp = FastMCP("DocumentMCP", log_level="ERROR")


# 데모용 인메모리 문서 저장소 — 엔지니어링 도메인으로 의도적으로 구성.
# Angela Smith, P.E. (Professional Engineer), condenser tower 등
# 실제 엔지니어링 워크플로를 흉내낸 샘플.
docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

# TODO: Write a tool to read a doc
# 도구 1: 문서 읽기 — 단일 인자(doc_id)로 문서 본문을 반환.
# name 을 명시해 클라이언트(Claude)가 호출 시 이 이름을 사용하도록 고정한다.
@mcp.tool(
    name = "read_doc_contents",
    description = "Read the contents of a document and return it as a string",
)
def read_document(
    doc_id: str = Field(description="ID of the document to read")  # ← 인자 description 이 도구 선택의 단서

):
    # 존재하지 않는 doc_id 방어 — MCP 도구는 명시적으로 예외를 던지는 것이 권장됨
    if doc_id not in docs:
        raise ValueError(f"Doc with id{doc_id} not found")
    return docs[doc_id]


# TODO: Write a tool to edit a doc

# 도구 2: 문서 편집 — 다중 인자(doc_id, old_str, new_str) 도구 예제.
# 각 Field description 이 자연어로 정확해야 Claude 가 올바른 인자를 채운다.
@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing a string in the documents content with a new string"
)
def edit_document(
    doc_id: str = Field(description="Id of the document that will be edited"),
    old_str:str = Field(description='Teh text to replace. Must match exactly, including white space'),
    new_str:str = Field(description='The text to insert in place of the old text')
):
    # 존재하지 않으면 즉시 에러 — 이후 replace 가 silent fail 하지 않도록
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    # 단순 문자열 replace — 실무라면 정규식·다중 매칭 처리 필요
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)

# TODO: Write a resource to return all doc id's

# 리소스 1 (direct URI): 모든 문서 ID 목록 — 카탈로그 역할.
# URI 가 고정 문자열이므로 "direct" — 클라이언트가 그대로 요청.
@mcp.resource(
    "docs://documents",
    mime_type="application/json",  # ← JSON 으로 응답 → 클라이언트가 json.loads 분기
)
def list_docs() -> list[str]:
    return list(docs.keys())

# TODO: Write a resource to return the contents of a particular doc

# 리소스 2 (templated URI): 단일 문서 내용 — {doc_id} 가 변수.
# 클라이언트는 docs://documents/plan.md 형태로 구체화하여 요청한다.
@mcp.resource(
    "docs://documents/{doc_id}",
    mime_type="text/plain"  # ← 평문 → 클라이언트는 resource.text 그대로 사용
)
def fetch(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]

# TODO: Write a prompt to rewrite a doc in markdown format

# 프롬프트: 사전 정의된 인스트럭션 카탈로그 — 클라이언트(슬래시 명령)가
# /format <doc_id> 형태로 호출하면 아래 텍스트가 UserMessage 로 주입된다.
@mcp.prompt(
    name='format',
    description="Rewrite a document in markdown format"
)
def format_document(
    doc_id:str=Field(description="ID of the document to format")
) -> list[base.Message]:
    # 도메인 전문 인스트럭션 — Claude 가 edit_document 도구를 호출하도록 유도
    prompt = f"""
    Your goal is to reformat the following document in markdown format.

    The id o the document you need to format is:
    <document_id>
    {doc_id}
    </document_id>

    Add in headers, bullet points, tables, etc as necessary.
    Feel free to add in examples to clarify the content.
    Use the 'edit_document' tool to edit the document. After the documnet has been Do not leave anything out. The entire contents of the document should be included in the reformatted version.


    Use the 'edit_document' tool to edit the document. After the documnet has been edited, return the full contents of the reformatted document as the final answer to this prompt.
    """

    # MCP 프롬프트는 Message 리스트를 반환 — UserMessage / AssistantMessage 조합 가능
    return [base.UserMessage(prompt)]

# TODO: Write a prompt to summarize a doc


# 진입점: stdio 트랜스포트로 서버 실행 → 클라이언트가 서브프로세스로 spawn
if __name__ == "__main__":
    mcp.run(transport="stdio")
