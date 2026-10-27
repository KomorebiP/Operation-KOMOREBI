# Independent mathematical audit — ABC conjecture piece

Date: 8 October 2026. Auditor: an isolated review agent, separate from the manuscript writer. This is an internal adversarial review of the stated scope. It is not specialist peer review or a formal verification of the entire corpus.

**Primary verdict: incomplete, with the smallest missing implication being a uniform global arithmetic comparison.** The new piece presents a research program and local theorems, not a proof of ABC. The corrected sufficient bridge requires a nonzero arithmetic witness with full contact divisibility and a height bound whose radical exponent divided by contact order tends to zero. None of the local jet or determinant results establishes that witness or comparison.

This is the final mathematical review of the revision pinned in `REVIEW_PINS.json`. Findings below were sent to the writer and the adopted repairs were rechecked in context. Original recovered archives remain unchanged.

## Normalized claim and domains

A primitive triple consists of positive integers a,b,c with a+b=c and gcd(a,b)=1. The prime supports are pairwise disjoint. Write R=rad(abc), R_u=rad(u), M_u=u/R_u, and Q=abc/R. ABC is the all-epsilon assertion c<=K_epsilon R^(1+epsilon), with K_epsilon uniform in the triple. The exact equivalent output defect is Q/(ab)=c/R=M_c/(R_a R_b).

The jet filter uses integers m>=0. Hankel ranks are integers r>=1, contact s_r=r(r+1)/2, and truncation levels are integers K>=r. Formal series are over Q. Complex positivity uses real 0<t<1. Local valuation statements use a prime p and v_p(t)=e>=1. The raw small-prime bound allows zero, with v_p(0)=infinity. A formal identity, a complex period value, and a p-adic period value are not identified as one algebraic scalar.

## Dependency graph

- Primitive triple -> disjoint prime supports -> Wronskian divisibility and exact phase Smith factors.
- Primitive shell gradient -> unimodular integral coordinate change -> integral formal implicit-function recursion -> formal smoothness. This supplies no size estimate.
- Kummer class -> valuation/sign calculation -> contact order up to logarithmic kernel. The resulting class supplies no radical-scale height comparison.
- Polylogarithm defining series -> rank-one moment decomposition -> finite Cauchy–Binet -> coefficientwise subset expansion -> exact Taylor contact and positive real nonvanishing.
- Restricted unit-index expansion -> balanced unit residue counts at every p-power -> exact depleted valuation.
- Universal subset expansion -> denominator-loss estimate -> exact good-prime raw valuation and a fixed small-prime lower bound.
- Finite truncation -> rational polynomial -> cleared denominator scalar -> explicit failure of output-prime contact above K.
- Correctly normalized arithmetic witness + nonvanishing + full divisibility + uniform height bound -> logarithm absorption -> ABC. Every witness-construction and height leaf remains open.
- External source leaves are recorded separately in `LITERATURE_CHECK.md`. Generic modularity, standard Kummer cohomology, classical polylogarithm formulas, and published IUT assertions are not certified by a passing Python run.

No closed local result depends on an ABC assumption. The sufficient bridges are conditional and do not discharge their own hypotheses.

## September block: exact claim cards and audit

The nine raw proof/status files are SHA-256 pinned in `audit_input_pins.json`. These are the authoritative written inputs, not search snippets or dashboard summaries.

| Claim | Raw locator | Obligations and reconstruction | Status |
|---|---|---|---|
| Correct defect Q/(ab)=c/R | proofs/01_Target_Correction.md, section 1 | Substitute Q=abc/R and disjoint R=R_a R_b R_c. The all-epsilon equivalences preserve uniform constants. | Passed |
| The target Q=R^o(1) is false | same, sections 2–3 | Family (1,2^k,2^k+1) gives Q>=2^(k-1), R<=3*2^k for k>=1. For every fixed eta<1 the exponential dominates any fixed logarithmic power. The family (t^d,(t+1)^d,t^d+(t+1)^d) yields 2s(d-1)<=B(d+2), hence necessary B>=2s as d grows. | Passed, with the discarded target refuted |
| Universal jet coefficient identity | proofs/02_Jet_Identities.md | Evaluate P_m(1/k). The binomial identity includes k<=m, where coefficients vanish. The leading coefficient is (-1)^m/(m+1)^(m+2). Alternating coefficients give l1 norm 1 after division by (m+1)!. | Passed |
| Depleted jet exact valuation | same | All surviving denominators are p-units. The first surviving index is m+1 unless p divides m+1, in which case it is m+2 with unit coefficient. Subsequent indices have strictly greater valuation for e>=1. | Passed |
| Differential jet identity | same | Apply (t d/dt)^(m+2) coefficientwise and use the generating function for binomial(k,m+1). | Passed |
| Hankel subset expansion | proofs/03_Hankel_Determinant.md, theorem 1 | Moment matrix is sum of (t^k/k) v_k v_k^T. Squared Vandermonde in 1/k yields numerator product(k_j-k_i)^2 and denominator product k_i^(2r-1). Each fixed coefficient has finitely many subsets. | Passed |
| Exact Taylor contact and coefficient | same, theorem 2 | The unique least-sum subset is {1,...,r}. Its coefficient simplifies to product k^(-(2k-1)). Checked the r=1 and r=2 boundary forms by direct expansion. | Passed |
| Real nonvanishing and bound | same, theorem 3 | Positive summands give positivity. Hadamard gives product Li_(2i+1). Sum over i>=1 of zeta(2i+1)-1 is sum over k>=2 1/[k(k^2-1)]=1/4. Apply log(1+x)<=x. | Passed |
| Third-chart growth | same, third chart | Classical inversion at an explicitly consistent boundary branch gives fixed-rank logarithmic growth. Every determinant term has total weight r^2. This is a bound, not a universal nonvanishing statement there. | Passed with the authenticated DLMF inversion leaf and the stated boundary branches |
| Depleted Hankel valuation e S_(p,r)+2 E_(p,r) | proofs/04_Padic_Determinant.md, theorem 4 | Pair valuations equal sums of collision counts modulo p^h. The first r unit indices have balanced counts in all unit residue classes at every h, hence the simultaneous minimum E. They also uniquely minimize index sum. Every other subset has strictly larger valuation. | Passed |
| Raw exact good-prime valuation e s_r | same, theorem 5 | For p>3r-1= (2r-1)+r, p^h-r>(2r-1)h. Each p-divisible index has index excess greater than denominator loss. For unit indices the loss is zero. The leading subset is a p-unit and uniquely minimizes valuation. | Passed |
| Explicit small-prime budget B_r | same, theorem 6 | For h_i=v_p(k_i), k_i>=p^h_i ceil(i/p^h_i). Each individual denominator deficit is bounded by C_(r,p,i). The maximum is finite and zero for good primes. Convergence permits the termwise lower bound to pass to the sum. | Passed as a lower bound only |
| Cleared finite truncation loses output contact | proofs/05_Truncation_Test.md, theorem 7 | Row/column denominator scaling gives L_K^(r^2). Least and greatest subsets are unique, so degree d=rK-r(r-1)/2. Modulo p>K dividing c, only the leading term of c^d A(a/c) survives, and all its factors are p-units. | Passed as a failure of this candidate |
| Corrected conditional bridge | proofs/06_Corrected_Bridge.md | Divide Q^s<=|W| by (ab)^s. For target epsilon choose eta=E_r/s_r<epsilon and delta<(epsilon-eta)/(1+epsilon). A fixed log power is bounded by a constant times c^delta. Rearrangement yields exponent below 1+epsilon, without assuming ABC. Constants may depend on selected rank, never the triple. | Conditional on four explicitly open witness obligations |

The p-dependent depleted functions are not the places of a single algebraic object by definition. Raw good-prime equality does not repair this missing identification. The finite truncation failure is a theorem for that specific scalar construction, not an impossibility theorem for all determinant approaches.

## Restated predecessor results

The review reconstructs the local algebra in project chapters 01–11, including the raw predecessor proofs where the new text inherits them. The historical 142-page verification report is provenance, not automatic recertification of every advanced assertion. Claims outside the explicit inventory remain external context or conditional routes.

| Result or structure | Reconstruction / restriction | Status |
|---|---|---|
| Prime-coordinate Leibniz identity and additive lattice | Work in the global free prime module, then restrict to S. The coefficient identity is immediate from v_p(mn)=v_p(m)+v_p(n). | Passed after domain clarification |
| Wronskian radical divisor | At input p^e, both terms are divisible by p^(e-1). At output primes use W=a d(c)-c d(a). Disjoint supports permit multiplication. | Passed |
| Exponent-weighted master inequality | Bound sum v_p(n)/p by log n/(2 log 2), then combine with nonzero integer divisibility. Theta excludes (1,1,2), whose Wronskian vanishes identically. | Passed after exception convention |
| Phase-only Smith theorem | Lambda is primitive. Same-sector minors vanish, cross-sector minors are +/-abc/(pq). Dividing by Q leaves squarefree R/(pq) with gcd 1. Both sectors nonempty except (1,1,2). | Passed |
| Exact lattice extension | Primitive Lambda gives a split integral row. The matrix index Q gives w(L)=QZ and an integer surjection omega. This does not bound a section's norm. | Passed |
| Stable real height | Let A,B,C be phase sector sums with aA+bB=cC. For D=B-A, the three intervals for A have pairwise intersections exactly at D<=Delta H. Rational minimizers can have denominators cleared along some integer obstruction multiple. | Passed with (1,1,2) excluded |
| Polyphase Smith theorem | V_e acts with determinant 1 on the augmentation ideal when gcd(e,N)=1 and multiplication e on the quotient. Its integral cokernel is cyclic of order e. | Passed |
| First-order no-gain statement | The linear term of each shell product is its shell sum. Kernels of synthesis are invisible to the two stated first-order maps. The statement makes no claim about higher-order size control. | Passed |
| Formal shell completion | The gradient gcd is 1. An integral unimodular linear change makes one linear coefficient 1. Recursive solution at each degree divides only by 1 and preserves integer coefficients. The completion is a power-series ring over Z. | Passed |
| Gauge picture | Torus language applies on a rational nonzero-factor open locus. It is not an integral torus decomposition. Three nonempty sectors give a two-dimensional aggregate plane, unit sectors give a line. | Correct after stated restrictions |
| Local CRT search | The quotient coordinate intervals must each be nonempty before their sum interval is used. With those checks, every integer between summed endpoints is attainable. Unit sectors enforce target zero. | Correct after repaired criterion |
| Global moving-search stopping | H(k)>=k Hbar. Since heights are integers, an improving coset must satisfy k Hbar<=B-1. This yields floor((B-1)/Hbar). | Passed |
| Prime-shell energies | Total energy is log n, activation energy is log rad n. Under a unitary transform the activation projector must be conjugated, or the original signal recovered by exact synthesis. | Correct after stated projection convention |
| Frey invariants and odd bad primes | Direct formulas give Delta=16a^2b^2c^2 and c4=16(a^2+ab+b^2). At each odd divisor of abc, c4 is a unit, so the displayed model has multiplicative reduction and discriminant depth 2e. | Passed algebraically, standard reduction criterion external |
| Landen two-isogeny | Parent translated equation has roots 0,-v^2,-u^2. Its quotient by (0,0) has roots 0,(u-v)^2,(u+v)^2. Scaling/translation of the child Frey model gives this quotient. Radical equality and strict output decrease are direct. | Passed with standard explicit two-isogeny formula |
| Modular area identity | Pull back omega under any nonconstant modular parametrization. Weight-two Petersson measure yields deg(phi) A(E)=4 pi^2 c_phi^2 ||f||^2. General Frey curves are not assumed optimal. | Correct after parametrization qualification, existence from modularity leaf |
| Divisor-polyphase identity | Each prime exponent uses sum_(d|e) phi(d)=e. All products are finite. | Passed |
| Atkin–Lehner packet identities | Commuting integral involutions imply the displayed orthogonality and sum identities. Application to a particular integral modular lattice requires those stated actions. | Passed under the stated involution hypotheses |
| Integral projector denominator | m e_U(Lambda) lies in Lambda iff m annihilates Lambda/(Lambda_U+Lambda_W). For primitive rank-one v, gcd of pairwise coefficient products is 1, giving denominator <v,v>. | Passed |
| Toy Hecke cotangent and congruence quotient | Kernel of target projection has basis m_i e_i with square m_i times that basis element. The target-only vector has first coordinate divisible by lcm(m_i). | Passed |
| Monogenic control | Monic polynomial, integer simple root, and rational product decomposition are required. Cotangent relation is F'(a0) times the root coordinate, and the monic complement polynomial gives the exact projector denominator. | Correct after hypothesis repair |
| Filtered contact quotient | Complex is in degrees -1,0. Cokernel is R_c Z/c Z. Carry extensions are nonsplit only for j>=2. | Correct after degree and range clarification |
| Cyclic transducer | Degree maps m/g and eta/g commute with differentials; image has order g, kernel m/g and cokernel eta/g. | Passed |
| Witt/logarithm local picture | Additive W_n(F_p)=Z/p^n with W_0=0. Odd logarithm is an isomorphism on principal units. The dyadic multiplicative row requires e>=2. The statement is additive, not a unital-ring isomorphism from pZ_p/p^e. | Passed with standard local identities and domain restrictions |
| Kummer kernel | The positive c class is controlled exactly by its valuation vector. Balanced negative beta also needs its sign coordinate when M is even. Resulting kernel divides all input exponents and is logarithmically bounded. | Passed, standard Kummer cohomology identification external |
| Fermat lift height | Coordinatewise Mth powers multiply absolute projective height by M. Canonical line-bundle degree M-3 restores full scale for the full plane carrier with its induced metric. O(1) is per fixed carrier, not uniform in M unless a metric is specified. | Passed |
| Three-point path identities and archimedean envelope | Root-of-unity filtering is direct in the disk, with compatible continuations. Classical dilogarithm/trilogarithm identities supply the fixed-rank packet. No algebraic or integral height bound is inferred from its complex norm. | Passed using authenticated DLMF inputs and the internal real-variable derivation |
| Sequential coherence factorization | Remove sign and Kummer depth before coefficient depth. Reduce the original logarithm row to the residual modulus rather than dividing that row by K. The prime exponents partition e-1 by definition. The residual primitive row has exact character order C. | Passed after explicit definition repair |
| Coherence endpoint | From c=R_c epsilon_2 K W C and K<=log_2 c, the all-epsilon WC bound is equivalent to ABC after independent logarithm absorption. A C-only bound is sufficient only on the stated W=1 subfamily. | Passed as an equivalent open endpoint |
| Arbitrary-index annihilator | Complete a primitive vector to a unimodular basis and choose a complementary primitive row. This shows abstract index cannot be bounded from the known vector alone. | Passed |

## New foundational and spectral proofs

| Claim | Exact audit | Status |
|---|---|---|
| Positive-epsilon quality finiteness | The forward implication uses the ABC bound with epsilon/2, forcing a bounded radical for quality above 1+epsilon, then bounded c. Reverse direction takes a finite maximum of the exceptional ratios. | Passed |
| Epsilon-zero counterexample family | For (1,4^(3^n)-1,4^(3^n)), the explicit cubing expansion proves v_3(b_n)=n+1. Thus rad(b_n)<=b_n/3^n and c_n/R_n>3^n/2. This proves unbounded defect, not a fixed positive exponent-gap counterexample. | Passed |
| Mason–Stothers proof | Nonconstant coprime A,B,C in characteristic zero give nonzero W=A'B-AB'. Every repeated root supplies its e-1 divisor, and degree comparison gives deg C<=n_0(ABC)-1. Sign/permutation yields all three bounds. | Passed |
| Asymptotic Fermat consequence | Fix epsilon=1 once, reduce common gcd, and use rad(xyz)<=xyz<z^3. Then z^(n-6)<K_1 with z>=2 excludes all sufficiently large n. No dependence of epsilon on n is assumed. | Passed as a conditional consequence only |
| Sparse Fourier energy | Exact character orthogonality and Parseval give energy (|G|/M^2)sum N(x)^2. Cauchy–Schwarz on r occupied residues gives the displayed lower bound. Repeated ternary contributions retain multiplicity. | Passed |
| Hypothetical sparse exception regime | ab>=c-1, Q>=c(c-1)/R and c>R^(1+epsilon) give Q>R^(1+2epsilon)/2. Separating finitely many small primes proves Q/phi(Q),3^omega(R)<<R^delta. With delta=epsilon/2, phi(Q)/M>>R^(1+epsilon). The conclusion is restricted to the stated eligible unit-group model. | Passed with model scope |
| Cyclic innovation rank and Prony recovery | Distinct Fourier nodes give rank min(r,d+1). The square moment Hankel matrix is V D V^T with invertible square Vandermonde V and nonzero diagonal D. The first 2r exact samples determine the annihilator and multiplicities. | Passed for a cyclic channel, not an arbitrary character line in a noncyclic group |
| Collision-filter minimum | The target summand lower-bounds every normalized filter. A Lagrange polynomial reaches equality at degree r-1 for an occupied target. An annihilator reaches zero at degree r for an absent target. | Passed |
| Galois denominator coordinate | A nonzero algebraic integer has nonzero integral norm. The product of absolute conjugates is >=1, giving a coordinate with denominator >=1 and numerator l1 bound 2^(r-1). This does not bound all conjugates or imply subpolynomial arithmetic height. | Passed |

The trilogarithm three-point closure was independently reconstructed using the real dilogarithm complement identity, the derivative identity d Li_3(w)=Li_2(w) dw/w, and the auxiliary identity Li_2(1-1/z)+Li_2(1-z)=-log(z)^2/2. The derivative of the displayed sum equals pi^2/(6z)-log z log(1-z)/z+log(z)^2/[2z(1-z)], and both sides approach zeta(3) as z approaches 1. Thus no unverified exact three-point trilogarithm theorem is needed for that real-variable claim.

## Named adversarial valuation controls

The computation auditor executed the suggested exact controls and supplied independently inspected standard-library scripts and JSON records. These are named finite or rigorously tail-certified checks, not a replacement for the general proofs.

- Raw rank one at p=2,t=2 is zero as -log_2(-1), while the depleted value has valuation 1. Modular partial sums at precisions 8,16,32,64 agree. This demonstrates why a raw small-prime lower bound cannot imply nonvanishing.
- Raw rank two at p=5,t=10 has valuation 4, while the depleted determinant has valuation 3. The strict threshold p>3r-1 therefore cannot be replaced by p>=3r-1 in the stated equality theorem. The adjacent good-prime control p=7,t=14 has both valuations 3.
- For the latter controls, v_p(k)<=k/p with p>=5 and weights at most 3 gives k-3v_p(k)>=2k/5. A truncation K=3N discards only terms of valuation greater than N. Integral moments make the determinant congruence valid, and the nonzero residual determines the named infinite-series valuations exactly. Precisions 6,8,12,16 all agree.

The source paths are `evidence/computation/good_prime_boundary_control.py`, `good_prime_run/results.json`, `exact_controls.py` with `controls_run/results.json` at `small_prime_rank_one_control`, and `crt_guard_run/results.json`. The final computation report controls the precise command, environment, input/output hashes and finite ranges. This review inspected the good-prime implementation's denominator removal, unit inverses, and tail contract rather than inferring correctness from its PASS label.

## Decisive inherited correction

The earlier boxed local CRT criterion omitted coordinatewise nonemptiness. In the sector r=10 with primes 2 and 5, target t=-1 and box height H=1, the code's deterministic centered residues are (-1,2). The quotient is q=0. The z_2 interval is [0,1] and z_5 interval is [0,-1], which is empty. The sums of lower and upper endpoints are both 0, so the old written criterion accepts a nonexistent packet. Direct enumeration of x_2,x_5 in {-1,0,1} gives no solution of 5x_2+2x_5=-1.

The repaired criterion requires every lower endpoint <= its own upper endpoint before checking the summed interval. The preserved reference implementation already contains that guard in `LocalMovingProfile.n_interval`. Its exact public search therefore does not inherit this written omission. The archive remains unchanged. Fresh finite regression and oracle results belong to the computation report, not to a universal proof by enumeration.

## Evidence boundaries

- Written local proofs were reconstructed from their raw definitions and exact dependencies, with the minimal-rank and empty-sector cases checked.
- Formal scripts are separate evidence. They do not encode the general determinant, analytic convergence, global arithmetic realization, or ABC endpoint. A compiler outcome on seven elementary scripts cannot certify those results.
- Python assertion counts describe tested finite ranges. They are not quantified universal theorems and do not authenticate an external paper.
- The IUT literature discussion is a source/status review only. This audit does not referee all of IUT or claim a repair of its contested comparison.
- There is no global novelty claim. Classical Cauchy–Binet, Vandermonde, Hadamard, Witt, Kummer, and polylogarithm ingredients retain their established status.

## Remaining gap and strongest safe statement

The strongest safe statement is that the project supplies exact local contact constructions, several exact algebraic normalization and obstruction results, and explicit failed candidate realizations. It isolates the correctly normalized global estimate. The missing theorem must construct one arithmetic object whose nonzero scalar or determinant-line section has the required local divisibility at the actual triple's primes and whose complete global norm has uniform radical-scale growth. Local scalar coexistence alone does not provide a product formula.

The cheapest discriminating next check is to specify one rank-two arithmetic realization, its comparison maps, its algebraic scalar or determinant section, and all norm factors. Check it against the output-prime truncation obstruction before increasing rank or accumulating more finite positive cases.

## Final revision and evidence scope

All 24 reader-chapter sources and all 24 guide spreads were reviewed for their stated mathematics and boundaries. The raw September proof notes were reconstructed independently, and the restated predecessor theorem proofs were checked from definitions. The exact figure formula/data sources were checked, including leading fractions, depletion indices, residue energies, safe budgets, declared census domain, and truncation coefficients. Root layout QA separately renders and inspects the publication pages. This report does not substitute its source review for that visual QA.

The final source revisions contain every adopted repair: the complete CRT interval criterion, unit-sector conventions, the exceptional (1,1,2) height case, integral versus rational gauge scope, transported activation projection, general modular parametrization, finite monogenic hypotheses and quotient, cohomological degrees, carry range j>=2, dyadic row e>=2, explicit residual row reduction, fixed-M height normalization, rational Borel ranks, exact real trilogarithm proof, selected-corpus frequency scope, and the corrected Phi_1 expansion -t^2/8-t^3/9-.... The safe rank-two budget components are explicitly in index order 3 and 4 at p=2, 1 and 2 at p=3. Definitions of a_r, V_0, and positive transducer moduli are explicit.

The exact split-Tate necessity leaf is authenticated in `LITERATURE_APPENDIX_TATE_FALTINGS.md`: split multiplicative E/Q_q, ell!=q, and scalarity of the entire local representation on E[ell^n]. The inertia Kummer image forces ell^n | v_q(q_E), and the cyclotomic graded Frobenius diagonal forces ell^n | q-1. This is a necessary condition only. Frobenius scalarity alone would not support the inertia conclusion. The number-field Faltings leaf in that appendix is contextual and needs End_K(E)=Z before concluding scalar Galois endomorphisms.

The final fresh formal status is read in `FORMAL_STATUS.md`. KTG's exact-version replay passes the 22 direct warning-as-error source checks and 42 named theorem axiom inspections. Its actual-IUT application remains conditional. The original seven ABCJet statements built and passed their axiom checks with two style warnings. A separately preserved copy with only two tactic-sequencing changes also passes warnings-as-errors. The original strict warning check failed on those style warnings and is retained. The finite algebraic scope was checked against the raw theorem statements. No infinite determinant, convergence, valuation-minimum theorem, or arithmetic witness is silently relabeled compiler-verified.

The publication's primary-source status wording follows the dated published IUT claim, the documented competing positions, and the LANA report's withheld judgment. The newer LANA repository statement recorded in the literature appendix also explicitly says it does not verify IUT. No community-consensus census or full IUT proof audit is claimed.

**No unresolved review-blocking mathematical defect remains within the stated inventory.** The open global hypotheses remain open. The primary verdict for a proof of ABC is still incomplete, and the reader edition is an audited exposition of that boundary.

## Conservative mathematical proofreading record

- Scope: all current reader theorem/proof sources, the guide body and mathematical figure labels/data, with the applicable notation and macros.
- Direct manuscript edits by this reviewer: none. The writer applied the reported mathematical repairs, then this review re-read the changed statements and arguments.
- Meaning-changing corrections adopted: complete CRT guard; exceptional and empty-sector domains; local scalarity and logarithm domains; field/model/metric qualifications; exact Phi_1 coefficient. These are mathematical corrections, not unexplained stylistic rewrites.
- Source-language/LaTeX review: theorem domains, signs, indices, coefficient normalizations, cohomological degrees, citation roles and cross-reference dependencies were checked. Root's documented build and render validation controls remaining layout and mechanical LaTeX checks.
- Unresolved issues in the stated reviewed scope: none. Advanced global maps and witness estimates are explicitly hypotheses and are not counted as proved.

Final hashes and exact covered source paths are in `REVIEW_PINS.json`. Changes to those inputs require review reconciliation before release.

