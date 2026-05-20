from pathlib import Path
import json

def load_policy(path="policies/policy.json"):
    p=Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Policy file not found: {p}")
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)
