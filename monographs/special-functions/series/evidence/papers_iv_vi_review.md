# Papers IV–VI: consolidation review

Reviewed 2026-10-07 against the complete current TeX manuscripts, their README files, source/claim maps, release audits, and stored result ledgers. This is a consolidation review with two focused statement checks. It is not a fresh universal proof audit, novelty review, full bibliography check, or Lean certificate.

## Authoritative source locators

All paths below are relative to `/workspace/scratch/de82c13900d1/special_function_sources/extracted/`.

| Volume | Canonical manuscript | SHA256 | Released pages / figure pairs |
|---|---|---|---:|
| IV | `Projector_Generated_Special_Functions_IV/Projector_Generated_Special_Functions_IV_Release/Projector_Generated_Special_Functions_IV.tex` | `c763a4e9bd48b993656db61ca19769ab1d7fe5c3ca8831363a4744806d5d8663` | 55 / 28 |
| V | `Projector_Generated_Special_Functions_V/Projector_Generated_Special_Functions_V_Release/source/Projector_Generated_Special_Functions_V.tex` | `dac902175f364c901e28aebc2889a5225b7c6fbf3fa78923a98e2ce86170cd7e` | 52 / 26 |
| VI | `Projector_Generated_Special_Functions_VI/Projector_Generated_Special_Functions_VI_Release/Projector_Generated_Special_Functions_VI.tex` | `bedb868d40f29b6f0e4c4f92fc35890379ba05f2a44ee0e5121bf33db37fc96b` | 54 / 28 |

The source theorem environments have **no theorem-specific LaTeX labels**. The numbers below follow the source chapter and shared theorem counters; figure labels do exist. Consolidation should assign stable theorem IDs while preserving these original numbers/names in its claim index.

## Core mathematics and original theorem names

### IV: arithmetic depth-time and the signed continuation

The signed seed is `C(k,t)=sum mu(n) chi(n) n^(-a-it) (1-n^(-beta))^k`, initially `a>1`, `beta>0`. Its time-average correlation is the positive squarefree kernel with weights `mu(n)^2 |chi(n)|^2 n^(-2a)`. The squarefree counting density gives a complex Beta asymptotic and the shape `alpha=(2a-1)/beta`. The separate time and scale limits are slices of the joint phase-space formula proved in V.

| Claim | Original location | Role |
|---|---|---|
| Exact time-average identity | IV Theorem 2.1, line 286 | Connect signed amplitude with positive diagonal correlation |
| Positive-definite packet kernel | IV Theorem 2.2, line 309 | Gram lift |
| Finite-difference coordinate formula | IV Theorem 3.1, line 365 | `D_xi(s)=L(s,xi)/L(2s,xi^2)` |
| Uniform complex packet asymptotic | IV Theorem 4.1, line 435 | Beta main term plus counting-error bound |
| Equal-depth dephasing | IV Corollary 5.1, line 513 | Gamma characteristic function after carrier removal |
| Polygamma cumulants | IV Corollary 6.1, line 610 | Limiting logarithmic frequencies, with stated moment-convergence proviso |
| Universal scale overlap | IV Theorem 7.1, line 658 | `sech^alpha(0.5 log(k/ell))` |
| Character depth-time decoherence | IV Theorem 8.1, line 728 | Nonprincipal character square-root bound, comparable depths |
| Parameter-shift equation | IV Theorem 9.1, line 815 | Signed resolvent recursion |
| Borel–Riesz bridge | IV Chapter 10, line 851 onward | Ordinary versus exponential generating coordinates |
| Finite signed Padé reduction | IV Theorem 11.1, line 898 | Exact rational 2m-moment contract under Hankel nonbreakdown |

The `n=1` packet is explicitly isolated in IV Chapter 12. Its scale generator would otherwise have an infinite eigenvalue. The remaining RH boundary is the principal coherence `|c_k|^2/E_k=O_epsilon(k^epsilon)` for every positive epsilon. This is consistently stated as open.

### V: the exact phase-space atlas

V combines IV's separate limits into one Gamma–sech ambiguity. Its normalized log-Gamma window generates the Fourier Meixner density, Wigner Bessel formula, Laguerre–Meixner–Pollaczek dual basis, uncertainty, and common positive discrete-series ladder.

| Claim | Original location |
|---|---|
| Joint arithmetic phase-space limit | V Theorem 1.1, line 243 |
| Normalization | V Proposition 2.2, line 369 |
| Exact ambiguity formula | V Theorem 3.1, line 404 |
| Real phase-space nonvanishing | V Corollary 3.2, line 447 |
| Shape shift | V Proposition 3.3, line 466 |
| Pöschl–Teller equation | V Theorem 3.4, line 491 |
| Fourier transform of the log-Gamma packet | V Theorem 4.1, line 540 |
| Exact characteristic function | V Corollary 4.2, line 582 |
| Closed Wigner formula / Exact marginals | V Theorem 5.1 / Corollary 5.2, lines 615 / 649 |
| Exact moments and uncertainty / Constant quantum geometric tensor | V Theorem 6.1 / Proposition 6.2, lines 678 / 748 |
| Orthonormality | V Theorem 7.1, line 803 |
| Laguerre–Meixner Fourier duality | V Theorem 8.1, line 855 |
| su(1,1) relations | V Theorem 9.1, line 917 |
| Fractional binomial orbit / Fractional-depth generator | V Theorems 10.1 / 10.2, lines 995 / 1020 |

V broadens the positive arithmetic domain to `a>1/2`, whereas its signed/fractional Möbius series still requires `a>1`. Uniform arithmetic convergence is on compact positive depth-ratio sets and compact real time sets. V Conjecture 13.1, line 1148, restates the principal signed coherence target.

### VI: shape composition, refinement, and smoothing

VI treats the positive shape as an independent continuous coordinate. Unequal shapes yield an exact cross-ambiguity. Its energy factorizes into beta-logit displacement and Meixner frequency. Shape addition produces a convolution semigroup, polynomial refinements, martingales, and a diagonal singular system. The coherent frame yields a separable Berezin smoothing kernel and a Gaussian limit after rescaling.

| Claim | Original location |
|---|---|
| Normalization | VI Proposition 1.1, line 236 |
| Cross-shape Gamma–sech formula / Strict shape affinity | VI Theorem 2.1 / Proposition 2.2, lines 270 / 334 |
| Exact cross-spectrogram factorization | VI Theorem 3.1, line 387 |
| Meixner shape semigroup / Two-step density ladder | VI Theorem 4.1 / Proposition 4.2, lines 429 / 452 |
| Lévy–Khintchine representation / Bernoulli cumulant law | VI Theorems 5.1 / 5.2, lines 483 / 528 |
| Two-child packet refinement | VI Theorem 6.1, line 594 |
| Multinomial packet refinement / Coassociativity | VI Theorem 7.1 / Corollary 7.2, lines 666 / 701 |
| Polynomial martingale law / Cocycle and compactness | VI Theorem 8.1 / Proposition 8.2, lines 739 / 794 |
| Cross-shape coherent overlap / Continuous tight frame | VI Theorems 9.1 / 9.2, lines 846 / 869 |
| Exact Berezin factorization / Injectivity and ill-posed inversion | VI Theorem 10.1 / Corollary 10.2, lines 931 / 992 |
| Gaussian marginal limits / Heat-operator limit | VI Theorem 11.1 / Corollary 11.2, lines 1025 / 1051 |
| Diagonal metric coefficients | VI Proposition 12.1, line 1075 |

VI's final geometry proposition states the three **diagonal coefficients**. It should not be paraphrased as asserting that the full shape/translation/modulation metric has no mixed terms.

## Consolidation recommendation

Use one spine, with each definition introduced once:

1. **Arithmetic depth-time system:** signed transfer, positive Gram lift, squarefree L-ratio, common Beta asymptotic, joint Gamma–sech limit, character sectors. Keep the complete signed resolvent/Padé/RH material as its own branch.
2. **Exact Gamma packet atlas:** normalized log-Gamma packet, ambiguity, Fourier density, Wigner formula, polynomial bases, uncertainty, and ladder operators. Retain the Fourier and Weyl conventions beside the defining formulas.
3. **Shape composition and transfer:** cross-shape ambiguity, factorization, convolution, beta-binomial/Dirichlet-multinomial refinement, martingale, compactness/Schatten thresholds.
4. **Coherent smoothing and limits:** tight frame, reproducing kernel, Berezin multiplier, inverse instability, standardized Gaussian/heat limit.

IV's equal-depth Gamma formula and scale overlap become specializations of V's joint formula. VI normalization duplicates V normalization. VI's equal-shape spectral density and characteristic function duplicate V's Meixner law. IV, V, VI all repeat the RH boundary and external quantum coordinate. Present these once, followed by source crosswalks, while preserving all original papers intact.

Do not unify the operator vectors merely by name: IV's signed expectation uses `phi_a=sum n^(-a/2)|n>`, whereas V's two-depth positive expectation uses `phi_a=sum n^(-a)|n>`. They produce different weights by design. Also reserve `beta` for the arithmetic scale exponent and use a different letter for the second Gamma shape in the consolidated text.

The exact unrestricted-shape statement in V Theorem 9.1 is an `su(1,1)` **Lie-algebra** representation on the finite basis span. The synthesis preserves this statement. Do not silently strengthen it to a representation of a particular global Lie group for every real positive shape without checking integration and covering-group conditions.

## Focused corrections and evidence boundaries

### 1. Character modulus versus conductor

**Normalized claim:** IV lines 399–404 use “chi has conductor q” and conclude `|chi(n)|^2=1_(n,q)=1`, then use density `delta_q=1/zeta(2) product_(p|q) p/(p+1)`.

**Verdict: correct only after a stated restriction.** For an arbitrary character modulo `q`, the identity holds with its **modulus** `q`. If `q` denotes conductor instead, the character must be primitive modulo that conductor, or induced characters must retain their actual modulus/coprimality restriction.

An admissible witness is the principal character modulo 4. Its conductor is 1, but `chi(2)=0`, contradicting the asserted conductor-1 coprimality identity. Its squarefree density excludes the prime 2 and is `(2/3)/zeta(2)`, not `1/zeta(2)`.

**Consolidated correction:** “Let chi be a Dirichlet character modulo q. Then `|chi(n)|²=1_(n,q)=1`; define `delta_q=...`.” For character decoherence, require chi and psi to be distinct characters modulo the same fixed q, equivalently require `chi overline(psi)` to be nonprincipal. Fix q in all asymptotic constants. This also clarifies V's brief character-conductor wording, line 231.

### 2. Rational Padé contract versus ordinary simple packets

**Normalized claim:** IV Theorem 11.1 fixes the actual Möbius moments, assumes the m-by-m Hankel determinant is nonzero, and then states a sum of m ordinary resolvent packets whenever the denominator's poles are simple.

**Primary verdict: incomplete, with the smallest missing implication.** The displayed linear-system proof establishes unique normalized rational matching with degree bounds `deg P <= m-1`, `deg Q <= m`. It does not establish that `deg Q=m`, which is the clean condition making the rational function proper and yielding exactly m finite simple resolvent terms.

Dependency chain: actual Möbius moments → invertible Hankel matrix → unique denominator coefficients → rational matching (**established internally**) → full denominator degree/properness (**not established**) → simple-pole partial fractions (**valid with the extra condition**).

Generic signed moments `(0,1,0,0)` at m=2 have nonzero Hankel determinant and unique Padé function `z`, with denominator 1. This illustrates why Hankel invertibility alone cannot supply the missing general implication. It is **not** a counterexample in the arithmetic Möbius family and is not presented as one.

**Strongest safe wording:** “If Delta_m is nonzero, a unique rational matching function with the stated degree bounds exists. If its normalized denominator has degree m and m simple zeros, the matching function has an m-term simple-packet decomposition and preserves the first 2m moments.” No proof of universal full denominator degree, universal nonbreakdown, physical-interval support, or numerical stability is added.

### 3. Preserve strong convergence hypotheses

IV Corollary 6.1 expressly includes a moment-convergence proviso; weak convergence of the log-frequency law alone does not prove all cumulants converge. Preserve that qualifier unless a separate uniform-integrability argument is supplied. VI Corollary 11.2 claims convergence in every Schwartz seminorm; this is inherited from its source proof's controlled-moment and multiplier-derivative argument, not established merely by the marginal Gaussian test. Neither result received a fresh complete proof audit here.

### 4. Bibliography and evidence

IV defers its full references to end-of-series consolidation. V's Kontorovich–Lebedev citation is only “classical papers,” and the external 2026 article is called “article in press.” A consolidated bibliography should supply exact current bibliographic records and pinpoint the external formulas/theorems used. Historical novelty is not established by these archives.

The original claim maps explicitly distinguish generated organization from invention of Gamma functions, Meixner–Pollaczek/Laguerre polynomials, Wigner/Kontorovich–Lebedev objects, SU(1,1), Lévy theory, and Berezin quantization. Preserve this attribution.

## Verification status

Archived built-in ledgers contain IV 18/18, V 19/19, and VI 24/24. Fresh project-wide verification in `special_work/independent_pytest_verification.md` records IV 18/18, V 19/19, VI 21/21 independent pytest cases, with zero failures, on clean source copies and unchanged original manifests. These pytest suites include both recomputed identities and artifact/ledger assertions. Their source built-in batches were not rerun by these suites.

This subagent's initial direct pytest invocation failed before collection because pytest was absent from the base runtime. The separate verification agent resolved dependencies in a scratch directory and successfully completed the fresh runs. No source archive was edited.

No Lean files are asserted to formalize these volume-specific analytic results on the basis of this review. Root's separate formalization inventory controls that statement.
