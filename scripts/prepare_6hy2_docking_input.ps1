<#
.SYNOPSIS
Creates clean, receptor-only DiffPepDock inputs for PDB entry 6HY2.

.DESCRIPTION
Uses the checked-in extracted receptor as its source, removes crystallographic
waters and alternate-location B atoms, and writes the deposited CR20 sequence.
The native complex in ../6HY2.pdb is intentionally not modified.
#>

[CmdletBinding()]
param(
    [string]$SourceReceptor = "6HY2_docking_input/6HY2_receptor_X.pdb",
    [string]$OutputDirectory = "6HY2_docking_input/diffpepdock"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $SourceReceptor -PathType Leaf)) {
    throw "Source receptor not found: $SourceReceptor"
}

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null

$receptorPath = Join-Path $OutputDirectory "6HY2.pdb"
$fastaPath = Join-Path $OutputDirectory "peptides.fasta"
$infoPath = Join-Path $OutputDirectory "receptor_info.json"

# Retain only the receptor's ATOM records. For alternate locations, keep the
# primary conformer (blank or A), which results in 262 protein residues.
$atomLines = Get-Content -LiteralPath $SourceReceptor | Where-Object {
    $_.StartsWith("ATOM  ") -and ($_.Length -lt 17 -or $_.Substring(16, 1) -in @(" ", "A"))
} | ForEach-Object { $_.TrimEnd() }
if ($atomLines.Count -eq 0) {
    throw "No retained ATOM records found in $SourceReceptor"
}
@($atomLines + "TER" + "END") | Set-Content -LiteralPath $receptorPath -Encoding ascii

@(
    ">6HY2_CR20",
    "WMLDPIAGKWSR"
) | Set-Content -LiteralPath $fastaPath -Encoding ascii

@{
    "6HY2" = @{}
} | ConvertTo-Json | Set-Content -LiteralPath $infoPath -Encoding ascii

Write-Host "Created $receptorPath"
Write-Host "Created $fastaPath"
Write-Host "Created $infoPath"
