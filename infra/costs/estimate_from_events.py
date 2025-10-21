#!/usr/bin/env python3
import json, datetime
from pathlib import Path
COSTS = json.load(open("shared/policies/costs_v1.json"))
RATES = COSTS["rates"]; EMAP = COSTS["event_map"]

def load_lines():
    lines=[]
    p=Path("logs/events.jsonl")
    if p.exists(): lines+=p.read_text().splitlines()
    today=datetime.datetime.utcnow().strftime("%Y-%m-%d")
    ap=Path(f"logs/archive/{today}.jsonl")
    if ap.exists(): lines+=ap.read_text().splitlines()
    return [json.loads(x) for x in lines if x.strip()]

def classify(ev):
    name=ev.get("event","")
    if name=="generation.completed":
        d=ev.get("detail",{})
        return "generation.completed:image" if "count" in d else "generation.completed:text"
    return name

def cost_for(ev):
    cls=classify(ev); m=EMAP.get(cls)
    if not m or not m.get("key"): return 0.0
    key=m["key"]; mf=m.get("multiplier_field"); default=m.get("default_count",1)
    mult=ev.get("detail",{}).get(mf,default) if mf else default
    return float(RATES[key])*float(mult)

def main():
    events=load_lines(); total=0.0; buckets={}
    for e in events:
        c=cost_for(e); total+=c; cls=classify(e); buckets[cls]=buckets.get(cls,0)+c
    report={"currency":COSTS["currency"],"total_cost":round(total,6),
            "by_event":{k:round(v,6) for k,v in sorted(buckets.items())},
            "events_count":len(events)}
    print(json.dumps(report,indent=2))

if __name__=="__main__": main()
