# Bonus: run with `python mcp_server.py` (port 8001)
from mcp.server.fastmcp import FastMCP
from shared_tools import triage_logic, specialist_logic

mcp = FastMCP("medical-tools", port=8001)

@mcp.tool()
def triage_symptom(symptom: str, duration_days: int = 0, severity: str = "mild") -> dict:
    """Gets the triage level (self-care / see a doctor / urgent) for a symptom.
    Use for any symptom the user describes. Deterministic rule table, report as returned."""
    return triage_logic(symptom, duration_days, severity)

@mcp.tool()
def specialist_finder(condition: str, triage_level: str) -> dict:
    """Finds which doctor or department to see. Call only after triage_symptom returned
    'see a doctor' or 'urgent', passing that exact level."""
    return specialist_logic(condition, triage_level)

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
