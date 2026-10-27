# Block 45 failure ledger

- The first previously surfaced Block 45 release was invalid because its linked files were never created. It was discarded; v0.44 remained authoritative.
- The supplied v0.44 source archive contained no executable Lean runtime. The seven-part offline runtime was restored and attached at the exact Lean and Mathlib pins.
- A broad portable-runtime self-test exceeded the command window after initial checks. It is not counted as a complete runtime verification.
- Initial compact-ball proofs encountered a local-instance linter warning and a topology inference mismatch. The proof was repaired with an explicit target space for the derivative bound.
- Early compact-time drafts had ambiguous `Mode` and `HilbertSpinor` names, a deprecated lemma name, and two algebraic rewrite failures. All were repaired before the accepted warning-as-error compile.
- One duplicate long Lean compile was terminated to avoid wasting memory. It is not evidence.
- The inherited top-level `KomorebiPhysics` target cannot import the non-module Block 44 source from a `module` root. The monolithic target therefore fails at the inherited module/non-module boundary. Block 45 is classified by modular cumulative verification, as Block 44 was.
- The proof uses a compact-ball Lipschitz constant for the exponential. It does not claim the sharper constant-one Duhamel estimate.
