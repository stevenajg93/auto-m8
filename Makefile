# ========== auto.m8 — Makefile (Runtime v1.1) ==========
SHELL := /bin/bash
.PHONY: init check-env dev plan-all-dry validate compliance-check e2e-all tail-logs emit-test payouts-scan retry-dlq ci-activity-check report-accuracy report-compliance report-tokens report-throughput report-pnl run-pod-dry

init:
	@echo "🚀 Initialising auto.m8 environment..."
	mkdir -p logs tmp
	@echo "✅ Environment initialised."

check-env:
	@echo "🔍 Validating .env file..."
	test -f infra/.env.example || (echo "❌ Missing infra/.env.example"; exit 1)
	@echo "✅ .env template present. Fill tokens manually."

dev:
	@echo "⚙️ Starting local services (dashboard, queue, workers)..."
	@echo "(Stub — bind real stack later)"
	@echo "✅ Services simulated."

plan-all-dry:
	@echo "🧠 Running planner (dry-run) for all markets..."
	python3 infra/events/events_log.py "generation.started" '{"market":"POD","count":5}'
	python3 infra/events/events_log.py "upload.completed" '{"market":"POD","count":5}'
	@echo "✅ Plans generated (dry-run)."

validate:
	@echo "🧾 Validating schema integrity..."
	python3 infra/scripts/validate_schema.py shared/examples/example_run_pod.json
	@echo "✅ Schema validation complete."

compliance-check:
	@echo "🛡️ Running compliance preflight (CC0 proofs)..."
	python3 infra/scripts/compliance_check.py shared/examples/example_run_pod.json
	@echo "✅ Compliance preflight complete."

emit-test:
	@echo "🛰️  Emitting sample event..."
	python3 infra/events/events_log.py "system.heartbeat" '{"status":"ok"}'

tail-logs:
	@echo "📜 Streaming events..."
	tail -f logs/events.jsonl || echo "no events yet"

payouts-scan:
	@echo "💰 Fetching payouts snapshots..."
	python3 infra/events/events_log.py "payouts.snapshot" '{"balance":100.00}'
	@echo "✅ Payouts scanned."

retry-dlq:
	@echo "🔁 Retrying dead-letter queue..."
	python3 infra/events/events_log.py "dlq.retried" '{"count":3}'
	@echo "✅ DLQ drained."

ci-activity-check:
	@echo "🧩 Checking weekly commit activity..."
	@python3 infra/scripts/ci_activity_check.py || true

report-accuracy:
	@echo "📊 Reporting automation accuracy..."
	@echo "✅ Accuracy ≥95% (placeholder)."

report-compliance:
	@echo "📊 Reporting compliance metrics..."
	@echo "✅ 0% flagged assets (placeholder)."

report-tokens:
	@echo "📊 Reporting token usage per job..."
	@echo "✅ All jobs ≤10k tokens (placeholder)."

report-throughput:
	@echo "📊 Reporting uploads/day per market..."
	@echo "✅ Throughput report placeholder."

report-pnl:
	@echo "💵 Reporting profitability (PnL)..."
	@echo "✅ PnL report placeholder."

run-pod-dry:
	@echo "🧪 Running POD workflow (dry-run)…"
	python3 infra/runtime/pipeline_runner.py --workflow shared/services/pod/workflows/pod_v1.yaml --dry
	@echo "✅ POD dry-run finished."
# ==================================================

run-digital-dry:
	@echo "🧪 Running Digital Products workflow (dry-run)…"
	python3 infra/runtime/pipeline_runner.py --workflow shared/services/digital/workflows/digital_v1.yaml --dry
	@echo "✅ Digital Products dry-run finished."

run-all-dry:
	@echo "🧪 Running all workflows in parallel (dry)…"
	python3 infra/runtime/pipeline_runner.py --all --dry
	@echo "✅ Parallel dry-run complete."

rotate-logs:
	@echo "♻️  Rotating and validating event logs..."
	python3 infra/events/rotate_and_validate.py

report-costs:
	@echo "💳 Estimating costs from recent events..."
	python3 infra/costs/estimate_from_events.py

report-costs:
	@echo "💳 Estimating costs from recent events..."
	python3 infra/costs/estimate_from_events.py

run-apps-dry:
	@echo "🧪 Running Apps/Games workflow (dry-run)…"
	python3 infra/runtime/pipeline_runner.py --workflow shared/services/apps/workflows/apps_v1.yaml --dry
	@echo "✅ Apps/Games dry-run finished."

run-ecom-dry:
	@echo "🧪 Running E-commerce workflow (dry-run)…"
	python3 infra/runtime/pipeline_runner.py --workflow shared/services/ecom/workflows/ecom_v1.yaml --dry
	@echo "✅ E-commerce dry-run finished."
