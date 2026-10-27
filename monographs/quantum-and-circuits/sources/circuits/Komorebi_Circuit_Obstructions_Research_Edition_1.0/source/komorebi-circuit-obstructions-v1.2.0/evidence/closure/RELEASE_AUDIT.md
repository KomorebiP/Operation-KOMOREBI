# Release audit: 1.0.0

Date: 2026-09-21. Status: **local release acceptance criteria passed**.

## Scope closed

The maintained artifact is **Komorebi Circuit Obstructions: Restoration, Discrepancy Covers, and Projection Limits**. Version 1.0.0 accepts the eight claims C01–C08 with their exact conventions and limits. It is not a resolution of P versus NP. No further conjecture, formalization project, or exploratory route is a release blocker.

The source baseline is the Complete Packets and Projection checkpoint. Its SHA-256 is `3401b64e0f2d7ef33440f54dd48f7fb458dc581e3af8af0683d4de2394e62600`. Ten original ZIP checkpoints are retained byte-for-byte; archive inclusion does not promote all historical statements to maintained claims. This closure adds documentation and operational hardening, not a new mathematical discovery.

## Executed checks

| Check | Actual outcome |
|---|---|
| Baseline preservation | All 92 sealed source files verified and unchanged |
| Original runner replay | Completed, including its documented predecessor replay; all seven immediate scientific outputs matched |
| Maintained quick suite | All 17 unittest methods passed, including the 276 small-function controls, distinct-wire gate legality, both output values, failure guards, and local documentation links |
| Maintained full suite | C++ profiles rebuilt for one through four inputs; all seven scientific files matched the frozen baseline |
| History mode in the new runner | Full pinned source runner completed; all seven output comparisons passed |
| Fresh extraction | `git archive` source snapshot, without Git metadata or prior build outputs, passed the full active runner |
| Source immutability | All 52 run input records have matching before/after hashes, including the source seal itself |
| Manifest validation | Version-2 record validated, including relocated retained output hashes |
| Metadata | All 10 Python source files parsed; workflow YAML and selected citation fields checked |

The principal scientific input commit was `6c82cdc4ae5877e148783099752544c067efc09e`, with a clean Git working tree at the recorded all-mode run. The later release commit adds this evidence and its seal without changing those scientific inputs. The evidence manifest explicitly records its actual executed command, working directories, software versions, resource limits, and input hashes.

The release source contains 51 sealed input files. Source and closure evidence have separate seals so a historical result record is not confused with an execution input. Seals are checksums, not signatures or proof certificates.

## Finite range and proof status

The full profile computation covers all 65,536 four-input Boolean functions. The independent rank/evaluation method checks the declared 765 cases, not all of that domain. Small restored constructions cover all 276 functions on one, two, or three inputs, with 4,240 scalar input/target evaluations and 2,344 cut checks. Optimality is based on matching written bounds and explicit constructions, not exhaustive reversible-circuit search.

Projection checks include 693,965 pair coefficients and nine exact ranks through 1,022 inputs. Full truth-table evaluation is only at the three declared smaller parameter values. Weighted-fingerprint checks include 1,052,736 polynomial/field-point evaluations and 20,544 independent coefficient extractions. The JSON evidence records the exact domains and exclusions.

All mathematical arithmetic is exact Boolean, integer, or finite-field arithmetic. Runtimes are not presented as a performance benchmark. The actual environment was Python 3.13.5 and g++ 14.2.0 on Linux x86_64. Fresh extraction used the same environment. The Windows and alternate-Python CI matrix is configured, not locally or remotely certified by this run.

Proofs are written and self-reviewed. No Lean kernel check, independent mathematical review, global novelty audit, best-known-bound assertion, or conjecture solution is claimed. A passing finite check does not replace a general proof.

## Retained evidence

- [Original source replay](source_replay.json), with [raw log](source_replay.log).
- [All-mode manifest](release_run/manifest.json), retaining exact result files and logs.
- [Manifest validation log](manifest_validation.log).
- [Fresh extraction record](fresh_source.json), with [raw log](fresh_source.log).
- [Metadata checks](metadata_checks.json).

The all-mode summary counts eight result comparisons: seven active scientific files plus the historical comparison record. That is not a claim of eight distinct mathematical suites. The historical record itself contains the seven source-output equality checks.

Retained output files were copied from their ignored build directory into `evidence/closure/release_run/`. Only manifest output-location fields were relocated. Executed argv, cwd, commit, timestamps, and all content hashes remain the original provenance. The relocation is declared in that manifest; the original absolute build paths are historical metadata, not files needed for reproduction.

To validate the retained record from this repository:

```sh
python scripts/validate_manifest.py evidence/closure/release_run/manifest.json --root .
python scripts/check_integrity.py
```

## Failures and repairs during closure

No scientific assertion or baseline comparison failed during this closure session. The streaming-container launch was rejected before execution; synchronous replay succeeded. GitHub search returned HTTP 422; a separate repository listing found no repositories accessible through the active connection. Two web requests for action tag-reference JSON failed, so the supplied workflow uses release-version tags rather than asserting unverified SHA pins. These events are described in [FAILURES.md](../../docs/FAILURES.md).

A draft fresh-extraction metadata helper looked for a nonexistent optional `sha256_before` key, which could make its local summary check vacuous. Before sealing, it was replaced by 52 explicit `sha256` versus `sha256_after` comparisons, all passing. The actual scientific runner and manifest validator already used the correct fields. No scientific output changed.

## Hosted and legal state

No hosted repository, issue, release, permission, or archive setting was modified. There was no accessible target repository in the active connection, and its exposed tool set supplied no create-repository operation. GitHub CI has not been executed. Destination and visibility remain unspecified. A distribution license has not been selected; no open-source license is silently granted.

The local identity is the publication pseudonym **Komorebi P.** The Git author email is an explicitly invalid placeholder, not a real personal email or a claim about account ownership. The final local tag fixes this scoped snapshot. Any subsequent correction must receive a new version rather than silently changing that snapshot.
