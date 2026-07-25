#!/usr/bin/env python3
"""Back-paginate Polymarket activity trades for a wallet address.

Public endpoint, stdlib only. Walks history via end=<min_ts>-1 (the only
viable method past the 3,500 offset cap), dedups by transactionHash, and
writes one JSON object per line to --out.
"""
import argparse, json, re, sys, time, urllib.request, urllib.error

BASE = "https://data-api.polymarket.com/activity"
LIMIT = 500
MAX_PAGES = 5000


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wallet")
    ap.add_argument("--slug-filter", default=None,
                    help="regex; keep only slugs matching (e.g. 'updown-5m')")
    ap.add_argument("--out", default="trades.jsonl")
    ap.add_argument("--max-pages", type=int, default=MAX_PAGES)
    a = ap.parse_args()

    pat = re.compile(a.slug_filter) if a.slug_filter else None
    seen, total, matched, pages = set(), 0, 0, 0
    cursor = None
    with open(a.out, "w") as f:
        while pages < a.max_pages:
            url = f"{BASE}?user={a.wallet}&limit={LIMIT}"
            if cursor is not None:
                url += f"&end={cursor}"
            try:
                data = fetch(url)
            except Exception as e:
                print(f"ERR page {pages}: {e}", file=sys.stderr); time.sleep(2); continue
            pages += 1
            if not data:
                print("empty page -> stop"); break
            pmin = min(t["timestamp"] for t in data)
            for t in data:
                total += 1
                h = t.get("transactionHash")
                if h in seen:
                    continue
                seen.add(h)
                if t.get("type") != "TRADE":
                    continue
                slug = t.get("slug", "") or ""
                if pat and not pat.search(slug):
                    continue
                matched += 1
                rec = {
                    "ts": t["timestamp"], "slug": slug,
                    "eventSlug": t.get("eventSlug"), "title": t.get("title"),
                    "side": t.get("side"), "outcome": t.get("outcome"),
                    "outcomeIndex": t.get("outcomeIndex"), "price": t.get("price"),
                    "size": t.get("size"), "usdcSize": t.get("usdcSize"),
                    "conditionId": t.get("conditionId"), "asset": t.get("asset"),
                    "tx": h,
                }
                f.write(json.dumps(rec) + "\n")
            cursor = pmin - 1
            if len(data) < LIMIT:
                print("short page -> stop"); break
            if pages % 50 == 0:
                print(f"progress pages={pages} total={total} matched={matched}", file=sys.stderr)
    print(f"DONE pages={pages} total={total} matched={matched}")


if __name__ == "__main__":
    main()
