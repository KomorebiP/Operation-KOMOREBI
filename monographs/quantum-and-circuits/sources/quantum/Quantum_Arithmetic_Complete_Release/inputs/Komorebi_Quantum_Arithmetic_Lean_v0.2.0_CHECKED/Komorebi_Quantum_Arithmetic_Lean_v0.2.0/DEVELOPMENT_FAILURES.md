# Development failures and repairs

## Runtime recovery

The initial container contained no Lean or Lake executable. A direct download
attempt failed at DNS resolution. The existing five part compact portable runtime
was located in the user's Library, materialized, joined, and extracted instead.
The compiler was then actually executed and reported Lean 4.34.0-rc2.

## Broad import attempt

The first attempt to compile the original `import Mathlib` draft drove memory to
the container's 4 GiB limit. That attempt was stopped without a proof result.
The active source uses module mode and focused imports. No original statement or
numerical table was changed. The focused native draft first compiled successfully.
It was then strengthened by replacing every native decision proof with direct
kernel reduction, and that version compiled successfully too.

## Semantic extensions

The added complex interpretation initially triggered two unnecessary sequencing
linter errors. A later pass exposed missing composition unfolding and vector
access rewrites. These were corrected with explicit existing lemmas.

The first unitary proof attempt expanded a finite list sum too early and lacked
the field big-operator import. The next attempt still needed an explicit rational
zero cast. The final proofs repair these elaboration issues without changing the
claims. The character orthogonality certificate passed throughout these attempts.

## Negative control design

An initial standalone false-energy test failed because imported implementation
definitions did not reduce in that module context. This was inconclusive as a
mathematical negative control and is not counted in the release verification.
The delivered runner instead pairs fresh source mutations with positive proofs
of their negations. Some failed decision tactics still report opaque reduction
internals, so an error message alone is not treated as evidence of falsity. All
four negations are proved with ordinary lemmas and audited before the mutated
source compilations are required to fail. The unmodified source must also pass.

## Record

Intermediate logs and source snapshots are kept for inspection. Failed historical
sources are not imported by the active modules or included in the active audit.
Final status is taken only from `verification/final_run/VERIFICATION.json`.
