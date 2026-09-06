# Re-ranking evaluation — headroom only

_generated 2026-09-06 13:15 UTC_

41 ensembles (method x target), decoys per ensemble from each docker's own multi-model output. **docker_top1** = the docker's rank-1 pose; **oracle** = best DockQ in the ensemble; **reranker_top1** = the pose `interpeprank` scores best. CAPRI counts shown as ≥acceptable / ≥medium / ≥high.

> No `rerank/<method>/<ID>/interpeprank.csv` score files found yet — showing docker-vs-oracle **headroom** only. Add the re-ranker's scores and re-run to fill the reranker columns.

## By method

| method | n | docker_top1 mean | oracle mean | headroom |
|---|--:|--:|--:|--:|
| af3 | 10 | 0.495 | 0.672 | +0.177 |
| afmultimer | 4 | 0.551 | 0.633 | +0.082 |
| boltz | 1 | 0.928 | 0.928 | +0.000 |
| chai | 13 | 0.448 | 0.562 | +0.114 |
| protenix | 13 | 0.650 | 0.665 | +0.016 |
| **all** | 41 | 0.545 | 0.637 | +0.092 |

## CAPRI bands captured (≥acceptable / ≥medium / ≥high)

| strategy | count |
|---|---|
| docker_top1 | 31/41  24/41  10/41 |
| oracle | 37/41  29/41  13/41 |

## Per ensemble

| method | target | qual | n | docker_top1 | oracle (rank) | headroom |
|---|---|---|--:|--:|--:|--:|
| af3 | 6Z2P | caut | 5 | 0.142 | 0.837 (#2) | +0.695 |
| af3 | 6HY2 | ok | 5 | 0.289 | 0.846 (#4) | +0.558 |
| af3 | 4EZS | ok | 5 | 0.287 | 0.681 (#2) | +0.394 |
| af3 | 4E81 | ok | 5 | 0.904 | 0.939 (#4) | +0.035 |
| af3 | 4EZO | caut | 5 | 0.711 | 0.740 (#2) | +0.029 |
| af3 | 4EZR | ok | 5 | 0.934 | 0.952 (#2) | +0.017 |
| af3 | 3QRX | caut | 5 | 0.525 | 0.540 (#1) | +0.015 |
| af3 | 4EZU | ok | 5 | 0.084 | 0.099 (#2) | +0.015 |
| af3 | 4JWC | caut | 5 | 0.672 | 0.681 (#2) | +0.009 |
| af3 | 8AHT | ok | 5 | 0.404 | 0.404 (#0) | +0.000 |
| afmultimer | 6HY2 | ok | 5 | 0.395 | 0.554 (#1) | +0.160 |
| afmultimer | 4EZS | ok | 5 | 0.294 | 0.432 (#3) | +0.138 |
| afmultimer | 4EZQ | caut | 5 | 0.587 | 0.617 (#3) | +0.031 |
| afmultimer | 4E81 | ok | 5 | 0.930 | 0.930 (#0) | +0.000 |
| boltz | 6HY2 | ok | 5 | 0.928 | 0.928 (#0) | +0.000 |
| chai | 4EZQ | caut | 5 | 0.210 | 0.824 (#4) | +0.614 |
| chai | 6Z2P | caut | 5 | 0.070 | 0.451 (#4) | +0.381 |
| chai | 4EZU | ok | 5 | 0.090 | 0.293 (#4) | +0.203 |
| chai | 6HY2 | ok | 5 | 0.206 | 0.367 (#1) | +0.162 |
| chai | 4EZO | caut | 5 | 0.688 | 0.729 (#4) | +0.041 |
| chai | 4EZS | ok | 5 | 0.375 | 0.410 (#1) | +0.035 |
| chai | 3QRX | caut | 5 | 0.228 | 0.249 (#3) | +0.022 |
| chai | 4E81 | ok | 5 | 0.946 | 0.961 (#1) | +0.014 |
| chai | 4JWC | caut | 5 | 0.685 | 0.691 (#3) | +0.006 |
| chai | 4EZR | ok | 5 | 0.919 | 0.924 (#1) | +0.005 |
| chai | 7SAY | ok | 5 | 0.068 | 0.068 (#3) | +0.000 |
| chai | 8AHT | ok | 5 | 0.550 | 0.550 (#0) | +0.000 |
| chai | 8GAL | ok | 5 | 0.786 | 0.786 (#0) | +0.000 |
| protenix | 6HY2 | ok | 5 | 0.685 | 0.787 (#1) | +0.102 |
| protenix | 7SAY | ok | 5 | 0.014 | 0.057 (#1) | +0.043 |
| protenix | 3QRX | caut | 5 | 0.389 | 0.408 (#2) | +0.020 |
| protenix | 6Z2P | caut | 5 | 0.769 | 0.782 (#3) | +0.014 |
| protenix | 4JWC | caut | 5 | 0.653 | 0.663 (#1) | +0.010 |
| protenix | 4E81 | ok | 5 | 0.898 | 0.906 (#2) | +0.008 |
| protenix | 4EZR | ok | 5 | 0.909 | 0.917 (#2) | +0.007 |
| protenix | 4EZO | caut | 5 | 0.750 | 0.750 (#0) | +0.000 |
| protenix | 4EZQ | caut | 5 | 0.793 | 0.793 (#0) | +0.000 |
| protenix | 4EZS | ok | 5 | 0.925 | 0.925 (#0) | +0.000 |
| protenix | 4EZU | ok | 5 | 0.178 | 0.178 (#0) | +0.000 |
| protenix | 8AHT | ok | 5 | 0.656 | 0.656 (#0) | +0.000 |
| protenix | 8GAL | ok | 5 | 0.827 | 0.827 (#0) | +0.000 |

---

- **headroom** = oracle − docker_top1: DockQ a perfect re-ranker would add on this ensemble. Mean headroom is the upper bound on what InterPepRank can deliver.
- **win/tie/loss**: reranker_top1 vs docker_top1, tie = within 0.02 DockQ.
- **ρ(score, DockQ)**: Spearman within one ensemble (5 poses) — noisy per row; read the per-method mean.
- 4JWD is excluded (dropped: no native interface). caution targets kept, flagged in the `qual` column.
