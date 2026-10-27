# Joint coefficient and parameter deformation: independent proof audit

**Normalized claim.** Let \(p\) be prime, \(R=\mathbb Z_p\), and let
\(e,k,s,M\) be nonnegative integers with \(M>2s\). Let
\(F,H\in R[Y_1,\ldots,Y_e,T_1,\ldots,T_k]^e\), let
\(a=(y_0,t_0)\in R^{e+k}\), and suppose \(F(a)=0\). Define the actual
partial Jacobian matrices
\[
J=D_YF(a)\in M_e(R),\qquad K=D_TF(a)\in M_{e\times k}(R).
\]
Suppose \(J\) is invertible over \(\mathbb Q_p\) and
\(p^sJ^{-1}\in M_e(R)\). For every \(v\in R^k\), set
\(\tau=t_0+p^Mv\) and \(G=F+p^MH\). The target is a unique
\(y\in y_0+p^{s+1}R^e\) with \(G(y,\tau)=0\), together with
\[
y-y_0\in p^{M-s}R^e,
\qquad
y-y_0=-p^MJ^{-1}\bigl(H(a)+Kv\bigr)+\varepsilon,
\quad \varepsilon\in p^{2M-3s}R^e.
\]
The formula is interpreted in \(\mathbb Q_p^e\), with an explicitly
integral error. No hypothesis on \(DG\), on the shifted Jacobian, or on an
already constructed solution is part of the target.

**Verdict: proved as written.** The four final mathematical modules have been
read in full independently of the proof builders. The normalized target above
is the literal conclusion of the final solved-coordinate theorem, and both
expanded statement contracts retain its actual polynomial derivatives and
parameter substitution. This is the mathematical source-review verdict.
Fresh Lean compilation and exact revision reconciliation are separate evidence,
recorded only after the fresh release gate has finished.

## Independent reconstruction and dependencies

1. `PolynomialJointSystem` uses the actual polynomial systems
   \[
   \widetilde F(Y,T)=(F(Y,T),T-t_0),\qquad
   \widetilde H(Y,T)=(H(Y,T),-v).
   \]
   Their perturbed root equations are exactly \(G(Y,T)=0\) and
   \(T=t_0+p^Mv\). This is equality in \(R^k\), not a finite congruence.
   The original center is an exact root of \(\widetilde F\).
2. The derivative of the actual appended system is
   \[
   B=D\widetilde F(a)=\begin{pmatrix}J&K\\0&I_k\end{pmatrix}.
   \]
   The lower left zero and lower right identity are derived by taking the
   partial derivatives of \(T-t_0\), not assumed as unrelated matrices.
3. Set \(c=p^s\) and let \(A\in M_e(R)\) represent \(cJ^{-1}\).
   The inherited inverse theorem proves both \(AJ=cI_e\) and \(JA=cI_e\).
   `PolynomialBlockInverse` constructs
   \[
   C=\begin{pmatrix}A&-AK\\0&cI_k\end{pmatrix}.
   \]
   Direct multiplication gives \(CB=BC=cI_{e+k}\): the upper right
   cancellation in \(BC\) is \(-JAK+cK=0\), which uses the right
   certificate. No extra factor of \(p^s\) is introduced.
4. The inherited actual-polynomial normalization applies this original
   certificate to \(\widetilde F+p^M\widetilde H\). At
   \(a+p^{s+1}u\), the preconditioned equation is
   \(p^{2s+1}(C_0+u+pQ(u))=0\), where \(Q(0)=0\) and
   \(C_0\in p^{M-(2s+1)}R^{e+k}\). Polynomial evaluation is nonexpanding
   on \(R^{e+k}\), so the factor \(p\) produces a strict contraction.
   Completeness constructs a fixed point, and its retained divisibility gives
   displacement depth \(M-s\). Injectivity of the original preconditioner
   transfers the zero equation back to the actual perturbed polynomials.
5. The inherited Taylor displacement lemma uses actual evaluated partial
   derivatives and an integral polynomial remainder. With displacement depth
   \(M-s\), the preconditioned quadratic error has depth \(2(M-s)\).
   Dividing the scalar certificate by \(p^s\) leaves the guaranteed error
   depth \(2M-3s\). The varied coefficient term has sufficient depth as well.
6. At the original center,
   \[
   C\widetilde H(a)=
   \bigl(A(H(a)+Kv),-p^sv\bigr).
   \]
   Two negatives in the upper right product give the plus sign before
   \(Kv\). Projecting the integral first-order estimate and applying the
   original solved inverse relation yields the claimed rational formula.
7. The parameter equations force the constructed full root to be
   \((y,\tau)\). Every competing solved root in
   \(y_0+p^{s+1}R^e\) produces a competing full root in the inherited
   uniqueness ball, because \(M\ge s+1\) implies
   \(\tau-t_0\in p^{s+1}R^k\). Therefore uniqueness covers the entire
   advertised solved ball, rather than only the smaller displacement ball.

The dependency graph is acyclic. The construction uses the inherited
certificate theorem, and the error uses the inherited integral estimate.
The combined result does not feed into either inherited theorem.

## Obligation matrix

| Obligation | Status | Evidence or remaining check |
|---|---|---|
| Actual integral p-adic coefficients and center | Passed | Generic ring definitions specialize directly to \(\mathbb Z_p\) |
| Actual polynomial augmentation and exact parameter equation | Passed | `augmented`, `augmentedPerturbation`, `perturb_augmented_root_iff` |
| Actual partial Jacobian blocks | Passed | Four explicit evaluated-derivative block theorems |
| Two-sided certificate and same exponent \(s\) | Passed | `blockCertificate_mul`, `mul_blockCertificate` |
| Original inverse bound is the public hypothesis | Passed | `exists_joint_deformation` assumes only the original actual solved inverse bound |
| Root existence without a new Jacobian hypothesis | Passed | `exists_joint_root_certificate` applies `exists_perturbed_root_certificate` to the actual appended polynomials |
| Full solved-ball uniqueness | Passed | `join_deformed_ball` proves the parameter comparison for every competing solved root |
| Plus sign \(H(a)+Kv\) | Passed | `blockCertificate_mulVec_join_neg` and its actual application in `exists_joint_root_certificate` |
| Integral error at depth \(2M-3s\) | Passed | Actual augmented `first_order_error_dvd` and original solved `exists_rational_error` application |
| Literal statement-to-interface contracts | Passed | Two contracts expand actual derivatives, exact parameter coordinates and the rational formula |
| Boundary controls | Passed | Actual linear combined motion at binary M=2 detects missing/reversed parameter term; nonlinear parameter-only control excludes an extra error digit |
| Exact source revision and axiom reconciliation | Separate release check | Recorded in `audit/reconciliation.json` after the fresh gate |
| General rank-deficient singular persistence | Out of scope | Fraction-field nonsingularity of the square solved block is explicit |
| Analyticity, presentation invariance and descent | Out of scope | No such conclusions occur in this target |

## Boundary and sign checks

- **Strict inequality.** \(M>2s\) implies \(M\ge2s+1\),
  \(M-s\ge s+1\), and nonnegative exponent identities used in
  normalization. Replacing the hypothesis by \(M\ge2s\) is not licensed.
  At \(s=M=0\), \(F(Y)=Y\), \(H(Y)=1\), \(a=0\), the perturbed
  root is \(-1\), which is outside \(pR\). This is a direct mathematical
  boundary example, not a newly compiled control.
- **Nonunit solved Jacobian.** \(J\) need not be invertible modulo \(p\).
  The theorem allows a nonzero denominator exponent \(s\). It excludes a
  genuinely singular matrix over \(\mathbb Q_p\).
- **No parameters.** When \(k=0\), the parameter vector and its prescribed
  shift are unique; the result reduces to the inherited coefficient-motion
  theorem.
- **No solved equations.** When \(e=0\), there is a unique empty solved
  vector and no equation to solve. The augmented system consists only of
  parameter equations. Empty finite matrix identities and singleton product
  spaces make the formulas and uniqueness statement valid.
- **Dyadic case.** No division by two, factorial denominator, or odd-prime
  assumption is used. All primes, including two, are admitted.
- **Sign-control strength.** A binary example with \(M=1\),
  \(H(a)=Kv=1\), cannot refute a reversed sign modulo the stated error
  depth: the two proposed centers differ by four, already divisible by
  \(2^{2M}\). A binary \(M=2\) example or an odd-prime example does
  distinguish the signs at the claimed precision. The final control uses \(F=Y+T\), \(H=1\), \(a=0\), \(v=1\),
  \(s=0\), \(M=2\): the actual point is \((y,\tau)=(-8,4)\).
  Omitting \(Kv\) gives error \(-4\), and reversing its sign gives
  error \(-8\); neither is divisible by sixteen. The original \(M=1\)
  identities are retained only as exact positive examples.
- **No global uniqueness.** The root comparison is confined to the stated
  solved ball with the same fixed parameter vector. No conclusion is made
  about other balls or roots with other parameters.

## Source and computation boundary

Raw inherited sources reviewed in full: `PolynomialRootMotion`,
`PolynomialMotionEstimate`, `PolynomialMotionRational`,
`PolynomialWeightedInverse`, `PolynomialMotionNormalization`,
`PolynomialWeightedNormalization`, `PolynomialTaylorDisplacement`,
`PolynomialTaylorRing`, and `PolynomialPadicContraction`.
The finite-coordinate split definitions in `PolynomialParameterSystem` were
also read in full. The inherited `PolynomialMotionControls` was reread in full
for the nonlinear sharpness root and its finite residue calculation. Only the
relevant divisibility equivalence and residue quotient interface in
`PolynomialPadicUnique` were reread, not the entire module.

The pinned local Mathlib source
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06` was checked at
`NumberTheory/Padics/PadicIntegers.lean` for completeness, the integral norm
bound, the nonarchimedean inequality and `norm_lt_one_iff_dvd`, and at
`Topology/MetricSpace/Contracting.lean` for the complete metric-space fixed
point construction and its uniqueness theorem. No uncached external paper
theorem or literature novelty claim is required by this block.

Development script failures are not mathematical counterexamples. They must be
recorded as observed outcomes without replacing missing raw logs by invented
logs. Fresh Lean elaboration, source hashes, output hashes and axiom closures
will be reconciled separately from this mathematical source review.


## Decisive controls and limits

The new nonlinear control is \(F(Y,T)=Y+Y^2+T\), \(H=0\), with
\(a=0\), \(p=2\), \(s=0\), \(M=1\), and \(v=1\). The inherited
scalar root theorem constructs an even root at parameter two. Its error
\(y+2\) is divisible by four and not by eight, checked by faithful reduction
modulo eight. Thus the universal claim of one additional error digit is false
even for parameter-only motion. This does not assert pointwise sharpness for
every value of \(s\), every system or every chosen inverse bound.

The two new negative compilation controls deliberately submit the proven
negations of the false omitted-term and reversed-sign divisibility claims as
proofs of those claims. They are expected to be rejected by Lean for a type
mismatch. Their mathematical counterexamples are the proved positive control
statements, not the fact that a malformed proof is rejected.

No mathematical route failed. Several initial proof scripts failed because of
finite-index simplification, a missing namespace opening, a coercion type and
explicit matrix type annotation in the contract.
The root wrapper's argument order was corrected before its first compilation.
The sign-control sensitivity issue was corrected by testing binary M=2. These
are distinct from the valid mathematical counterexamples above. See `dev` for
observed compilation outcomes and the explicit raw-log retention boundary.

**Exact remaining mathematical gap in this target: none.** The safe conclusion
is the stated local joint deformation theorem under fraction-field
nonsingularity of the square solved block. General rank-deficient singular
persistence, analyticity, native presentation invariance and descent remain
outside the result. Release evidence requires the fresh cumulative Lean gate
and exact source/review reconciliation, recorded separately from this raw
mathematical audit.
