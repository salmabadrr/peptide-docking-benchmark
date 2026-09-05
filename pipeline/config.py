"""Shared config: load the frozen target list and expose repo paths."""
from __future__ import annotations

import pathlib
from dataclasses import dataclass, field

import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
TARGETS_YAML = REPO / "configs" / "targets.yaml"

DATA = REPO / "data"
NATIVES = DATA / "natives"          # <ID>_assembly.cif (raw) + <ID>_native.pdb (reduced)
SEQUENCES = DATA / "sequences"      # <ID>_receptor.fasta / _peptide.fasta / _complex.fasta
INPUTS = REPO / "inputs"            # inputs/<method>/<ID>.<ext>
PREDICTIONS = REPO / "predictions"  # predictions/<method>/<ID>.pdb
RESULTS = REPO / "results"

RCSB_FASTA = "https://www.rcsb.org/fasta/entry/{pdb_id}/display"
RCSB_ASSEMBLY_CIF = "https://files.rcsb.org/download/{pdb_id}-assembly{n}.cif"
RCSB_ENTRY_CIF = "https://files.rcsb.org/download/{pdb_id}.cif"


@dataclass
class Target:
    pdb_id: str
    receptor_chains: list[str]
    peptide_chains: list[str]
    peptide_length: int
    topology: str = "unknown"
    native_source: str = "assembly1"
    native_receptor: list[str] = field(default_factory=list)
    native_peptide: list[str] = field(default_factory=list)
    tier: int = 99
    quality: str = "unknown"        # ok | caution | drop
    include: bool = True
    report_separately: bool = False
    notes: str = ""
    source: str = "AMP data edited.xlsx"   # or "rcsb_discovery" for discover_targets.py finds

    @property
    def assembly_n(self) -> int:
        """Assembly number from native_source, e.g. 'assembly1' -> 1."""
        digits = "".join(c for c in self.native_source if c.isdigit())
        return int(digits) if digits else 1


def _clean_id(raw: str) -> str:
    return raw.strip().strip("\xa0").upper()


# CAPRI quality bands from a DockQ score (standard thresholds). Single source of
# truth -- imported by run_dockq.py and aggregate.py.
CAPRI_BANDS = (("high", 0.80), ("medium", 0.49), ("acceptable", 0.23))


def capri_class(dockq: float) -> str:
    for name, lo in CAPRI_BANDS:
        if dockq >= lo:
            return name
    return "incorrect"


def load_targets(path: pathlib.Path | None = None) -> dict[str, Target]:
    path = path or TARGETS_YAML
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    out: dict[str, Target] = {}
    for pdb_id, d in raw.items():
        pid = _clean_id(pdb_id)
        nc = d.get("native_chains") or {}
        out[pid] = Target(
            pdb_id=pid,
            receptor_chains=[str(c) for c in d["receptor_chains"]],
            peptide_chains=[str(c) for c in d["peptide_chains"]],
            peptide_length=int(d["peptide_length"]),
            topology=d.get("topology", "unknown"),
            native_source=d.get("native_source", "assembly1"),
            native_receptor=[str(c) for c in nc.get("receptor", [])] or [str(d["receptor_chains"][0])],
            native_peptide=[str(c) for c in nc.get("peptide", [])] or [str(d["peptide_chains"][0])],
            tier=int(d.get("tier", 99)),
            quality=str(d.get("quality", "unknown")),
            include=bool(d.get("include", True)),
            report_separately=bool(d.get("report_separately", False)),
            notes=d.get("notes", ""),
            source=d.get("source", "AMP data edited.xlsx"),
        )
    return out


def select(targets: dict[str, Target], only: list[str] | None, tiers: list[int] | None,
           included_only: bool = True) -> list[Target]:
    """Filter helper shared by the CLI scripts.

    By default returns only `include: true` targets. An explicit --only list
    overrides that (so you can still prep/inspect a dropped target by name).
    """
    items = list(targets.values())
    if only:
        want = {_clean_id(x) for x in only}
        items = [t for t in items if t.pdb_id in want]
    else:
        if included_only:
            items = [t for t in items if t.include]
        if tiers:
            items = [t for t in items if t.tier in set(tiers)]
    return sorted(items, key=lambda t: (t.tier, t.pdb_id))


if __name__ == "__main__":
    ts = load_targets()
    inc = [t for t in ts.values() if t.include]
    for t in sorted(ts.values(), key=lambda x: (x.tier, x.pdb_id)):
        flag = "" if t.include else "  [DROPPED]"
        print(f"tier {t.tier}  {t.pdb_id:5s} {t.quality:8s} rec={t.native_receptor} "
              f"pep={t.native_peptide} len={t.peptide_length} {t.topology}{flag}")
    print(f"\n{len(inc)} included / {len(ts)} total")
