# Reproducibility

## Package verification

From the repository root:

```powershell
python -m pip install -e ".[dev,research]"
python -m pytest
am-spd verify
am-spd verify --full
```

When running directly from an uninstalled checkout, use:

```powershell
$env:PYTHONPATH = "src"
python -m pytest
python -m am_spd.cli verify
```

The standard suite checks the public API, normalized-raster archive identity to numerical tolerance, finite outputs, tree-frontier structure, image input and output, and command-line behavior. Bit-for-bit parity is checked separately for retained-source checkpoint continuation; it is not implied by residual closure.


## Exact paper replay through the installed package

Version 1.0.0 bundles checksummed archived source images and core packet bases, packet history, and reference ledgers. Replay recomputes downstream singular, tree, and portfolio stages with the byte-preserved v0.3 backend. New decompositions use the corrected v1.0 backend. Anchoring the historical source and core avoids changes in font rasterization and transform sampling across dependency versions; replay does not repeat the original geometry-discovery search.

```powershell
$env:OPENBLAS_NUM_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
am-spd reproduce-paper --output-dir artifacts\paper-replay --strict-reference
```

The comparison report separates required final invariants from archived intermediate Lagrange diagnostics. Two intermediate rows came from an earlier tie-equivalent solver revision. They remain visible in `diagnostic_differences`; final reconstruction values and exact-budget results are checked independently.

## Build the finalized manuscript

The self-contained source is under `docs/paper/final`.

```powershell
Set-Location docs\paper\final
.\build.ps1
```

Or from Bash:

```bash
cd docs/paper/final
./build.sh
```

The expected output is a 78-page PDF. The audited build completed without undefined references, duplicate labels, overfull boxes, underfull boxes, or LaTeX warnings.

The manuscript tables under `docs/paper/final/tables` were regenerated from the JSON files under `docs/paper/final/data`. The complete editorial and technical record is in `docs/paper/MANUSCRIPT_AUDIT.md`.

## Regenerate the finalized source from the preserved snapshot

The provenance generator reconstructs the focused manuscript from `research/original`:

```powershell
python docs\paper\final\generate_final_manuscript.py `
  --repository-root . `
  --output-dir artifacts\final_manuscript_source
Set-Location artifacts\final_manuscript_source
.\build.ps1
```

The output directory is replaced. Do not point it at the repository root or `research/original`.

## Original research verification

The recovered source snapshot is under `research/original`. Historical programs can rewrite generated results, so run the verification wrapper from the package root:

```powershell
.\scripts\verify_full.ps1
```

Or from Bash:

```bash
bash scripts/verify_full.sh
```

Each invocation copies the snapshot into a unique `artifacts/verification/run_*` directory and runs the historical programs there. Package integration verification runs against the installed current package. Logs and regenerated historical results remain in that run directory, while `research/original` stays unchanged. The full source bundle is required; compact distributions can run `python -m am_spd verify --full` without the historical snapshot.

The archived final suite's expected totals are:

- 11 implementation and stress groups
- 12,154 scenarios
- 0 failures
- 9,960 exact tree comparisons

The wrapper prints its `full_verification.log` path. Retain this log and the copied run directory when recording current-release verification evidence.

## Recompute benchmark assets

Preserve the research snapshot by generating assets in a separate copy:

```powershell
.\scripts\reproduce_paper.ps1 -OutputDirectory artifacts\recomputed-research
```

The wrapper copies `research/original` into a new output directory, runs the regeneration there, and rejects an existing destination. The underlying research commands overwrite their generated tables, figures, and result files, so do not run them directly in the preserved snapshot.

## Rebuild the archival manuscript

The original 147-page edition remains available for provenance. Build it in a fresh copy so auxiliary files and regenerated PDF output do not alter the snapshot:

```powershell
$ArchiveCopy = "artifacts\archival-manuscript"
if (Test-Path -LiteralPath $ArchiveCopy) { throw "Choose a new archival build directory." }
New-Item -ItemType Directory -Path $ArchiveCopy -Force | Out-Null
Get-ChildItem -LiteralPath research\original -Force | Copy-Item -Destination $ArchiveCopy -Recurse
Push-Location $ArchiveCopy
try {
  foreach ($Pass in 1..3) {
    pdflatex -interaction=nonstopmode -halt-on-error Projector_Resolved_Adaptive_Multiscale_Singular_Packet_Decomposition_Final.tex
    if ($LASTEXITCODE -ne 0) { throw "Archival manuscript build failed." }
  }
} finally {
  Pop-Location
}
```

This archival build is not the focused 78-page manuscript distributed under `docs/paper`.

## Thread control

Dense linear algebra can create many native threads. For repeatable local verification, set:

```powershell
$env:OPENBLAS_NUM_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
```
