#!/usr/bin/env python3
# Ensure ≥2 commits in the last 7 days on default branch
import subprocess, sys, datetime
since=(datetime.datetime.utcnow()-datetime.timedelta(days=7)).isoformat()+"Z"
log=subprocess.check_output(["git","log","--since",since,"--pretty=%H"]).decode().strip().splitlines()
count=len([h for h in log if h.strip()])
if count<2:
    print(f"❌ CI activity check failed: {count} commits in the last 7 days (need ≥2).")
    sys.exit(1)
print(f"✅ CI activity check OK: {count} commits in last 7 days.")
