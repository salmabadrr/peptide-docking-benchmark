"""Explode each predictor's multi-model output into per-decoy PDBs for re-ranking.

Objective 2: does an external re-ranker (InterPepRank) pick a better pose than the
docker's own rank-1?  To answer that we need every pose scored, not just the top
one.  For each predictions/_raw/<method>/<ID>/ this writes the N ranked models as

    predictions/<method>/<ID>_rank00.pdb ... <ID>_rankNN.pdb

with rank00 = the predictor's OWN top pose, using the same 2-chain / native-chain-ID
normalisation as collect_predictions.py.  pipeline/run_dockq.py already scores any
<ID>_rankNN.pdb it finds (rows tagged rank=NN), so after this you just run:

    python run_dockq.py --method <method>          # scores best + every rank
    python rerank_eval.py                          # docker-top1 vs oracle vs re-ranker

It also writes results/rerank_manifest.csv:  method, pdb_id, decoy_rank, src_model,
out_pdb  -- decoy_rank is the predictor's own order (0 = best); a re-ranker scores
the out_pdb files and we compare its pick against decoy_rank 0.

CPU only.  Deps: gemmi, pyyaml.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

from config import PREDICTIONS, RESULTS, load_targets
from ingest import load_any, rechain_two

RAW = PREDICTIONS / "_raw"
_TAIL_INT = re.compile(r"(\d+)(?=\D*$)")  # last integer in a filename


def _tail_int(p: Path) -> int:
    m = _TAIL_INT.search(p.stem)
    return int(m.group(1)) if m else 999


def _sorted_by_tail(paths):
    return sorted((p for p in paths if p.is_file()), key=_tail_int)


def list_af3(d: Path):
    return _sorted_by_tail(d.glob("*_model_*.cif")) or _sorted_by_tail(d.glob("*model_*.cif"))


def list_chai(d: Path):
    return _sorted_by_tail(d.glob("pred.rank_*.cif"))


def list_protenix(d: Path):
    return _sorted_by_tail(d.glob("**/*_sample_*.cif"))


def list_boltz(d: Path):
    # boltz ranks are 1-based; _sorted_by_tail keeps them in order
    return _sorted_by_tail(d.glob("**/rank_*.cif")) or _sorted_by_tail(d.glob("**/*_model_*.cif"))


def list_afmultimer(d: Path):
    """Order by ranking_debug.json so rank00 = AlphaFold-Multimer's own best."""
    pdbs = list(d.glob("*unrelaxed_model_*.pdb"))
    if not pdbs:
        return []
    by_n = {}
    for p in pdbs:
        m = re.search(r"model_(\d+)", p.name)
        if m:
            by_n[int(m.group(1))] = p
    rj = next(iter(d.glob("*ranking_debug.json")), None)
    if rj:
        try:
            order = json.loads(rj.read_text()).get("order", [])
            out = []
            for tag in order:  # e.g. 'model_3_multimer_v3_pred_0'
                mm = re.search(r"model_(\d+)", tag)
                if mm and int(mm.group(1)) in by_n:
                    out.append(by_n[int(mm.group(1))])
            if out:
                return out
        except (json.JSONDecodeError, OSError):
            pass
    return [by_n[k] for k in sorted(by_n)]


LISTERS = {"af3": list_af3, "chai": list_chai, "protenix": list_protenix,
           "boltz": list_boltz, "afmultimer": list_afmultimer}

MANIFEST_FIELDS = ["method", "pdb_id", "decoy_rank", "src_model", "out_pdb"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--method", nargs="+", default=sorted(LISTERS),
                    choices=sorted(LISTERS))
    ap.add_argument("--only", nargs="+", metavar="PDBID")
    ap.add_argument("--max-decoys", type=int, default=10,
                    help="cap poses kept per ensemble (default 10)")
    ap.add_argument("--manifest", default=str(RESULTS / "rerank_manifest.csv"))
    args = ap.parse_args()

    targets = load_targets()
    want = {x.upper() for x in args.only} if args.only else None
    rows, rc, n_pdb = [], 0, 0

    for method in args.method:
        mraw = RAW / method
        if not mraw.is_dir():
            continue
        out_dir = PREDICTIONS / method
        out_dir.mkdir(parents=True, exist_ok=True)
        for d in sorted(p for p in mraw.iterdir() if p.is_dir()):
            pid = d.name.upper()
            if want and pid not in want:
                continue
            if pid not in targets:
                print(f"{method}/{d.name}: not in targets.yaml, skipped", file=sys.stderr)
                continue
            t = targets[pid]
            models = LISTERS[method](d)[: args.max_decoys]
            if len(models) < 2:
                print(f"{method}/{pid}: {len(models)} model(s) found, need >=2 to re-rank",
                      file=sys.stderr)
                continue
            for i, src in enumerate(models):
                out_pdb = out_dir / f"{pid}_rank{i:02d}.pdb"
                try:
                    st = rechain_two(load_any(src), t.native_receptor[0], t.native_peptide[0])
                    st.write_pdb(str(out_pdb))
                    n_pdb += 1
                except Exception as e:  # noqa: BLE001
                    print(f"{method}/{pid} rank{i:02d}: ERROR {type(e).__name__}: {e}",
                          file=sys.stderr)
                    rc = 1
                    continue
                rows.append({"method": method, "pdb_id": pid, "decoy_rank": i,
                             "src_model": str(src.relative_to(RAW.parent.parent)),
                             "out_pdb": str(out_pdb.relative_to(PREDICTIONS.parent))})
            print(f"{method:11s} {pid}: {len(models)} decoys -> {out_dir.name}/{pid}_rank00..{len(models)-1:02d}.pdb")

    man = Path(args.manifest)
    man.parent.mkdir(parents=True, exist_ok=True)
    with man.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS)
        w.writeheader()
        for r in sorted(rows, key=lambda r: (r["method"], r["pdb_id"], r["decoy_rank"])):
            w.writerow(r)
    print(f"\n{n_pdb} decoy PDBs written; manifest ({len(rows)} rows) -> {man}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
