# Attempts and corrections

All final production statements compile. The following development failures occurred and are not counted as passes.

1. An interactive container session was unavailable. Ordinary noninteractive execution was used instead.
2. The initial file used a deprecated Real import and omitted the `noncomputable` declaration required for real division. The import and elaboration setting were corrected.
3. `Mathlib.Tactic.Omega` was not an available module. The stored compiler's `Lean.Elab.Tactic.Omega` import was used.
4. Warnings-as-errors caught an unused simplifier argument and a deprecated multiplication lemma. The argument was removed and the inequality proved from constituent lemmas.
5. A newly drafted worked-example constant was mistyped as 189/3125000. Lean rejected it. Exact rational calculation and the final kernel proof give 189/7812500. This was a new fixture error, not a correction to a number printed in the source monograph. The incorrect value is retained as a negative control.
6. A `leanchecker --help` attempt first failed because Lean was not on the subprocess PATH. A second help attempt reached the tool execution limit because the executable does not implement that help mode and selected a default target. After inspecting the stored tool source, the explicit `leanchecker --verbose CoupledFormal` invocation passed. The successful replay is restricted to that module, not all imported Mathlib.

The theorem hypotheses were not deleted to obtain compilation. The full analytic claims were not promoted. Final machine-readable stage receipts, rather than these development attempts, define the checked scope.

7. The first new archive candidate was structurally valid, but strict validation rejected the build script's `SHA256SUMS.txt` name because the inherited verifier expects `SHA256SUMS`. The archive was not delivered. The next candidate exposed a checksum-list ordering difference between path-component order and full-string order. Both the filename and ordering were corrected. Each rejected candidate was withheld and replaced before final extraction and strict validation.
