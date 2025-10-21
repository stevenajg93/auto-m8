#!/usr/bin/env python3
"""
auto-m8 — Pipeline Runner (dry-run)
Loads a workflow YAML, validates steps, routes tool names to adapter stubs,
and emits events via infra/events/events_log.py. No real uploads in dry mode.
"""
import argparse, json, os, subprocess, sys, time
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing PyYAML. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[2]
EVENTS = ROOT / "infra" / "events" / "events_log.py"

# Simple tool router (maps 'uploader.api.platform' to adapter module)
ADAPTER_MAP = {
    "Redbubble": "shared.adapters.redbubble",
    "Gumroad": "shared.adapters.gumroad",
    "Shutterstock": "shared.adapters.shutterstock",
    "GooglePlay": "shared.adapters.google_play",
    "Amazon": "shared.adapters.amazon",
}

def emit(event_type: str, detail: dict):
    cmd = [sys.executable, str(EVENTS), event_type, json.dumps(detail)]
    subprocess.run(cmd, check=True, stdout=sys.stdout, stderr=sys.stderr)

def load_yaml(path: Path) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)

def dotted_import(module_name: str):
    __import__(module_name)
    return sys.modules[module_name]

def route_tool(step: dict):
    tool = step.get("tool", "")
    args = step.get("args", {}) or {}
    # Handle uploader.api.platform
    if tool == "uploader.api.platform":
        platform = args.get("platform")
        modname = ADAPTER_MAP.get(platform)
        if not modname:
            raise ValueError(f"No adapter mapped for platform: {platform}")
        return dotted_import(modname)
    # Other tools are stubs/no-ops for now
    return None

def run_step(step: dict, dry: bool):
    name = step.get("name", "unnamed")
    tool = step.get("tool", "noop")
    args = step.get("args", {}) or {}

    emit("step.started", {"name": name, "tool": tool})
    time.sleep(0.05)

    if tool == "generator.image.sd":
        # pretend we generated N images
        n = int(args.get("n", 1))
        emit("generation.completed", {"count": n, "args": args})
    elif tool == "metadata.tagger":
        emit("tagging.completed", {"args": args})
    elif tool == "uploader.api.platform":
        adapter = route_tool(step)
        payload = {"ref": "s3://auto-m8/stub-object"}
        meta = {"title": "Stub Asset"}
        auth = args.get("auth_ref", "env:TOKEN")
        if dry:
            emit("upload.skipped.dryrun", {"platform": adapter.__name__, "args": args})
        else:
            res = adapter.upload(payload, meta, auth)  # type: ignore[attr-defined]
            emit("upload.completed", {"platform": adapter.__name__, "result": res})
    elif tool == "uploader.browser.playwright.platform":
        # Browser fallback stub
        emit("upload.fallback.skipped.dryrun", {"args": args})
    elif tool == "compliance.cc0.verify":
        emit("compliance.checked", {"args": args})
    else:
        emit("step.noop", {"name": name, "tool": tool})

    emit("step.finished", {"name": name, "tool": tool})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflow", required=True, help="Path to workflow YAML")
    ap.add_argument("--dry", action="store_true", help="Dry-run (no real uploads)")
    args = ap.parse_args()

    wf_path = Path(args.workflow).resolve()
    if not wf_path.exists():
        print(f"Workflow not found: {wf_path}", file=sys.stderr)
        sys.exit(1)

    wf = load_yaml(wf_path)
    market = wf.get("market", "UNKNOWN")
    steps = wf.get("steps", [])

    emit("workflow.started", {"market": market, "workflow": str(wf_path), "dry": bool(args.dry)})
    for step in steps:
        run_step(step, dry=args.dry)
    emit("workflow.finished", {"market": market, "workflow": str(wf_path), "dry": bool(args.dry)})

if __name__ == "__main__":
    main()
