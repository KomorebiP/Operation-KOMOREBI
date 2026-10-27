# Independent visual-guide data QA

Date: 8 October 2026. Verdict: **PASS within the stated finite-data and presentation scope**.

All 24 spread bodies were read. The 25-page rendered guide was inspected in contact sheets, and physical PDF pages 10–25 were inspected individually at full resolution. Final page 22 was reinspected after its figure correction. Root separately inspected the earlier full-resolution pages. No unresolved arithmetic, hypothesis, misleading count, clipped label, or paint-over issue was found in this pass.

The independent checker `computation/guide_data_qa.py` does not import the figure generator. It passed 429 comparisons using integer and rational arithmetic for proof-bearing data. Its direct signed-permutation determinant expansion checks the displayed contact orders and leading fractions through rank five, independently of the generator's Cauchy–Binet implementation. Symmetric subset sums check the jet polynomial coefficients, and direct finite moment multiplication checks the positive rank-two example.

The checked data include the radical and balanced normalization, the exact `2 + 109*3^10 = 23^5` example, all 121 plotted census rows, the LTE lower-bound family, all nine toy cyclic assignments, Fermat height coefficients, jet coefficients, unit-residue collision energies, the rank-two denominator budget, and the truncation congruence. The 15,198,743-triple count is reused from the authenticated completed census, rather than re-enumerated in this QA. Every plotted row's radical, coprimality, domain and exact `c > R` classification was independently checked. Floating quality values and chart coordinates are display data only.

The prose retains the necessary distinctions: `a <= b` and `c <= 10000` for the census, the cyclic chart's toy domain, fixed prime support versus uniform ABC, coefficient norm versus arithmetic height, fixed-rank Fermat normalization, real positivity only for `0 < t < 1`, strict `p > 3r-1`, possible raw zeros at small primes, and a conditional global witness. The status panel was checked against `LITERATURE_CHECK.md`. This pass does not independently re-audit the full IUT argument or survey mathematical acceptance.

Two Figure 21 presentation issues were corrected before the final pin. Its valuation annotation now includes `v_p(t)=e>=1`. Its lower copper note was moved rightward from behind the prime-three bar. Full-resolution final page 22 shows every letter clearly. The initial QA checker's loop bound was also changed from a floating square root to exact `isqrt` during self-review, before final recording. All 429 results remained unchanged.

The final version 2 record is `computation/guide_data_run/manifest.json`. It validates with input freshness and output hashes checked against the project root. Its result and all source/data pins are in `computation/guide_data_run/results.json`, with validation output in `computation/guide_data_manifest_validation.json`. The superseded preliminary QA run is retained outside the deliverable as scratch work. The figure generator's independent final execution record is `visual/computations/atlas-final-v1.0b/manifest.json`.

Key SHA-256 pins are:

| File | SHA-256 |
|---|---|
| Final guide PDF | `56706de139b5211dc5cc06f227d5605d055fcd3891d08e46b447440ae7166856` |
| Guide body | `c4b97cebe9e9686c8b9896ec690e4885231ba837fa86df7bf254cfea7deb30a6` |
| Figure generator | `577720ded003558abac5b0e7197916a2cf36b914a5642d9a923a65864c33dfb0` |
| Figure data | `23c2819004a7a6afeff36c2165f9346efa632eaa0115b45625693fa1683e6bb5` |
| Plotted census CSV | `3aad073f34947a9fe7e9ba950482e6c7882189951f460f44f3032c1a9716b882` |

This QA supports the displayed finite data and their declared interpretation. It does not replace the universal proof audit, create a global arithmetic realization, or prove ABC.
