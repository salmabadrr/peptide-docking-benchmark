# Tool Interfaces

This document summarizes verified interfaces for DiffPepDock, InterPepRank, and DockQ based on the information currently available in the repository and official DiffPepBuilder/DiffPepDock documentation.

## DiffPepDock

### Official repository / source
- Official source: `https://github.com/YuzheWangPKU/DiffPepBuilder`
- The official README documents DiffPepDock within the DiffPepBuilder repository.

### Installation requirements
- Clone the repository and use the provided `environment.yml` to create a conda environment.
- Example commands from the official README:
  - `conda env create -f environment.yml`
  - `conda activate diffpepbuilder`
- Postprocessing requires PyRosetta.
  - The README recommends installing a prebuilt PyRosetta wheel, e.g. `pyrosetta-2024.39+release.59628fb-cp39-cp39-linux_x86_64.whl`.
- Model weights for docking must be downloaded from Zenodo and placed in `experiments/checkpoints/diffpepdock_v1.pth`.

### Python / environment requirements
- Uses a conda-managed Python environment from `environment.yml`.
- The provided PyRosetta example wheel targets Python 3.9 (`cp39`) and Linux x86_64.
- Uses PyTorch and Hydra-based scripts.

### Command-line interface
- Preprocess docking inputs:
  - `python experiments/process_batch_dock.py --pdb_dir examples/docking_data --write_dir data/docking_data --receptor_info_path examples/docking_data/docking_cases.json --peptide_seq_path examples/docking_data/peptide_seq.fasta`
- Run docking inference:
  - `export BASE_PATH="your/path/to/DiffPepBuilder"`
  - `torchrun --nproc-per-node=8 experiments/run_docking.py data.val_csv_path=data/docking_data/metadata_test.csv`
- Run postprocessing separately:
  - `export BASE_PATH="your/path/to/DiffPepBuilder"`
  - `python experiments/run_postprocess.py --in_pdbs runs/docking --ori_pdbs examples/docking_data --amber_relax --rosetta_relax`
- Optional postprocessing flag:
  - `--save_best` to record only top-ranked poses in the summary.

### Required input files
- Preprocessing requires:
  - `--pdb_dir` directory with receptor and peptide structures.
  - `--write_dir` output directory for preprocessed data.
  - `--receptor_info_path` JSON file describing reference ligands, binding motifs, or peptide chain information.
  - `--peptide_seq_path` FASTA file of peptide sequences for docking.
- Docking inference requires a metadata CSV produced by preprocessing, e.g. `data/docking_data/metadata_test.csv`.
- Model weights are required in `experiments/checkpoints/`.

### Output files
- Docking inference outputs generated protein-peptide complexes under `runs/docking/`.
- Postprocessing outputs a summary CSV at `runs/docking/postprocess_results.csv`.
- `--save_best` can restrict postprocessing summary output to top-ranked poses.

### How multiple poses are represented
- The README states that DiffPepDock generates protein-peptide complexes and saves them to `runs/docking/`.
- The exact representation of multiple docking poses is not explicitly documented in the available README.

### How scores are reported
- Postprocessing calculates binding ddG values and summarizes them in `runs/docking/postprocess_results.csv`.
- The README does not explicitly document the exact ranking score(s) used by the original DiffPepDock inference step beyond postprocessing output.

### Batch execution support
- Yes. The official README describes automated scripts for docking batches of peptide sequences.

### GPU / CPU requirements
- DiffPepDock docking inference uses `torchrun` and the official config includes `use_gpu=true`.
- GPU use is expected for docking inference.
- Postprocessing requires PyRosetta and may be more CPU-bound, but the README does not explicitly specify hardware requirements for that stage.

### Whether the tool modifies input structures
- The workflow writes preprocessed data to `data/docking_data/` and docking outputs to `runs/docking/`.
- There is no evidence in the available documentation that original source PDBs are overwritten.
- The README does note file naming conventions and input preprocessing requirements.

### Preprocessing required
- Yes. `experiments/process_batch_dock.py` is required to preprocess receptor data, docking cases, and peptide sequences before docking inference.
- This preprocessing produces the metadata CSV used by `experiments/run_docking.py`.

## InterPepRank

### Verified repository / source
- Not verified from the current workspace or the available repository documentation.
- No official InterPepRank GitHub repo or README is present in this repository.

### Verified interface information
- Missing or unverified from available sources:
  - installation requirements
  - Python/environment requirements
  - command-line interface
  - required input files
  - output files
  - representation of multiple poses
  - score reporting format
  - batch execution support
  - GPU/CPU requirements
  - whether the tool modifies input structures
  - preprocessing requirements

## DockQ

### Verified repository / source
- Not verified from the current workspace or the available repository documentation.
- No official DockQ GitHub repo or README is present in this repository.

### Verified interface information
- Missing or unverified from available sources:
  - installation requirements
  - Python/environment requirements
  - command-line interface
  - required input files
  - output files
  - representation of multiple poses
  - score reporting format
  - batch execution support
  - GPU/CPU requirements
  - whether the tool modifies input structures
  - preprocessing requirements

## Notes
- This summary is based only on the DiffPepBuilder/DiffPepDock official README and the repository contents currently available in the workspace.
- InterPepRank and DockQ interfaces must be confirmed from their official documentation or repositories before implementation.
