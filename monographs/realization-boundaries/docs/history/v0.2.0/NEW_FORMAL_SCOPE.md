# New formal scope — v0.2.0

## Pure intermediate subgroups

`IsPure H` is the root-lifting condition: a positive-integer root of a member of H that exists in P also exists in H. The hypothesis D ≤ H is separate. A lifted root differs from any other ambient root by torsion, and torsion is already D. This proves root closure. Clearing rational denominators then constructs `rationalImage H hD hH` as an actual rational submodule of P/D. `purePreimageOrderIso` proves the order equivalence, including both inverse identities. The positive controls show why the D-containment condition cannot be dropped: the zero subgroup is pure, but is no rational preimage.

## Countability

`finiteSupportCode` embeds actual finite-support vectors into Mathlib's dependent finitely supported function type. This proves D is countable without substituting a finite truncation. `primeSeed` proves D is infinite. The normal-form domain Q x D is countable, and every selector group is countable. The paired groups are countably infinite. For arbitrary W, the quotient map and a representative-plus-finite-correction encoding prove Countable(H_W) iff Countable(W). The dimension-language equivalence remains a named obligation.

## The ambient topology and finite targets

Each prime coordinate carries its discrete topology. P carries the genuine product topology and is bundled as a profinite additive group. Finite coordinate cuts prove density of D and every H_W. The canonical congruence kernels are open.

Every abstract homomorphism H_W → F, for a finite group F, factors through the actual coordinate quotient at the positive integer Nat.card(F). Extending that finite-coordinate map to P gives a continuous homomorphism. Agreement on the dense subgroup proves uniqueness. This construction is natural in all finite targets. A separate equivalence identifies Hom(H_W,F) with Hom(D,F), and a theorem identifies its forward map with literal restriction.

## Actual profinite completion

`CanonicalCompletion W` is exactly

```lean
ProfiniteAddGrp.ProfiniteCompletion.completion (AddGrpCat.of (preimage W))
```

It is Mathlib's limit over all finite-index normal additive subgroups. It is not a private definition of the desired product.

For each such subgroup K, extend the quotient map H_W → H_W/K to P. Naturality proves coherence, producing `ambientToCompletion`. In the other direction, the kernel of each prime-coordinate map is an actual finite-index normal subgroup. Read that quotient coordinate from the completion to construct `completionToAmbient`.

Both comparison maps are additive and continuous. Their compositions equal the identities first on the respective dense canonical images, and hence everywhere. `profiniteCompletionEquiv` packages the result as a continuous additive equivalence. `profiniteCompletionEquiv_eta` states that it sends the canonical image of every original group element to the very same ambient vector.

`completion_eta_isEmbedding` and `fullProfiniteTopology_eq` prove that the induced product topology is the full profinite topology. This is not merely a statement about matching finite-quotient cardinalities.

## Proper inclusion after completion

Specializing W to zero identifies the original named D with H_0 and proves its canonical completion theorem. Specializing to the paired rational lines proves the theorem for every binary selector. The inclusion D → G_a is proved not surjective. Nevertheless `finiteSupportToPairedCompletion` is an actual isomorphism of their canonical completions, and its canonical-point theorem verifies that it extends that same inclusion.

## Boundaries not crossed

No proof of unmarked selector classification, all-homomorphism diagonalization, endomorphism rings, exact root counts, cyclic CRT identification, topological cyclicity, seed ranks, computability degrees, or grammar diagonalization is claimed here. No verified extraction of the Python engine is claimed. The source uses classical choice and noncomputable definitions where declared.
