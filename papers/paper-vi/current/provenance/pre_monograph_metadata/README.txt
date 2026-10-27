KOMOREBI — PAPER VI FINAL COMPANION EDITION
Komorebi P. | October 5, 2026 (America/Chicago)
Transfer semigroups, probabilistic refinement, fractional operators and memory

READING SET
papers/Paper_VI_Traditional_Final.pdf
papers/Paper_VI_Visual_Guide_Final.pdf
papers/Paper_VI_Lean_Guide_Final.pdf
Exact page counts, hashes and file sizes are recorded in EDITION.json.

The traditional paper reconciles three recovered branches. Part I retains the
latest reviewed v0.5.0 core. Part II retains the full strengthened mathematical
development. Part III retains earlier results missing from that development,
with their setup and proofs, and receives the holomorphic operator material
previously transferred out of Paper IV. An explicit crosswalk accounts for all
63 earlier Annals results: 39 are covered elsewhere and 24 retained separately.

The 33 core results, 84 strengthened results, 24 retained earlier results and
one migrated proposition are 142 theorem-like records, with conceptual overlap.
There are 140 explicit proof environments. These counts are not a claim of 142
independent new theorems or an enlargement of the formalization contract.
Definitions, examples, remarks, imported standard facts and open conjectures
are separate from those theorem-like counts.

The visual guide retains all 28 original worked pages and 26 editable vector
plates, and adds explanations of the broader developments. Its mathematical
figures use explicit constructions and computations. The Lean guide provides
the 33-result contract, exact source excerpts, a complete 341-target catalog,
module navigation, and a precise map of human and formal scopes.

FORMAL EVIDENCE
The inherited September 6 v0.5.0 release records 33 complete scoped results,
341 explicit theorem declarations in 47 proof modules, and 782 audited
namespace declarations. Namespace declarations include definitions and
generated declarations; they are not another theorem count. All compiler and
axiom-audit transcripts, dependency pins and original formal sources remain
included. Prose-to-Lean correspondence is manually reviewed.

No fresh Lean compilation or kernel audit was possible in this environment.
Fresh source and inventory checks are explicitly distinguished from inherited
kernel evidence. The broader strengthened, retained and migrated results do
not extend the 33-result formal contract. In particular, bounded Banach-space
holomorphic substitution is broader than the finite-matrix jet construction.

The three broad core conjectures remain open: transfer-semigroup realization,
uniform refinement control, and latent-packet closure. Finite-dimensional and
otherwise restricted results do not establish their unrestricted forms.

FRESH COMPUTATIONAL EVIDENCE
The following available checks ran against isolated copies:
- Six original unittest verifier controls.
- 37 unchanged companion test functions, called directly.
- 17 independently implemented boundary cases, not original pytest dispatch.
- 79 original numerical output fields compared with the saved float results.
- Earlier Annals suite: 475,471 mixed checks in 16 groups.
- Strengthened baseline: 149,349 mixed checks in 14 groups.
- Strengthened expanded suite: 154,608 mixed checks in 15 groups.
- Independent exact rational witnesses: 182 assertions and four false controls.
- Static formal-source contracts, all three archive file sets, all 739
  preserved source files and the 534-file original snapshot inventory.

The three numerical tallies overlap and use different counting conventions;
they must not be summed into a number of independent results. Floating-point
checks use source tolerances and are not interval certificates. Additional
visual-guide checks have a separate report next to the editable guide.

NOT RERUN
Lean/lake, pytest and SymPy were unavailable; no installation was attempted.
The original combined formal gate, full pytest dispatch, original 204 SymPy
visual assertions and 11 false controls, original 19 companion figure-pair
generation and original 26-plate generation were not rerun. Preserved vector
plates were compiled into the new guide. Inherited reports are dated evidence
about their own source releases, not fresh execution reports for this edition.

PACKAGE CONTENTS
papers/ — finalized reading PDFs
editable/ — final TeX, vector assets, source excerpts, navigation and builders
source/ — all three recovered source branches, unchanged
downloads/ — all three original archives
audit/ — original-source review and separate final correction validation
verification/ — current computations, implementation review and PDF evidence
provenance/ — recovery, source selection and assembly records
COMPANION_MAP.json — inventory of navigation and evidence files
CORRECTIONS_AND_SCOPE.txt — explicit correction and scope record
SERIES_STATUS.json — Paper VI closed; Papers VII–XII frozen

REBUILD AND VERIFY
From this package root, with the documented dependencies already available:

  python3 scripts/build_pdfs.py --check-only --report /tmp/paper-vi-build.json
  python3 scripts/verify_integrity.py

Computational replay commands and their exact scope are in verification/README.txt.
Use a new output directory for replay. The builders do not install dependencies.
Original source instructions and locked Lean dependencies remain in the source
trees. Raw source artifacts are deliberately retained, including inherited
outputs. No new license grant is introduced by this editorial package.
