# Semantic review: Paper I Block 07

## Publication-facing objects

The ring typeclass is `Ring`, not `CommRing`. The module is a left `Module R M`. Finiteness is `Module.Finite R M`, not an assumed finite basis over R. Arbitrary finitely generated modules over rings need not be free.

The ideal submodule is literally `I • (⊤ : Submodule R M)`. The module quotient is literally `M ⧸ I • top`. Its scalar ring is literally `R ⧸ I`. Two-sidedness of I is needed for that ring quotient and is automatic for the Jacobson radical. The weaker Nakayama lifting theorem permits arbitrary left ideals inside the radical.

The quotient map is semilinear over `Ideal.Quotient.mk I`. Its underlying function, representative action and scalar action are definitional. Its surjectivity and exact kernel are separately proved. Nothing is inferred solely from matching dimensions.

The generating predicates and rank definitions are exactly those in `Komorebi.SeedRankBasics`. Both directions of the generating-set/family theorem use actual spans. The minimum-cardinality proof gives both inequalities using quotient images and actual quotient lifts.

No semisimplicity of R/J is inferred for an arbitrary ring. The supplementary semisimple statement is an application of the proved upstream instance when an `IsSemisimpleRing (R/J)` assumption actually exists. No such assumption is required for generator lifting or the rank equality.

## The noncommutative local boundary

`IsLocalRing R` is used without `CommRing R`. The proof establishes that the Jacobson radical is a maximal left ideal, then uses its two-sidedness to construct the division ring on the actual quotient. The dimension is left dimension for the inherited scalar action.

A caller does not supply the desired maximality theorem, division-ring certificate, rank equality, a decomposition, or a generating family. The only module hypothesis for the manuscript-facing rank formula is finite generation, in addition to the ordinary ring/module structures.

The natural-valued rank formula is accompanied by the cardinal formula and a separate finite-generation result for the quotient. It is not an equality of two `toNat` values used to conceal infinite ranks.

## Tests are mathematical consumers

The dual-quaternion example is noncommutative and has a nonzero radical. The lift {1+epsilon} is tested through the new generator-lifting theorem. The integer example proves actual failure with an ideal outside the radical. The power-series fraction-field example proves actual failure without finite generation. Missing-instance rejection controls complement, rather than replace, these examples.

## Object audit classification correction

The expanded inspection reads serialized compiler objects as well as the imported checked environment. Seven inherited compiler-generated declarations ending in `_unsafe_rec` have `isPartial = true`. Earlier source-owned inventory totals included these entries without distinguishing them from logical declarations. Lean's official kernel-replay mechanism excludes unsafe and partial runtime implementations.

This block records these seven exact names separately, retains their source ownership and transitive-axiom inventory, rejects any unexpected partial declaration, and forbids authored partial/unsafe declarations in production sources. The mathematical sources did not need changing.

For the new whole-closure replay, none of the project's modules or constants is trusted in the starting kernel environment. The replay input consists of every checked logical declaration from the entire production closure plus the new boundary module. An exact NAME-SET comparison, not just a count, matches these logical entries against the imported ownership audit. The partial runtime helpers are not in that set and are separately matched by name. Any dependence of a logical declaration on an unavailable project constant would prevent successful replay.

One byte-for-expression-identical generated theorem can appear in more than one module's serialized data. Such duplication is accepted only when type, universe parameters, theorem group and proof expression all match. A non-theorem duplicate or an incompatible duplicate is rejected.

The replay wrapper is audit instrumentation and uses unsafe I/O for Lean's object reader, as the official checker does. It is not a mathematical production module or an extra axiom. Its malformed-proof control adds a well-typed claim `0 = 1` with the wrong proof `Eq.refl 0` and must be rejected by the kernel.

This is stronger project-dependency replay than importing project dependencies as already trusted for each single-module replay, but it remains the SAME Lean kernel. Cached upstream Mathlib is authenticated and reused, not freshly rebuilt or independently verified. No claim of executable runtime correctness for the generated partial helpers is made.

## Publication delta

Two proof-level records are intended to move to covered only after the accepted verification returns PASS: the module-top theorem and local-algebra formula. The noncommutative Nakayama classical input becomes integrated. The semisimple formula remains partial, with only its radical/top reduction now discharged. The coverage generator asserts that all 108 stored statements, source proofs and source-location/hash records are unchanged.
