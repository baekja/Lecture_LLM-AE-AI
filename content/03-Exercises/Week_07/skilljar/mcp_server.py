from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md":   "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf":      "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf":     "This document presents the projected future performance of the system.",
    "plan.md":         "The plan outlines the steps for the project's implementation.",
    "spec.txt":        "These specifications define the technical requirements for the equipment.",
}


# Tool: Read a doc
@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string",
)
def read_document(
    doc_id: str = Field(description="ID of the document to read")
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]


# Tool: Edit a doc
@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing a string in the document content with a new string",
)
def edit_document(
    doc_id: str = Field(description="Id of the document that will be edited"),
    old_str: str = Field(description="The text to replace. Must match exactly, including white space"),
    new_str: str = Field(description="The text to insert in place of the old text"),
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)


# Resource: Direct — return all doc IDs
@mcp.resource(
    "docs://documents",
    mime_type="application/json",
)
def list_docs() -> list[str]:
    return list(docs.keys())


# Resource: Templated — return contents of a particular doc
@mcp.resource(
    "docs://documents/{doc_id}",
    mime_type="text/plain",
)
def fetch(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]


# Prompt: Reformat a doc as markdown
@mcp.prompt(
    name="format",
    description="Rewrite a document in markdown format",
)
def format_document(
    doc_id: str = Field(description="ID of the document to format")
) -> list[base.Message]:
    prompt = f"""
    Your goal is to reformat the following document in markdown format.

    The id of the document you need to format is:
    <document_id>
    {doc_id}
    </document_id>

    Add in headers, bullet points, tables, etc as necessary.
    Feel free to add in examples to clarify the content.
    Use the 'edit_document' tool to edit the document. Do not leave anything out.
    The entire contents of the document should be included in the reformatted version.

    After the document has been edited, return the full contents of the reformatted document
    as the final answer to this prompt.
    """
    return [base.UserMessage(prompt)]


if __name__ == "__main__":
    mcp.run(transport="stdio")
