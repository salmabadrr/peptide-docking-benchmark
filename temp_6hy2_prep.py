from pathlib import Path
import json
from Bio.PDB import MMCIFParser, PDBIO, Select, PDBParser
from Bio.Data.IUPACData import protein_letters_3to1

out_dir = Path('6HY2_docking_input')
out_dir.mkdir(exist_ok=True)

parser = MMCIFParser(QUIET=True)
structure = parser.get_structure('6HY2', '6HY2.cif')
model = structure[0]

if 'X' not in model:
    raise SystemExit('Receptor chain X not found in 6HY2.cif')
if 'A' not in model:
    raise SystemExit('Peptide chain A not found in 6HY2.cif')

peptide_residues = []
for res in model['A']:
    if 'CA' in res and res.get_resname().upper() in protein_letters_3to1:
        peptide_residues.append(protein_letters_3to1[res.get_resname().upper()])
peptide_seq = ''.join(peptide_residues)
if len(peptide_seq) == 0:
    raise SystemExit('No peptide sequence extracted from chain A')

fasta_path = out_dir / '6HY2_peptide_A.fasta'
with fasta_path.open('w', encoding='utf-8') as fh:
    fh.write(f'>6HY2_A\n{peptide_seq}\n')

class ChainXSelect(Select):
    def accept_chain(self, chain):
        return chain.id == 'X'

receptor_pdb_path = out_dir / '6HY2_receptor_X.pdb'
io = PDBIO()
io.set_structure(structure)
io.save(str(receptor_pdb_path), ChainXSelect())

receptor_info_path = out_dir / '6HY2_receptor_info.json'
with receptor_info_path.open('w', encoding='utf-8') as fh:
    json.dump({'6HY2': {'lig_chain': 'A'}}, fh, indent=2)

pdb_parser = PDBParser(QUIET=True)
receptor_struct = pdb_parser.get_structure('6HY2_receptor', str(receptor_pdb_path))
chain_ids = [chain.id for chain in receptor_struct[0].get_chains()]

print('created', receptor_pdb_path)
print('created', fasta_path)
print('created', receptor_info_path)
print('peptide_seq', peptide_seq)
print('peptide_length', len(peptide_seq))
print('receptor_chains', chain_ids)
