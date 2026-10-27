# Independent audit of the native-conjecture continuation

Date: 2026-09-08.

## Target and primary verdict

Target: whether the additions in `native_work/` establish the original native Conjectures 13.2 and 13.3 and whether their narrower results are valid as stated.

**Primary verdict: incomplete, with the smallest missing implication identified.** The original claims still lack specified categories, lift functors, presentation equivalences, packet types and reconstruction maps. The additions correctly preserve this status. No narrower result was improperly promoted to the unrestricted original.

The polynomial obstruction argument is valid for its stated finite presentation. The intrinsic finite-algebra obstruction is a correct specialization of checked external results. The topology argument validly refutes its explicit Hausdorff interpretation. The affine Lean source accurately states a narrower specialization. This is an independent agent audit, not third-party proof checking or human peer review.

## Files read

- `native_work/Native_Conjectures_Progress.md`
- `native_work/lean/FiniteAffineObstruction.lean` and its saved axiom output
- `native_work/check_polynomial_obstructions.py`
- `native_work/polynomial_obstruction_checks.json`
- `native_work/polynomial_obstruction_manifest.json`
- Original manuscript text from `native_work/paper_ix.txt`, especially Definition 1.1 and the native claims on printed page 26

No author-owned files were edited by this reviewer.

## Obligation matrix

| Claim or dependency | Audit result | Reason |
|---|---|---|
| Polynomial correction identity | Passed | Monomial expansion; terms with two corrections contain `p^(2L)`, divisible by `p^(L+1)` for `L>=1` |
| All next-level solutions are correction digits | Passed | Each lift of a fixed residue vector has a unique correction in the finite vector space |
| Obstruction zero iff one-step lift | Passed | Exactly the equation `e + J*t = 0` |
| Representative independence | Passed | Same Jacobian modulo `p`; residual changes by `J*s` |
| Obstruction finite and lift count exact | Passed | Finite-field image/kernel dimensions; no nonsingularity assumption |
| Raw Jacobian cokernel presentation independence | Failed, correctly disclosed | `(X)` and `(X,0)` have distinct raw cokernels |
| Intrinsic finite-algebra obstruction | Passed in stated scope | Exact square-zero specialization of Stacks 08S5 |
| Finite presentation computes the intrinsic group | Passed | Stacks 0GPU plus presentation comparison in 00S1 |
| Intrinsic obstruction group finite | Passed | Hom from finitely generated conormal module to `F_p` injects into a finite power of `F_p` |
| Every native seed system falls within this algebraic setting | Not addressed | Required encoding and lift-preservation theorem not supplied |
| Dense diagonal integers give topological counterexample | Passed in stated interpretation | Equality locus over Hausdorff target is closed; diagonal integers are dense and proper |
| Counterexample refutes every interpretation of native 13.3 | Not claimed | Continuity, Hausdorff target and canonical local maps are explicitly required |
| Finite/profinite CRT reconstruction | Passed in stated scope | Ring CRT commutes with polynomial evaluation; completion is distinguished from global integers |
| Finite equality-label representation iff rectangularity | Passed in stated scope | Three-edge closure and odd-path shortening |
| Universal property of the component quotient | Passed | Functions identifying every relation edge descend uniquely to connected components |
| Full polynomial or intrinsic theorem checked in Lean | Not claimed | Standalone source is affine only |

## Polynomial and affine audit

The residual `F(x)/p^L` is an exact integer vector because `x` represents an actual solution modulo `p^L`. Dividing the Taylor congruence by `p^L` is therefore legitimate. The hypothesis `L>=1` is necessary for the nonlinear monomial argument and is present. It also makes the Jacobian unchanged by replacing `x` with `x+p^L*s`.

The correction equation uses a plus sign. Vanishing of the cokernel class gives a solution to that equation because the image of `J` is closed under negation. A nonempty solution set is an affine coset of the kernel, which proves the torsor assertion and stated finite count. No smoothness or invertibility assumption is silently used. Cases of zero variables, zero equations and zero Jacobian remain valid.

The raw quotient depends on equations. For `(X)` at zero, `J` is surjective and the quotient is zero. For `(X,0)`, the image consists of vectors with second coordinate zero, so the quotient is `F_p`. These presentations define the same solution functor. Thus the prose correctly refuses to equate representative independence with presentation independence.

The affine Lean construction takes the quotient of `(Fin e -> ZMod p)` by the actual range of reduction composed with the integer-linear map `A`. It proves finiteness for nonzero `p`, extracts the residual from the divisibility hypotheses, and characterizes every representative of the original residue by an integer correction vector. The cancellation of `p^L` occurs in the integers, where nonzeroness is established. The theorem does not use vacuous field divisibility.

The formal affine theorem permits any natural `p>0`, including `p=1`, and `L=0`. This is valid for the affine argument. The polynomial prose only claims primes and `L>=1`; neither range is silently transferred to the other.

The final authoritative transcript `native_work/lean/replay_02/native_affine_audit.json` was inspected and has aggregate PASS. The revised source and the positive-control source both compiled with exit code zero. All thirteen main declarations (nine theorems, three definitions, one abbreviation) and all four positive-control theorems have axiom reports, with no missing declarations or unexpected axioms. The two false strengthenings were rejected with exit code one and the expected type mismatches. The four positive controls include a genuinely nonzero obstruction, an actual solution modulo two, and a proof that the same constant system has no solution modulo four.

The source SHA-256 recorded by the final replay is `8f7ffb9f8387cbb23949f65d8d79ef601dd677ed567208f0bdeff475609ba056`. Final report SHA-256 reported by the producing agent is `cb74691585fe1399ea66d511f8c1e2b6423bd1c0a5fca5576778226f313a3cb4`. This reviewer inspected the report and raw logs rather than running a second compiler replay. No pending native compiler gate remains in this audit.

## Independent external-source check

The following live primary sources were independently read on 2026-09-08. No immutable revision is claimed.

1. [Stacks Lemma 91.2.1, 08S5](https://stacks.math.columbia.edu/tag/08S5): the ring-map lifting obstruction and its vanishing criterion.
2. [Stacks Remark 91.2.4, 0GPU](https://stacks.math.columbia.edu/tag/0GPU): the conormal/differential presentation of the obstruction group.
3. [Stacks Lemma 10.134.2, 00S1](https://stacks.math.columbia.edu/tag/00S1): comparison of polynomial presentations gives homotopy-equivalent naive cotangent complexes, with comparison maps determined up to homotopy.

For the application, take the source algebra extension to be the identity extension of `B` with zero kernel, the target extension to be `Z/p^(L+1) -> Z/p^L`, and all base algebras to be `Z` with identity maps. The target kernel is `p^L/p^(L+1)`, identified with `F_p`; it is square zero for `L>=1`. Its `B`-action factors through the specified residue map. These choices meet the lifting theorem's hypotheses.

The finite-presentation calculation must be connected to the intrinsic complex. The third source explicitly supplies that arrow; this reviewer requested that its citation be added to the main note. With a finite presentation `P -> B`, the module `I/I^2` is finitely generated over `B`. A linear map from that module to `F_p` is determined by finitely many generator values, so the Hom group is finite. The cokernel of a map into that finite group is finite as well. No complete-intersection or projectivity hypothesis on `I/I^2` is required for this finiteness argument.

The intrinsic Ext group, rather than the raw list-of-equations cokernel, supplies presentation independence. Nothing in these external results automatically identifies every operator or weighted-topological seed object in the manuscript with a finitely presented commutative integer algebra. That remains the exact missing application step.

## Topological counterexample audit

Let `A=Z_2`, `B=product_(p>2) Z_p`, and let `D` be the image of the diagonal integer map into `A x B`.

- Every nonempty basic open set restricts finitely many coordinates to finite congruence conditions. Refining each open coordinate to a residue ball and using finite CRT yields an integer in the open set. Hence `D` is dense.
- The tuple with 2-adic coordinate zero and all odd coordinates one is outside `D`. An integer mapping to zero in `Z_2` must be divisible by arbitrarily large powers of two, so it is zero, contradicting its 3-adic coordinate being one.
- For continuous maps from `A` and `B` to a Hausdorff space `C`, their equality locus is the preimage of the closed diagonal of `C x C`. It is therefore closed. It cannot equal the proper dense set `D`.

This argument does not need a group structure on `C`, compactness, or a claim that all common quotients are trivial. It is stronger and simpler as an equality-locus obstruction. It specifically concerns canonical embeddings of global integers into their local realizations. Arbitrary abstract bijections, non-Hausdorff targets or noncontinuous maps are outside the claim.

For the stated integral local factors, taking the restricted product with the whole `Z_p` as the distinguished subset gives the ordinary product. The completion correction is accurate: compatible finite congruence data reconstruct profinite integers, and the diagonal image of global integers is generally a proper dense subset. The note does not promote this completion identity to recovery of global integer solutions from arbitrary local tuples.

## Finite compatibility quotient audit

The added finite-set theorem is correct. For a relation `R` between finite sets `A` and `B`, the stated three-edge condition is necessary for any representation `R(a,b) iff f(a)=g(b)`: transitivity of equality forces the fourth edge.

For sufficiency, the graph vertices are the disjoint union of `A` and `B`, so every path from an `A` vertex to a `B` vertex has odd length. The first three edges of a path can be replaced by a single edge using rectangularity. Induction reduces the path to an edge of `R`. Thus two opposite-side vertices share a component precisely when they are related. Isolated vertices cause no false cross pairs. Empty sets and the empty relation are covered by the same component construction.

The component set is finite as a quotient of a finite vertex set. Its universal property is valid: any pair of maps agreeing on each relation edge combines to a function constant on paths and therefore factors uniquely through components. This property holds even without rectangularity. If rectangularity fails, the violating three-edge pattern explicitly gives an extra fourth cross pair in the equality locus, so the note is correct that the equality locus then strictly enlarges the relation.

The universal property is not a cardinality-minimal label claim. For example, isolated vertices on one side can sometimes share a label without changing the cross relation, whereas the canonical component quotient keeps them separate. The note explicitly avoids that unsupported minimum claim. It also correctly states that the set-theoretic theorem supplies no automatic continuity, Hausdorff topology, spectral structure, Frobenius compatibility or proof of the unspecified native spine statement. The evidence is an elementary prose proof, not Lean verification.

## Computation audit and replay

The script uses exact Python integers. Polynomial values are evaluated by Horner's method, while the Jacobian is computed separately from derivative coefficients. Every correction digit is compared with direct evaluation modulo the next prime power. This is a meaningful independent implementation check of the correction criterion.

A read-only replay imported the module without invoking its file-writing `main`, reran all exhaustive cases, and compared the recomputed counts with the saved output. It passed:

| Quantity | Count |
|---|---:|
| Coefficient vectors | 625 |
| Residues scanned | 130000 |
| Solution points checked | 6502 |
| Liftable points | 5118 |
| Obstructed points | 1384 |
| Singular solution points | 3004 |

The declared scope is one-variable polynomials of degree at most three, coefficient vectors in `{-2,-1,0,1,2}^4`, primes `2,3,5`, and precisions `1,2,3`. Script and saved-output SHA-256 values matched the manifest. The installed computation-manifest validator returned success. There is no randomness, floating arithmetic or resource truncation.

**Computation verdict:** implementation and finite assertion verified in the stated range. This does not prove the universal polynomial theorem, the intrinsic Ext theorem, or either unrestricted native conjecture. The main note correctly separates those evidence classes.

## Required status boundary

Retain native Conjectures 13.2 and 13.3 as unresolved in their original generality. The concrete advances may be reported as a proved polynomial specialization, a Lean-checked affine specialization, a known intrinsic obstruction theorem under an explicit algebraic restriction, a proved counterexample to the specified Hausdorff reconstruction interpretation, and a proved finite-set compatibility criterion with its explicit universal property.
