# Paper III, Section 17 — continuation report v0.3.0

**Local continuation:** 19 October 2026  
**Current classification:** Mathematical development and exact finite testing advanced. **Not a Lean-checked closeout**. Paper III remains in progress.

## Scope completed in this working block

The exact general expansion for any finite resolution of the identity is proved in ordinary mathematics, and a plausible Lean proof has been written in a nonproduction draft module. A stronger formulation was identified: the expansion itself needs neither idempotence nor pairwise annihilation. These extra properties enter only to make the packet ranges into invertible coordinates. The same source constructs the literal range-to-range multilinear jet and derives the reconstruction statement for actual projector systems.

A second draft module proves the ambient continuous multilinear operator norm estimate using mathlib's stated inequalities. This estimate bounds the full projected jet by the output operator norm, the multilinear operator norm and the product of the input projector norms. Moving from ambient extensions to range-restricted continuous maps requires a separate bounded-range identification. Neither draft has been compiled or kernel replayed here. The accepted Section 16 code and object files remain unchanged.

## Executed evidence

- ZIP recovery: inherited v0.2.0 archive CRC passed on intake. The exact previous manifest was preserved for comparison, and no accepted mathematical source module was modified.
- 2,622 exact finite assertions passed in `tests/section17/exact_section17.py`. This includes 75 distinct arbitrary-rank tensor reconstruction tests, 174 exact operator-norm inequality checks, 192 independently symbolically differentiated decorated second-order chain-rule cases, 35 Touchard counts, and 28 Stirling/partition checks. Further assertions verify projector idempotence, completeness, annihilation, output-range membership and per-output sums.
- Four deliberate invalid shortcuts were rejected: dropping cross packets, dropping completeness, inferring inverse coordinates from nonorthogonal complete idempotents over `F_2`, and omitting intermediate packet labels in the higher chain rule. The last shortcut had 154 explicit counterexamples among the symbolic configurations.
- A static source-policy pass rejected no forbidden admitted/opaque/unsafe proof patterns in the two draft Lean modules. **A lexical scan is not a Lean compilation, axiom audit or kernel replay.**
- Runtime: `lean` and `lake` are absent from this container PATH; the seven-part 2.9 GB pinned toolchain archive is not included in the inherited package. No new Lean proof claim was accepted.

## New facts established mathematically

1. An identity expansion for all multilinear forms is independent of symmetry and requires only the sums of projectors to equal identity. This isolates the exact algebraic reason reconstruction works.
2. A genuine range-to-range packet jet is obtained by composition with the range inclusions, the given multilinear map and the output projector, with no invented external coordinates.
3. The finite norm estimate follows from two operator norm composition inequalities. Boundedness is necessary in infinite-dimensional Banach contexts; Section 16's algebraic projectors do not automatically provide it.
4. The second-order decorated chain rule contains both the `D²F(DG,DG)` branch and the `DF(D²G)` branch, with separate intermediate packet sums. Omitting either can destroy cross interactions.
5. The number of intermediate packet labelings is `sum_{k=1}^n S(n,k) M^k`, not just `M^n`; the exact tests enumerate partitions to independently validate this combinatorial count.

## Unresolved

- Compile the two draft modules in the exact pinned Lean/mathlib environment; resolve any errors; run source-owned census, axiom audit, logical replay, and negative compiler controls.
- Bind the norm result to actual Banach-range continuous maps, then connect it to `iteratedFDeriv` and the manuscript's smoothness hypotheses. The unrestricted Taylor integral, higher partition composition and pruning claims are not formally accepted.
- The independent October 16 `98+2 / 2693` formalization is still missing its matching proof sources and receipts, so it is not counted.
- Publications are not renumbered or marked as final. Licensing remains unselected. No existing completed proofs are downgraded or silently overwritten.

## Next restart

Start from `formal/drafts/MultilinearPacketJets.lean` and `formal/drafts/BoundedPacketJetNorm.lean`. Recover the pinned runtime described in `verification/RUNTIME_IDENTITY.json`, use a fresh empty output object directory, and compile the new sources. Once this passes, complete the genuinely continuous range bridge and the formal derivative correspondence. Keep all rejected attempts. Do not move to Paper IV until Paper III's publication-to-formalization mapping has been reconciled.
