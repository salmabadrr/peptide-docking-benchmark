# EPIC-AMP protein–peptide docking benchmark — results draft

_Working draft for the thesis/paper Results section. Numbers are current as of the
last pipeline run (2026-09-06); regenerate from `results/REPORT.md`,
`results/rerank.md`, `results/summary.csv` before submission._

---

## 1. Aim and scope

We benchmark current all-atom structure-prediction methods on their ability to
reproduce experimentally determined **protein–antimicrobial-peptide (AMP)
complexes**, scored against the crystal structures with **DockQ**. Two questions:

- **Objective 1 — prediction accuracy.** How close is each method's top-ranked
  model to the native complex?
- **Objective 2 — pose re-ranking.** Given a method's own set of models, can an
  external scoring function (GraphPep; InterPepRank) select a better pose than the
  method's own rank 1?

DockQ is used only for evaluation, never for model selection.

---

## 2. Benchmark construction

### 2.1 Starting point

The seed set was a manually curated spreadsheet of protein–AMP crystal structures
(`AMP data edited.xlsx`, ~18 entries) plus five AlphaFold-Multimer predictions from
prior lab work. Every candidate had to be (i) a genuine antimicrobial peptide bound
to (ii) a single protein partner, in (iii) a crystal structure suitable as a DockQ
reference.

### 2.2 RCSB discovery sweep

To enlarge the set we ran an automated search of the RCSB PDB
(`pipeline/discover_targets.py`): **26 AMP-family query terms** (defensin,
cathelicidin, magainin, protegrin, LL-37, drosocin, apidaecin, pyrrhocoricin,
thanatin, melittin, …), resolution ≤ 2.8 Å, receptor 40–2000 aa, peptide 4–50 aa,
exactly one receptor and one peptide chain. **506 unique candidates** were
screened; **77** passed the geometric filter and were fully scored
(`results/discovery_candidates.csv`): 39 `ok`, 13 `caution`, 25 `drop` by the
automated resolved-fraction / non-standard-residue check.

Each surviving candidate was then **manually verified against the deposited entry's
own citation title** to confirm real antimicrobial activity (not a crystal-form
duplicate, not a protease-substrate or cytokine-antagonist false positive from the
generic "antimicrobial peptide" term). Eight were added; four that had been added
on a first pass were later removed (see 2.3 C–D).

### 2.3 Exclusion criteria

`configs/targets.yaml` is the single source of truth and retains every rejected
entry (`include: false`) with its reason. **30 entries total → 13 included, 17
excluded.**

| Class | Rule | n | Entries |
|---|---|---|---|
| **A. Peptide disordered** | < 50 % of the peptide modelled in the crystal → no reliable native interface | 6 | 6Z2Q (2/19), 8GQA (9/20), 3QNJ (8/19), 4JWE (9/21), 8ITG (7/42), 6Y0X (5/12) |
| **B. D-amino-acid / non-standard peptide** | peptide chain contains D-residues or non-proteinogenic residues with no one-letter code | 6 | 6Q6W, 6Q77, 6Q85, 6Q86, 6Y0W (all D-peptide ligands of LecB), 8ONU (DAB + hydroxyproline) |
| **C. Unencodable residue in SEQRES** | discovery candidate whose SEQRES carries a literal `X` (modified residue) | 2 | 4JWI (`PRPILLPWRX`), 7NEF (`KKLLKLLKLLLX`) |
| **D. Not a genuine AMP** | discovery candidate whose citation shows a non-antimicrobial context | 2 | 2HD4 (proteinase-K inhibitor peptide), 4N6P (lactoferrin fragment in a drug-binding study; also the representative of a 15-way duplicate cluster) |
| **E. Resolved fragment not in contact** | ≥ 50 % modelled, but the ordered residues lie outside the receptor interface | 1 | 4JWD (7/14 modelled; those 7 sit ~6.1 Å from the nearest receptor atom → DockQ finds no native interface) |

**Rationale for class B.** Every method here (AlphaFold-Multimer, AlphaFold 3,
Boltz-2, Chai-1, Protenix) takes a plain letter sequence and builds the
L-enantiomer. Scoring an L-model against a D-native measures a mirror-image
mismatch, not the predictor's skill — every method scores ≈ 0 identically, adding
no signal — and an all-D chain crashes DockQ outright (Bio.PDB drops the
all-non-standard chain, raising `KeyError`).

### 2.4 Final target set (n = 13)

8 `ok` (≥ 80 % of the peptide resolved), 5 `caution` (50–80 % resolved; DockQ
computed over the modelled fragment, reported with an asterisk).

| PDB | Receptor | Peptide | Len | Resolved | Quality | Source |
|---|---|---|--:|---|---|---|
| 6HY2 | LpxA acyltransferase (*E. coli*) | peptide inhibitor | 12 | 12/12 | ok | seed |
| 4EZS | DnaK chaperone (*E. coli*) | Metchnikowin | 8 | 8/8 | ok | seed |
| 8GAL | LptA (*E. coli*) | Thanatin | 20 | 18/20 | ok | seed |
| 6Z2P | O-glycan protease (*Akkermansia*) | Glycodrosocin | 19 | 10/19 | caution | seed |
| 4JWC | DnaK (*E. coli*) | Cathelicidin-3 / Bac7-type | 16 | 9/16 | caution | seed |
| 4EZR | DnaK (*E. coli*) | Drosocin | 8 | 8/8 | ok | discovery |
| 4E81 | DnaK (*E. coli*) | Apidaecin fragment | 10 | 9/10 | ok | discovery |
| 4EZU | DnaK (*E. coli*) | PR-bombesin (*Bombina maxima*) | 17 | 14/17 | ok | discovery |
| 4EZQ | DnaK (*E. coli*) | Pyrrhocoricin | 9 | 7/9 | caution | discovery |
| 4EZO | DnaK (*E. coli*) | PR-39 | 15 | 8/15 | caution | discovery |
| 8AHT | Calmodulin | Melittin | 26 | 25/26 | ok | discovery |
| 3QRX | Centrin | Melittin | 26 | 20/26 | caution | discovery |
| 7SAY | engineered GCN4 scaffold | LL-37 | 37 | 35/37 | ok | discovery |

**Composition caveats.** DnaK is the receptor in **7 of 13** targets (proline-rich
AMPs threaded through the substrate channel); melittin (`GIGAVLKVLTTGLPALISWIKRKRQQ`)
is the peptide in **two** targets with different host proteins (8AHT, 3QRX). 7SAY's
"receptor" is an artificial crystallisation scaffold, not a natural partner —
included only to have an LL-37 complex at all.

### 2.5 Native reference preparation

`pipeline/prep_native.py` downloads the RCSB entry, keeps biological assembly 1,
retains one receptor + one peptide chain, strips ligands / waters / alternate
locations / hydrogens, and writes `data/natives/<ID>_native.pdb`.
`data/natives/_audit.csv` records the resolved fraction that drives the
ok/caution/drop call.

---

## 3. Methods and how they were run

No local GPU was available; all predictors were run through their public web
portals (manual submission, no API) except Boltz-2, which requires a GPU batch job.

| Method | Model | Where run | Targets done | Notes |
|---|---|---|--:|---|
| AlphaFold-Multimer | AF2 for complexes | COSMIC² (SDSC HPC), web | 6 | 5 models/target, ranked by `iptm+ptm` |
| AlphaFold 3 | AF3 | AlphaFold Server, web | 10 | 5 models, `ranking_score` |
| Chai-1 | open AF3-class | lab.chaidiscovery.com, web (free) | 13 | 5 models, `aggregate_score` |
| Protenix | ByteDance AF3 reproduction | protenix-server.com, web (free) | 13 | 5 samples, `ranking_score` |
| Boltz-2 | open biomolecular model | university HPC (GPU) | 1 | blocked on cluster scheduler/env; only 6HY2 |

`pipeline/collect_predictions.py` normalises every download to a 2-chain PDB with
native chain IDs and extracts each tool's own confidence to
`results/confidences.csv`. Seed = 1 where user-controllable; server defaults
elsewhere. **43 predictions total.**

---

## 4. Evaluation protocol

`pipeline/run_dockq.py` runs **DockQ v2** as
`DockQ <model> <native> --mapping <rec><pep>:<rec><pep> --allowed_mismatches 3
--short`. CAPRI bands (standard thresholds): **incorrect < 0.23 ≤ acceptable <
0.49 ≤ medium < 0.80 ≤ high**. Results roll up through `pipeline/report.py` into
`results/REPORT.md` and `results/summary.csv`.

---

## 5. Results — Objective 1 (prediction accuracy)

### 5.1 Per method

| Method | n | mean DockQ | ≥ acceptable | ≥ medium | ≥ high | mean confidence | Spearman(confidence, DockQ) |
|---|--:|--:|--:|--:|--:|--:|--:|
| Boltz-2 | 1 | 0.928 | 1/1 | 1/1 | 1/1 | 0.96 | – |
| Protenix | 13 | **0.650** | 11/13 | 10/13 | 4/13 | 0.79 | 0.68 |
| AlphaFold-Multimer | 6 | 0.520 | 5/6 | 3/6 | 1/6 | 0.73 | 0.80 |
| AlphaFold 3 | 10 | 0.495 | 8/10 | 5/10 | 2/10 | 0.74 | 0.71 |
| Chai-1 | 13 | 0.448 | 7/13 | 6/13 | 2/13 | 0.56 | 0.73 |

Means are over **different target subsets** (see §7). On the **complete 13-target
set**, only Chai-1 and Protenix have run every target: **Protenix leads clearly**
(mean 0.650, 10/13 ≥ medium) over Chai-1 (0.448, 6/13 ≥ medium). Boltz-2's single
point (6HY2, 0.93) is its best-case and not comparable.

### 5.2 Per target (best pose, DockQ)

`*` = caution (partial peptide).

| Target | Len | af3 | af-mult | boltz | chai | protenix | best |
|---|--:|--:|--:|--:|--:|--:|--:|
| 4E81 | 10 | 0.90 | 0.93 | – | 0.95 | 0.90 | **0.95 (high)** |
| 4EZR | 8 | 0.93 | – | – | 0.92 | 0.91 | **0.93 (high)** |
| 4EZS | 8 | 0.29 | 0.29 | – | 0.38 | 0.93 | **0.93 (high)** |
| 6HY2 | 12 | 0.29 | 0.39 | 0.93 | 0.21 | 0.69 | **0.93 (high)** |
| 8GAL | 20 | – | 0.75 | – | 0.79 | 0.83 | 0.83 (high) |
| 4EZQ* | 9 | – | 0.59 | – | 0.21 | 0.79 | 0.79 (medium) |
| 6Z2P* | 19 | 0.14 | 0.17 | – | 0.07 | 0.77 | 0.77 (medium) |
| 4EZO* | 15 | 0.71 | – | – | 0.69 | 0.75 | 0.75 (medium) |
| 4JWC* | 16 | 0.67 | – | – | 0.69 | 0.65 | 0.69 (medium) |
| 8AHT | 26 | 0.40 | – | – | 0.55 | 0.66 | 0.66 (medium) |
| 3QRX* | 26 | 0.53 | – | – | 0.23 | 0.39 | 0.53 (medium) |
| 4EZU | 17 | 0.08 | – | – | 0.09 | 0.18 | **0.18 (incorrect)** |
| 7SAY | 37 | – | – | – | 0.07 | 0.01 | **0.07 (incorrect)** |

- **4 targets solved to high accuracy** by at least one method (4E81, 4EZR, 4EZS,
  6HY2). All are short (8–12 aa).
- **2 targets fail for every method**: 7SAY (LL-37, best 0.07; but the receptor is
  a synthetic scaffold — arguably a mis-specified target) and 4EZU (PR-bombesin,
  best 0.18, fnat ≈ 0 — likely wrong site/register).
- **Large between-method spread on nominally easy targets.** 4EZS (8-aa peptide):
  AF3 / AF-Multimer / Chai-1 all ≈ 0.29–0.38 (acceptable) but Protenix 0.925.
  6HY2: Boltz-2 0.93 and Protenix 0.69 vs AF3 / Chai-1 ≈ 0.2–0.29. The choice of
  method matters more than the apparent difficulty of the target.

### 5.3 Confidence vs accuracy

Pooled **Spearman(confidence, DockQ) = 0.69** over 41 predictions; per-method
0.68–0.80. Each tool's self-reported confidence is a **usable filter** for which
predictions to trust, though not a precise accuracy estimate.

### 5.4 Determinants of difficulty

- **Peptide length:** Spearman(length, DockQ) = **−0.43** — longer peptides score
  worse. The four high-accuracy targets are all ≤ 12 aa; the two total failures are
  the two longest (17, 37 aa).
- **Partial resolution (caution targets):** no systematic penalty — several of
  Protenix's best scores are on caution targets (6Z2P 0.77, 4EZO 0.75) — but these
  DockQ values are computed over a peptide fragment and are weaker evidence.
- **Receptor family:** the DnaK proline-rich-AMP complexes (7/13) are mostly
  solved to medium/high by Protenix; the two hardest are non-DnaK (7SAY scaffold,
  and 4EZU which is DnaK but with an unusual peptide).

---

## 6. Results — Objective 2 (pose re-ranking)

### 6.1 Setup

Each method emits 5 ranked models per target. We treat these as a decoy set:
`pipeline/rerank_prep.py` explodes them to per-pose PDBs (rank 00 = the method's
own top pose), `run_dockq.py` scores **every** pose, and `pipeline/rerank_eval.py`
compares three selection strategies by the DockQ of the selected pose —
**docker top-1** (baseline), **re-ranker top-1**, and **oracle** (best of the 5).
**41 ensembles** (af3 ×10, chai ×13, protenix ×13, af-multimer ×4, boltz ×1),
5 poses each. For methods where the whole complex moves between models,
`pipeline/graphpep_prep.py` superposes each pose's receptor onto rank 00's frame.

### 6.2 Re-ranking headroom (oracle − docker top-1)

| Method | n | docker top-1 (mean DockQ) | oracle (mean DockQ) | headroom |
|---|--:|--:|--:|--:|
| AlphaFold 3 | 10 | 0.495 | 0.672 | **+0.177** |
| Chai-1 | 13 | 0.448 | 0.562 | **+0.114** |
| AlphaFold-Multimer | 4 | 0.551 | 0.633 | +0.082 |
| Protenix | 13 | 0.650 | 0.665 | +0.016 |
| Boltz-2 | 1 | 0.928 | 0.928 | +0.000 |
| **All** | 41 | 0.545 | 0.637 | **+0.092** |

A perfect re-ranker would raise the **≥ medium** count from 24/41 → 29/41 and
**≥ high** from 10/41 → 13/41. The headroom is **highly method-dependent**:

- **AF3 and Chai-1 leave substantial accuracy on the table** — their rank 1 is
  often not their best pose. Extreme cases: af3/6Z2P 0.14 → 0.84 (pose #2),
  chai/4EZQ 0.21 → 0.82 (#4), af3/6HY2 0.29 → 0.85 (#4), chai/6Z2P 0.07 → 0.45.
- **Protenix is already near-oracle** (+0.016) — its own confidence ranking is
  effectively optimal on this set, so external re-ranking has almost nothing to
  add.

This sets the ceiling any re-ranker must approach to be useful.

### 6.3 GraphPep

GraphPep (Huang lab, HUST; *Nat. Mach. Intell.* 2026) — interaction-derived graph
network + ESM-2 features; binding score `−log(1 + predicted_fnat)`, more negative =
better pose. Package: Zenodo 10.5281/zenodo.17099863 (trained weights bundled); run
locally on CPU (WSL); see `methods/graphpep/`. Reproduced the shipped example
bit-for-bit. All 41 ensembles scored.

| Method | n | docker top-1 | oracle | **GraphPep top-1** | Δ vs docker | win / tie / loss | mean ρ(score, DockQ) |
|---|--:|--:|--:|--:|--:|:--:|--:|
| AlphaFold 3 | 10 | 0.495 | 0.672 | **0.620** | **+0.125** | 2 / 8 / 0 | +0.02 |
| Chai-1 | 13 | 0.448 | 0.562 | 0.461 | +0.013 | 2 / 11 / 0 | +0.04 |
| AlphaFold-Multimer | 4 | 0.551 | 0.633 | 0.465 | **−0.086** | 0 / 3 / 1 | 0.00 |
| Protenix | 13 | 0.650 | 0.665 | 0.612 | **−0.038** | 1 / 11 / 1 | −0.42 |
| Boltz-2 | 1 | 0.928 | 0.928 | 0.908 | −0.019 | 0 / 0 / 1 | −0.10 |
| **All** | 41 | 0.545 | 0.637 | **0.559** | **+0.014** | **5 / 33 / 3** | −0.12 |

(win/tie/loss = GraphPep top-1 vs docker top-1, tie = within 0.02 DockQ. ρ =
Spearman(GraphPep score, DockQ) within one 5-pose ensemble, per-method mean.)

**GraphPep does not improve on the dockers' own ranking on this set.** Overall it is
within noise of the baseline (+0.014 DockQ, 33/41 ties) and recovers only ~15 % of
the +0.092 headroom. The picture by method:

- **AlphaFold 3 — clear benefit (+0.125, 71 % of AF3's headroom recovered).**
  Two decisive corrections drive it: af3/6Z2P 0.14 → 0.84 and af3/6HY2 0.29 → 0.85,
  in both cases selecting the true oracle pose. No losses. But it still misses
  af3/4EZS (leaves +0.39 on the table).
- **Chai-1 — neutral (+0.013).** Catches chai/6HY2 (0.21 → 0.37) and chai/4EZS
  (0.375 → 0.410), ties everything else, and misses the two largest Chai headrooms
  (chai/4EZQ 0.21 → 0.82, chai/6Z2P 0.07 → 0.45).
- **Protenix and AlphaFold-Multimer — net harmful (−0.038, −0.086).** GraphPep
  confidently swapped in a much worse pose on protenix/4EZQ (0.79 → 0.23) and
  afmultimer/4EZQ (0.59 → 0.23). Because Protenix's own ranking is already
  near-oracle, any re-ranking there is downside risk only.
- **Within-ensemble discrimination is essentially absent.** Pooled
  Spearman(GraphPep score, DockQ) = **−0.12**; −0.42 for Protenix. GraphPep's score
  ordering does not track DockQ across a method's five models — it lands the right
  pose occasionally but not systematically.
- **CAPRI bands:** ≥ high 10 → 12/41 (the two AF3 saves); ≥ acceptable and ≥ medium
  unchanged (31/41, 24/41).

**Interpretation / caveats.** GraphPep was trained on classical docking decoys
(FlexPepDock, ADCP, LEADS-PEP) — broad conformational spreads around a fixed
receptor. AlphaFold-style ensembles are five near-duplicate high-confidence models
with a moving receptor (which we re-frame by superposition); this is a real
distribution shift and the most likely reason the score fails to rank them. Only
5 poses per ensemble is also thin for a ranking task, and results are single-seed.
The one robust finding is that **GraphPep can rescue AF3's occasional
catastrophic rank-1 errors**, but it cannot be applied blindly — for Protenix it
costs accuracy.

### 6.4 InterPepRank

Not run. Code is on Bitbucket (`isaakh94/interpeprank`), a 2020-era
TensorFlow/Spektral/Keras stack, and its node features require an HHblits search of
`uniclust30_2016_03` (~50 GB) for the receptor PSSM. Deferred to the university
cluster. The evaluation harness (`rerank_eval.py --reranker interpeprank`) is
ready; only the score files are missing.

---

## 7. Limitations and pitfalls

**Dataset**

1. **Small n (13).** Adequate for descriptive comparison; **not** for significance
   testing between methods. All method rankings here are indicative.
2. **Uneven method coverage.** Chai-1 and Protenix span all 13 targets; AF3 10,
   AlphaFold-Multimer 6, Boltz-2 1 (web submission is manual; Boltz-2 needs a GPU
   we don't have). Per-method means in §5.1 are over different subsets and are not
   yet strictly comparable — only the Chai-1 vs Protenix comparison is complete.
3. **Receptor redundancy.** DnaK is 7/13 targets; melittin is the peptide in 2.
   Effective diversity is lower than n = 13; family-level averaging is advisable.
4. **7SAY is a mis-specified target** — the "receptor" is an engineered GCN4/M-protein
   crystallisation scaffold, not a physiological LL-37 partner. Its near-zero DockQ
   for every method should probably be excluded from headline statistics.
5. **Caution targets (5/13)** are scored over a 50–78 % peptide fragment; their
   DockQ values carry less weight and are flagged with `*`.
6. **Single seed / server-default sampling.** No estimate of sampling variance
   within a method.
7. **Assembly ambiguity.** Biological assembly 1 was used throughout; the seed
   spreadsheet did not specify assembly vs deposited entry.

**Data-quality traps encountered (and how they were caught)**

8. **D-amino-acid peptides crash DockQ silently** (Bio.PDB drops the
   all-non-standard chain → `KeyError`). Must be filtered before scoring
   (criterion B).
9. **Literal `X` in RCSB SEQRES** (non-proteinogenic residues) is written verbatim
   into every predictor's input file. The discovery screen only checked *resolved*
   residues; `prep_native.py` checks SEQRES and caught 4JWI / 7NEF (criterion C).
10. **Name-based AMP identification is unreliable.** 2HD4 and 4N6P were added as
    "lactoferricin-related" by name association; their citation titles show a
    proteinase-K inhibitor peptide and a small-molecule drug-binding study
    respectively (criterion D). AMP relevance must be verified against the entry's
    own citation.
11. **>50 % resolved ≠ scorable.** 4JWD has 7/14 residues modelled but they do not
    contact the receptor, so DockQ returns no interface at all (criterion E, added
    after the first DockQ run produced empty output for every method on 4JWD).

**Tooling issues (documented for reproducibility)**

12. **GraphPep v1.1 release is incomplete** — `bin/getseq.awk` (called by `pre.py`)
    is missing; supplied as `methods/graphpep/getseq.awk`. `GraphPep.sh` is not
    whitespace-safe (the repo path contains a space) — worked around by staging
    each job into a space-free directory.
13. **ESM-2 checkpoint integrity.** The `esm2_t33_650M_UR50D.pt` already on disk
    was truncated (~4 MB short, no zip central directory); re-downloaded from the
    fair-esm host. `fair-esm 2.0.0` is also incompatible with `torch ≥ 2.6`
    (`weights_only=True` default rejects the checkpoint) — patched to
    `weights_only=False`.

---

## 8. Reproducibility

- **Target set:** `configs/targets.yaml` (every included and excluded entry, with
  reason). Full discovery output: `results/discovery_candidates.csv`.
- **Pipeline:** `pipeline/` — `prep_native → make_inputs → collect_predictions →
  run_dockq → report`; Objective 2 adds `rerank_prep → run_dockq → rerank_eval`
  (+ `graphpep_prep`).
- **Scores:** `results/summary.csv` (per-pose DockQ), `results/confidences.csv`
  (tool confidences), `results/REPORT.md`, `results/rerank.md`,
  `results/rerank.csv`.
- **External:** DockQ v2 (`pip install DockQ`); GraphPep
  (Zenodo 10.5281/zenodo.17099863, weights bundled); ESM-2
  `esm2_t33_650M_UR50D`; RCSB PDB accessions as listed.
- **Predictor versions/dates:** record per submission (COSMIC² pipeline version;
  AlphaFold Server date; Chai-1 / Protenix server version) — _to be tabulated._
