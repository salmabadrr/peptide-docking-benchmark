"""Batch-normalise every raw predictor download AND pull each tool's own confidence.

Walks predictions/_raw/<method>/<ID>/, for each target:
  1. finds the top-ranked model file (method-specific rule),
  2. normalises it to predictions/<method>/<ID>.pdb (2 chains, renamed to the native
     chain IDs -- same as ingest.py),
  3. reads that model's confidence JSON and writes a row to results/confidences.csv:
       method, pdb_id, model_rank, ptm, iptm, ranking_score, has_clash, model_file

ranking_score is each tool's own headline "is this pose good" number
(AF3/Protenix ranking_score, Chai aggregate_score, AlphaFold-Multimer iptm+ptm).

CPU only. Deps: gemmi, pyyaml.
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
MODEL_N = re.compile(r"model[_.]?(\d+)|sample[_.]?(\d+)|rank[_.]?(\d+)", re.I)


def _n(path: Path) -> int:
    m = MODEL_N.search(path.name)
    return int(next(g for g in m.groups() if g)) if m else 999


def pick_af3(d: Path):
    fs = sorted(d.glob("*model_0.cif")) or sorted(d.glob("*_model_*.cif"), key=_n)
    if not fs:
        return None, None
    conf = next(iter(sorted(d.glob("*summary_confidences_0.json"))
                     or sorted(d.glob("*summary_confidences_*.json"), key=_n)), None)
    return fs[0], conf


def pick_chai(d: Path):
    fs = sorted(d.glob("pred.rank_0.cif")) or sorted(d.glob("pred.rank_*.cif"), key=_n)
    if not fs:
        return None, None
    conf = next(iter(sorted(d.glob("scores.rank_0.json"))
                     or sorted(d.glob("scores.rank_*.json"), key=_n)), None)
    return fs[0], conf


def pick_protenix(d: Path):
    fs = sorted(d.glob("**/*sample_0.cif")) or sorted(d.glob("**/*sample_*.cif"), key=_n)
    if not fs:
        return None, None
    conf = next(iter(sorted(d.glob("**/*summary_confidence_sample_0.json"))
                     or sorted(d.glob("**/*summary_confidence_sample_*.json"), key=_n)), None)
    return fs[0], conf


def pick_afmultimer(d: Path):
    # COSMIC2 flat files named 'output_dir%2F<ID>%2Funrelaxed_model_N_...pdb'
    rank_json = next(iter(d.glob("*ranking_debug.json")), None)
    pdbs = list(d.glob("*unrelaxed_model_*.pdb"))
    if not pdbs:
        return None, rank_json
    if rank_json:
        order = json.loads(rank_json.read_text()).get("order", [])
        if order:
            best_tag = order[0]  # e.g. 'model_3_multimer_v3_pred_0'
            bn = re.search(r"model_(\d+)", best_tag)
            if bn:
                want = f"unrelaxed_model_{bn.group(1)}_"
                for p in pdbs:
                    if want in p.name:
                        return p, rank_json
    return sorted(pdbs, key=_n)[0], rank_json


def pick_boltz(d: Path):
    fs = sorted(d.glob("**/rank_1.cif")) or sorted(d.glob("**/rank_*.cif"), key=_n) \
         or sorted(d.glob("**/*model_0.cif"))
    if not fs:
        return None, None
    # prefer the scores.csv summary table (Neurosnap-style output); fall back to rank_1.json
    conf = next(iter(sorted(d.glob("**/scores.csv"))), None) \
        or next(iter(sorted(d.glob("**/rank_1.json")) or sorted(d.glob("**/rank_*.json"), key=_n)), None)
    return fs[0], conf


PICKERS = {"af3": pick_af3, "chai": pick_chai, "protenix": pick_protenix,
           "afmultimer": pick_afmultimer, "boltz": pick_boltz}


def confidence(method: str, conf_path: Path | None) -> dict:
    out = {"ptm": "", "iptm": "", "ranking_score": "", "has_clash": ""}
    if not conf_path or not conf_path.exists():
        return out
    if conf_path.suffix == ".csv":  # boltz / Neurosnap scores.csv -- first (best) row
        rows = list(csv.DictReader(conf_path.read_text().splitlines()))
        if rows:
            r0 = rows[0]
            out["ptm"] = r0.get("Mean pTM", "")
            out["iptm"] = r0.get("Mean ipTM", r0.get("Protein ipTM", ""))
            out["ranking_score"] = r0.get("Confidence Score", "")
        return out
    d = json.loads(conf_path.read_text())
    if method in ("af3", "protenix"):
        out["ptm"], out["iptm"] = d.get("ptm", ""), d.get("iptm", "")
        out["ranking_score"] = d.get("ranking_score", "")
        out["has_clash"] = d.get("has_clash", "")
    elif method == "chai":
        out["ptm"], out["iptm"] = d.get("ptm", ""), d.get("iptm", "")
        out["ranking_score"] = d.get("aggregate_score", "")
        out["has_clash"] = d.get("has_inter_chain_clashes", "")
    elif method == "afmultimer":
        scores = d.get("iptm+ptm", {})
        order = d.get("order", [])
        out["ranking_score"] = round(scores[order[0]], 4) if order and order[0] in scores else \
            (round(max(scores.values()), 4) if scores else "")
    elif method == "boltz":
        out["ptm"], out["iptm"] = d.get("ptm", ""), d.get("iptm", "")
        out["ranking_score"] = d.get("confidence_score", d.get("aggregate_score", ""))
    for k in ("ptm", "iptm", "ranking_score"):
        if isinstance(out[k], float):
            out[k] = round(out[k], 4)
    return out


FIELDS = ["method", "pdb_id", "model_file", "ptm", "iptm", "ranking_score", "has_clash"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--method", nargs="+", default=sorted(PICKERS))
    ap.add_argument("--only", nargs="+", metavar="PDBID")
    ap.add_argument("--out", default=str(RESULTS / "confidences.csv"))
    args = ap.parse_args()

    targets = load_targets()
    want = {x.upper() for x in args.only} if args.only else None
    rows, rc = [], 0
    for method in args.method:
        mraw = RAW / method
        if not mraw.is_dir():
            continue
        for d in sorted(mraw.iterdir()):
            if not d.is_dir():
                continue
            pid = d.name.upper()
            if want and pid not in want:
                continue
            if pid not in targets:
                print(f"{method}/{d.name}: not in targets.yaml, skipped", file=sys.stderr)
                continue
            model, conf = PICKERS[method](d)
            if not model:
                print(f"{method}/{pid}: no model file found", file=sys.stderr)
                rc = 1
                continue
            t = targets[pid]
            try:
                st = rechain_two(load_any(model), t.native_receptor[0], t.native_peptide[0])
                outdir = PREDICTIONS / method
                outdir.mkdir(parents=True, exist_ok=True)
                st.write_pdb(str(outdir / f"{pid}.pdb"))
            except Exception as e:  # noqa: BLE001
                print(f"{method}/{pid}: normalise ERROR {type(e).__name__}: {e}", file=sys.stderr)
                rc = 1
                continue
            c = confidence(method, conf)
            rows.append({"method": method, "pdb_id": pid,
                        "model_file": str(model.relative_to(RAW.parent.parent)), **c})
            print(f"{method:11s} {pid}: {model.name}  ptm={c['ptm']} iptm={c['iptm']} "
                 f"rank_score={c['ranking_score']}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for r in sorted(rows, key=lambda r: (r["pdb_id"], r["method"])):
            w.writerow({k: r.get(k, "") for k in FIELDS})
    print(f"\n{len(rows)} predictions normalised; confidences -> {out}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
