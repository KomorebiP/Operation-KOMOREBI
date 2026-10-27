# Paper IX: independent mathematical audit

Audit date: 6 October 2026. Target: the 54 theorem, proposition, lemma, and corollary blocks in the raw current consolidated Sections 10, 20, 30, and 40, their defining context, examples, and mathematical boundary discussion in Section 50.

**Normalized core claim and primary verdict: proved as written.** The concrete packet constructions, correctly normalized all-address congruences, sharp four-packet displacement and period laws, classical dyadic reconstruction tower, finite polynomial obstruction/count/tower/chart results, weighted deformation, and qualitative analytic regularity follow under the stated hypotheses. No correction to a current core theorem statement was identified. This verdict concerns the mathematical arguments; it is not a fresh Lean compilation or a certification of every reprinted historical claim.

Two additional proof paragraphs were recommended to the traditional-edition agent: the commutator argument reflecting flatness through the nonsingular Euler operator, and the explicit extraction/saturation argument from flatness to the row-capped divisor bound. These fill explanatory compression in a valid argument and do not change a theorem's hypotheses or conclusion.

The recovered historical Annals text has five distinct corrections or restrictions, listed below. Its proof blocks were text-read and hypothesis-scanned in full, with fresh reconstruction of selected algebraic and analytic estimates. That is a separate, limited historical audit. Some of its external classical theorem inputs, bibliography records, and source fidelity have not been independently authenticated in this pass. A raw historical reprint must retain this distinction.

## Target, independence, and evidence boundary

The source root is `/workspace/scratch/cbc2b5a746c7/paper_ix_work/source/consolidated/PRSC_IX_Consolidated_Manuscript`. Exact source locators, statement text, hashes, proof hashes, and individual verdicts are in `MATH_AUDIT.json`. Sections 10/20/30 were read directly before consulting retained compiler/source verdicts. Critical arithmetic implications were then reconstructed from raw baseline proof bodies rather than treating retained PASS records as a premise. Section 40 received an isolated fresh subagent review, recorded in `regularity.md` and `regularity.json`.

The proof-audit skill and its general logic/typing, topology, computation-dependent, and external-source checklists were applied. There is no claim of independent kernel acceptance on this host: Lean and Lake were not rerun. The current core's standard source inputs were checked in exact mathematical form. Authentication of the historical pinned Mathlib revision remains conditional and inherited, distinctly from mathematical correctness.

Definitions control the audit: `C_{N,j}(0)=1`, `U_{N,j}=j!C_{N,j}`, original Euler coefficients are supported only in degrees divisible by N; vectors are finite and divisibility is coordinatewise; polynomial lift depth is positive except for affine systems; zero valuation is extended infinity; actual evaluated formal partial derivatives supply every Jacobian; weighted inverse depth is the supplied s, not a substituted determinant valuation.

## Dependency graph

1. Residue indicator identities, characteristic-zero factorial encoding, Hurwitz coefficient multiplication, and triangular recursion establish the concrete coordinate objects. Finite Newton identities derive coefficients from the sequence; they do not assert an unproved infinite tail bound.
2. The reciprocal factorial EGF and the cleared binomial recurrence define the same normalized packet. Multiplication by j! gives the original Euler packet and determines the factorial loss at high addresses.
3. Lucas reduction gives integral normalized packets in the standard window j<p and a common mod-p reduction. The divisor-branch all-address proof instead factors the original packet into the actual section ratios.
4. The cyclic group-ring prime-block estimate establishes weighted logarithmic sections. Initial-zero removal at c=ap, inversion in the weighted ring, and a differentiated factorization establish weighted singular ratios. The logarithmic differential operator and normalized Frobenius defect preserve the weighted ring; exponential substitution transfers this to Hurwitz flatness.
5. Nonsingular ratios propagate through the actual Riccati equation. The Euler commutator reflects flatness through its unit pivots on p-supported degrees. Coefficientwise Picard agreement and finite dependence of each defect then prove flatness of the actual ratio. There is no assumed all-ratio certificate.
6. Product closure and exact section factorization establish flatness of j!P. Coefficient extraction gives order-k divisibility when k≤mn; saturation gives p^min(k,mn); step multiplication and amplification give the stated arbitrary-step bounds.
7. Finite Newton expansion turns difference divisibility into the prime-power packet period. Degree conversion supplies qp^r. The only m=2 branch outside m|(p−1) is p=2,N=4, supplied by the separate all-row charged operator proof.
8. Odd-denominator four-packet sources satisfy unit-step difference gains. Charged fourth-derivative product/inverse/shift laws prove the all-row bound. Finite rational Newton prefixes plus an all-order logarithmic envelope prove exact first-displacement valuations. These imply every positive period and its least element. Density/completeness and compact self-isometry surjectivity give the exact continuous packet images.
9. Classical odd-length source generating functions yield their reconstruction and integral truncation. The classical dyadic source/kernel identity yields exact reconstruction. Its Bernoulli coefficient identity and v₂(B₂m)=−1 for m>0 give exact weight 4m−1, sharp uniform tail depth 4M+3, and row-specific summand weights.
10. Polynomial Taylor remainder at positive depth produces the actual correction equation. Its cokernel criterion, representative independence, shared-kernel quotient, residue-digit bijection, and rank-nullity give finite obstructions, torsors, and counts.
11. Reduced-Jacobian surjectivity persists in the initial residue ball, producing a compatible integer tower. Completion gives exact roots. Square next-digit uniqueness separates all completed roots. The square local inverse plus arbitrary-target surjectivity and a chosen invertible minor give the full parameter chart. A prescribed solved block requires its own surjectivity.
12. The integral certificate A=p^sJ⁻¹, preconditioning, scaled Taylor identity, and strict p-adic contraction give weighted full-ball uniqueness and depth r−s. Applying the original certificate to coefficient perturbation gives the first-order error 2M−3s. The triangular augmented inverse preserves s and yields the forcing H(a)+Kv with the correct negative sign.
13. Polynomial strict derivatives and an augmented actual block derivative supply the external strict/analytic inverse theorem inputs. Product-neighborhood selection gives both directions of the local root graph; continuity transfers any supplied selection to that graph. Coefficient inclusion transfers integral inputs into ambient Q_p.

No circular dependency was found. Universal arithmetic claims depend on proved operator/recurrence estimates, not on the finite numerical checks.

## Obligation matrix

| Obligation | Verdict | Decisive check / limit |
|---|---|---|
| Packet normalization and reciprocal typing | passed | Cleared product gives exactly the stated binomial row; C₀=1, U₀=j!, and off-support coefficients vanish |
| All-address factorial correction | passed | ΔU=j!ΔC; high address p=3,N=6,j=3 gives a sharp one-digit loss |
| Divisor parameters and singular ratio range | passed | m|(p−1) implies m≤p−1; c=ap<N gives a<m and c<p², so v_p(c!)=a compensates the shifted weight |
| Group-ring prime blocks | passed | Each p-block lies in (p,x^(p−1)−1); its pth-power relation yields the factorial ideal bound before division |
| Weighted operator and formal-series passage | passed | Θ, normalized defect, products and unit inverses preserve the stated floor weight; fixed output coefficients have finite input dependence |
| Riccati admissibility and flat inverse | passed | Centered q,y have zero constant coefficient and p-supported degrees; unit pivots and the actual commutator reflect full flatness |
| Saturation and step amplification | passed | No negative degree is extracted; high orders use shifted rows where the cap cannot shrink; finite polynomial displacement retains the cap |
| Nishibuchi range and degree | passed | q/m is integral in both branches; mp·(p^(r−1)q/m)=qp^r; n≥r is sufficient, not claimed earliest |
| Dyadic all-row proof | passed | Charge-one source → charge-minus-one inverse → charge-one shift; no row cap or negative degree occurs |
| Newton dominance / least periods | passed | Higher terms are at least one digit above TΔf; every positive T classified; T=0 excluded from nonzero displacement |
| Packet isometry and image | passed | Rational values have integral unit-denominator embeddings; dense extension is isometric; compact self-isometry is onto |
| Classical dyadic sharpness | passed | First omitted row has a single summand κ_(M+1), with A(0)=1; no tail-cancellation assumption |
| Finite obstruction depth | passed | Nonlinear 2L≥L+1 needs L≥1; affine exact identity admits L=0; q=1 remains valid |
| Torsors/counts | passed | Counts are for residue lifts, not integer representatives; rank formula only over prime fields |
| Shared correction quotient | passed | u−v=s+t gives common w=u−s=v+t; signs and quotient direction are correct |
| Smooth towers and square uniqueness | passed | One recursively chosen compatible path, fixed actual Jacobian, closed precision balls, all-root digit comparison |
| Parameter charts | passed | A suitable minor is selected; entire initial-ball root locus is graphed; approximate center need not be mapped to itself |
| Prescribed endpoint paths | passed | Exact integer parameter increments are retained; arbitrary Q_p endpoint is constructed by compatible truncations; rectangular endpoint uniqueness excluded |
| Weighted threshold and uniqueness ball | passed | r>2s yields nonnegative normalized exponents; contraction runs on the full ball of depth s+1 |
| Coefficient/joint first-order motion | passed | Error exponent 2M−3s exceeds displacement M−s; original inverse suffices; both triangular inverse products checked |
| Zero dimensions and minimum parameters | passed | Singleton modules/spaces make d=0,e=0,k=0 meaningful; q=1 finite lifts, M=0 truncation, r=0 least periods, n=0 and u=0 handled in their stated domains |
| Analytic root graph | passed mathematically | Exact complete-field inverse theorem form checked; product neighborhoods and both inverse identities checked separately |
| Historical exact Mathlib revision | conditional | Current official exact-form theorem contracts verified; pinned bodies absent and pinned retrieval blocked |
| Fresh formal compilation | not addressed | No Lean/Lake execution; retained records are not relabeled as new tests |
| Full historical theorem certification | not addressed | Textual sweep plus selected reconstruction only; unresolved bibliography and external classical leaves remain bounded |
| Native unrestricted presentation invariance/descent | out of scope | Current manuscript states these as open; raw cokernel and proper dense diagonal counterexamples correctly prevent overclaiming |

## Decisive reconstructions and smallest examples

The p=3,N=6,j=3 packet recurrence gives C₁=−1/84, C₂=703/5460 and ΔC₁=64/455, with valuation zero. Multiplication by 3! gives ΔU₁=384/455, with valuation one. Thus the factorial loss is part of the theorem rather than an optional weakening.

For the four dyadic packets, independently reconstructed Newton valuations at orders 1 through 7 are: j=0 and j=1: (1,3,4,7,8,10,11); j=2: (4,6,9,13,16,22,23); j=3: (2,8,8,15,15,19,23). The finite prefixes printed in the exact-displacement proof agree. The universal envelope is supplied by the all-row theorem after the finite threshold; the prefix calculation alone is not the proof.

For E_c=tD+c and B_p=(D^(p²)−D^p)/p, the literal commutator is [B_p,E_c]=pD^(p²)−D^p. This operator commutes with B_p. Hence B_p^rE_cy=E_cB_p^ry+r(pD^(p²)−D^p)B_p^(r−1)y. Earlier flatness makes the correction Hurwitz-integral. On degrees divisible by p, d+c is a unit when p does not divide c. This proves the needed full-flatness reflection, beyond the simpler ordinary-integrality observation.

For k≤mn, extracting B_p^kF at degree mpn−pk gives p^(−k)Δ_h^kU(n), with h=(p−1)/m. For k>mn, applying additional differences to Δ_h^(mn)U uses rows n+ih≥n, all carrying p^(mn). Powers of Δ_(uh)=((I+Δ_h)^u−I) then have only base orders at least k, proving the row cap without a hidden n>0 assumption.

For weighted lifting, A=p^sJ⁻¹ gives AJ=JA=p^sI. At scale p^(s+1), the normalized equation is u=−C−pQ(u), Q(0)=0. The map contracts by |p|<1; if C∈p^(r−2s−1)R^d, digit induction gives u at that same depth and b−a at depth r−s. This proves uniqueness in the entire stated ball, not merely in the smaller displacement ball. F=X²+3 at p=2,a=1 shows the excluded boundary r=2s has no root modulo eight.

For joint motion, the actual augmented derivative is [[J,K],[0,I]], and its certificate [[A,−AK],[0,p^sI]] multiplies to p^sI on both sides. Multiplying the augmented forcing (H(a),−v) gives solved forcing A(H(a)+Kv). At p=2,s=0,M=2,F=Y+T,H=1,v=1, the exact root is −8; omitting Kv predicts −4 and reversing its sign predicts 0, both violating depth four. At M=1,F=Y+Y²+T, the even root has error y+2 of exact valuation two, so no uniform extra error digit is available.

Finite nonlinear obstruction fails at L=0 for X²−1, q=2,x=0. Singular one-step success fails to imply an infinite branch for X²−5. Full Jacobian surjectivity fails to permit a prescribed solved block for F(Y,T)=T. Rectangular surjectivity fails to imply root uniqueness for F(X,Y)=X. Each of these excluded conclusions is correctly delimited in the current core.

## Recovered historical corrections and restrictions

Source: `strengthening/recovery/PSC_Paper_IX_Local_Polyphase_Annals_Edition.retrieved.tex`. Line numbers below refer to the unmodified recovered text, not the edited edition. Each item was communicated to the traditional-edition agent and root before final assembly.

| ID / locator | As-printed problem | Decisive evidence | Strongest safe statement |
|---|---|---|---|
| HIST-1: matrix state setup 1782–1784; `thm:matrix_carmichael_mahler` 1786–1817; finite-adelic analogue 1819–1847 | Initial state v₀ and observable w are untyped; stated p^(Lr) divisibility needs integral inputs | p=3,L=1,C=4,v₀=1/3,w=1 gives Δ₁a₀=1, losing the guaranteed digit | Require v₀,w∈Z_p^d locally and v₀,w∈Z^d for integral finite-adelic divisibility; retain admissible nonnegative sequence indices |
| HIST-2: `lem:matrix_power_amplification` 2476–2489; downstream theorem 2491–2519 | Lower bound L≥1 is absent from the standalone printed statement | p=3,d=1,L=0,X=2=1+B,B=1: X³−1=7 is not divisible by 3, even though X is a unit | Require L≥1; the binomial induction then supplies L+a. Earlier intended scalar ranges do not excuse an ambiguous standalone lemma |
| HIST-3: `thm:prime_power_sparsification` 2394–2430 after convergent expansion at 2313–2348 | Kernel congruence is correct; multiplying it by arbitrary convergent Q_p coefficients need not preserve precision modulo p | p=2,M=2,s=0,f(x)=x/2: c₁=1/2,c₂=0,g(q)=q,d₁=1; d₁ is not congruent to c₂ modulo 2 | Require c_r∈Z_p for the coefficient congruences; no integrality restriction needed for the exact finite kernel identity |
| HIST-4: `ex:compressed_mod_seven` 561–572 | Printed positive tail (1,6,4,...) is numerically wrong | Defining recurrence gives e₁=−1=6,e₂=5,e₃=−61=2 modulo 7 | Correct positive tail is (6,5,2,6,5,2,...); exact period three remains true |
| HIST-5: `cor:local_source_change` 1390–1401; source definition 1269–1287; even H_p at 1304 | Full source sequences include odd S_n(p), while the proof changes only even generating functions | p=3,ℓ=2,n=1: A_(3,1)=1−3+5=3; dyadic odd source vanishes and even L₃K₂ preserves zero odd coefficients | Restrict source-chart transport to even subsequences/evenized EGFs H_p. H_p=L_pK_ℓH_ℓ is valid |

An additional typing clarification is recommended around historical polynomial lifting at 2745: “polynomial map Z_p^d→Z_p^r” must mean a polynomial with integral coefficients. An arbitrary integer-valued Q_p polynomial such as (X²−X)/2 on Z₂ can have a nonintegral Jacobian, making its reduction modulo p undefined. Under the intended integral-coefficient convention, the displayed positive-depth Taylor argument is valid.

Historical dyadic boundary conventions at 1477–1548 also need to be visible: exact reconstruction-term weights use even n and 1≤r≤n/2; an empty tail is zero and its empty minimum is +∞; printed fixed-depth formulas omit terms with negative source indices. These are typing/empty-set clarifications, not new counterexamples. The current core states these boundaries correctly.

Historical proof-reading scope: the finite field mode algebra, subgroup support/period, triangular transport, recurrence/CRT, finite affine kernels, source/kernel identities, and one-level obstruction arguments were reconstructed directly. The polynomial-exponential operator formula, matrix binomial estimates, odd unit-depleted Tate norm estimate, dyadic source logarithmic expansion and translated kernel convergence were inspected. The latter classical analytic developments still have unauthenticated external Mahler/unit/analytic source leaves in this pass and are not globally promoted to the newly audited core. Older “full inverse bound remains open” paragraphs are superseded historical status statements, not present mathematical obstructions.

## Sources, computations, and exact remaining gap

The root's fresh primary-source check is recorded in `../references/SOURCE_REVIEW_2026-10-06.md`. The official Nishibuchi PDF was internally stamped v2, 1 June 2026. Definition 2.1/Remark 2.3 and Conjecture 3.9 match the reciprocal EGF, positive m dividing p−1 or m=2, j<N, q=lcm(2,p−1), and original-degree displacement qp^r. This citation authenticates the compared conjecture's statement; it is not a proof input for the paper's result.

The exact Bernoulli leaf is NIST DLMF §24.10(i), equation 24.10.1. Its reduced denominator is the product of primes q with (q−1)|2m. For m>0, 2 appears exactly once; the reduced numerator is therefore odd, giving v₂(B₂m)=−1 and nonvanishing. This is exactly the implication needed at core Section 20 lines 924–954. B₀ is excluded; the sharp tower invokes κ_m only for m≥1.

The regularity subagent independently checked current official Mathlib strict and analytic inverse theorem contracts and their complete-field hypotheses. Its report records the source versions. Requests for the pinned historical revision were blocked; current source was not silently relabeled as the pinned dependency.

Commands and computations: `rg --files`, `rg -n`, direct `cat`/`sed` reads, standard-library ZipFile extraction of selected baseline proof bodies to `baseline_inputs`, and exact `fractions.Fraction` recurrence/difference reconstruction. `python small_exact_checks.py` passed its 28 dyadic-prefix, normalization-loss, and six mod-seven-row checks. The independent larger computation agent's `verification/computation/scripts/exact_finite_gate.py` was also adversarially read, especially the nonunit finite uniqueness convention: p^s residue representatives modulo p^N agree modulo p^(N−s), and do not represent p^s completed roots. Its bounded outputs remain separately recorded. Neither finite check replaces a universal proof.

There is no remaining mathematical repair to the 54 current core theorem statements. The remaining formal evidence gap is exact historical source/toolchain authentication and a fresh unchanged-module Lean run, if requested and available. The recovered historical text needs the five visible restrictions/corrections above and honest unresolved-source labels. General fraction-field-singular persistence, unrestricted native presentation invariance, global descent, exact higher packet differences, and arbitrary-row dyadic tail valuation remain outside the proved conclusions.

## Accepted bounded provenance for the small checks

The earlier direct `small_exact_checks.json` is retained unchanged as a predecessor. A fresh byte-identical copy of `small_exact_checks.py` was executed through the current Mathbox version-2 bounded runner in `small_exact_bounded_run_v2`. Its manifest pins eight input files, records their unchanged before/after hashes, the actual CPython 3.12.14 environment and command, logs, runtime and all three declared output hashes. Effective caps were 30 seconds wall time, 256 MiB address space, 20 seconds per-process CPU, one CPU affinity core, one cooperative numerical-library thread, and 1 MiB combined logs.

`small_exact_bounded_run_v2/manifest.json` passed the current validator with `--root /workspace/scratch/cbc2b5a746c7/paper_ix_work`. The scientific JSON and source-copy provenance both passed, and the scientific JSON exactly matches the predecessor bytes. `small_exact_bounded_review.json` records the interpretation: implementation and finite assertion verified in the literal scripted range. This adds execution provenance for the existing finite checks; it does not add a universal theorem, a fresh Lean run, or a new mathematical search.

An earlier bounded attempt completed and initially validated, but a concurrent revision of the shared vendor provenance metadata made its input record stale. Its record is preserved as `small_exact_bounded_run/manifest.stale.json` with `STATUS.json`; it is not an accepted manifest. The accepted replacement pins an immutable audit-owned byte-identical runner and validator snapshot. This was a provenance freshness issue, not a mathematical test failure.
