#!/usr/bin/env bash
# Headless AlphaFold2-Multimer via ColabFold for the benchmark targets.
#
# ColabFold needs JAX, which is not supported on native Windows -- run this on
# Linux: the university HPC (fast, GPU) or any Linux box with internet (CPU works
# for these small complexes, ~20-60 min each). The MSA step calls the public
# ColabFold MMseqs2 server, so outbound internet is required.
#
# Install (once):
#   pip install "colabfold[alphafold]"        # or: conda/mamba env, or the colabfold docker image
#
# Usage:
#   bash run_colabfold.sh ../inputs/colabfold ../predictions/_raw/colabfold
# then back on any machine:
#   python ingest.py --method colabfold --src predictions/_raw/colabfold
#   python run_dockq.py --method colabfold
set -euo pipefail

IN_DIR="${1:-../inputs/colabfold}"
OUT_DIR="${2:-../predictions/_raw/colabfold}"
SEED="${COLABFOLD_SEED:-1}"
NUM_MODELS="${COLABFOLD_NUM_MODELS:-5}"
EXTRA_ARGS="${COLABFOLD_EXTRA_ARGS:-}"   # e.g. "--num-recycle 6 --amber"

mkdir -p "$OUT_DIR"
echo "colabfold_batch $(colabfold_batch --version 2>/dev/null || echo '?')  seed=$SEED  models=$NUM_MODELS  $(date -u +%FT%TZ)" \
  | tee "$OUT_DIR/RUN_INFO.txt"

shopt -s nullglob
for fasta in "$IN_DIR"/*.fasta; do
  id="$(basename "$fasta" .fasta)"
  if compgen -G "$OUT_DIR/${id}"'*rank_001*.pdb' > /dev/null; then
    echo "== $id: done, skipping"; continue
  fi
  echo "== $id"
  colabfold_batch \
    --model-type alphafold2_multimer_v3 \
    --num-models "$NUM_MODELS" \
    --random-seed "$SEED" \
    --rank iptm \
    $EXTRA_ARGS \
    "$fasta" "$OUT_DIR" 2>&1 | tee -a "$OUT_DIR/${id}.log"
done

echo "done -> $OUT_DIR"
