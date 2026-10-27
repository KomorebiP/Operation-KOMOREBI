# Actual ordinary ideal-class character sums

## Frozen target and status

For a number field `K`, degree `d = finrank ℚ K`, and an ordinary class character
`χ : ClassGroup (𝓞 K) →* ℂ` with `χ ≠ 1`, define

\[
S_\chi(X)=\sum_{\substack{0\ne I\subseteq\mathcal O_K\\NI\le X}}
\chi([I]).
\]

Both modules compile with `-DwarningAsError=true`. The result is unconditional
for these ordinary ideal-class characters, using the preceding proved quantitative
ideal-class theorem. No arithmetic counting estimate or cancellation is assumed
in the new character theorem.

## Exact arithmetic attachment

`IdealClassCharacterSum.lean` proves finiteness of the actual set of nonzero
integral ideals of norm at most any real `X`. It injects this set into the known
finite set of ideals of norm at most `Nat.floor X`. This works for all real `X`,
including negative values, without silently including the zero ideal.

The definition `weightedSum K w X` is a finite sum over that actual ideal subtype.
The grouping theorem proves exactly

\[
S_w(X)=\sum_{C\in\mathrm{Cl}(\mathcal O_K)}w(C)A_C(X).
\]

It identifies the fibers with the very subtype counted by the predecessor
`classCount`, using an explicit equivalence and equality of finite cardinalities.

For any finite group and nontrivial complex multiplicative character, the file
also proves `∑ g, χ g = 0`. The proof picks `a` with `χ a ≠ 1`, permutes the group
by left multiplication by `a`, and derives
`(χ a - 1) * (∑ g, χ g) = 0`. Thus the needed finite-group cancellation is proved,
rather than included as a character-sum hypothesis.

## Uniform quantitative bound

`IdealClassCharacterBound.lean` uses the already proved bounds

\[
|A_C(X)-c_K X|\le M_C X^{1-1/d}\quad(X\ge1).
\]

For arbitrary class weights of total sum zero, it cancels the common leading
term exactly and proves

\[
|S_w(X)|\le \left(\sum_C|w(C)|M_C\right)X^{1-1/d}\quad(X\ge1).
\]

The conclusion has the explicit quantifier form
`∃ M : ℝ, 0 ≤ M ∧ ∀ X : ℝ, 1 ≤ X → ‖weightedSum K w X‖ ≤ M * X ^ countExponent K`.
The constants depend on the field and weights, and not on the threshold.

The specialization to nontrivial ordinary class characters supplies the required
zero-sum condition from the finite-group theorem. The module also proves the
corresponding `=O[atTop]` theorems and that the actual exponent is strictly less
than one. These APIs are consumed by the actual class-character Mellin lane.

## Module inventory

| Module | Theorems | Other named declarations |
|---|---:|---|
| `IdealClassCharacterSum` | 2 | 1 finite-instance proof, 1 definition |
| `IdealClassCharacterBound` | 6 | none |

Total: 8 theorem declarations, 1 named instance, 1 definition.
All predecessor sources remain unchanged.

## Verification and failed attempts

- `privatechecks/class_sum_attempt1.log`: compiler rejected incorrect finite-set
  parameter naming, an untyped summation binder, instance-style lint, deprecated
  tactic spelling, and an overloaded equivalence-sum call. These were fixed by
  explicit types, the current API, and `Fintype.sum_equiv`.
- `privatechecks/class_sum_attempt2.log`: compiler rejected the finite-target
  instance inference and an ambiguously inferred subtype projection. The repair
  explicitly ascribes the finite subtype and projection types.
- `privatechecks/class_sum_attempt3.log`: strict compilation succeeded, exit 0.
- `privatechecks/class_bound_attempt1.log`: strict compilation succeeded on the
  first attempt, exit 0.
- `privatechecks/class_characters_hashes.json`: frozen source and proof-object
  SHA-256 hashes.
- `privatechecks/class_characters_axioms.log`: named-declaration axiom inspection.

The failed attempts were elaboration and API failures; no failed mathematical
claim was retained, and no hypothesis was weakened to obtain a compiler pass.

## Remaining scope boundary

An ordinary ideal-class character depends only on `[I]`. It cannot in general
encode an independently prescribed residue of `NI` modulo a cyclotomic conductor.
This block therefore does not establish the character-sum estimate required for
arbitrary norm-residue characters, a ray-class counting theorem, an arithmetic
Euler-product identity, Frobenius-class occurrence, or Claim 9.1 in full.
The paper ledger is unchanged by these two modules.
