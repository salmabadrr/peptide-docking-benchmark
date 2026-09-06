"""Turn our per-decoy PDBs into GraphPep's expected input pair, per ensemble.

GraphPep scores many peptide poses against ONE fixed receptor:
    protein.pdb   receptor only (one model)
    decoys.pdb    peptide only, multi-MODEL (one MODEL per pose, identical topology)

Our predictions/<method>/<ID>_rankNN.pdb each hold a whole complex whose receptor
drifts pose-to-pose, so for every ensemble this:
  1. takes rank00's receptor as the reference frame + protein.pdb,
  2. superposes each rankNN receptor onto it (matched CA atoms) and applies that
     same transform to that pose's peptide,
  3. writes the transformed peptides as decoys.pdb (MODEL 1..N == decoy_rank 0..N-1).

Output: rerank/graphpep/<method>/<ID>/{protein.pdb,decoys.pdb}
Then run methods/graphpep/score_all.sh (loops GraphPep.sh over these) and
pipeline/rerank_eval.py --reranker graphpep --score-ascending.

CPU only. Deps: gemmi, pyyaml.
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import gemmi

from config import PREDICTIONS, RESULTS, load_targets
from ingest import load_any

OUT = RESULTS.parent / "rerank" / "graphpep"


def ca_positions(chain: gemmi.Chain) -> dict:
    out = {}
    for res in chain:
        a = res.find_atom("CA", "*")
        if a is not None:
            out[(res.seqid.num, res.seqid.icode)] = a.pos
    return out


def one_chain_model(st: gemmi.Structure, chain_id: str, model_num: int) -> gemmi.Model | None:
    m = st[0]
    if not any(c.name == chain_id for c in m):
        return None
    for cname in [c.name for c in m if c.name != chain_id]:
        m.remove_chain(cname)
    m.num = model_num
    return m


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="+", metavar="PDBID")
    ap.add_argument("--methods", nargs="+")
    args = ap.parse_args()

    targets = load_targets()
    want = {x.upper() for x in args.only} if args.only else None

    # gather rank files
    groups: dict[tuple[str, str], list[Path]] = defaultdict(list)
    for mdir in sorted(p for p in PREDICTIONS.iterdir() if p.is_dir() and not p.name.startswith("_")):
        if args.methods and mdir.name not in args.methods:
            continue
        for f in sorted(mdir.glob("*_rank[0-9][0-9].pdb")):
            pid = f.name.split("_rank")[0].upper()
            groups[(mdir.name, pid)].append(f)

    n_ok, rc = 0, 0
    for (method, pid), files in sorted(groups.items()):
        if want and pid not in want:
            continue
        if pid not in targets or not targets[pid].include or len(files) < 2:
            continue
        t = targets[pid]
        rec_id, pep_id = t.native_receptor[0], t.native_peptide[0]
        files = sorted(files, key=lambda p: int(p.name.split("_rank")[1][:2]))

        ref = load_any(files[0])
        ref_rec = next((c for c in ref[0] if c.name == rec_id), None)
        if ref_rec is None:
            print(f"{method}/{pid}: no receptor chain {rec_id} in {files[0].name}", file=sys.stderr)
            rc = 1
            continue
        ref_ca = ca_positions(ref_rec)

        odir = OUT / method / pid
        odir.mkdir(parents=True, exist_ok=True)

        # protein.pdb = reference receptor only
        prot = load_any(files[0])
        one_chain_model(prot, rec_id, 1)
        prot.write_pdb(str(odir / "protein.pdb"))

        decoys = gemmi.Structure()
        decoys.name = f"{method}_{pid}_decoys"
        n_used = 0
        for i, fp in enumerate(files):
            st = load_any(fp)
            rec = next((c for c in st[0] if c.name == rec_id), None)
            pep = next((c for c in st[0] if c.name == pep_id), None)
            if rec is None or pep is None:
                print(f"{method}/{pid} rank{i:02d}: missing chain(s), skipped", file=sys.stderr)
                continue
            if i > 0:
                cur = ca_positions(rec)
                fixed, moving = [], []
                for k, p in ref_ca.items():
                    if k in cur:
                        fixed.append(p)
                        moving.append(cur[k])
                if len(fixed) >= 3:
                    sup = gemmi.superpose_positions(fixed, moving)
                    T = sup.transform
                    for c in st[0]:
                        for res in c:
                            for a in res:
                                a.pos = gemmi.Position(T.apply(a.pos))
                else:
                    print(f"{method}/{pid} rank{i:02d}: only {len(fixed)} CA matches, "
                          "left un-superposed", file=sys.stderr)
            m = one_chain_model(st, pep_id, n_used + 1)
            if m is None:
                continue
            decoys.add_model(m)
            n_used += 1

        if n_used < 2:
            print(f"{method}/{pid}: only {n_used} usable pose(s)", file=sys.stderr)
            rc = 1
            continue
        decoys.write_pdb(str(odir / "decoys.pdb"))
        print(f"{method:11s} {pid}: protein.pdb + decoys.pdb ({n_used} models) -> "
              f"rerank/graphpep/{method}/{pid}/")
        n_ok += 1

    print(f"\n{n_ok} ensembles prepped under {OUT}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
