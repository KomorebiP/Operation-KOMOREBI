# Development failures and repairs

## Mathematical corrections

The earlier suggestion that positive residual depth by itself indicates stronger axioms was too strong. For fixed data, allowing additional witness depths weakens the assertion. This is now explicit in ResidualAudit.lean.

The earlier claim that an R^1 obstruction could repair finite-support reflection was not justified. The integer tower supplies a specific counterexample: every finite-prefix cokernel vanishes while the global cokernel class is nonzero. The original broad admissible-class schema was underspecified, so this is a refutation of its natural finite-prefix instance, not a claimed refutation of every possible corrected schema.

The predecessor's fixed-system flattenability property does not exclude a different representation. The degreePacked construction makes this limitation exact.

## Environment and implementation failures

1. The fresh container initially had only the seven archived runtime parts, not an extracted Lean executable. Restoration completed and the concatenated compressed archive matched SHA-256 66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34.
2. The Python zstandard module was unavailable. The installed zstd executable was used instead.
3. A streaming container session was unavailable. Restoration and verification were run as ordinary processes and their completed exit status and logs were inspected within this interaction.
4. The first ResidualAudit attempt had a universe mismatch in the small counterexample. Its existential binder was explicitly fixed to universe zero. No mathematical hypothesis changed.
5. A quotient-lemma field-notation invocation failed. Rewriting by the lemma, followed by the surjectivity witness, compiled.
6. Warnings-as-errors rejected a letI style choice. An ordinary typed let declaration fixed the warning without suppressing the linter.
7. The verifier initially reported a failed negative control even though Lean rejected the false proof correctly. The checker searched for lowercase 'type mismatch' while Lean emitted 'Type mismatch'. Matching was made case insensitive. The original failed verifier report and original compiler rejection are retained under verification/development_first_*. The final verifier was rerun from a clean project build.

None of these repairs introduced a custom axiom, a proof placeholder, a native-decide shortcut, or a suppressed mathematical proof obligation.
