#!/usr/bin/awk -f
# Minimal PDB -> 1-letter sequence, FASTA-ish (">seq" header + one sequence line).
# GraphPep v1.1's bin/pre.py shells out to `getseq.awk <pdb>` but the released
# package is missing this file; this is a drop-in. One residue per (chain,resSeq,
# iCode) first occurrence; first model only.
BEGIN {
    m["ALA"]="A"; m["ARG"]="R"; m["ASN"]="N"; m["ASP"]="D"; m["CYS"]="C";
    m["GLN"]="Q"; m["GLU"]="E"; m["GLY"]="G"; m["HIS"]="H"; m["ILE"]="I";
    m["LEU"]="L"; m["LYS"]="K"; m["MET"]="M"; m["PHE"]="F"; m["PRO"]="P";
    m["SER"]="S"; m["THR"]="T"; m["TRP"]="W"; m["TYR"]="Y"; m["VAL"]="V";
    m["MSE"]="M"; m["SEC"]="U"; m["HYP"]="P"; m["PYL"]="K";
    seq=""; prev="";
    print ">seq";
}
/^ENDMDL/ { exit }
/^ATOM/ || /^HETATM/ {
    resn=substr($0,18,3); gsub(/ /,"",resn);
    key=substr($0,22,1) substr($0,23,4) substr($0,27,1);
    if (key != prev) {
        aa=m[resn]; if (aa=="") aa="X";
        seq=seq aa;
        prev=key;
    }
}
END { print seq }
