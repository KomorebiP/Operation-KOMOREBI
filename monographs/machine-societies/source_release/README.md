# Machine Societies — First edition

## A Theory of Persistent Plural Computational Organization

**Komorebi P. · Operation Komorebi · Version 1.0.0 · 8 October 2026**

This is the first consolidated theoretical edition. The release designation identifies a complete editorial and source package. It does not imply journal acceptance, independent peer review, formal proof-assistant verification, a demonstrated machine society, or closure of the open problems.

## Read the work

`Machine_Societies_v1.0.0.pdf` is the 106-page reading edition. Its five parts cover realization, institutions, continuity and knowledge, joint feasibility, and accountability. The front matter provides reading routes and notation. `THEOREM_INDEX.md` locates every theorem and proposition by printed page. `CLAIM_AND_DEPENDENCY_MAP.md` separates the main logical dependencies and their limits.

The work does not report the author's agent experiments. The mathematical examples are analytical constructions. Companion checks use exact finite arithmetic and support the implementation of those constructions, not general empirical or priority claims.

## Rebuild the PDF

From this directory on a system with a working LaTeX installation:

```bash
bash build.sh
```

On Windows PowerShell with LaTeX and latexmk on PATH:

```powershell
.\build.ps1
```

The output is `build/Machine_Societies_v1.0.0.pdf`. The source is `Machine_Societies_v1.0.0.tex`, with figure assets in `figures/`. A reasonably complete TeX installation must provide the packages declared in the preamble, including newtx, amsmath, microtype, booktabs, longtable, hyperref and placeins. No standalone font files are distributed. The PowerShell script was inspected but not executed on Windows in this release.

## Run the mathematical reference programs

Python 3.10 or later is required by the reference code. The delivered run used the interpreter recorded in the computation manifest. The exact suite uses only the Python standard library.

```bash
python code/demo_commons.py
python code/demo_accountability.py
python validation/check_finite_models.py
python validation/audit_source.py
python validation/verify_release.py
```

The delivered aggregate suite passed **75 groups and 922,032 assertions**. Of these, 62 groups and 700,130 assertions retain the v0.7 domains. The 13 added groups contain 221,902 assertions. Counts are deterministic coverage, not independent experiments or proof counts.

The accountability demo records the exact privacy margin, the distinction between the ordinary safe kernel and the stoppable kernel, and the eight-unit settlement witness. The original commons demo retains the distinct five-unit audit-and-service contract. Their observation laws are not interchangeable.

## Check the original package snapshot

Before running programs that regenerate JSON receipts or other outputs:

```bash
python validation/verify_release.py --snapshot
```

This checks `SHA256SUMS.txt`, including the reading PDF. Running the suite changes timestamps and receipts, so a later original-snapshot mismatch is expected. The normal verifier checks the current computation record and pinned execution inputs. A successful hash check certifies bytes relative to this package, not their origin or the truth of mathematical premises.

## Package contents

`code/` contains bounded exact reference routines, not a deployed governance system. `validation/` contains test domains, execution receipts, source audit, final build diagnostics, source review and fresh-rebuild evidence. `figures/` contains 14 vector figures and their Python regeneration scripts. Figure regeneration additionally requires NumPy and Matplotlib, with any script-specific requirements visible in its imports. The existing figure assets suffice to rebuild the manuscript without regenerating them.

`sources/` preserves historical source and validation snapshots. Their manifests and README files describe their own releases, not the current one. They are archival records and are not inputs to the active mathematical suite except for the explicitly identified predecessor source comparison.

## Status and limits

There are **62 theorem/proposition statements with prose proofs**, not 62 claims of mathematical priority. All 56 v0.7 statement-and-proof pairs remain verbatim. Six are added in the accountability chapter. The edition also contains six formal definitions, 22 formal counterexamples, 14 vector figures and 58 references.

The new proof arguments, the source integration and the finite programs were reviewed within this project. This is not independent replication or a comprehensive new proof audit of every retained result. The reference review is targeted. PDF/A, tagged accessibility, Windows execution and renderer equivalence are not certified. See `PROOFREADING_REPORT.md` and `PUBLICATION_HANDOFF.md` for the release boundary.
