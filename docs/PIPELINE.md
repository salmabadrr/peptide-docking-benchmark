# Benchmark pipeline (CPU / no-GPU track)

Everything here runs on a normal laptop. GPU work (Boltz-2, self-hosted
Chai-1/Protenix, DiffPepDock) stays on the HPC and is not covered by this doc.

**Target set:** 6 of the original 18 are `include: true` in `configs/targets.yaml`
(3 `ok`: 6HY2, 4EZS, 8GAL; 3 `caution` — partial peptide, report with an asterisk:
6Z2P, 4JWC, 4JWD). 12 were dropped, for one of two reasons — see the DROPPED
section of `configs/targets.yaml` and `data/natives/_audit.csv` for the exact
reason per target:

- **peptide mostly disordered** (<50% of the peptide resolved) — 6Z2Q, 8GQA, 3QNJ,
  4JWE, 8ITG, 6Y0X;
- **D-amino-acid / non-standard peptide residues** — a sequence-only predictor can
  only build the L-enantiomer, so these are not comparable by DockQ — 6Q6W, 6Q77,
  6Q85, 6Q86, 6Y0W (D-peptides bound to the same LecB lectin), 8ONU (DAB/HYP + `X`
  in the sequence).

`run_dockq.py` and `aggregate.py` skip `include: false` targets by default (pass
`--only <ID>` or `--include-dropped` to force one through, e.g. for provenance).

**Shelved tools:** PepNN-Struct (binding-site predictor, not a complex) and
GraphPep (a scoring function, needs GPU) are out of scope for now.

```
configs/targets.yaml                     18 targets, frozen (source of truth)
        │
        ▼  pipeline/prep_native.py
data/sequences/<ID>_{receptor,peptide,complex}.fasta      full construct sequences
data/natives/<ID>_native.pdb                              1 receptor + 1 peptide, cleaned
        │
        ▼  pipeline/make_inputs.py
inputs/colabfold/<ID>.fasta      headless   (pipeline/run_colabfold.sh, Linux/HPC)
inputs/boltz/<ID>.yaml           headless   (HPC)
inputs/chai/<ID>.fasta           headless on GPU, or web upload
inputs/af3_server/<ID>.json      MANUAL web upload only (login + terms, no API)
        │
        ▼  run each predictor, collect raw output into predictions/_raw/<method>/
        ▼  pipeline/ingest.py --method <m> --src predictions/_raw/<m>
predictions/<method>/<ID>.pdb    2 chains, renamed to native IDs
        │
        ▼  pipeline/run_dockq.py
results/summary.csv              one row per (method, target[, rank])
results/dockq/<method>/<ID>.json raw DockQ output
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

### Not in this pipeline — category mismatch

* **PepNN-Struct** predicts peptide **binding-site residues**, not a full complex →
  can't be scored by DockQ. If kept, evaluate with residue-level precision / recall /
  AUROC against the native interface, separately.
* **GraphPep** and **InterPepRank** are **scoring / re-ranking** functions, not
  structure generators. They belong to Objective 2 (rank poses from a
  DiffPepDock-style ensemble), which is on hold until DiffPepDock runs.

## Reproducibility notes to record per run

* ColabFold: version (in `RUN_INFO.txt`), `alphafold2_multimer_v3`, `--num-models 5`,
  `--random-seed 1`, MSA = ColabFold MMseqs2 server + date.
* AlphaFold Server: `modelSeeds:[1]` (in the JSON), submission date, server version shown on the result page.
* DockQ: v2, explicit `--mapping`, standard thresholds (CAPRI classes:
  incorrect <0.23, acceptable 0.23–0.49, medium 0.49–0.80, high ≥0.80).
  `--capri-peptide` is available but the DockQ authors flag it as unreliable — report standard DockQ as primary.
