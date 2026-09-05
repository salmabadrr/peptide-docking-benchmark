"""Combine DockQ scores + each tool's own confidence + target metadata into one report.

Reads:
  results/summary.csv       (pipeline/run_dockq.py)  -- DockQ per (method, target)
  results/confidences.csv   (pipeline/collect_predictions.py) -- ptm/iptm/ranking_score per (method, target)
  configs/targets.yaml      -- peptide length, resolved fraction, quality, AMP name

Writes:
  results/REPORT.md         -- main results table, per-method summary, per-target
                              matrix, and an insights section (confidence-vs-accuracy
                              correlation, hardest targets, peptide-length effect, caveats)

CPU only, stdlib + pyyaml.
"""
from __future__ import annotations

import csv
import datetime as dt
import re
import statistics as st
from pathlib import Path

import yaml

from config import RESULTS, TARGETS_YAML, capri_class


def read_csv(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def spearman(xs, ys) -> float | None:
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pairs) < 4:
        return None
    xr = _rank([p[0] for p in pairs])
    yr = _rank([p[1] for p in pairs])
    try:
        return round(st.correlation(xr, yr), 2)
    except Exception:  # noqa: BLE001
        return None


def _rank(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    r = [0.0] * len(vals)
    i = 0
    while i < len(vals):
        j = i
        while j + 1 < len(vals) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def amp_name(notes: str) -> str:
    m = re.search(r"peptide\s*=\s*([^.;]+)", notes)
    return (m.group(1).strip() if m else "").split(" -- ")[0][:32]


def main() -> int:
    raw = yaml.safe_load(TARGETS_YAML.read_text(encoding="utf-8"))
    included = {k: v for k, v in raw.items() if v.get("include", True)}

    dq = {(r["method"], r["pdb_id"]): r for r in read_csv(RESULTS / "summary.csv")
          if r.get("rank", "best") == "best"}
    conf = {(r["method"], r["pdb_id"]): r for r in read_csv(RESULTS / "confidences.csv")}

    methods = sorted({m for m, _ in dq} | {m for m, _ in conf})
    targets = sorted(included, key=lambda k: (included[k].get("tier", 9), k))

    L = []
    w = L.append
    w(f"# Benchmark report — DockQ vs. tool confidence\n")
    w(f"_generated {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M UTC}_\n")
    n_pred = len(dq)
    w(f"{n_pred} predictions scored across {len(methods)} methods and "
      f"{len({p for _, p in dq})} of {len(included)} included targets.\n")
    w("`rank_score` = each tool's own headline confidence for the top pose "
      "(AF3/Protenix `ranking_score`, Chai `aggregate_score`, AlphaFold-Multimer "
      "`iptm+ptm`, Boltz `confidence_score`). DockQ: incorrect <0.23, acceptable "
      "0.23–0.49, medium 0.49–0.80, high ≥0.80.\n")

    # ---- Section 1: main table, grouped by target ----
    w("\n## 1. Results by target\n")
    for t in targets:
        d = included[t]
        w(f"\n### {t} — {amp_name(d.get('notes',''))}  ·  peptide {d.get('peptide_length','?')} aa, "
          f"resolved {d.get('peptide_resolved','?')}  ·  quality: {d.get('quality','?')}\n")
        w("| method | DockQ | class | iRMSD | fnat | rank_score | ptm | iptm |")
        w("|---|--:|---|--:|--:|--:|--:|--:|")
        for m in methods:
            r, c = dq.get((m, t)), conf.get((m, t))
            if not r and not c:
                continue
            dv = num(r["dockq"]) if r else None
            dq_s = f"{dv:.3f}" if dv is not None else "-"
            cls = (r["capri_class"] if r and r.get("capri_class")
                   else ("ERROR" if r and r.get("note", "").startswith("ERROR") else "-"))
            irmsd = r["irmsd"] if r and r.get("irmsd") not in (None, "") else "-"
            fnat = r["fnat"] if r and r.get("fnat") not in (None, "") else "-"
            rs = c["ranking_score"] if c and c.get("ranking_score") not in (None, "") else "-"
            ptm = c["ptm"] if c and c.get("ptm") not in (None, "") else "-"
            iptm = c["iptm"] if c and c.get("iptm") not in (None, "") else "-"
            w(f"| {m} | {dq_s} | {cls} | {irmsd} | {fnat} | {rs} | {ptm} | {iptm} |")

    # ---- Section 2: per-method summary ----
    w("\n## 2. By method\n")
    w("| method | n | DockQ mean | ≥acceptable | ≥medium | ≥high | mean rank_score | "
      "Spearman(rank_score, DockQ) |")
    w("|---|--:|--:|--:|--:|--:|--:|--:|")
    for m in methods:
        rows = [(dq.get((m, t)), conf.get((m, t))) for t in targets]
        dvs = [num(r["dockq"]) for r, _ in rows if r and num(r["dockq"]) is not None]
        rss = [num(c["ranking_score"]) if c else None for r, c in rows
               if r and num(r["dockq"]) is not None]
        if not dvs:
            continue
        sp = spearman(rss, dvs)
        w(f"| {m} | {len(dvs)} | {st.mean(dvs):.3f} "
          f"| {sum(v >= 0.23 for v in dvs)}/{len(dvs)} "
          f"| {sum(v >= 0.49 for v in dvs)}/{len(dvs)} "
          f"| {sum(v >= 0.80 for v in dvs)}/{len(dvs)} "
          f"| {st.mean([x for x in rss if x is not None]):.2f} "
          f"| {sp if sp is not None else 'n/a'} |")

    # ---- Section 3: target x method DockQ matrix ----
    w("\n## 3. DockQ matrix (best pose)\n")
    w("| target | pep_len | qual | " + " | ".join(methods) + " | best |")
    w("|---|--:|---|" + "|".join(["--:"] * len(methods)) + "|--:|")
    for t in targets:
        d = included[t]
        cells, vals = [], []
        for m in methods:
            r = dq.get((m, t))
            v = num(r["dockq"]) if r else None
            if v is not None:
                cells.append(f"{v:.2f}")
                vals.append(v)
            else:
                cells.append("ERR" if r and r.get("note", "").startswith("ERROR") else "-")
        star = "*" if d.get("quality") == "caution" else ""
        w(f"| {t}{star} | {d.get('peptide_length','?')} | {d.get('quality','?')[:4]} | "
          + " | ".join(cells) + f" | {max(vals):.2f} |" if vals else
          f"| {t}{star} | {d.get('peptide_length','?')} | {d.get('quality','?')[:4]} | "
          + " | ".join(cells) + " | - |")

    # ---- Section 4: insights ----
    w("\n## 4. Insights\n")
    # overall method ranking
    means = []
    for m in methods:
        dvs = [num(dq[(m, t)]["dockq"]) for t in targets
               if (m, t) in dq and num(dq[(m, t)]["dockq"]) is not None]
        if dvs:
            means.append((m, st.mean(dvs), len(dvs)))
    means.sort(key=lambda x: -x[1])
    w("**Overall ranking (mean DockQ over each method's scored targets — not the same "
      "target set for every method yet, so treat as indicative):**\n")
    for m, mu, n in means:
        w(f"- {m}: {mu:.3f}  (n={n})")

    # confidence vs accuracy, pooled
    allc, alld = [], []
    for (m, t), c in conf.items():
        r = dq.get((m, t))
        if r and num(r["dockq"]) is not None and num(c["ranking_score"]) is not None:
            allc.append(num(c["ranking_score"]))
            alld.append(num(r["dockq"]))
    sp_all = spearman(allc, alld)
    w(f"\n**Does the tools' own confidence predict DockQ accuracy?** Pooled "
      f"Spearman(rank_score, DockQ) = **{sp_all}** over {len(alld)} predictions. "
      "Per-method values are in section 2. A high positive value means the tool's "
      "self-reported confidence is a usable filter for which predictions to trust.")

    # hardest targets
    hard = []
    for t in targets:
        dvs = [num(dq[(m, t)]["dockq"]) for m in methods
               if (m, t) in dq and num(dq[(m, t)]["dockq"]) is not None]
        if dvs:
            hard.append((t, max(dvs), st.mean(dvs), len(dvs)))
    hard.sort(key=lambda x: x[1])
    w("\n**Hardest targets (lowest *best-of-all-methods* DockQ):**\n")
    for t, mx, mu, n in hard[:6]:
        d = included[t]
        w(f"- {t} ({amp_name(d.get('notes',''))}): best {mx:.2f}, mean {mu:.2f} over {n} methods "
          f"— quality {d.get('quality')}, {d.get('peptide_resolved','?')} resolved")

    # peptide length effect
    lp = []
    for (m, t), r in dq.items():
        v = num(r["dockq"])
        pl = included.get(t, {}).get("peptide_length")
        if v is not None and pl:
            lp.append((int(pl), v))
    sp_len = spearman([x[0] for x in lp], [x[1] for x in lp])
    w(f"\n**Peptide length vs DockQ:** Spearman = **{sp_len}** over {len(lp)} predictions "
      f"(negative = longer peptides score worse).")

    # errors / caveats
    errs = [(m, t) for (m, t), r in dq.items() if r.get("note", "").startswith("ERROR")]
    if errs:
        w("\n**DockQ could not score:**\n")
        for m, t in sorted(errs):
            w(f"- {m}/{t}: {dq[(m,t)]['note']}")
    w("\n**Caveats:**")
    w("- `caution` targets (6Z2P, 4JWC, 4JWD, 4EZQ, 4EZO, 3QRX) have a partly-unresolved "
      "native peptide, so DockQ scores them over a fragment — weaker evidence, marked * in section 3.")
    w("- 4JWD: the 7 resolved peptide residues sit ~6 Å from the receptor (no contact), so "
      "DockQ finds no native interface at all — this target's reference is effectively unusable; "
      "consider reclassifying it from caution to drop.")
    w("- AlphaFold-Multimer confidence is only `iptm+ptm` (combined); ptm/iptm not reported separately by that pipeline.")
    w("- Method means are over different target subsets until every method has run on all included targets.")

    (RESULTS / "REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {RESULTS / 'REPORT.md'}  ({n_pred} predictions, {len(methods)} methods)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
