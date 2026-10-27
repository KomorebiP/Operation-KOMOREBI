# Continue from Model-Theory Normalization v0.6

This is a continuation of v0.5, not a new p-adic block. Read NORMALIZED_CORE,
FORMALIZATION_COVERAGE, RESULTS, PROOF_AUDIT_v06 and DEVELOPMENT_FAILURES first.
Do not modify any frozen historical archive. Verify FILE_MANIFEST and current
v06 evidence manifests before running scripts that regenerate outputs.

## What changed

The old fast Smith producer remains unverified. A new actual Lean implementation
uses a positive-pivot integer echelon basis for the modular preimage containing
m Z^d. Both insertion-span inclusions and membership equivalence are formal.
The cached worklist is proved equal to the original reference at every fuel budget.
The prime-power sufficient-fuel and first-order defining-formula endpoints are
composed. All 203 inherited/stress problems are now direct kernel computations,
not merely supplied trace checks. Exact verification counts belong in RESULTS.

## Main declarations

- EchelonCore: coordinates_correct, coordinates_solution, synth_injective.
- EchelonInsert: gcd_update_data, insert_correct, lattice_insert.
- EchelonModular: diagonal_kernel, build_correct, insert_preimage, member_correct.
- EchelonDiscovery: fastWorklist_matches, fastPrimeDiscover_eq_reference,
  fastPrimeDiscover_total_correct, fastPrimeDiscover_defines_behavior.

## Next high-value obligation

Control coefficient growth in the integer basis. It is upper triangular but not
Hermite-normalized. Prove a tail-row reduction pass preserves the exact lattice,
keep positive pivots, and derive explicit stored/intermediate coefficient bounds.
Only then make an asymptotic bit-complexity claim. A Python suite observed stored
coefficients up to 730 bits, which is evidence of the issue, not a universal bound.

Do not silently call this canonical Smith form or equate d auxiliary integer rows
with the intrinsic minimal modular generator count. Keep the full m Z^d preimage;
removing those rows without another correct representation loses torsion.

Other independent targets: executable minimum-coordinate basis extraction, parser
verification, relational discovery, structural holdouts, and independent review.

## Execution

The current runtime is not bundled. Use the precise pins and fresh replay commands
in README. Existing .olean paths in COLD_STATE are historical execution evidence and
may not exist in another session. No process is promised to continue after a turn.
