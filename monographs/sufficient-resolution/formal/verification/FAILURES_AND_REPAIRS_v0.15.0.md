# Failures and repairs — v0.15.0

1. **Missing project build objects.** The source-only v0.14 archive intentionally omitted
   `.lake` project objects, so the first attempted extension import could not resolve
   inherited Komorebi modules. The v0.14 dependency closure was rebuilt serially under
   the pinned runtime. That predecessor run passed before final block-15 verification.

2. **Near-accepted convergence proof.** An early draft tried to apply an exact accepted
   norm-domination theorem directly to an inexact source. This was invalid because only
   `||x-y||≤kappa` was available. The final proof selects exact accepted companions,
   proves their convergence, proves `x-y→0`, and combines the limits.

3. **Verifier generation.** The first generated block-15 verifier retained several
   block-14 import/root labels and one indentation defect. It was corrected before any
   final verification claim. The final verifier is syntax-checked and the two production
   runs both pass.

4. **Source-only launch transport timeout.** The container call that launched the
   independent source-only replay timed out at the transport layer while the background
   verifier continued. The process was monitored to completion; its final report records
   a successful run. This was not a Lean command timeout.

No production theorem hypothesis was weakened to resolve these issues. Warnings remain
fatal in the final compilation commands. No production `sorry`, `admit`, or custom axiom
was introduced.
