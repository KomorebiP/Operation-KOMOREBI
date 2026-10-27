# Komorebi KZFC Residual Reflection v0.7.0

An explicit first-order ZFC base theory and an internally interpreted guarded residual sentence, formalized with Lean 4.34.0-rc2 and pinned Mathlib.

## Main results

    Every membership structure M:
      M models ZFC iff AxiomSemantics(M).
      M models Theta iff InternalGuardedExtension(M).
      M models KZFC iff AxiomSemantics(M) and InternalGuardedExtension(M).

    Concrete ZFSet:
      ZFSet models the explicit ZFC theory.
      ZFSet models KZFC iff ResidualExistence.
      ZFSet models KZFC iff FilterExtensionExistence.

The ZFC presentation has eight fixed axioms and the full Separation and Replacement schemas with arbitrary finite parameter tuples. KZFC adjoins the predecessor's closed membership-only sentence Theta.

These equivalences do not assert an uncountable witness or prove KZFC modelhood. The arbitrary-structure results interpret internal witnesses without replacing them by externally computed sets or cardinalities. A complete internally coded residual-constraint classification remains unproved.

## New modules

* `GeneralMembershipSemantics.lean`: capture-free formula semantics in arbitrary membership structures.
* `ZFCAxiomSyntax.lean`: explicit ZFC sentences, both full schemas, deterministic parameter closure.
* `ZFCModelSemantics.lean`: exact axiom meanings and internal regression consequences.
* `ZFSetZFCModel.lean`: uniform proof of every axiom and schema in ZFSet.
* `InternalResidualSentence.lean`: wholly internal reading of the guarded sentence for any structure.
* `KZFCTheory.lean`: actual ZFC-plus-Theta theory and completed concrete modelhood comparison.

All 20 predecessor mathematical modules and 210 theorem declarations are retained unchanged. The new block adds 80 named declarations, including supporting lemmas. See `verification/RESULTS.json`, `verification/process_record.json`, and `verification/audit_coverage.json` for the active verdict and its exact coverage. Historical verdicts are under provenance and are not fresh verification.

## Contents and reproduction

The archive contains all Lean sources, dependency pins, theorem inventory, mathematical account, explicit proof boundary, development-failure logs, predecessor provenance, complete verification evidence and scripts. It excludes compiler binaries and compiled dependencies. Follow `REPRODUCE.md` using the retained pinned portable Lean kit.

Read `PROOF_BOUNDARY.md` before interpreting the results as a statement about foundations. No custom existence axiom, independence theorem or new consistency-strength claim is present.
