#!/usr/bin/env python3
import json, datetime, sys, os
LOG_PATH = "logs/events.jsonl"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

def emit(event_type, detail):
    record = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "event": event_type,
        "detail": detail
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")
    print(f"🛰️  Event logged: {event_type}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: events_log.py <event_type> '<json_detail>'")
        sys.exit(1)
    emit(sys.argv[1], json.loads(sys.argv[2]))
