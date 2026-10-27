# Artifact consistency gate

`release_gate.py` requires the exact current artifact, not just a successful
historical test log. It checks:

1. Strict manifest and checksum coverage, rejecting unlisted files and symlinks.
2. Historical proof-snapshot identity for all four retained proof baselines.
3. Fresh formal PASS, all check flags, all 51 module sources, the exact 526-name
   axiom inventory, and unique compilation/replay command labels.
4. Exact wheel runtime-source inventory and bytes, project/version metadata,
   and agreement with the wheel used in installed acceptance.
5. Test receipt binding for the current Python source, scripts, tests and build
   metadata. Changing a source after testing invalidates the receipt.
6. The actual LaTeX/PDF hashes in a successful build receipt.
7. The explicit still-unselected publication decision.

Tests include stale source, stale wheel, wrong metadata, duplicate entries,
missing proof coverage, forbidden axioms, omitted replays, altered snapshots,
and regenerated manifests that cannot conceal stale test evidence.

These are finite consistency checks over artifacts and receipts. They do not
prove the truth of arbitrary supplied receipts. Replacing all evidence and code
is outside the authenticity guarantees of unsigned hashes. Kernel replay,
external-input semantic fidelity and public licensing remain distinct matters.

A failed check returns `technical_status: FAIL`; the artifact should not be
represented as the tested release. Technical PASS with pending licenses does
not authorize publication. The current script deliberately refuses to silently
interpret newly supplied permission metadata; an explicit publication review
must accompany that change.
