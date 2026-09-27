---
name: verify-api-fact
description: Use before writing or changing any code that relies on INDstocks broker/API behaviour (endpoints, fields, limits, order types, statuses, auth, WebSocket messages) — confirms the fact from official docs and records it with source and date.
---

# Verify an INDstocks API Fact

Rule (from `CLAUDE.md` and `docs/standards/trading-safety-rules.md` §5): **no guessing about broker behaviour.**

## Checklist

1. **Check the recorded facts**
   - [ ] Search `docs/research/01-indstocks-api.md` for the behaviour.
   - [ ] If it's recorded with a source and date, use it. Done.
   - [ ] If it's marked ⚠️ or listed under "Open questions", continue.

2. **Check the official docs**
   - [ ] WebFetch the relevant page under <https://api-docs.indstocks.com/>, e.g. `/conventions/`, `/Users/`, `/historicalData/`, `/Websockets/`, `/faq/`, `/api-overview/`.
   - [ ] Ask the fetch for **exact** quotes: paths, field names, types, units (ms vs s), limits, error codes.
   - [ ] Unofficial sources (blogs, `indstocks-mcp`) are hints only. Confirm in the official docs.

3. **Record it**
   - [ ] Add or update the fact in `docs/research/01-indstocks-api.md`: value, **source URL**, and "verified on YYYY-MM-DD".
   - [ ] Remove it from "Open questions" if it's resolved.
   - [ ] For regulation facts, update `docs/research/02-regulation.md` instead.

4. **If the docs don't answer it**
   - [ ] Mark it ⚠️ **unverified** and add it to "Open questions" in `01-indstocks-api.md`.
   - [ ] Code must handle the uncertainty defensively (e.g. unknown order status → `HALTED`).
   - [ ] Tell the owner, who can ask INDstocks support at instockssupport@indmoney.com.

5. **Optional live check (read-only)**
   - [ ] Only for data, quote, instrument, profile or WebSocket price behaviour.
   - [ ] Write a test marked `@pytest.mark.live_api` and run it with `uv run pytest -m live_api`.
   - [ ] Record the observed response shape (secrets redacted) as a fixture under `backend/tests/fixtures/`.

## Never

- Place, modify or cancel a **real order** to "test" behaviour.
- Generate tokens in a loop. Limit is 1/minute, and 5 wrong TOTP codes cause a lockout.
- Log or commit secrets or tokens while verifying.
