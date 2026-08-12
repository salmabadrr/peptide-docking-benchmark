[CmdletBinding()]
param(
    [string]$InputDirectory = "6HY2_docking_input/diffpepdock"
)

$ErrorActionPreference = "Stop"

$receptorPath = Join-Path $InputDirectory "6HY2.pdb"
$fastaPath = Join-Path $InputDirectory "peptides.fasta"
$infoPath = Join-Path $InputDirectory "receptor_info.json"
foreach ($path in @($receptorPath, $fastaPath, $infoPath)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Required docking input is missing: $path"
    }
}

$atomLines = Get-Content -LiteralPath $receptorPath | Where-Object { $_.StartsWith("ATOM  ") }
$heteroLines = Get-Content -LiteralPath $receptorPath | Where-Object { $_.StartsWith("HETATM") }
$chains = $atomLines | ForEach-Object { $_.Substring(21, 1) } | Sort-Object -Unique
$residues = $atomLines | Where-Object { $_.Substring(12, 4).Trim() -eq "CA" } |
    ForEach-Object { "{0}:{1}" -f $_.Substring(21, 1), $_.Substring(22, 5) } | Sort-Object -Unique
$sequence = (Get-Content -LiteralPath $fastaPath | Where-Object { -not $_.StartsWith(">") }) -join ""
$info = Get-Content -LiteralPath $infoPath -Raw | ConvertFrom-Json

if ($chains -ne "X") { throw "Expected only receptor chain X; found: $($chains -join ', ')" }
if ($residues.Count -ne 262) { throw "Expected 262 receptor residues; found: $($residues.Count)" }
if ($heteroLines.Count -ne 0) { throw "Receptor must not contain HETATM records; found $($heteroLines.Count)" }
if ($sequence -ne "WMLDPIAGKWSR") { throw "Unexpected peptide sequence: $sequence" }
if ($info.PSObject.Properties.Name -notcontains "6HY2") { throw "receptor_info.json must define the 6HY2 target" }

Write-Host "PASS: receptor chain X, 262 residues; peptide WMLDPIAGKWSR, 12 residues."
