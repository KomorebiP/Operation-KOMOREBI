# Strong Artin research boundary after v0.11

## What is now closed

At the exact prime-cyclic defect algebra, the finite geometric ambiguity and its support propagation are explicit and checked:

1. `p` generic quotient-character branches form one cyclic orbit;
2. they collapse modulo `p` to one reduced point with nilpotent thickness `p`;
3. the cyclic twist is an actual algebra automorphism;
4. any nonempty twist-stable branch support is the full orbit;
5. any surjective twist-equivariant quotient algebra through which one branch factors admits every branch.

## Strongest next theorem

A relative/global support theorem should supply an algebra `B` and map

`q : A_cyc -> B`

in the automorphic or patched setting such that:

- `q` is surjective (or replace this by the exact quotient/support condition needed in the chosen formulation);
- `B` carries a quotient-character action `beta` with `beta ∘ q = q ∘ twist`;
- at least one generic characteristic-zero branch factors through `B`.

Then `all_branches_factor_through_equivariant_surjection` gives every cyclic branch automatically.

## Why this is narrower than general nonregular automorphy lifting

The singular direction is not arbitrary. It is the explicitly modeled quotient-character factor `A_cyc`. A future patching argument can try to kill/control transverse deformation directions while **retaining** this one cyclic factor. The v0.11 result then handles the full finite branch orbit by symmetry.

## Not proved

- existence/nonvanishing of the relevant patched automorphic module;
- an `R=T` or full-support theorem in this singular weight-zero setting;
- twist-equivariance of that patched/Hecke support;
- local deformation-component compatibility at all ramified places;
- unrestricted Galois realization or Strong Artin.
