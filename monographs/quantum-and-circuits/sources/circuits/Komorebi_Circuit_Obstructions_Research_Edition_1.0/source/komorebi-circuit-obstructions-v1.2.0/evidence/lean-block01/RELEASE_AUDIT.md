# Local v1.1.0 release audit: Lean Block 01

## Accepted scope

C01 (original companion Theorem 2.1) is formalized. The 40 actual declarations are 16 gate/circuit lemmas, 13 boundary/cut lemmas, and 11 checked example/control statements. This is one maintained claim group, not 40 new independent discoveries. C02–C08 and the other 28 numbered companion entries remain outside this block.

## Formal verification

A clean source build passed with Lean 4.34.0-rc2. All three modules passed warning-as-error compilation, all 40 declarations have printed types and axiom dependencies, and the toolchain's `leanchecker` replayed all three modules. The axiom union is exactly `propext`, `Classical.choice`, and `Quot.sound`. All four deliberately invalid compile controls were rejected. There are no active admitted proofs, custom axioms, native-decision proof oracles, or kernel-check bypasses in the maintained source.

The final receipt is `verified/verification.json`; the computation manifest pins every formal source file before and after execution and hashes every retained result/log. The abstract boundary is specialized to finite input registers and zero ancillas. Reversibility is proved from the gate definitions. Endpoint correctness is a stated hypothesis, not assumed circuit minimality or a lower bound.

## Original evidence

Before modifying the inherited release, the full active scientific suite passed: 17 unit-test methods and all seven frozen scientific-result comparisons. The inherited mathematical checker sources are unchanged. The baseline receipt is in `baseline/`. A full recursive replay of every historical research checkpoint was not performed in this block.

## Documents and predecessors

The 15-page Lean reference covers every formal declaration, with exact names and physical source lines. `PDF_AUDIT.json` records page/inventory checks and visual inspection. The old 28-page companion and v1.0.0 source archives are preserved unchanged. The old edition's no-Lean status is historical, not retroactively edited.

## Development faults

See `DEVELOPMENT_FAILURES.md`. The compiler download was blocked and was replaced by partial recovery of the user's portable toolchain. An XOR precedence ambiguity and a comment-sensitive inventory regex were corrected. A PDF title-key parse error and an overflowing inline table were corrected. All final proof checks and PDF checks passed. Failed logs are retained without being promoted to evidence of success.

## Remaining boundaries

The recovered compiler was executed and its binaries hashed, but the complete upstream distribution was not reassembled or authenticated. The bundled checker is not an independent kernel implementation. No independent human review, novelty claim, P versus NP resolution, new degree lower bound, or hosted GitHub publication is asserted. The local Git tag identifies a deliverable source/evidence snapshot; final ZIP and bundle replay receipts are supplied alongside the delivery artifacts.
