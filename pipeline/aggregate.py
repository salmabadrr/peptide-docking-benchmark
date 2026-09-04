"""Roll up results/summary.csv into per-method and per-target views.

Reads  results/summary.csv  (written by run_dockq.py)
Writes results/by_method.csv    one row per method: n, DockQ mean/median, CAPRI rates
       results/by_target.csv    target x method matrix of best-pose DockQ
       results/report.md        human-readable summary

Only rank == "best" rows feed the headline stats. Rows whose `note` starts with
ERROR are counted separately (n_error) and never as DockQ 0. `caution` targets
(partial native peptide) are marked with * and also reported as an ok-only subset.

CPU only, stdlib only.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import statistics as stats
from pathlib import Path

from config import RESULTS, capri_class, load_targets


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def read_rows(summary_csv: Path) -> list[dict]:
    with summary_csv.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def method_stats(rows: list[dict]) -> dict:
    scored = [r for r in rows if _f(r["dockq"]) is not None]
    errors = [r for r in rows if r.get("note", "").startswith("ERROR")]
    dq = [_f(r["dockq"]) for r in scored]
    out = {
        "n": len(scored),
        "n_error": len(errors),
        "dockq_mean": round(stats.mean(dq), 3) if dq else "",
        "dockq_median": round(stats.median(dq), 3) if dq else "",
        "pct_acceptable": round(sum(v >= 0.23 for v in dq) / len(dq), 2) if dq else "",
        "pct_medium": round(sum(v >= 0.49 for v in dq) / len(dq), 2) if dq else "",
        "pct_high": round(sum(v >= 0.80 for v in dq) / len(dq), 2) if dq else "",
        "mean_irmsd": round(stats.mean([_f(r["irmsd"]) for r in scored]), 2) if scored else "",
        "mean_fnat": round(stats.mean([_f(r["fnat"]) for r in scored]), 2) if scored else "",
    }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--summary", default=str(RESULTS / "summary.csv"))
    ap.add_argument("--outdir", default=str(RESULTS))
    args = ap.parse_args()

    summary = Path(args.summary)
    if not summary.exists():
        raise SystemExit(f"{summary} not found -- run run_dockq.py first")
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    targets = load_targets()

    def included(pid: str) -> bool:
        t = targets.get(pid)
        return t.include if t else True

    rows = [r for r in read_rows(summary)
           if r.get("rank", "best") == "best" and included(r["pdb_id"])]
    methods = sorted({r["method"] for r in rows})
    tgt_ids = sorted({r["pdb_id"] for r in rows},
                     key=lambda p: (targets[p].tier if p in targets else 9, p))

    # ---- by_method.csv : all included, then ok-only subset -------------------
    bm_fields = ["method", "subset", "n", "n_error", "dockq_mean", "dockq_median",
                 "pct_acceptable", "pct_medium", "pct_high", "mean_irmsd", "mean_fnat"]
    bm_rows = []
    for m in methods:
        mrows = [r for r in rows if r["method"] == m]
        bm_rows.append({"method": m, "subset": "all", **method_stats(mrows)})
        ok = [r for r in mrows if targets.get(r["pdb_id"]) and targets[r["pdb_id"]].quality == "ok"]
        if ok:
            bm_rows.append({"method": m, "subset": "ok-only", **method_stats(ok)})
    with (outdir / "by_method.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=bm_fields)
        w.writeheader()
        w.writerows(bm_rows)

    # ---- by_target.csv : target x method matrix of best DockQ ---------------
    cell = {}
    for r in rows:
        v = _f(r["dockq"])
        cell[(r["pdb_id"], r["method"])] = f"{v:.3f}" if v is not None else (
            "ERR" if r.get("note", "").startswith("ERROR") else "-")
    with (outdir / "by_target.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["pdb_id", "tier", "quality"] + methods)
        for p in tgt_ids:
            t = targets.get(p)
            w.writerow([p, t.tier if t else "", t.quality if t else ""]
                       + [cell.get((p, m), "-") for m in methods])

    # ---- report.md --------------------------------------------------------
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    L = [f"# Benchmark results\n", f"_generated {now} from `results/summary.csv`_\n",
         "## Methods (best pose per target)\n",
         "| method | subset | n | err | DockQ mean | median | ≥acceptable | ≥medium | ≥high | iRMSD | fnat |",
         "|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|"]
    for b in bm_rows:
        L.append("| {method} | {subset} | {n} | {n_error} | {dockq_mean} | {dockq_median} "
                 "| {pct_acceptable} | {pct_medium} | {pct_high} | {mean_irmsd} | {mean_fnat} |".format(**b))

    L += ["\n## Per-target DockQ (best pose)\n",
          "\\* = `caution` target (native peptide only partially resolved).\n",
          "| target | tier | " + " | ".join(methods) + " |",
          "|---|--:|" + "|".join(["--:"] * len(methods)) + "|"]
    for p in tgt_ids:
        t = targets.get(p)
        star = "*" if t and t.quality == "caution" else ""
        L.append(f"| {p}{star} | {t.tier if t else ''} | "
                 + " | ".join(cell.get((p, m), "-") for m in methods) + " |")

    prov = [m for m in methods if m in {"afmultimer"}]
    errs = [f"{r['method']}/{r['pdb_id']}: {r['note']}" for r in rows if r.get("note", "").startswith("ERROR")]
    dropped = [f"{p} ({t.quality}: {t.notes})" for p, t in sorted(targets.items()) if not t.include]
    L.append("\n## Notes\n")
    if prov:
        L.append(f"- **Provisional**: {', '.join(prov)} rows use predictions with "
                 f"unrecorded settings/seed; replace with a fresh, pinned run.")
    if errs:
        L.append("- **DockQ errors** (chain dropped by DockQ — usually a non-standard/D peptide):")
        L += [f"  - {e}" for e in errs]
    L.append(f"- **Excluded from the benchmark** ({len(dropped)}): see `configs/targets.yaml`.")
    L += [f"  - {d}" for d in dropped]

    (outdir / "report.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"wrote {outdir/'by_method.csv'}, {outdir/'by_target.csv'}, {outdir/'report.md'}")
    print(f"methods: {', '.join(methods)}   targets scored: {len(tgt_ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
