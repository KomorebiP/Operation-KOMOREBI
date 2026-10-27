# Development failures — v0.8

1. The runtime parts were recovered from the retained Library files. A preliminary
zstandard import was unavailable. Archive inspection showed XZ, and the completed
restore used Python's standard lzma module. No mathematics depended on that import.

2. An interactive streaming execution request returned StreamingExecNotEnabledContainerError
before the requested script executed. The script was then created using the ordinary
container interface, run and polled during this interaction. The restore completed.
Runtime checks and part hashes are retained; compiler/cache payloads are not bundled.

3. One enclosing dependency-bootstrap call was interrupted before a complete run
receipt. No process remained running. The remaining dependencies were rebuilt and
all selected modules later passed the separate empty-build cold audit. This partial
bootstrap is not counted as successful full verification.

4. 7 recorded draft Lean checks returned nonzero before correction.
They concerned Euclidean recursion/termination elaboration, gcd/cast/order APIs,
absolute-value syntax and rewriting, and a queried missing API name. Per-attempt
source hashes and diagnostics are retained in v08_evidence/development and indexed
in DEVELOPMENT_ATTEMPTS.json. The final proofs contain no placeholder or extra axiom.

5. The final 82-task cold audit and the new Python audit both completed successfully.
The negative-control failures in that audit are intentional mathematical rejection
tests, not failed accepted theorems. No final mathematical task timeout was relabeled
as success. Any subsequent packaging failure must be separately recorded.

6. The first fresh-extraction selected Lean recheck was interrupted by its enclosing
60-second execution call after all nine selected modules compiled, before the seven
controls completed. No process remained running. The nine completed outputs are
retained in v08_evidence/extracted_attempt1, but that attempt is NOT a complete
replay. A fresh retry is reported separately in the external extraction report.
