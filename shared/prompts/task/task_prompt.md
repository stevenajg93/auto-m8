# ⚙️ auto.m8 — Task Prompt (Per-Market Job Planner)

**Input Placeholders**
- `market` ∈ {POD, DIGITAL_PRODUCTS, STOCK_MEDIA, APPS_GAMES, ECOM}
- `market_spec_tldr` ≤2k tokens
- `asset_sources_index` ≤1k tokens (URLs + license hashes)
- `automation_repos_tldr` ≤1k tokens (repo names + README gists)
- `workflow_yaml` ≤3k tokens (job map)
- `quotas_cost_caps` (tokens/day, $/day)
- `ab_testing_policy` (title/tag bounds)

**Task:**  
Compress inputs and extract a plan: generate → tag → package → upload → verify → payout_log.  
Each step is idempotent, schema-valid, and pre-checked for compliance.

**Constraints:**  
- Max tokens: 10k  
- Only schema-valid JSON  
- Never upload without passed compliance gate  
- Respect per-platform rate limits  

