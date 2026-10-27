# SF-DISCOVERY-100 research closeout

Cutoff and assessment are the same contemporaneous checkpoint,
**SF-DISCOVERY-100**. The authoritative scope and ancestry are recorded in
[TARGET_CONTRACT.json](TARGET_CONTRACT.json): base checkpoint SF-DISCOVERY-001,
source archive SHA-256
`0a1acf60c1f6badc31b6be96dcc94dfd276e5e04ea04e148a5c9d47cee002fc3`.
This artifact-based base is used in the absence of a Git revision or executable
research ledger. [README.md](README.md) is the small current entry point;
the unchanged route files and frozen extensions preserve the detailed history.

The research checkpoint is complete for the claims stated below: five structural extensions, an exact reusable API and catalog, independent mathematical review, and one successful bounded release run. The monograph and atlas present these results together. Historical priority and the explicitly listed next questions remain open.

## Canonical status and preserved baseline

`routes/` preserves the v0.1 / SF-DISCOVERY-001 proof revisions and their original open questions. `new_results/` supplies the current extensions. Its conclusions supersede an old open-status paragraph where the new proof closes that question; the original paragraph remains part of the audit history. The old routes are not silently revised to resemble later results.

The independent audit in [evidence/v1_independent_audit.md](evidence/v1_independent_audit.md) finds all five frozen proof chapters **proved as written under their stated domains**, with no missing implication in the audited claims. This is an informal mathematical audit, not a machine-checked proof certificate.

## Completed claims and exact evidence

| Route | Completed in v1.0 | Proof and computational evidence |
|---|---|---|
| Dilation growth | Positive normalized finite banks have positive lower and finite upper type at the maximum active channel order. Parameters depend jointly holomorphically in the contraction domain, and tap weights have explicit compact continuity bounds. | `new_results/dilation_type.md`; `reports/dilation_type.json` |
| Arithmetic inverse | For `a>1/2`, `beta>0` and positive integer `Q`, equality of exact depth germs is equivalent to equality of `a`, `beta` and `rad(Q)`. Conditional peeling, bounded-window prime instability and fixed-modulus character-sector separation are proved. | `new_results/arithmetic_inverse.md`; `reports/arithmetic_inverse.json` |
| Finite-prime sieve | For real strengths, the measure and all-degree Hankel positivity hold exactly when every `lambda_p>=-1`. Every violation has an explicit finite polynomial negative detector. Conditional fibers, with all other strengths in the positive domain, have roots below `-1` and collapsing nearest margins. | `new_results/multi_prime_sieve.md`; `reports/multi_prime_sieve.json` |
| Orbit spectral zeta | For each integer `N>=2`, the unweighted, multiplicity-aware zeta has exact convergence abscissa `1/N` and global meromorphic continuation. Its only unshifted pole is at `1/N`, with residue `sin(pi/N)/(N*pi)`; its nonpositive-integer values vanish and `Z'_N(0)=-log N`. Nonnegative real shifts have the proved product and, for a positive shift, the full pole ladder. | `new_results/spectral_continuation.md`; `reports/spectral_continuation.json` |
| Sequences and filters | Integer coefficient polynomials and rational denominator clearing are proved. The positive-scale chart includes zero radius above unit scale and entire infinite order on the one-unit edge. Root filters, EGF antiderivative taps, Hurwitz products and carry-preserving polyphase matrices have exact identities. | `new_results/sequence_polyphase.md`; `reports/family_lab_checks.json`; `family_lab.py` |

Report paths in the table are below `evidence/release-run-001/`. Four baseline reports with exact checks and the arithmetic-polynomial numerical report accompany them. The shipped sequence catalog has 18 rows through index 12 and states each row's normalization and scope.

The spectral shift parameter is real and nonnegative. At zero shift only the unshifted pole remains; positive shifts have poles `1/N-k`, `k>=0`, and regularized product `N E_{N,1}(a)`. Zeros are counted with multiplicity and use the fixed principal logarithm. No simplicity of trace zeros is inferred.

## Evidence closeout

All ten scripts passed once in **40.35 seconds**. The run recorded **19,331 principal exact checks + 540 exact helper checks = 19,871 actual exact assertion statements**, and **5,576 numerical assertion statements**. The 61 iteration guards are separate operational bookkeeping. Grouped numerical conditions count once, and subset counters are not added twice.

The schema-2 manifest validator passed against the current files. All 25 pinned inputs and 22 byte-identical snapshot files remained unchanged; all 57 declared results were present and hashed. The external mpmath source tree also remained unchanged. The run used a 600-second wall limit, 2 GiB address space, 300 CPU seconds, one core and cooperative one-thread settings; CPU and memory caps apply per process.

The contract, full bounds and accounting are in [evidence/release_contract.json](evidence/release_contract.json), [evidence/release_summary.md](evidence/release_summary.md) and [checks/RELEASE_CHECKS.md](checks/RELEASE_CHECKS.md). The manifest, hashes, validator record, logs and complete reports are preserved in `evidence/release-run-001/`. Finite checks support implementations within those ranges. Universal analytic conclusions rest on the proofs, and ordinary high-precision calculations are not interval certificates.

## Repairs and history retained

Independent review reproduced acceptance of a fractional section residue and an empty zero-base phase matrix. Both invalid inputs now raise `ValueError`, with dedicated passing regressions. Two draft sequence integers were corrected against the exact catalog. These findings and repairs are recorded in the mathematical audit and sequence chapter.

Earlier failures remain visible: the arithmetic-polynomial report keeps the failed absolute determinant-residual test and successful scale-normalized replacement; the inverse report keeps a failed primary-page retrieval and authenticated substitute. The v0.1 histories retain the known one-dilation overlap and earlier environment, plotting and manuscript corrections. No current aggregate failure is hidden or removed; the release run has none.

## Exact remaining questions

| Route | Still open or outside the proved scope |
|---|---|
| Dilation | A single type limit, its leading constant or logarithmic modulation; zero and connection-formula theory; general minimal-bank identifiability; growth claims for signed banks. Positive lower type is now closed. |
| Arithmetic inverse | Stable finite-data recovery within specified bounded parameter classes and control of uncertain prior atom subtraction. Exact germ recovery does not certify an unbounded prime list from noisy finite observations. Character estimates are fixed-modulus, not uniform in growing `Q`. |
| Sieve | Optimal negative-detector degrees, sharp all-root asymptotics and multiplicities, and a full multivariate singular-surface or real-stability theory. Conditional roots may repeat; the nonreduction statement uses the same nodes and variable. |
| Spectral | Functional equations, residue- or derivative-weighted zero sums with separate multiplicity and convergence control, and any RH-type property. Global continuation of the unweighted orbit family and its nonnegative real shifts is now closed. |
| Sequences and priority | OEIS comparisons or accessions, and broad historical comparison of the candidate extensions. The catalog itself makes no novelty assertion. |

Historical priority remains unresolved throughout the candidate extensions. The one-dilation definition is known, and the major transform, moment and spectral mechanisms are classical. Scoped nonreduction results and successful checks do not convert those facts into a global novelty certificate. The remaining questions are later research routes, not omitted dependencies of the completed claims.
