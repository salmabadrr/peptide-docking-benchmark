# GraphPep — pose re-ranking (Objective 2)

GraphPep (Huang lab, HUST; *Nat. Mach. Intell.* 2026) scores protein–peptide
complexes with an interaction-derived graph network + ESM-2 features. We use it to
re-rank each docker's own 5-model ensemble and compare its top pick against the
docker's rank-1 and the oracle best (`pipeline/rerank_eval.py`).

- Code + trained weights: Zenodo `10.5281/zenodo.17099863` (`GraphPep_v1.1.zip`,
  11 MB, GPL-3). Datasets: `10.5281/zenodo.17097750`.
- Score: `bin/core.py` computes `PRED_SCORE = -log(1 + predicted_fnat)`, so
  **more negative = better pose** → `rerank_eval.py --score-ascending`.
- CPU-only is fine (our job: 41 ensembles × 5 poses). No cluster, no MSA database —
  ESM-2 replaces the PSSM step.

## One-time setup (done on this machine, in WSL)

Environment (`~/gp_env`, Python 3.12 venv — the pinned 3.8/torch-2.0 combo in the
package's `environment.yml` also works but isn't required for inference):

```bash
python3 -m venv --without-pip ~/gp_env && . ~/gp_env/bin/activate
curl -sS https://bootstrap.pypa.io/get-pip.py | python
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install numpy pandas "pytorch-lightning>=2.0,<2.4" torch-geometric fair-esm rdkit MDAnalysis pymol-open-source-whl
```

GraphPep package (`~/GraphPep_v1.1`):

```bash
# unpack GraphPep_v1.1.zip to ~/GraphPep_v1.1, then:
cp methods/graphpep/getseq.awk ~/GraphPep_v1.1/bin/     # missing from the release; pre.py shells out to it
# edit ~/GraphPep_v1.1/GraphPep.sh header:
#   export GraphPep_root=/home/<you>/GraphPep_v1.1
#   export esm2_path=<path to esm2_t33_650M_UR50D.pt>
#   export PATH=$GraphPep_root/bin:$PATH      # for the getseq.awk shell-out
#   source ~/gp_env/bin/activate             # replaces 'source activate graphpep_env'
```

ESM-2 weights: `esm2_t33_650M_UR50D.pt` (~2.6 GB) +
`esm2_t33_650M_UR50D-contact-regression.pt` from
`https://dl.fbaipublicfiles.com/fair-esm/{models,regression}/`.
(One copy already lives at
`C:\Users\salma\AMP-Benchmarking\EPIC-AMP\DiffPepBuilder\experiments\checkpoints\`.)

### Notes / gotchas

- `getseq.awk` is **not in the released zip** — `bin/pre.py` calls it via `os.system`;
  without it the ESM step fails. `methods/graphpep/getseq.awk` is a drop-in.
- GraphPep takes **one fixed receptor** for all decoys. Our predictions move the
  whole complex, so `pipeline/graphpep_prep.py` superposes each pose's receptor onto
  rank00's and re-frames the peptide accordingly.
- `-PB` (PoseBusters plausibility) also needs Open Babel + posebusters — we don't use it.

## Run

```bash
python pipeline/rerank_prep.py                 # predictions/<m>/<id>_rankNN.pdb (+ manifest)
python pipeline/run_dockq.py                   # DockQ for every pose -> results/summary.csv
python pipeline/graphpep_prep.py               # rerank/graphpep/<m>/<id>/{protein,decoys}.pdb
bash   methods/graphpep/score_all.sh           # -> rerank/graphpep/<m>/<id>/graphpep.csv   (run in WSL)
python pipeline/rerank_eval.py --reranker graphpep --score-ascending
#   -> results/rerank.md / rerank.csv  (docker top-1 vs GraphPep top-1 vs oracle)
```
