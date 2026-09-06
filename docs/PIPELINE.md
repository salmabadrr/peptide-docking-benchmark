# Benchmark pipeline (CPU / no-GPU track)

Everything here runs on a normal laptop (GraphPep re-ranking runs under WSL, still
CPU). GPU/cluster work (Boltz-2 full run, InterPepRank, DiffPepDock) is not covered
by this doc — see `methods/<tool>/README.md`.

**Target set:** 13 of the 30 entries in `configs/targets.yaml` are `include: true`
(8 `ok`; 5 `caution` — partial peptide, report with an asterisk: 6Z2P, 4JWC, 4EZQ,
4EZO, 3QRX). 17 were dropped; the DROPPED section of `configs/targets.yaml` and
`data/natives/_audit.csv` give the exact reason per target:

- **(A) peptide mostly disordered** (<50% resolved) — 6Z2Q, 8GQA, 3QNJ, 4JWE, 8ITG, 6Y0X;
- **(B) D-amino-acid / non-standard peptide** — sequence-only predictors build only
  the L-enantiomer — 6Q6W, 6Q77, 6Q85, 6Q86, 6Y0W (LecB D-peptides), 8ONU (DAB/HYP);
- **(C) unencodable `X` in SEQRES** — 4JWI, 7NEF;
- **(D) not a genuine AMP** (checked against the entry's citation) — 2HD4, 4N6P;
- **(E) resolved peptide fragment not in contact with the receptor** — 4JWD
  (7/14 modelled, ~6 Å from the receptor → DockQ finds no interface).

`run_dockq.py`, `report.py` and `aggregate.py` skip `include: false` targets by
default (pass `--only <ID>` or `--include-dropped` to force one through).

**Out of scope here:** PepNN-Struct (binding-site predictor, not a complex).

```
configs/targets.yaml                     30 entries, 13 included (source of truth)
        │  pipeline/prep_native.py
data/sequences/<ID>_{receptor,peptide,complex}.fasta      construct sequences
data/natives/<ID>_native.pdb                              1 receptor + 1 peptide, cleaned
        │  pipeline/make_inputs.py
inputs/{afmultimer,af3_server,chai,boltz,colabfold}/<ID>.*   one input file per method
        │  run each predictor -> predictions/_raw/<method>/
        │  pipeline/collect_predictions.py
predictions/<method>/<ID>.pdb            top pose, 2 chains, native IDs
results/confidences.csv                  each tool's own confidence
        │  pipeline/run_dockq.py
results/summary.csv                      one row per (method, target[, rank])
        │  pipeline/report.py
results/REPORT.md                        DockQ x confidence x peptide metadata

  Objective 2 (pose re-ranking) — same inputs, branches after collect_predictions:
        │  pipeline/rerank_prep.py           explode 5 models -> <ID>_rankNN.pdb
        │  pipeline/run_dockq.py             per-pose DockQ (rank=00..NN)
        │  pipeline/graphpep_prep.py         -> rerank/graphpep/<m>/<ID>/{protein,decoys}.pdb
        │  methods/graphpep/score_all.sh     (WSL) -> rerank/graphpep/<m>/<ID>/graphpep.csv
        │  pipeline/rerank_eval.py --reranker graphpep --score-ascending
results/rerank.md / rerank.csv           docker top-1 vs re-ranker top-1 vs oracle
```

## Setup

```bash
cd peptide-docking-benchmark
python -m venv .venv
.venv/Scripts/pip install -r pipeline/requirements.txt      # Windows
# source .venv/bin/activate; pip install -r pipeline/requirements.txt   # Linux/mac
```

## Run (tier 1 first: 6HY2, 6Q6W, 6Q77, 4EZS)

```bash
cd pipeline
python prep_native.py --tier 1
python make_inputs.py --tier 1
# ... produce predictions (see below) ...
python ingest.py  --method colabfold --src ../predictions/_raw/colabfold --tier 1
python run_dockq.py --method colabfold
```

Add `--tier 2`, then `--tier 3` (multi-chain: check each `notes:` in targets.yaml and
pass `--source assembly` to `prep_native.py` where the biological receptor is a
crystal-symmetry dimer). Dropped targets are skipped automatically; use
`--only <ID>` or `make_inputs.py --include-dropped` to force one.

## Which tools this covers

| Tool | Objective | How to run | GPU |
|------|-----------|-----------|-----|
| AlphaFold2-Multimer (ColabFold) | 1 – structure | `run_colabfold.sh` on HPC / Linux+internet (CPU ok, slow) | no* |
| AlphaFold 3 (AlphaFold Server) | 1 – structure | **manual** upload `inputs/af3_server/*.json`, download job, `ingest.py --method af3` | no (Google's GPU) |
| Chai-1 | 1 – structure | web upload `inputs/chai/*.fasta`, or headless on a GPU box | no via web |
| Protenix | 1 – structure | web (protenix-server.com), or headless on a GPU box | no via web |
| DockQ | evaluation | `run_dockq.py` | no |

\* ColabFold has no GPU *requirement* for these small complexes but needs Linux (JAX).

## Objective 2 — pose re-ranking

`GraphPep` and `InterPepRank` are **scoring / re-ranking** functions, not structure
generators. We do not wait for DiffPepDock: each Objective-1 method already emits 5
ranked models per target, and that is the decoy set we re-rank. Question: does the
re-ranker's top-scored pose beat the docker's own rank 1 (and how close to the
oracle best-of-5)?

```bash
cd pipeline
python rerank_prep.py                     # predictions/<m>/<ID>_rankNN.pdb + rerank_manifest.csv
python run_dockq.py                        # per-pose DockQ -> summary.csv (rank=00..NN)
python graphpep_prep.py                    # rerank/graphpep/<m>/<ID>/{protein,decoys}.pdb
# in WSL, with the GraphPep env (see methods/graphpep/README.md):
bash ../methods/graphpep/score_all.sh
python rerank_eval.py --reranker graphpep --score-ascending   # -> results/rerank.md
```

GraphPep has been run on all 41 ensembles (`results/rerank.md`,
`docs/RESULTS_DRAFT.md` §6). InterPepRank uses the same `rerank_eval.py` once its
score files exist (`methods/interpeprank/`), but its environment + HHblits database
are cluster-blocked. DiffPepDock (`methods/diffpepdock/`) is a separate,
multi-GPU-cluster job and is not required for the analysis above.

### Not in this pipeline — category mismatch

* **PepNN-Struct** predicts peptide **binding-site residues**, not a full complex →
  can't be scored by DockQ. If kept, evaluate with residue-level precision / recall /
  AUROC against the native interface, separately.

## Reproducibility notes to record per run

* ColabFold: version (in `RUN_INFO.txt`), `alphafold2_multimer_v3`, `--num-models 5`,
  `--random-seed 1`, MSA = ColabFold MMseqs2 server + date.
* AlphaFold Server: `modelSeeds:[1]` (in the JSON), submission date, server version shown on the result page.
* DockQ: v2, explicit `--mapping`, standard thresholds (CAPRI classes:
  incorrect <0.23, acceptable 0.23–0.49, medium 0.49–0.80, high ≥0.80).
  `--capri-peptide` is available but the DockQ authors flag it as unreliable — report standard DockQ as primary.
