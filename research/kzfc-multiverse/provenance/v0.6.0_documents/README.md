# Komorebi KZFC Residual Reflection v0.6.0

## Completed scope

The release constructs an actual closed first-order sentence Theta in the language with membership as its only nonlogical symbol. It proves, in Lean, that its realization in the concrete ZFSet universe is equivalent to the previously specified residual and complete-filter-extension existence assertions.

    Theta := exists K, Guard(K) and Phi(K)

    ZFSet |= Theta <-> ResidualExistence
                  <-> FilterExtensionExistence

Phi is the unchanged predecessor's complete-filter-extension formula. Guard is newly encoded as membership syntax and independently interpreted as a regular uncountable initial cardinal. The result classifies the meaning of the sentence; it does not prove the sentence true.

## New modules

* `SetCardinalGuard.lean`: initial cardinals, inductive members, bounded small subsets, exact guard characterization for all set witnesses.
* `GuardedExistenceFormula.lean`: actual guard syntax, closed sentence, realization equivalences, baseline and counterexample regressions.
* `GuardedTheory.lean`: adjoining the sentence to an explicitly supplied base theory, the general model insertion rule, and its concrete ZFSet interpretation.

There are 210 named theorem declarations, comprising all 173 predecessor declarations and 37 additions. Supporting lemmas and interface results are included. All 17 predecessor mathematical modules are preserved byte-for-byte. Audit and root import files are intentionally updated.

## Why the guard matters

The unguarded sentence `exists K, Phi(K)` is proved true through the aleph0 instance. It is not the intended uncountable existence assertion. The guard excludes aleph0 and nonregular cardinals. The guard itself is proved to hold at every infinite successor cardinal, while the filter-extension formula fails at those cardinals. Thus the guard does not smuggle in the extension property or make the combined sentence trivial.

## Verification and provenance

Use `verification/RESULTS.json`, `verification/process_record.json`, and `verification/computation_manifest.json` for the active run. The interrupted_serial_clean directories contain incomplete historical attempts, not active verdicts. The completed run is a clean, input-hash-pinned staged session with all 47 compiler commands recorded and all 210 theorem declarations audited. Compiler attempts and environment failures are retained separately. The complete predecessor archive is under `provenance/v0.5.0`.

The distribution includes Lean sources, proof boundaries, mathematical exposition, source/API records, reproduction and verification scripts, logs and source hashes. It excludes compiler binaries, font files, the Mathlib dependency cache and project build products. The pinned portable Lean runtime remains an external prerequisite.

## Precise limits

No uncountable compactness cardinal is assumed or proved to exist. No custom Lean axiom is introduced. No internal derivation from an encoded ZFC axiom theory, arbitrary-model set-theoretic classification, relative consistency or independence theorem is supplied. The generic base theory in `GuardedTheory` is an explicit argument and is not renamed ZFC by convention.

Read `THEORY.md`, `PROOF_BOUNDARY.md`, and `REPRODUCE.md` before extending the project.
