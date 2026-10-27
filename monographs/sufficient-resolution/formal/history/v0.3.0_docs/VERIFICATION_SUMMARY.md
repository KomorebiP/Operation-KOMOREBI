# Verification summary — Sufficient Resolution v0.3.0

**Passed. 13 September 2026.**

| Check | Result |
|---|---|
| Fresh v0.2.0 predecessor source rebuild and kernel replay | Passed: 125 theorems, 169 named declarations, 11 modules |
| Predecessor production source preservation | All 11 proof files byte-for-byte unchanged |
| Current cumulative source rebuild, with warnings as errors | Passed: 16 production modules and import root |
| Current explicit theorem/lemma declarations | 190 (65 added) |
| Current explicitly named declarations audited | 263 (94 added) |
| Axiom allowlist | Only propext, Classical.choice, Quot.sound |
| Same-kernel leanchecker replay | Passed for all 16 production modules |
| Deliberately false Lean theorem | Rejected |
| Deliberate Lean placeholder | Rejected |
| Deliberate custom axiom | Detected and rejected by the audit allowlist |
| New exact rational controls | 1,657 assertions, 30 systems passed |
| New Python negative controls | 10 corrupt/invalid inputs or certificates rejected |
| Original exact rational controls | 5 checks passed |
| Discrete-memory predecessor controls | 1,307 assertions across 20 systems passed |
| Extracted-source clean build and axiom audit | Passed again: all 190 theorems and 263 named declarations |
| Extracted-source same-kernel replay | Passed again for all 16 production modules |
| Execution inputs compared across release/extraction runs | All 27 source, script and configuration inputs identical |
| Manifest result/source hashes | Validated for both runs |

The 30 new systems cover state dimension 0–6, operation alphabets of size 0–2,
output dimension 0–3, complete word-map fidelity through depth at most 4, and
explicit horizon observation tables through depth at most 5. They include zero
state, empty alphabet, zero readout, zero output space, full readout, dependent
rational outputs, sharp nilpotent chains, duplicate operations, and a noncommuting
example that is also instantiated in Lean. The random seed is 20260913.

The controls compare sparse row saturation against explicit all-word observation
tables using a separate forward-elimination rank routine. They validate exact
certificate identities and JSON round trips. These finite tests do not replace
the universal Lean proofs, and the Python minimizer is not formally verified.

All 11 predecessor production proof sources are unchanged. The kernel checks use
Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, and Mathlib commit
aeb72f1e9981b6d35b426b16dca7759be3e7ba06. All nine package revisions are pinned and
checked. Imported Lean/Mathlib artifacts are reused. This is same-kernel replay,
not independent proof-kernel implementation or fresh certification of all imports.

Production code contains no sorry, admit, custom axioms, unsafe declarations or
native_decide. The 263 figure refers to explicitly named source declarations;
automatically generated projections/instances are not inflated into that count.
The theorem count includes supporting lemmas and exact examples.

## Evidence

- `verification/release/report.json`, `axioms.json`, and per-module logs.
- `verification/roundtrip/report.json`, `axioms.json`, and per-module logs.
- `verification/ROUNDTRIP_SOURCE_MATCH.json`: exact execution-input comparison.
- `verification/principal_signatures_v0.3.0.log`: fully elaborated central theorem types.
- `verification/predecessor_v0.2.0_sources.json`: source-preservation hashes.
- `verification/development_v0.3.0/`: failed draft diagnostics and corrected reruns.

A source checkpoint archive was extracted and rebuilt. The final archive adds the
resulting evidence and updated documentation afterward; the executed proof/test
inputs remain byte-identical. Final ZIP integrity and member hashes are checked
separately, not confused with Lean proof verification.

Initial failures were import/API, dependent-rewrite, hypothesis-inclusion, comment
placement and extensionality issues. All were corrected without adding assumptions
to the intended contracts or disabling warning checks. The runtime extraction's
first attempt also failed for a missing destination directory; restoration and
all actual source verification then succeeded. Details are in DEVELOPMENT_NOTES.md.
