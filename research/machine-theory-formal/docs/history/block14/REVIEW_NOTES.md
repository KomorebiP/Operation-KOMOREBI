# Block 14 review and execution notes

The exact target is Core 8.1, Reviewed Core 0.2, `r:reconstruction`. This block starts from the checksum-verified Block 13 package, SHA-256 `df15d82cdb68fe42a92fe9e510775d0e49652cc882d847321173d6b967ecc546`. Its 7,245 payload files passed the shipped integrity verifier before editing. All 58 predecessor substantive modules and five source-book files are pinned unchanged.

## Source and proof review

The actual decoder has the entire record vector space as its domain. Kernel inclusion first defines a quotient map and an induced map on the attainable range; the field-linear extension theorem then supplies a full-domain decoder. Surjectivity is unnecessary. The generic proof works without finite dimension, while the explicit source-facing finite-dimensional, finite-participant theorem retains the manuscript's scope. Full-state reconstruction and the joint-kernel intersection are included.

The source's following two-dimensional F₂ example recovers both b and s from (b+s,s). Its sentence suggesting that the nuisance bit may remain unknown cannot describe s after those joint observations. The companion documents the ambiguity and uses a separate third nuisance coordinate for the general target-relative possibility. The manuscript is not edited, and this caveat does not change the proposition.

A separate agent reconstructs the critical proof from the source and reviews the raw implementation. Its findings and file hashes are preserved in `evidence/CORE81_SOURCE_AND_CODE_AUDIT.md`. The review is a second reasoning pass in the same model family, not independent peer review. Code checking and source fidelity are separate obligations.

## Corrections and actual failures

The main module's first authoring compile failed on quotient/range coercion transparency, an unavailable `LinearMap.rangeRestrict_apply` name, unused simplifier arguments and an existential-proposition normalization. The revised proof uses explicit type changes, the actual quotient equivalence lemma and `exists_prop`. The second authoring compile passed with warnings treated as errors. The theorem was not weakened and no unfinished proof was admitted. Logs are in `evidence/development14`.

The first example build failed on overaggressive product extensionality and characteristic-two normalization. Explicit pointwise extensionality and `decide` corrected it; the second build passed. Adding a bridge to the general field theorem caused a third build to hit Lean's deterministic heartbeat limit during type inference and fail a decoder rewrite. The fourth build exposed the missing `Field F₂` instance directly. Importing `Mathlib.Algebra.Field.ZMod` supplied the actual field structure, and the fifth build passed without increasing the heartbeat limit or weakening a theorem. Logs are in `evidence/development14`. These are development failures, not final gate successes or evidence against the source theorem.

The new source-facing API compiled on its first preflight. All eight new negative fixtures rejected for their required mathematical diagnostics on their first preflight, with no import failures or timeouts. The full inherited-fixture preflight also passed: the new aggregate compiled and all 135 existing contracts satisfied their required diagnostics or axiom-policy rejection, with no timeouts or import/name-resolution failures. Thus all 143 controls were exercised before the frozen cold gates. These rehearsals remain distinct from complete cold-build and kernel-replay evidence.

The first runtime-report preparation script assumed every manifest entry had a sha256 field. Directory entries do not, so it raised KeyError before producing the recovery report. The corrected script selects the six regular artifact files. The failure and successful recovery are both retained in `evidence/runtime14`. No compiler or runtime bytes were changed.

One documentation edit was rejected by the patch tool because it combined deletion and addition of the same path in one patch. It did not alter the review notes; a subsequent single-file replacement wrote the intended text. This was an editing error, not a failed mathematical check.

The current runtime is reused read-only with the previously established executable-location adapter and 4,096 MiB Lean internal memory limit. Recovery rechecks the compiler identity, all nine dependency revisions and selected artifact hashes. This does not redownload or rebuild upstream libraries. Earlier runtime and fixture failures belong to their preserved historical records and are not recounted as new Block 14 failures.

## Verification contract

Only the terminated current-source receipts in `evidence/final14`, `evidence/fresh14` and `evidence/FRESH_REBUILD_BLOCK14.json` establish release status. The verifier builds every local production module in an empty object directory, checks explicit source-facing APIs, audits actual elaborated declarations and transitive axioms, replays substantive modules through `leanchecker`, and requires the stipulated negative-control outcomes. A separately extracted frozen source snapshot supplies the second complete gate. Every production object must match byte for byte.

The foundational allowlist is unchanged: `propext`, `Classical.choice` and `Quot.sound`. Lean compilations use one thread, warnings as errors, a 4,096 MiB internal memory limit and a 45-second command wall limit. The supervisor allows 900 seconds per whole gate. No separate operating-system memory cap is claimed.

Prior blocks observed differing nonproduction `Audit.olean` binaries despite matching generated source and axiom output. The current comparison reports its own outcome. No cause is presumed, and the production comparison has no exception. A failed import or wrong diagnostic never counts as successful rejection of a mathematical falsehood.

## Assurance boundary

Classical algebraic existence does not provide a communication protocol, authentication, disclosure permission, an installed bounded decoder, a noisy inverse or a numerical stability estimate. None is claimed. Same-kernel replay with preserved dependency objects does not rebuild or independently authenticate upstream Lean and Mathlib. No Windows execution, benchmark, hosted publication or empirical data collection occurs. Five selected source results remain unformalized; the next connected target is Core 8.2.
