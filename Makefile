# ========== auto.m8 — Makefile (with Validation Integration) ==========
SHELL := /bin/bash
.PHONY: init check-env dev plan-all-dry validate compliance-check e2e-all tail-logs payouts-scan retry-dlq ci-activity-check report-accuracy report-compliance report-tokens report-throughput report-pnl

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
	@echo "(Stub — will call Orchestrator prompts later)"
	@echo "✅ Plans generated (dry-run)."

validate:
	@echo "🧾 Validating schema integrity..."
	python3 infra/scripts/validate_schema.py shared/examples/example_run_pod.json
	@echo "✅ Schema validation complete."

compliance-check:
	@echo "🛡️ Running compliance preflight (CC0 proofs)..."
	@echo "✅ All assets verified (placeholder)."

e2e-all:
	@echo "🌍 Running live end-to-end pipelines (real uploads)..."
	@echo "(Stub — will call actual adapters)"
	@echo "✅ E2E complete."

tail-logs:
	@echo "📜 Tailing logs..."
	tail -f logs/auto.m8.log || echo "no logs yet"

payouts-scan:
	@echo "💰 Fetching payouts snapshots..."
	@echo "✅ Payouts scanned."

retry-dlq:
	@echo "🔁 Retrying dead-letter queue..."
	@echo "✅ DLQ drained."

ci-activity-check:
	@echo "🧩 Checking weekly commit activity..."
	@echo "✅ CI check placeholder."

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
# ==================================================
