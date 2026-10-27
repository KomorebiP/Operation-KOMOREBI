# Paper IX: remaining work after exact dyadic periods

Author: Komorebi P.  
Draft status: 2026-09-08. Read-only inventory of the existing release, with the new shared-correction block still pending verification. This draft does not promote either native conjecture to proved.

## Notation and scope

- `C_(N,j)(n)` denotes the normalized reciprocal packet coefficient. Write `U_(N,j)(n)=j! C_(N,j)(n)` for the original coefficient at degree `Nn`. For the exceptional dyadic family, abbreviate `U_j=U_(4,j)` and require `0≤j<4`.
- `Delta_u f(n)=f(n+u)-f(n)` acts on the packet index. A shift `u` in an `N`-packet is degree displacement `Nu`.
- `E_(2n)` below denotes the classical signed Euler coefficient of `sech(z)`. Its classical dyadic reconstruction tower is separate from the four `N=4` reciprocal families. The notation `T_M(n)` is the existing depth-M approximation to this classical `E_(2n)`.
- A lower valuation bound includes zero by meaning actual divisibility in `Z_p`, or the zero-safe rational predicate `precision`. Exact valuation statements include a nonzero hypothesis or conclusion. This distinction matters because the Lean rational valuation assigns a finite conventional value at zero.

## Completed and checked in Lean

| Result | Exact checked scope | Main source |
| --- | --- | --- |
| Nishibuchi Conjecture 3.9 | Every prime p, m>0 with `m ∣ p-1` or `m=2`, and `j<mp`. Original coefficients are p-integral. With `q=lcm(2,p-1)`, degree displacement `q p^r` gives a period modulo `p^r` from packet row `n≥r`, for r>0. | Baseline `NishibuchiCompletion.conjecture_3_9` and `full_period_degree` |
| Improved divisor-branch starting condition | On `m ∣ p-1`, the same sufficient period holds whenever `r≤mn`, equivalently `n≥ceil(r/m)`. This is a sufficient threshold, not an optimality assertion. | Baseline `NishibuchiCompletion.divisor_period` |
| Divisor-branch step amplification | For `h=(p-1)/m`, all natural u,k,n satisfy precision `min(k(1+v_p(u)),mn)` for `Delta_(uh)^k U_(mp,j)(n)`. Normalization subtracts `v_p(j!)`. The row cap remains in this branch. | `AllResidueStepAmplification.unnormalized_precision`, `normalized_precision` |
| All-row N=4 higher-difference bounds | For every j<4 and natural u,k,n, `Delta_u^k C_(4,j)(n)` has precision `k(1+v_2(u))`. The original U_j gain additionally includes `v_2(j!)`. There is no row cap. At u=0, positive-order differences vanish. | `DyadicFourFinalStrengthening.normalized_step_precision`, `unnormalized_step_precision` |
| Exact N=4 first-difference valuations | For every n≥0 and T>0, the difference `U_j(n+T)-U_j(n)` is nonzero and has valuation `v_2(T)+d_j`, where `(d_0,d_1,d_2,d_3)=(1,1,5,3)`. For normalized C the gains are `(1,1,4,2)`. | `DyadicFourLeastPeriods.exact_displacement`, `normalized_exact_displacement` |
| All positive N=4 periods and least period | At every precision exponent r≥0, positive T is a period on every packet row exactly when `2^max(0,r-d_j) ∣ T`. That power of two is the least positive packet period. Degree shifts are exactly 4T, without an assertion about arbitrary off-grid shifts of the full sequence. | `DyadicFourLeastPeriods.period_iff_dvd`, `least_packet_period`, `original_degree_exact_displacement` |
| Optimal classical dyadic Euler tower | `E_(2n)-T_M(n)` lies in `2^(4M+3) Z_2` for all n,M≥0. At n=M+1 the error has exact valuation 4M+3. Each positive-depth summand with `1≤m≤n` has valuation `4m-1+v_2 binom(2n,2m)`. Bounds on omitted weights yield tail bounds. | `DyadicSharpTower.dyadic_supercongruence_sharp`, `first_omitted_error_valuation`, `summand_valuation`, `dyadic_supercongruence_row_weight` |
| Finite affine one-step obstruction | Every finite integer-linear system `Ax=b`, every positive integer modulus p, every L≥0 and every actual solution modulo `p^L` has an explicit finite cokernel class. Its vanishing is equivalent to a next-level solution reducing to the given solution. The theorem does not require p prime. | `Komorebi.NativeAffine.finite_affine_obstruction` in `native/lean/FiniteAffineObstruction.lean` |

The exact-period release records PASS for its 16 continuation modules and 192 explicit declaration audits. The native affine specialization has its separate passing audit. This inventory relies on the actual checked source and saved gate records; it is not a claim that every theorem from every recovered manuscript was replayed here.

The earlier recovered Annals manuscript still describes some congruential differences as open. That is historical text superseded by the later checked results above in their stated parameter ranges. Its older global-gluing and general affine-kernel boundaries remain relevant.

## In progress: shared corrections and a specified common quotient

**Pending.** The current SharedCorrection theorem has not yet been admitted to the checked list in this draft.

The intended finite linear model uses one correction module V and maps `J:V→A`, `K:V→B`. Individually attainable target corrections lie in `im J` and `im K`. The proposed common quotient is

`C = V/(ker J + ker K)`.

The target statement is that individually attainable corrections can be realized by one vector in V exactly when their induced classes in C agree. Any universal property must specify the category and maps. If reconstructing corrections modulo invisibility, the common invisible part is `ker J ∩ ker K`; reconstructing V itself requires accounting for that kernel.

Passing this theorem would supply a concrete algebraic compatibility criterion and a bridge between two separately attainable correction conditions. It would not by itself establish global prime-by-prime descent, nonlinear lift continuation, or native Conjecture 13.3 for arbitrary packet systems. Update this row only after its actual theorem, assumptions, controls and axiom report have passed.

## Established in prose, or formal consequences not yet checked in Lean

| Item | Current evidence and exact boundary | Next formal obligation |
| --- | --- | --- |
| Finite polynomial obstruction | `native/Native_Conjectures_Progress.md` proves the Taylor correction equation, representative independence, vanishing criterion, kernel torsor and finite lift count for a fixed finite integer-polynomial presentation, p prime and L≥1. Exact bounded Python checks supplement that universal prose proof. | Formalize the multivariable expansion modulo `p^(L+1)`, then transfer the affine criterion. Do not assume the Taylor bridge as a premise. |
| Intrinsic obstruction for finitely presented commutative Z-algebras | The native note and independent source audit specialize verified Stacks results to a finite obstruction in an Ext group. This is an external classical theorem in that algebraic category, not a fresh Lean theorem. | Prove the native seed-to-algebra encoding and lift-preservation map, or explicitly retain this as a restricted theorem. |
| Finite compatibility by equality labels | The native note proves that a finite relation can be represented by equality in a common set exactly when it is rectangular. Connected components give a universal quotient for maps agreeing along edges. This is not a minimum-label theorem. | Formalize the relation, three-edge closure, component quotient and universal property if this finite-set route is retained alongside the linear route. |
| Finite and profinite polynomial reconstruction | The native note proves finite reconstruction by CRT and distinguishes profinite completion from global integers. | Connect actual packet constraints and transition maps to this fixed-system reconstruction. |
| Classical dyadic source interpolation | The recovered Annals manuscript proves an analytic interpolation of classical `E_(2n)` from its source and kernel. This inventory does not certify a Lean formalization of that analytic theorem. | Audit and formalize the precise Tate-algebra convergence and interpolation statement if needed. This remains separate from N=4. |
| Continuous N=4 extension and normalized isometry | The exact displacement law implies a unique continuous extension of U_j to Z_2. The normalization `G_j(x)=(U_j(x)-j!)/2^d_j` should be formalized as an isometric bijection `Z_2→Z_2`. This is a derived consequence, not part of the checked release. | Construct the extension, prove residue-level permutations and compatible inverses, then the isometry and surjectivity. |
| Binary-carry form of the classical row weight | The manuscript rewrites `v_2 binom(2n,2m)` by binary digit sums. Lean currently states the binomial valuation directly. | Add the carry identity if the digit formula itself is a desired deliverable. |

The continuous-isometry consequence does not require guessing surjectivity: on natural inputs the exact valuation law makes every induced map modulo `2^r` injective, hence bijective on the finite residue set. Compatibility across r and completeness give the inverse-limit bijection. This short mathematical derivation still needs its own Lean objects and proof if it is to be advertised as formally checked.

## Research questions still open

1. **Exact higher-order difference valuations.** Current all-order results are lower bounds. The exact first-displacement law does not determine `v_2(Delta_u^k U_j(n))` for k≥2. Differences of leading terms can cancel. A useful next target is one fixed order, beginning with k=2, with every zero case and address stated explicitly.
2. **Other prime and parameter period classifications.** The full Nishibuchi family has sufficient periods. Least-period and exact-displacement classifications for general divisor branches have not been obtained here. First isolate the active residue modes and boundary behavior for one small family.
3. **General higher valuations of the affine Mahler kernel.** The recovered manuscript proves residual sparsity and valuation transport, not a universal exact formula for `v_p(Theta_(p^a,s)(r,k))`. The finite affine obstruction quotient is unrelated to such an exact kernel formula.
4. **Further recovery of older odd-edge formulas into Lean.** The historical reciprocal/Fermat-quotient towers are documented, but this continuation does not freshly formalize all of them. Inventory exact theorem statements before treating this as unfinished new mathematics.

## Definition-dependent native conjectures

**Native 13.2 remains unresolved in its original generality.** Specify the category of arithmetic seed presentations, allowed equivalences, precise one-step lift functor, obstruction-packet type and meaning of finite. A raw Jacobian cokernel is independent of the integer representative, but can change under a redundant equation: `(X)` and `(X,0)` give different raw groups. A canonical construction must respect the chosen presentation equivalences. One successful lift is not indefinite continuation.

**Native 13.3 remains unresolved as an underspecified global statement.** Specify X, its local realizations, the distinguished subsets in the restricted product, maps to C, category of fiber products and universal property meant by smallest. Decide whether X is global or completed. The natural interpretation recovering diagonal global integers through continuous maps to a Hausdorff spine is refuted by the proper dense diagonal-integer example in the native note. That refutes the stated interpretation, not every possible formulation. The finite linear SharedCorrection result, if it passes, does not supply the missing global descent assumptions.

## Actionable order

1. Finish and independently check the shared-correction theorem, then record its exact finite algebraic scope alongside the affine obstruction theorem.
2. Formalize the N=4 continuous isometric-bijection consequence; the finite exact-displacement theorem supplies a complete route.
3. Formalize the fixed-presentation multivariable polynomial obstruction criterion, retaining p prime and L≥1.
4. Formulate precise restricted versions of native 13.2 and 13.3, including invariance and completion choices, and prove their application maps. Keep unrestricted statements open until those maps are supplied.
5. Research exact second differences and selected additional prime families. Keep bounded searches distinct from universal valuation claims.
6. Return to the general affine Mahler-kernel valuation problem after a concrete family exposes the next structural obstruction.

## Files inspected for this draft

- `release_staging/PRSC_IX_Exact_Dyadic_Periods/README.md` and `RELEASE_AUDIT.json`.
- `review/SHARP_DYADIC_README.md` and `review/NATIVE_INDEPENDENT_AUDIT.md`.
- `native/Native_Conjectures_Progress.md` and `native/lean/FiniteAffineObstruction.lean`.
- `strengthening/formalization/DyadicFourLeastPeriods.lean`, `AllResidueStepAmplification.lean`, `DyadicFourFinalStrengthening.lean`, and `DyadicSharpTower.lean`.
- Baseline `formalization/NishibuchiCompletion.lean`.
- Recovered `PSC_Paper_IX_Local_Polyphase_Annals_Edition.retrieved.tex`.

No existing release file was changed by this inventory task.
