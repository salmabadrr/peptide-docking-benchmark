# Benchmark results

_generated 2026-09-03 19:25 UTC from `results/summary.csv`_

## Methods (best pose per target)

| method | subset | n | err | DockQ mean | median | ≥acceptable | ≥medium | ≥high | iRMSD | fnat |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| afmultimer | all | 3 | 2 | 0.466 | 0.48 | 0.67 | 0.33 | 0.0 | 3.95 | 0.48 |
| afmultimer | ok-only | 2 | 2 | 0.613 | 0.613 | 1.0 | 0.5 | 0.0 | 3.47 | 0.64 |

## Per-target DockQ (best pose)

\* = `caution` target (native peptide only partially resolved).

| target | tier | afmultimer |
|---|--:|--:|
| 6Q77 | 1 | ERR |
| 6Z2P* | 2 | 0.171 |
| 8ONU | 2 | 0.480 |
| 6Q86 | 3 | ERR |
| 8GAL | 3 | 0.746 |

## Notes

- **Provisional**: afmultimer rows use predictions with unrecorded settings/seed; replace with a fresh, pinned run.
- **DockQ errors** (chain dropped by DockQ — usually a non-standard/D peptide):
  - afmultimer/6Q77: ERROR RuntimeError: DockQ produced no JSON (KeyError: 'B')
  - afmultimer/6Q86: ERROR RuntimeError: DockQ produced no JSON (KeyError: 'C')
- **Excluded from the benchmark** (6): see `configs/targets.yaml`.
  - 3QNJ (drop: Oncocin (Pro-rich AMP) in the DnaK substrate channel; only 8/19 residues ordered.)
  - 4JWE (drop: Same system as 4JWC/4JWD; only 43% of this peptide variant ordered.)
  - 6Y0X (drop: 5 receptor chains, 3 peptide copies, flagged cyclic in AMPs.xlsx, only 5/12 ordered. Multiple disqualifiers.)
  - 6Z2Q (drop: Only 2 of 19 peptide residues (TS) modelled. No usable interface.)
  - 8GQA (drop: MslA RiPP precursor analog, 4 Cys — likely macrocyclic. Only 9/20 residues ordered.)
  - 8ITG (drop: 42-mer mini-protein; only 7 residues modelled. Outside the peptide-docking regime anyway.)
