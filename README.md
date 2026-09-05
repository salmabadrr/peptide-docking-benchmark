# EPIC-AMP — Protein–Peptide Docking Benchmark

A reproducible benchmark comparing computational tools for predicting how an
antimicrobial peptide (AMP) binds its target protein, scored against real crystal
structures with **DockQ**. Built in support of the **EPIC-AMP** project
(computational analysis of AMPs and their properties).

## Objectives

**1. Structure prediction accuracy** (current focus) — how well each method
reproduces a known protein–peptide complex.

![Objective 1: structure prediction vs. crystal structure](<vis 1.png>)

**2. Pose re-ranking** (deferred — needs DiffPepDock ensembles first) — whether
InterPepRank picks a better pose than a docking method's own top-ranked one.

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
| DiffPepDock | 2 (prerequisite) | HPC (GPU) | deferred |
| InterPepRank, GraphPep | 2 | — | deferred |
| PepNN-Struct | — | — | shelved (predicts binding sites, not a complex) |

## Pipeline

```text
configs/targets.yaml           frozen target list (source of truth)
        │  pipeline/prep_native.py
data/sequences/, data/natives/  sequences + cleaned native reference + quality audit
        │  pipeline/make_inputs.py
inputs/<method>/<ID>.*          ready-to-submit predictor inputs
        │  (run the external predictor)
predictions/<method>/<ID>.pdb   normalised prediction (pipeline/ingest.py)
        │  pipeline/run_dockq.py
results/summary.csv             one row per (method, target)
        │  pipeline/aggregate.py
results/by_method.csv  results/by_target.csv  results/report.md
```

Full how-to: [`docs/PIPELINE.md`](docs/PIPELINE.md). Web-submission steps:
[`docs/WEB_RUNBOOK.md`](docs/WEB_RUNBOOK.md). Verified tool CLIs:
[`docs/tool_interfaces.md`](docs/tool_interfaces.md).

## Target set

Targets come from `AMP data edited.xlsx`, screened by `pipeline/prep_native.py`
against two disqualifiers: **peptide mostly disordered** in the crystal, or
**D-amino-acid / non-standard peptide residues** (no sequence-only predictor can
represent these). `configs/targets.yaml` records every target's status and reason;
`data/natives/_audit.csv` has the raw numbers. `pipeline/discover_targets.py`
searches RCSB for additional candidates and screens them the same way.

## Repository layout

```text
peptide-docking-benchmark/
├── configs/targets.yaml   frozen target list + quality/native metadata
├── pipeline/              the CPU evaluation pipeline (see Pipeline above)
├── methods/boltz/         Boltz-2 HPC job (prepared, runs once the cluster is known)
├── docs/                  PIPELINE.md, WEB_RUNBOOK.md, tool_interfaces.md
├── data/ inputs/ predictions/ results/    generated (see .gitignore)
└── 6HY2_docking_input/, scripts/, *.py    earlier DiffPepDock/6HY2 prep (historical)
```

## Status

- [x] Target list frozen + data-quality screen (`configs/targets.yaml`, `_audit.csv`)
- [x] Pipeline built: native prep → input generation → ingest → DockQ → aggregation
- [x] Validated end-to-end on real predictions (AF3, AlphaFold-Multimer, Boltz-2, Chai-1, Protenix)
- [ ] Full method coverage across every included target
- [ ] Boltz-2 HPC job (blocked on cluster scheduler/environment details)
- [ ] Expand target set via `discover_targets.py`
- [ ] Objective 2 (DiffPepDock, InterPepRank, GraphPep)
