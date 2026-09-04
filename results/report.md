# Benchmark results

_generated 2026-09-04 23:32 UTC from `results/summary.csv`_

## Methods (best pose per target)

| method | subset | n | err | DockQ mean | median | ≥acceptable | ≥medium | ≥high | iRMSD | fnat |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| af3 | all | 2 | 0 | 0.288 | 0.288 | 1.0 | 0.0 | 0.0 | 3.14 | 0.15 |
| af3 | ok-only | 2 | 0 | 0.288 | 0.288 | 1.0 | 0.0 | 0.0 | 3.14 | 0.15 |
| afmultimer | all | 2 | 0 | 0.458 | 0.458 | 0.5 | 0.5 | 0.0 | 2.88 | 0.49 |
| afmultimer | ok-only | 1 | 0 | 0.746 | 0.746 | 1.0 | 1.0 | 0.0 | 0.88 | 0.81 |
| boltz | all | 1 | 0 | 0.928 | 0.928 | 1.0 | 1.0 | 1.0 | 0.51 | 0.9 |
| boltz | ok-only | 1 | 0 | 0.928 | 0.928 | 1.0 | 1.0 | 1.0 | 0.51 | 0.9 |
| chai | all | 2 | 0 | 0.291 | 0.291 | 0.5 | 0.0 | 0.0 | 3.45 | 0.23 |
| chai | ok-only | 2 | 0 | 0.291 | 0.291 | 0.5 | 0.0 | 0.0 | 3.45 | 0.23 |
| protenix | all | 2 | 0 | 0.805 | 0.805 | 1.0 | 1.0 | 0.5 | 1.06 | 0.83 |
| protenix | ok-only | 2 | 0 | 0.805 | 0.805 | 1.0 | 1.0 | 0.5 | 1.06 | 0.83 |

## Per-target DockQ (best pose)

\* = `caution` target (native peptide only partially resolved).

| target | tier | af3 | afmultimer | boltz | chai | protenix |
|---|--:|--:|--:|--:|--:|--:|
| 4EZS | 1 | 0.287 | - | - | 0.375 | 0.925 |
| 6HY2 | 1 | 0.289 | - | 0.928 | 0.206 | 0.685 |
| 6Z2P* | 2 | - | 0.171 | - | - | - |
| 8GAL | 3 | - | 0.746 | - | - | - |

## Notes

- **Provisional**: afmultimer rows use predictions with unrecorded settings/seed; replace with a fresh, pinned run.
- **Excluded from the benchmark** (12): see `configs/targets.yaml`.
  - 3QNJ (drop: DROP (disordered): Oncocin (Pro-rich AMP) in the DnaK substrate channel; only 8/19 residues ordered.)
  - 4JWE (drop: DROP (disordered): same system as 4JWC/4JWD; only 43% of this peptide variant ordered.)
  - 6Q6W (drop: DROP (D-peptide): receptor = LecB fucose-binding lectin (P. aeruginosa); peptide 'SB5' is a fully D-amino-acid synthetic construct (D-Ala/D-Leu/D-Lys/D-Tyr). Sequence-only predictors can only build the L-enantiomer -- not comparable.)
  - 6Q77 (drop: DROP (D-peptide): same LecB receptor; peptide 'SB12' fully D (LKALKKLA, all D). Crashed DockQ (Bio.PDB drops the all-nonstandard chain -> KeyError) during pipeline validation.)
  - 6Q85 (drop: DROP (D-peptide): same LecB receptor; peptide 'SB11' fully D. Also 4 receptor+peptide copies.)
  - 6Q86 (drop: DROP (D-peptide): same LecB receptor; peptide 'SB4' fully D. Crashed DockQ during pipeline validation (KeyError, same as 6Q77).)
  - 6Y0W (drop: DROP (D-peptide): same LecB receptor; peptide 'cFucRH46D' fully D (7 distinct D-residue types) plus an X in the sequence. Most heavily D-substituted of the set.)
  - 6Y0X (drop: DROP (disordered): 5 receptor chains, 3 peptide copies, flagged 'cyclic' in AMPs.xlsx, only 5/12 ordered. Multiple disqualifiers.)
  - 6Z2Q (drop: DROP (disordered): only 2 of 19 peptide residues (TS) modelled. No usable interface.)
  - 8GQA (drop: DROP (disordered): MslA RiPP precursor analog, 4 Cys -- likely macrocyclic. Only 9/20 residues ordered.)
  - 8ITG (drop: DROP (disordered): 42-mer mini-protein; only 7 residues modelled. Also outside the peptide-docking size regime.)
  - 8ONU (drop: DROP (non-standard residues): receptor = LptA (E. coli); peptide is a Thanatin-like derivative containing DAB (2,4-diaminobutyric acid, non-proteinogenic) and HYP (hydroxyproline). RCSB sequence is 'VPITYXNRATXKCARY' -- literal X characters were being written into every tool's input file.)
