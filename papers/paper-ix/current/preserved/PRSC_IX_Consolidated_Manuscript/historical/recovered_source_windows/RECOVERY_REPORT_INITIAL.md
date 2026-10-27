# Recovered edge towers and dyadic sharpening

Recovery date: 2026-09-08. Scope: user-owned papers and current PRSC IX Lean source. No external publication or priority claim is made.

## Finding

The user's recollection is supported by the actual files. The manuscript program did sharpen the edge formulas, introduced a separate dyadic reconstruction, and later sharpened that dyadic reconstruction to the optimal uniform exponent `4M+3`. The currently supplied v0.11.0 Lean baseline still exposes only the earlier exponent `2M+2` for classical dyadic Euler reconstruction. This is a genuine mismatch between the stronger manuscript and the formalized statement, although the earlier theorem remains true.

## Exact source mapping

| Recovered source | Exact statements | Relation to current goal |
| --- | --- | --- |
| `Petrescu_Euler_Congruences_Convolution_Extension.tex`, Library id `libfile_3074742837bc81918ccde233870fe9c5`, revision 2026-06-22 | `thm:even-edge-exact`, `cor:even-edge-filtration`, lines 926–965: exact edge identity at `n=lambda(p-1)-2r >= 2`, with Fermat quotient depth `ell` and transfer depth `m`, filtered by `2m+ell`. `thm:shifted-inverse`, `cor:literal-two` in the later prime-two section give literal dyadic reconstruction. | Confirms both the sharpened edge tower and separate dyadic branch existed earlier. The displayed dyadic tail here is still `2^(2M+2)`. |
| `Petrescu_Euler_Composite_Periodicity_Refined.tex`, `libfile_8a25b6cbcfc081918dddc7e0b1f37a1a`, revision 2026-06-23 | `thm:edge-tower`, lines 542–562, gives both `p^(2M+1)` and `p^(2M+2)` versions by retaining `R_(r+M)+p F_(r+M)`; `thm:closed-edge` is the exact depleted identity. | A stronger prime-edge formulation than the A000111-only first tower. Assumes p odd and its explicit edge range. |
| `PSC_Paper_IX_Local_Polyphase_Annals_Edition.tex`, `libfile_c5e6e596363081919961a7f0d9e83edd` | `prop:dyadic_beta_unified`, lines 1192–1228; `thm:exact_dyadic_kernel_weight`, lines 1476–1503; `thm:optimal_dyadic_truncation`, lines 1505–1535. Exact `v2(beta_m)=s2(m)-1`, exact `v2(kappa_(2,m))=4m-1`, row contribution `4m-1+v2 binom(n,2m)`, and optimal uniform tail `2^(4M+3)`. | Strongest recovered explicit classical Euler dyadic tower. This is the immediate formalization target missing from the baseline. |
| `DEEP_AUDIT(8).md`, `libfile_b296ea67520c81918c5a79764f2db5f5`, lines 19–38 | Explicitly records the merge of this sharpening into Paper IX and explains the change from the earlier visible power-of-two bound to the full normalized kernel. | Independent historical evidence that the sharpening was already intended, rather than a new suggestion. |

## Notation and exact claim

Here `E_(2n)` are the classical signed secant Euler numbers, defined by `sech(t)`. The current Lean `EulerCoefficients.eulerEven n` is `E_(2n)`.

The source is

`R_d = (3^(d+2)-1)/(4(d+1)(d+2))`, for even nonnegative `d`.

Current Lean `Dyadic.sourceEven n` is `R_(2n)`. The ordinary series inverse has coefficients `beta_m` in `z^2/sinh(z)^2`. The full exponential coefficient is

`kappa_(2,m) = beta_m * 2^(2m) * (2m)! = -2^(4m)*(2m-1)*B_(2m)` for positive m.

The dyadic coordinate identity is

`E_d = sum_(m=0)^(d/2) kappa_(2,m) * binom(d,2m) * R_(d-2m)`.

The sharp result asserts divisibility by `2^(4M+3)` in `Z_2` of its tail after depth M. It is sharp uniformly because at `d=2M+2` the only omitted term is `kappa_(2,M+1)`, whose valuation is exactly `4M+3`. Retaining the binomial valuation gives a valid stronger row-dependent lower bound. Empty tails are exactly zero; an implementation should handle them by divisibility rather than assign the usual infinity-valued valuation to Lean's zero convention.

## Comparison with the current formalization

`formalization/DyadicIntegrality.lean` proves source unit valuation and beta integrality. `formalization/DyadicReconstruction.lean` proves the exact reconstruction identity and defines the same truncation. Its `dyadic_supercongruence` at line 87 concludes only `(2:Z_[2])^(2*M+2) | eulerEven n - truncationPadic n M`.

Its summand is `beta_m * 2^(2m) * descFactorial(2n,2m) * sourceEven(n-m)`. The falling factorial splits as `(2m)! * binom(2n,2m)`, so recovering the precise beta/factorial weight is exactly the missing step. No change to the sequence or truncation is needed.

## What this does and does not settle

The relevant current strengthening goal is incomplete, with the smallest missing implication being a Lean proof of the sharper kernel weight and its passage through the existing tail sum. The manuscript proof depends on the Bernoulli identity and `v2(B_(2m))=-1` from von Staudt–Clausen. The recovered text was read in full around these arguments. That external theorem has not been independently sourced in this recovery subtask. A direct elementary proof or a separately verified formal Bernoulli dependency would close that leaf.

The all-address `N=4` Nishibuchi packet in `DyadicFourCongruences.lean` is a different reciprocal family: `ExponentialSection.normalizedCoeff 4 j n`. Its current bound has a starting-row cap and cannot be strengthened merely by reusing the classical `sech` tower. For example the reciprocal of `sum z^(4n)/(4n)!` has coefficient -1 at degree 4, while classical `sech z` has Euler coefficient 5 at degree 4. Thus even j=0 is not the same sequence. A new source-kernel identity or a precise transfer map with controlled valuation losses is required to carry the sharper classical result to the N=4 packet. The retrieved files do not supply this missing map for all four addresses.

## Recovery details

Two attempts to materialize source-file bytes failed with HTTP 502. Content reads succeeded. The complete Annals TeX is reconstructed in `PSC_Paper_IX_Local_Polyphase_Annals_Edition.retrieved.tex` from four consecutive content reads. It is a retrieved textual copy, not a claim of byte-for-byte identity with the original Library object. Other working text files preserve the relevant source windows and the full audit note. Complete search responses are preserved in request1.json and request2.json.
