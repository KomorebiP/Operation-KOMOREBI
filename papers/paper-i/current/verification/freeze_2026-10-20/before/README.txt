Paper I: release edition
Komorebi P. | 15 October 2026

Read the three current companions
  papers/Paper_I_Traditional_Final.pdf — 105 pages
  papers/Paper_I_Lean_Guide_Final.pdf — 44 pages
  papers/Paper_I_Machine_Native_Final.pdf — 100 pages

The traditional manuscript contains the mathematics, examples, 10 main
figures and 22 visual atlas plates. The guide explains the formal sources and
verification. The machine companion contains the current 108-record catalog.

Release status
  All 69 proof-level records have complete formal correspondences at their
  stated scopes; none remains partial or unmapped. See RELEASE_REPORT.txt,
  RELEASE_SUMMARY.json and formal/evidence/RELEASE_VERIFICATION.json for exact
  verification counts and boundaries. The 96 exact visual checks, 33 companion
  tests and 10 regenerated PDF/PNG figure pairs passed. All PDFs were checked.

Current source and evidence
  editable/traditional/ — manuscript, figures and atlas sources
  editable/lean_guide/ — current guide and historical contract tutorial
  editable/machine/ — current catalog renderer and scoped runtime exposition
  formal/current/ — complete current formal source closure
  formal/coverage/COVERAGE_108.json — exact current statement correspondence
  formal/evidence/ — accepted formal verification and semantic reviews
  verification/PUBLICATION_QA.json — final PDF hashes and visual checks
  COMPANION_CROSSWALK.json — all 108 records across current companions

Rebuild the PDFs
  python3 scripts/build_pdfs.py --check-only
Requires Python 3, XeLaTeX, pdfLaTeX and the packages/fonts named in the
component build notes. This keeps rebuilt PDFs under build/. Omit --check-only
to replace papers/, publication/pdfs/, and the editable PDF outputs from the
included current sources.
The generator reads the current inventory and accepted verification receipt;
rendering the documents does not run Lean or change formal coverage.

Check file identity
  python3 scripts/verify_integrity.py
The checksum manifest is for the delivered release. Rebuilding files can change
PDF bytes; preserved evidence still identifies its own original inputs.

Historical material
  source/traditional_v1.3.1/ and source/machine_v1.0.1/ preserve earlier source
  and execution evidence. Their historical maps and version numbers retain
  their original scope. Current release status is provided at the paths above.
  Earlier proofreading and correction reports under verification/ are history.

Formal replay requires the separately provisioned pinned Lean 4.34.0-rc2
runtime and dependency cache. See the formal build instructions. The release
does not claim an independently implemented kernel or universal Python tests.
