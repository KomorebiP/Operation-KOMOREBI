# Final supplement review

Checkpoint **SF-DISCOVERY-001**. Review-only final mathematical proofreading and content consistency review on 2026-10-08 UTC. The reviewer did not edit the manuscript or the audited route files. This review compares the 17-page rendered supplement with the already audited mathematical routes and finite evidence; it is not an exhaustive historical-priority search or a replacement for the independent proof audit.

**Final verdict: no objective mathematical or content-consistency issue remains in the reviewed supplement.** The two hypothesis/definition clarifications and the citation correction listed below were incorporated by the author, together with one decimal display correction. The definitions, displayed domains, coefficient laws, examples, restricted nonreduction statements, and novelty classifications agree with the audited routes.

## Findings resolved before the pinned revision

1. The initial tap-bank summary omitted the word **finite**, although its raw route and independent theorem audit assumed finitely many channels. The final text explicitly specifies finitely many channels indexed by `j=1,...,J`. The maximum-order theorem is therefore stated within its proved scope.
2. The transport summary named shifted Hankel determinants without defining their indexing or the degree-zero convention. The final manuscript supplies `tau_m^(k)=det[M_(k+i+j)]_(i,j<m)` and `tau_0^(k)=1`, making the `m=1` Desnanot–Jacobi identity self-contained.
3. The initial reference map used the descriptive phrase “Path-length and q-analogs” as a title for Méndez's paper. It now gives the actual title, *Combinatorial differential operators in: Faà di Bruno formula, enumeration of ballot paths, enriched rooted trees and increasing rooted trees*. Its source locator and Example 2.4 reference match the authenticated route and independent review.
4. Independent 85-digit coefficient evaluation gives `T_(1/3,2/3)(1)=1.0759239897408249150209596749139764...`. The supplement's 16-place display was corrected from `1.0759239897408248` to `1.0759239897408249`. This is a uniquely forced decimal display correction, not a change of a defining formula or theorem. The audited raw route retains its older approximate display; the route's stated analytic truncation bound is separate from its floating decimal conversion. That unchanged last-place approximation is not used in a proof.

The previously corrected `N=4,k=3` denominator is verified as `691/9979200` and appears correctly in the final supplement.

## Independent exact examples

Without importing any author check script, the reviewer implemented the defining coefficient convolution with Python standard-library `fractions.Fraction` and obtained:

| Example | Coefficients of `z,z^3,z^5,z^7` |
|---|---|
| `T_(1/3,2/3)` | `1, 2/27, 4/2187, 232/11160261` |
| Bank `(h,q,r)=(1/4,1/4,1/4),(3/4,3/4,3/4)` | `1, 7/48, 427/30720, 176681/188743680` |

Thus the first worked bank agrees exactly with its defining feedback recurrence. Its most expansive active channel is `(3/4,3/4)`, so the already proved finite-bank theorem gives order `log(2)/log(4/3)`, not a weight-averaged characteristic equation.

The `N=2,3,4,5` spectral table was also independently recomputed from `a_n=(-1)^n/(Nn)!` and the triangular log-derivative recurrence. Every displayed entry agrees:

| N | First | Second | Third |
|---|---|---|---|
| 2 | `1/2` | `1/6` | `1/15` |
| 3 | `1/6` | `1/40` | `53/13440` |
| 4 | `1/24` | `17/10080` | `691/9979200` |
| 5 | `1/120` | `5/72576` | `997/1743565824` |

These checks are bounded implementation checks, not analytic proofs of the infinite root sums.

## Independent N=4 factorization

The identity `D_4(z)=cos(z/sqrt(2))*cosh(z/sqrt(2))` is exact. Write the product as one quarter of the four exponentials `exp((±1±i)z/sqrt(2))`, with the four sign choices. Their exponent slopes are the four rotations of `exp(i*pi/4)`. Summing Taylor coefficients annihilates every degree except `4n`, where the coefficient is `(-1)^n/(4n)!`. This proves the identity at every degree and hence everywhere by entire convergence. A separate rational convolution checked those coefficients through degree 32.

The cosine zeros lie at `z=sqrt(2)*pi*(j+1/2)` and the hyperbolic-cosine zeros at their imaginary rotations. Each orbit therefore has the single positive coordinate `w_j=(sqrt(2)*pi)^4*(j+1/2)^4`. The supplement's Hurwitz-zeta reduction follows within the stated initial half-plane; it does not presume simplicity for general `N`.

## Numerical displays and finite evidence

Independent 85-digit evaluation reproduces the complex-depth example as

`A_(2,2,1)(1/2+i/4) = 0.060331832893434017916580279067114453 - 0.0074123840537854362519812489378992369 i`.

The displayed order of the `(3/4,3/4)` channel agrees with `2.4094208396532090045824043308124365...`. These are ordinary high-precision calculations, not interval certificates.

The prime-sieve evidence agrees with the supplement's precision, grid, degree and check counts: 160 working digits, 60 parameter cases, degree through 6, 1,260 orthogonality conditions, 24 Uvarov cases, 60 depth transports and 48 tau identities. The exact assertion sum is arithmetically consistent: `1811+1218+301+138=3468`. Numerical tests are kept separate. The source record distinguishes the failed original absolute determinant criterion from the dimensionless replacement, and the manuscript retains that distinction.

## Coverage and final validation

Reviewed every displayed formula and table in `main.tex`, with nearby hypotheses, notation and prose; checked the 17-page PDF text structure and all three page contact sheets; compared the five raw routes, independent audit, weak-tap note and available figure/numerical evidence. No clipped content or blank spill page was seen in the contact sheets. The final log has no undefined references or overfull boxes.

The strict half-plane and principal-power convention for the orbit series, deleted `n=1` atom at complex depth, finite positive tap hypothesis, sieve endpoint `lambda>=-1`, degree-zero kernel convention, restricted D-finite exclusions and absence of a historical-priority claim are all preserved. The asymptotic beta approximation is explicitly distinguished from an exact identity. The weak-tap compact-convergence proof uses the entire coefficient majorant and does not imply a uniform approximation on an unbounded domain.

Routine manuscript edits by reviewer: **none**. Mathematical-token edits by reviewer: **none**. Unresolved objective proofreading issues: **none**. Historical priority remains unresolved as explicitly stated. The present review did not independently repeat the full bounded literature search, and external theorem authentication remains with the pinned independent audit.

## Revision pins

| Artifact | SHA-256 |
|---|---|
| `main.tex` | `ad42665ade193ad193a333dda856afe6c4e24853e2222dd61a473bae323bc2c2` |
| `main.pdf` | `214009cf71a41090f01f396fae5b566b0d22f1f726ad656e439a466424c7f86f` |
| `routes/asymmetric_dilation.md` | `5956a622393e36f646a15c4a1c439c1a2682c53eb52e198a1f4463e190925911` |
| `routes/nonlinear_dilation.md` | `2e9c83a7d5ecb46861b83ea1e46c231def02aec74a787344af4adc6d1593c9af` |
| `routes/complex_depth.md` | `eca782880926cd3089eb83628b8b4746a8206f0d9c048dbe892deb192a4e0cc3` |
| `routes/arithmetic_polynomials.md` | `69fa99ae14c672973565449bd0f50bae9794da1ddf1305cf33c5b857db75be78` |
| `routes/orbit_zeta.md` | `8b7bba5ec2805db7c322fc56a200cb9859beb5e412c4b16185299a665903bfe1` |
| `evidence/weak_tap_note.md` | `c307b3eca965f49a594882e9316dee03fcd534fa431762349310c56fc818f2ba` |
| `evidence/independent_math_review.md` | `a666d0d39c7a3c496caf1be1038ca3f0510c5915b09a0ce1fe76d2b575a19337` |
| `evidence/arithmetic_polynomial_checks.json` | `18491dca5e24aa7d979e8cebcb838831bfa517bfaf23034f598b6afe29b52278` |
| `evidence/figure_computation.json` | `5635e609d738e0cec81a3110516b7be110f01aa79fe1b84ec27d5bfdd5e81aa7` |
| `evidence/tap_figure_computation.json` | `07ada4aa07331d78fd96a2edd37d8b1a75058ce4e9d8e98cd43936cceb036e6c` |
