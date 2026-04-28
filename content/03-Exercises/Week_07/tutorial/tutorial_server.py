from mcp.server.fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP("My First MCP Server")


@mcp.tool()
def get_current_time(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """현재 날짜와 시간을 반환합니다.

    Args:
        format: 날짜/시간 형식 (Python strftime 포맷)
    """
    return datetime.now().strftime(format)


@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """두 숫자를 더합니다.

    Args:
        a: 첫 번째 숫자
        b: 두 번째 숫자
    """
    return a + b


@mcp.tool()
def calculate_area(width: float, height: float, unit: str = "m") -> str:
    """직사각형 면적을 계산합니다.

    Args:
        width: 너비
        height: 높이
        unit: 단위 - 예: m, mm, cm (기본값: m)
    """
    area = width * height
    return f"{area:.2f} {unit}²"


if __name__ == "__main__":
    mcp.run()
