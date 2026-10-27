# Verification scope

87/87 complete proposition mappings, 0 partial and 0 unformalized.

The cumulative verification contract is a clean warnings-as-errors compilation of every mathematical module, an audit of every explicitly named declaration, individual kernel replay through the pinned Lean checker, and rejection of each invalid control for a mathematical diagnostic. A control must return the ordinary compiler diagnostic exit code 1 with exactly one intended mathematical diagnostic. Missing imports, unknown identifiers, qualified instance-synthesis failures, unrelated linter or helper errors, and resource failures do not count as successful rejection. The classifier is tested against the three actual superseded mixed diagnostics and their clean repaired receipts.

Only `propext`, `Classical.choice` and `Quot.sound` are permitted axiom dependencies. An axiom-free declaration is also accepted. Missing, extra, duplicate, truncated or unapproved axiom records fail the audit. Source inspection also rejects placeholders, added axioms and unchecked proof bypasses in active mathematical source.

The counts are 254 proof modules, 4454 explicitly named declarations, 2887 named theorems and 183 rejection controls. These are inventory counts, not measures of novelty or proof difficulty.

Raw correspondence reviews are retained in `verification/current_scope/`. They are internal same-team checks and are not represented as external independent review. They compare actual theorem hypotheses and conclusions with the frozen manuscript statements. Kernel checking validates the encoded claims; source correspondence establishes which manuscript statements those claims cover.

A source checkpoint and an execution receipt are separate records. The current cumulative report is `verification/current/report.json`. A successful mathematical scope review does not by itself certify compilation.

All 155 inherited mathematical source files remain byte for byte identical to the checked parent. Of its 137 inherited rejection controls, 134 remain byte for byte identical and 3 have documented test repairs removing unrelated elaboration or linter errors. Their false assertions are retained. Exact original and repaired control bytes, reasons and clean intended-rejection receipts are preserved in `history/control_repairs/` and bound by `SOURCE_LINEAGE.json`. The preserved predecessor source snapshot retains the identity chain. Historical receipts remain historical and do not substitute for current execution.

## Accepted execution

The delivered execution is PASS: all 254 mathematical modules compile with warnings treated as errors and pass individual kernel replay. The complete root import, exact rational examples, all 4,454 named-declaration axiom checks and all 183 isolated rejection controls pass. The only permitted logical axioms are propext, Classical.choice and Quot.sound.
