---
name: polymarket-activity-pull
description: "Paginate Polymarket activity trades by wallet address."
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags:
      - Polymarket
      - Trading
      - DataPull
      - Crypto
---

# Polymarket Address Trade Puller

Pull, paginate, and resolve Polymarket activity trades for any wallet address
using only public endpoints and Python's standard library. It does not place
orders, compute fees, or trade — it extracts and enriches historical trade
data so you can analyze a strategy. No pip installs; stdlib only.

## When to Use

- "Pull all Polymarket trades for wallet 0x…"
- "Get every BTC/ETH Up or Down 5m trade for this address"
- "Paginate a Polymarket account's history past the 3,500-row offset cap"
- "Resolve what each Polymarket market actually settled at (Up or Down)"
- "Reconstruct per-market PnL from a wallet's fills"

## Prerequisites

- Python 3.10+ (standard library only — `urllib`, `json`, `concurrent.futures`).
- Outbound HTTPS to:
  - `data-api.polymarket.com` (activity feed)
  - `gamma-api.polymarket.com` (market metadata + resolutions)
- No API key, auth token, or Polymarket account required (public read endpoints).
- A writable working directory for the JSONL/JSON outputs.

## How to Run

Invoke the three scripts in sequence through the `terminal` tool:

```bash
python3 scripts/pull_activity.py <WALLET> --slug-filter "updown-5m" --out trades.jsonl
python3 scripts/fetch_resolutions.py --src trades.jsonl --out resolutions.json
python3 scripts/analyze_pnl.py --trades trades.jsonl --resolutions resolutions.json --out pnl.json
```

Replace `<WALLET>` with the full `0x…` address. Drop `--slug-filter` to pull
all markets the address touched.

## Quick Reference

- Activity feed: `GET https://data-api.polymarket.com/activity?user=<addr>&limit=500[&end=<ts>]`
- Resolution feed: `GET https://gamma-api.polymarket.com/events?slug=<slug>`
- Page size cap: **500 rows/call**. Offset cap: **3,500** (so paginate by `end=<ts>`, not `offset=`).
- Walk history: `end = min(timestamp in batch) - 1`, repeat until a short (<500) page.
- Dedup key: **`transactionHash`** (window boundaries overlap; `end` is inclusive).
- Slug encodes market open time: `btc-updown-5m-<unix_ts>` → open = last segment.
- `outcomePrices` is a **JSON-encoded string** `"[\"0.99\",\"0.01\"]"`, not an array; `json.loads` it.
- Winner = the side whose parsed price equals `1.0`.

## Procedure

1. **Pull activity.** Run `pull_activity.py` with the wallet and an optional
   `--slug-filter` regex (e.g. `updown-5m` to keep only the 5-minute Up/Down
   family). The script back-paginates via `end=<min_ts>-1`, dedups by
   `transactionHash`, and writes one JSON object per line to `--out`.
2. **Check integrity.** Confirm row count equals unique `tx` count (0 dups)
   and that the `side` field is present. See Verification.
3. **Resolve markets.** Run `fetch_resolutions.py --src trades.jsonl`. It
   extracts every unique slug, fetches `gamma-api/events?slug=…` in parallel
   (16 workers), parses `outcomePrices` → winner, and checkpoint-writes
   `resolutions.json` every 500 slugs (resumable).
4. **Join for PnL.** Run `analyze_pnl.py`. It groups trades by slug, sums
   buy cost, computes payout = held winning shares × $1, and reports
   per-asset win rate, net PnL, and bps. Open/unresolved markets are skipped.
5. **(Optional) chart.** Feed the JSONL + resolutions into an offline SVG
   chart script, or read the summary JSON directly with `read_file`.

## Pitfalls

- **Offset cap is 3,500.** The `/activity` `offset` param silently stops
  returning rows past 3,500. This skill never uses `offset` — it time-windows
  with `end=<ts>`, which walks the entire history regardless of size.
- **500-row page cap.** Expect many calls for active accounts (one wallet
  needed ~1,011 pages / 505k rows). The fetcher prints progress every 50 pages.
- **BUY-only feed.** The data-api activity stream shows only this user's BUY
  fills — there are no SELL records and no fee fields. PnL here is buy-side
  exposure only; it understates costs if the platform charges fees.
- **`/pnl` is 404.** There is no public per-user PnL endpoint; reconstruct it
  from trades × resolutions (this skill does).
- **`outcomePrices` is a string.** Forgetting `json.loads` yields a string
  like `"[\"1.0\",\"0.0\"]"` and breaks winner detection.
- **Unresolved markets.** Some slugs are still open or malformed; skip them
  (the parser returns `None` and `analyze_pnl` counts them as `unresolved`).
- **Asset mixing.** BTC and ETH 5m slugs share the `updown-5m` suffix but
  differ by `btc-` / `eth-` prefix. Filter or split on the prefix.

## Verification

After the pull, prove integrity with:

```bash
python3 -c "import json; rows=[json.loads(l) for l in open('trades.jsonl')]; print('rows',len(rows),'unique_tx',len({r['tx'] for r in rows}))"
```

Expect `rows == unique_tx` (zero duplicates). After resolution,
`resolutions.json` should have one key per unique slug and `with_winner`
count ≈ total slugs. After `analyze_pnl.py`, the printed `net_pnl` and
`win_rate` should be finite and plausible (convergence strategies land near
50–70% win rate).
