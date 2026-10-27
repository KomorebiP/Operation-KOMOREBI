# Polynomial controls development

The first development compilation failed before the final source was frozen.
The terminal diagnostics showed underconstrained pointwise subtraction from an
anonymous zero function, overly broad `simp` unfolding evaluation at zero into
`constantCoeff`, and redundant `ring`/simp arguments rejected by the warnings
gate. These were elaboration and tactic issues, not failed counterexamples.
That first terminal output was not redirected to a file; this paragraph records
its substance rather than claiming a preserved raw log.

The corrected second development compilation passed; its raw output is
`controls_02.log` (empty because the successful file emits no diagnostics).
The final fresh replay recompiles the frozen source and its three deliberately
invalid proofs, preserving each output and exit status independently.

The positive theorems establish the mathematical counterexamples. The negative
files check that Lean rejects attempts to use a negation, or two separate lift
proofs, as a proof of the corresponding false stronger statement.
