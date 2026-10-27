# Failure log

No failed draft or interrupted process is counted as a successful theorem check.

1. An attempted interactive container session was rejected because streaming
   sessions are unavailable. No Lean process ran in that attempted invocation.
   Runtime restoration then succeeded through ordinary bounded calls.
2. A grouped dependency-rebuild invocation hit the outer tool time limit while
   processing FDGaussianTransport. Its log lacks a completion receipt. The
   module passed when rerun alone. Its final output hash comes only from the
   successful independent invocation.
3. The unchanged 1,997-line monolithic perturbation source reached a 25-second
   process cap. The required proof-body slices were extracted reproducibly into
   nine smaller modules and all nine compiled. The original full source is
   retained unchanged under PREDECESSOR, but its timed-out compilation is not
   relabeled as a pass. Unneeded continuous-time proof blocks were not rebuilt.
4. The first matrix/operator compatibility draft had unused section-variable
   linter errors. The final version explicitly omits those unnecessary instances.
5. The first centered-covariance Gaussian proof used an extensionality tactic
   that descended to scalar coordinates before a vector uniqueness theorem.
   It was replaced with explicit continuous-linear-map extensionality.
6. A subsequent centered-covariance draft contained a proof step after the goal
   was already solved and an unused simplifier argument. Both were removed.

The saved audit directories retain those attempted source snapshots and compiler
logs. The final 38 modules each have a successful final-source receipt. Two
separate negative controls deliberately submit a false equality and a placeholder
proof; their rejection is expected and recorded, not a release failure.

The Mathbox skill's validator executable is not installed in the working
filesystem. The manifest follows its retrieved version-1 template; the project
integrity verifier checks its output hashes together with the actual per-process
receipts. No claim of running that unavailable official validator is made.
