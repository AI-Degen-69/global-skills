#!/usr/bin/env python3
"""Fetch Polymarket market resolutions for every slug in a trades JSONL.

Parallel + checkpointed + resumable. Writes slug -> {winner, outcomePrices,
endDate, conditionId}. Runs from the skill directory or any cwd (use --src/--out).
"""
import argparse, json, threading, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

WORKERS = 16
RETRIES = 4
_lock = threading.Lock()


def fetch(url):
    for _ in range(RETRIES):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(0.5)
        except Exception:
            time.sleep(0.5)
    return None


def parse(ev):
    if not ev or not isinstance(ev, list) or not ev:
        return None
    ev = ev[0]
    mkt = (ev.get("markets") or [{}])[0]
    try:
        op = json.loads(mkt.get("outcomePrices", "[]"))
    except Exception:
        op = []
    winner = None
    if len(op) == 2:
        try:
            u, d = float(op[0]), float(op[1])
            if u == 1.0 and d == 0.0:
                winner = "Up"
            elif d == 1.0 and u == 0.0:
                winner = "Down"
        except Exception:
            pass
    return {"winner": winner, "outcomePrices": op, "endDate": mkt.get("endDate"),
            "conditionId": mkt.get("conditionId")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="trades.jsonl")
    ap.add_argument("--out", default="resolutions.json")
    a = ap.parse_args()

    slugs = set()
    with open(a.src) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("slug"):
                slugs.add(r["slug"])
    slugs = sorted(slugs)
    print(f"unique slugs: {len(slugs)}")

    resolved = {}
    if Path(a.out).exists():
        resolved = json.loads(Path(a.out).read_text())
        print(f"loaded {len(resolved)} existing")
    todo = [s for s in slugs if s not in resolved]
    print(f"remaining: {len(todo)}")

    done = ok = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(fetch, f"https://gamma-api.polymarket.com/events?slug={s}"): s
                for s in todo}
        for fut in as_completed(futs):
            s = futs[fut]
            res = fut.result()
            parsed = parse(res) if isinstance(res, list) else None
            with _lock:
                resolved[s] = parsed
                done += 1
                if parsed and parsed.get("winner"):
                    ok += 1
                if done % 500 == 0:
                    Path(a.out).write_text(json.dumps(resolved))
                    print(f"  {done}/{len(todo)} ok={ok}")
    Path(a.out).write_text(json.dumps(resolved))
    print(f"DONE total={len(resolved)} with_winner={ok}")


if __name__ == "__main__":
    main()
