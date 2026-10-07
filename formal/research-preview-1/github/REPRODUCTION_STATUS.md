# Launch proof-reproduction checkpoint

The mathematical release remains Research Preview 1 RC1, frozen at Block 34.
This launch-preparation revision changes release tooling and documentation, not
mathematical statements, proof source, dependency pins, or the Future Research section.

## Fresh proof execution completed

On 21 September 2026 the prepared release's own `tools/replay_lean.py --clean`
completed against a restored, checksum-verified Lean 4.34.0-rc2 toolchain and its
retained dependency cache. The script deleted the project-local build directory
before compiling all 92 production modules. Lake completed 2,618 jobs.

All 22 recorded commands passed their expected checks: tool versions, nine locked
dependency revisions, build, positive control, concrete and universal examples,
two axiom inventories, and five intentionally rejected controls. The audit covered
1,120 declared theorems and 2,510 project-owned theorem constants, including
generated constants. Nineteen declared theorems are axiom-free. The only observed
axioms were `propext`, `Quot.sound`, and `Classical.choice`.

The 108 execution-input files had identical before/after hashes. All nine dependency
checkouts had the expected revision and clean tracked source worktrees. Cached
compiled dependencies were retained, not independently rebuilt. This is an actual
fresh project proof replay, not a reinterpretation of historical Block 34 logs.

The compact record is [LOCAL_PROOF_REPLAY.json](LOCAL_PROOF_REPLAY.json).
The companion **Komorebi_Launch_Proof_Replay_Evidence.zip** contains the full fresh
receipt and command logs under `proof_replay/`. It does not contain toolchain
binaries, cached dependency objects, or private research archives.

After extracting the evidence archive, validate it against this checkout with:

```bash
python -B tools/check_proof_receipt.py /path/to/evidence/proof_replay
```

On Windows the path may be a quoted local Windows path. This command checks the
recorded evidence and source identity without executing Lean. It rejects incomplete
commands, stale source hashes, modified logs, missing axiom coverage, timeouts,
and incorrect negative-control diagnostics. It does not cryptographically attest
that an external party ran the commands.

## What this does not establish

The exact runtime was recovered from previously retained archives. Direct network
retrieval in the current container still fails at DNS resolution. Therefore a
fresh **public dependency bootstrap and GitHub-hosted run remain pending**. The
public pinned mathlib toolchain file was checked and agrees with the declared Lean
version; reading that file is not a bootstrap execution.

The GitHub connector again returned 404 for the proposed private destination.
That can indicate insufficient permissions, not absence. Local upload preflight
stopped because GitHub CLI was unavailable, before any remote operation. No remote
was created or pushed by this block, and no publication or license was selected.

## Hosted gate improvements

The manual Lean workflow now validates the full proof receipt against the checkout.
It also records minimal workflow context after bootstrap or replay failure, so the
uploaded evidence can show which step failed or was skipped. A context-only record
always declares `proof_verified: false`; it cannot substitute for a successful
`REPLAY.json`, its checked logs, and the recorded input hashes.

Only allowlisted nonsecret run metadata is recorded. Workflows retain read-only
permissions, fixed action references, and no automatic publication. The changed
workflow has been inspected and its helper scripts tested locally, but it has not
run on GitHub.

## Remaining launch gates

The remaining work is the private upload, first hosted artifact/reference checks,
the pinned public proof run, owner review of rights and public files, and explicit
publication approval. No additional mathematical block is required for this scope.
