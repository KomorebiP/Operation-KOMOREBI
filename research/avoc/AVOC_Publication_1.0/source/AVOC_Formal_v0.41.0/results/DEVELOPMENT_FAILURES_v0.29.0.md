# Development failures — v0.29.0

1. The container interactive-session API returned StreamingExecNotEnabledContainerError while starting runtime restoration. No successful restoration was claimed from it. The documented assembler was then run as a local subprocess and polled to completion. All seven part checks and the combined archive SHA passed; extraction completed.
2. The first generic factorization module had an unused Field section variable in a cost-only theorem. Warnings-as-errors rejected it. The variable was explicitly omitted; the final module compiled.
3. The first GF(5) checker build lacked the Field instance and then its Fact (Nat.Prime 5) prerequisite. The field module and ordinary `by decide` primality instance were added. Early downstream missing-import failures were setup failures, not negative proof evidence.
4. Examples initially resolved an ambiguous `check_iff` to the parent affine checker and over-simplified the amortization expression. Names were qualified and explicit equality rewrites replaced the failed definitional-equality attempt. The final examples all kernel-check.
5. A first demo invocation during the clean build correctly refused missing/stale outputs; it was rerun after all targets finished.
6. The first mutation fixture assumed every change to U or V invalidates U A V=I. That is false: nullspace changes can leave a valid certificate. The checker correctly accepted such a case. The independent oracle was repaired to classify mutations by the actual polynomial identities, retaining the valid alternatives. The entire final regression passed after this repair. This was a test-assumption failure, not checker unsoundness.

Failed compiler and regression logs are retained under results/v0.29.0/development/. No unfinished proof, placeholder or native-evaluation axiom was accepted. The final local rebuild, full axiom audit and complete negative suite succeeded. The old live-store and crash suites were not rerun.
