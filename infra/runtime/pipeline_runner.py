#!/usr/bin/env python3
"""
auto-m8 — Pipeline Runner (parallel multi-market orchestrator)
Executes multiple YAML workflows concurrently with dry-run safety.
"""
import argparse, concurrent.futures, json, os, subprocess, sys, time
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
EVENTS = ROOT / "infra" / "events" / "events_log.py"

ADAPTER_MAP = {
    "Redbubble": "shared.adapters.redbubble",
    "Gumroad": "shared.adapters.gumroad",
    "Shutterstock": "shared.adapters.shutterstock",
    "GooglePlay": "shared.adapters.google_play",
    "Amazon": "shared.adapters.amazon",
}

def emit(event_type: str, detail: dict):
    subprocess.run([sys.executable, str(EVENTS), event_type, json.dumps(detail)], check=True)

def dotted_import(name: str):
    __import__(name)
    return sys.modules[name]

def route_tool(step):
    tool = step.get("tool", "")
    args = step.get("args", {}) or {}
    if tool == "uploader.api.platform":
        platform = args.get("platform")
        modname = ADAPTER_MAP.get(platform)
        if not modname:
            raise ValueError(f"No adapter mapped for {platform}")
        return dotted_import(modname)
    return None

def run_step(step, dry):
    name = step.get("name"); tool = step.get("tool"); args = step.get("args", {}) or {}
    emit("step.started", {"name": name, "tool": tool})
    time.sleep(0.05)
    if tool == "generator.image.sd":
        emit("generation.completed", {"count": args.get("n",1)})
    elif tool == "generator.text.llm":
        emit("generation.completed", {"count": args.get("n",1)})
    elif tool == "metadata.tagger":
        emit("tagging.completed", {"taxonomy": args.get("taxonomy","")})
    elif tool == "uploader.api.platform":
        adapter = route_tool(step)
        if dry:
            emit("upload.skipped.dryrun", {"platform": adapter.__name__})
        else:
            res = adapter.upload({}, {}, "env:TOKEN")
            emit("upload.completed", {"platform": adapter.__name__, "result": res})
    elif tool == "compliance.cc0.verify":
        emit("compliance.checked", {"license": args.get("license_url","")})
    else:
        emit("step.noop", {"tool": tool})
    emit("step.finished", {"name": name, "tool": tool})

def run_workflow(wf_path: Path, dry=True):
    wf = yaml.safe_load(open(wf_path))
    market = wf.get("market", wf_path.stem)
    emit("workflow.started", {"market": market, "dry": dry})
    for step in wf.get("steps", []):
        run_step(step, dry=dry)
    emit("workflow.finished", {"market": market, "dry": dry})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="Run all workflows under shared/services")
    ap.add_argument("--workflow", help="Path to a single workflow YAML")
    ap.add_argument("--dry", action="store_true", help="Dry-run mode")
    args = ap.parse_args()

    paths = []
    if args.all:
        for wf in Path(ROOT/"shared/services").rglob("*.yaml"):
            paths.append(wf)
    elif args.workflow:
        paths = [Path(args.workflow)]
    else:
        print("Use --all or --workflow <path>", file=sys.stderr)
        sys.exit(1)

    emit("orchestrator.started", {"count": len(paths)})
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(paths),5)) as ex:
        futures = [ex.submit(run_workflow, wf, args.dry) for wf in paths]
        concurrent.futures.wait(futures)
    emit("orchestrator.finished", {"count": len(paths)})

if __name__ == "__main__":
    main()
