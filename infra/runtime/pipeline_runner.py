#!/usr/bin/env python3
"""
auto-m8 — Pipeline Runner (parallel multi-market orchestrator)
Guarantees workflow.finished emission for observability completeness.
"""
import argparse, concurrent.futures, json, subprocess, sys, time
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
EVENTS = ROOT / "infra" / "events" / "events_log.py"
ADAPTER_MAP = {
    "Redbubble": "shared.adapters.redbubble",
    "Gumroad": "shared.adapters.gumroad",
    "Shutterstock": "shared.adapters.shutterstock",
    "GooglePlay": "shared.adapters.google_play",
    "Amazon": "shared.adapters.amazon"
}

def emit(event, detail):
    subprocess.run([sys.executable, str(EVENTS), event, json.dumps(detail)], check=True)

def dotted_import(name):
    __import__(name)
    return sys.modules[name]

def route_tool(step):
    if step.get("tool") == "uploader.api.platform":
        p = step["args"].get("platform")
        m = ADAPTER_MAP.get(p)
        if m: return dotted_import(m)
    return None

def run_step(step, dry):
    name, tool, args = step.get("name"), step.get("tool"), step.get("args",{})
    emit("step.started", {"name":name,"tool":tool})
    time.sleep(0.05)
    if tool.startswith("generator."):
        emit("generation.completed", {"args":args})
    elif tool=="metadata.tagger":
        emit("tagging.completed", {"args":args})
    elif tool=="uploader.api.platform":
        adapter=route_tool(step)
        if dry:
            emit("upload.skipped.dryrun", {"platform":adapter.__name__ if adapter else "unknown"})
        else:
            res=adapter.upload({}, {}, "env:TOKEN") if adapter else {"status":"no-adapter"}
            emit("upload.completed", {"platform":adapter.__name__ if adapter else "unknown","result":res})
    elif tool=="compliance.cc0.verify":
        emit("compliance.checked", {"args":args})
    emit("step.finished", {"name":name,"tool":tool})

def run_workflow(path,dry=True):
    wf=yaml.safe_load(open(path))
    market=wf.get("market",path.stem)
    emit("workflow.started", {"market":market,"dry":dry})
    try:
        for s in wf.get("steps",[]): run_step(s,dry)
    finally:
        emit("workflow.finished", {"market":market,"dry":dry})

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--all",action="store_true")
    ap.add_argument("--workflow")
    ap.add_argument("--dry",action="store_true")
    a=ap.parse_args()
    files=[]
    if a.all:
        for wf in (ROOT/"shared/services").rglob("*.yaml"): files.append(wf)
    elif a.workflow: files=[Path(a.workflow)]
    else:
        print("Use --all or --workflow <path>",file=sys.stderr); sys.exit(1)
    emit("orchestrator.started", {"count":len(files)})
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(files),5)) as ex:
        futures=[ex.submit(run_workflow,f,a.dry) for f in files]
        concurrent.futures.wait(futures)
    emit("orchestrator.finished", {"count":len(files)})
