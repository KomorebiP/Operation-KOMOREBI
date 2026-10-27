# Shared correction quotient

Author: Komorebi P.

`SharedCorrection.lean` works over arbitrary commutative rings and additive modules. It requires neither a field nor finite dimension, nor a surjectivity assumption on either original map.

For linear maps `J : U →ₗ[R] V` and `K : U →ₗ[R] W`, it constructs

- `commonKernel J K = ker J ⊔ ker K`;
- `Common J K = U / (ker J ⊔ ker K)`;
- linear, surjective labels from `range J` and `range K` to `Common J K`;
- the joint map from a correction to its two local images;
- a genuine fiber-product submodule defined by equality of the labels;
- an explicit linear equivalence between the joint image and that fiber product.

The principal equality is unconditional:

`[u] = [v]` in the common quotient if and only if there exists `w` with `J w = J u` and `K w = K v`.

Proof mechanism: quotient equality gives `u-v = s+t` with `J s=0` and `K t=0`. The single correction `w=u-s=v+t` has both requested images. Conversely, such a correction expresses `u-v` as `(u-w)+(w-v)` in the kernel sum. The labels are constructed using the first isomorphism theorem and quotient linear maps, not a guessed representative.

Two universal properties are also proved: any linear observation annihilating both kernels factors uniquely through the common quotient, and any pair of linear maps on the attainable local images agreeing on every correction factors uniquely through the two labels. The latter is the pushout universal property for the range restrictions, not a minimum-cardinality claim.

The common quotient is finite whenever either target is finite, even when the correction module is infinite. This follows from the corresponding surjective label on that map's attainable image.

These results concern explicitly supplied linear correction maps. They do not assert a global p-adic reconstruction, a minimum number of labels, presentation independence for unspecified arithmetic seed systems, or the original manuscript conjectures without their missing definitions. This block supplies a concrete shared-correction instance of the finite gluing criterion.

The source uses public module declarations. All local proof checks use the pinned portable Lean 4.34.0-rc2 runtime, one Lean thread and warnings as errors. The enclosing release verifier supplies fresh compilation, full declaration axiom reports and independent controls.
