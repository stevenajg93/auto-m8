#!/usr/bin/env python3
"""
Rotates logs/events.jsonl into logs/archive/YYYY-MM-DD.jsonl
and validates each entry against AutoM8Event.v1 schema.
"""
import json, datetime, os, sys
from jsonschema import validate, ValidationError
from pathlib import Path

LOG_PATH = Path("logs/events.jsonl")
ARCHIVE_DIR = Path("logs/archive")
SCHEMA = json.load(open("shared/schemas/event_schema.json"))

if not LOG_PATH.exists():
    print("No events log found.")
    sys.exit(0)

ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
archive_file = ARCHIVE_DIR / f"{today}.jsonl"

valid, invalid = 0, 0
with open(LOG_PATH) as src, open(archive_file, "a") as dst:
    for line in src:
        try:
            obj = json.loads(line)
            validate(instance=obj, schema=SCHEMA)
            dst.write(json.dumps(obj) + "\n")
            valid += 1
        except (json.JSONDecodeError, ValidationError):
            invalid += 1

LOG_PATH.write_text("")  # clear current log
print(f"✅ Rotated {valid} valid events → {archive_file}")
if invalid:
    print(f"⚠️ {invalid} invalid events skipped.")
