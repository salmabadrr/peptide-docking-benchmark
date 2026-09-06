#!/bin/bash
# Loop GraphPep over every prepped ensemble and emit rerank_eval.py-ready score files.
#
# Prereq (one-time, see methods/graphpep/README.md):
#   - GraphPep_v1.1 unpacked at $GP_ROOT (default ~/GraphPep_v1.1), with getseq.awk
#     (this dir) copied into $GP_ROOT/bin/ and GraphPep.sh's env lines pointed at
#     your venv + a valid esm2_t33_650M_UR50D.pt, plus:
#         export PATH=$GraphPep_root/bin:$PATH
#   - python venv on PATH: torch, torch-geometric, pytorch-lightning, rdkit,
#     MDAnalysis, fair-esm, pymol
#   - pipeline/graphpep_prep.py already run
#
# GraphPep.sh is not whitespace-safe, and this repo path contains a space, so each
# ensemble is staged into a space-free work dir ($WORK, default ~/gp_run) before
# scoring; score.csv / graphpep.csv are copied back into rerank/graphpep/<m>/<id>/.
#
# Usage:  bash methods/graphpep/score_all.sh [REPO_ROOT] [GP_ROOT] [WORK]   (run in WSL)
set -u
REPO=${1:-$(cd "$(dirname "$0")/../.." && pwd)}
GP_ROOT=${2:-~/GraphPep_v1.1}
WORK=${3:-~/gp_run}
BASE="$REPO/rerank/graphpep"

[ -d "$BASE" ] || { echo "no $BASE -- run pipeline/graphpep_prep.py first"; exit 1; }
mkdir -p "$WORK"
n=0; fail=0
for d in "$BASE"/*/*/ ; do
    [ -f "$d/protein.pdb" ] && [ -f "$d/decoys.pdb" ] || continue
    rel=${d#"$BASE"/}; rel=${rel%/}
    tag=${rel//\//_}
    w="$WORK/$tag"
    mkdir -p "$w"
    cp -f "$d/protein.pdb" "$d/decoys.pdb" "$w/"
    printf '%-28s ' "$rel"
    ( cd "$w" && bash "$GP_ROOT/GraphPep.sh" protein.pdb decoys.pdb -out score.csv ) \
        > "$w/graphpep.log" 2>&1
    if [ -f "$w/score.csv" ]; then
        cp -f "$w/score.csv" "$d/score.csv"
        awk -F, 'NR==1{print "decoy_rank,score"; next}{print $1-1","$2}' "$w/score.csv" > "$d/graphpep.csv"
        echo "ok  ($(tail -n +2 "$w/score.csv" | wc -l) decoys)"
        n=$((n+1))
    else
        echo "FAIL (see $w/graphpep.log)"
        fail=$((fail+1))
    fi
done
echo
echo "scored $n ensembles, $fail failed"
echo "next:  python pipeline/rerank_eval.py --reranker graphpep --score-ascending"
