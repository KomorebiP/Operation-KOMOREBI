# Development notes — v0.9.0

The prior v0.8.0 source package was reproduced with its unmodified verifier before
extension: 584 theorem declarations, 705 named axiom audits, and all 47 project
modules replayed using the same pinned kernel. Logs are preserved separately.
The portable chunk archive was restored and its combined SHA256 checked.

Block-09 drafts initially failed on quotient coercion/API rewrites, inner-product
instance elaboration, dependent projection arguments, and warning-fatal unused
section hypotheses. An attempted definition returning a Prop-valued projection
instance was replaced by a theorem, without changing the claim. Deprecated
`push_neg` use was corrected to the supported `push Not`. A cumbersome zero-map
example was replaced with the actual scalar quotient-by-zero examples. Failed
probes and compiler diagnostics remain in verification/development_v0.9.0.

An optional external source fetch failed due to container DNS. The pinned local
Mathlib source and compiled APIs were available and used; no unverified external
claim supplies a proof hypothesis. No warning suppression or placeholder was used
in production. New proof sources compiled individually before cumulative replay.

The old v0.8.0 package carried stale lakefile.toml version 0.7.0. This release
corrects that packaging metadata to 0.9.0. Dependency pins and all 47 predecessor
proof sources are unchanged. Execution-input changes are recorded in the verifier.

The exact rational check distinguishes ambient Gram geometry from a naive
orthonormal coefficient convention. In the supplied example these give squared
values 16 and 4 respectively. This is an intended diagnostic, not a test failure.

Final current verification status, any remaining failures, and both source replay
paths are recorded in VERIFICATION_SUMMARY.md and their report.json files.


## v0.10.0 — regularized reconstruction

The actual bounded coercive normal operator was constructed through the pinned
Mathlib Lax–Milgram theorem, not supplied as an assumed inverse. All seven new
modules compile warning-free. Draft symmetry/API/projection/unused-hypothesis and
tactic errors were corrected with logs in verification/development_v0.10.0.
A supplementary signature-display command timed out at the outer 20-second limit;
its monitored 180-second-limit rerun passed. Both complete production replays passed,
including 60 same-kernel module replays, 863 axiom audits, ten rational suites and
the example CLI. All 53 predecessor proof files remain byte-identical.
