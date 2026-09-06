# Benchmark report — DockQ vs. tool confidence

_generated 2026-09-06 11:05 UTC_

43 predictions scored across 5 methods and 13 of 13 included targets.

`rank_score` = each tool's own headline confidence for the top pose (AF3/Protenix `ranking_score`, Chai `aggregate_score`, AlphaFold-Multimer `iptm+ptm`, Boltz `confidence_score`). DockQ: incorrect <0.23, acceptable 0.23–0.49, medium 0.49–0.80, high ≥0.80.


## 1. Results by target


### 4E81 — Apidaecin fragment  ·  peptide 10 aa, resolved 9/10  ·  quality: ok

| method | DockQ | class | iRMSD | fnat | rank_score | ptm | iptm |
|---|--:|---|--:|--:|--:|--:|--:|
| af3 | 0.904 | high | 0.672 | 0.927 | 0.92 | 0.9 | 0.89 |
| afmultimer | 0.930 | high | 0.631 | 0.976 | 0.8569 | - | - |
| chai | 0.946 | high | 0.551 | 0.976 | 0.7338 | 0.879 | 0.6975 |
| protenix | 0.898 | high | 0.715 | 0.902 | 0.812 | 0.9194 | 0.7852 |

### 4EZQ — Pyrrhocoricin  ·  peptide 9 aa, resolved 7/9  ·  quality: caution

| method | DockQ | class | iRMSD | fnat | rank_score | ptm | iptm |
|---|--:|---|--:|--:|--:|--:|--:|
| afmultimer | 0.587 | medium | 1.244 | 0.333 | 0.8424 | - | - |
| chai | 0.210 | incorrect | 4.226 | 0.244 | 0.6849 | 0.8714 | 0.6382 |
| protenix | 0.793 | medium | 1.068 | 0.844 | 0.8493 | 0.9232 | 0.8309 |

### 4EZR — Drosocin  ·  peptide 8 aa, resolved 8/8  ·  quality: ok

| method | DockQ | class | iRMSD | fnat | rank_score | ptm | iptm |
|---|--:|---|--:|--:|--:|--:|--:|
| af3 | 0.934 | high | 0.476 | 0.918 | 0.95 | 0.91 | 0.94 |
| chai | 0.919 | high | 0.487 | 0.878 | 0.6296 | 0.876 | 0.568 |
| protenix | 0.909 | high | 0.55 | 0.878 | 0.9532 | 0.93 | 0.959 |

### 4EZS — Metchnikowin (Drosophila)  ·  peptide 8 aa, resolved 8/8  ·  quality: ok

| method | DockQ | class | iRMSD | fnat | rank_score | ptm | iptm |
|---|--:|---|--:|--:|--:|--:|--:|
| af3 | 0.287 | acceptable | 3.009 | 0.184 | 0.79 | 0.89 | 0.74 |
| afmultimer | 0.294 | acceptable | 2.735 | 0.184 | 0.7 | - | - |
| chai | 0.375 | acceptable | 2.321 | 0.265 | 0.5157 | 0.8746 | 0.4259 |
| protenix | 0.925 | high | 0.664 | 0.959 | 0.9339 | 0.9314 | 0.9345 |

### 6HY2 —   ·  peptide 12 aa, resolved 12/12  ·  quality: ok

| method | DockQ | class | iRMSD | fnat | rank_score | ptm | iptm |
|---|--:|---|--:|--:|--:|--:|--:|
| af3 | 0.289 | acceptable | 3.275 | 0.125 | 0.74 | 0.94 | 0.66 |
| afmultimer | 0.395 | acceptable | 2.494 | 0.25 | 0.5337 | - | - |
| boltz | 0.928 | high | 0.507 | 0.9 | 0.96 | 0.97 | 0.88 |
| chai | 0.206 | incorrect | 4.578 | 0.2 | 0.3131 | 0.9212 | 0.1611 |
| protenix | 0.685 | medium | 1.464 | 0.7 | 0.8606 | 0.9646 | 0.8346 |

### 3QRX — Melittin (different host-protein  ·  peptide 26 aa, resolved 20/26  ·  quality: caution

| method | DockQ | class | iRMSD | fnat | rank_score | ptm | iptm |
|---|--:|---|--:|--:|--:|--:|--:|
| af3 | 0.525 | medium | 2.501 | 0.786 | 0.53 | 0.57 | 0.36 |
| chai | 0.228 | incorrect | 3.447 | 0.429 | 0.4411 | 0.5948 | 0.4027 |
| protenix | 0.389 | acceptable | 2.42 | 0.786 | 0.6327 | 0.6233 | 0.6351 |

### 4EZO — PR-39 antibacterial protein  ·  peptide 15 aa, resolved 8/15  ·  quality: caution

| method | DockQ | class | iRMSD | fnat | rank_score | ptm | iptm |
|---|--:|---|--:|--:|--:|--:|--:|
| af3 | 0.711 | medium | 1.486 | 0.837 | 0.85 | 0.89 | 0.79 |
| chai | 0.688 | medium | 1.554 | 0.796 | 0.784 | 0.8833 | 0.7592 |
| protenix | 0.750 | medium | 1.302 | 0.816 | 0.8536 | 0.9189 | 0.8373 |

### 4EZU — 'PR-bombesin' from Bombina maxim  ·  peptide 17 aa, resolved 14/17  ·  quality: ok

| method | DockQ | class | iRMSD | fnat | rank_score | ptm | iptm |
|---|--:|---|--:|--:|--:|--:|--:|
| af3 | 0.084 | incorrect | 6.39 | 0.0 | 0.7 | 0.88 | 0.6 |
| chai | 0.090 | incorrect | 8.43 | 0.117 | 0.5948 | 0.8504 | 0.5309 |
| protenix | 0.178 | incorrect | 4.557 | 0.117 | 0.8298 | 0.9177 | 0.8079 |

### 6Z2P — Glycodrosocin  ·  peptide 19 aa, resolved 10/19  ·  quality: caution

| method | DockQ | class | iRMSD | fnat | rank_score | ptm | iptm |
|---|--:|---|--:|--:|--:|--:|--:|
| af3 | 0.142 | incorrect | 4.799 | 0.056 | 0.54 | 0.91 | 0.39 |
| afmultimer | 0.171 | incorrect | 4.887 | 0.167 | - | - | - |
| chai | 0.070 | incorrect | 7.547 | 0.056 | 0.362 | 0.8947 | 0.2288 |
| protenix | 0.769 | medium | 1.187 | 0.833 | 0.6357 | 0.9393 | 0.5599 |

### 7SAY — LL-37, the canonical human cathe  ·  peptide 37 aa, resolved 35/37  ·  quality: ok

| method | DockQ | class | iRMSD | fnat | rank_score | ptm | iptm |
|---|--:|---|--:|--:|--:|--:|--:|
| chai | 0.068 | incorrect | 14.435 | 0.148 | 0.3256 | 0.5994 | 0.2571 |
| protenix | 0.014 | incorrect | 18.272 | 0.0 | 0.4405 | 0.5858 | 0.4042 |

### 8AHT — Melittin (bee venom AMP)  ·  peptide 26 aa, resolved 25/26  ·  quality: ok

| method | DockQ | class | iRMSD | fnat | rank_score | ptm | iptm |
|---|--:|---|--:|--:|--:|--:|--:|
| af3 | 0.404 | acceptable | 4.015 | 0.379 | 0.56 | 0.54 | 0.46 |
| chai | 0.550 | medium | 2.459 | 0.495 | 0.6045 | 0.7742 | 0.5621 |
| protenix | 0.656 | medium | 1.849 | 0.663 | 0.6521 | 0.7183 | 0.6355 |

### 4JWC — Cathelicidin-3/Bac7-type (Bos ta  ·  peptide 16 aa, resolved 9/16  ·  quality: caution

| method | DockQ | class | iRMSD | fnat | rank_score | ptm | iptm |
|---|--:|---|--:|--:|--:|--:|--:|
| af3 | 0.672 | medium | 1.431 | 0.692 | 0.83 | 0.88 | 0.78 |
| chai | 0.685 | medium | 1.377 | 0.692 | 0.4247 | 0.8379 | 0.3214 |
| protenix | 0.653 | medium | 1.715 | 0.692 | 0.8372 | 0.9225 | 0.8159 |

### 8GAL — Thanatin  ·  peptide 20 aa, resolved 18/20  ·  quality: ok

| method | DockQ | class | iRMSD | fnat | rank_score | ptm | iptm |
|---|--:|---|--:|--:|--:|--:|--:|
| afmultimer | 0.746 | medium | 0.88 | 0.808 | - | - | - |
| chai | 0.786 | medium | 0.768 | 0.827 | 0.8176 | 0.8868 | 0.8003 |
| protenix | 0.827 | high | 0.72 | 0.923 | 0.9477 | 0.9358 | 0.9507 |

## 2. By method

| method | n | DockQ mean | ≥acceptable | ≥medium | ≥high | mean rank_score | Spearman(rank_score, DockQ) |
|---|--:|--:|--:|--:|--:|--:|--:|
| af3 | 10 | 0.495 | 8/10 | 5/10 | 2/10 | 0.74 | 0.71 |
| afmultimer | 6 | 0.520 | 5/6 | 3/6 | 1/6 | 0.73 | 0.8 |
| boltz | 1 | 0.928 | 1/1 | 1/1 | 1/1 | 0.96 | n/a |
| chai | 13 | 0.448 | 7/13 | 6/13 | 2/13 | 0.56 | 0.73 |
| protenix | 13 | 0.650 | 11/13 | 10/13 | 4/13 | 0.79 | 0.68 |

## 3. DockQ matrix (best pose)

| target | pep_len | qual | af3 | afmultimer | boltz | chai | protenix | best |
|---|--:|---|--:|--:|--:|--:|--:|--:|
| 4E81 | 10 | ok | 0.90 | 0.93 | - | 0.95 | 0.90 | 0.95 |
| 4EZQ* | 9 | caut | - | 0.59 | - | 0.21 | 0.79 | 0.79 |
| 4EZR | 8 | ok | 0.93 | - | - | 0.92 | 0.91 | 0.93 |
| 4EZS | 8 | ok | 0.29 | 0.29 | - | 0.38 | 0.93 | 0.93 |
| 6HY2 | 12 | ok | 0.29 | 0.39 | 0.93 | 0.21 | 0.69 | 0.93 |
| 3QRX* | 26 | caut | 0.53 | - | - | 0.23 | 0.39 | 0.53 |
| 4EZO* | 15 | caut | 0.71 | - | - | 0.69 | 0.75 | 0.75 |
| 4EZU | 17 | ok | 0.08 | - | - | 0.09 | 0.18 | 0.18 |
| 6Z2P* | 19 | caut | 0.14 | 0.17 | - | 0.07 | 0.77 | 0.77 |
| 7SAY | 37 | ok | - | - | - | 0.07 | 0.01 | 0.07 |
| 8AHT | 26 | ok | 0.40 | - | - | 0.55 | 0.66 | 0.66 |
| 4JWC* | 16 | caut | 0.67 | - | - | 0.69 | 0.65 | 0.69 |
| 8GAL | 20 | ok | - | 0.75 | - | 0.79 | 0.83 | 0.83 |

## 4. Insights

**Overall ranking (mean DockQ over each method's scored targets — not the same target set for every method yet, so treat as indicative):**

- boltz: 0.928  (n=1)
- protenix: 0.650  (n=13)
- afmultimer: 0.520  (n=6)
- af3: 0.495  (n=10)
- chai: 0.448  (n=13)

**Does the tools' own confidence predict DockQ accuracy?** Pooled Spearman(rank_score, DockQ) = **0.69** over 41 predictions. Per-method values are in section 2. A high positive value means the tool's self-reported confidence is a usable filter for which predictions to trust.

**Hardest targets (lowest *best-of-all-methods* DockQ):**

- 7SAY (LL-37, the canonical human cathe): best 0.07, mean 0.04 over 2 methods — quality ok, 35/37 resolved
- 4EZU ('PR-bombesin' from Bombina maxim): best 0.18, mean 0.12 over 3 methods — quality ok, 14/17 resolved
- 3QRX (Melittin (different host-protein): best 0.53, mean 0.38 over 3 methods — quality caution, 20/26 resolved
- 8AHT (Melittin (bee venom AMP)): best 0.66, mean 0.54 over 3 methods — quality ok, 25/26 resolved
- 4JWC (Cathelicidin-3/Bac7-type (Bos ta): best 0.69, mean 0.67 over 3 methods — quality caution, 9/16 resolved
- 4EZO (PR-39 antibacterial protein): best 0.75, mean 0.72 over 3 methods — quality caution, 8/15 resolved

**Peptide length vs DockQ:** Spearman = **-0.43** over 43 predictions (negative = longer peptides score worse).

**Caveats:**
- `caution` targets (6Z2P, 4JWC, 4EZQ, 4EZO, 3QRX) have a partly-unresolved native peptide, so DockQ scores them over a fragment — weaker evidence, marked * in section 3.
- 4JWD (Cathelicidin-3 fragment / DnaK) is **dropped from the benchmark**: its 7 resolved peptide residues sit ~6 Å from the receptor, so the native has no interface and DockQ cannot score it (see `configs/targets.yaml`, DROPPED section E).
- AlphaFold-Multimer confidence is only `iptm+ptm` (combined); ptm/iptm not reported separately by that pipeline.
- Method means are over different target subsets until every method has run on all included targets.
