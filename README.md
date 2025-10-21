# auto.m8 — Fully Autonomous Multi-Marketplace Revenue Engine

Overview
auto.m8 is a self-driving factory for digital assets that generates → tags → uploads → earns → reinvests across:
- POD
- Digital Products
- Stock Media
- Apps/Games
- E-commerce

Run & Test Sheet
- make init                : Bootstrap environment
- make check-env           : Verify env template
- make dev                 : Start local services (stub)
- make plan-all-dry        : Simulate all pipelines
- make validate            : Schema validation
- make compliance-check    : License + provenance gate
- make e2e-all             : Live run (future)
- make payouts-scan        : Check balances
- make retry-dlq           : Retry failed tasks
- make report-*            : Metrics and analytics

Structure
infra/
  scripts/
shared/
  prompts/{system,task,tool,critique}/
  schemas/
  examples/

Next Steps
1. Bind real adapters in /shared/adapters
2. Add real workflows in /shared/services/*/workflows/
3. Configure CI for weekly commit check
4. Push to GitHub for public visibility
