# Verification summary — Sufficient Resolution v0.11.0

**New block passed. Verification is block-scoped.**

## Actual completed validation

| Check | Result |
|---|---|
| Five new production modules, fresh serial compilation, warnings as errors | PASS |
| New block import root | PASS |
| Transitive axiom audit | All 38 new named declarations passed |
| Same-kernel `leanchecker` replay | All five new modules passed |
| Necessary inherited project objects reused | 13, with source/object hashes recorded |
| Inherited proof sources preserved | All 60 byte-identical |
| Executed source/script/configuration inputs unchanged | 42 of 42 |
| Principal signatures printed | Eight actual contracts |
| Deliberate false proof and placeholder | Rejected |
| Deliberate custom axiom | Compiled intentionally, then detected by allowlist |
| New exact rational controls | 920 assertions across 100 parameterized systems and 100 vectors |
| Corrupted recovery certificates | 64 rejected |
| Full fresh inherited/cumulative replay | NOT COMPLETED |
| Independently extracted second proof replay | NOT RUN |

## Counts and historical boundary

The cumulative source inventory is 764 theorem/lemma declarations in 65 modules,
with 901 explicitly named declarations. The new block contributes 36 theorems and
38 named declarations in five modules. The remaining 728 theorems/60 modules retain
their historical verification evidence from v0.10.0; this release does not present
those historical passes as fresh results. All 60 inherited production files are
byte-for-byte identical. Helpers and classical specializations are included in counts.
The Papers I–XII census is unchanged.

## Runtime and provenance

Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. All nine dependency HEADs match
the retained manifest. The restored compact runtime SHA256 matched
f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7.

The final command is `scripts/verify_block11.py --reuse-project-dependencies` with
the pinned runtime and output folder `verification/release_v0.11.0`. The five new
modules and block root are rebuilt. Thirteen necessary inherited objects, compiled
during this turn with logs in development_v0.11.0, are reused and identified by both
source and object hash. Pinned imported Mathlib objects are reused, not rebuilt.
The new axiom audit is transitive, and allows only propext, Classical.choice and
Quot.sound. `leanchecker` uses Lean's SAME kernel, not an independent implementation.

Each final Lean command is serial, one-threaded, with a 240-second wall limit. The
container has a 4 GiB cgroup memory allowance and a four-CPU quota. Native Windows
execution is not claimed. Runtime/object caches are not included in the archive.

`computation-manifest.json` uses the retained project-local VERSION-1 format with
supplementary before/after input hashes, not an upstream mathbox version-2 certification.

## Failures and repairs

Concurrent imports initially exceeded practical memory capacity and stalled. The
fresh predecessor rerun was interrupted, so it has no complete fresh audit/replay
result. Serial targeted verification replaced that attempt. The outer launch of the
final verifier returned a transport timeout while the process continued; its actual
process was monitored, not duplicated. Details and partial logs are retained.

Draft coercion, filter-constant, unused-hypothesis, deprecated-API, pointwise-division
and dependent-projection errors were corrected without disabling warnings. One finite
control initially passed redundant columns to a helper requiring an independent basis;
it was corrected to use the actual range projector A A-dagger. No outstanding new-block
compilation, axiom-audit, or kernel-replay failure remains. The full fresh cumulative
replay remains uncompleted and is not a claimed pass. An initial archive filename
truncated the final .0 of the version; the filename construction was corrected and
the final archive integrity checks rerun. No proof input changed.

## Finite computational range

`check_regularization_limits.py` uses fractions.Fraction, seed 20260913, source/target
dimensions 0 through 4, and lambda=1/k^2 for k in 1,2,4,8. It checks the exact dual
identity, source-filter contraction, finite closed-range bound, kernel-error identity,
noise and solver inequalities, and corrupted responses. Additional finite diagonal
sections illustrate fixed-vector versus moving-vector errors. They are NOT a proof
about an infinite diagonal operator. Python and its shared rational helpers are not
formally verified or extracted from Lean. No numerical limit is promoted to a theorem.

## Evidence

- verification/release_v0.11.0/report.json: commands, statuses, times, input hashes.
- verification/release_v0.11.0/axioms.json: all 38 transitive audits.
- verification/PRINCIPAL_SIGNATURES_v0.11.0.log: actual assumptions and conclusions.
- verification/CONTRACT_REVIEW_v0.11.0.md: interpretation boundaries.
- verification/PREDECESSOR_PRESERVATION_v0.11.0.json: 60 unchanged sources.
- verification/incomplete_predecessor_v0.10.0: incomplete attempted run, not a pass.
- verification/FAILURES_AND_REPAIRS_v0.11.0.md: resource and draft failures.

Archive CRC/member hashes establish byte integrity, not theorem truth or a second
proof replay. The final source-only archive includes the cumulative source and
historical evidence but excludes `.lake` caches.
