# ABC computation audit

Date: 8 October 2026. Primary verdict: **implementation and finite assertions verified in the stated ranges**. The approximate analytic checks in the implementation companion are reproduced numerical evidence only. None of these runs proves ABC, constructs the open global arithmetic witness, or repairs IUT III Corollary 3.12.

## Contract and provenance

The scientific questions are whether the recovered exact computations reproduce their archived output, whether the new reader examples use the correct radical and normalization, and whether two delicate local boundaries survive independent controls. Arithmetic is over ordinary integers, rational numbers, or explicitly specified modular rings. Display qualities use floating natural logarithms only after exact integer classification.

The runtime is CPython 3.12.14, built with Clang 22.1.3, on Linux x86_64 with glibc 2.39. The canonical matrix and implementation companions use SymPy 1.14.0. Their approximate polylogarithm checks use mpmath 1.3.0 at 80 decimal digits. The jet replay and the independent census, rank-one and strict-prime controls use the Python standard library only.

Six version 2 computation manifests record the actual argv, UTC start, elapsed time, exit status, input hashes before and after execution, scientific output hashes, logs, and enforced wall-clock and output limits. No random sampling is used except the inherited Wronskian packet test. That test retains `random.Random(20260731)`, the Mersenne Twister generator, and the original sample order. All six manifests passed the current computation-audit validator, with source freshness and output hashes checked against this project root. These recording checks do not authenticate a mathematical theorem.

| Run | Recorded scientific output | Fresh result |
|---|---|---|
| `jet_replay/run` | Latest jet block's exact finite assertions | 149,306 assertion evaluations, scientific output identical to archive |
| `canonical_replay/run` | July final mathematical audit | All seven output groups identical to archive |
| `implementation_replay/run` | Nine canonical implementation groups | All nine groups identical to archive |
| `controls_run` | Independent primitive census and worked examples | 15,198,743 primitive triples, 121 with `c > R` |
| `crt_guard_run` | Individual CRT interval guard | 2,928 comparisons with full finite brute force, all agree |
| `good_prime_run` | Strict good-prime threshold | Named raw/depleted valuation distinction certified |

The original recovered ZIP archives and the files under `abc_sources` were not edited. Replay copies are separate. The jet and canonical mathematical verifiers are unchanged. The canonical implementation audit has exactly two path edits because its original input and output paths point to `/mnt/data`. The adaptation diff is retained at `computation/implementation_replay/path_only_adaptation.diff`. No mathematical code or tolerance was changed.

## Input authentication

`computation/jet_input_authentication.json` verifies all 19 entries in the jet block's SHA-256 manifest. Its original ZIP SHA-256 is `8fa40fc2c39b13ed0eb05fde23a0a08d1e3426b189d0b7ec29b91f51d658bf8c`.

`computation/canonical_input_authentication.json` verifies all 55 entries in the canonical verified package's `SHA256SUMS.txt`, including the main mathematical verifier, its archived output, all seven reference-code files, the coherence corpus, the release metadata, and the historical rendered publication. The canonical package ZIP SHA-256 is `8e0fff13a45cd5f2e9dd0a32384918014b2065a32fda0438c19a1c7278c45b1f`. Its source `MANIFEST.json` is descriptive release metadata rather than a hash inventory, so the checksum file is the authentication authority.

The checked IUT–KTG archive and all 131 of its manifest files were also authenticated during handoff. That separate formal work is described in `FORMAL_STATUS.md`. The redundant copied IUT corpus was moved outside the deliverable. Historical archives retain their original prose and disclosures.

## Latest jet block

The source is the 19 September 2026 `Komorebi_ABC_Jet_Determinant_Block01` verifier. Its six proof notes were read to establish the meanings of the tested objects. The implementation uses `Fraction` for rational determinants and Bareiss integer elimination for modular moment matrices. The shifted matrix is `Li_(i+j+1)`, not the exploratory unshifted variant. Its smallest rank-one case is included.

The fresh replay tested the following finite ranges:

| Family | Exact implemented range |
|---|---|
| Jet coefficients | `m = 0..30`, coefficient indices `k = 1..80` |
| Jet leading units | Primes through 31 at the first surviving depleted index |
| Normalization | Primitive triples with `c = 2..250` and `a < b` |
| Endpoint family | `1 + 2^k = 2^k + 1`, `k = 1..30` |
| Balanced square family | `t^2 + (t+1)^2`, `t = 1..80` |
| Finite Cauchy–Binet | Ranks `1..5`, `K = r..r+4`, arguments `1/3`, `2/3`, `-1/2` |
| Residue-class energy | Primes 2, 3, 5, 7, ranks `1..6`, subsets of the first 11 unit indices |
| Depleted modular determinant | Primes 2, 3, 5, 7, 11, 13, 17, ranks `1..8`, valuations `e = 1,2,3`, units `1,p-1,p+1` |
| Denominator budget | Ranks `1..8`, ordered indices through 300, plus rational determinant checks |
| Stored triangle replay | All 361 stored moduli and phase rows |

The fresh result is 149,306 assertion evaluations, including 504 exact valuation comparisons and 504 nonzero-residue comparisons on the same modular evaluations. Counts are the source's evaluation counters, not a count of distinct theorems or independent proof obligations. Some tests reuse inputs, and the first three endpoint-family square-root checks are vacuous conditional branches. This accounting detail does not change the reproduced output.

The 361 triangle rows verify pairwise coprimality, the gcd product defining the triangle defect, and the stored image-order formula. They do not reconstruct the upstream arithmetic phases from an ABC triple. Their source CSV SHA-256 is `31ca0d62f016adc15b6c12cd8681bd199d9fd6e299110c57f863b856432b405b`.

At rank 2 the explicit budget is `2^7 * 3^3 = 3456`. At rank 3 the nonzero exponents are 27 at 2, 12 at 3, 6 at 5, and 1 at 7. This is the analytic coefficient budget defined by the proof notes. It is not a denominator theorem for a global motivic object.

The exact modular truncation of a depleted moment is justified by its modulus: every omitted index has `e*k` at least the chosen precision and every denominator is a prime unit. The finite residue therefore decides the stated valuation of that explicitly defined depleted series at the tested argument. It does not decide a global ABC inequality.

## Canonical mathematical and implementation replays

The unchanged `final_math_audit.py` reproduced:

| Output | Fresh value | Scope |
|---|---:|---|
| Phase Smith invariants | 152,095 triples | Nondegenerate primitive `a <= b`, `c <= 1000` |
| Polyphase Smith invariants | 195 cases | `N = 2..12`, `e = 1..30`, coprime parameters |
| Wronskian divisibility | 2,499 packets | Seeded null vectors from 2,500 attempts, then primitive reduction |
| Divisor-packet identity | 5,001 cases | Integers `1..4999` and two named large integers |
| Kummer kernel identity | 391 cases | Nonsquarefree `c < 1000` |
| Walsh projector identities | 254 packets | Diagonal involution model, ranks `1..7` |
| Worked weighted packet minimum | 6 | Full cube `[-8,8]^3` for the specified additive row |

The phase audit computes the first determinantal divisor and the gcd of all two-by-two minors over the integers. It does not estimate a rank numerically. The Wronskian test is sampling, not an exhaustive search of a packet lattice. The diagonal Walsh model verifies the algebra of the specified involutions, not an automorphic construction.

The portable implementation replay reproduced all nine archived result groups. Exact values include the following:

| Example | Result |
|---|---|
| Moving search `3 + 125 = 128` | `phi = 8`, `best_k = 1`, exact master gap `1/1` |
| Moving search `1 + 4374 = 4375` | `phi = 62`, exact master gap `248/243` |
| Large-integer control | `c = 5020969537440000`, `phi = 4072242` |
| Contact at 128 | Powerful part 64, Kummer kernel 1 |
| Filtered transfer | Source 64, target 4, kernel 16, image 4 |
| Toy Hecke order | Congruence exponent 144, cotangent order 13824, defect factor 96 |
| Monogenic filter | Projector denominator 90, cotangent order 90 |
| Coherence at `3 + 125 = 128` | Factors `(2,1,1,32)`, row `(29,31)` modulo 32 |

The moving-search minimum 8 and the weighted additive-packet minimum 6 optimize different objects. Neither is substituted for the other. The large-integer control uses arbitrary-precision Python integers and reproduces the archived exact rational gap.

The companion's character-orthogonality residuals, Hecke-moment means, and polylogarithmic distribution and functional-equation residuals are numerical tests. The polylogarithm module uses 80-digit mpmath arithmetic and tolerances `10^-60` or `10^-55`. These checks passed as written but have no certified interval error bound in this release. They are not proof-bearing exact identities. The exact algebraic determinant and symbolic carry-polynomial checks are classified separately.

## Independent census and examples

`exact_controls.py` computes radicals with an integer sieve. It enumerates every positive primitive triple with `a <= b` and `2 <= c <= 10000`. The count is 15,198,743. An independent Euler totient sieve gives the same count, namely one triple at `c=2` plus half the totient sum for `3 <= c <= 10000`.

Exactly 121 of these triples satisfy the integer inequality `c > rad(abc)`. The maximum displayed quality is approximately 1.567887 at `1 + 4374 = 4375`, with radical 210. No floating threshold chooses membership. The CSV contains all 121 cases and the integer histogram records counts by `c` interval and radical bit length. This is a finite census. It supplies no uniform constant and no conclusion about larger triples.

The correct high-quality example outside that census is

`2 + 109 * 3^10 = 23^5 = 6436343`, with radical 15042 and displayed quality approximately 1.629911684.

The initially suggested equality `2 + 3^10 = 23^5` is false. The exact control rejects it. `2 + 3^10 = 59051`, and 59051 is prime. The corrected example was used before publication.

The endpoint-family output records exact radicals and both defects for `k = 1..20`. In each example, `Q/(ab) = c/R` is checked through exact integer multiplication, with `rad(1)=1`. This reinforces the difference between the false target for unbalanced `Q` and the actual ABC defect. It does not replace the written asymptotic counterexample proof.

## Two independent local boundary controls

### Nonempty CRT intervals

The manuscript's aggregate quotient test needs every individual interval to be nonempty. The deterministic counterexample has radical 10, primes 2 and 5, target -1, and height 1. Centered residues are `(-1,2)` and the quotient is 0. The lift intervals are `[0,1]` and `[0,-1]`. Their summed lower and upper bounds both equal 0, so the aggregate inequality alone wrongly accepts the case. Full brute force finds no vector with sup norm at most 1 satisfying `5*x_2 + 2*x_5 = -1`.

The preserved `LocalMovingProfile.n_interval` already checks `lower > upper` and returns the empty interval `(1,0)`. Its exact gauge gives minimum height 2. The new manuscript criterion was corrected to include individual nonempty guards. No archived code was edited. `construct` is normally called after this feasibility check and ends with exact bounds and target assertions.

An independent brute-force oracle enumerates the complete height box for 12 squarefree radicals, targets -30 through 30, and heights 0 through 3. All 2,928 feasibility comparisons agree with the preserved guarded method. Every returned lift passes its exact target and height checks.

### Small primes and the strict threshold

At rank one, prime 2 and argument 2, the raw moment's residues vanish modulo `2^N` for `N = 8,16,32,64`, while the depleted moment has valuation 1. The cutoff is `K=2N`. This supports the written analytic identity `Li_1(2) = -log_2(-1) = 0` and shows why a lower valuation bound alone cannot promise raw nonvanishing at small primes. The finite zero residues are not themselves a proof of that analytic identity.

A second control tests the strict good-prime threshold. At rank 2, prime `5 = 3r-1`, and argument 10, the raw determinant has valuation 4 while its depleted version has valuation 3. At prime 7 and argument 14, both valuations are 3. Exact calculations use precisions 6, 8, 12 and 16.

These named values have a justified infinite-series tail bound. For `p >= 5`, `s <= 3`, and `t=2p`, the inequality `v_p(k) <= k/p` gives `v_p(t^k/k^s) >= 2k/5`. After `K=3N`, every omitted moment term has valuation greater than `N`. All moment terms here are integral, so determinant residues are valid modulo `p^N`. The nonzero residues thus certify the named valuations. The result shows that `p > 3r-1` cannot be weakened to `p >= 3r-1` in the raw exact-valuation theorem. A zero correction budget at the boundary does not force equality.

## Failures and corrected issues

No fresh computation run failed, timed out, or changed a declared execution input. All scientific output comparisons with the two inherited exact audits and the implementation audit matched their archived values.

Three issues are retained explicitly. The historical jet development had a float contamination at the rank-one empty product, detected by the exact Cauchy–Binet test and corrected before its accepted run. The old global target `Q = R^{o(1)}` was mathematically false and was retracted in the September proof notes. The new manuscript's initial CRT aggregate-only wording and the suggested prime-power example were corrected after exact counterchecks. An unverified tentative factorization appeared briefly in a team message and was corrected immediately from the exact factorization output, before any publication used it.

The current formal runtime recovery is separate from the historical missing-compiler failures. Its status is recorded in `FORMAL_STATUS.md` and must not be inferred from the Python result.

## Remaining implication

The structural conclusions supported here are exact normalization, rational coefficient cancellation, finite lattice and determinant identities, and the explicitly tested local valuations. The decisive open step is still a nonzero global arithmetic scalar or determinant-line section with the full local divisibility and the correctly balanced radical-scale height bound. None of the six computational runs supplies that object or applies a product formula to unrelated period values.

The cheapest useful next mathematical check is an explicitly proposed arithmetic realization tested against all the local, normalization, nonvanishing and height gates. Merely increasing the census bound or assertion count would not decide that missing implication.
