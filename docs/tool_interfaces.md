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

### Official repository / source
- Official source: `https://bitbucket.org/isaakh94/interpeprank/src/master/`
- The official README and `environment.yml` are hosted in the repository root.

### Installation procedure
- Install system dependencies:
  - `sudo apt install graphviz libgraphviz-dev libgraph6`
- Build the contact map library:
  - `cd contact_map`
  - `make`
  - `./make_lib.sh`
- Create and activate the conda environment:
  - `conda env create -f environment.yml`
  - `conda activate interpeprank`

### Dependencies
- Conda environment includes:
  - `python=3.7.6`
  - `tensorflow-gpu=1.14.0`
  - `keras-gpu=2.2.4`
  - `numpy=1.18.1`
  - `pandas=0.24.2`
  - `scikit-learn=0.20.3`
  - `scipy=1.2.1`
  - `h5py`, `protobuf`, `tensorflow-estimator`, and associated GPU packages
- Pip dependencies include:
  - `pygraphviz`, `networkx`, `spektral`, `requests`
- System-level dependencies include `graphviz`, `libgraphviz-dev`, and `libgraph6`.

### Python / environment requirements
- Requires Python 3.7, as specified exactly in `environment.yml`.
- Uses TensorFlow 1.14 GPU build and associated CUDA toolkit packages, indicating a GPU-capable environment.

### CLI / interface
- Create graph representations for a batch of models:
  - `scripts/create_graphrep.py example/example_list.txt example/receptor.psi example/peptide.fa -r example/receptor.pdb`
- Apply trained networks to make predictions:
  - `scripts/apply_nets.py test.h5 example/example_list.txt --basetargets`

### Required input files
- A list of PDB files describing candidate models (`example/example_list.txt`).
- A peptide FASTA file (`example/peptide.fa`).
- A receptor MSA in `.psi` format (`example/receptor.psi`).
- A receptor PDB file (`example/receptor.pdb`).

### Output files
- Prediction output is written to `ipr_out.csv`.
- Example outputs can be compared against `example/expected_output.csv`.

### Scoring method
- The exact score computation is not explicitly documented in the available README.
- The tool produces InterPepRank predictions, but the scoring formula and meaning of the numeric output are unverified from the current documentation.

### Whether higher or lower scores are better
- Not explicitly documented in the README.
- This is unverified and must be confirmed from the tool documentation or publication.

### How multiple docking poses can be processed
- `scripts/create_graphrep.py` is described as processing a batch of models with the same receptor and peptide.
- This implies multiple docking poses can be handled together via a model list file.

### Batch-processing capability
- Yes. The official README explicitly describes batch processing using `scripts/create_graphrep.py` on a list of models.

### CPU / GPU requirements
- The environment file includes `tensorflow-gpu=1.14.0` and `cudatoolkit=10.1`, indicating GPU support is expected.
- Explicit CPU-only execution is not documented in the README.

### Preprocessing requirements
- Requires receptor MSA generation before scoring:
  - `hhblits -i <receptor_sequence> -opsi <psi_file> -all -n 2`
- Requires graph representation creation via `scripts/create_graphrep.py` before `scripts/apply_nets.py`.

### Whether input structures are modified
- The documentation does not indicate any modification of original input PDB files.
- This is treated as unverified but likely read-only.

### Programmatic parsing
- Prediction results are written as CSV (`ipr_out.csv`), which can be parsed programmatically.
- No additional structured output format is documented in the README.

## DockQ

### Official repository / source
- Official source: `https://github.com/wallnerlab/DockQ`
- The official README and `pyproject.toml` are hosted in the repository root.

### Installation procedure
- Install from PyPI:
  - `pip install DockQ`
- Or clone and install locally:
  - `git clone https://github.com/bjornwallner/DockQ/`
  - `cd DockQ`
  - `pip install .`

### Dependencies
- Python package dependencies from `pyproject.toml`:
  - `numpy < 2.0`
  - `biopython >= 1.79`
  - `networkx`
  - `parallelbar`
- Build requirements include:
  - `setuptools>=68`
  - `cython`
  - `numpy < 2.0`

### Python / environment requirements
- Requires Python `>=3.8`, as specified in `pyproject.toml`.

### CLI / interface
- Basic command:
  - `DockQ <model> <native>`
- Common flags:
  - `--short`
  - `--verbose`, `-v`
  - `--no_align`
  - `--n_cpu CPU`
  - `--max_chunk CHUNK`
  - `--optDockQF1`
  - `--allowed_mismatches ALLOWED_MISMATCHES`
  - `--mapping MODELCHAINS:NATIVECHAINS`
  - `--small_molecule`
  - `--capri_peptide`
  - `--json filename.json`

### Required input files
- A model structure file (`model`), typically PDB or mmCIF.
- A native/reference structure file (`native`), typically PDB or mmCIF.

### Output files
- Standard output text with per-interface DockQ results.
- Optional JSON output via `--json filename.json`.

### Scoring method
- DockQ computes a score based on interface RMSD metrics and contact metrics, including:
  - `iRMSD`
  - `LRMSD`
  - `fnat`
  - `fnonnat`
  - `F1`
- The score is a continuous quality measure as defined by the DockQ paper.

### Whether higher or lower scores are better
- Higher scores are better.
- The README legend explicitly defines quality ranges:
  - `0.00 <= DockQ < 0.23` - Incorrect
  - `0.23 <= DockQ < 0.49` - Acceptable quality
  - `0.49 <= DockQ < 0.80` - Medium quality
  - `DockQ >= 0.80` - High quality

### How multiple docking poses can be processed
- The README documents evaluation of a single model/native pair per invocation.
- Multiple poses would need to be handled by repeated calls or external scripting; batch CLI support is not explicitly documented.

### Batch-processing capability
- Not explicitly documented as a built-in DockQ feature.
- A batch workflow is likely implemented externally by looping over pose files.

### CPU / GPU requirements
- DockQ supports a CPU-based workflow and includes `--n_cpu` for parallel processing.
- No GPU requirements are documented in the README.

### Preprocessing requirements
- No preprocessing is explicitly required beyond having prepared model and native structure files.
- Optional chain mapping can be provided to guide interface matching.

### Whether input structures are modified
- The documentation does not indicate any modification of input structure files.
- This is treated as read-only scoring.

### Programmatic parsing
- JSON output is available via `--json filename.json`.
- The tool can also be imported as a Python module:
  - `from DockQ.DockQ import load_PDB, run_on_all_native_interfaces`
- Programmatic execution can return results dictionaries from Python API calls.

## Notes
- This summary is based on the DiffPepBuilder/DiffPepDock official README, the DockQ official GitHub repository, and the InterPepRank official Bitbucket repository.
- DiffPepDock details are confirmed from the official DiffPepBuilder documentation.
- InterPepRank and DockQ interface details are verified from their official repositories; unverified fields are explicitly noted.
