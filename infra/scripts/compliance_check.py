#!/usr/bin/env python3
import json, sys

path = sys.argv[1] if len(sys.argv) > 1 else "shared/examples/example_run_pod.json"
data = json.load(open(path))

def err(msg): 
    print("❌", msg); sys.exit(1)

plan = data.get("plan", {})
pipes = plan.get("pipelines", [])
missing = []

for p in pipes:
    for step in p.get("steps", []):
        comp = step.get("compliance", {})
        # Only enforce on steps that produce/ship assets
        if step.get("name") in ("generate","package","upload","verify"):
            lp = comp.get("license_proof")
            pb = comp.get("provenance_bundle")
            blocked = comp.get("blocked", False)
            if blocked:
                missing.append(f"{p.get('market')}:{step.get('name')} — blocked=true")
            if not lp or not pb:
                missing.append(f"{p.get('market')}:{step.get('name')} — missing license_proof/provenance_bundle")

if missing:
    print("❌ Compliance preflight failed:")
    for m in missing: print(" -", m)
    sys.exit(1)

print("✅ Compliance preflight passed:", path)
