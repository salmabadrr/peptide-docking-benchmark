# EPIC-AMP Peptide-Docking Benchmark — Data Snapshot

_Generated 2026-09-05 11:38 UTC_

Source of truth for the target list: `configs/targets.yaml`. Source of truth for results: `results/summary.csv`. This file is a snapshot for review/sharing — re-run the pipeline and regenerate this file rather than hand-editing it.

**14 of 30** targets considered are in the active benchmark (rest dropped, with reasons, below). **9** (method, target) DockQ scores so far, across **5** methods. Discovery sweep found **8** new targets worth adding out of 77 candidates screened.

---

## 1. Targets (all, included and dropped)

| pdb_id | source | tier | quality | include | topology | peptide_length | peptide_resolved | pep_nonstd | notes |
|---|---|---|---|---|---|---|---|---|---|
| 4E81 | rcsb_discovery | 1 | ok | True | linear | 10 | 9/10 |  | Receptor = DnaK (E. coli); peptide = Apidaecin fragment. Near-duplicate 4F00 (same complex, slightly lower resolved fraction) skipped as redundant. |
| 4EZQ | rcsb_discovery | 1 | caution | True | linear | 9 | 7/9 |  | Receptor = DnaK (E. coli); peptide = Pyrrhocoricin. 78% peptide resolved; report with asterisk. |
| 4EZR | rcsb_discovery | 1 | ok | True | linear | 8 | 8/8 |  | Receptor = DnaK chaperone (E. coli, same family as 4EZS/4JWC/4JWD/4JWI/4EZU/4EZQ/4EZO); peptide = Drosocin. |
| 4EZS | AMP data edited.xlsx | 1 | ok | True | linear | 8 | 8/8 |  | Receptor = DnaK chaperone (E. coli); peptide = Metchnikowin (Drosophila). |
| 6HY2 | AMP data edited.xlsx | 1 | ok | True | linear | 12 | 12/12 |  | Phase-1 pilot. DiffPepBuilder preprocess_utils CA-atom patch applied for this entry. |
| 3QRX | rcsb_discovery | 2 | caution | True | linear | 26 | 20/26 |  | Receptor = Centrin; peptide = Melittin (different host-protein partner than 8AHT). 77% resolved; report with asterisk. |
| 4EZO | rcsb_discovery | 2 | caution | True | linear | 15 | 8/15 |  | Receptor = DnaK (E. coli); peptide = PR-39 antibacterial protein. 53% peptide resolved; report with asterisk. |
| 4EZU | rcsb_discovery | 2 | ok | True | linear | 17 | 14/17 |  | Receptor = DnaK (E. coli); peptide = 'PR-bombesin' from Bombina maxima (frog). Verified via the entry's own (unpublished) citation title: 'Structural studies of DnaK in complex with proline rich antimicrobial peptides' (Zahn & Sträter) -- genuinely antimicrobial despite the hormone-like name. Near-duplicate 4EZV (caution, same complex) skipped as redundant. |
| 6Z2P | AMP data edited.xlsx | 2 | caution | True | linear | 19 | 10/19 |  | Receptor = O-glycan protease (Akkermansia); peptide = Glycodrosocin. Only the central 10 aa (RPYSPRPTSH) ordered. Paired with dropped 6Z2Q. Report with asterisk; verify the ordered stretch covers the interface. |
| 7SAY | rcsb_discovery | 2 | ok | True | linear | 37 | 35/37 |  | Receptor = engineered GCN4/M-protein crystallization scaffold; peptide = LL-37, the canonical human cathelicidin AMP. CAVEAT: receptor is an artificial scaffold, not a natural binding partner -- included to have an LL-37 structure at all; weigh accordingly. |
| 8AHT | rcsb_discovery | 2 | ok | True | linear | 26 | 25/26 |  | Receptor = Calmodulin; peptide = Melittin (bee venom AMP). Near-duplicate 8AHS (same complex, lower resolved fraction) skipped as redundant. |
| 4JWC | AMP data edited.xlsx | 3 | caution | True | linear | 16 | 9/16 |  | Receptor = DnaK (E. coli); peptide = Cathelicidin-3/Bac7-type (Bos taurus). Shares system with 4JWD. 56% of peptide ordered; report with asterisk. |
| 4JWD | AMP data edited.xlsx | 3 | caution | True | linear | 14 | 7/14 |  | Receptor = DnaK (E. coli); peptide = Cathelicidin-3 fragment (Bos taurus). Shares system with 4JWC. 50% of peptide ordered; report with asterisk. |
| 8GAL | AMP data edited.xlsx | 3 | ok | True | linear | 20 | 18/20 |  | Receptor = LptA (E. coli); peptide = Thanatin. Two receptor+peptide copies (A/B and C/D); keep A/B. |
| 2HD4 | rcsb_discovery | 1 | drop | False | linear | 8 | 8/8 |  | DROP (not an AMP): wrongly added as 'lactoferricin-related'. Actual PDB title: 'Crystal structure of proteinase K inhibited by a lactoferrin octapeptide Gly-Asp-Glu-Gln-Gly-Glu-Asn-Lys' -- a generic protease-inhibitor peptide (acidic, no cationic character), unrelated to the antimicrobial lactoferricin region (which is N-terminal and cationic). Caught by user inspection, not by the automated screen. |
| 4JWI | rcsb_discovery | 1 | drop | False | linear | 10 | 8/10 |  | DROP (unencodable residue): receptor = DnaK (E. coli); peptide 'PRPILLPWRX' -- literal X at the C-terminus (likely a modified/amidated residue with no one-letter code). |
| 4N6P | rcsb_discovery | 1 | drop | False | linear | 6 | 6/6 |  | DROP (not an AMP): wrongly added as 'lactoferricin-related'. Actual PDB title: 'Crystal Structure of C-lobe of Bovine lactoferrin complexed with meclofenamic acid' -- the peptide is an incidental C-terminal fragment in a small-molecule drug-binding study, not lactoferricin (which is N-terminal). No mention of antimicrobial activity anywhere in the entry. This was also the representative picked for a 15-way duplicate cluster (3U72,3VDF,4DXU,4FIM,4FJP,4G2Z,4GRK,3V5A,4FOR,3TOD,3U8Q,3UGW,3UK4,3USD,4DIG) -- the whole cluster is therefore not AMP-relevant, not merely redundant. |
| 6Q6W | AMP data edited.xlsx | 1 | drop | False | linear | 12 | 12/12 | DAL;DLE;DLY;DTY | DROP (D-peptide): receptor = LecB fucose-binding lectin (P. aeruginosa); peptide 'SB5' is a fully D-amino-acid synthetic construct (D-Ala/D-Leu/D-Lys/D-Tyr). Sequence-only predictors can only build the L-enantiomer -- not comparable. |
| 6Q77 | AMP data edited.xlsx | 1 | drop | False | linear | 8 | 8/8 | DAL;DLE;DLY | DROP (D-peptide): same LecB receptor; peptide 'SB12' fully D (LKALKKLA, all D). Crashed DockQ (Bio.PDB drops the all-nonstandard chain -> KeyError) during pipeline validation. |
| 7NEF | rcsb_discovery | 1 | drop | False | linear | 12 | 11/12 |  | DROP (unencodable residue): receptor = LecB fucose-binding lectin (P. aeruginosa) -- same receptor as the 5 dropped D-peptide targets. Peptide 'KKLLKLLKLLLX' -- literal X at the C-terminus, same pattern as its D-peptide sibling 7NEW. Confirms it's part of the same synthetic-peptide series, not a usable L-control. |
| 6Z2Q | AMP data edited.xlsx | 2 | drop | False | linear | 19 | 2/19 |  | DROP (disordered): only 2 of 19 peptide residues (TS) modelled. No usable interface. |
| 8GQA | AMP data edited.xlsx | 2 | drop | False | unknown | 20 | 9/20 |  | DROP (disordered): MslA RiPP precursor analog, 4 Cys -- likely macrocyclic. Only 9/20 residues ordered. |
| 8ONU | AMP data edited.xlsx | 2 | drop | False | unknown | 16 | 13/16 | DAB;HYP | DROP (non-standard residues): receptor = LptA (E. coli); peptide is a Thanatin-like derivative containing DAB (2,4-diaminobutyric acid, non-proteinogenic) and HYP (hydroxyproline). RCSB sequence is 'VPITYXNRATXKCARY' -- literal X characters were being written into every tool's input file. |
| 3QNJ | AMP data edited.xlsx | 3 | drop | False | linear | 19 | 8/19 |  | DROP (disordered): Oncocin (Pro-rich AMP) in the DnaK substrate channel; only 8/19 residues ordered. |
| 4JWE | AMP data edited.xlsx | 3 | drop | False | linear | 21 | 9/21 |  | DROP (disordered): same system as 4JWC/4JWD; only 43% of this peptide variant ordered. |
| 6Q85 | AMP data edited.xlsx | 3 | drop | False | linear | 12 | 12/12 | DAL;DLE;DLY;DTY | DROP (D-peptide): same LecB receptor; peptide 'SB11' fully D. Also 4 receptor+peptide copies. |
| 6Q86 | AMP data edited.xlsx | 3 | drop | False | linear | 13 | 13/13 | DAL;DLE;DLY;DTY | DROP (D-peptide): same LecB receptor; peptide 'SB4' fully D. Crashed DockQ during pipeline validation (KeyError, same as 6Q77). |
| 6Y0W | AMP data edited.xlsx | 3 | drop | False | unknown | 14 | 13/14 | DAL;DHI;DLE;DLY;DPN;DTR;DTY | DROP (D-peptide): same LecB receptor; peptide 'cFucRH46D' fully D (7 distinct D-residue types) plus an X in the sequence. Most heavily D-substituted of the set. |
| 6Y0X | AMP data edited.xlsx | 4 | drop | False | unknown | 12 | 5/12 |  | DROP (disordered): 5 receptor chains, 3 peptide copies, flagged 'cyclic' in AMPs.xlsx, only 5/12 ordered. Multiple disqualifiers. |
| 8ITG | AMP data edited.xlsx | 4 | drop | False | linear | 42 | 7/42 |  | DROP (disordered): 42-mer mini-protein; only 7 residues modelled. Also outside the peptide-docking size regime. |

---

## 2. DockQ Results (raw)

| method | pdb_id | tier | quality | rank | dockq | capri_class | irmsd | fnat | note |
|---|---|---|---|---|---|---|---|---|---|
| af3 | 4EZS | 1 | ok | best | 0.2872 | acceptable | 3.009 | 0.184 |  |
| af3 | 6HY2 | 1 | ok | best | 0.2886 | acceptable | 3.275 | 0.125 |  |
| boltz | 6HY2 | 1 | ok | best | 0.9276 | high | 0.507 | 0.9 |  |
| chai | 4EZS | 1 | ok | best | 0.3752 | acceptable | 2.321 | 0.265 |  |
| chai | 6HY2 | 1 | ok | best | 0.2059 | incorrect | 4.578 | 0.2 |  |
| protenix | 4EZS | 1 | ok | best | 0.9254 | high | 0.664 | 0.959 |  |
| protenix | 6HY2 | 1 | ok | best | 0.6853 | medium | 1.464 | 0.7 |  |
| afmultimer | 6Z2P | 2 | caution | best | 0.1705 | incorrect | 4.887 | 0.167 |  |
| afmultimer | 8GAL | 3 | ok | best | 0.7462 | medium | 0.88 | 0.808 |  |

---

## 3. By Method (computed from section 2)

| method | n_scored | n_error | dockq_mean | pct_acceptable | pct_medium | pct_high | mean_irmsd | mean_fnat |
|---|---|---|---|---|---|---|---|---|
| af3 | 2 | 0 | 0.288 | 100% | 0% | 0% | 3.14 | 0.15 |
| afmultimer | 2 | 0 | 0.458 | 50% | 50% | 0% | 2.88 | 0.49 |
| boltz | 1 | 0 | 0.928 | 100% | 100% | 100% | 0.51 | 0.9 |
| chai | 2 | 0 | 0.291 | 50% | 0% | 0% | 3.45 | 0.23 |
| protenix | 2 | 0 | 0.805 | 100% | 100% | 50% | 1.06 | 0.83 |

---

## 4. By Target (best-pose DockQ matrix)

| pdb_id | tier | quality | af3 | afmultimer | boltz | chai | protenix |
|---|---|---|---|---|---|---|---|
| 4E81 | 1 | ok | - | - | - | - | - |
| 4EZQ | 1 | caution | - | - | - | - | - |
| 4EZR | 1 | ok | - | - | - | - | - |
| 4EZS | 1 | ok | 0.287 | - | - | 0.375 | 0.925 |
| 6HY2 | 1 | ok | 0.289 | - | 0.928 | 0.206 | 0.685 |
| 3QRX | 2 | caution | - | - | - | - | - |
| 4EZO | 2 | caution | - | - | - | - | - |
| 4EZU | 2 | ok | - | - | - | - | - |
| 6Z2P | 2 | caution | - | 0.171 | - | - | - |
| 7SAY | 2 | ok | - | - | - | - | - |
| 8AHT | 2 | ok | - | - | - | - | - |
| 4JWC | 3 | caution | - | - | - | - | - |
| 4JWD | 3 | caution | - | - | - | - | - |
| 8GAL | 3 | ok | - | 0.746 | - | - | - |

---

## 5. Discovery Candidates (RCSB expansion sweep, 77 scored)

| pdb_id | matched_query | receptor_len | peptide_len_seqres | resolved_frac | pep_nonstd | verdict | decision | decision_reason |
|---|---|---|---|---|---|---|---|---|
| 4EZR | antimicrobial peptide;drosocin | 219 | 8 | 1.0 |  | ok | ADDED | confirmed relevant, non-redundant AMP complex |
| 3OSZ | antimicrobial peptide | 279 | 10 | 1.0 |  | ok | NOT ADDED (not AMP-relevant) | Proteinase K + generic substrate peptide, not identified as an AMP |
| 5VB9 | antimicrobial peptide | 119 | 15 | 1.0 |  | ok | NOT ADDED (not AMP-relevant) | Interleukin-17A + inhibitor peptide -- immune signalling, not antimicrobial |
| 8QFZ | antimicrobial peptide | 128 | 12 | 1.0 |  | ok | NOT ADDED (not AMP-relevant) | TSLP antagonist, macrocyclic/disulfide peptide -- immune signalling, wrong topology |
| 2HD4 | antimicrobial peptide | 279 | 8 | 1.0 |  | ok | NOT ADDED (corrected) | wrongly flagged 'lactoferricin-related'; actual PDB title is a generic proteinase K inhibitor-peptide study, not the antimicrobial lactoferricin region (caught by user inspection) |
| 7W0Q | host defense peptide | 174 | 10 | 1.0 |  | ok | NOT ADDED (not AMP-relevant) | E3 ligase TRIM7 + generic peptide -- not antimicrobial |
| 8T5P | host defense peptide | 192 | 5 | 1.0 |  | ok | NOT ADDED (not AMP-relevant) | TRAF3 + viral ORF3a fragment -- antiviral immune signalling, not an AMP |
| 6R7W | cathelicidin;LL-37 | 277 | 14 | 1.0 |  | ok | NOT ADDED (not AMP-relevant) | bacterial protease Mirolysin + generic lipoprotein fragment |
| 8GAK | thanatin | 132 | 20 | 1.0 |  | ok | NOT ADDED (redundant) | same LptA+Thanatin complex as existing target 8GAL |
| 2XS3 | LL-37 | 166 | 4 | 1.0 |  | ok | NOT ADDED (not AMP-relevant) | bacterial protease Karilysin + generic tetrapeptide substrate |
| 4N6P | lactoferricin | 341 | 6 | 1.0 |  | ok | NOT ADDED (corrected) | wrongly flagged 'lactoferricin-related'; actual PDB title is a lactoferrin C-lobe / meclofenamic-acid drug-binding study, peptide is an incidental C-terminal fragment (lactoferricin is N-terminal), no antimicrobial mention anywhere |
| 3U72 | lactoferricin | 335 | 6 | 1.0 |  | ok | NOT ADDED (redundant) | same Lactotransferrin self-complex as 4N6P -- also not AMP-relevant (15-way duplicate cluster, all excluded) |
| 3VDF | lactoferricin | 335 | 6 | 1.0 |  | ok | NOT ADDED (redundant) | same Lactotransferrin self-complex as 4N6P -- also not AMP-relevant (15-way duplicate cluster, all excluded) |
| 4DXU | lactoferricin | 335 | 6 | 1.0 |  | ok | NOT ADDED (redundant) | same Lactotransferrin self-complex as 4N6P -- also not AMP-relevant (15-way duplicate cluster, all excluded) |
| 4FIM | lactoferricin | 335 | 6 | 1.0 |  | ok | NOT ADDED (redundant) | same Lactotransferrin self-complex as 4N6P -- also not AMP-relevant (15-way duplicate cluster, all excluded) |
| 4FJP | lactoferricin | 335 | 6 | 1.0 |  | ok | NOT ADDED (redundant) | same Lactotransferrin self-complex as 4N6P -- also not AMP-relevant (15-way duplicate cluster, all excluded) |
| 4G2Z | lactoferricin | 335 | 6 | 1.0 |  | ok | NOT ADDED (redundant) | same Lactotransferrin self-complex as 4N6P -- also not AMP-relevant (15-way duplicate cluster, all excluded) |
| 4GRK | lactoferricin | 335 | 6 | 1.0 |  | ok | NOT ADDED (redundant) | same Lactotransferrin self-complex as 4N6P -- also not AMP-relevant (15-way duplicate cluster, all excluded) |
| 3V5A | lactoferricin | 335 | 6 | 1.0 |  | ok | NOT ADDED (redundant) | same Lactotransferrin self-complex as 4N6P -- also not AMP-relevant (15-way duplicate cluster, all excluded) |
| 4FOR | lactoferricin | 335 | 6 | 1.0 |  | ok | NOT ADDED (redundant) | same Lactotransferrin self-complex as 4N6P -- also not AMP-relevant (15-way duplicate cluster, all excluded) |
| 3TOD | lactoferricin | 335 | 6 | 1.0 |  | ok | NOT ADDED (redundant) | same Lactotransferrin self-complex as 4N6P -- also not AMP-relevant (15-way duplicate cluster, all excluded) |
| 3U8Q | lactoferricin | 335 | 6 | 1.0 |  | ok | NOT ADDED (redundant) | same Lactotransferrin self-complex as 4N6P -- also not AMP-relevant (15-way duplicate cluster, all excluded) |
| 3UGW | lactoferricin | 335 | 6 | 1.0 |  | ok | NOT ADDED (redundant) | same Lactotransferrin self-complex as 4N6P -- also not AMP-relevant (15-way duplicate cluster, all excluded) |
| 3UK4 | lactoferricin | 335 | 6 | 1.0 |  | ok | NOT ADDED (redundant) | same Lactotransferrin self-complex as 4N6P -- also not AMP-relevant (15-way duplicate cluster, all excluded) |
| 3USD | lactoferricin | 335 | 6 | 1.0 |  | ok | NOT ADDED (redundant) | same Lactotransferrin self-complex as 4N6P -- also not AMP-relevant (15-way duplicate cluster, all excluded) |
| 4DIG | lactoferricin | 335 | 6 | 1.0 |  | ok | NOT ADDED (redundant) | same Lactotransferrin self-complex as 4N6P -- also not AMP-relevant (15-way duplicate cluster, all excluded) |
| 8AHT | melittin | 149 | 26 | 0.96 |  | ok | ADDED | confirmed relevant, non-redundant AMP complex |
| 7SAY | antimicrobial peptide;cathelicidin;LL-37 | 71 | 37 | 0.95 |  | ok | ADDED | confirmed relevant, non-redundant AMP complex |
| 4U2W | antimicrobial peptide | 223 | 16 | 0.94 |  | ok | NOT ADDED (not AMP-relevant) | trypsin + Bowman-Birk protease inhibitor, not antimicrobial |
| 8RTZ | antimicrobial peptide | 348 | 15 | 0.93 |  | ok | NOT ADDED (not AMP-relevant) | FtsI + bicyclic/macrocyclic inhibitor peptide -- wrong topology |
| 7NEF | antimicrobial peptide | 115 | 12 | 0.92 |  | ok | NOT ADDED | unencodable X in peptide SEQRES (found by full prep_native.py audit) |
| 8GAJ | thanatin | 132 | 21 | 0.9 |  | ok | NOT ADDED (redundant) | same LptA+Thanatin complex as existing target 8GAL |
| 4E81 | apidaecin | 219 | 10 | 0.9 |  | ok | ADDED | confirmed relevant, non-redundant AMP complex |
| 8AHS | melittin | 149 | 26 | 0.88 |  | ok | NOT ADDED (redundant) | same Calmodulin+Melittin complex as added target 8AHT (lower resolved fraction) |
| 6ACO | antimicrobial peptide | 270 | 7 | 0.86 |  | ok | NOT ADDED (not AMP-relevant) | Sirtuin-5 + succinylated histone peptide -- metabolism, not antimicrobial |
| 4EZU | antimicrobial peptide | 219 | 17 | 0.82 |  | ok | ADDED | confirmed relevant, non-redundant AMP complex |
| 1AVF | antimicrobial peptide | 329 | 26 | 0.81 |  | ok | NOT ADDED (not AMP-relevant) | Gastricsin protease self-complex, not antimicrobial |
| 4JWI | antimicrobial peptide;cathelicidin;bactenecin | 219 | 10 | 0.8 |  | ok | NOT ADDED | unencodable X in peptide SEQRES (found by full prep_native.py audit) |
| 4F00 | apidaecin | 219 | 10 | 0.8 |  | ok | NOT ADDED (redundant) | same DnaK+Apidaecin complex as added target 4E81 (lower resolved fraction) |
| 5I8X | antimicrobial peptide | 114 | 9 | 0.78 |  | caution: partial peptide | NOT ADDED (optional) | LecB receptor already represented via the dropped D-peptide series; designed peptide, not a natural AMP -- optional add if more LecB-family diversity is wanted |
| 5I8M | antimicrobial peptide | 114 | 9 | 0.78 |  | caution: partial peptide | NOT ADDED (redundant) | same LecB+designed-peptide complex as 5I8X |
| 4EZQ | pyrrhocoricin | 219 | 9 | 0.78 |  | caution: partial peptide | ADDED | confirmed relevant, non-redundant AMP complex |
| 3QRX | melittin | 169 | 26 | 0.77 |  | caution: partial peptide | ADDED | confirmed relevant, non-redundant AMP complex |
| 4EZV | antimicrobial peptide | 219 | 17 | 0.76 |  | caution: partial peptide | NOT ADDED (redundant) | same DnaK+bombesin-peptide complex as added target 4EZU |
| 2VKN | polymyxin | 70 | 12 | 0.75 |  | caution: partial peptide | NOT ADDED (not AMP-relevant) | yeast MAP-kinase-kinase signalling complex, not antimicrobial |
| 6RYF | host defense peptide | 894 | 14 | 0.64 |  | caution: partial peptide | NOT ADDED (not AMP-relevant) | ERAP1 antigen-processing enzyme + generic substrate |
| 4EZO | antimicrobial peptide;cathelicidin | 219 | 15 | 0.53 |  | caution: partial peptide | ADDED | confirmed relevant, non-redundant AMP complex |
| 2PSX | antimicrobial peptide | 227 | 4 | 0.5 |  | caution: partial peptide | NOT ADDED (not AMP-relevant) | Kallikrein-5 + Leupeptin (protease inhibitor, not a ribosomal AMP) |
| 2PSY | antimicrobial peptide | 227 | 4 | 0.5 |  | caution: partial peptide | NOT ADDED (redundant) | same Kallikrein-5+Leupeptin complex as 2PSX |
| 1TWQ | antimicrobial peptide | 165 | 4 | 0.5 |  | caution: partial peptide | NOT ADDED (not AMP-relevant) | peptidoglycan recognition protein + muramyl tripeptide -- ligand is a cell-wall fragment, not an AMP |
| 1HNE | antimicrobial peptide | 218 | 6 | 0.5 |  | caution: partial peptide | NOT ADDED (not AMP-relevant) | human leukocyte elastase + synthetic chloromethylketone inhibitor peptide |
| 1PPG | antimicrobial peptide | 218 | 6 | 0.5 |  | caution: partial peptide | NOT ADDED (redundant) | same elastase+inhibitor complex as 1HNE |
| 2EAX | antimicrobial peptide | 164 | 5 | 1.0 | DAL;FGA | drop: non-standard/D peptide residues | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 6Q87 | antimicrobial peptide | 114 | 13 | 1.0 | DAL;DLE;DLY;DTY | drop: non-standard/D peptide residues | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 7NEW | antimicrobial peptide | 115 | 12 | 0.92 | DLE | drop: non-standard/D peptide residues | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 8ANR | antimicrobial peptide | 114 | 12 | 0.92 | DLE;DLY | drop: non-standard/D peptide residues | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 8AOO | antimicrobial peptide | 114 | 12 | 0.92 | DLE;DLY | drop: non-standard/D peptide residues | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 8AN9 | antimicrobial peptide | 114 | 12 | 0.92 | DLE;DLY | drop: non-standard/D peptide residues | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 8ANO | antimicrobial peptide | 114 | 12 | 0.92 | DLE;DLY | drop: non-standard/D peptide residues | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 3VVS | antimicrobial peptide | 461 | 11 | 0.91 | DPN | drop: non-standard/D peptide residues | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 6Y0U | antimicrobial peptide | 115 | 14 | 0.86 | DLY | drop: non-standard/D peptide residues | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 3DPO | pyrrhocoricin | 219 | 11 | 0.82 | ALC | drop: non-standard/D peptide residues | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 4HY9 | pyrrhocoricin | 219 | 12 | 0.75 | ALC | drop: non-standard/D peptide residues | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 6Q8D | antimicrobial peptide | 114 | 11 | 0.73 | DAL;DLE;DLY | drop: non-standard/D peptide residues | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 4HYB | pyrrhocoricin | 219 | 11 | 0.73 | ALC | drop: non-standard/D peptide residues | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 2APH | antimicrobial peptide | 165 | 6 | 0.67 | DAL | drop: non-standard/D peptide residues | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 3DPP | pyrrhocoricin | 219 | 20 | 0.65 | ALC | drop: non-standard/D peptide residues | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 3DPQ | pyrrhocoricin | 219 | 20 | 0.6 | ALC | drop: non-standard/D peptide residues | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 6Y0V | antimicrobial peptide | 114 | 14 | 0.5 | DLY | drop: non-standard/D peptide residues | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 6B0U | host defense peptide | 428 | 9 | 0.44 |  | drop: peptide mostly disordered | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 6M7Y | nisin | 996 | 34 | 0.44 |  | drop: peptide mostly disordered | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 8A8X | host defense peptide | 179 | 7 | 0.43 |  | drop: peptide mostly disordered | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 3RIG | defensin | 273 | 12 | 0.42 |  | drop: peptide mostly disordered | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 4EZN | pyrrhocoricin | 219 | 20 | 0.3 |  | drop: peptide mostly disordered | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 6S5P | antimicrobial peptide | 115 | 7 | 0.14 |  | drop: peptide mostly disordered | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 2X3T | antimicrobial peptide | 171 | 9 | 0.0 |  | drop: peptide mostly disordered | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
| 4WVP | antimicrobial peptide | 218 | 6 | 0.0 |  | drop: peptide mostly disordered | NOT ADDED | failed the resolved-fraction / D-residue screen (see verdict) |
