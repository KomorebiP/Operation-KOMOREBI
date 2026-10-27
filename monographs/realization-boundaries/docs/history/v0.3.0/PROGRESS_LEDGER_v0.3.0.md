# Progress ledger — Realization Boundaries Lean v0.3.0

## Authoritative checkpoint

- Parent: `Realization_Boundaries_Lean_v0.2.0_Checked.zip`.
- Accepted receipt: `verification/accepted_v0.3.0/run.json`, PASS.
- Current proof source: twenty production modules and the root entrypoint.
- All fifteen inherited production modules are unchanged. See `provenance/PARENT_v0.2.0_SOURCE_IDENTITY.json`.
- Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
- Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

## Newly completed

1. TailSignature: actual root semantics, homomorphism preservation, explicit numerator/denominator/support exceptions, and eventual signature for every nontorsion selector-group element.
2. SelectorClassification: finite bit changes give literal subgroup equality; unmarked isomorphism iff finite disagreement; marked isomorphism iff literal equality. The stronger any-nontorsion-image homomorphism theorem is proved without assumed diagonality.
3. HomomorphismObstruction: torsion image, unique D-valued factor, no injections or surjections under infinite disagreement, and exact embedding/surjection existence criteria.
4. NormalFormTransport: finite section difference, exact coordinate change, preservation of the actual ambient point, and an AddEquiv for the twisted group laws.
5. ClassificationConsequences: single-bit controls, constant-selector nonisomorphism with common canonical completion, no reconstruction under completion-isomorphism invariance, and no lift of the canonical completion comparison when selectors differ infinitely.

## Verification totals

Twenty cleanly rebuilt production modules, 193 explicit source theorems/lemmas, 459 audited declarations, 66 positive contract proofs, 20 intended rejection controls, 20 same-kernel replays, and 65 passing command gates. Proof sources and recorded compiler/dependency cache hashes are unchanged across the accepted run. No admitted proof, unsafe production declaration or project-specific axiom is accepted.

## Current theorem-map boundary

The original 45-entry registry remains `docs/MONOGRAPH_COVERAGE.json`. Entries 7.1, 7.2, 7.3, 7.6 are now COMPLETE. Entries 9.1 and 9.3 are PARTIAL, with the canonical-completion no-decoder/no-lift contracts proved but the exact Pro-category decoder and full global categorical statement still unimplemented. Entry 9.4 remains pending: do not confuse nonisomorphic objects with the behavior of an already supplied homomorphism.

## Next major restart point

Start `RealizationBoundaries/DiagonalHomomorphisms.lean` from the actual prime-root/quotient and finite-target interfaces.

1. For f:G_a -> G_b, define lambda_p from the image of the actual prime seed e_p. Prove the formula `(f x)_p = lambda_p * x_p` for every actual source element. A direct route subtracts `(x_p.val)` times e_p, uses the single-prime root criterion on the zero-coordinate remainder, then applies f and projects. Alternatively factor the coordinate map through the already checked p-quotient. **Do not assume diagonality or continuity.**
2. Define coordinate multiplication on P, prove it preserves D, and derive its induced rational-linear map on P/D using unique division. Prove the restriction G_a -> G_b exists exactly when the generator's tail lands in the target rational line, equivalently when lambda*u_a-s_b(r) has finite support for some r.
3. Derive the endomorphism ring, unique rational quotient scalar, surjectivity onto Q, and the nonzero-coordinate automorphism criterion. Retain exceptional denominator primes explicitly.
4. Then prove the restricted reflection theorem (book 9.4) for a supplied homomorphism whose induced completion map is an isomorphism. This does not contradict the current no-decoder and no-lift theorems.
5. The diagonal formula also supplies the finite-seed obstruction for G_a; combine it with actual topology, countability and topological cyclicity only after their relevant interfaces are proved.

A separate continuation can close root-fiber cardinalities, CRT cyclic identifications, topological cyclicity of P, and the rational-dimension formulation. Computability requires explicit presentation and oracle semantics and must retain nonuniformity of unmarked decoding. Grammar diagonalization must disagree infinitely often because finite changes preserve these groups.

## Reproduction and runtime

Run `scripts/verify.py` with `--kit` or `KOMOREBI_LEAN_KIT` and a new evidence directory. The five Library or mounted archives `Lean_Compact_01.zip` through `05.zip` restore the portable kit. Their concatenated archive hash is `f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`. The prior ledger preserves the exact Library identifiers. Do not infer filesystem paths from Library filenames.

## Preservation and limits

The printed monograph and original publication ZIP were not modified. Earlier ledgers remain historical checkpoints. `docs/history/v0.2.0` retains the preceding current documentation. Original accepted run directories remain intact. Development failures are preserved separately, including an interrupted elaboration and its replacement by a proved congruence lemma. This is internal formal verification with the same trusted Lean kernel and restored caches, not external peer review or independent upstream authentication.
