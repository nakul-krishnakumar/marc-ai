# app/utils/file_parser.py
"""
Utilities for parsing tool outputs (JSON, text).
"""
import json
from typing import Dict, Any

def parse_json_output(output: str) -> Dict[str, Any]:
    """
    Parse JSON output from static analysis tools.
    """
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON", "raw": output}
