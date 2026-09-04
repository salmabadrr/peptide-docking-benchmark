"""Batch-score normalised predictions against the native references with DockQ v2.

For every predictions/<method>/<ID>.pdb it runs:
    DockQ <model> <native> --mapping <rec><pep>:<rec><pep> --json ...
(explicit mapping because ingest.py already renamed chains to the native IDs),
parses the JSON, and appends a row to results/summary.csv. Raw DockQ JSON is
kept under results/dockq/<method>/<ID>.json.

If <ID>_rankNN.pdb files exist (ingest --keep-all-models) every rank is scored and
the rows are tagged rank=NN, so you can later ask whether a re-ranker beats rank 0.

CPU only. Deps: DockQ (pip install DockQ), pyyaml.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

from config import NATIVES, PREDICTIONS, RESULTS, capri_class, load_targets

FIELDS = ["method", "pdb_id", "tier", "quality", "topology", "rank", "dockq", "capri_class",
          "irmsd", "lrmsd", "fnat", "fnonnat", "f1", "clashes",
          "pep_len_model", "pep_len_native", "mapping", "model_file", "native_file", "note"]


def dockq_bin() -> str:
    for name in ("DockQ", "DockQ.exe"):
        if shutil.which(name):
            return name
    # fall back to the venv next to this script
    for c in (Path(sys.executable).parent / "DockQ.exe", Path(sys.executable).parent / "DockQ"):
        if c.exists():
            return str(c)
    sys.exit("DockQ not found on PATH -- pip install DockQ")


def run_one(binexe, model: Path, native: Path, mapping: str, out_json: Path,
            allowed_mismatches: int, capri_peptide: bool) -> dict:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    cmd = [binexe, str(model), str(native), "--mapping", mapping,
           "--json", str(out_json), "--allowed_mismatches", str(allowed_mismatches), "--short"]
    if capri_peptide:
        cmd.append("--capri_peptide")
    p = subprocess.run(cmd, capture_output=True, text=True)
    if not out_json.exists():
        # last stderr line is the useful bit (usually a Bio.PDB KeyError on a chain
        # DockQ dropped -- e.g. an all-non-standard / D-amino-acid peptide)
        tail = next((ln.strip() for ln in reversed(p.stderr.splitlines()) if ln.strip()), "")
        raise RuntimeError(f"DockQ produced no JSON ({tail})")
    data = json.loads(out_json.read_text())
    iface = next(iter(data["best_result"].values()))  # single interface for 1:1 targets
    return {
        "dockq": round(float(data.get("GlobalDockQ", data.get("best_dockq", 0.0))), 4),
        "irmsd": round(float(iface["iRMSD"]), 3),
        "lrmsd": round(float(iface["LRMSD"]), 3),
        "fnat": round(float(iface["fnat"]), 3),
        "fnonnat": round(float(iface["fnonnat"]), 3),
        "f1": round(float(iface["F1"]), 3),
        "clashes": int(iface["clashes"]),
        "pep_len_model": int(iface["len2"]),
        "mapping": data.get("best_mapping_str", mapping),
        "stderr_tail": p.stderr.strip().splitlines()[-1] if p.stderr.strip() else "",
    }


def iter_models(method_dir: Path, pdb_id: str):
    top = method_dir / f"{pdb_id}.pdb"
    if top.exists():
        yield "best", top
    for rp in sorted(method_dir.glob(f"{pdb_id}_rank*.pdb")):
        yield rp.stem.split("_rank")[-1], rp


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--method", nargs="+", help="subdirs of predictions/ to score (default: all)")
    ap.add_argument("--only", nargs="+", metavar="PDBID")
    ap.add_argument("--allowed-mismatches", type=int, default=3)
    ap.add_argument("--capri-peptide", action="store_true",
                    help="also pass --capri_peptide (CAPRI peptide thresholds; see DockQ caveat)")
    ap.add_argument("--out", default=str(RESULTS / "summary.csv"))
    ap.add_argument("--include-dropped", action="store_true",
                    help="also score quality:drop / include:false targets (default: skip)")
    args = ap.parse_args()

    binexe = dockq_bin()
    targets = load_targets()
    want_ids = {x.strip().upper() for x in args.only} if args.only else None

    methods = args.method or sorted(d.name for d in PREDICTIONS.iterdir()
                                    if d.is_dir() and not d.name.startswith("_"))
    if not methods:
        print("no method dirs under predictions/", file=sys.stderr)
        return 2

    rows = []
    for method in methods:
        mdir = PREDICTIONS / method
        for pid, t in sorted(targets.items(), key=lambda kv: (kv[1].tier, kv[0])):
            if want_ids:
                if pid not in want_ids:
                    continue
            elif not t.include and not args.include_dropped:
                continue
            native = NATIVES / f"{pid}_native.pdb"
            if not native.exists():
                continue
            models = list(iter_models(mdir, pid))
            if not models:
                continue
            mapping = f"{t.native_receptor[0]}{t.native_peptide[0]}:{t.native_receptor[0]}{t.native_peptide[0]}"
            for rank, model in models:
                base = {"method": method, "pdb_id": pid, "tier": t.tier, "quality": t.quality,
                        "topology": t.topology, "rank": rank, "pep_len_native": t.peptide_length,
                        "model_file": str(model.relative_to(PREDICTIONS.parent)),
                        "native_file": str(native.relative_to(PREDICTIONS.parent)), "note": ""}
                try:
                    r = run_one(binexe, model, native, mapping,
                                RESULTS / "dockq" / method / f"{pid}{'' if rank=='best' else '_'+rank}.json",
                                args.allowed_mismatches, args.capri_peptide)
                    note = r.pop("stderr_tail", "")
                    base.update(r)
                    base["capri_class"] = capri_class(r["dockq"])
                    if "mismatch" in note.lower():
                        base["note"] = "seq mismatch model/native"
                    print(f"{method:12s} {pid} rank={rank:>4s}  DockQ={r['dockq']:.3f}  "
                          f"({base['capri_class']})  iRMSD={r['irmsd']}  fnat={r['fnat']}")
                except Exception as e:  # noqa: BLE001
                    base.update({k: "" for k in FIELDS if k not in base})
                    base["note"] = f"ERROR {type(e).__name__}: {e}"
                    print(f"{method:12s} {pid} rank={rank}: {base['note']}", file=sys.stderr)
                rows.append(base)

    if not rows:
        print("nothing scored", file=sys.stderr)
        return 1
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=FIELDS)
        wr.writeheader()
        for r in rows:
            wr.writerow({k: r.get(k, "") for k in FIELDS})
    print(f"\nwrote {len(rows)} rows -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
