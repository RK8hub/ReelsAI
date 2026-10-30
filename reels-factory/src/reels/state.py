import json
from pathlib import Path
from datetime import datetime

STATES = ["created","scripting","planning","rendering","ready","exported"]

def new_project(root: Path, brief) -> Path:
    slug = brief.topic.lower().replace(" ","-")[:40] or "proyecto"
    pid = datetime.now().strftime("%Y-%m-%d") + "_" + slug
    d = root / "projects" / pid
    d.mkdir(parents=True, exist_ok=True)
    (d / "assets").mkdir(exist_ok=True)
    (d / "audio").mkdir(exist_ok=True)
    (d / "renders").mkdir(exist_ok=True)
    (d / "export").mkdir(exist_ok=True)
    (d / "brief.json").write_text(brief.model_dump_json(indent=2))
    (d / "project.json").write_text(json.dumps({
        "id": pid, "state": "created", "mode": brief.mode,
        "stages": {}, "scenes": {}, "errors": [], "regenerations": 0
    }, indent=2))
    return d

def set_state(proj: Path, state: str):
    p = proj / "project.json"
    data = json.loads(p.read_text())
    data["state"] = state
    p.write_text(json.dumps(data, indent=2))