# Realization Boundaries — checked Lean companion v0.6.0

**Current checkpoint:** `verification/accepted_v0.6.0/run.json`, PASS. This continues v0.5.0; the entire book is not yet formalized.

## New in this checkpoint

For every rational preimage H_W in the actual infinite prime product and every positive integer m, the full root fiber of m y = x is parameterized by the actual product of coordinates at primes dividing m. It has rad(m) elements when solvable, and is empty otherwise.

The actual quotient H_W/mH_W is additively equivalent to ZMod(rad(m)). Representative formulas and the canonical quotient transition maps are checked, including the commuting modular-reduction square. The literal subgroup mH_W equals rad(m)H_W.

Every finite group is a quotient exactly when it is cyclic and squarefree in order. The converse constructs a surjection. Every finite surjection has kernel exactly |F| H_W. No target commutativity premise is assumed.

The coordinate-normalized root is unique under its zero-divisor-coordinate convention; an unrestricted solvable equation has a unique root only for m=1. The zero-multiplier/zero-target fiber is infinite and nonempty. Its natural-cardinal value zero does not assert emptiness.

All 31 parent production modules, the final PDF and the original publication ZIP remain unchanged. Five new modules add 60 named theorem/lemma declarations.

## Principal interfaces

| Declaration | Contract |
|---|---|
| `rootKernelEquiv` | Actual multiplication kernel and finite divisor-coordinate additive equivalence. |
| `rootFiberEquiv` | All solutions, not merely a count. |
| `rootFiber_card` | Positive-multiplier soluble and obstructed branches. |
| `cyclicIntegerQuotientEquiv` | Actual quotient to the cyclic radical group. |
| `cyclicIntegerQuotientEquiv_restriction` | Commuting transition with canonical modular reduction. |
| `finite_quotient_exists_iff` | Exact finite-target classification and existence converse. |
| `finite_surjection_ker` | Literal finite-surjection kernel. |
| `normalizedRoot_unique` | Unique normalized root, not unrestricted uniqueness. |
| `unique_root_iff_one` | Exact unrestricted uniqueness criterion. |

Import `RealizationBoundaries`. Names are in the `RealizationBoundaries` namespace. `docs/NEW_EXACT_TYPES_v0.6.0.md` exports exact new types; `docs/NAMED_THEOREMS.json` gives source positions and accepted axiom dependencies for all named lemmas/theorems.

## Verification

36 cleanly rebuilt and kernel-replayed production modules, 371 named lemmas/theorems, 813 audited declarations, 173 positive contracts, 41 intended rejection controls, and 118 passing command gates. These are different measures, not percentages of completion or claims of historical novelty.

```bash
export KOMOREBI_LEAN_KIT=/path/to/Komorebi_Portable_Lean_4.34.0-rc2
python3 scripts/verify.py --output ../realization-boundaries-fresh-verification
```

Use a new output directory. The pinned archived runtime is excluded from the ZIP. The verifier checks pins, snapshots source/cache inputs, deletes project build output, rebuilds serially, audits all declarations, compiles positive tests, verifies exact rejection diagnostics, kernel-replays production and checks final hashes. A failed gate returns nonzero. Negative controls are not production imports.

## Handoff

`CURRENT_CHECKPOINT.json` identifies the accepted receipt. `LEAN_VERIFICATION_REPORT.md` records scope and actual failures/resolutions. `PROGRESS_LEDGER_v0.6.0.md` gives the restart point: the actual subgroup/prime-spectrum lattice of D. Entries 6.2 and 6.3 are newly COMPLETE. Entry 6.1 retains its explicit algorithm boundary. The remaining oracle, grammar, graph and categorical interfaces are separately tracked in the 45-entry coverage map.

## Trust and license

Accepted axioms are `propext`, `Classical.choice`, and `Quot.sound`. No admitted production proof, project axiom, unsafe declaration or native-decision trust axiom was accepted. Replay uses the same Lean kernel and restored caches, not a second verifier or upstream source authentication. No external peer review, Python extraction theorem or historical-priority certification is claimed.

The open license is in `LICENSE`. Preserved publication materials retain their own terms. No runtime, dependency cache or font file is redistributed. `SHA256SUMS` covers all shipped members except itself.
