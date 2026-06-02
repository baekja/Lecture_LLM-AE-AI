from io import BytesIO
from pathlib import Path

from markitdown import MarkItDown, StreamInfo
from pydantic import Field


def binary_document_to_markdown(binary_data: bytes, file_type: str) -> str:
    """Converts binary document data to markdown-formatted text."""
    md = MarkItDown()
    file_obj = BytesIO(binary_data)
    stream_info = StreamInfo(extension=file_type)
    result = md.convert(file_obj, stream_info=stream_info)
    return result.text_content


def document_path_to_markdown(
    path: str = Field(
        description="Filesystem path to a PDF (.pdf) or DOCX (.docx) document to read and convert."
    ),
) -> str:
    """Read a PDF or DOCX file from disk and convert its contents to markdown.

    Opens the file at the given path in binary mode, infers the document
    type from the file extension (case-insensitive), and returns the
    converted markdown text. Only `.pdf` and `.docx` files are supported.

    When to use:
    - When you have a path to a local PDF or DOCX file and need its
      contents as markdown for downstream processing or display.
    - When the file is accessible on the same filesystem as the MCP server.

    When not to use:
    - For formats other than PDF or DOCX — these will be rejected.
    - When the document bytes are already in memory; call
      `binary_document_to_markdown` directly to skip the disk read.

    Examples:
    >>> document_path_to_markdown("tests/fixtures/mcp_docs.pdf")
    '# MCP Documentation\\n...'
    >>> document_path_to_markdown("/tmp/report.docx")
    '## Quarterly Report\\n- ...'
    """
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"No file found at path: {path}")
    extension = file_path.suffix.lstrip(".").lower()
    if extension not in {"pdf", "docx"}:
        raise ValueError(
            f"Unsupported file extension '.{extension}'. Only .pdf and .docx are supported."
        )
    return binary_document_to_markdown(file_path.read_bytes(), extension)
