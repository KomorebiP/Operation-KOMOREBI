# Independent packaging-script review

Verdict: **PASS for the exact packaging script reviewed below**. This is a code review, not a claim that the new Lean checkpoint or final archive has already passed.

Reviewer: coordinating agent, independent of the script's author. The complete script was read, including accepted-input validation, path handling, copying, manifest generation and terminal archive checks.

Script: `packaging/package_release.py`.

SHA-256: `3a2015755345db474406401dca00027f8a5abc7ea8eefc543b6cf78e59959e59`.

The builder binds the exact predecessor ZIP and every one of its 5,863 expanded files. It preserves them byte-for-byte under `inherited_v1.11.0/`. Its current formal tree comes from the accepted run source and must match the frozen assembly, source inventory and live overlay. It retains failed and successful development attempts, logs, mathematical/type review, verifier review, and accepted evidence, excluding reproducible objects and runtime binaries.

Current acceptance requires successful replay and reviewed postflight, source/helper/manifest preservation, every command's intended outcome, complete full new types, the all-declaration axiom policy, final review verdicts, and exact evidence hashes in the accepted ledger. The review manifest must predate the replay. The mathematical and terminal reviews must bind the actual source/export/receipt identities. A supplied prose PASS is bound as evidence, not automatically proved correct by the packager.

The script rejects unsafe, duplicate and colliding paths, nonregular archive entries, symbolic links, existing release destinations and malformed manifests. It checks copied hashes, repeats input checks, compares the finished ZIP to its expanded tree and manifest, and separately verifies historical and current formal subtrees. The archive's own digest is written to an external delivery report, avoiding a circular self-checksum.

The retained 12 adverse-input checks and predecessor validation support the implementation review. They do not establish correctness for arbitrary hostile inputs. Actual final-archive verification remains a separate gate. The script does not rerun Lean or independently authenticate the external compiled dependency caches.

No unresolved packaging defect was found for this release contract. Final archives must be built only after all project writers have frozen their files. Historical absolute paths remain unchanged provenance.
