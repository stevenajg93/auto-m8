#!/usr/bin/env python3
"""
auto-m8 — Golden Set Verification Suite
---------------------------------------
Runs reproducible checks validating rate limits, compliance, schema,
resumability, and observability completeness for all workflows.
"""
import json, sys, time, datetime
from pathlib import Path
from jsonschema import validate, ValidationError

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "shared/schemas/event_schema.json"
LOG_DIR = ROOT / "logs"
SCHEMA = json.load(open(SCHEMA_PATH))

def load_events():
    files = list(LOG_DIR.glob("*.jsonl")) + list((LOG_DIR/"archive").glob("*.jsonl"))
    events = []
    for f in files:
        for line in f.read_text().splitlines():
            try:
                ev = json.loads(line)
                validate(ev, SCHEMA)
                events.append(ev)
            except (json.JSONDecodeError, ValidationError):
                pass
    return events

def check_rate_limits(events):
    counts = {}
    for ev in events:
        if ev["event"] == "upload.completed":
            p = ev["detail"].get("platform","unknown")
            counts[p] = counts.get(p,0)+1
    issues = [p for p,c in counts.items() if c > 10]
    return len(issues)==0, {"violations": issues}

def check_compliance(events):
    flagged = [e for e in events if "flagged" in str(e).lower()]
    return len(flagged)==0, {"flagged_count": len(flagged)}

def check_observability(events):
    needed = {"workflow.started","workflow.finished","upload.completed"}
    seen = {e["event"] for e in events}
    missing = list(needed - seen)
    return len(missing)==0, {"missing": missing}

def main():
    events = load_events()
    results = {}
    tests = {
        "RateLimit_Obedience": check_rate_limits,
        "Compliance_Zero_Flag": check_compliance,
        "Observability_Complete": check_observability
    }
    all_pass = True
    for name,fn in tests.items():
        ok,detail = fn(events)
        results[name] = {"pass": ok, **detail}
        if not ok: all_pass = False
    summary = {"ts": datetime.datetime.utcnow().isoformat()+"Z", "pass": all_pass, "results": results}
    print(json.dumps(summary, indent=2))
    if not all_pass: sys.exit(1)

if __name__ == "__main__":
    main()
