# 6HY2 DiffPepDock input

This directory is the receptor-only input for a blind DiffPepDock run. It is
generated reproducibly from the deposited 6HY2 structure with:

- receptor: author chain `X` (E. coli LpxA), 262 residues;
- peptide: CR20, `WMLDPIAGKWSR` (12 residues);
- no native peptide, waters, or other heteroatoms in `6HY2.pdb`.

Regenerate and validate it from the repository root:

```powershell
./scripts/prepare_6hy2_docking_input.ps1
./scripts/test_6hy2_docking_input.ps1
```

Preprocess it with the verified DiffPepBuilder interface (run from the
DiffPepBuilder checkout after its environment and model resources are installed):

```powershell
python experiments/process_batch_dock.py `
  --pdb_dir ../6HY2_docking_input/diffpepdock `
  --write_dir ../6HY2_preprocessed `
  --receptor_info_path ../6HY2_docking_input/diffpepdock/receptor_info.json `
  --peptide_seq_path ../6HY2_docking_input/diffpepdock/peptides.fasta
```

The generated `6HY2_preprocessed/` directory is intentionally git-ignored.
