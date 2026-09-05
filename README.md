# EPIC-AMP
# Protein–Peptide Docking Benchmark

## Overview

This repository contains a reproducible benchmarking framework for evaluating computational methods for protein–peptide structure prediction, docking, and docking-pose selection.

The long-term objective is to systematically compare multiple computational approaches for predicting protein–peptide complexes against experimentally determined crystal structures.

Work is organised in two objectives (see below). **Objective 1** (structure
prediction accuracy) is the current focus; **Objective 2** (pose re-ranking, which
depends on DiffPepDock) is deferred.

The evaluation half of the pipeline is built and runs on CPU (`pipeline/`,
see [`docs/PIPELINE.md`](docs/PIPELINE.md)): frozen target list → native-reference
prep → per-method input generation → prediction ingest → **DockQ** scoring →
aggregation. Predictions themselves are produced with the external tools below.

**Structure predictors (Objective 1)** — run via free web services (no local GPU):

| Method | How it is run | Status |
| --- | --- | --- |
| AlphaFold-Multimer | COSMIC² (`cosmic2.sdsc.edu`), web upload | in progress |
| AlphaFold 3 | AlphaFold Server, web upload | queued |
| Chai-1 | web server | queued |
| Protenix | web server | queued |
| Boltz-2 | university HPC (GPU), batch job | blocked on cluster details |
| DiffPepDock | HPC (GPU) | deferred (Objective 2 prerequisite) |

**Deferred / out of scope for now:** InterPepRank and GraphPep (pose scoring /
re-ranking — Objective 2).

**DockQ** (v2, `pip install DockQ`) is the independent structural metric and is
never used to select or rank predictions.

---

## Research Objectives

The benchmark has two main objectives.

### 1. Compare protein–peptide structure prediction methods

The first objective is to evaluate how accurately different computational methods can reproduce experimentally determined protein–peptide complexes.

For each method, predicted complexes will be compared against experimentally determined crystal structures using DockQ and related structural metrics.

Conceptually:

![alt text](<_- visual selection 7.png>)

The resulting benchmark will allow comparison of the structural accuracy of the different approaches under a standardized evaluation framework.

---

### 2. Evaluate docking-pose ranking with InterPepRank

The second objective is to investigate whether InterPepRank can improve the selection of native-like poses from a docking-generated ensemble.

For the initial experiment, DiffPepDock will generate multiple candidate protein–peptide complexes.

The generated poses will then be evaluated by InterPepRank.

Two predictions will be compared:

1. The original top-ranked DiffPepDock pose.
2. The top-ranked pose selected by InterPepRank.

Both predictions will be evaluated independently against the experimental crystal structure using DockQ.

![alt text](<_- visual selection (10).png>)

This provides a direct assessment of whether InterPepRank selects a more native-like structure from the DiffPepDock-generated ensemble.

---

## Pipeline

```text
configs/targets.yaml          frozen target list (single source of truth)
        │  pipeline/prep_native.py
data/sequences/<ID>_*.fasta    receptor / peptide / complex sequences
data/natives/<ID>_native.pdb   DockQ reference: 1 receptor + 1 peptide, cleaned
data/natives/_audit.csv        per-target quality screen (see below)
        │  pipeline/make_inputs.py
inputs/<method>/<ID>.*         ready-to-submit predictor inputs
        │  (run the external predictor)
predictions/_raw/<method>/…    raw predictor output
        │  pipeline/ingest.py
predictions/<method>/<ID>.pdb  2 chains, renamed to the native chain IDs
        │  pipeline/run_dockq.py   (DockQ <model> <native> --mapping …)
results/summary.csv            one row per (method, target)
results/dockq/<method>/<ID>.json
        │  pipeline/aggregate.py
results/by_method.csv  results/by_target.csv  results/report.md
```

The evaluation stages do not depend on any individual predictor. Full how-to in
[`docs/PIPELINE.md`](docs/PIPELINE.md); web-submission steps in
[`docs/WEB_RUNBOOK.md`](docs/WEB_RUNBOOK.md).

## Target set and data-quality screen

Targets come from `AMP data edited.xlsx`. `pipeline/prep_native.py` screens each
crystal complex and records the verdict in `data/natives/_audit.csv`; a target is
excluded (`include: false` in `configs/targets.yaml`) when its native cannot give a
meaningful DockQ reference:

* **peptide mostly disordered** — < ~50 % of the peptide resolved in the crystal;
* **non-standard / D-amino-acid peptide** — residues a sequence-only predictor
  cannot represent (D-residues, non-proteinogenic residues, `X` in the sequence),
  so an all-L prediction is not comparable to the native.

`configs/targets.yaml` and `data/natives/_audit.csv` are the authoritative list of
what is in and what was cut, and why.

---

## Evaluation Metrics

The primary structural evaluation metric will be **DockQ**.

Additional structural metrics may include:

* DockQ score
* interface RMSD (iRMSD)
* ligand RMSD (LRMSD)
* fraction of native contacts (Fnat)
* F1 score
* clash-related metrics

The evaluation procedure will be kept independent of the prediction and ranking stages.

**DockQ will not be used to select or rank predictions.**

---

## Reproducibility

Benchmark runs should record the target, input structures/sequences, prediction method and tool version, configuration parameters, random seeds where applicable, prediction/ranking scores, DockQ results, and execution environment/logs.
Large generated structures and intermediate outputs should not be committed directly to GitHub unless required.

---

## Repository layout

```text
peptide-docking-benchmark/
├── configs/targets.yaml        frozen target list + per-target quality/native metadata
├── pipeline/                    CPU evaluation pipeline
│   ├── config.py                loads targets.yaml; shared paths; CAPRI bands
│   ├── prep_native.py           build native references + sequences + audit
│   ├── make_inputs.py           targets.yaml + sequences -> per-method inputs
│   ├── ingest.py                raw predictor output -> predictions/<method>/<ID>.pdb
│   ├── run_dockq.py             batch DockQ -> results/summary.csv
│   ├── aggregate.py             summary.csv -> by_method / by_target / report.md
│   ├── run_colabfold.sh         optional local AF2-Multimer (only if a GPU box is available)
│   └── requirements.txt
├── methods/boltz/               Boltz-2 HPC job (prepared; runs when the cluster is known)
├── docs/PIPELINE.md             pipeline how-to
├── docs/WEB_RUNBOOK.md          COSMIC² / AF3 / Chai / Protenix submission steps
├── docs/tool_interfaces.md      verified external-tool CLIs
├── data/  inputs/  predictions/  results/    generated (see .gitignore)
└── 6HY2_docking_input/, scripts/, *.py       earlier DiffPepDock/6HY2 prep (historical)
```

---

## Development Status

### Done

* [x] Frozen 18-target list; data-quality screen → excluded targets recorded in `configs/targets.yaml` + `data/natives/_audit.csv`
* [x] Native reference builder (`prep_native.py`) — sequences + cleaned 1:1 native + audit
* [x] Per-method input generation (`make_inputs.py`)
* [x] Prediction ingest / chain normalisation (`ingest.py`)
* [x] DockQ evaluation (`run_dockq.py`) and results aggregation (`aggregate.py`)
* [x] End-to-end pipeline validated on existing AlphaFold-Multimer predictions

### In progress

* [x] AlphaFold-Multimer — full run via COSMIC²
* [x] AlphaFold 3 (AlphaFold Server), Chai-1, Protenix — web submissions
* [x] Boltz-2 — HPC batch job (blocked on scheduler + environment details)
* [ ] `tests/` for the parsers and aggregation

### Deferred (Objective 2)

* [ ] DiffPepDock adapter and Boltz-2 · InterPepRank adapter · GraphPep · statistical comparison

---

## Project Context

This benchmarking framework is being developed in support of the **EPIC-AMP** project, which focuses on computational analysis of antimicrobial peptides and their properties.

The docking benchmark provides a systematic framework for evaluating the ability of modern computational structure-prediction and docking methods to model peptide–protein interactions.
