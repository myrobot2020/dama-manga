import json
from pathlib import Path

def list_valid_suttas():
    """Returns sutta IDs from local data if available, else defaults."""
    sutta_file = Path("data/an_sutta_names.txt")
    if sutta_file.exists():
        try:
            with open(sutta_file, "r", encoding="utf-8") as f:
                return [line.split("|")[0].strip() for line in f.readlines() if "|" in line]
        except:
            pass
    return ["an1.1", "an1.2", "an1.3", "an1.10", "sn1.1", "sn1.2", "dn1", "mn1"]

def get_sutta_content(sutta_id):
    """Returns mock content for the given sutta ID."""
    return {
        "title": f"Mock Title for {sutta_id}",
        "content": f"This is mock content for {sutta_id}. In this sutta, the Buddha discusses various qualities of mind and practice."
    }
