# Papers VII–VIII: bounded source review and consolidation map

Review date: 2026-10-07. Sources were read without edits. This is a bounded mathematical source review under `mathbox:proof-audit`, not a complete historical novelty review or a fresh formal verification. Primary verdict for consolidation: **correct only after stated restrictions and corrections to the recurrence and evidence claims**. Individual findings below have their own precise verdicts.

## Authoritative source locators

- `special_function_sources/extracted/Projector_Generated_Special_Functions_VII/Projector_Generated_Special_Functions_VII_Release/Source/Projector_Generated_Special_Functions_VII.tex` (1,140 lines).
- The VII Python implementation, separate test file, source-and-claim map, and release audit in the same `Source` directory.
- `special_function_sources/extracted/Projector_Generated_Special_Functions_VIII/Projector_Generated_Special_Functions_VIII_Release/Projector_Generated_Special_Functions_VIII.tex` (1,250 lines).
- The VIII Python implementation, separate test file, source-and-claim map, and release audit in the VIII release directory.

The source audits report VII: 60 PDF pages, 30 figure pairs, 13 built-in checks and 20 tests. They report VIII: 62 PDF pages, 32 figure pairs, 23 built-in checks and 20 tests. Those are source-release reports, not fresh counts or proof claims from this review.

## Consolidation map

| Common core | VII source | VIII source | Consolidated treatment |
|---|---|---|---|
| Positive discrete-series ladder | Definition 1.1 | Definitions 1.1–1.2, Proposition 1.3 | Define symmetric q-numbers and the q-ladder once, specialize at q=1. |
| Coproduct and scalar Casimir | Chapter 1 and Chapter 3 | Theorem 2.1, Definition 2.2, Theorem 2.3 | One q-coproduct convention, local scalar identity, ordered tensor factors. |
| Excitation and multiplicity spaces | Proposition 2.1, Theorem 2.2 | Theorem 3.1 | Use VIII's explicit triangular full-row-rank proof for all q, including q=1. |
| Two-body lowest-weight seed | Classical coupling input | Theorem 4.1 | Retain the proved coefficient ratio and closed q-product vector. Do not conflate this seed with a separately proved positive scalar q-Hahn orthogonality system. |
| Pair-Casimir atlases and overlap | Proposition 3.1, Definition 4.1, Theorem 4.2 | Chapter 5, Theorem 5.1 | Define the overlap as a finite matrix without requiring a polynomial parameter map. |
| Exact small examples | Chapter 5 general-shape N=1; Chapter 6 half-shape N=2 | Theorem 6.1 half-shape N=1 | Retain VII's general-shape classical formula, VIII's q formula and limits, plus the N=2 classical example if space permits. |
| Tridiagonal recurrence | Theorem 7.1 | Chapter 5 | State as a consequence of the cited Racah/tridiagonal-pair input. Fix the sign-gauge issue described below. |
| Bistochastic measurement and entropy | Theorems 9.1 and 10.1, Boundary 11.1 | Theorem 7.1 | Prove one general orthogonal-overlap channel theorem. Distinguish measured distribution from coherent evolution. |
| Monotonic q-mixing and negative control | None | Theorem 7.2 and Boundary 7.3 | Keep one-excitation monotonicity and the higher-level counterexample together. |
| Orthogonal deformation tangent | Shape sensitivity only | Theorem 8.1 | Keep q-flow generator; call its coefficient a speed/metric coefficient for the declared q-coordinate and gauge. |
| Four-body tree bases | Proposition 12.1 | Chapter 10 | Same five planar trees, common finite multiplicity space. |
| Loop coherence | Theorem 13.1 | Theorem 10.1 | Prove the overlap telescoping identity once. Correct the claim about what this test detects. |
| Givens compilation | Theorem 15.1 | Theorem 12.1 | One general theorem for any real orthogonal d-by-d matrix. |
| Scalar Racah/q-Racah definitions | Chapter 18, no explicit shape map | Theorems 13.1–13.2, no explicit shape map | Separate scalar identities from matrix construction. Record the missing shape/parameter/weight/phase map. |
| Askey–Wilson bridge | Future extension | Theorem 14.1 uses classical identity | Present the normalized scalar polynomial and q-difference identity under admissible denominators. No continuous-series packet transform has been constructed. |
| Quantum-number module | Chapter 19 | Chapter 15 | One optional appendix; tensoring separate registers is elementary and does not advance zeta spectral claims. |

The common operational contribution is the data record containing multiplicity projector, Casimir observables, coupling atlases, signed overlaps, measurement kernels, tangent, tree graph, and reconstruction compiler. Classical positive-series, Hahn/Racah/q-Racah, entropy majorization, pentagon coherence, and Givens ingredients are explicitly classical in both volumes. The release does not establish historical priority for the combined architecture.

## Finding 1: positive recurrence coefficients conflict with the displayed gauge

Claim: VII Theorem 7.1, source lines 573–589, asserts positive off-diagonal coefficients b_j for the already defined Racah matrix. **Verdict: refuted as written.**

At N=1 and all three shapes 1/2, the manuscript's matrix is

\[
R=\begin{pmatrix}1/2&\sqrt3/2\\\sqrt3/2&-1/2\end{pmatrix},\qquad
\Lambda_{23}=\operatorname{diag}(0,2).
\]

Hence its opposing Casimir is uniquely

\[
J=R\Lambda_{23}R^{\mathsf T}
=\begin{pmatrix}3/2&-\sqrt3/2\\-\sqrt3/2&1/2\end{pmatrix}.
\]

Its unique off-diagonal recurrence coefficient is negative. The first-row/first-column-positive convention in `canonicalize_overlap` is not the Jacobi-positive convention.

Strongest safe correction: in the chosen matrix gauge, use real nonzero signed b_j. If J is irreducibly tridiagonal, choose signs s_0=1 and s_{j+1}=s_j sign(J_{j,j+1}); then SJS has positive off-diagonals and the rephased overlap SR satisfies the positive-coefficient recurrence. This changes a convention, not the underlying operator theorem. The explicit small matrices must retain their original phase convention unless reprinted accordingly.

Dependencies: overlap definition (internal), pair spectrum (classical representation input), matrix multiplication (exact), irreducible tridiagonality (cited external representation input). The source's claim map calls the tridiagonal property a direct result, but VII's proof appeals to the Racah algebra rather than deriving its matrix relations in this release.

## Finding 2: pentagon closure does not independently validate signs, ordering, or projectors

Claim: VII source line 784 says a wrong phase, label order, or missing multiplicity vector breaks the loop; VIII lines 815–816 says any wrong projector, order, omitted vector, or inconsistent tree basis prevents closure. **Verdict: refuted as written.** The loop theorem itself is proved correctly.

For any complete orthonormal bases B_0,...,B_4 of the same space, U_{r,r+1}=B_r^T B_{r+1} gives a telescoping product equal to I. If each B_r is consistently rephased/permuted by an orthogonal S_r, the edges transform to S_r^T U_{r,r+1} S_{r+1}; these factors also telescope. A common wrong subspace, or a consistently truncated common subspace, can likewise pass the loop test. The bases need not be Casimir eigenbases for the loop to close.

Safe evidence description: closure checks numerical overlap composition and common-space completeness as represented by the matrices. It cannot by itself certify the intended lowest-weight projector, correct spectrum, tree labels, independent local recoupling formula, or physical phase convention. Separate lowering-kernel, dimension, Casimir eigen-equation, spectrum, and joint-diagonalization checks support those claims. A stronger Biedenharn–Elliott implementation test would compare independently computed local Racah edge blocks, with prescribed labels, against the global tree overlaps before composing them.

Both code implementations construct all edges directly from global bases. They do not independently construct the local quantum-6j associator formula and then test its pentagon.

## Finding 3: termination alone does not give a nondegenerate positive orthogonal family

Claim: VIII scalar chapter, line 888, says a finite orthogonal family arises when one denominator parameter is q^{-N}. **Verdict: correct only after additional admissibility and nondegeneracy restrictions.**

Exact minimal counterexample to the unrestricted assertion: take N=1, q=1/2, alpha=beta=1/2, gamma=4, delta=1. Then gamma q=2=q^{-1}. All finite summands for n,y in {0,1} have nonzero denominator. Yet

\[
\mu(0)=\mu(1)=3,\qquad R_0=(1,1),\qquad R_1=(1,1).
\]

The two vectors cannot form a nonzero orthogonal family. Finite support, a distinct lattice, nonzero polynomial norms, and positive weights are different requirements.

The implementation's own scalar fixture uses N=6, q=.73 and exponent parameters (A,B,G,D)=(.6,.8,-7,.4). Recomputing its table and solving R_n w=0 for n=1,...,6 with sum(w)=1 gives approximate weights

`[-6.6561148, -7.5865608, -4.1546856, 1.0819641, 5.8787513, 7.8884803, 4.5481656]`.

These are signed weights. This numerical fixture is useful for duality and the classical limit, but does not certify positive scalar orthogonality. The exact two-point example above is the decisive universal counterexample.

## Finding 4: the matrix-to-polynomial comparison is not supplied

**Verdict: incomplete, with the smallest missing implication identified.** VII source line 910 states that shapes determine standard Racah parameters but does not give the map. VIII lines 552–556 invoke the classical identification, and the open directions explicitly ask for closed shape-parameter formulas for the complete symmetric-convention matrix.

The Python scalar table is computed with independent free exponent parameters. No test compares a normalized scalar table with the matrix overlap for a mapped shape tuple. Therefore the exact missing bridge is a formula

\[
R_{jm}^{\boldsymbol\kappa,q}
=s_j t_m\sqrt{w(j)/h(m)}\,R_m(\mu(j);\alpha,\beta,\gamma,\delta\mid Q),
\]

including the base Q relative to the symmetric q convention, the shape/excitation parameter map, label orientations, nonzero norms, positive weights, and phase factors. This is a classical identification input, not an analytic theorem newly completed by the release. No exact convention check against an external primary source was undertaken in this bounded review.

## Finding 5: scalar domains and continuous terminology need precise boundaries

- Matrix construction: q in (0,1], positive shapes, nonnegative integer N, finitely many ordered factors. Infinite operators act first on finite-support vectors. Numerical code has fixed rank tolerances and floating-point growth, so the analytic range is broader than tested numerical range.
- Scalar q-Racah: use 0<q<1 for the displayed basic-hypergeometric expression, n,y nonnegative integers in the selected finite range, and all denominator q-Pochhammer products appearing in the finite sum nonzero. q=1 is a separately defined limit. Duality follows by exchanging the finite numerator and denominator factors under these conditions.
- Classical-limit theorem: requires that every finite limiting denominator Pochhammer factor be nonzero, or separately justified cancellation/continuation. The theorem omits that qualification in its displayed statement.
- Askey–Wilson: the displayed terminating object is a normalized Askey–Wilson polynomial in x=(z+z^{-1})/2, not a constructed nonpolynomial continuous-series function transform. Its q-difference identity is classical and well-defined away from denominator/pole locations (or by justified removable continuation). No spectral measure, unitary continuous-series transform, or matrix-to-continuous packet lift is proved.
- Ordered q-coproduct: the five trees use contiguous planar blocks. Do not extend VII's arbitrary-subset language to unordered/noncontiguous q-subsets without a separate braided or embedded coproduct construction.

## Evidence quality and cheapest next checks

The separate Pytest suites call the same implementation functions. They are separate assertion suites, not independent mathematical implementations. Many have useful closed-form or spectral checks, but orthogonality of an eigenbasis overlap, squared-amplitude bistochasticity, telescoping closure, and a projected skew generator each have partial construction-level tautologies. In VIII, the returned `generator` is explicitly antisymmetrized; its separate test of returned skew-symmetry is automatic. The built-in ledger's raw skew residual and tangent residual provide the useful numerical evidence.

Recommended consolidation corrections:

1. Use a single conditional tridiagonal-recurrence proposition with explicit gauge choice.
2. Describe pentagon evidence as overlap composition, backed by the separate operator checks.
3. Restrict scalar formulas to nonsingular finite expressions and separate positivity from termination.
4. Keep a visible matrix-to-polynomial comparison obligation rather than identifying independently generated tables.
5. Merge the repeated entropy/Givens/pentagon proofs once. Put original source releases, figures, tests and historical audits in appendices/archive.

The attempted use of SymPy for the tiny symbolic check failed because SymPy is not installed in the active interpreter. The same check was completed by direct exact formulas, rational arithmetic and NumPy. No original source file was changed.
