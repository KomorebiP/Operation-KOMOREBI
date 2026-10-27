PAPER V FINAL RELEASE 1.2.0
Komorebi P. | 20 October 2026
Multiresolution Signal Calculus
Exact coordinates, singular packets, and stable reconstruction

STATUS
Closed within the documented publication and finite formal scope. The repaired October 11 derivative is now integrated into the canonical Paper V package. The build no longer requires absent packaged fonts. A strict verifier checks every shipped file, including exact membership, paths, sizes and SHA-256 values.

READING SET
papers/Paper_V_Traditional_Final.pdf: 131 pages.
papers/Paper_V_Visual_Guide_Final.pdf: 43 pages.
papers/Paper_V_Lean_Guide_Final.pdf: 60 pages.
Total: 234 pages. Matching copies are in publication/pdfs/.

CHANGES
All 83 existing proof environments and 118/119 numbered mathematical records are byte-preserved. Standard Fact E11.1 now presents the precisely normalized square-wave Gibbs example, an elementary midpoint-sum derivation and an authenticated NIST reference. The retained-packet theorems are unchanged. Both guides and the integrated atlas use the final manuscript locators. A small tree-label collision and sparse tutorial spill pages are repaired without changing mathematical text or data.

EVIDENCE
verification/closeout_2026-10-20/ contains fresh finite execution, static source reconciliation, isolated PDF replay, publication QA, strict-verifier controls, dependency controls, source preservation and retained failed attempts. Earlier verification/monograph_checks/ and audit/ records remain dated history; they are not newly performed audits. New finite results are not added to inherited theorem counts.

FORMAL BOUNDARY
The formal contract is 20 scoped manuscript results, 225 targets and 23 proof modules. September 6 compiler evidence is inherited. No fresh Lean compilation is claimed by this closeout. The 63 broader prose proof records do not add formal coverage. Stable edge-packet recovery and the edge-packet approximation-class conjecture remain open. The separated-jump results retain their explicit model, gap and grid assumptions.

REPRODUCTION
python3 -B scripts/verify_release.py --report /absolute/path/outside/package/release.json
python3 -B scripts/verify_integrity.py --strict
python3 -B scripts/build_pdfs.py --check-only --report /absolute/path/outside/package/build.json
python3 -B scripts/replay_finite.py --output /absolute/path/outside/package/new_finite_run
python3 -B scripts/test_integrity.py --evidence /absolute/path/outside/package/new_controls

The PDF builders require Python 3, XeLaTeX, BibTeX, the declared TeX packages and externally installed fonts resolvable by kpsewhich. Font bytes are verified in temporary staging and never downloaded or installed. See FONT_DEPENDENCIES.txt. Finite replay additionally requires NumPy, pytest, SymPy and mpmath; the receipt records tested versions. No dependency binaries or Lean runtime are bundled.

HISTORY AND SCOPE
The 17 missing October 5 verification artifacts remain accurately inventoried in provenance/HISTORICAL_RECOVERY_GAPS.json. Current mathematical manuscripts, figures and original Lean sources are present. New runs cannot authenticate lost historical bytes. The older monograph-preservation comparator expects every original background record unchanged; use the current closeout source-preservation record for this expressly documented E11.1 replacement.

LICENSE
Original code and machine-readable material: MIT. Original papers, guides, figures, prose and editable sources: CC BY 4.0. Code listings also MIT. Third-party notices remain applicable. See LICENSE.md and LICENSE_STATUS.json. Individual PDFs have adjacent .license notices. Current grants supersede historical restrictive notices for original project material included here.

Progress and restart: PROGRESS_LEDGER_v1.2.0.txt. This release changes Paper V only.
