# Development record

The original v0.1.0 archive remains an unverified historical draft. It used a
broad Mathlib import and native evaluation. This release uses targeted imports
and kernel reduction for its finite certificates.

The shell download attempt failed because network name resolution was blocked.
The complete portable installation was instead restored from the five user
Library parts. Assembly checked the part hashes and the combined archive hash.
The compiler then ran successfully.

The first build command used the unsupported spelling `-wfail`. It was corrected
to `--wfail`. The corresponding failed log is retained.

The first complex interpretation attempt failed because an implicit complex
extensionality tactic was unavailable and some casts and finite sums did not
simplify in the needed direction. Explicit complex extensionality and controlled
rewrites repaired those proofs. A redundant tactic warning then failed the
warnings as errors build and was removed.

The Fourier convention proof first failed on real to complex casts inside
trigonometric expressions and on square root constants. Explicit cast identities
and square root lemmas repaired the proof.

Two final finite lookup lemmas initially contained free variables at the point
of kernel decision. Reverting those variables through `decide +kernel +revert`
repaired the elaboration. The entire final source was subsequently rebuilt and
replayed from a clean project.

An early long build exceeded the tool response window but its process continued.
The later complete source build and replay logs, not that partial response, are
the verification evidence. No timeout has been counted as a successful proof.

The exploratory `Probe.lean` contains failed name checks and is retained only
under development. The original draft, failed logs, and probe are excluded from
the final active module list and theorem count.
