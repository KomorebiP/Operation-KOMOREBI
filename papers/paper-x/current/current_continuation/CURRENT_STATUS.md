# Paper X: arithmetic residue counting

The full source ledger remains **17 checked / 3 partial**. This continuation targets the arithmetic residue-counting dependency of Claim 9.1. Compiler evidence and audit scope are recorded in `verification.json`.

| Claim | Status | Checked scope and remaining obligation |
|---|---|---|
| 8.2 | Checked, conditional | Actual local relations, reductions, nonempty finite levels, and inverse-limit closure remain premises of applications. |
| 9.1 | Partial | Actual additive residue counts and norm-character bounds now connect the lattice geometry to actual ideal sums. Coprime inverse-class representatives are constructed automatically; norm-character measurability, Mellin endpoint control, pole assembly, and the final compatible-system separator from choice-free arithmetic coverage are checked. The remaining general obstruction is prescribed-Frobenius conjugacy occurrence (weak Chebotarev); the analytic route also still lacks its arithmetic Euler-product/residue and prescribed-prime divergence inputs. |
| 9.2 | Partial | The supplied-data summand constructions remain checked. Actual Hodge–Tate/Weil–Deligne attachment, coefficient comparisons, and remaining general recovery are unfinished. |
| 11.1 | Partial | The conditional existence core remains checked. Required horizontal transports and the remaining local preservation and recovery dependencies are unfinished. |
| 11.2 | Checked, conditional | The full-spine existence/occupancy equivalence covers every supplied required packet, with its stated application data and premises. |

## Arithmetic target of this continuation

Let `K` be a number field of degree `d`, `C` an ordinary ideal class, `m ≠ 0`, and `χ : ZMod m →*₀ ℂ`.  The strongest checked automatic-representative theorem in this continuation is

`PaperX.NormResidueLattice.exists_classNormSum_bound_of_scalar_power_autoRep`.

Its exact scalar hypothesis is

    ∃ a : (ZMod m)ˣ, χ ((a : ZMod m) ^ d) ≠ 1.

Under that condition Lean constructs a nonzero integral ideal `J` with `[J] = C⁻¹` and `gcd(N(J),m)=1`, constructs the required quotient-unit norm witness, and derives `B ≥ 0` such that for every `X ≥ 1`,

    ‖Σ_{I nonzero integral, [I]=C, N(I)≤X} χ(N(I) mod m)‖ ≤ B X^(1−1/d).

Thus neither an inverse-class representative nor its nonzero character value is part of the public hypothesis anymore.  The easier theorem `exists_classNormSum_bound_of_scalar_units_autoRep` derives the exact scalar condition from nontriviality of `χ` on scalar units together with `gcd(d, φ(m)) = 1`.

The underlying counting proof still proceeds through the actual additive quotient `J/mJ`: multiplication by a quotient unit permutes this finite quotient and forces the finite mean to vanish.  The two real norm signs are counted separately and recombined.  The exact generator-to-ideal identity remains

    generatorSum_J,χ(X N(J)) = w_K χ(N(J)) classNormSum_C,χ(X),

with `w_K` the full roots-of-unity order.  The newly constructed coprime representative makes `χ(N(J)) ≠ 0` automatic.

## Other completed dependencies

The block constructs the actual determinant norm on O_K/mO_K, its congruence and basis independence, and the quotient cardinality m^d. It proves density normalization using the actual lattice quotient index, rather than an arbitrary target set. The signed norm agrees with the real-coordinate sign of the embedded integer. An exact counterexample shows that congruent generators can have different absolute-norm residues when signs are ignored.

Separately, actual nontrivial ordinary ideal-class characters have power-saving sums. Their summatory functions are measurable, have the required logarithmic moment, and satisfy the first-order real Mellin endpoint estimate. A pole-assembly result retains the external zeta/product hypotheses. Ordinary class characters and norm-residue characters are distinct constructions throughout.

## What still prevents promotion of Claim 9.1

The former representative, measurability/Mellin, and final-separator gaps are now closed in Lean.  The full source ledger nevertheless remains **17 checked / 3 partial** because the following arithmetic inputs are not yet proved.

1. **Exceptional scalar characters.**  For a norm-residue character `χ`, the scalar route applies exactly when
   `∃ a : (ZMod m)ˣ, χ(a ^ [K:ℚ]) ≠ 1`.  Lean proves this is equivalent to nontriviality of the `[K:ℚ]`-th power of the restricted scalar character.  The easier conditions “scalar restriction nontrivial” and `gcd([K:ℚ], φ(m)) = 1` imply the exact criterion automatically.  Characters trivial on all scalar degree-powers still require a non-scalar quotient-unit witness or a justified arithmetic descent.
2. **Arithmetic Euler attachment for the analytic route.**  The actual norm-character sums now have the required power saving and first-order Mellin endpoint control, and the pole-rigidity implication is checked.  The arithmetic Euler-product identity, its nonzero pole residues, and the prescribed-prime reciprocal-series divergence are still external arithmetic obligations if this analytic route is used.
3. **General prescribed Frobenius occurrence.**  `PaperX.GeneralArithmeticCoverage.ExistentialArithmeticCoverage` remains unproved.  It is the choice-free weak-Chebotarev statement: for every finite Galois subfield, conjugacy class, and finite forbidden set, there is an unramified rational prime outside the forbidden set with an actual absolute Frobenius witness in that class.  The new theorem `PaperX.ArithmeticSystemSeparation.finite_arithmetic_system_separator` proves that this single proposition already implies the full nonsingular finite trace-separator conclusion.  Thus final separator assembly is no longer a separate gap.

### New checked Claim 9.1 infrastructure

- `FinitePrimeAvoidance.exists_ne_zero_mem_avoiding_prime_multiples`: simultaneous nonzero CRT avoidance for finitely many prime multiples.
- `IdealPrimeAvoidance.exists_inverse_class_representative_avoiding`: inverse ideal-class representative avoiding any prescribed finite family of prime ideals.
- `NormResidue.exists_coprime_inverse_class_representative`: for every class and nonzero modulus, an inverse-class integral representative with norm coprime to the modulus.
- `NormResidueLattice.exists_classNormSum_bound_of_scalar_units_autoRep`: automatic-representative norm-character power saving under the scalar-unit/totient criterion.
- `NormResidueLattice.normCharacterMellin_sub_isBigO_of_scalar_units_autoRep`: actual norm-character endpoint variation `O(h)` with no supplied representative.
- `NormResidueLattice.normCharacter_pole_criterion_of_scalar_units_autoRep`: pole rigidity with only the genuine arithmetic product/residue data retained.
- `NormResidueLattice.exists_classNormSum_bound_of_scalar_power_autoRep`: the weaker exact scalar-power criterion, without degree--totient coprimality.
- `NormResidue.scalar_power_witness_iff_restricted_pow_ne_one`: exact characterization of the exceptional scalar-character case.
- `ArithmeticSystemSeparation.finite_arithmetic_system_separator`: full finite compatible-system separator from the single choice-free arithmetic-coverage proposition.

All load-bearing declarations in this continuation compile with warnings treated as errors under Lean 4.34.0-rc2 / Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`; their axiom reports contain only `propext`, `Classical.choice`, and `Quot.sound`.  No result in this update is a proof of general Chebotarev, and Claim 9.1 is not promoted to checked.
