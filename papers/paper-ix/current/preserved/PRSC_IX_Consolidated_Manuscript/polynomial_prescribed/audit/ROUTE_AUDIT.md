# Prescribed parameter obstruction: independent proof audit

**Normalized claim and verdict: proved as written.**

Let \(q>0\), \(L\geq1\), and let \(m,k,e\geq0\). Put

\[
F\in\mathbb Z[Y_1,\ldots,Y_m,T_1,\ldots,T_k]^e,
\qquad x\in\mathbb Z^{m+k},\qquad F(x)=q^Lr.
\]

Let \(J:(\mathbb Z/q)^m\to(\mathbb Z/q)^e\) and
\(K:(\mathbb Z/q)^k\to(\mathbb Z/q)^e\) be the reductions of the actual
solved-coordinate and parameter-coordinate Jacobian blocks at \(x\). For
the prescribed parameter digit \(v\in(\mathbb Z/q)^k\), define

\[
\omega_v=[\bar r+Kv]\in\operatorname{coker}J.
\]

The actual fiber consists of residue vectors \(y\in(\mathbb Z/q^{L+1})^{m+k}\)
that reduce to \(x\) modulo \(q^L\), satisfy \(F(y)=0\pmod {q^{L+1}}\),
and have parameter coordinates equal to the residue classes of
\(x_T+q^Lv\) modulo \(q^{L+1}\). The source spells out canonical integer
representatives for these conditions and proves their equivalence with
the correction-digit model.

This actual fiber is equivalent to

\[
\{u\in(\mathbb Z/q)^m:\bar r+Kv+Ju=0\}.
\]

It is nonempty exactly when \(\omega_v=0\), and when nonempty it is a
torsor under \(\ker J\). For prime \(p\), its cardinality is

\[
\begin{cases}
p^{m-\operatorname{rank}_{\mathbb F_p}J},&\omega_v=0,\\
0,&\omega_v\ne0.
\end{cases}
\]

The wrapper obtains one exact residual \(r\) from the lower-root hypothesis
and then quantifies over every parameter digit \(v\). It does not assume an
already derived residual or a linearization premise at its public entry point.

## Review boundary

The reviewer read the raw four new mathematical modules separately from their
builders. The review also read the inherited actual-residue equivalence,
integer Taylor obstruction, digit bridge, finite fiber and torsor proofs,
and the exact pinned Mathlib source leaves listed in
`prescribed_source_audit.json`. The control file was written and self-reviewed
by this reviewer. Independence describes the separation of the proof author
and reviewer; agreement between agents is not itself mathematical evidence.

The precise reviewed revisions, exposition revision, target and fresh-gate
reconciliation are recorded in `REVIEWED_SOURCES.json`. Individual development
checks and the final fresh gate are distinct evidence. The final gate report
must be reconciled with these source hashes before release.

## Dependency graph

1. `PolynomialObstruction.residual_exists` derives \(F(x)=q^Lr\) from
   coordinatewise divisibility. Its uniqueness lemma uses \(q>0\).
2. `PolynomialTaylor.taylor_step_dvd` and
   `PolynomialObstruction.next_level_iff_digit` prove the actual Taylor
   congruence for \(L\geq1\).
3. `PolynomialDigitBridge.digit_solution_iff` reduces the integer correction
   modulo \(q\), using actual partial derivatives.
4. `ResidueLiftDigits.digitEquivResidue` bijects correction digits with all
   next-level residue vectors retaining the lower residue. Injectivity cancels
   the nonzero integer \(q^L\); surjectivity derives the digit from divisibility.
5. `PolynomialLiftCounts.digitEquivLifts` restricts this equivalence to actual
   polynomial roots. Polynomial congruence justifies canonical representatives.
6. `PolynomialPrescribedSystem.digitJacobian_join` splits the full actual
   Jacobian into the \(J\) and \(K\) blocks. `prescribed_equation_iff` gives
   \(\bar r+Kv+Ju=0\).
7. `PolynomialPrescribedLifts.prescribedDigitEquivLifts` restricts the root
   equivalence by the parameter condition. Its reverse implication uses
   injectivity of parameter `digitResidue`; no parameter choices are lost.
8. `FiniteFiberCounts.fiber_nonempty_iff_class_zero` identifies existence with
   the zero quotient class. The minus sign occurs only when choosing a
   preimage of the quotient representative, as required.
9. `PolynomialPrescribedCounts.liftAddTorsor` transports ordinary kernel
   translation and difference through the actual residue equivalence. It
   verifies both action and torsor identities without choosing a base lift.
10. Prime-field rank-nullity and finite-dimensional cardinality give the exact
    count. The public wrappers derive the residual from the actual lower root.

There is no cycle: the new prescribed statements depend on established
unrestricted polynomial lifting and finite linear algebra, not conversely.

## Obligation matrix

| Obligation | Status | Evidence |
|---|---|---|
| Actual polynomial, actual Jacobian blocks | Passed | Explicit `pderiv` and `eval` in both block definitions |
| Domain/codomain \(m,k,e\) and block order | Passed | `Fin.castAdd k` and `Fin.natAdd m`, with `Fin.sum_univ_add` |
| Sign of shifted residual | Passed | Full equation is \(\bar r+Kv+Ju=0\); odd-prime control distinguishes signs |
| All actual residue lifts represented | Passed | Unrestricted equivalence plus exact restriction equivalence |
| Parameter digits specify classes, not integer representatives | Passed | Constraint is equality in `ZMod (q^(L+1))` |
| Canonical representatives preserve polynomial roots | Passed | Inherited polynomial congruence in `digit_residue_solution_iff` |
| Lower-root hypothesis suffices | Passed | `finite_prescribed_obstruction` and `finite_prescribed_lift_count` derive \(r\) |
| Uniformity in every prescribed digit | Passed | A single existential \(r\) precedes `∀ v` |
| Nonempty torsor under solved kernel | Passed | Explicit translation/difference transported through the equivalence |
| No full-Jacobian surjectivity assumption silently used | Passed | No such premise; dyadic control has surjective full block and obstructed parameter |
| Composite \(q\) criterion/torsor | Passed | Ring/module arguments; positivity only for actual finite residues |
| Rank count restricted to primes | Passed | Every finite-field rank theorem has `[Fact (Nat.Prime p)]` |
| \(q=1\), zero dimensions, \(L=1\) | Passed | General arguments include these cases; their interpretation is below |
| Infinite compatible parameter towers | Out of scope | Only a single finite lifting step is asserted |
| Native presentation invariance and descent | Out of scope | The finite polynomial presentation and coordinate split are fixed |

## Boundary cases and decisive controls

- **Dyadic failure of arbitrary parameter freedom.** For \(F(Y,T)=T\),
  \(x=0\), \(q=2\), \(L=1\), the full Jacobian \((0,1)\) is surjective,
  but \(J=0\). Prescribing \(v=1\) forces \(T=2\pmod4\), contradicting
  \(F=0\pmod4\). Prescribing \(v=0\) leaves exactly two actual residues:
  \((0,0)\) and \((2,0)\). The control proves nonexistence and exact
  cardinality through the inspected actual residue interface.
- **Odd-prime sign control.** For \(F(Y,T)=T+3\), \(x=0\), \(q=3\),
  \(L=1\), the residual is \(r=1\). Digit \(v=2\) cancels it and gives
  an actual root modulo \(9\); digit \(v=1\) does not. This distinguishes
  \(\bar r+Kv\) from \(\bar r-Kv\).
- **Why \(L\geq1\).** The Taylor quadratic remainder has factor \(q^{2L}\);
  \(2L\geq L+1\) holds exactly in the required range. At \(L=0\),
  \(F(Y)=Y^2\), \(x=0\), \(q=2\) has zero derivative, but digit \(1\)
  does not give a root modulo \(2\). This is a direct mathematical
  counterexample to dropping the depth hypothesis, not a claim of a separate
  newly compiled Lean control.
- **Degenerate modulus.** At \(q=1\), both residue rings are the one-element
  ring. The actual fiber and kernel have one element and the criterion is
  tautologically true. No field rank is assigned to this case.
- **No solved coordinates.** At \(m=0\), the sole possible solved digit
  works exactly when \(\bar r+Kv=0\). The actual fiber has zero or one element.
- **No equations.** At \(e=0\), the obstruction vanishes and every solved digit
  works; the prime count is \(p^m\).
- **No parameters.** At \(k=0\), the result specializes to the established
  unrestricted finite lifting criterion and count.

## Verification and limitations

The exact pinned Mathlib proofs used for quotient vanishing, subtype
equivalence, rank-nullity, finite-field cardinality and the torsor interface
were read locally. Their hypotheses match the uses here. No external novelty
claim or unverified mathematical citation is used.

The control development encountered normalization issues for finite indices,
an incorrect application of the `Equiv.nonempty` API, and numeral normalization
over `ZMod 3`. These were proof-script failures, not counterexamples to the
target. The failed compiler logs are preserved next to the final successful
compile log. The fresh gate and independent reconciliation determine the final
release verification status.

**Exact remaining gap in this target: none.** The safe conclusion is the full
finite, fixed-presentation, prescribed-parameter criterion, actual fiber torsor,
and prime counts stated above. It does not establish an infinite lift tower
for an arbitrary prescribed parameter sequence, a presentation-independent
native obstruction, or a descent theorem.
