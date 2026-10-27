# Replay evidence scope

The release verifier stages all source inputs under one fresh root, removes old local object files, and recompiles 10 unchanged direct dependency modules plus 11 new modules. AxiomAudit.lean prints the dependencies of every one of the 72 named new constants. All 22 compiler invocations returned zero.

The pinned Mathlib object cache is reused. It is not a full Mathlib rebuild or an independent kernel. Development attempts are not substituted for this fresh replay.

Compiled .olean files and duplicate staging sources are deliberately omitted from the deliverable ZIP. Source files, raw logs, object/source hashes, commands, exact parent archive, and a runnable verifier are retained. Running verify.py recreates the objects and rewrites RESULT.json plus verification/fresh. verification/release_result.json is the immutable original release report. Check SHA256SUMS.txt on the pristine extracted payload before replaying.
