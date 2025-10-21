# 🔧 auto.m8 — Tool-Use Prompt (Adapters Directory)

**Abstract Tools (bind later by CTO):**
- generator.image.sd → Stable Diffusion / SDXL (local)
- generator.music.mg → MusicGen (local)
- generator.text.llm → LLM for descriptions/titles
- metadata.tagger → keyword extractor
- uploader.api.[platform] → native API client
- uploader.browser.playwright.[platform] → browser fallback
- compliance.cc0.verify → license/provenance check
- optimizer.ab.title_tag → AB framework
- scheduler.rate_limit → token bucket per platform
- payouts.fetch.[platform] → balance snapshot
- monitor.events.emit → event logger
- retry.queue.push/pop → DLQ handler

**Tool Invocation Contract**
```json
{
  "op": "uploader.api.platform",
  "args": {
    "payload_ref": "s3://...",
    "meta_ref": "ipfs://...",
    "auth_ref": "env:PLATFORM_TOKEN"
  },
  "on_fail": {
    "fallback_op": "uploader.browser.playwright.platform",
    "policy": "rotate_proxy, human_solve_captcha=false"
  }
}

