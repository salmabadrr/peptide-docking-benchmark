# Third-Party Tool Modifications

## Purpose

This document maintains a **complete and reproducible record** of every modification made to any third-party docking, preprocessing, inference, scoring, or evaluation tool used in the EPIC-AMP benchmark.

Each modification is documented with:
- The exact problem that necessitated the change
- Original behavior and modified behavior
- Exact line numbers and code changes (via `git diff`)
- Verification results from both original and patched implementations
- Scientific impact assessment
- Whether the modification affects benchmark reproducibility

**CRITICAL RULE**: No modification to any third-party tool shall be made without documenting it in this file **before** results are generated or committed.

---

## Modification Summary

| Tool | File | Type | Reason | Scientific Impact | Status |
|------|------|------|--------|-------------------|--------|
| DiffPepBuilder | `experiments/preprocess_utils.py` | Robustness fix | Missing CA atom handling | Preprocessing only (no change to docking/inference) | ✓ Verified & Necessary |

---

## DiffPepBuilder

### Repository & Version

| Property | Value |
|----------|-------|
| **Tool Name** | DiffPepBuilder |
| **Source** | https://github.com/YuzheWangPKU/DiffPepBuilder.git |
| **Current Commit** | `c19eb4f` (Oct 24: Fix bug in sampling number specification) |
| **Clone Location** | `DiffPepBuilder/` (nested in EPIC-AMP workspace) |

### Modified File

**Path**: `DiffPepBuilder/experiments/preprocess_utils.py`

**Function**: `get_motif_center_pos()`

**Purpose**: Unified coordinate extraction and residue selection for ligand, hotspot, and motif modes.

### Problem

The original implementation in DiffPepBuilder's `get_motif_center_pos()` function unconditionally accesses the CA (alpha carbon) atom from every residue in the structure without verifying:

1. Whether the residue has a CA atom
2. Whether the residue is in the standard insertion position (alternate location code)
3. Whether the residue is a standard protein residue

When processing the `6HY2` PDB structure, certain residues lacked CA atoms, causing a `KeyError: 'CA'` exception during preprocessing.

### Original Behavior

The original implementation attempted to access `r["CA"]` directly:

```python
# Original line ~305:
rec_residues = [r for r in struct.get_residues() if r.parent.id != lig_chain_str]

# Original line ~310:
lig_ca = [
    r["CA"].coord for r in struct.get_residues() if r.parent.id == lig_chain_str
]

# Original lines ~325 and ~331:
ref_coords_ca = [r["CA"].coord for r in ref_struct.get_residues()]

# Original line ~344-345:
ref_coords_ca = [
    r["CA"].coord for r in struct.get_residues() if r.parent.id != lig_chain_str
]
```

**Result on 6HY2**: `KeyError: 'CA'` when Bio.PDB encounters a residue without a CA atom.

### Modification

Added explicit checks before accessing CA atoms. The modification filters residues by:

- `r.id[0] == " "` — Selects only residues in the standard insertion position (insertion code is space)
- `"CA" in r` — Verifies the CA atom exists before attempting to access it

### Exact Lines Changed

**Git diff details:**

```
File: experiments/preprocess_utils.py
Index: 5980686..c50bd9a 100644 (mode unchanged)
```

| Original Line(s) | Modified Line(s) | Change |
|------------------|------------------|--------|
| 305 | 305–307 | `rec_residues` list comprehension: Added `and r.id[0] == " " and "CA" in r` filters |
| 310 | 312–314 | Ligand CA selection: Added `and r.id[0] == " " and "CA" in r` filters |
| 325 | 329 | Hotspots ref_coords: Added `if "CA" in r` filter |
| 331 | 336 | Motif ref_coords: Added `if "CA" in r` filter |
| 344–345 | 348–350 | Fallback ref_coords: Added `and r.id[0] == " " and "CA" in r` filters |

**Complete diff** (5 locations modified):

```diff
@@ -300,16 +300,20 @@ def get_motif_center_pos(
         seq_rec.append(res_short)
         chain_id_rec.append(res.parent.id)
         mask_rec.append(0.0)
     mask_rec = np.array(mask_rec, dtype=float)
 
-    rec_residues = [r for r in struct.get_residues() if r.parent.id != lig_chain_str]
+    rec_residues = [
+        r for r in struct.get_residues() if r.parent.id != lig_chain_str and r.id[0] == " " and "CA" in r
+    ]
     ref_coords_ca, rec_keep = [], []
 
     if lig_chain_str:
         lig_ca = [
-            r["CA"].coord for r in struct.get_residues() if r.parent.id == lig_chain_str
+            r["CA"].coord
+            for r in struct.get_residues()
+            if r.parent.id == lig_chain_str and r.id[0] == " " and "CA" in r
         ]
         if not lig_ca:
             raise errors.DataError(
                 f"Specified ligand chain {lig_chain_str} not found in {os.path.basename(infile)}"
             )
@@ -320,17 +324,17 @@ def get_motif_center_pos(
      elif hotspots:
          io = PDB.PDBIO()
          io.set_structure(struct)
          io.save(out_motif_file, select=ResSelector(hotspots))
          ref_struct = p.get_structure("", out_motif_file)[0]
-        ref_coords_ca = [r["CA"].coord for r in ref_struct.get_residues()]
+        ref_coords_ca = [r["CA"].coord for r in ref_struct.get_residues() if "CA" in r]
      elif motif:
          io = PDB.PDBIO()
          io.set_structure(struct)
          io.save(out_motif_file, select=ResSelector(motif))
          ref_struct = p.get_structure("", out_motif_file)[0]
-        ref_coords_ca = [r["CA"].coord for r in ref_struct.get_residues()]
+        ref_coords_ca = [r["CA"].coord for r in ref_struct.get_residues() if "CA" in r]
 
      if ref_coords_ca:
          for i in ref_coords_ca:
              for k, j in enumerate(rec_residues):
@@ -339,11 +343,13 @@ def get_motif_center_pos(
      else:
          warnings.warn(
              f"No ligand/motif/hotspots for {os.path.basename(infile)}; using whole receptor."
          )
          ref_coords_ca = [
-            r["CA"].coord for r in struct.get_residues() if r.parent.id != lig_chain_str
+            r["CA"].coord
+            for r in struct.get_residues()
+            if r.parent.id != lig_chain_str and r.id[0] == " " and "CA" in r
          ]
          rec_keep = [resid_unique(r) for r in rec_residues]
          mask_rec[:] = 1
 
          io = PDB.PDBIO()
```

### Scientific Impact

**Pipeline Stage**: Preprocessing only (feature extraction and structure analysis)

**Affected Stages**: 
- ✓ Input PDB parsing and chain identification
- ✓ Peptide/ligand sequence extraction
- ✓ Receptor coordinate centering
- ✗ **NOT** Affected: DiffPepBuilder's neural network inference
- ✗ **NOT** Affected: Pose generation or scoring

**Change Type**: Robustness fix with no algorithmic modification

**Does it change results?**: 
- Without patch: 6HY2 preprocessing **fails** → no results possible
- With patch: 6HY2 preprocessing **succeeds** → benchmark can proceed

**Scope**: General robustness enhancement (applies to any PDB with non-standard residues, alternate locations, or missing atoms)

### Verification

#### 1. Original Unmodified Implementation (from Git HEAD)

**Test Method**: Loaded original `preprocess_utils.py` from `HEAD` commit `c19eb4f` using `git show HEAD:experiments/preprocess_utils.py` and tested on 6HY2.

**Input**: `6HY2_docking_input/6HY2.pdb` with `lig_chain_str='A'`

**Result**: **FAILED**

```
Error type: KeyError
Error msg: 'CA'
Location: Line 310 in get_motif_center_pos(), when accessing r["CA"].coord
```

**Error trace**:
```
File "C:\Users\salma\AMP-Benchmarking\EPIC-AMP\.venv\Lib\site-packages\Bio\PDB\Entity.py", line 65, in __getitem__
    return self.child_dict[id]
           ~~~~~~~~~~~~~~~^^^^
KeyError: 'CA'
```

**Conclusion**: Original code cannot preprocess 6HY2.

#### 2. Patched Implementation

**Test Method**: Same input and setup, using the patched version currently in the workspace.

**Input**: `6HY2_docking_input/6HY2.pdb` with `lig_chain_str='A'`

**Result**: **SUCCESS**

**Outputs Generated**:
- `6HY2_preprocessed/6HY2_nat.pkl` — Preprocessed feature dictionary
- `6HY2_preprocessed/metadata_test.csv` — Metadata index

**Verification Details**:

| Property | Value |
|----------|-------|
| PDB Name | 6HY2 |
| Num Chains | 2 (peptide + receptor) |
| Peptide Chain | A |
| Receptor Chain | B |
| Peptide Sequence | WMLDPIAGKWSR |
| Peptide Length | 12 residues |
| Total Modeled Positions | 90 |
| Feature Dictionary | ✓ Successfully pickled (contains aatype, coordinates, masks) |

**Conclusion**: Patched code successfully preprocesses 6HY2 and produces valid outputs.

#### 3. Data Integrity Check

The 6HY2 structure was inspected independently to verify the source of the CA atom issue:

```python
from Bio import PDB
parser = PDB.PDBParser(QUIET=1)
struct = parser.get_structure('x', '6HY2_docking_input/6HY2.pdb')[0]
chain_a = struct['A']

# Verified:
# - Chain A has 32 residues
# - Standard amino acid residues (with CA) are correctly identified
# - Non-standard or alternate-location residues are safely skipped
# - Final peptide sequence matches expected: WMLDPIAGKWSR (12 residues)
```

### Reproducibility

**Target-Specific**: No. The patch is general and applies to any PDB structure with:
- Non-standard residues (e.g., water molecules, ligands, ions)
- Alternate locations (insertion codes other than space)
- Missing atoms in otherwise valid protein residues

**Future Benchmark Runs**: **YES, RETAIN THIS PATCH**

**Rationale**:
1. The original code is demonstrably broken on this dataset
2. The patch is a minimal, defensive change (adds guards, doesn't change logic)
3. The patch enables 6HY2 preprocessing without altering results for well-formed residues
4. Upstream bug: Should be reported/fixed in DiffPepBuilder if not already addressed in later versions

**Version Dependency**: This patch was verified against DiffPepBuilder commit `c19eb4f`. If DiffPepBuilder is updated, re-test this specific function to ensure compatibility.

---

## Future Tool Modifications

### Process for Adding Modifications

When integrating a new third-party tool or making changes to an existing tool:

1. **Before any code modification**:
   - Document the problem statement in this file
   - Record the tool name, version, and source
   - Note the exact file path and line numbers

2. **During modification**:
   - Make minimal, focused changes
   - Add comments explaining the change
   - Keep the modification isolated from benchmark code

3. **After modification**:
   - Document exact changes using `git diff`
   - Record line numbers and before/after code
   - Test both original and modified implementations
   - Document verification results

4. **Before generating results**:
   - Ensure all modifications are documented here
   - Review the "Scientific Impact" section
   - Confirm whether results should be flagged as "using patched tools"

### Template for New Modifications

```markdown
## [Tool Name]

### Repository & Version
- **Source**: [URL]
- **Current Version**: [Commit/Release]

### Modified File
- **Path**: [Relative path in workspace]
- **Function**: [Function name(s) affected]

### Problem
[What broke or needed fixing]

### Original Behavior
[Code snippet]

### Modification
[Code snippet]

### Exact Lines Changed
[Line ranges]

### Scientific Impact
- **Stage**: [Which pipeline stage]
- **Change Type**: [Bug fix / Compatibility / Performance / etc.]
- **Result Changes**: [Yes/No - does it affect benchmark results]

### Verification
[Test results for original and patched versions]

### Reproducibility
- **Target-Specific**: [Yes/No]
- **Retain for Future Runs**: [Yes/No]
- **Rationale**: [Explanation]
```

### Compliance

- **No silent modifications**: Every change to a third-party tool must be documented.
- **Audit trail**: Git history combined with this file provides complete change record.
- **Transparency**: Benchmark results must note when patched versions of tools were used.
- **Verification**: Every modification must have verification results from both original and patched implementations.

---

## Summary of Modifications

**Total Third-Party Tools Cloned**: 1 (DiffPepBuilder)

**Total Tools Modified**: 1 (DiffPepBuilder)

**Total Modifications**: 1 (robustness fix in `preprocess_utils.py`)

**Status**: ✓ All modifications verified and documented

**Impact on Benchmark**: Required for 6HY2 preprocessing; does not affect docking/inference/evaluation stages.

---

**Document Last Updated**: 2026-08-12  
**Verification Commit**: DiffPepBuilder `c19eb4f`  
**Approved for Benchmark**: Yes
