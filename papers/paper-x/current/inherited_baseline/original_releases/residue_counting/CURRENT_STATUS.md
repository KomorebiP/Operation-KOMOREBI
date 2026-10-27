# Paper X: arithmetic residue counting

The full source ledger remains **17 checked / 3 partial**. This continuation targets the arithmetic residue-counting dependency of Claim 9.1. Compiler evidence and audit scope are recorded in `verification.json`.

| Claim | Status | Checked scope and remaining obligation |
|---|---|---|
| 8.2 | Checked, conditional | Actual local relations, reductions, nonempty finite levels, and inverse-limit closure remain premises of applications. |
| 9.1 | Partial | Actual additive residue counts and norm-character bounds under explicit arithmetic witnesses now connect the lattice geometry to actual ideal sums. The intended characters must still supply those witnesses; arithmetic Euler products, prescribed-Frobenius prime-series divergence, and final source separation remain unfinished. |
| 9.2 | Partial | The supplied-data summand constructions remain checked. Actual Hodge–Tate/Weil–Deligne attachment, coefficient comparisons, and remaining general recovery are unfinished. |
| 11.1 | Partial | The conditional existence core remains checked. Required horizontal transports and the remaining local preservation and recovery dependencies are unfinished. |
| 11.2 | Checked, conditional | The full-spine existence/occupancy equivalence covers every supplied required packet, with its stated application data and premises. |

## Arithmetic target of this continuation

Let K be a number field of degree d, C an ordinary ideal class, J a nonzero integral ideal with [J]=C⁻¹, and m a positive integer. Let χ:ZMod(m)→*₀ℂ be multiplicative. Suppose an actual unit u of O_K/mO_K satisfies χ(N̄(u))≠1, and χ(N(J))≠0. The final theorem `PaperX.NormResidueLattice.exists_classNormSum_bound_of_unit` gives a constant B≥0 such that, for every X≥1,

    ‖Σ_{I nonzero integral, [I]=C, N(I)≤X} χ(N(I) mod m)‖ ≤ B X^(1−1/d).

The sum is over actual ideals. No finite-mean, lattice discrepancy, boundary atlas, generator estimate, or generator-to-ideal identity is assumed in this final statement. Those are derived. The constant can depend on K, J, m, and χ; uniformity over all such data is not claimed. Degree one is included.

The proof first counts the actual additive quotient J/mJ. Multiplication by u gives a permutation of this quotient and derives the vanishing finite means. The two real norm signs are counted separately and recombined. Their principal-ideal absolute norms then give one actual bounded-generator sum. The exact identity is

    generatorSum_J,χ(X N(J)) = w_K χ(N(J)) classNormSum_C,χ(X).

Here w_K is the full roots-of-unity order. It is applied after sign recombination. Recovering the ideal sum uses χ(N(J))≠0; that condition is not inferred from nontriviality of χ.

## Other completed dependencies

The block constructs the actual determinant norm on O_K/mO_K, its congruence and basis independence, and the quotient cardinality m^d. It proves density normalization using the actual lattice quotient index, rather than an arbitrary target set. The signed norm agrees with the real-coordinate sign of the embedded integer. An exact counterexample shows that congruent generators can have different absolute-norm residues when signs are ignored.

Separately, actual nontrivial ordinary ideal-class characters have power-saving sums. Their summatory functions are measurable, have the required logarithmic moment, and satisfy the first-order real Mellin endpoint estimate. A pole-assembly result retains the external zeta/product hypotheses. Ordinary class characters and norm-residue characters are distinct constructions throughout.

## What still prevents promotion of Claim 9.1

1. Prove the required residue-unit witnesses for the intended arithmetic characters, or handle the characters without such witnesses by a separate justified descent. Nontriviality on a larger group alone is insufficient.
2. Supply inverse-class representatives with the required nonzero character value, for example by a checked coprime-representative argument.
3. Prove measurability of the actual norm-character summatory function and attach it to the Mellin framework. The compiled Mellin consumers in this block apply to ordinary class characters; the analogous norm-character connection remains to be checked.
4. Attach the resulting character sums to the actual arithmetic Euler products and prescribed prime set, prove the needed prime-series divergence, and apply the existing separator machinery to the manuscript statement.

These are substantive arithmetic obligations. The new restricted character theorem advances them without changing their hypotheses into conclusions. Universal positive occupancy and Claim 9.2's period-data comparison are not asserted.
