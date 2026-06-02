# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Setup (one-time):
```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

Run the MCP server (stdio transport, blocks until killed):
```bash
uv run main.py
```

Run tests:
```bash
uv run pytest                                      # all tests
uv run pytest tests/test_document.py               # single file
uv run pytest tests/test_document.py::TestBinaryDocumentToMarkdown::test_binary_document_to_markdown_with_pdf  # single test
uv run pytest -k pdf                               # by keyword
uv run pytest -v                                   # verbose
```

Inspect the server interactively (no client wiring needed):
```bash
uv run mcp dev main.py     # opens MCP Inspector — `mcp[cli]` is already in deps
```

## Architecture

This is a FastMCP server that exposes document/utility tools over MCP. Three layers:

1. **`main.py`** — the server entry point. Instantiates `FastMCP("docs")` and registers tools via the `mcp.tool()(func)` decorator-call form. `mcp.run()` defaults to stdio transport, which is what an MCP client (Claude Desktop, Claude Code, etc.) connects to via subprocess.
2. **`tools/`** — pure Python functions, one per file by domain (`math.py`, `document.py`). Functions here have **no MCP awareness** — they're plain callables with pydantic `Field` annotations and docstrings. This separation lets `pytest` import and test them directly without spinning up the server (see `tests/test_document.py`).
3. **`tests/fixtures/`** — binary test inputs (`mcp_docs.pdf`, `mcp_docs.docx`) consumed by the document tests. New document-format tests should add fixtures here.

**Important gotcha:** `tools/document.py::binary_document_to_markdown` is implemented and tested but **not yet registered** in `main.py`. To expose it over MCP, add `mcp.tool()(binary_document_to_markdown)` alongside the existing `add` registration. The math tool serves as the reference pattern.

Document conversion is delegated to `markitdown` (with `[docx,pdf]` extras). Binary input → `BytesIO` → `MarkItDown.convert(stream, StreamInfo(extension=file_type))` → markdown text. The `file_type` argument is the file extension without a dot (`"pdf"`, `"docx"`).

## Defining MCP tools (from README conventions)

Tools are plain Python functions registered with the server:

```python
mcp.tool()(my_function)
```

Every tool function must have:

1. **Docstring structure** — the LLM sees this verbatim as the tool description, so it directly drives tool-selection quality:
   - **One-line summary** as the first line.
   - Detailed explanation of functionality.
   - **When to use (and not use)** the tool — explicit guidance prevents the model from misapplying it.
   - **Usage examples** with expected input/output (doctest-style `>>>` is fine; see `tools/math.py::add`).

2. **Parameter descriptions via `pydantic.Field`** — these become the parameter schema the model sees, not just runtime validation:

   ```python
   from pydantic import Field

   def my_tool(
       param1: str = Field(description="Detailed description of this parameter"),
       param2: int = Field(description="Explain what this parameter does"),
   ) -> ReturnType:
       """Comprehensive docstring here"""
       # Implementation
   ```

3. **Type hints on every parameter and the return** — FastMCP introspects these to build the JSON schema advertised to clients. Untyped params will either be rejected or default to `Any`/string and silently degrade tool-selection accuracy.

The reference implementation is `tools/math.py::add` — mirror its docstring shape (summary → details → "When to use" → "Examples") and `Field(description=...)` style for every new tool. Then register it in `main.py`; without that registration step the tool exists as a Python function but is invisible to MCP clients.
