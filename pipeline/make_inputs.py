"""Generate per-method input files from the frozen target list + prepared sequences.

Reads data/sequences/<ID>_{receptor,peptide}.fasta (produced by prep_native.py) and
writes ready-to-run / ready-to-paste inputs under inputs/<method>/.

Methods:
  colabfold   inputs/colabfold/<ID>.fasta        one record, chains joined by ':'  (colabfold_batch)
  boltz       inputs/boltz/<ID>.yaml             Boltz-1/2 YAML  (boltz predict --use_msa_server)
  chai        inputs/chai/<ID>.fasta             Chai-1 fasta    (chai fold / web upload)
  af3_server  inputs/af3_server/<ID>.json        AlphaFold Server dialect  (manual web upload)
              inputs/af3_server/_ALL.json        every included target in one array (bulk upload)

colabfold/boltz/chai inputs can be run headless; af3_server is a manual upload
(the server has login + terms acceptance and no automation API).

CPU only. Deps: pyyaml.
"""
from __future__ import annotations

import argparse
import json
import sys

from config import INPUTS, SEQUENCES, load_targets, select

SEED = 1  # fixed for reproducibility; record alongside results


def read_seq(pdb_id: str, kind: str) -> str:
    p = SEQUENCES / f"{pdb_id}_{kind}.fasta"
    if not p.exists():
        raise FileNotFoundError(f"{p} missing -- run prep_native.py first")
    return "".join(l.strip() for l in p.read_text().splitlines() if not l.startswith(">"))


def w(path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def colabfold(pdb_id, rec, pep):
    # ColabFold reads chains separated by ':' as a complex.
    w(INPUTS / "colabfold" / f"{pdb_id}.fasta", f">{pdb_id}\n{rec}:{pep}\n")


def chai(pdb_id, rec, pep):
    w(INPUTS / "chai" / f"{pdb_id}.fasta",
      f">protein|name={pdb_id}-receptor\n{rec}\n>protein|name={pdb_id}-peptide\n{pep}\n")


def boltz(pdb_id, rec, pep):
    import yaml
    doc = {
        "version": 1,
        "sequences": [
            {"protein": {"id": "A", "sequence": rec}},
            {"protein": {"id": "B", "sequence": pep}},
        ],
    }
    w(INPUTS / "boltz" / f"{pdb_id}.yaml",
      yaml.safe_dump(doc, sort_keys=False, default_flow_style=False))


def af3_job(pdb_id, rec, pep) -> dict:
    return {
        "name": pdb_id,
        "modelSeeds": [SEED],
        "sequences": [
            {"proteinChain": {"sequence": rec, "count": 1}},
            {"proteinChain": {"sequence": pep, "count": 1}},
        ],
        "dialect": "alphafoldserver",
        "version": 1,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="+", metavar="PDBID")
    ap.add_argument("--tier", nargs="+", type=int)
    ap.add_argument("--methods", nargs="+",
                    default=["colabfold", "boltz", "chai", "af3_server"],
                    choices=["colabfold", "boltz", "chai", "af3_server"])
    ap.add_argument("--include-dropped", action="store_true",
                    help="also emit inputs for quality:drop / include:false targets")
    args = ap.parse_args()

    targets = select(load_targets(), args.only, args.tier, included_only=not args.include_dropped)
    if not targets:
        print("no targets matched", file=sys.stderr)
        return 2

    af3_all = []
    for t in targets:
        rec, pep = read_seq(t.pdb_id, "receptor"), read_seq(t.pdb_id, "peptide")
        if "colabfold" in args.methods:
            colabfold(t.pdb_id, rec, pep)
        if "chai" in args.methods:
            chai(t.pdb_id, rec, pep)
        if "boltz" in args.methods:
            boltz(t.pdb_id, rec, pep)
        if "af3_server" in args.methods:
            job = af3_job(t.pdb_id, rec, pep)
            w(INPUTS / "af3_server" / f"{t.pdb_id}.json", json.dumps([job], indent=2))
            af3_all.append(job)
        print(f"{t.pdb_id} [{t.quality}]: rec {len(rec)}aa  pep {len(pep)}aa  -> {', '.join(args.methods)}")

    if af3_all:
        w(INPUTS / "af3_server" / "_ALL.json", json.dumps(af3_all, indent=2))
        print(f"\naf3_server/_ALL.json: {len(af3_all)} jobs "
              f"(AlphaFold Server caps bulk uploads ~20-30/day -- split if needed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
