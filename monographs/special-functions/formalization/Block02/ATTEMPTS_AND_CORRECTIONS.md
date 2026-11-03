# Execution corrections retained for SF-LEAN-B02

The mathematical route is the local uniform-convergence route described in
`TARGET.md`. It proves the full local target. The sparse-power-series and
direct derivative-majorant alternatives were deferred after that success;
no mathematical obstruction or impossibility is inferred for those routes.

Preflight runs 001–003 stopped at source-map identity checks because the
Windows checkout had converted LF bytes to CRLF. Their receipts are preserved
in `evidence/preflight00*.json`. The canonical Git bytes were restored, and
`.gitattributes` now preserves exact bytes for the Special Functions tree.
These were source-identity failures before mathematical checking.

Full run 004 passed both compilations, both exact axiom audits, both kernel
replays, and the three mathematical rejection controls. Lean also rejected the
placeholder as required, but the verifier expected single quotation marks
around `sorry`; Lean's diagnostic used backticks. That run is retained with
its failed classification and exact old control manifest in
`evidence/attempt004/`. Its failure has not been overwritten as a pass.

The diagnostic expectation was corrected. A complete fresh replay in run 005
then passed all 20 steps, including all four rejection controls. Its receipt
and logs are the current files directly under `evidence/`. The production
Lean source was unchanged between those two complete runs.

The final public proof has no placeholder or custom axioms. The deliberately
invalid placeholder remains isolated in `lean/analytic_controls/` and is
required to fail with warnings treated as errors.
