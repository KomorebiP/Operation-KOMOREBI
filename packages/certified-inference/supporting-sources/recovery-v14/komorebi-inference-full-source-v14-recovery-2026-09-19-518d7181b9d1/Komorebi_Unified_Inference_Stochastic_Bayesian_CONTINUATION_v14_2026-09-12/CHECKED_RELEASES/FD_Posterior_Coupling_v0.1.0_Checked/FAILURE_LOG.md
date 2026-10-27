# Development failures and verification scope

Failed drafts are retained under audit with their exact attempted source, compiler
output, source/dependency hashes and nonzero process receipts. They are not counted
as checked. There were 15 completed failed Lean draft checks in this block, followed
by successful final-source checks for every active module.

The failures were grouped by mechanism:

1. The initial request for a streaming container session was rejected because that
   feature is unavailable. No Lean process ran in that attempted call. The portable
   runtime was restored using supported bounded execution, and its restoration log
   records completion. This was an execution-interface failure, not a theorem failure.
2. The first generic transport draft omitted the ENNReal notation scope and adequate
   product measurability assumptions. The final version uses explicit Borel and
   second-countable hypotheses where required. Euclidean applications satisfy them.
3. Gaussian quadratic integration used the wrong argument shape for a coordinate
   projection integral lemma. The final application specifies the real scalar field
   and uses the library's actual argument order.
4. The affine coupling draft needed the sampler definition unfolded and a fully
   qualified subtraction-application lemma. These were elaboration issues.
5. The square-root tolerance helper used an incorrect exponent argument/cast in its
   first two drafts. The final proof uses ENNReal's power/rpow lemmas with explicit
   natural-number and real-number casts.
6. Matrix energy calculations required the matrix diagonal definition and the actual
   Euclidean inner-product/dot-product convention. Both were made explicit.
7. Several successful mathematical proofs initially triggered warning-as-error checks
   for unused section instances, unused hypotheses or a redundant tactic. Those
   assumptions/steps were removed rather than suppressing the linters.
8. A latent coordinate type was initially named with the reserved lambda token. It was
   renamed to a permitted identifier. The subsequent unused-instance warnings were
   also fixed before the factor-model module was counted as checked.

No completed Lean process in this block returned the timeout code. Earlier project
versions have their own recorded timeout histories; those are not conflated with
this block. Per-module execution remained bounded. There were no mathematical
counterexamples to the final statements during these checks.

Two deliberate negative controls submit a false natural-number equality and a
placeholder proof; both are rejected by the actual pinned compiler. Their expected
failures are stored under checks/negative, outside the active source namespace.

The official Mathbox manifest-validation executable was not found in the available
skill filesystem. The retained version-1 manifest template was used, and this
release's own verifier checks its artifact hashes and substantive evidence fields.
No claim of running the unavailable official validator is made.

Only the 16 retained modules actually imported by the new coupling chain were rebuilt.
The complete older multiscale moment-bridge and continuous-time program remain
preserved in the full continuation rather than being falsely described as recompiled.
