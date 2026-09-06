# InterPepRank — pose re-ranking (Objective 2)

InterPepRank scores a set of docked receptor–peptide structures ("decoys") and
predicts which one is closest to native. We use it to test **Objective 2**: does
its top-scored pose beat each docker's own rank-1 pose?

- Paper: Johansson-Åkhe, Mirabello, Wallner. *InterPepRank: Assessment of Docked
  Peptide Conformations by a Deep Graph Network.* Front. Bioinform. 2021.
  <https://www.frontiersin.org/articles/10.3389/fbinf.2021.763102/full>
- Code: `https://bitbucket.org/isaakh94/interpeprank` (Bitbucket, not GitHub)
- Model: edge-conditioned graph convolution network (Spektral + Keras + TensorFlow).
- Output: a normalised-LRMSD score in **[0, 1], higher = better pose**
  (`LRMSDnorm = 1 / (1 + (LRMSD/4)^2)`). Paper uses a 0.47 cutoff to drop poor decoys.

## What it needs (why this is HPC work, like Boltz-2)

| Requirement | Notes |
|---|---|
| Its own env | ~2020 stack — Spektral 0.x + Keras + TensorFlow. Build a dedicated `conda`/`venv` on **Python 3.7–3.8**; do not mix with the benchmark's `.venv`. |
| Network weights | Bundled in the repo or a separate download — check the repo README after cloning. |
| Node features | one-hot AA + **PSSM + self-entropy** from HHblits 2.0.15 vs `uniclust30_2016_03` (~50 GB). PSSM/entropy are zeroed for peptide residues; the **receptor** needs a real MSA. If the repo ships a reduced/no-MSA mode, note it here. |
| Compute | CPU is fine (paper: ~100 min for 70k decoys; >95 % is graph prep). GPU optional. Our job is tiny (~215 decoys). |

Because of the HHblits database this realistically runs on the university cluster.
Same blocker class as `methods/boltz/`.

## Install (fill in the exact commands once run on the cluster)

```bash
git clone https://bitbucket.org/isaakh94/interpeprank
cd interpeprank
# read its README for: env file / requirements, where the weights go, the exact
# scoring entrypoint (script name + args), and whether it wants one PDB per decoy
# or a Rosetta silent file.
conda env create -f <its-env-file>        # or: python3.8 -m venv + pip install -r requirements.txt
# point it at HHblits + uniclust30_2016_03 (module load hh-suite; set DB path)
```

Record: repo commit hash, TF/Spektral versions, weights file, HHblits DB build, date.

## How it plugs into this benchmark

1. **Make the decoys** (already done — regenerable):
   ```
   python pipeline/rerank_prep.py
   ```
   writes `predictions/<method>/<ID>_rank00..NN.pdb` (rank00 = the docker's own top
   pose; 2 chains, native chain IDs) and `results/rerank_manifest.csv`
   (`method, pdb_id, decoy_rank, src_model, out_pdb`).

2. **Score every decoy with DockQ** (already done):
   ```
   python pipeline/run_dockq.py
   ```
   adds `rank=00..NN` rows to `results/summary.csv`.

3. **Run InterPepRank** on the decoy PDBs. For each ensemble, write its scores to:
   ```
   rerank/<method>/<ID>/interpeprank.csv
   ```
   with columns `decoy_rank,score` — `decoy_rank` matching the manifest (0-based),
   `score` = InterPepRank's [0,1] output (higher = better). A tiny wrapper that
   loops the manifest rows and calls InterPepRank's entrypoint per `out_pdb` is the
   easiest way; put it here as `score_decoys.py` / `run_interpeprank.slurm`.

4. **Evaluate**:
   ```
   python pipeline/rerank_eval.py                    # reranker=interpeprank by default
   python pipeline/rerank_eval.py --score-ascending  # only if score is lower=better
   ```
   writes `results/rerank.csv` + `results/rerank.md` — per (method, target):
   `docker_top1` vs `reranker_top1` vs `oracle` DockQ, Δ vs docker, win/tie/loss,
   and Spearman(score, DockQ) within the ensemble.

## Current status

- Decoys prepped and DockQ-scored: **41 ensembles** (chai ×13, af3 ×10, protenix ×13,
  afmultimer ×4, boltz ×1), 5 poses each.
- `results/rerank.md` currently shows **headroom only** (oracle − docker_top1):
  mean **+0.092 DockQ**, but very uneven — af3 **+0.177**, chai **+0.114**,
  protenix **+0.016**. That headroom is the ceiling InterPepRank has to reach.
- Blocked on: cloning the repo + standing up the env + HHblits DB on the cluster.
