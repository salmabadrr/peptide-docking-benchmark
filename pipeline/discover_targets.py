"""Find candidate protein-peptide crystal structures beyond the curated 18.

1. Queries the RCSB search API (full-text "antimicrobial peptide" / "host defense
   peptide" by default, or a supplied ID list) for X-ray entries with >=2 protein
   chains and a resolution cutoff.
2. Skips anything already in configs/targets.yaml (included or dropped).
3. For each remaining candidate: fetches the RCSB FASTA, groups chains into
   entities, and keeps only entries that look like a single receptor + single
   peptide (one long protein entity ~40-2000 aa, one short one ~4-50 aa, no other
   distinct protein/nucleic-acid entities -- the same shape as the curated set).
4. Runs the SAME screen prep_native.py applies to the curated 18: fraction of the
   peptide resolved in the deposited coordinates, and any D-amino-acid / other
   non-standard residue in the peptide chain.
5. Writes a candidate table, best first, for manual review before anything is
   added to targets.yaml -- this script never edits that file.

Output: results/discovery_candidates.csv

Usage:
  python discover_targets.py                          # live RCSB search, ~150 candidates
  python discover_targets.py --limit 300
  python discover_targets.py --pdb-ids 6Q6W 4XYZ ...   # test specific IDs instead of searching
  python discover_targets.py --query "thanatin"        # different full-text term

CPU only. Deps: gemmi, requests, pyyaml. Network: RCSB search + files.rcsb.org.
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

import gemmi
import requests

from config import RESULTS, load_targets
from prep_native import RCSB_ENTRY_CIF, RCSB_FASTA, STANDARD_AA, UA, parse_rcsb_fasta

SEARCH_URL = "https://search.rcsb.org/rcsbsearch/v2/query"

RECEPTOR_LEN = (40, 2000)   # aa range treated as "the protein target"
PEPTIDE_LEN = (4, 50)       # aa range treated as "the bound peptide"


def _get(url: str, tries: int = 2) -> str:
    for i in range(tries):
        r = requests.get(url, headers=UA, timeout=15)
        if r.ok:
            return r.text
        if r.status_code == 404:
            raise FileNotFoundError(url)
        time.sleep(2 * (i + 1))
    r.raise_for_status()
    return ""


def search_rcsb(query_text: str, resolution_max: float, limit: int) -> list[str]:
    payload = {
        "query": {
            "type": "group", "logical_operator": "and",
            "nodes": [
                {"type": "terminal", "service": "full_text", "parameters": {"value": query_text}},
                {"type": "terminal", "service": "text", "parameters": {
                    "attribute": "rcsb_entry_info.polymer_entity_count_protein",
                    "operator": "greater_or_equal", "value": 2}},
                {"type": "terminal", "service": "text", "parameters": {
                    "attribute": "rcsb_entry_info.resolution_combined",
                    "operator": "less_or_equal", "value": resolution_max}},
                {"type": "terminal", "service": "text", "parameters": {
                    "attribute": "exptl.method", "operator": "exact_match", "value": "X-RAY DIFFRACTION"}},
            ],
        },
        "return_type": "entry",
        "request_options": {"paginate": {"start": 0, "rows": limit}},
    }
    r = requests.post(SEARCH_URL, json=payload, timeout=30)
    if r.status_code == 204 or not r.text.strip():
        return []  # RCSB returns an empty 204 body (not JSON) when a term has zero hits
    r.raise_for_status()
    d = r.json()
    return [x["identifier"] for x in d.get("result_set", [])]


def is_proteinish(seq: str) -> bool:
    aa = set("ACDEFGHIKLMNPQRSTVWYX")
    return sum(c in aa for c in seq.upper()) / max(len(seq), 1) > 0.9


def classify(entities: list[tuple[list[str], str]]):
    """-> (receptor_chain, receptor_seq, peptide_chain, peptide_seq) or None."""
    proteinish = [(ids, seq) for ids, seq in entities if seq and is_proteinish(seq)]
    receptors = [(ids, seq) for ids, seq in proteinish if RECEPTOR_LEN[0] <= len(seq) <= RECEPTOR_LEN[1]]
    peptides = [(ids, seq) for ids, seq in proteinish if PEPTIDE_LEN[0] <= len(seq) <= PEPTIDE_LEN[1]]
    # exactly one distinct receptor-sized sequence and one distinct peptide-sized
    # sequence, and nothing else unaccounted for (no third molecule / extra chaperone)
    if len({seq for _, seq in receptors}) != 1 or len({seq for _, seq in peptides}) != 1:
        return None
    if len(proteinish) != len(receptors) + len(peptides):
        return None
    (rec_ids, rec_seq) = receptors[0]
    (pep_ids, pep_seq) = peptides[0]
    return rec_ids[0], rec_seq, pep_ids[0], pep_seq


def audit_candidate(pdb_id: str, rec_chain: str, pep_chain: str, pep_seq: str) -> dict:
    cif = _get(RCSB_ENTRY_CIF.format(pdb_id=pdb_id))
    st = gemmi.make_structure_from_block(gemmi.cif.read_string(cif).sole_block())
    st.setup_entities()
    st.remove_alternative_conformations()
    st.remove_hydrogens()
    st.remove_ligands_and_waters()
    model = st[0]
    names_present = {ch.name for ch in model}
    if pep_chain not in names_present or rec_chain not in names_present:
        return {"resolved_pep_len": 0, "resolved_frac": 0.0, "pep_nonstd": "chain not in coordinates"}
    # a chain name can appear on more than one gemmi Chain object (e.g. a polymer
    # portion plus an empty ligand/water sub-chain sharing the same auth ID) --
    # iterate all of them and accumulate, don't pick just one by name.
    nonstd = set()
    n_resolved = 0
    for ch in model:
        if ch.name != pep_chain:
            continue
        for res in ch.get_polymer():
            info = gemmi.find_tabulated_residue(res.name)
            if info and (info.is_amino_acid() or info.is_nucleic_acid()):
                n_resolved += 1
                if res.name not in STANDARD_AA:
                    nonstd.add(res.name)
    frac = n_resolved / max(len(pep_seq), 1)
    return {"resolved_pep_len": n_resolved, "resolved_frac": round(frac, 2),
            "pep_nonstd": ";".join(sorted(nonstd))}


def verdict_for(resolved_frac: float, pep_nonstd: str) -> str:
    if pep_nonstd:
        return "drop: non-standard/D peptide residues"
    if resolved_frac < 0.5:
        return "drop: peptide mostly disordered"
    if resolved_frac < 0.8:
        return "caution: partial peptide"
    return "ok"


# Well-known AMP family / individual-peptide names -- broader and more precise than
# the single generic phrase "antimicrobial peptide", which mostly returns unrelated
# protease/inhibitor papers that merely mention AMPs in passing.
DEFAULT_QUERIES = [
    "antimicrobial peptide", "host defense peptide", "cathelicidin", "defensin",
    "thanatin", "magainin", "LL-37", "nisin", "protegrin", "indolicidin",
    "pyrrhocoricin", "lactoferricin", "drosocin", "metchnikowin", "bactenecin",
    "temporin", "brevinin", "attacin", "cecropin", "apidaecin", "bombinin",
    "melittin", "dermaseptin", "polymyxin", "bacitracin", "piscidin",
]

FIELDS = ["pdb_id", "matched_query", "receptor_len", "peptide_len_seqres", "peptide_resolved",
          "resolved_frac", "pep_nonstd", "receptor_chain", "peptide_chain", "verdict"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--query", nargs="+", default=DEFAULT_QUERIES,
                    help="one or more full-text search terms (default: a list of known AMP families)")
    ap.add_argument("--resolution-max", type=float, default=2.8)
    ap.add_argument("--limit", type=int, default=200, help="max candidates to fetch PER query term")
    ap.add_argument("--pdb-ids", nargs="+", help="test these IDs instead of searching")
    ap.add_argument("--delay", type=float, default=0.4,
                    help="seconds to sleep between candidates -- be gentle on RCSB, avoid rate-limit stalls")
    ap.add_argument("--out", default=str(RESULTS / "discovery_candidates.csv"))
    ap.add_argument("--no-resume", action="store_true",
                    help="ignore any previous partial run and rescreen everything")
    args = ap.parse_args()

    known = set(load_targets().keys())  # already curated (included or dropped) -- skip
    matched_by: dict[str, list[str]] = {}

    if args.pdb_ids:
        candidates = [x.upper() for x in args.pdb_ids]
        for c in candidates:
            matched_by[c] = ["--pdb-ids"]
    else:
        seen: dict[str, list[str]] = {}
        for q in args.query:
            print(f"searching RCSB: '{q}', <= {args.resolution_max} A, X-ray, "
                 f">=2 protein chains, limit {args.limit} ...")
            for pid in search_rcsb(q, args.resolution_max, args.limit):
                seen.setdefault(pid, []).append(q)
        matched_by = seen
        candidates = list(seen.keys())
    candidates = [c for c in candidates if c not in known]

    # Resume support: write each row to --out as soon as it's found (flushed), and
    # track every screened ID (kept or not) in a sidecar file, so a stall/kill/crash
    # loses at most the one candidate in flight, not the whole run.
    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    screened_path = outp.with_suffix(".screened.txt")
    already_screened: set[str] = set()
    if not args.no_resume and screened_path.exists():
        already_screened = set(screened_path.read_text().split())
        print(f"resuming: {len(already_screened)} candidates already screened in a previous run")
    candidates = [c for c in candidates if c not in already_screened]
    print(f"{len(candidates)} unique candidates to screen across {len(args.query) if not args.pdb_ids else 1} "
         f"query term(s) (already-curated + already-screened IDs excluded)")

    write_header = not (outp.exists() and outp.stat().st_size > 0)
    csv_fh = outp.open("a", newline="", encoding="utf-8")
    writer = csv.DictWriter(csv_fh, fieldnames=FIELDS + ["resolved_pep_len"])
    if write_header:
        writer.writeheader()
    screened_fh = screened_path.open("a", encoding="utf-8")

    n_kept = 0
    for i, pid in enumerate(candidates, 1):
        if i % 10 == 0 or i == len(candidates):
            print(f"... progress {i}/{len(candidates)} ({n_kept} kept so far)")
        try:
            entities = parse_rcsb_fasta(_get(RCSB_FASTA.format(pdb_id=pid)))
            shape = classify(entities)
            if shape is not None:
                rec_chain, rec_seq, pep_chain, pep_seq = shape
                a = audit_candidate(pid, rec_chain, pep_chain, pep_seq)
                v = verdict_for(a["resolved_frac"], a["pep_nonstd"])
                row = {"pdb_id": pid, "matched_query": ";".join(matched_by.get(pid, [])),
                      "receptor_len": len(rec_seq),
                      "peptide_len_seqres": len(pep_seq), "resolved_pep_len": a["resolved_pep_len"],
                      "resolved_frac": a["resolved_frac"], "pep_nonstd": a["pep_nonstd"],
                      "receptor_chain": rec_chain, "peptide_chain": pep_chain, "verdict": v}
                writer.writerow(row)
                csv_fh.flush()
                n_kept += 1
                print(f"[{i}/{len(candidates)}] {pid}: rec {len(rec_seq)}aa pep {len(pep_seq)}aa "
                     f"resolved {a['resolved_frac']:.2f} -> {v}")
            # else: not a simple 1 receptor + 1 peptide protein complex -- not kept
        except Exception as e:  # noqa: BLE001 - one bad candidate shouldn't stop the sweep
            print(f"[{i}/{len(candidates)}] {pid}: skip ({type(e).__name__}: {e})", file=sys.stderr)
        finally:
            screened_fh.write(pid + "\n")
            screened_fh.flush()
            time.sleep(args.delay)

    csv_fh.close()
    screened_fh.close()

    # cosmetic final pass: re-read everything written so far (this run + any earlier
    # resumed runs) and rewrite the file sorted best-first
    with outp.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    order = {"ok": 0, "caution: partial peptide": 1, "drop: non-standard/D peptide residues": 2,
             "drop: peptide mostly disordered": 2}
    rows.sort(key=lambda r: (order.get(r["verdict"], 3), -float(r["resolved_frac"] or 0)))

    with outp.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=[f for f in FIELDS if f != "peptide_resolved"] + ["resolved_pep_len"])
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in w.fieldnames})

    n_ok = sum(1 for r in rows if r["verdict"] == "ok")
    n_caution = sum(1 for r in rows if r["verdict"].startswith("caution"))
    print(f"\nwrote {len(rows)} scored candidates -> {outp}")
    print(f"{n_ok} ok, {n_caution} caution, {len(rows)-n_ok-n_caution} drop")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
