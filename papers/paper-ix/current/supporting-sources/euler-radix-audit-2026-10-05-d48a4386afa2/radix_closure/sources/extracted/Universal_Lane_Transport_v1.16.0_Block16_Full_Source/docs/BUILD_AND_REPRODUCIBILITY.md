# Build and reproducibility

## Prerequisites

- Python 3.11 or later
- dependencies in `requirements.txt`
- `latexmk`
- a complete TeX Live or MiKTeX installation containing `newtx`, `tcolorbox`,
  `cleveref`, `pdflscape`, `seqsplit`, the AMS packages, and the other packages
  imported by the source

The v1.16.0 release audit used Python 3.13, NumPy 2.3.5, Matplotlib 3.10.8,
SymPy 1.14.0, Pillow 12.3.0, PyMuPDF 1.26.7, PyYAML 6.0.3, latexmk 4.86, and TeX
Live 2025/dev.

## Fast verification

From the repository root:

```bash
python -m pip install -r requirements.txt
python scripts/check_release.py
cd manuscript
python verify_block15_lane_transport.py
python verify_block16_holonomy_lane_transport.py
python verify_block16_publication_audit.py
```

Expected principal records:

```text
Block 15: PASS, 197099 assertions, 0 failures
Block 16: PASS, 1344823 assertions, 0 failures
Publication audit: PASS, 85 checks, 0 failures
```

## Normal build

POSIX:

```bash
cd manuscript
./Build.sh
```

PowerShell:

```powershell
Set-Location manuscript
& .\Build.ps1
```

The normal build:

1. authenticates prior regression records;
2. replays the recent nonlinear, Galois, and global-synthesis suites;
3. runs the Block 15 and Block 16 exact verifiers;
4. regenerates current figures and LaTeX components;
5. retains the frozen Block 15 source-audit record;
6. compiles the v1.16.0 integrated manuscript;
7. refreshes the Block 16 publication audit;
8. recompiles the integrated manuscript with the current audit table;
9. reruns the final Block 16 publication audit;
10. compiles the standalone holonomy theorem note.

## Build modes

```bash
./Build.sh --full
./Build.sh --audit-only
```

`--full` replays the broader historical verifier and figure pipeline.
`--audit-only` skips the expensive historical recomputation but still runs the
controlling lane verifiers, source generators, integrated build, publication
audit, and standalone build.

PowerShell uses `-FullRegression` and `-AuditOnly`.

## Canonical outputs

```text
manuscript/Komorebi_Stratified_Universality_Foundations_v1.16.0_Block16.pdf
standalone/Holonomy_Twisted_Lane_Transport_and_Orbit_Descent.pdf
```

The audited active-environment outputs contain 239 and 7 US-letter pages,
respectively. TeX timestamps, producer metadata, package versions, and font
metrics can prevent byte-identical builds. A successful source build is not
therefore represented as byte-for-byte reproducibility unless its checksum
matches the release manifest.

## Packaging

```bash
python scripts/package_release.py
```

This verifies the repository, refreshes source manifests, and writes a
compact research-extension archive, a full-source archive, and a checksum file
under `dist/`. ZIP entry timestamps and ordering are fixed for deterministic
archives.

## Validation boundary

The build pipeline checks package integrity, exact finite formulas, source
synchronization, and PDF structure. It does not provide independent proof
review, literature review, or a historical-priority determination.
