import json
from mcp.server.fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP("Structural Engineering Server")

# ── Tools ──────────────────────────────────────────
@mcp.tool()
def get_current_time(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """현재 날짜와 시간을 반환합니다."""
    return datetime.now().strftime(format)

@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """두 숫자를 더합니다."""
    return a + b

@mcp.tool()
def calculate_area(width: float, height: float, unit: str = "m") -> str:
    """직사각형 면적을 계산합니다."""
    area = width * height
    return f"{area:.2f} {unit}²"

# ── Resources ──────────────────────────────────────
@mcp.resource("data://materials/concrete")
def get_concrete_properties() -> str:
    """콘크리트 재료 물성치를 반환합니다."""
    return json.dumps({
        "C24": {"fck": 24, "Ec": 25742},
        "C27": {"fck": 27, "Ec": 26871},
        "C30": {"fck": 30, "Ec": 27924},
        "C35": {"fck": 35, "Ec": 29388},
        "C40": {"fck": 40, "Ec": 30722}
    }, indent=2)

@mcp.resource("data://materials/{material_type}")
def get_material_properties(material_type: str) -> str:
    """지정된 재료의 물성치를 반환합니다."""
    materials = {
        "steel": json.dumps({"SS275": {"Fy": 275}, "SS355": {"Fy": 355}, "Es": 200000}),
        "rebar": json.dumps({"SD400": {"fy": 400}, "SD500": {"fy": 500}, "Es": 200000})
    }
    return materials.get(material_type, f"'{material_type}' not found")

if __name__ == "__main__":
    mcp.run()