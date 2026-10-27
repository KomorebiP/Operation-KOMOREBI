# Progress ledger — Realization Boundaries Lean v0.5.0

## Authoritative checkpoint

- Parent: `Realization_Boundaries_Lean_v0.4.0_Checked.zip`.
- Accepted receipt: `verification/accepted_v0.5.0/run.json`, PASS.
- Production: 31 modules and the root import entrypoint.
- All 26 parent production modules are unchanged; the finalized PDF and publication ZIP are unchanged.
- Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
- Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`; all nine locked packages checked.

## Newly completed

1. `SeedGeneration`: actual full-endomorphism orbit hull, universal invariant-subgroup property, hull invariance, topological closure, and a proper closed-coordinate certificate.
2. `SeedObstructions`: finite total support for D seed families; finite unselected support for every selector-group element; missing prime certificates for every finite seed family; algebraic and topological non-generation.
3. `GenerationRanks`: genuine least-cardinal definitions and an IsLeast proof; exact algebraic full-endomorphism, topological full-endomorphism, and ordinary topological ranks aleph_0 for D and every G_A.
4. `Procyclic`: actual finite CRT interpolation, density of the ordinary all-one cyclic subgroup in P, exact ordinary topological rank one, transport of a named generator to every actual canonical completion, and the complete paired rank-separation theorem.
5. `GenerationConsequences`: the all-one point is absent from D and every G_A; the corresponding completion point is outside the original eta image; it has infinite order. Prime seeds witness that its ordinary cyclic subgroup is proper, while its full-endomorphism hull is all of P. The latter permits arbitrarily specified coordinate multipliers and is not a finite-grammar theorem.

## Verification totals

31 production modules cleanly rebuilt and kernel-replayed; 311 named source theorems/lemmas; 698 audited declarations; 134 positive contract declarations; 33 intended rejections; 100 passing command gates. Source/compiler/cache endpoint identities pass. Production axiom dependencies are confined to `propext`, `Classical.choice`, and `Quot.sound`.

## Coverage boundary

Newly COMPLETE book entries: **2.3, 2.4, 7.9**. All 45 original records remain in `docs/MONOGRAPH_COVERAGE.json`. The general graph-reachability theorem is not completed by the diagonal specialization. Exact computability and grammar claims remain separate. No finite experiment is used as a universal proof.

## Next concrete restart point

Start `RealizationBoundaries/RootFibers.lean`, preserving all accepted sources and evidence.

1. For a positive multiplier m, define the actual root fiber `{y : H_W | m • y = x}` and the m-torsion kernel. Given one actual root, prove translation is an equivalence from the kernel to the full fiber.
2. Identify the kernel with `DivisorCoordinates m` by extending those coordinates by zero. This uses actual coordinate values, not an assumed cardinal count. Prove both inverse laws and support membership.
3. Derive finiteness and the exact root count as the product of the distinct prime divisors of m. Retain the positive-multiplier hypothesis. Failure of the root criterion gives the empty fiber.
4. Construct the explicit cyclic CRT equivalence for the finite divisor product, then compose with `integerQuotientEquiv`. The new `finite_coordinate_interpolation` is a reusable surjectivity input; it is not yet a complete cyclic quotient isomorphism.
5. Reconcile with monograph 6.2 and the remaining clauses of 6.3. Keep cardinal arithmetic, empty products (m=1), and prime-power multipliers explicit in controls.

Independent later blocks: full directed-graph reachability; subgroup/prime-spectrum classification; finitely generated subgroup structure; rational-dimension formulation; oracle-copy semantics and the marked/unmarked uniformity boundary; diagonal escape with infinitely many disagreements. Do not substitute finite support for finite support outside the selected primes.

## Runtime and reproduction

Run `scripts/verify.py` using `--kit` or `KOMOREBI_LEAN_KIT` and a new evidence directory. The five `Lean_Compact_01.zip` through `05.zip` archive-member chunks restore the pinned kit; their concatenated archive hash is `f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`. Original Library identifiers remain in the v0.1.0 ledger. The runtime is not re-embedded in the small source package.

## Preservation and limits

Historical docs are in `docs/history/v0.4.0`; previous ledgers and accepted runs remain intact. Development failures are retained separately. Verification uses the same trusted Lean implementation and restored caches, not a second independent kernel, an upstream source rebuild, or external peer review. The original book has not been silently revised.
