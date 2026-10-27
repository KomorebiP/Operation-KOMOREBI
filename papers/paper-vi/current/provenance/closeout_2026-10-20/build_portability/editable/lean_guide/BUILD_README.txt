Paper VI Lean and evidence guide / monograph edition, 9 October 2026

Build the supplied guide:
  python3 build.py

Compile in isolation without changing delivered files:
  python3 build.py --check-only

Compile to an explicit destination:
  python3 build.py --output-directory /path/to/destination

Requirements: XeLaTeX with the TeX packages named by preamble.tex and
komorebi-monograph.sty. The font files and their licenses are bundled.
The builder stages the full authored source tree, retains relative assets,
and compiles four passes. It does not invoke Lean or regenerate evidence.

Documentation checks:
  python3 reconcile_sources.py
  python3 verify_pdf.py

The first checks the supplied tables and exact excerpts against the source
snapshot. The second checks target-name extraction, excerpt hashes, page
bounds and fonts, then renders every page into contact sheets. Inspection
of rendered pages remains necessary for visual layout.

Optional data generation:
  python3 assemble.py
  python3 navigation.py

These read the preserved source contract, current computation review,
traditional source maps and actual PDF page labels. Generated tables are
already included for ordinary PDF reproduction. Run data generation only
when updating those inputs, then compile and inspect the guide again.
Data generation requires fontTools and PyMuPDF in addition to Python.

Preserved formal scope: 33 manuscript result rows, 341 theorem targets,
47 proof modules, 48 exact source excerpts, and nine dependency pins.
The 782 namespace declarations describe the wider inherited audit scope.
The broader 142 theorem-like traditional records and 140 written proof
bodies overlap and do not extend the 33-result formal contract.

The September 6, 2026 v0.5.0 kernel build and axiom audit are inherited
execution evidence. Lean, Lake and Elan were unavailable for this edition.
No fresh kernel execution is claimed. Three continuum conjectures remain
open. Finite tests and static source checks have only their stated scope.

Earlier authoring files are retained under historical_assembly. The
preserved original mathematical source and historical evidence live in
the package source/complete/original_snapshot tree.
