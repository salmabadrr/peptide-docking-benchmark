# EPIC-AMP
# Protein–Peptide Docking Benchmark

## Overview

This repository contains a reproducible benchmarking framework for evaluating computational methods for protein–peptide structure prediction, docking, and docking-pose selection.

The long-term objective is to systematically compare multiple computational approaches for predicting protein–peptide complexes against experimentally determined crystal structures.

The initial implementation focuses on **DiffPepDock**, which will serve as the first fully automated prediction pipeline. Additional methods will be integrated progressively using a common benchmarking interface.

The planned methods include:

* DiffPepDock
* AlphaFold 3
* Protenix
* PepNN-Struct
* GraphPep
* Boltz-1
* Chai-1
* AlphaFold-Multimer

In addition to structure-generation methods, **InterPepRank** will be evaluated as a docking-pose scoring and ranking method. **DockQ** will be used as an independent structural evaluation metric.

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

```text
  c:\Users\salma\Downloads\_- visual selection (5).png
```

This provides a direct assessment of whether InterPepRank selects a more native-like structure from the DiffPepDock-generated ensemble.

---

## Benchmark Methods

### Structure Generation / Prediction

| Method             | Role                                   | Status                     |
| ------------------ | -------------------------------------- | -------------------------- |
| DiffPepDock        | Peptide docking / structure generation | **Initial implementation** |
| AlphaFold 3        | Complex structure prediction           | Planned                    |
| Protenix           | Complex structure prediction           | Planned                    |
| PepNN-Struct       | Protein–peptide structure prediction   | Planned                    |
| GraphPep           | Protein–peptide structure prediction   | Planned                    |
| Boltz-1            | Biomolecular structure prediction      | Planned                    |
| Chai-1             | Biomolecular structure prediction      | Planned                    |
| AlphaFold-Multimer | Multimeric complex prediction          | Planned                    |

### Pose Ranking

| Method       | Role                                 | Status              |
| ------------ | ------------------------------------ | ------------------- |
| InterPepRank | Protein–peptide pose scoring/ranking | Initial integration |

### Structural Evaluation

| Method | Role                                                       |
| ------ | ---------------------------------------------------------- |
| DockQ  | Independent structural evaluation against native complexes |

---

## Standardized Benchmark Architecture

The framework is designed around a common interface so that each prediction method can be integrated independently.

Each method-specific adapter is responsible for:

1. Preparing the required input.
2. Running the external prediction/docking software.
3. Collecting generated structures.
4. Recording tool-specific scores and metadata.
5. Converting outputs into the benchmark's standardized structure format.

The downstream evaluation pipeline should not depend on the internal implementation of any individual prediction method.

```text
Method-specific adapter
          │
          ▼
Standardized prediction
          │
          ▼
Common evaluation framework
          │
          ├── DockQ
          ├── RMSD metrics
          ├── interface metrics
          └── result aggregation
```

This design allows additional prediction methods to be added without rewriting the benchmarking framework.

---

## Initial Development Strategy

Development will proceed incrementally.

### Phase 1 — DiffPepDock

The first implementation will establish the complete pipeline:

```text
Input target
     ↓
DiffPepDock
     ↓
Multiple predicted poses
     ↓
InterPepRank
     ↓
Pose ranking
     ↓
DockQ
     ↓
Benchmark results
```

The pipeline will first be validated on a small number of targets before being extended to the complete benchmark dataset.

### Phase 2 — Additional Prediction Methods

Once the benchmarking framework is validated using DiffPepDock, additional prediction methods will be integrated individually:

```text
AlphaFold 3
Protenix
PepNN-Struct
GraphPep
Boltz-1
Chai-1
AlphaFold-Multimer
```

Each method will be evaluated using the same benchmark targets and standardized evaluation procedure wherever technically possible.

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

Each benchmark run should preserve:

* target identifier
* input structures and sequences
* prediction method
* tool version
* configuration parameters
* random seed where applicable
* generated model identifiers
* prediction scores
* ranking scores
* DockQ results
* execution logs
* software environment information

Large generated structures and intermediate outputs should not be committed directly to GitHub unless required.

---

## Project Structure

```text
peptide-docking-benchmarking/
│
├── README.md
├── AGENTS.md
├── pyproject.toml
│
├── configs/
│   └── benchmark.yaml
│
├── docs/
│   └── tool_interfaces.md
│
├── src/
│   └── peptide_benchmark/
│       ├── pipeline.py
│       ├── ranking.py
│       ├── evaluation.py
│       ├── results.py
│       │
│       └── methods/
│           ├── diffpepdock.py
│           ├── alphafold3.py
│           ├── protenix.py
│           ├── pepnn_struct.py
│           ├── graphpep.py
│           ├── boltz.py
│           ├── chai.py
│           └── alphafold_multimer.py
│
├── tests/
│
├── data/
│   └── README.md
│
└── results/
    └── README.md
```

---

## Development Status

### Repository Setup

* [x] GitHub repository created
* [x] Initial project repository configured
* [x] Initial benchmarking architecture defined
* [x] DiffPepDock interface inspected

### Current

* [ ] Verify InterPepRank interface
* [ ] Verify DockQ interface
* [ ] Implement DiffPepDock adapter
* [ ] Implement InterPepRank adapter
* [ ] Implement DockQ evaluation
* [ ] Validate complete pipeline on a single target

### Planned

* [ ] Expand to multiple benchmark targets
* [ ] Integrate AlphaFold 3
* [ ] Integrate Protenix
* [ ] Integrate PepNN-Struct
* [ ] Integrate GraphPep
* [ ] Integrate Boltz-1
* [ ] Integrate Chai-1
* [ ] Integrate AlphaFold-Multimer
* [ ] Aggregate benchmark results
* [ ] Statistical comparison of methods
* [ ] Generate benchmark reports and visualizations

---

## Project Context

This benchmarking framework is being developed in support of the **EPIC-AMP** project, which focuses on computational analysis of antimicrobial peptides and their properties.

The docking benchmark provides a systematic framework for evaluating the ability of modern computational structure-prediction and docking methods to model peptide–protein interactions.
