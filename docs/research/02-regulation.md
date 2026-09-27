# Regulation — SEBI Retail Algo Framework

- **Status:** partially verified on 2026-09-27. **Confirm with INDstocks support before going live.** Email: instockssupport@indmoney.com

## What is known

| Fact | Confidence | Source |
|---|---|---|
| SEBI's retail algo framework was issued in early 2025 and rolled out in phases | High | [CAalley](https://www.caalley.com/news-updates/indian-news/sebi-extends-retail-algo-trading-rollout-full-compliance-by-april-2026) |
| **Fully applicable to all brokers from 1 April 2026**, so it is in force today | High | CAalley |
| Order placement through the API needs a **whitelisted static IP** (NSE/INVG/67858, 5 May 2025) | High | [INDstocks FAQ](https://api-docs.indstocks.com/faq/) |
| An orders-per-second (OPS) threshold of **10 OPS** applies. Below it you are a regular API user; above it, strategy registration is mandatory | Medium (secondary sources) | [QuantInsti](https://www.quantinsti.com/articles/algorithmic-trading-india/), [AlgoBulls](https://algobulls.com/blog/industry-insights-and-updates/sebi-new-algotrading-regulations-for-retail-investors-2026) |
| INDstocks order API limit is 10 req/s | High | INDstocks Conventions |

## What this means for us

- Our bot places **at most ~6–10 orders per day**, far below 10 OPS.
- **Static IP is mandatory before live mode.** Options:
  - a static IP from the ISP, or
  - an India-region VPS (~₹500–1,000/month).

  Paper mode needs neither.
- The code must never burst orders. The order client has a hard cap of **2 orders/second** (our own limit, stricter than the broker's).

## Must confirm with the broker (before Step 4, live)

- [ ] Does a self-built, personal-use API bot below 10 OPS need any algo-ID tag or registration with INDstocks?
- [ ] Is any extra consent or declaration needed on the INDstocks account for API order placement?
- [ ] Can the static IP be an IPv4 of a cloud VPS?

Record the answers here with date and source.
