#!/usr/bin/env python3
import json, sys, os
from jsonschema import validate, ValidationError

schema_path = "shared/schemas/output_schema.json"
data_path = sys.argv[1] if len(sys.argv) > 1 else "shared/examples/example_run_pod.json"

with open(schema_path) as f:
    schema = json.load(f)
with open(data_path) as f:
    data = json.load(f)

try:
    validate(instance=data, schema=schema)
    print("✅ Schema validation passed for", data_path)
except ValidationError as e:
    print("❌ Schema validation failed:", e.message)
    sys.exit(1)
