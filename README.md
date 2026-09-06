# EPIC-AMP — Protein–Peptide Docking Benchmark

A reproducible benchmark comparing computational tools for predicting how an
antimicrobial peptide (AMP) binds its target protein, scored against real crystal
structures with **DockQ**. Built in support of the **EPIC-AMP** project
(computational analysis of AMPs and their properties).

## Objectives

**1. Structure prediction accuracy** (current focus) — how well each method
reproduces a known protein–peptide complex.

![Objective 1: structure prediction vs. crystal structure](<vis 1.png>)

**2. Pose re-ranking** (in progress) — whether an external scoring function
(GraphPep; InterPepRank) picks a better pose than a docking method's own
top-ranked one, run over each docker's own 5-model output. GraphPep has been run
on all ensembles; see [`results/rerank.md`](results/rerank.md),
[`methods/graphpep/`](methods/graphpep/README.md) and
[`docs/RESULTS_DRAFT.md`](docs/RESULTS_DRAFT.md).

![Objective 2: pose re-ranking evaluation](<vis 2.png>)

DockQ is never used to select or rank predictions — only to evaluate them.

## Methods

| Method | Objective | Runs on | Status |
| --- | --- | --- | --- |
| AlphaFold-Multimer | 1 | web — COSMIC² | in progress |
| AlphaFold 3 | 1 | web — AlphaFold Server | in progress |
| Chai-1 | 1 | web | in progress |
| Protenix | 1 | web | in progress |
| Boltz-2 | 1 | university HPC (GPU) | blocked on cluster access |
| GraphPep | 2 | laptop (CPU) / WSL | **done** — run on all 41 ensembles (`results/rerank.md`) |
| InterPepRank | 2 | HPC — own env + HHblits DB | harness ready; blocked on cluster |
| DiffPepDock | 2 (prerequisite) | HPC (multi-GPU) | blocked on cluster |
| PepNN-Struct | — | — | shelved (predicts binding sites, not a complex) |

Blocked on university-cluster access: **Boltz-2**, **InterPepRank**, **DiffPepDock**.

## Pipeline

Every step is a script in `pipeline/`. Steps 1–2 and 4–6 run on a normal laptop
(CPU); step 3 is the external predictors.

| # | Run | What it produces |
| --- | --- | --- |
| 1 | `prep_native.py` | `data/sequences/` (receptor + peptide sequences) and `data/natives/` (crystal structure trimmed to one receptor + one peptide, the DockQ reference), plus `data/natives/_audit.csv` — the quality screen |
| 2 | `make_inputs.py` | `inputs/<method>/<ID>.*` — one ready-to-submit input file per method (FASTA, JSON, or YAML depending on the tool) |
| 3 | *run each predictor* (web or HPC) | download the results into `predictions/_raw/<method>/` |
| 4 | `collect_predictions.py` | `predictions/<method>/<ID>.pdb` — each tool's top pose, converted to a common format; and `results/confidences.csv` — each tool's own confidence scores |
| 5 | `run_dockq.py` | `results/summary.csv` — one DockQ score per (method, target) |
| 6 | `report.py` | `results/REPORT.md` — DockQ scores next to tool confidence, peptide length, and analysis |

`aggregate.py` optionally also writes `results/by_method.csv` and
`results/by_target.csv`.

**Objective 2 (re-ranking).** Run over each docker's own 5-model output:

| # | Run | What it produces |
| --- | --- | --- |
| 1 | `rerank_prep.py` | `predictions/<method>/<ID>_rankNN.pdb` — every pose (rank00 = the docker's own top), + `results/rerank_manifest.csv` |
| 2 | `run_dockq.py` | per-pose DockQ rows in `results/summary.csv` (`rank=00..NN`) |
| 3 | `graphpep_prep.py` | `rerank/graphpep/<method>/<ID>/{protein,decoys}.pdb` — GraphPep's fixed-receptor + multi-model-peptide format |
| 4 | `methods/graphpep/score_all.sh` (WSL) | `rerank/graphpep/<method>/<ID>/graphpep.csv` — GraphPep's per-pose score |
| 5 | `rerank_eval.py --reranker graphpep --score-ascending` | `results/rerank.md` / `rerank.csv` — docker top-1 vs re-ranker top-1 vs oracle |

InterPepRank plugs into the same harness once its scores land
(`rerank_eval.py --reranker interpeprank`); see `methods/interpeprank/`.

More detail: [`docs/PIPELINE.md`](docs/PIPELINE.md) (running the pipeline),
[`docs/WEB_RUNBOOK.md`](docs/WEB_RUNBOOK.md) (submitting to the web servers),
[`docs/tool_interfaces.md`](docs/tool_interfaces.md) (verified tool commands).

## Target set

Targets come from `AMP data edited.xlsx`, screened by `pipeline/prep_native.py`
against two disqualifiers: **peptide mostly disordered** in the crystal, or
**D-amino-acid / non-standard peptide residues** (no sequence-only predictor can
represent these). `configs/targets.yaml` records every target's status and reason;
`data/natives/_audit.csv` has the raw numbers. `pipeline/discover_targets.py`
searches RCSB for additional candidates and screens them the same way.

## Repository layout

| Path | What's in it |
| --- | --- |
| `configs/targets.yaml` | The benchmark's target list — every complex, its status (`ok` / `caution` / `drop`), and why. The single source of truth. |
| `pipeline/` | All the Python scripts (see the Pipeline table above). |
| `methods/` | Per-tool setup/run notes and job scripts that don't fit the shared pipeline: `graphpep/` (done), `interpeprank/` + `diffpepdock/` (blocked on cluster). |
| `docs/` | Guides + write-ups: `PIPELINE.md`, `WEB_RUNBOOK.md`, `tool_interfaces.md`, `RESULTS_DRAFT.md`. |
| `data/` | Generated: target sequences and the trimmed crystal reference structures, plus `_audit.csv`. |
| `inputs/` | Generated: the per-tool input files, one folder per method. |
| `predictions/` | Generated: raw predictor downloads (`_raw/`) and the normalised structures DockQ scores. |
| `results/` | Generated: DockQ scores, tool confidences, and the report. |

Generated folders: the small text outputs (CSVs, sequences, native PDBs) are
committed; bulky raw model files are not (see `.gitignore`).

The root also holds some **historical** files from the earlier DiffPepDock/6HY2
prototyping — `6HY2_docking_input/`, `scripts/`, and a few loose `*.py` — kept for
reference, not used by the current pipeline.

## Status

- [x] Target list frozen + data-quality screen (`configs/targets.yaml`, `_audit.csv`)
- [x] Pipeline built: native prep → inputs → collect/normalise → DockQ → report
- [x] Run end-to-end on real predictions from AF3, AlphaFold-Multimer, Boltz-2, Chai-1, Protenix (see `results/REPORT.md`)
- [ ] Full Objective-1 method coverage across every included target
- [~] Objective 2 (pose re-ranking): harness built and **GraphPep run on all 41 ensembles** (`results/rerank.md`, `docs/RESULTS_DRAFT.md` §6); InterPepRank and DiffPepDock still to run
- [ ] Cluster access needed: Boltz-2 full run, InterPepRank, DiffPepDock
- [ ] Expand target set via `discover_targets.py`
