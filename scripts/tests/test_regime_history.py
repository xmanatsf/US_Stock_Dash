"""Diff the FULL 1,255-day regime history and score series against the shipped RenMac dashboard.

Matching the final day's verdict samples one bar out of 1,255. The pillars here were rebuilt from
a specification rather than line-ported, so the only real test of score_at / classify /
debounce_labels is the whole history: label by label, score by score, and run by run.

Exact equality is not expected. What matters is that the regime DISTRIBUTION and the run
structure agree, and above all that the capitulation split fires on the same days -- 'Capitulation
/ washout' and 'Capitulation inside a confirmed top' carry opposite instructions off identical
measurements, so a disagreement there is the most consequential possible divergence.

    python scripts/tests/test_regime_history.py [--verbose]
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# The score block prints a Greek delta; a Windows console defaults to cp1252 and would
# raise UnicodeEncodeError there, killing a diagnostic that has nothing wrong with it.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GOLDEN = os.path.join(ROOT, "reference", "golden", "semi_renmac_data.json")
OURS = os.path.join(ROOT, "data", "processed", "semis", "summary.json")


def runs(labels, dates):
    out = []
    for i, l in enumerate(labels):
        if l is None:
            continue
        if out and out[-1][0] == l:
            out[-1][2] = dates[i]
        else:
            out.append([l, dates[i], dates[i]])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(OURS):
        print("build the semis tab first: python scripts/build_semis.py")
        return 1
    g = json.load(open(GOLDEN, encoding="utf-8"))
    o = json.load(open(OURS, encoding="utf-8"))

    gdates, odates = g["dates"], o["dates"]
    print(f"[grid] golden {len(gdates)} days ({gdates[0]}..{gdates[-1]}), "
          f"ours {len(odates)} days ({odates[0]}..{odates[-1]}), identical={gdates == odates}")

    # The goldens are a fixed capture of one workbook vintage; CapIQ's 5y window ROLLS rather than
    # extends, so a data refresh moves both ends of our grid and the two will never again be
    # identical. Compare on the date INTERSECTION instead of giving up -- the divergence this file
    # exists to track (see reference/golden/README.md) must survive routine refreshes.
    gi = {d: i for i, d in enumerate(gdates)}
    oi = {d: i for i, d in enumerate(odates)}
    shared = [d for d in gdates if d in oi]
    if not shared:
        print("  FAIL the two grids do not overlap at all; nothing is comparable")
        return 1
    if gdates != odates:
        gonly = [d for d in gdates if d not in oi]
        oonly = [d for d in odates if d not in gi]
        print(f"  overlap {len(shared)} sessions ({shared[0]}..{shared[-1]})")
        print(f"  golden-only {len(gonly)} sessions"
              + (f" ({gonly[0]}..{gonly[-1]})" if gonly else ""))
        print(f"  ours-only   {len(oonly)} sessions"
              + (f" ({oonly[0]}..{oonly[-1]})" if oonly else ""))

    gd = od = shared
    n = len(shared)
    gr = [g["regimes"][gi[d]] for d in shared]
    orr = [o["regimes"][oi[d]] for d in shared]
    gs = [g["scores"][gi[d]] for d in shared]
    os_ = [o["scores"][oi[d]] for d in shared]

    both = [i for i in range(n) if gr[i] is not None and orr[i] is not None]
    agree = sum(1 for i in both if gr[i] == orr[i])
    print(f"\n[labels] {len(both)} comparable sessions, {agree} identical "
          f"({100.0*agree/max(1,len(both)):.1f}%)")

    gc, oc = Counter(gr[i] for i in both), Counter(orr[i] for i in both)
    keys = sorted(set(gc) | set(oc), key=lambda k: -gc.get(k, 0))
    print(f"\n{'regime':<40}{'golden':>8}{'ours':>8}{'delta':>8}")
    for k in keys:
        a, b = gc.get(k, 0), oc.get(k, 0)
        print(f"  {k:<38}{a:>8}{b:>8}{b-a:>+8}")

    # the consequential one
    print("\n[capitulation split] identical measurements, opposite instruction")
    for lab in ("Capitulation / washout", "Capitulation inside a confirmed top"):
        gi = {gd[i] for i in both if gr[i] == lab}
        oi = {gd[i] for i in both if orr[i] == lab}
        inter = len(gi & oi)
        print(f"  {lab:<38} golden {len(gi):>4}  ours {len(oi):>4}  overlap {inter:>4}")
        if gi and oi and not (gi & oi):
            print("    WARN the two builds place this label on entirely different days")

    # scores
    pairs = [(gs[i], os_[i]) for i in range(n) if gs[i] is not None and os_[i] is not None]
    if pairs:
        diffs = [abs(a - b) for a, b in pairs]
        diffs_sorted = sorted(diffs)
        mean = sum(diffs) / len(diffs)
        med = diffs_sorted[len(diffs_sorted) // 2]
        p90 = diffs_sorted[int(len(diffs_sorted) * 0.9)]
        within = sum(1 for d in diffs if d <= 10)
        print(f"\n[scores] {len(pairs)} comparable  mean|Δ|={mean:.1f}  median={med:.1f}  "
              f"p90={p90:.1f}  max={max(diffs):.1f}")
        print(f"  within 10 points: {within} ({100.0*within/len(pairs):.1f}%)")
        # direction agreement matters more than level
        same_sign = sum(1 for a, b in pairs if (a >= 0) == (b >= 0))
        print(f"  same sign: {same_sign} ({100.0*same_sign/len(pairs):.1f}%)")

    grr, orr_runs = runs(gr, gd), runs(orr, od)
    print(f"\n[runs] golden {len(grr)} runs, ours {len(orr_runs)}")
    print(f"  golden last: {grr[-1][0]} from {grr[-1][1]}")
    print(f"  ours   last: {orr_runs[-1][0]} from {orr_runs[-1][1]}")

    same_day = gdates[-1] == odates[-1]
    print(f"\n[final verdict]  golden last session {gdates[-1]}, ours {odates[-1]}"
          f"{'' if same_day else '  -- DIFFERENT DAYS, so a mismatch below is expected, not a defect'}")
    gv = g["verdict"]
    ov = o["verdict"]
    for k in ("regime", "score", "coverage", "comp", "peakDate", "peakVal", "drawdown"):
        a, b = gv.get(k), ov.get(k)
        ok = ("==" if a == b else "!=") if same_day else ("==" if a == b else "differs")
        print(f"  {k:<12} golden={str(a):<24} ours={str(b):<24} {ok}")
    if not same_day:
        print("  The seven-field final-verdict match was verified on the 20260807 vintage, where both\n"
              "  builds ended on 2026-08-07. Once the data is refreshed this block compares two\n"
              "  different sessions and is informational only -- the overlap sections above are the\n"
              "  comparison that still means something.")

    if args.verbose:
        print("\n[first 25 label disagreements]")
        shown = 0
        for i in both:
            if gr[i] != orr[i]:
                print(f"  {gd[i]}  golden={gr[i]:<36} ours={orr[i]}")
                shown += 1
                if shown >= 25:
                    break

    print("\nThis is a comparison, not a pass/fail gate: the engine deliberately differs from the "
          "legacy build in composite construction and percentile causality. Investigate any "
          "capitulation-split disagreement or a regime distribution that moves by more than "
          "a few percent of sessions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
