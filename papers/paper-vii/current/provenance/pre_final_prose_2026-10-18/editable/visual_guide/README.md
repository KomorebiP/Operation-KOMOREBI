# Paper VII visual guide — completed proofreading

The current 42-page guide has a cover, one route page and all
40 worked visual pages. Their bodies match the integrated traditional atlas,
and all 38 duplicated editable TikZ plates agree. The October 18 corrections
clarify parity conjugation and the number of displayed arrays, replace a scalar
dimension tensor-product symbol with multiplication, and repair three label or
arrow placements. The supplied generator sources reflect those corrections.

`Paper_VII_Visual_Guide_Final.tex` is the current entry point. `source/front.tex`
supplies the routes; `source/pages.tex` and `source/extended_pages.tex` supply
the worked pages. Run `python3 build.py` with the dependencies in the root
README. The builder stages sources in isolation, performs four XeLaTeX passes,
and emits one final PDF through xdvipdfmx. It accepts `--output-directory DIR`
and `--check-only`. Fonts resolve from relative files if supplied, otherwise
from explicitly selected installed OpenType faces; standalone font binaries
are not included. No scientific program is rerun by a PDF build.

After rebuilding the traditional volume and its page map, run
`python3 make_crosswalk.py --refresh-source-locators`, rebuild this guide, and
run `python3 make_crosswalk.py` once more to pin the final PDF identity.
The JSON/CSV crosswalks retain all 80 declared reading targets for 40 V-pages,
with actual printed labels and physical positions. The atlas omits those
standalone locator arguments, so its layout has no crosswalk dependency.

The exact symbolic/rational computations under `checks/` and the October 9
v2 manifests remain dated, bounded earlier evidence. They were not rerun during
this proofreading. Generating vector plates is distinct from checking their
mathematics. Existing programs and raw results remain supplied; the original
symbolic generator requires SymPy. The current source and visual acceptance
reports are in `../../verification/proofread_2026-10-18/`. Older PDF QA and
preservation reports retain their original source/PDF pins.

The inherited formal contract has 19 scoped finite items; its compiler evidence
remains inherited. All five original physical continuum targets remain open.
The guide does not expand the formal contract or prove physical existence.
