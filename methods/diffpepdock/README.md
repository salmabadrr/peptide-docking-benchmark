# DiffPepDock — peptide docking (Objective 2 prerequisite)

DiffPepDock is a diffusion-based blind peptide–protein docking method. In this
benchmark it is the **decoy generator for Objective 2**: it produces a large,
conformationally diverse ensemble of poses per target, which the re-rankers
(GraphPep, InterPepRank) then score. The Objective-2 analysis currently runs on
each Objective-1 method's own 5-model output (`pipeline/rerank_prep.py`), so
DiffPepDock is **not on the critical path** — it would widen the decoy pool and
give the re-rankers a harder, more realistic ranking task.

## Status: blocked on university-cluster access

| Need | Detail |
|---|---|
| Compute | multi-GPU node; the reference pipeline uses `torchrun` across GPUs |
| Environment | its own conda env (diffusion model + ESM); vendored helper files from earlier prototyping are in the repo root (`process_batch_dock.py`, `preprocess_utils.py`) |
| Input | receptor PDB + peptide sequence (per target); one job per `configs/targets.yaml` include |
| Output | N docked poses per target → `predictions/_raw/diffpepdock/<ID>/` |

## How it will plug in

1. Run DiffPepDock on the cluster → `predictions/_raw/diffpepdock/<ID>/` (N poses).
2. `pipeline/rerank_prep.py --method diffpepdock` (add a lister) →
   `predictions/diffpepdock/<ID>_rankNN.pdb`.
3. `pipeline/run_dockq.py` → per-pose DockQ.
4. `pipeline/graphpep_prep.py` / InterPepRank feature prep → re-ranker scores.
5. `pipeline/rerank_eval.py --reranker <graphpep|interpeprank>` — same as for the
   AF-style ensembles, now over the DiffPepDock pool.

Blocked alongside **Boltz-2** (full run) and **InterPepRank** — all three are
waiting on cluster access.
