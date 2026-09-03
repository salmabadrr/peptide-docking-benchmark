"""Normalise raw predictor outputs into predictions/<method>/<ID>.pdb.

Every supported tool emits a 2-chain complex with chain 1 = receptor (first input)
and chain 2 = peptide. This script finds the top-ranked model for each target in a
results directory, keeps those two polymer chains in order, renames them to the
native chain IDs from configs/targets.yaml, and writes a clean PDB that DockQ can
score directly (no --mapping needed for the tier 1/2 1:1 targets).

Method presets (filename globs, best-model rule):
  colabfold  *<ID>*rank_001*.pdb            (ColabFold / colabfold_batch)
  boltz      **/<ID>*model_0.cif            (boltz predict output tree)
  chai       *<ID>*model_idx_0.{cif,pdb}    (chai fold)
  af3        *<ID>*model_0.cif / *sample_0* (AlphaFold Server unzipped job folder)
  protenix   *<ID>*sample_0.cif            (Protenix server)
  generic    *<ID>*.{pdb,cif}  -> first match (use --rank-glob to be explicit)

Examples:
  python ingest.py --method colabfold --src ~/Downloads/colabfold_out
  python ingest.py --method af3 --src ~/Downloads/af3_jobs --keep-all-models
  python ingest.py --method chai --src ./chai_out --only 6HY2

CPU only. Deps: gemmi, pyyaml.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import gemmi

from config import PREDICTIONS, load_targets, select

PRESETS = {
    "colabfold": ["*{id}*rank_001*.pdb", "*{id}*rank_1_*.pdb", "*{id}*_relaxed_rank_001*.pdb"],
    "boltz": ["**/{id}*model_0.cif", "**/{id}*model_0.pdb", "boltz_results_{id}/**/*model_0.cif"],
    "chai": ["*{id}*model_idx_0.cif", "*{id}*model_idx_0.pdb", "*{id}*/pred.model_idx_0.*"],
    "af3": ["*{id}*model_0.cif", "*{id}*sample_0.cif", "*{id}*/*model_0.cif", "*{id}*.cif"],
    "protenix": ["*{id}*sample_0.cif", "*{id}*/*sample_0.cif", "*{id}*rank_1*.cif"],
    "generic": ["*{id}*.pdb", "*{id}*.cif"],
}
RANK_RE = re.compile(r"(?:rank[_-]?|model[_-]?|sample[_-]?|idx[_-]?)(\d+)", re.I)


def rank_key(p: Path) -> tuple:
    m = RANK_RE.search(p.name)
    return (int(m.group(1)) if m else 999, p.name)


def find_models(src: Path, pdb_id: str, method: str, rank_glob: str | None) -> list[Path]:
    globs = [rank_glob] if rank_glob else PRESETS[method]
    hits: list[Path] = []
    for g in globs:
        hits += list(src.glob(g.format(id=pdb_id)))
        hits += list(src.glob(g.format(id=pdb_id.lower())))
    # de-dup, keep files only
    seen, out = set(), []
    for p in sorted(hits, key=rank_key):
        if p.is_file() and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def load_any(path: Path) -> gemmi.Structure:
    st = gemmi.read_structure(str(path))
    st.setup_entities()
    st.remove_alternative_conformations()
    st.remove_hydrogens()
    st.remove_ligands_and_waters()
    return st


def rechain_two(st: gemmi.Structure, rec_id: str, pep_id: str) -> gemmi.Structure:
    model = st[0]
    polymer_chains = []
    for ch in model:
        poly = [r for r in ch.get_polymer()
                if (info := gemmi.find_tabulated_residue(r.name))
                and (info.is_amino_acid() or info.is_nucleic_acid())]
        if poly:
            polymer_chains.append((ch.name, poly))
    if len(polymer_chains) < 2:
        raise ValueError(f"expected >=2 polymer chains, found {len(polymer_chains)}")
    if len(polymer_chains) > 2:
        # keep the two largest (receptor + peptide); warn upstream
        polymer_chains.sort(key=lambda c: -len(c[1]))
        polymer_chains = sorted(polymer_chains[:2], key=lambda c: -len(c[1]))
    # largest = receptor, smallest = peptide
    polymer_chains.sort(key=lambda c: -len(c[1]))
    (_, rec_res), (_, pep_res) = polymer_chains[0], polymer_chains[1]

    out = gemmi.Structure()
    out.name = st.name
    m = gemmi.Model("1")
    for cid, residues in ((rec_id, rec_res), (pep_id, pep_res)):
        nc = gemmi.Chain(cid)
        for r in residues:
            nc.add_residue(r)
        m.add_chain(nc)
    out.add_model(m)
    out.setup_entities()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--method", required=True,
                    choices=list(PRESETS) + ["colabfold", "boltz", "chai", "af3", "protenix"])
    ap.add_argument("--src", required=True, type=Path, help="directory with raw predictor output")
    ap.add_argument("--out-method", help="predictions/<name>/ dir (default: --method value)")
    ap.add_argument("--only", nargs="+", metavar="PDBID")
    ap.add_argument("--tier", nargs="+", type=int)
    ap.add_argument("--rank-glob", help="override filename glob; use {id} for the PDB ID")
    ap.add_argument("--keep-all-models", action="store_true",
                    help="also write <ID>_rankNN.pdb for every model found")
    args = ap.parse_args()

    if not args.src.is_dir():
        print(f"--src {args.src} is not a directory", file=sys.stderr)
        return 2

    out_method = args.out_method or args.method
    out_dir = PREDICTIONS / out_method
    out_dir.mkdir(parents=True, exist_ok=True)
    targets = select(load_targets(), args.only, args.tier)

    rc, n_ok = 0, 0
    for t in targets:
        models = find_models(args.src, t.pdb_id, args.method, args.rank_glob)
        if not models:
            print(f"{t.pdb_id}: no model files in {args.src}", file=sys.stderr)
            continue
        rec_id, pep_id = t.native_receptor[0], t.native_peptide[0]
        try:
            best = rechain_two(load_any(models[0]), rec_id, pep_id)
            best.write_pdb(str(out_dir / f"{t.pdb_id}.pdb"))
            n_ok += 1
            extra = ""
            if args.keep_all_models:
                for i, mp in enumerate(models):
                    s = rechain_two(load_any(mp), rec_id, pep_id)
                    s.write_pdb(str(out_dir / f"{t.pdb_id}_rank{i:02d}.pdb"))
                extra = f"  (+{len(models)} ranked)"
            print(f"{t.pdb_id}: {models[0].name} -> predictions/{out_method}/{t.pdb_id}.pdb{extra}")
        except Exception as e:  # noqa: BLE001
            rc = 1
            print(f"{t.pdb_id}: ERROR {type(e).__name__}: {e}  ({models[0]})", file=sys.stderr)
    print(f"\n{n_ok}/{len(targets)} normalised into predictions/{out_method}/")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
