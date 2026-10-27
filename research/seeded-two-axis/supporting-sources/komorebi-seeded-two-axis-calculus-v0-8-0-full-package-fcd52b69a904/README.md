# Komorebi Seeded Two-Axis Calculus v0.8.0

27 September 2026. Author: Komorebi P.

The current manuscript is a 73-page working formalization, with the complete
v0.7.0 source, PDF, and package preserved in `previous/`. No previous mathematical
sections were removed. New theorem-ledger entries K42–K52 cover nonidentity
arithmetic resolution, finite-level interaction kernels, completion defects,
arithmetic fracture reconstruction, effective lattice gluing, and compatible
operator descent.

## Evidence boundary

These are written proofs with authoring-session self-review, not Lean-checked
proofs and not independent referee review. The scripts provide exact finite
regression evidence only. This package does not claim a new set-theoretic axiom,
historical novelty, arbitrary coherent-tower effectivity, automorphic existence,
or Langlands reciprocity. Several mechanisms are classical algebra expressed
and proved in the present calculus.

The new genuine existence result constructs an integral lattice from a localized
free module, local p-adic lattices, and specified generic identifications. Those
identifications are input. Matching coarse invariants alone does not supply them.

## Files

- The PDF and same-named standalone `.tex` are the current reading/editing entry points.
- `proofs/` retains the two integrated new proof blocks.
- `checks/` contains the two unchanged inherited checkers, the new tower/gluing
  checker, and JSON results from this session.
- `audit/` contains the exact source diff, base hashes, static checks, primary-source
  checks, mathematical audit, final LaTeX log, run logs, and visual contact sheets.
- `STATUS.md` is the current mathematical scope and remaining obligations.
- `RESEARCH_LOG.md` links immutable route records.
- `previous/` includes the exact supplied v0.7.0 full package and its source/PDF.

## Build

The standalone TeX does not require the proof-fragment files at compile time.
In the package root, with a LaTeX distribution containing the packages named in
the preamble and `latexmk`, run:

```sh
mkdir -p build
latexmk -pdf -outdir=build -interaction=nonstopmode -halt-on-error Komorebi_Seeded_Two_Axis_Calculus_v0.8.0.tex
```

Tested with pdfTeX 1.40.26 (TeX Live 2025/dev/Debian), latexmk 4.86.
The final run had no LaTeX warnings, overfull boxes, undefined references, or
undefined citations. PDF bytes may vary on another build because of timestamps.
No font files are included in the package.

## Regenerate the integrated source

```sh
python audit/integrate_v080.py
```

This deliberately overwrites the standalone source from the preserved v0.7.0
source and the two proof fragments, while updating the abstract, ledger,
bibliography, and audit appendix. Preserve any direct edits before running it.
The integration step was rerun to verify idempotence. The retained source diff
shows exactly what changed. `audit/render_scan_used.py` records the local visual
scan used for this release and contains that session's paths; it is not needed
for compilation or mathematical tests.

## Reproduce the finite checks

Tested with Python 3.13.5 and SymPy 1.14.0. Install `requirements.txt` in an
appropriate environment, then run from the root:

```sh
python checks/check_models.py --max-length 10 --output checks/base_regression_results.json
python checks/check_interactions.py --output checks/interaction_results.json
python checks/check_resolution_towers.py --output checks/resolution_results.json
```

All use exact integers, rational arithmetic, and finite residue enumeration.
There is no random sampling or tolerance-based acceptance. The infinity sentinel
used for the valuation of zero is not a floating-point numerical approximation.
The new HNF lattice outputs are checked against exact residue groups and indices.
Each output reports the actually tested family. Rerunning changes timings and
absolute command paths, so report hashes need not match the release.

## Verification of archive integrity

From the package root, `sha256sum -c SHA256SUMS.txt` checks the complete supplied
file inventory except the checksum file itself. `audit/release_manifest.json`
records base hashes, commands, environment, evidence scope, and output hashes.
It is a standalone provenance record, not a claim of Mathbox schema validation.
