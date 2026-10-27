# Komorebi Special Functions: expanded visual guide v0.4

The guide contains 180 pages and 171 illustrated lessons: the original 110 lessons across Special Functions I–VIII, plus 48 lessons in three visual atlases and 13 closing bridge/capstone lessons. Each lesson has a computed figure, a central formula, reading directions, a worked example, a carry-forward statement, and a source/scope note.

The three atlases cover 30 identified OEIS entries. Sixteen sequence lessons explain definitions and exact transforms; sixteen polyphase lessons show residue channels, refinement, carry, and reconstruction; sixteen tap lessons show finite convolution, recurrence residuals, filter composition, Haar reconstruction, lifting, rational resampling, and chunked streaming.

The closing addition has four seed/response/coefficient bridges, three operator-contract lessons, and a six-lesson capstone following one finite Fibonacci record. The capstone separates truncation endpoints from an interior defect, proves an operation can depend on a discarded channel, repairs the state under an explicit recurrence model, and retains both FIR history and a streaming phase clock.

All figures use Python and Matplotlib. No AI-generated imagery is used. Ordinary and exponential generating-function coefficients, finite filters, recurrence kernels, and reciprocal infinite responses retain separate conventions.

## Read and rebuild

Open `Komorebi_Special_Functions_Expanded_Visual_Guide_v0.4.pdf`. The contents and PDF bookmarks link to every lesson.

Install `requirements.txt` in Python 3.11 or newer, and install a TeX distribution with PDFLaTeX, Latin Modern, microtype, amsmath, graphicx, fancyhdr, hyperref and bookmark. The tested runtime is Python 3.12.14 and TeX Live 2023/Debian. From this directory run:

```sh
python reproduce_guide.py
```

The runner regenerates all 171 figure pairs, compiles the guide three times, and validates each lesson's page blocks and internal navigation. It does not repeat human visual inspection or an independent mathematical review. The dense V03/VI03 color meshes retain 300-dpi image layers inside otherwise vector figures to avoid PDF cell seams.

## Source layout

- `main.tex`, `guide_macros.tex`, and chapter `.tex` files: editable book source.
- `guide_style.py` and `figures_*.py`: the eleven figure-generation entry points and their shared style.
- `figures/`: figure PDF files and PNG previews.
- `source_data/oeis/`: thirty compact official-source extracts, including names, offsets, dated entry revisions and prefixes.
- `source_context/`: the selected Seed Calculus V convolution section with its original transform convention.
- `evidence/`: source authentication, author checks, independent computations, preservation bridges, final structure and page QA.
- `evidence/edition_v0.2/` and `evidence/edition_v0.3/`: earlier editions' evidence, preserved with their original hashes and scopes.

The v0.2 and v0.3 PDFs are retained as inspected baselines. The current preservation bridge compares all 158 inherited lesson bodies and footers with v0.3. The eight original releases and consolidated traditional manuscript remain in the separate v0.1 consolidation package. This addition does not alter those releases.

## Source and mathematical scope

The OEIS records are pinned to official export commit `2ce625d68f85e35e26e15c0d9681f69280c095e7`, dated 7 October 2026. Identifications and prefix comparisons are distinct from proof of a transform. Compact extracts retain attribution and the OEIS Creative Commons Attribution Share Alike 4.0 license notice. The narrow formula-support record identifies the exact source statements for Apéry, Bell, Fubini, Euler secant/tangent, and partition examples.

Finite FIR/polyphase routing also uses Projector-Resolved Seed Calculus V, Section 4. This is a different source from Special Functions V. Its coarse-delay convention `z^(-m)` is translated to `u^m`. For finite taps, each coefficient sum remains finite even for growing formal sequences; no bounded signal norm is asserted for Fibonacci.

The independent addition audit records exact finite contracts, actual tested ranges, source derivations, and final author-file hashes. Bounded computations verify implementations in the recorded ranges. Known source identities and elementary coefficient derivations support the displayed general formulas. The addition makes no new Lean certification, historical novelty claim, or universal constant-coefficient recurrence claim.

The original special-function correction register and proof boundaries remain active, including zero-depth atoms, character moduli, signed cancellation, Padé hypotheses, recurrence gauges, and the scalar-to-matrix q-Racah comparison. The current source-preservation record pins 23 inherited chapter, generator, and shared-style files. Inherited page inspection is carried forward only after final lesson-body render comparison; the updated headers, opening pages, source pages, and all 13 closing lessons receive final visual QA. Precise final coverage and delivery hashes are in `evidence/FINAL_QA.json`.

The v0.4 independent audit checks the thirteen closing lessons separately from the previous 48-lesson audit. Its general statements have elementary coefficient/state derivations; its exact finite computations validate the displayed implementations in their recorded ranges. The periodic-difference example makes its boundary contract explicit, and the stable-response example makes its analytic response contract explicit.
