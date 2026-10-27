# Paper VII traditional monograph — completed proofreading

**Quantum Seeds and Effective Dynamics**, dated 18 October 2026, is the
154-page current reading edition. The original project title is
*Quantum Seed and Packet Calculus*. It retains the finite core, the complete
strengthened development, all six supplements, three earlier alternative
derivations, and the 40-page worked visual atlas.

All nine files in `parts/` remain. Seven are byte-identical to the retrieved
baseline; two have six documented prose clarifications and two local figure-layout
changes. All 107 complete proof bodies and all extracted mathematical
spans in those parts are byte-identical. The ordered inventory remains 147
statement-like records: 142 numbered and five unnumbered, including 96
theorem/proposition/lemma/corollary records. These overlapping counts do not
measure independent discoveries or expand formal coverage.

Run `python3 build.py` with Python 3, XeLaTeX, xdvipdfmx and BibTeX installed.
The builder stages the complete authored source tree in isolation, runs four
XeLaTeX passes with BibTeX after the first, and emits the PDF once after the
reference passes. `--output-directory DIR` writes products elsewhere;
`--check-only` leaves shipped products unchanged. It regenerates no mathematical
source, figures, data or formal evidence.

The relative `fonts/` path is supported if font files are supplied. Otherwise
styles select installed OpenType P052 and Nimbus Sans faces explicitly, plus
Latin Modern text/math fonts. No standalone font binaries were added to the
retrieved delivery. License notices are retained. See the root README for
requirements and the reason for explicit face selection.

After editing and building this volume, run `python3 map_pages.py` to refresh
`canonical_label_to_final.json`, `current_source_records.json` and the maps in
`evidence/`. They resolve actual printed page labels and physical PDF positions.
Then refresh both guide navigation tables before rebuilding them. The visual
guide needs `make_crosswalk.py --refresh-source-locators`; the Lean guide uses
`navigation.py`. Neither command expands the formal contract.

The 38 atlas plates and the 35 inherited scientific figure identities remain.
Three prior finite illustrations and their exact model data are retained.
Current proofreading and final PDF review are under
`../../verification/proofread_2026-10-18/`. Earlier `evidence/` review products,
`historical_assembly/` and the October 9 monograph reports retain their dated
scope; newly regenerated page maps are current navigation. Use the root
preservation/publication commands for this revision.

The inherited formal contract covers 19 scoped finite items and 323 theorem
declarations in 25 active modules. No fresh Lean compilation ran. The five
continuum conjectures remain open; see the root report for exact scope.
