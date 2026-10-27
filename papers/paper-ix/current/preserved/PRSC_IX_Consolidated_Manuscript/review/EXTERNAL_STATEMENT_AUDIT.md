# Nishibuchi external statement and capstone audit

Date checked: 2026-09-08.

Reviewed release: `PRSC_IX_v0.11.0_Nishibuchi_Completion`.

## Claim and verdict

Claim: `KomorebiPaperIX.NishibuchiCompletion.conjecture_3_9` supplies the full statement of Nishibuchi Conjecture 3.9 in the conventions of Definition 2.1, including the suggested sufficient threshold.

**Verdict: proved as written.** This verdict concerns the external statement correspondence and the top-level proof assembly inspected here. The independent reviewer did not run Lean; fresh compiler replay is a separate verification task. No claim of exhaustive human peer review or historical priority follows from this audit.

## External source authentication

- Author: Yuta Nishibuchi.
- Title: *p-adic Congruences of Generalized Euler Numbers and Relations to Even Zeta Values*.
- Exact version: arXiv:2605.10677v2, 1 June 2026.
- Retrieved primary-source locator: https://arxiv.org/pdf/2605.10677
- Authentication: the retrieved PDF's first-page stamp identifies `arXiv:2605.10677v2 [math.NT] 1 Jun 2026`.
- Versioned HTML, PDF, and abstract requests failed with `DisabledError`. The unversioned official PDF successfully supplied full extracted text, and its internal version stamp resolved the version question.
- Relevant locations: Definition 2.1 and Remark 2.3, printed page 3; Notation 3.2 and Remark 3.3, printed page 5; Conjecture 3.9 and Proposition 3.10, printed page 8.
- The release contained no retained original PDF. This review subsequently downloaded the official PDF using an ordinary HTTPS request and authenticated its extracted first-page version stamp. The source and text are retained beside this report as `Nishibuchi_arxiv_2605.10677v2.pdf` and `Nishibuchi_arxiv_2605.10677v2.txt`.
- PDF SHA-256: `e461b77d6d8a78946705b1bcab9f4d5720a6009db2f63537278a0ae0634da95c`; length 398338 bytes. Extraction succeeded with `pdftotext -layout`. Full provenance is in `NISHIBUCHI_SOURCE_RECORD.json`.
- The skill's cache-ingest helper was attempted but could not verify Git ignore coverage, so no helper-managed cache ingestion is claimed. Standalone retention of the explicit review artifacts succeeded.
- Source status: conjectures the general result and proves identified special cases. No wider novelty search was performed.

The source defines the numbers by the reciprocal EGF with denominator coefficients `1/(N*n+j)!`, for positive `N` and `0 <= j < N`. It observes support on multiples of `N`. For prime `p`, positive `m` dividing `p-1` or equal to 2, the conjecture asserts integrality of the packet coefficients and eventual congruence under degree displacement `lcm(2,p-1)*p^r`, for each positive `r`. The adjacent numerical observation suggests a positive threshold at most `r`.

## Notation and normalization

| Source object | Inspected Lean object | Finding |
|---|---|---|
| Degree-indexed EGF coefficient | `NishibuchiCompletion.generalizedEuler N hN j d` | `EGF.decode` multiplies ordinary coefficient by `d!` |
| Original packet coefficient at degree `N*n` | `Congruential.unnormalized N j n` | Identified by `generalizedEuler_at_packet` |
| Normalized packet | `Congruential.coeff N j n` | Constant term 1 |
| Original constant term | `Congruential.unnormalized N j 0` | Exactly `j!` |
| Original section with degrees `N*n+j` | `ExponentialSection.originalSection N j` | Exact residue-selector coefficients |
| Original reciprocal identity | `original_generating_identity` | Original series times section equals `X^j` |
| Congruence modulo `p^r` | `GlobalEulerBoundary.precision p (r:ℤ)` on the rational difference | Zero-safe valuation condition, obtained from ideal divisibility in `ℤ_[p]` |

The normalization is substantive: multiplying the normalized packet by `j!` produces the original sequence. `Congruential.packet_times_kernel`, `ExponentialSection.original_section_factorization`, and `AllResidueEuler.decode_unnormalized` establish this from actual coefficients. There is no substitution of an arbitrary sequence with the desired properties.

The residue restriction is the domain set in Definition 2.1 and again in Notation 3.2. This audit does not extend the conjecture to arbitrary `j >= N` merely because Remark 2.2 discusses an extended definition.

## Dependency graph

1. `Triangular.solve` defines the rational normalized packet and proves its coefficient recurrence.
2. `packet_times_kernel` proves that this packet is the reciprocal of the actual factorial kernel.
3. Expansion by `N` and multiplication by `j!` identify the original EGF and degree-indexed coefficients.
4. The divisor branch uses `all_residue_flat`, `unnormalized_integral`, and `global_unnormalized_bound` from `AllResidueEuler`.
5. The exceptional branch uses explicit odd affine unit inverses in `DyadicFourKernel`, actual reciprocal flatness in `DyadicFourDwork`, and the integral lifts and saturated bounds in `DyadicFourCongruences`.
6. `PeriodFromDifferences.prime_power_period` turns the saturated higher differences into a displacement congruence.
7. `allowed_parameters` exhausts the two parameter branches. `original_degree_shift` converts the packet displacement into the source degree displacement.
8. `conjecture_3_9` combines unrestricted packet integrality with the explicit choice `n0=r` for positive `r`.

The original external conjecture is a statement to be proved, not an axiom or external theorem invoked by the implementation. At the top-level assembly there is no assumed integrality, assumed finite-difference estimate, presumed period, or circular use of the capstone.

## Obligation matrix

| Obligation | Result | Decisive evidence |
|---|---|---|
| Exact external version | Passed | Official PDF's internal v2 stamp |
| Actual coefficient normalization | Passed | EGF decode, `unnormalized = j! * coeff`, generating identity |
| All stated residues | Passed | `hj : j < m*p`; both branches quantified over that range |
| Integrality includes `n=0` | Passed | `∀n` in capstone; no threshold premise on integrality |
| Primality and positive modulus | Passed | `[Fact p.Prime]`, `hmpos : 0<m`, explicit nonzero product |
| Exceptional parameters exhausted | Passed | Odd primes have `2 | p-1`; remaining branch is exactly `p=2,m=2` |
| Positive precision exponent | Passed | Source and capstone both require `r>0`; `r=0` is no omission |
| Genuine integral divisibility | Passed | Period proof uses `ℤ_[p]`, then an explicit rational valuation bridge |
| Exact degree displacement | Passed | `m*p*(n+p^(r-1)*(q/m)) = m*p*n + q*p^r` |
| Positive uniform threshold | Passed | Witness `r`; `0<r` proves positivity; all `n>=r` covered |
| Higher differences to period | Passed | Finite Newton expansion and binomial divisibility, detailed below |
| Fresh Lean replay by this reviewer | Not addressed | Separate parent verification task |
| Full human peer review and novelty search | Out of scope | No such conclusion claimed |

## Higher-difference implication

The proof is finite algebra. Put `t=p^(r-1)`. Newton expansion expresses `f(n+t*h)-f(n)` as the sum over `1<=k<=t` of `choose(t,k)*Delta_h^k f(n)`.

For `k>=r`, the saturated bound gives divisibility by `p^r` directly. For `k<r`, the proof uses `p^r | choose(p^(r-1),k)*p^k`. The latter follows from `p^(r-1) | k*choose(p^(r-1),k)` and `v_p(k)<k`. This includes `r=1`, when `t=1`. It does not require an infinite expansion, convergence, an assumed previous period, or cancellation of a nonunit in an integral ring.

On the divisor branch the bound is `p^min(k,m*n)`, and `n>=r` implies `m*n>=r`. The basic step `(p-1)/m` is multiplied by `q/(p-1)` to produce `q/m`. On the dyadic exceptional branch the bound is `2^min(k,n)` with unit packet step, yielding packet displacement `2^(r-1)` and degree displacement `2^(r+1)`.

## Remaining work and safe conclusion

No missing external-statement implication was found. The initial audit JSON's missing source text is now resolved by inspection of the official v2 PDF and the actual Lean definitions. Fresh compiler verification and durable packaging remain separate engineering gates.

This conclusion does not prove Paper IX's distinct native Conjectures 13.2 and 13.3. It also does not establish least periods, earliest thresholds, or an optimal valuation formula. Those limitations are accurately recorded by the release.

Read-only source inspection used `cat`, `sed`, and `rg` over the active contract, capstone, EGF, exponential-section, all-residue, dyadic, finite-difference, and valuation-bridge modules. Core release files were not edited.
