# What to dock — quick reference

Scored benchmark set: **6 protein–AMP complexes** (after the data-quality screen).
Every method is run on the **same 6**.

## The 6 targets

| PDB | Receptor protein | Antimicrobial peptide | Peptide sequence (native) | Quality |
|-----|------------------|-----------------------|---------------------------|---------|
| 6HY2 | LpxA — UDP-GlcNAc *O*-acyltransferase (*E. coli*) | peptide inhibitor (12 aa) | `WMLDPIAGKWSR` | ok |
| 4EZS | DnaK — Hsp70 chaperone (*E. coli*) | Metchnikowin (*Drosophila*) | `PRPGPIYY` (8 aa modelled) | ok |
| 8GAL | LptA — LPS transport (*E. coli*) | Thanatin (*Murgantia histrionica*) | `GSKPVPIIACNRKTGKCRRI` (18/20) | ok |
| 6Z2P | O-glycan protease (*Akkermansia muciniphila*) | Glycodrosocin | `GKPRPYSPRPTSHPRPIRV` (10/19) | caution* |
| 4JWC | DnaK — Hsp70 chaperone (*E. coli*) | Cathelicidin-3 / Bac7-type (*Bos taurus*) | `RRIRPRPPRLPRPRPR` (9/16) | caution* |
| 4JWD | DnaK — Hsp70 chaperone (*E. coli*) | Cathelicidin-3 fragment (*Bos taurus*) | `PRPLPFPRPGPRPI` (7/14) | caution* |

\* caution = only part of the peptide is resolved in the crystal; report these DockQ
scores with an asterisk. `ok` = ≥80 % of the peptide resolved.

Notes: DnaK is the receptor in 3 of the 6 (4EZS, 4JWC, 4JWD) — different AMPs each
time, but keep the receptor imbalance in mind when averaging. Inputs for all 6 are
already generated under `inputs/` and `data/sequences/<ID>_complex.fasta`.

## Which tool runs where

| Tool | What it is | Where to run | Input to upload | Status |
|------|-----------|--------------|-----------------|--------|
| **AlphaFold-Multimer** | AlphaFold2 for complexes | **Web — COSMIC²** (`cosmic2.sdsc.edu`), login | `data/sequences/<ID>_complex.fasta` | ready to submit |
| **AlphaFold 3** | latest AlphaFold | **Web — AlphaFold Server** (`alphafoldserver.com`), Google login | `inputs/af3_server/_ALL.json` (all 6 at once) | ready to submit |
| **Chai-1** | open AF3-class model | **Web — Chai-1 server** (`lab.chaidiscovery.com`) | `inputs/chai/<ID>.fasta` | ready to submit |
| **Protenix** | ByteDance AF3 reproduction | **Web — Protenix server** (`protenix-server.com`) | `data/sequences/<ID>_complex.fasta` | ready to submit |
| **Boltz-2** | open biomolecular model | **HPC** (GPU batch job) | `inputs/boltz/<ID>.yaml` | blocked — need cluster scheduler + env |
| DiffPepDock | peptide docking (diffusion) | HPC (GPU) | — | deferred (Objective 2) |
| InterPepRank / GraphPep | pose re-ranking, not prediction | — | — | deferred (Objective 2) |

## Workflow per method

1. Submit the 6 jobs on the web portal (or the HPC batch job for Boltz-2).
2. Download the results into `predictions/_raw/<method>/`.
3. Hand off — the rest is automated:
   `python pipeline/ingest.py --method <m> --src predictions/_raw/<m>`
   `python pipeline/run_dockq.py --method <m>`
   `python pipeline/aggregate.py`  →  `results/report.md`

Record for each run: tool/version, seed, submission date (reproducibility).
