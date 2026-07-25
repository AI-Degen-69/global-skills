#!/usr/bin/env python3
"""Join Polymarket trades to resolutions and compute per-market / per-asset PnL.

Holds positions to resolution: payout = held winning shares x $1.
Reports win rate, net PnL, bps, and edge by price/size bucket. Skips
unresolved markets.
"""
import argparse, json, statistics
from collections import defaultdict
from pathlib import Path


def bucket_price(p):
    if p < 0.1: return "<0.10"
    if p < 0.2: return "0.10-0.20"
    if p < 0.3: return "0.20-0.30"
    if p < 0.4: return "0.30-0.40"
    if p < 0.5: return "0.40-0.50"
    if p < 0.6: return "0.50-0.60"
    if p < 0.7: return "0.60-0.70"
    if p < 0.8: return "0.70-0.80"
    if p < 0.9: return "0.80-0.90"
    return ">=0.90"


def bucket_size(s):
    if s < 1: return "<$1"
    if s < 5: return "$1-5"
    if s < 20: return "$5-20"
    if s < 100: return "$20-100"
    if s < 500: return "$100-500"
    return "$500+"


def asset(slug):
    if slug.startswith("btc"): return "BTC"
    if slug.startswith("eth"): return "ETH"
    return "OTHER"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trades", required=True)
    ap.add_argument("--resolutions", required=True)
    ap.add_argument("--out", default="pnl.json")
    a = ap.parse_args()

    res = json.loads(Path(a.resolutions).read_text())
    by_mkt = defaultdict(list)
    for line in open(a.trades):
        line = line.strip()
        if line:
            by_mkt[json.loads(line)["slug"]].append(json.loads(line))

    out = {}
    for want in ["FULL", "BTC", "ETH"]:
        agg = {"cost": 0.0, "payout": 0.0, "pnl": 0.0, "win": 0, "lose": 0, "flat": 0, "unres": 0}
        by_price = defaultdict(lambda: {"cost": 0.0, "payout": 0.0, "n": 0, "w": 0})
        by_size = defaultdict(lambda: {"cost": 0.0, "payout": 0.0, "n": 0, "w": 0})
        for slug, trs in by_mkt.items():
            if want != "FULL" and asset(slug) != want:
                continue
            rd = res.get(slug)
            if not rd or not rd.get("winner"):
                agg["unres"] += 1
                continue
            w = rd["winner"]
            cost = sum(r.get("usdcSize", 0) or 0 for r in trs)
            payout = 0.0
            for r in trs:
                p = r.get("price")
                if not p:
                    continue
                shares = (r.get("usdcSize", 0) or 0) / p
                if r["outcome"] == w:
                    payout += shares
                b = bucket_price(p); sz = (r.get("usdcSize", 0) or 0)
                by_price[b]["cost"] += sz; by_price[b]["payout"] += (shares if r["outcome"] == w else 0)
                by_price[b]["n"] += 1; by_price[b]["w"] += 1 if r["outcome"] == w else 0
                s = bucket_size(sz)
                by_size[s]["cost"] += sz; by_size[s]["payout"] += (shares if r["outcome"] == w else 0)
                by_size[s]["n"] += 1; by_size[s]["w"] += 1 if r["outcome"] == w else 0
            pnl = payout - cost
            agg["cost"] += cost; agg["payout"] += payout; agg["pnl"] += pnl
            if pnl > 0: agg["win"] += 1
            elif pnl < 0: agg["lose"] += 1
            else: agg["flat"] += 1
        agg["win_rate"] = 100 * agg["win"] / max(1, agg["win"] + agg["lose"])
        agg["bps"] = 10000 * agg["pnl"] / max(1, agg["cost"])
        agg["roi_pct"] = 100 * agg["pnl"] / max(1, agg["cost"])
        agg["by_price"] = {k: {**v, "edge": v["payout"] - v["cost"],
                               "winrate": 100 * v["w"] / max(1, v["n"])} for k, v in by_price.items()}
        agg["by_size"] = {k: {**v, "edge": v["payout"] - v["cost"],
                              "winrate": 100 * v["w"] / max(1, v["n"])} for k, v in by_size.items()}
        out[want] = agg

    Path(a.out).write_text(json.dumps(out, indent=2, default=str))
    for k, v in out.items():
        print(f"[{k}] resolved={v['win']+v['lose']+v['flat']} win_rate={v['win_rate']:.1f}% "
              f"net_pnl=${v['pnl']:,.0f} bps={v['bps']:.1f}")


if __name__ == "__main__":
    main()
