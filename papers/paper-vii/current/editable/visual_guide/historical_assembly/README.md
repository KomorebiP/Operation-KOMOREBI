# Paper VII — final standalone visual guide

`Paper_VII_Visual_Guide_Final.pdf` contains 40 worked pages: the original 28 visual pages, with current reading references and documentary scope clarifications, followed by 12 new exact worked pages for strengthened results. The guide accompanies the final traditional edition.

All 26 original TikZ vector plates and the original algebraic/symbolic model and generator sources are retained byte-for-byte. The ordered 287 original inline/display mathematical spans are unchanged. Twelve additional editable TikZ plates display exact algebraic data; they use no AI-generated artwork and no sampled coordinate curve as proof.

## Read and reproduce

- `source/pages.tex`: retained original mathematical content and revised source lines.
- `source/extended_pages.tex`: worked pages V-29 through V-40, including spaces, assumptions, exceptional cases and evidence limits.
- `graphics/`: all 26 original editable vector sources and their index.
- `graphics_extended/`: 12 added vector sources and their index.
- `source/models.py`, `source/generate_graphics.py`: unchanged original SymPy-dependent sources.
- `checks/verify_examples.py`, `checks/EXACT_CHECKS.json`: unchanged original suite and inherited 180-check result.
- `checks/verify_extended.py`: fresh standard-library exact rational/Gaussian-rational matrix checks.
- `checks/EXTENDED_CHECKS.json`: latest fresh result: 373 positive assertions, 12 rejected false controls.
- `checks/EXTENDED_CONTRACT.json`, `computations/final-20261006/`: bounded contract, actual execution log, result and validated version-2 manifest.
- `SOURCE_CROSSWALK.md` and `.json`: all 40 guide pages mapped to final traditional-edition sources.
- `provenance/`: source hashes, original page text, ordered mathematical-span preservation, inherited checks, saved finite ledger, and formal-scope records.
- `BUILD_AUDIT.json`, `build_logs/`, `PDF_TEXT.txt`: PDF/page/link/glyph checks and build evidence.

From this directory run:

```text
python3 build.py
```

The build uses paths relative to its own directory, runs the new exact checks, regenerates only the added vector plates, compiles two LaTeX passes in a temporary directory, and checks the full 40-page PDF. It requires already-available Python 3, PyMuPDF, `pdflatex`, and the LaTeX packages listed in the preamble. It installs nothing and needs no network access. The build writes outputs in this directory.

The original `requirements.txt` is retained as a historical source record. SymPy is unavailable in the current environment. The original 180-check symbolic suite and original plate generator are consequently **inherited, not freshly replayed**. Their code, saved results and hashes remain available. The new exact suite uses only Python's standard library; NumPy is not needed for this guide's exact evidence.

## Mathematical and execution boundary

The saved v0.6.0 ledger lists 19 finite items with their recorded hypotheses. Its 323 declaration/25-module counts are inherited metadata. This guide performs no Lean kernel execution and asserts no additional Lean coverage. The five original targets—anomaly-free refinement, uniform Feshbach control for the proposed tower, Lorentzian reconstruction, an Einstein infrared limit, and a positive physical massless spin-two sector—remain open.

The strengthened edition supplies written proofs and conditional bounded-limit criteria. Fresh finite checks illustrate their algebraic examples; the check count does not prove universal convergence, authenticate an external theorem, establish a physical continuum, or replace an operator-domain argument. Each new worked page states which part is exact arithmetic and which part uses the written analytic argument.
