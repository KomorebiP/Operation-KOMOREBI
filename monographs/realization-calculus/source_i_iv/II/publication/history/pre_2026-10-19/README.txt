KOMOREBI PAPER II
Modern Monograph — 15 October 2026
Current publication state: READY_WITH_SCOPED_FORMAL_COVERAGE

READING FILES
  papers/Paper_II_Traditional_Final.pdf    80 pages
  papers/Paper_II_Visual_Guide_Final.pdf    26 pages
  papers/Paper_II_Lean_Guide_Final.pdf    48 pages

Start with the traditional paper for definitions and written proofs. Its
twenty-four worked plates also appear in the standalone visual guide. The
Lean guide begins with the current source/evidence correspondence, then
preserves the inherited 25-row declaration-level walkthrough.

CURRENT PROOF SCOPE
Start with READ_FIRST.txt for the current entry points. RELEASE_STATUS.json
records the release gates and scope accepted by the final review.
Current evidence is under verification/release_2026-10-15/.
The current computation report is
  verification/release_2026-10-15/paper2_work/computation_final/reviewed_evidence.json
MONOGRAPH_COMPUTATION_CHECKS.json remains a historical record.
Current Lean sources are under formal/current/. The exact current statement,
proof, target and source-hash map is:
  formal/coverage/Paper_II_Current_Correspondence_2026-10-15.json
Recorded map status: FINAL_SCOPED_CORRESPONDENCE_WITH_TWO_ANALYTIC_GAPS.
Its recorded statuses and release gates are copied into the guide without
being promoted by publication. The general canonical rectifiable functional-
calculus bridge remains separately identified. Consult the current map for
the exact remaining scope; the historical 25-row/160-name contract is not a
count of the enlarged current project.

THIS REVISION
The final proofread clarifies filtration lower bounds, packet hypotheses,
weighted endpoints, finite-length gluing, degree-zero conventions, Smith-chart
domains, and one-sided inverse language. The rectifiable functional-calculus
proof cites the verified Conway source. Every mathematical-token edit is
recorded with its before/after text and audit provenance. Original sources
and historical reports retain their original dates and scope.

PUBLICATION EVIDENCE
The three PDFs build from the current editable sources. Current navigation
comes from the actual traditional PDF and AUX, including named destinations
and printed-page references. The publication manifest binds PDFs, build logs,
and actual local TeX inputs. Page QA and formal replay are separate records.
The inherited October 8 publication metadata remains in publication/history/.

REBUILD
  python3 publication/build_current.py
The current correspondence must match the chapter hashes. XeLaTeX, BibTeX,
bundled fonts, and PyMuPDF are required. Per-edition build.py entry points
compile the packaged sources directly. publication/sync_current_scope.py
renders current evidence; the older guide data generator retains its
historical canonical input. The current date and fixed TeX timestamp are
15 October 2026. No Lean process is invoked by a PDF build.

EDITABLE AND HISTORICAL SOURCES
  editable/traditional/      Paper, figures, atlas, bibliography and fonts.
  editable/visual_guide/     Twenty-four plates and exact model sources.
  editable/lean_guide/       Current scope plus inherited formal walkthrough.
  formal/current/           Current Lean project.
  formal/coverage/          Current and historical scope correspondence.
  publication/              Coordinated builders and publication metadata.
  source/                   Preserved source releases and provenance.

Paper I and the other paper releases are untouched by this package.

FINAL PUBLICATION REVIEW
All 154 pages passed rendering and visual review; current navigation is bound
to the exact PDFs. Evidence: verification/publication_2026-10-15/page_qa/page_qa.json
51 of 53 proof-level scopes are kernel checked and semantically
accepted. 2 analytic scopes remain partial. The remaining bridge covers
rectifiable velocity/geometric-length representation, agreement with the
classical contour integral, and canonical independence. Full Lean coverage
of the manuscript is not claimed. Root RELEASE_STATUS.json records the
separate package-level release decision.
