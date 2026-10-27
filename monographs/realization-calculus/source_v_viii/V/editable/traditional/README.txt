PAPER V — MULTIRESOLUTION SIGNAL CALCULUS
Modern monograph edition, 20 October 2026

Paper_V_Traditional_Final.pdf is the 129-page reading volume. Part I keeps the released twenty-result formal core. Part II keeps the complete sixty-three-proof extended branch with E-prefixed section and result numbers. Part III integrates all forty visual plates, identified by V1 through V40. The two broad edge recovery conjectures remain open.

All 83 proof environments and 118 of the 119 numbered records are preserved byte for byte from the preceding publication source. Standard Fact E11.1 is now a precisely scoped square-wave comparison with an elementary derivation and an authenticated NIST reference. The prior mathematical repairs remain documented in EDITORIAL_CHANGES.json and the corrected-source patches. MONOGRAPH_EDITING_NOTES.json records this edition's prose, presentation and rendering changes.

The formal evidence is the inherited September 2026 release: 225 registered theorem targets supporting the twenty core results. No fresh Lean compilation is claimed. The broader E-prefixed prose results do not extend that formal contract.

BUILD
Run python3 build.py with XeLaTeX and BibTeX installed. The builder copies this complete tree, including vector assets, to an isolated working directory and runs four XeLaTeX passes. It preserves authored prose and mathematical sources. The --check-only option compiles without replacing delivered output. The legacy --assemble flag compiles the authored volume without running historical assembly. Earlier source and builder snapshots are kept under historical_assembly for provenance.

FIGURES
Run python3 generate_monograph_figures.py to reproduce the three additional exact-model figure pairs using Python, NumPy and Matplotlib. Rational cancellation and bounds use fractions.Fraction, and integer address checks are exact. Their finite scope is recorded in monograph_figures/FIGURE_MODELS.json.
Run python3 generate_readable_heatmaps.py to reproduce the four presentation-only readability changes from unchanged original plotting models. Historical research figures and source snapshots are retained separately.
The complete visual atlas source is atlas-pages.tex and its vector assets are in visual_graphics. It corresponds to the separately delivered visual guide.

NAVIGATION AND VERIFICATION
Run python3 audit_and_crosswalk.py after building to update manuscript locators and prior raw-to-corrected source crosswalks. Printed locators are resolved against actual PDF page labels. It requires PyMuPDF. canonical_label_to_final.json and manuscript_record_to_final.json map both branches; VISUAL_ATLAS_LOCATORS.json maps every V plate in this volume.
qa_monograph.py renders contact sheets and checks text bounds. Human visual inspection is separately recorded in VERIFICATION.json. The complete final review and bounded computation evidence are under the package's verification directory. Finite checks are not universal proofs.
