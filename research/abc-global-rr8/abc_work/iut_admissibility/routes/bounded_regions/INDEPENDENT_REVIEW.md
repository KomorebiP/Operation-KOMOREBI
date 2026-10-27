# Independent audit of the bounded-region model

## Normalized claim and primary verdict

**Primary verdict: proved as written.** This verdict concerns the mathematical statements in the specified finite-product local-field model. It does not certify any dictionary to IUT admissibility, indeterminacies, or normalized volumes; the audited note explicitly makes no such identification.

For a fixed prime `p`, a finite nonempty product `A = product K_i` of finite extensions of `Q_p`, its product integer ring `O`, a full fractional ideal `J = I(a)`, and `g in A^times`, the claim is as follows. Among measurable positive-measure `S subset J`, the **algebraic** `O`-span is `I(k)`, where each `k_i` is the attained minimum coordinate valuation. The output hulls are exactly the full ideals in `gJ`. Every positive real measure at most the measure of a prescribed full ideal can be attained by a compact subset with precisely that hull. Consequently, prescribed output hull `H` and raw output measure `tau > 0` are simultaneously attainable exactly when `H subset gJ` and `tau <= mu(H)`. Hull logarithmic degrees have the stated additive-semigroup spectrum, whereas raw-region logarithmic volumes with a fixed hull fill a real interval. The specified `Q_3` example proves that hull volume does not descend either through equality of raw volume or through equality almost everywhere.

## Revision and review provenance

- Raw proof: `/workspace/scratch/f276b5072653/abc_work/iut_admissibility/routes/bounded_regions/PROOF_NOTE.md`.
- SHA-256 of the exact input audited: `134189a2833d90c2b46ae964173a553a7414bba74c93d28df35b6c040e8bb0cb`.
- Checkpoint named in that input: `ABC-20261025-RR6`.
- Base RR5 archive identity supplied for context: `79351e014266a936a96a3511d859957d2e00a6f25c3a18e6e3c987f761dafa01`. The archive itself was not separately audited here.
- Review: an isolated delegated audit, reconstructed directly from the raw definitions and proof, without using another review or a recorded status as evidence. No raw-proof changes were made.
- Method: the `mathbox:proof-audit` skill, including its general logic, topology, and external-input obligations. No applicable ancestor `AGENTS.md` or ancestor `.mathbox` ledger was found.

## Dependency graph

1. A finite extension of `Q_p` has a discrete integral valuation, a compact open integer ring, and finite residue field. Product Haar measure is normalized on `O`. These give compactness and the ideal measure formula.
2. Singleton measure zero, finiteness of the product, and positivity of `mu(S)` imply that no coordinate projection of `S` is identically zero.
3. Coordinate valuations are bounded below and integer valued. Their finite minima are attained. Coordinate idempotents in `O` isolate finitely many minimizing coordinates and produce the entire ideal `I(k)` by a finite algebraic span.
4. Commutativity of multiplication by `g` with `O`-coefficients gives `H(gS) = gH(S)`. Its coordinate valuations and Haar scaling give Theorem 1 and the attainable-hull criterion.
5. The nested finite partitions of a full ideal by cosets modulo `p^n` produce an open subset of any prescribed relative measure in `[0,1]`. A complement gives a compact set; adjoining one principal generator, a null singleton, fixes the algebraic hull without changing its measure. This gives Lemma 2.
6. Containment and measure monotonicity give necessity in Theorem 3. Applying Lemma 2 inside `H` and pulling back by `g` gives sufficiency.
7. Substitution of `h = a+b+n` in the ideal measure formula gives the degree semigroup. Lemma 2 independently gives the continuous raw-volume interval.
8. The null singleton in the explicit `Q_3` example changes the algebraic hull. This obstructs both asserted quotient descents.

There is no circular dependency, computational leaf, or unstated IUT input in these implications.

## Obligation matrix

| Obligation | Verdict | Decisive check |
|---|---|---|
| Product Haar normalization and multiplication factor | Passed | `mu_i(pi_i O_i)=q_i^(-1)` from the index `q_i`; units preserve the normalized integer-ring measure. Products give `d(g)=product q_i^(-b_i)`, including negative `b_i`. |
| Finiteness and attainment of each `k_i` | Passed | Inside `J`, finite valuations belong to the nonempty subset of integers bounded below by `a_i`. A coordinate-zero slice has product measure zero, so positive `mu(S)` supplies a nonzero coordinate value. |
| Algebraic hull without closure | Passed | A minimizing point for coordinate `i`, multiplied by the corresponding idempotent and by all coefficients in `O_i`, yields the whole coordinate ideal. Summing over the finite set of coordinates yields `I(k)` using finite sums. |
| Complete target-hull classification | Passed | Every hull lies in the `O`-stable ideal `gJ`; conversely `S=g^(-1)H` is a compact open positive-measure ideal in `J` for any full `H subset gJ`. |
| Every real measure with a fixed hull, compactly | Passed | The base-`p^D` coset construction gives an open set of the desired complementary measure. Its complement in compact `L` is compact. Adjoining a generator preserves measure and compactness and forces the hull. |
| Joint raw-volume and hull criterion | Passed | Necessity uses `gS subset H subset gJ`; sufficiency uses the same compact `T subset H` for both its measure and its hull, then takes `g^(-1)T`. |
| Positive-measure submodule specialization | Passed | For an `O`-submodule, its algebraic span is itself. Theorem 1 therefore makes it a full ideal, so its output measure must equal `mu(H)`. |
| Degree semigroup and local finiteness | Passed | All coordinate exponent increments are independent nonnegative integers. Positive generators `log(q_i)` bound every increment in a bounded degree drop. The common prime gives `log(q_i)=f_i log(p)`. |
| Continuous raw volumes versus discrete hull degrees | Passed | `tau` ranges over `(0,mu(H)]`; taking its logarithm divided by positive `D` gives exactly `(-infinity,ell_D(H)]`. This does not alter the discrete hull spectrum. |
| Weighted ideal-only convention | Passed | Direct substitution gives the stated weighted spectrum for positive fixed `w_i`. No measure on arbitrary regions is inferred from that formula. |
| Rank normalization and Haar caveat | Passed | Multiplication by `p` has index `p^D`, so `ell_D(pT)=ell_D(T)-log(p)`. For `D>1`, `(2m)^(1/D) != 2m^(1/D)` for disjoint sets of common positive measure `m`. |
| Equal-volume/almost-everywhere quotient obstruction | Passed | In `Q_3`, adding `1` to `9Z_3` adds zero measure but supplies an `O`-generator. The two hull measures are respectively `1` and `1/9`. |
| Actual IUT admissibility or normalization | Out of scope | No admissibility dictionary is supplied or claimed. The model classification alone does not settle the remaining IUT existence/comparison question. |

## Adversarial reconstruction and edge cases

The coordinate-zero argument uses finite product measure inside the finite-measure ambient `J`, so there is no infinite-factor or `0 times infinity` issue. Haar singletons are null: a positive singleton mass would, by translation invariance, give arbitrarily large measure to finite subsets of a compact open set. Positive measure is used only to ensure nonzero coordinate projections; it need not imply that a coordinate minimum is attained at one common point. Different minimizing points suffice because `O` contains every coordinate idempotent. This is exactly why the proof establishes the algebraic span and does not require a closure operation.

In the measure construction, `L/pL` has `p^D` elements and every depth-`n` coset has relative measure `p^(-nD)`. Choose any ordering of the children at each stage. For digits `d_n` of a number `theta in [0,1)`, select `d_n` children from the one unselected continuation coset at depth `n-1`, then retain one of the remaining children as the next continuation coset. Since `d_n <= p^D-1`, that continuation always exists. Chosen cosets at different depths are disjoint, and their measures sum exactly to `theta mu(L)`. Nonunique terminating base expansions cause no problem: either choice has the same sum. All selected cosets are relatively open, so their complement is closed in compact `L` and is compact. Adding the generator is a finite union of compact sets.

The permitted upper endpoint `t=mu(L)` gives the empty open complement and `E=L`. Arbitrarily small positive `t` is permitted. The excluded endpoint `t=0` and measure-zero general input regions are not silently used to establish the positive-measure theorems. The hypotheses `r>=1` and finite extensions of `Q_p` ensure both `D>=1` and nondiscreteness. The multiplication map by `g` is a homeomorphism because every coordinate of `g` is nonzero; its factor `d(g)` is positive and finite, so pulling a compact positive-measure region back preserves all required properties.

As a minimal check on the common-prime semigroup, take one unramified quadratic local field over `Q_p`, `J=O`, and `g=1`. Here `q=p^2` and `D=2`; attainable hull degrees are `-n log(p)`. The value `-log(p)/2` satisfies the upper inequality `u<=0` but is not attainable as a hull degree. Lemma 2 nevertheless realizes it as a region log-volume under the fixed hull `O`, by choosing raw measure `p^(-1)`. This verifies the distinction without assuming the degree semigroup is saturated.

Finally, in the note's `Q_3` example, `1` is outside `9Z_3`, the union is compact, and the difference really is exactly a null singleton. The `O`-span of that singleton is `Z_3`, while `9Z_3` is already an `O`-submodule. Thus the example refutes quotient descent in both stated senses. It asserts nothing about representative classes that exclude such singleton additions.

## Source/computation checks and remaining gap

The audit uses the stated local-field model and elementary valuation, finite-index, product-measure, and Haar facts with the correct hypotheses. No numerical experiment, finite enumeration, external theorem attribution, or software output is a proof dependency. The input identity was recorded with `sha256sum`; ancestor instructions and ledger locations were checked by direct filesystem inspection. The mathematical checks above were performed symbolically.

There is **no remaining proof gap in the stated model results**, and no counterexample was found within their hypotheses. The strongest safe conclusion is exactly the model classification, including the joint criterion and the failure of the two volume quotients to retain algebraic-hull information. The cheapest next check outside this audit is to supply precise admissible representative and equivalence definitions for the intended IUT operation, then verify that their maps and measurement order match one of these model constructions. The present verdict does not transfer across an unspecified dictionary.
