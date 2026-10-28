# Focused soundness and reader-list review

**27 October 2026 · Komorebi P. · AI-assisted self-review**

This pass screened seven relatively small entries at [commit c4a0a9c57685](https://github.com/KomorebiP/Operation-KOMOREBI/commit/c4a0a9c57685da333c4254e7825beb1dee580ae9), audited three specific mathematical claims, and checked two implementation boundaries. It is not independent peer review, a whole-manuscript audit, or certification of the remaining collection. The [review record](../manifests/reader-curation-2026-10-27.json) pins the inspected source files.

The standard is a precise claim with adequate support. Lean is optional. A short proof can be sufficient. A large archive or a Lean file can still leave its headline claim unsupported. Distinguish a written proof, a finite computation, an unexecuted protocol, and an implementation sketch.

## Reader-list decisions

| Entry | Decision | Reason and remaining boundary |
|---|---|---|
| Euler Signal Bridge | Retain | Short algebraic proofs support the stated operator identities. Fresh exact controls passed. No universal Euler congruence or novelty claim follows. |
| Hilbert 12: ambient dual slice | Retain through a clarified reading note | Finite algebra has substantive content. The Gauss-cube explanation needs an explicit cyclotomic specialization. The original checker already uses the correct group-ring coefficients. |
| Resolution Semantics | Retain | The two-world obstruction has a complete elementary proof. This pass does not certify its other theorems or forcing applications. Its Lean scaffold remains uncompiled. |
| Hilbert 12: analytic Fourier branch | Retain at its existing development status | A 15 KB note supplies explicit statements and arguments, rather than a placeholder. This pass inspected its scope and symbolic-check design but did not replay the SymPy checker or audit every theorem. The special-value equality remains open. |
| Hilbert 12: contracting ambient torsion | Retain at its existing development status | The note provides finite transport formulas, a declared 343-point domain, and separate analytic obligations. This was a scope review, not acceptance of all analytic inputs or a new verifier run. |
| PRISM-1R | Move to the incubator and remove from the main research list | A blueprint and minimal semantic model are present, but hardware qualification is missing. The top-level skeleton ties certificate, dependency, and fault predicates to success and equates current with consumed generation. Those connections cannot demonstrate the advertised runtime checks. |
| RRCT multispace convergence protocol | Move to the incubator and remove from the main research list | The recorded run covers synthetic estimator checks. The Qwen runner and primary causal campaign were not executed. Wording that candidate geometry “was measured in a frozen model” must remain unavailable until an actual model run supplies evidence. |

The [incubator](INCUBATOR.md) lists the two deferred entries and their return criteria. Their original files, import receipts, and full catalogue entries remain available. File counts and the absence of Lean were not removal criteria. Other entries have not automatically passed this new standard merely because they remain listed.

<a id="claim-e1--eulerfir-transfer"></a>

## Claim E1: Euler/FIR transfer

**Normalized claim:** For an integer sequence $a$ indexed by nonnegative integers, $M\geq1$, $s\geq0$, and $k\geq0$, define $Sa(n)=a(n+1)$, $\Delta=S-I$, and $Ra(q)=a(Mq+s)$. Then

$$
\Delta_q^k R=R(S^M-I)^k,
\qquad
\Delta_q^k(Ra)(0)=\sum_r[t^r]\,(1+t)^s((1+t)^M-1)^k\,\Delta^r a(0).
$$

**Primary verdict: proved as written**, for the hypotheses stated above in the [source note](../research/euler-signal-bridge/READ_ME.txt).

The dependency chain is $S_qR=RS^M$, subtraction of the identity, induction on $k$, and the finite polynomial substitution $S=I+\Delta$. Evaluating at zero gives the coefficient formula. The polynomial has no terms below degree $k$ and degree at most $Mk+s$. The cases $k=0$ and $M=1$ are included. No analytic interpolation, convergence theorem, or external research theorem is needed.

The new standard-library harness compares sample-space stencils with polynomial-coordinate evaluation in 210 sequence cases, checks 180 composition rows, and tests five prime residual polynomials. These 395 cases corroborate the written argument. They do not prove a congruence for an entire infinite Euler branch. The original plotting program was not rerun.

**Remaining gap:** None identified for these two identities. Any stronger arithmetic valuation statement needs its own hypotheses and proof. The cheapest next check is a statement-specific review of the proposed valuation bound, if one is asserted.

<a id="claim-g1--the-six-gauss-cube-identities"></a>

## Claim G1: The six Gauss-cube identities

**Normalized claim:** For the source's cubic character, $J=2+3\omega$, a primitive seventh root $\zeta_7$, and $r\in\{1,\ldots,6\}$, the sum $G_r=\sum_{k=1}^6\chi(k)\zeta_7^{rk}$ satisfies $G_r^3=7J$.

**Primary verdict: computationally verified only in the stated range**, covering all six nonzero residue classes for this fixed modulus and character. No varying-prime generalization is assessed.

The dependency chain is exact Eisenstein coefficient multiplication, cyclic convolution modulo $z^7-1$, and specialization using $\Phi_7(\zeta_7)=0$. The computation returns $7J-J\Phi_7(z)$ for every slice. The [reading note](components/H12_AMBIENT_DUAL_SLICE.md) explains why omitting the last specialization would be wrong: the group-ring identity $g_r^3=7J$ is contradicted by $z=1$. This is a clarification of the original checker, not a counterexample to the lemma at a primitive root.

The separate fixed-vector check enumerates all 343 vectors over $\mathbb F_7$, finds seven solutions of $(M-2I)a=0$, and verifies that each pairs trivially with the specified vector $u$. This checks the finite obstruction used in section 2. It does not validate the analytic descent arguments.

**Remaining gap:** The elliptic-gamma/arithmetic comparison, inherited divisor input, and branch normalization are outside this review. The safest reusable result is the fixed finite-algebra identity with the stated quotient relations. A further analytic claim requires a separate audit of its exact dependencies.

<a id="claim-r1--no-symmetric-two-world-retraction"></a>

## Claim R1: No symmetric two-world retraction

**Normalized claim:** Let $A=\mathbb F_2^2$ and $D=\{(0,0),(1,1)\}$. No additive retraction $P:A\to D$ fixing $D$ commutes with coordinate swap. Consequently no Boolean retraction does either.

**Primary verdict: proved as written**, in the source's theorem “No symmetric Boolean projector,” [TeX lines 387–399](../research/resolution-semantics/Komorebi_Resolution_Semantics.tex).

The dependency chain is the definition of a retraction, swap invariance of $D$, and addition in characteristic two. Equivariance gives $P(1,0)=P(0,1)$, so additivity forces $P(1,1)=0$, contradicting that $P$ fixes $(1,1)$. Boolean homomorphisms are additive for symmetric difference. All sixteen scalar maps determining maps into $D$ were also enumerated: exactly two additive retractions, both Boolean, and neither swap-equivariant.

**Remaining gap:** None identified for this obstruction. It does not establish the note's model-existence, forcing, or other theorem claims. Those need their own review. No Lean execution was needed for this argument.

## Obligations and provenance

| Obligation | Outcome |
|---|---|
| E1: domain, shift law, finite expansion, and zero-order boundary | Passed in written self-review. Finite controls passed. |
| G1: quotient relations and all six slices | Passed in exact finite checks. Specialization is now explicit in the reading note. |
| R1: retraction, symmetry, and characteristic-two contradiction | Passed in written self-review. Exhaustive finite control passed. |
| Hilbert 12 analytic input and external literature claims | Not addressed. No analytic or literature verdict supplied. |
| Resolution Semantics outside the selected obstruction | Not addressed. |
| PRISM-1R hardware execution and RRCT real-model evidence | Missing from the inspected records. Return criteria remain open. |
| Whole collection, novelty, and independent peer review | Out of scope. |

The new check ran under Python 3.12.14 on Windows 11 in a separate copy authenticated against the audited commit. The [v2 execution manifest](../verification/audits/soundness-2026-10-27/run/manifest.json) records unchanged input hashes, a completed run, a 30-second limit, and hashed logs. Its Git field is `unavailable` because the execution copy has no `.git`. Source provenance comes from the independently checked blob identities in the review record. The original SymPy and plotting programs were inspected but were not reproduced: SymPy and Matplotlib were unavailable in this interpreter. No dependencies were installed.

The reusable check is `verification/audits/soundness-2026-10-27/check_focused.py`. Run it from the collection root with `python -B`. Its [contract and logs](../verification/audits/soundness-2026-10-27/) state the finite range and exclusions. This is a disclosed AI-assisted self-review, not a fresh independent reviewer. Original scientific source bytes and prior evidence remain intact.

[Quality and completion guide](COMPLETION_STATUS.md) · [Finalization queue](FINALIZATION_QUEUE.md) · [Research index](../research/README.md)
