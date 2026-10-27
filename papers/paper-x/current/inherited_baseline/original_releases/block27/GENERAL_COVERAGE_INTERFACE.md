# General arithmetic coverage interface

Block 27 connects actual arithmetic Frobenius witnesses to the quotient hypothesis used by the general separator. It does not prove the prime-coverage hypothesis. Claim 9.1 remains partial.

## Exact remaining arithmetic proposition

Let \(\overline{\mathbb Q}\) be the algebraic closure used by Lean, let \(G_{\mathbb Q}=\operatorname{Gal}(\overline{\mathbb Q}/\mathbb Q)\), and let \(B\) be the integral closure of \(\mathbb Z\) in \(\overline{\mathbb Q}\).

A `Witness p` contains an actual maximal ideal \(Q\subset B\) above \((p)\), an element \(\gamma\in G_{\mathbb Q}\) stabilizing \(Q\), and the equality

\[
\overline{\gamma x}=\bar x^{\,p}\qquad(x\in B).
\]

Witnesses exist for every rational prime by the preceding integral-closure theorem. Their existence alone does not prove that any prescribed conjugacy class occurs in a finite extension.

`ExistentialArithmeticCoverage` is the following proposition:

For every finite Galois subfield \(L\subset\overline{\mathbb Q}\), every finite set \(S\) of rational primes, and every \(\sigma\in\operatorname{Gal}(L/\mathbb Q)\), there is a rational prime \(p\notin S\) outside the explicit prime divisors of \(\operatorname{disc}(L)\), together with an actual `Witness p`, such that its canonical restriction to \(L\) is conjugate to \(\sigma\).

This proposition is a definition of the remaining input. No theorem in this block establishes it, and it is never introduced as a Lean axiom.

## What the interface proves

1. **Actual finite number fields recover all open normal quotients.** For an open normal subgroup \(H\subset G_{\mathbb Q}\), the actual fixed field \(\overline{\mathbb Q}^{H}\) is finite and Galois over \(\mathbb Q\). Its restriction map has kernel exactly \(H\). The proofs use the infinite Galois correspondence, rather than postulating an abstract finite field corresponding to a quotient.
2. **The algebraic coverage conditions are equivalent.** `FiniteFieldCoverage s` is equivalent to `CofiniteQuotientCoverage s`. Both retain arbitrary finite exclusions. In the forward direction, an automorphism conjugating the finite restrictions is lifted to an absolute automorphism by surjectivity of restriction. In the reverse direction, the kernel of restriction to each finite field is proved open and normal.
3. **The ramified prime exclusion costs no extra coverage assumption.** The discriminant prime set is finite and may be added to the permitted finite exclusions separately for each field. `UnramifiedFiniteFieldCoverage s` is therefore equivalent to the same cofinite quotient condition.
4. **Actual witness choices add no extra arithmetic hypothesis.** Outside the discriminant, any two actual absolute witnesses at \(p\) restrict to conjugate automorphisms of \(L\). This uses the derived vanishing of finite inertia, the actual prime-conjugacy theorem, and the fixed inner conjugacy between chosen-embedding restriction and canonical subfield restriction.
5. **The choice-free arithmetic proposition supplies the separator's exact input.** For every fixed global witness family `w`, `ExistentialArithmeticCoverage` is equivalent to `ArithmeticCoverage w`. Consequently, `cofiniteQuotientCoverage_of_existentialArithmeticCoverage` supplies precisely the general separator's quotient hypothesis for the family `fun p => (w p).element`.
6. **Coefficient-prime good sets stay separate.** `arithmetic_dense_good_overlap` derives the conjugacy density on any two cofinite good sets, after any further finite exclusion. It does not replace their possibly different good sets with an assumed universal set.

## Assumptions and boundaries

- The arithmetic field is \(\mathbb Q\), and the finite fields in the interface are genuine finite Galois subfields of the fixed algebraic closure.
- Arithmetic Frobenius means the \(p\)-power residue action. No inverse/geometric convention is silently substituted.
- The discriminant exclusion depends on the finite field. No single finite set is asserted to make all finite extensions unramified.
- `Witness p` does not assert that \(\overline{\mathbb Q}/\mathbb Q\) is unramified at \(p\). Its absolute inertia may be nontrivial.
- Coverage concerns conjugacy classes. It does not assert that the chosen Frobenius elements themselves form a dense subset.
- Global choice of witnesses is justified by proved individual existence. Uniform choice independence is derived after finite restriction; it is not added as an assumption.
- The general arithmetic prime-coverage proposition is still unproved. The new conditional equivalences do not establish a general Chebotarev theorem or complete Claim 9.1.
- The existing compatible-system separator additionally retains its representation hypotheses: irreducible finite-dimensional members, characteristic-zero coefficient fields, continuous characters, common algebraic trace data on cofinite good sets, and memberwise nonisomorphism of distinct systems. This module supplies its coverage argument only under the explicit arithmetic input.
- Claims 9.2 and 11.1 retain their independent arithmetic comparison and assembly obligations. This interface does not establish Hodge–Tate or Weil–Deligne attachment.

## Source map

| Result | Lean declaration |
|---|---|
| Actual finite Galois fixed field | `fixedFiniteField`, `fixedFiniteField_numberField` |
| Exact restriction kernel | `restriction_fixedFiniteField_ker` |
| Finite fields versus open normal quotients | `finiteFieldCoverage_iff_cofiniteQuotientCoverage` |
| Actual discriminant exclusions | `unramifiedFiniteFieldCoverage_iff_cofiniteQuotientCoverage` |
| Canonical restricted witness independence | `canonicalRestriction_witnesses_isConj` |
| Choice-free arithmetic obligation | `ExistentialArithmeticCoverage` |
| Independence of the global witness family | `existentialArithmeticCoverage_iff_arithmeticCoverage` |
| Input to the existing separator | `cofiniteQuotientCoverage_of_existentialArithmeticCoverage` |
| Density on coefficient-prime overlaps | `arithmetic_dense_good_overlap` |

All declarations in this table belong to `PaperX.GeneralArithmeticCoverage`.

The file is an author scope and dependency review. The independent release audit and compiler evidence are recorded separately in the block's verification records.

## Arithmetic base scope

This exact interface is over Q. The source principal example uses G_{F,S}, and Claim 9.1 does not specialize F to Q. General-base applications additionally require actual-prime/norm-power Frobenius attachment and coverage over F, or a proved reduction from that problem to this rational-base interface. The generic representation-theoretic separator does not itself establish the arithmetic transfer.
