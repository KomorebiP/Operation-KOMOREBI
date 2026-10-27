# Machine Understanding
## Representation, Explanation, and Transfer

**Komorebi P. · Operation Komorebi · First consolidated edition · Version 1.0.0 · 8 October 2026**

This 50-page theoretical manuscript asks what a reasoner retains beyond a correct answer. Its finite framework connects reusable state, operation transport, information acquisition, corrective evidence, recipient-relative explanation, and an explicit resource account. A three-register instrument provides a continuing analytical example.

## Read first

- `Machine_Understanding_v1.0.0.pdf` is the reading manuscript.
- `Machine_Understanding_v1.0.0.tex` is the canonical mathematical source.
- `Machine_Understanding_v1.0.0.md` is a reading export with the same statement numbers and references. The PDF controls pagination and layout.
- `THEOREM_INDEX.md` locates all 20 theorem/proposition statements.
- `CLAIMS.json` records each statement's hypotheses, conclusion, boundaries, and lineage.
- `REVIEW_NOTES.md` records actual review and verification scope.
- `FIRST_EDITION_SCOPE.md` separates this edition's completed scope from future research.

## What 1.0 adds

The 17 statements and corresponding proofs in v0.5 are preserved verbatim. Three additions sharpen the implementation boundary. Task-dependent interpreter information is charged rather than hidden in a free background. Fixed recipient programs give a finite covering criterion that is stricter than choosing a convenient decoder after designing a code. A finite resource frontier then joins those same decoders to one state-changing experiment tree while charging both online execution and every compiled controller branch.

The integrated instrument uses one exact diagnostic, one source modular subtraction, one three-bit broadcast, and one modular addition in each of two fixed recipients. For one known old-record fibre its literal controller has six records, of which two are visited. Installed programs, prior knowledge, model construction, offline search, and generic dispatch remain explicit and separate. These are named reference-procedure charges, not universal physical runtimes or minimal program sizes.

## Reproduce

With Python 3.10 or newer and a LaTeX installation containing `latexmk`, `newtxtext`, `newtxmath` and the source's other declared packages:

```bash
bash build.sh
```

This reruns all three exact suites, both current demonstrations, the source audit, and the computation-record verifier, then rebuilds the PDF using the supplied vector figures. Fresh receipts go to `build/validation_rerun/`; released receipts in `validation/final/` are not overwritten.

On Windows, use `powershell -ExecutionPolicy Bypass -File build.ps1` from the package directory. The PowerShell script was inspected, not executed on Windows for this release.

Mathematical checks alone:

```bash
python code/run_validation.py --out-dir build/validation_rerun
python code/verify_computation.py build/validation_rerun/computation_manifest.json
```

Reading Markdown requires Pandoc after the LaTeX build:

```bash
python code/make_markdown.py
```

Figures can be regenerated with Matplotlib using `code/make_figures.py` and `code/make_expanded_figures.py`. No standalone font files or third-party paper full texts are distributed.

## Executable material

`code/understanding.py` implements the earlier finite constructions. `code/resource_contracts.py` adds fixed-recipient codebooks, explicit-tree Pareto frontiers, and an independently traversing policy checker. `code/demo_first_edition.py` executes the actual frozen recipient programs over all 125 instrument states. `code/edition_checks.py` compares the resource frontier with a separately coded enumeration of complete bounded history trees.

The exact suites passed **38 groups and 252,669 assertions**. Counts describe the executed finite domains, not independent replications or new discoveries. The PDF contains **20 prose-proof statements, 3 definitions, 12 counterexamples, 8 vector figures, and 19 references**.

## Evidence and release boundaries

This is a theoretical first edition, not a validated diagnostic for a deployed neural model. No agent experiments are reported. General claims rest on conditional prose proofs, not assertion totals. There has been no independent peer review, Lean build, journal acceptance, or exhaustive priority review. Source verification is project-local, with pinned inputs, explicit commands, and output hashes, not independent execution attestation.

Historical material under `validation/predecessor_v05/` belongs to the earlier release and is labeled accordingly. Its old paths and receipts are retained as history, not reclassified as current verification. `SHA256SUMS` covers the distributed first-edition files; use `python code/verify_release.py` to check them. The external v0.5 PDF and ZIP remain unchanged.
