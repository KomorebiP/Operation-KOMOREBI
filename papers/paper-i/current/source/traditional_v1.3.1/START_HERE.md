# Paper I — complete project bundle
## Distribution v1.3.1 · visual-refresh edition

**Projector-Resolved Seed Calculus I: Typed Seeds, Operator Grammars, and Exact Reconstruction**  
**Author: Komorebi P.**

Open `paper/Projector_Resolved_Seed_Calculus_I.pdf` for the 39-page article.
Open `README.md` for build and verification instructions.
Open `CONTINUE_HERE.md` to resume work in a new session.

This archive contains the manuscript, all ten current figure pairs, their Python
source, the full local Lean development, tests, dependency pins, build scripts,
numerical outputs, claim mapping, review, and historical verification logs.

## Check the extracted archive

From this directory, with Python available:

```sh
python scripts/verify_manifest.py
python scripts/check_bundle.py --tests
```

The first command checks every file in the SHA-256 manifest. The second repeats
that check and runs the 33 Python tests without regenerating publication assets.
Neither command installs software. The test command needs the recorded Python
dependencies already installed. A Windows convenience wrapper is also provided:

```powershell
.\CHECK_BUNDLE.ps1 -Tests
```

The PowerShell wrapper is provided for convenience; it was not executed on Windows
in this packaging pass. The Python commands were exercised on Linux.

## Version and verification boundaries

The distribution and artwork revision is **1.3.1**. The preserved manuscript text
still prints **1.3.0**; it was not silently edited to change its version label.
The local Lean sources are the unchanged development with component label **1.0.2**.
The computational core retains package label **1.1.2**, with the v1.3.1 visual module.

The prior visual-refresh archive retained obsolete v1.3.0 checksums and metadata.
Those records are preserved under `provenance/pre_packaging_records/`. The root
manifest and release inventory have been replaced with records for this exact bundle.

Fresh packaging checks reran all 33 Python tests, regenerated the finite examples
and figures in an isolated copy, and rebuilt the PDF. All ten PNGs matched exactly;
all 39 rebuilt pages matched in extracted text and rendered pixels at 144 DPI.
The 20 Lean source files match the hashes in the preserved successful Lean audit.
**Lean was not executed again in this packaging pass.**

## External software is not bundled

This is a complete **project-source and artifact** archive, not a self-contained
runtime. The Lean compiler, Mathlib dependency source/cache, Python interpreter,
Python package wheels, and TeX installation remain external. Their pins and run
instructions are included. No standalone font files are distributed.

This is Paper I only. It is not an archive of Papers II–XII or an assembled journal.
