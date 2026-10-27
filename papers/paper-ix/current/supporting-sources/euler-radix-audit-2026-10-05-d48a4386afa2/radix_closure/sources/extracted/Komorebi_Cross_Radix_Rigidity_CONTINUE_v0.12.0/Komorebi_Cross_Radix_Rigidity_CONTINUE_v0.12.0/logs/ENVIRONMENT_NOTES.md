# Environment / proof-engineering incidents retained for v0.5.0

1. **Full portable verifier timeout.** The full `run.sh verify` invocation began successfully and passed Lean, Lake, pinned dependency checks, and its core arithmetic proof before the execution tool ceiling was reached. This incomplete verifier run is not used as certification.
2. **Initial module-path failure.** The default portable `PortableCheck` Lake target did not import copied Cross-Radix modules merely by filename. The source was not changed; the compile setup was repaired to use an explicit project/module path.
3. **First clean-root containment failure.** Lake rejected `/mnt/data/cross_radix_v050_clean/src/...` when invoked from a different Lake workspace because inputs must lie under its root. The clean audit directory was therefore made its own Lake root, reusing only the pinned package cache.
4. **Batch execution ceilings.** Two clean batch invocations reached the tool's wall-clock ceiling while beginning `CrossRadixFiniteLCMIntersection` and `CrossRadixDFTShellAgreement`. There was no Lean diagnostic from those interrupted batches. Each module was then run individually under the same strict pinned environment and passed.

These are environment/proof-engineering incidents, not mathematical counterexamples. Only the saved successful strict logs certify the final sources.
