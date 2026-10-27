# Paper IX sixth-block specification notes

**Author: Komorebi P.**

Release v0.6.0. The original 28-page status-corrected PDF is preserved unchanged. These notes and the cumulative ledger specify how Section 9 is formalized. Earlier amendments remain applicable.

## 9.1: coefficient ring and the meaning of order

The companion theorem is proved for finite square matrices over any **commutative ring**. No field, characteristic-zero, invertibility, eigenvalue, or diagonalizability hypothesis is imposed. The source sequence satisfies the explicit first-order relation `v (n+1) = C *ᵥ v n`. Its equality to the power orbit is then proved by induction.

For a state space of dimension d, the actual characteristic polynomial of C^N is monic of degree d in a nontrivial coefficient ring. The theorem supplies its d-step recurrence. This means **order at most d** for the sampled sequence; it is not a proof that its minimal recurrence has order exactly d. The identity on a two-dimensional state space has constant packet orbits, which satisfy a first-order recurrence. The zero ring and zero-dimensional state space are also covered by the formal equations.

The recurrence coefficient of each earlier state is the negative of the corresponding characteristic-polynomial coefficient. No scalar recurrence is assumed in place of Cayley-Hamilton. The vector identity, its coordinate specialization, and arbitrary linear scalar observations are covered.

## Jump and address conventions

The source uses `v (N*k+j)`, and the effective evolution is the actual matrix power **C^N**, not C. The formula also allows any natural offset j, not just j<N. For the interpretation as disjoint residue packets, use N>0 and 0<=j<N. For N=0 the formula remains algebraically valid but describes a constant subsequence, not a positive-modulus residue partition.

An arithmetic subsequence of an arithmetic subsequence has step N*M and offset N*s+j. That address identity is checked separately.

## 9.2: actual Fibonacci and Lucas sequences

The Fibonacci values are Mathlib's actual `Nat.fib`, cast into the integers. The state is `(F_(n+1), F_n)` and the companion matrix is `[[1,1],[1,0]]`. Their first-order relation is proved, rather than asserted as a certificate for an unrelated sequence.

The Lucas sequence is independently defined by L_0=2, L_1=1, L_(n+2)=L_n+L_(n+1). The identities `trace(C^N)=L_N` and `det(C^N)=(-1)^N` are derived. The sign in the recurrence is therefore essential:

    F_(N(k+2)+j) = L_N F_(N(k+1)+j) - (-1)^N F_(Nk+j).

Even steps have a subtractive previous term; odd steps have an additive previous term. All subtraction is in the integers, not truncated natural-number subtraction. The proof avoids Binet roots altogether and covers N=0.

## Boundary

Theorem 7.5 and Corollary 8.5 remain pending. Neither conjecture is resolved. Nothing in this block establishes an infinite p-adic expansion, the global Euler finite-difference estimate, a minimal-polynomial classification, floating-point stability, or a hardware complexity claim. The finite Python computations are independent mirrors, not extraction from Lean.

Pinned Mathlib supplies the general Cayley-Hamilton theorem, characteristic-polynomial coefficient facts, matrix algebra, and the basic Fibonacci recurrence. Those existing results are reused; they are not reclassified as new independent discoveries.
