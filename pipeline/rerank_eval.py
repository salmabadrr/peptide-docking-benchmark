"""Objective 2: does a re-ranker beat each docker's own rank-1 pose?

Inputs
  results/summary.csv        per-decoy DockQ (run rerank_prep.py then run_dockq.py)
  results/rerank_manifest.csv  method,pdb_id,decoy_rank,src_model,out_pdb
  rerank/<method>/<ID>/<reranker>.csv   [optional] the re-ranker's scores, one row
                                        per decoy: a `decoy_rank` column (0-based,
                                        matches the manifest) + a `score` column.
                                        Higher score = better pose (InterPepRank's
                                        normalised-LRMSD output). Pass
                                        --score-ascending if lower = better.

For every (method, target) ensemble it compares three ways of picking one pose:
  docker_top1   the docker's own rank-0 decoy            (baseline)
  reranker_top1 the decoy the re-ranker scores best      (only if score files exist)
  oracle        the best DockQ in the ensemble           (ceiling)

Outputs
  results/rerank.csv   one row per (method, target)
  results/rerank.md    per-method + overall roll-up: mean DockQ per strategy,
                       CAPRI-band counts, re-ranker win/tie/loss vs the docker,
                       mean Spearman(score, DockQ) within an ensemble, and the
                       headroom (oracle - docker_top1) that a perfect re-ranker
                       would capture.

CPU only. stdlib + pyyaml (via config/report).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import statistics as st
import sys
from pathlib import Path

from config import RESULTS, capri_class, load_targets
from report import num, spearman

RERANK_DIR = RESULTS.parent / "rerank"
TIE = 0.02  # DockQ within this -> call it a tie, not a win/loss


def read_csv(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_decoy_dockq() -> dict[tuple[str, str], dict[int, float]]:
    """(method, pdb_id) -> {decoy_rank: dockq} from the numbered rank rows."""
    out: dict[tuple[str, str], dict[int, float]] = {}
    for r in read_csv(RESULTS / "summary.csv"):
        rk = r.get("rank", "")
        if not rk.isdigit():
            continue
        dq = num(r["dockq"])
        if dq is None:
            continue
        out.setdefault((r["method"], r["pdb_id"]), {})[int(rk)] = dq
    return out


def load_scores(method: str, pid: str, reranker: str) -> dict[int, float] | None:
    for cand in (RERANK_DIR / method / pid / f"{reranker}.csv",
                 RERANK_DIR / method / f"{pid}.csv",
                 RERANK_DIR / f"{method}_{pid}_{reranker}.csv"):
        if cand.exists():
            rows = read_csv(cand)
            sc: dict[int, float] = {}
            for row in rows:
                rk = row.get("decoy_rank", row.get("rank", ""))
                s = num(row.get("score", row.get("interpeprank_score", row.get("value", ""))))
                if str(rk).strip().lstrip("-").isdigit() and s is not None:
                    sc[int(rk)] = s
            if sc:
                return sc
    return None


def bands(vals: list[float]) -> str:
    return (f"{sum(v >= 0.23 for v in vals)}/{len(vals)}  "
            f"{sum(v >= 0.49 for v in vals)}/{len(vals)}  "
            f"{sum(v >= 0.80 for v in vals)}/{len(vals)}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reranker", default="interpeprank",
                    help="name of the score files under rerank/ (default: interpeprank)")
    ap.add_argument("--score-ascending", action="store_true",
                    help="re-ranker score where LOWER = better pose")
    ap.add_argument("--only", nargs="+", metavar="PDBID")
    ap.add_argument("--methods", nargs="+")
    args = ap.parse_args()

    targets = load_targets()
    want = {x.upper() for x in args.only} if args.only else None
    decoys = load_decoy_dockq()

    rows = []
    for (method, pid), dqs in sorted(decoys.items()):
        if want and pid not in want:
            continue
        if args.methods and method not in args.methods:
            continue
        if pid not in targets or not targets[pid].include:
            continue
        if 0 not in dqs or len(dqs) < 2:
            continue
        ranks = sorted(dqs)
        docker_top1 = dqs[0]
        oracle = max(dqs.values())
        oracle_rank = min(r for r in ranks if dqs[r] == oracle)

        rec = {"method": method, "pdb_id": pid, "quality": targets[pid].quality,
               "n_decoys": len(dqs), "docker_top1": round(docker_top1, 3),
               "oracle": round(oracle, 3), "oracle_rank": oracle_rank,
               "headroom": round(oracle - docker_top1, 3),
               "reranker_top1": "", "reranker_pick": "", "delta_vs_docker": "",
               "spearman_score_dockq": ""}

        sc = load_scores(method, pid, args.reranker)
        if sc:
            common = [r for r in ranks if r in sc]
            if common:
                sign = 1 if args.score_ascending else -1
                pick = min(common, key=lambda r: sign * sc[r])
                rec["reranker_pick"] = pick
                rec["reranker_top1"] = round(dqs[pick], 3)
                rec["delta_vs_docker"] = round(dqs[pick] - docker_top1, 3)
                rec["spearman_score_dockq"] = spearman([sc[r] for r in common],
                                                       [dqs[r] for r in common])
        rows.append(rec)

    if not rows:
        print("no ensembles to evaluate -- run rerank_prep.py + run_dockq.py first",
              file=sys.stderr)
        return 1

    have_rr = any(r["reranker_top1"] != "" for r in rows)

    # ---- write per-ensemble CSV ----
    fields = ["method", "pdb_id", "quality", "n_decoys", "docker_top1", "oracle",
              "oracle_rank", "headroom", "reranker_pick", "reranker_top1",
              "delta_vs_docker", "spearman_score_dockq"]
    with (RESULTS / "rerank.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    # ---- write markdown ----
    L: list[str] = []

    def emit(s=""):
        L.append(s)

    emit(f"# Re-ranking evaluation — {args.reranker if have_rr else 'headroom only'}")
    emit(f"\n_generated {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M UTC}_\n")
    emit(f"{len(rows)} ensembles (method x target), decoys per ensemble from each "
         "docker's own multi-model output. **docker_top1** = the docker's rank-1 pose; "
         "**oracle** = best DockQ in the ensemble; **reranker_top1** = the pose "
         f"`{args.reranker}` scores best. CAPRI counts shown as ≥acceptable / ≥medium / ≥high.\n")
    if not have_rr:
        emit(f"> No `rerank/<method>/<ID>/{args.reranker}.csv` score files found yet — "
             "showing docker-vs-oracle **headroom** only. Add the re-ranker's scores and "
             "re-run to fill the reranker columns.\n")

    # by method
    emit("## By method\n")
    hdr = "| method | n | docker_top1 mean | oracle mean | headroom |"
    sep = "|---|--:|--:|--:|--:|"
    if have_rr:
        hdr += " reranker_top1 mean | Δ vs docker | win/tie/loss | mean ρ(score,DockQ) |"
        sep += "--:|--:|:--:|--:|"
    emit(hdr); emit(sep)

    def method_block(name, rs):
        d1 = [r["docker_top1"] for r in rs]
        orc = [r["oracle"] for r in rs]
        line = (f"| {name} | {len(rs)} | {st.mean(d1):.3f} | {st.mean(orc):.3f} "
                f"| +{st.mean([o - a for o, a in zip(orc, d1)]):.3f} |")
        if have_rr:
            rr = [(r["reranker_top1"], r["docker_top1"], r["delta_vs_docker"],
                   r["spearman_score_dockq"]) for r in rs if r["reranker_top1"] != ""]
            if rr:
                wins = sum(1 for a, b, _, _ in rr if a - b > TIE)
                loss = sum(1 for a, b, _, _ in rr if b - a > TIE)
                tie = len(rr) - wins - loss
                rhos = [x for _, _, _, x in rr if isinstance(x, (int, float))]
                rr_mean = st.mean([a for a, _, _, _ in rr])
                d_mean = st.mean([d for _, _, d, _ in rr])
                rho_s = f"{st.mean(rhos):.2f}" if rhos else "n/a"
                line += f" {rr_mean:.3f} | {d_mean:+.3f} | {wins}/{tie}/{loss} | {rho_s} |"
            else:
                line += " - | - | - | - |"
        emit(line)

    for m in sorted({r["method"] for r in rows}):
        method_block(m, [r for r in rows if r["method"] == m])
    method_block("**all**", rows)

    # CAPRI-band comparison
    emit("\n## CAPRI bands captured (≥acceptable / ≥medium / ≥high)\n")
    emit("| strategy | count |")
    emit("|---|---|")
    emit(f"| docker_top1 | {bands([r['docker_top1'] for r in rows])} |")
    if have_rr:
        rr_vals = [r["reranker_top1"] for r in rows if r["reranker_top1"] != ""]
        emit(f"| {args.reranker}_top1 | {bands(rr_vals)} |")
    emit(f"| oracle | {bands([r['oracle'] for r in rows])} |")

    # per-ensemble detail
    emit("\n## Per ensemble\n")
    cols = "| method | target | qual | n | docker_top1 | oracle (rank) | headroom |"
    csep = "|---|---|---|--:|--:|--:|--:|"
    if have_rr:
        cols += " reranker pick | reranker_top1 | Δ | ρ |"
        csep += "--:|--:|--:|--:|"
    emit(cols); emit(csep)
    for r in sorted(rows, key=lambda r: (r["method"], -r["headroom"])):
        line = (f"| {r['method']} | {r['pdb_id']} | {r['quality'][:4]} | {r['n_decoys']} "
                f"| {r['docker_top1']:.3f} | {r['oracle']:.3f} (#{r['oracle_rank']}) "
                f"| +{r['headroom']:.3f} |")
        if have_rr:
            if r["reranker_top1"] != "":
                line += (f" #{r['reranker_pick']} | {r['reranker_top1']:.3f} "
                         f"| {r['delta_vs_docker']:+.3f} | {r['spearman_score_dockq']} |")
            else:
                line += " - | - | - | - |"
        emit(line)

    emit("\n---\n")
    emit("- **headroom** = oracle − docker_top1: DockQ a perfect re-ranker would add on "
         "this ensemble. Mean headroom is the upper bound on what InterPepRank can deliver.")
    emit("- **win/tie/loss**: reranker_top1 vs docker_top1, tie = within "
         f"{TIE:.2f} DockQ.")
    emit("- **ρ(score, DockQ)**: Spearman within one ensemble (5 poses) — noisy per row; "
         "read the per-method mean.")
    emit("- 4JWD is excluded (dropped: no native interface). caution targets kept, flagged "
         "in the `qual` column.")

    (RESULTS / "rerank.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {RESULTS / 'rerank.csv'} and {RESULTS / 'rerank.md'}  "
          f"({len(rows)} ensembles, reranker={'yes' if have_rr else 'pending'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
