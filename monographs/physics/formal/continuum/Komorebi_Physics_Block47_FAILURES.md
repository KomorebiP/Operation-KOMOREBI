# Block 47 Failure Ledger

1. **Parent closure rebuilds timed out repeatedly.** Resumed unchanged builds eventually completed the 3,059-job Block 47 import closure. Earlier timeouts are inconclusive and excluded.
2. **First negative control was ambiguous.** Opening two namespaces made `HilbertSpinor` ambiguous. The control was rewritten with the fully qualified type and rerun; it then failed only at the intended `False` goal.
3. **All-in-one fresh verifier timed out.** Its completed warning-as-error gate was retained. The module build, API, axiom audit, and each negative control were rerun as isolated commands to terminal results.
4. **Default root build failed at 3,943/3,944 jobs.** The root `module` cannot import the inherited non-`module` Block 44 source. This packaging failure is recorded and excluded from the checked modular classification.
5. **No unbounded-operator shortcut was used.** The block transports already checked bounded unitary propagators through Fourier equivalence; it does not identify them with an unproved unbounded functional calculus.
