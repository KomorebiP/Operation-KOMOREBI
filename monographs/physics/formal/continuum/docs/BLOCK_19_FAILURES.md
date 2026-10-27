# Block 19 failure and repair record

This file distinguishes completed verification from interrupted or invalid attempts.

## Prior unsupported completion claim

An earlier conversational response described Block 19 as complete, but the mounted artifact state did not support that claim. The only surviving machine record was `Komorebi_Physics_Lean_v0.19.0_RESULT.md`, which stated that the production verifier had not produced a PASS sentinel and that no checked Block 19 ZIP was released. The corresponding claim audit reported zero new mathematical modules and all required claims false. That earlier response is superseded by the current release only after the cumulative production and fresh-extraction verifiers pass.

## Development failures repaired in this release

1. The first production translation contained incomplete proofs in the cosine Big-O helper, normalized-velocity quotient algebra, shell-interior conversion, and proof-dependent derivative interface.
2. The exact-velocity theorem initially used a proof argument inside the differentiated function. It was replaced by the proof-independent `positiveFrequency` function and an eventual equality to the principal branch.
3. The examples module initially omitted the namespace containing `energy` and did not have an available compiled object for its new import.
4. The new source files initially lacked the Lean `module` header and public imports, so the aggregate library correctly rejected them as non-module imports.
5. One negative control failed because of a missing namespace rather than its intended false proposition. The missing namespace was repaired and the control now fails with the designated `unsolved goals` diagnostic.
6. Several tactic drafts generated algebraic side goals or linter diagnostics. They were normalized without weakening theorem statements or adding admissions.

No failed compile, status poll, interrupted process, or provisional document is counted as proof evidence. The authoritative results are the completed JSON verification reports packaged with this release.
