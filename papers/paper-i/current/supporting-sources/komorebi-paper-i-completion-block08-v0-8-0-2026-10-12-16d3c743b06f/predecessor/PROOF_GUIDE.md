# Paper I completion, Block 07: noncommutative radical lifting

## Scope

Let R be an arbitrary unital ring and let M be a finitely generated left R-module. No commutativity, Noetherian, finite length or semisimplicity assumption is imposed. Write J = Jac(R), and use the literal submodule JM consisting of finite sums of radical multiples.

This block proves the full set/family generator-lifting equivalence and the existing canonical seed-rank identity

    seedRank_R(M) = seedRank_{R/J}(M/JM).

For a noncommutative local ring, it constructs the division-ring structure on the actual R/J and proves

    seedRank_R(M) = dim_{R/J}(M/JM),

with LEFT vector-space dimension. These are classical mathematical results integrated into Paper I's actual objects and definitions, not claims of new classical discoveries. Verification status and exact command outcomes are recorded separately in VERIFICATION.json.

## 1. Noncommutative Nakayama is proved at the required scope

Source: `source/extension/PaperICompletion7/Nakayama.lean`.
Namespace: `Komorebi.PaperICompletion7.Nakayama`.

For a finitely generated module, every proper submodule N is contained in a maximal submodule P. The module Jacobson radical is contained in every such P. Therefore N + Jac_R(M) cannot equal M while N is proper. This proves `eq_top_of_sup_module_jacobson`.

The pinned library proves that the ring radical acting on M lies in the module radical. Thus, for ANY left ideal I contained in Jac(R),

    N + IM = M  implies  N = M.

This is `eq_top_of_sup_ideal_smul`; `eq_top_of_sup_jacobson_smul` is the usual specialization. Neither two-sidedness of I nor commutativity is needed for this lifting assertion. Two-sidedness is required later when R/I itself must be a scalar ring. The proof does not silently replace the noncommutative statement with a commutative Nakayama lemma.

## 2. The quotient and scalar action are literal

`IdealTop I M` abbreviates the actual quotient M / (I • top). For a two-sided ideal, `idealTopMap I` is the actual quotient projection, semilinear with respect to the actual ring quotient map R → R/I. Its representative and scalar-action theorems are definitional equalities:

    q(x) = [x],       q(a • x) = [a] • [x].

`idealTopMap_surjective` proves that every quotient vector has a lift. Independently, `idealTopMap_ker` proves the exact kernel equality

    ker(q) = I • top.

Surjectivity is not used as a substitute for that kernel computation. For a submodule N, the comap of its image is N + IM. The exact kernel plus Nakayama therefore gives `map_eq_top_iff`.

## 3. The generating-family theorem preserves the family

Source: `source/extension/PaperICompletion7/ModuleTop.lean`.
Namespace: `Komorebi.PaperICompletion7.ModuleTop`.

`image_generates_iff` uses the original `Komorebi.SeedRankBasics.Generates`, which is actual submodule span. The image of a span under the semilinear quotient map is the span of the image. Thus

    Generates_{R/I}(q(S))  iff  Generates_R(S)

for every set S, under I ≤ Jac(R) and finite generation of M.

`family_generates_iff` preserves the original index type; it is not merely a statement that some equally sized generating family exists. `lifts_generate` states that ANY specified lifts of a generating quotient family generate M. `quotient_basis_lifts_generate` specializes this to lifts of an actual quotient basis.

## 4. Equality of the canonical minima is derived

The seed rank here is the existing cardinal minimum of sizes of generating sets, not a new definition built to equal the quotient dimension.

`seedRank_eq_idealTop` proves both inequalities. Mapping a minimum generating set down gives the quotient inequality. Conversely, choose a minimum quotient generating set, choose actual lifts using surjectivity, prove their image is precisely the original set, and apply generator lifting. The cardinality of the lifted image is no greater than the original set's cardinality. This gives the reverse inequality.

`seedFinrank_eq_idealTop` derives the equality of the original natural-valued minima. `idealTop_finite` separately establishes finite generation of the quotient as a module over R/I.

The manuscript-facing definitions and results are:

- `RadicalTop R M`, the actual M/JM.
- `generates_iff_radicalTop`, the full set equivalence.
- `seedRank_eq_radicalTop`, the canonical cardinal equality.
- `seedFinrank_eq_radicalTop`, its natural-valued counterpart.

No semisimplicity of R/J is required. When R/J is semisimple, the pinned `IsSemisimpleRing.isSemisimpleModule` instance applies to this actual quotient; its name, full type and axiom dependencies are checked in the declaration crosswalk. There is no claim here that R/J is semisimple for every ring.

## 5. The residue division ring is constructed, not supplied

Source: `source/extension/PaperICompletion7/LocalResidue.lean`.
Namespace: `Komorebi.PaperICompletion7.LocalResidue`.

In a local ring, if a + b = 1 then at least one of a or b is a unit. Consequently two proper left ideals cannot sum to the whole ring. Distinct maximal left ideals would have that sum, so the maximal left ideal is unique.

The ring Jacobson radical is the intersection of maximal left ideals. Since the maximal left ideal exists and is unique, `jacobson_isMaximal` proves that the actual radical is maximal. It is already a two-sided ideal. `residueDivisionRing R` then constructs `DivisionRing (R / Ring.jacobson R)` from these facts and the pinned quotient construction.

There is no `CommRing R` assumption, no chosen commutative residue field, and no hypothesis asserting that the desired quotient is a division ring. The division-ring structure uses the existing quotient addition and multiplication.

Over that actual residue division ring, the minimum size of a generating set is the LEFT vector-space dimension. Composing that fact with the proved module-top equality gives `seedRank_eq_residue_dimension` and `seedFinrank_eq_residue_finrank`.

The local-ring class excludes the zero ring. The module itself may be zero, and the general lifting/rank theorems do not impose a nonzero-module assumption.

## 6. Exact mathematical boundary tests

`tests/BoundaryConsumers.lean` contains 19 public theorem assertions plus supporting constructions and private proofs.

### A genuinely noncommutative ring with a nonzero radical

Let H be the rational quaternion division ring, and let DH = H ⊕ Hε be its trivial square-zero extension. Multiplication is

    (a,b)(c,d) = (ac, ad + bc).

The tests construct its local-ring instance, prove that the actual radical is the kernel of first-coordinate projection to H, and prove ε ≠ 0, ε² = 0 and ε ∈ Jac(DH). They verify that the quaternion generators i and j do not commute, including after inclusion in DH.

The regular DH-module has seed rank one. Its actual module top has left dimension one over the internally constructed radical quotient division ring. The family {1 + ε} is proved to generate by the NEW quotient-lifting theorem. Thus the test is not merely a commutative field example, nor a noncommutative example with a zero radical where lifting would be vacuous.

### The radical-containment hypothesis is necessary

For the integer ring, take N = 3Z and I = 2Z. The test proves N is proper but

    N + I Z = Z.

The new Nakayama theorem implies that I cannot be contained in the Jacobson radical, which is also checked as an explicit theorem. This is an actual counterexample to arbitrary-ideal lifting, not just a rejected API application.

### Finite generation is necessary

Let R = Q[[t]] and let F be its fraction field, considered as an R-module. The test proves t lies in the actual Jacobson radical and its action on F is invertible, so

    Jac(R)F = F.

Consequently the actual radical quotient has seed rank zero, while F itself is nonzero and has nonzero seed rank. The test derives that F is not finitely generated over R. This is a genuine counterexample to dropping finite generation, not a missing-instance demonstration.

Other tests check the exact semilinear quotient kernel, representative scalar action and zero-module convention. These are Lean proofs, not numerical experiments.

## 7. What this does not establish

This block does not prove the general matrix-product formula over arbitrary division rings, construct a Wedderburn decomposition, or implement a radical/generator/decomposition algorithm. The radical/top reduction needed for that next formula is now available and must not be reconstructed as if still missing.

The nonsplit semisimple, regular-module multiplicity, expanded packet/functorial/topological and executable-algorithm obligations remain in the coverage map. Papers II–XII have not been rerun in this audit sweep.

## Pinned primary dependencies

The implementation uses the supplied pinned Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, especially `RingTheory/Jacobson/Radical.lean`, `RingTheory/Ideal/Quotient/Basic.lean`, `RingTheory/LocalRing/Basic.lean` and the canonical span-rank results. No dependency was updated. The proof-level audit and kernel replay boundaries are explained in the completion report and `audit/SEMANTIC_REVIEW.md`.
