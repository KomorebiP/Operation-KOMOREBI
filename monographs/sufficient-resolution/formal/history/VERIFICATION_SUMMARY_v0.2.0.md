# Verification summary — Sufficient Resolution v0.2.0

**Status: passed. 13 September 2026.**

| Check | Result |
|---|---|
| Original v0.1.0 source rebuild and kernel replay | Passed: 68 theorems, 98 named declarations |
| Preservation of original production sources | All six files byte-for-byte unchanged |
| Cumulative clean source compilation | Passed: 11 production modules and import root |
| Warnings treated as errors | Passed |
| Explicit theorem declarations | 125 (57 new) |
| Explicitly named declarations audited | 169 (71 new) |
| Axiom allowlist | Only propext, Classical.choice, Quot.sound |
| Same-kernel leanchecker replay | Passed for all 11 production modules |
| Deliberately false theorem | Rejected |
| Deliberate placeholder | Rejected |
| Deliberate custom axiom | Detected and rejected by audit allowlist |
| Original rational controls | 5 passed |
| Discrete-memory rational controls | 1,307 assertions passed across 20 systems |
| Extracted-source clean rebuild and kernel replay | Passed again for all 11 modules |
| Execution-input hashes between original and extracted source | Identical |
| Manifest result/source-hash validation | Passed for both cumulative runs |

The exact-rational controls cover visible dimensions 1–2, hidden dimensions 0–3,
evolution depth through 9, and power-defect pairs through m,n=4. They include
nonorthogonal split coordinates, delayed return, zero hidden dimension, and a
prepared/all-state distinction. These finite controls are not the universal proof.

The source includes no production sorry, admit, custom axiom, unsafe or
native_decide. Deliberate negative-control files are not imported by the library.
The declared counts include helper lemmas and exact examples, not independent
discoveries or a cross-paper theorem census.

Both compilation and replay use Lean 4.34.0-rc2, commit
6a10ac8c22beadecabdbb0919c2b50214762f91d, and Mathlib commit
aeb72f1e9981b6d35b426b16dca7759be3e7ba06. All nine package pins are checked.
The imported runtime and Mathlib artifacts are reused; they are not independently
reconstructed or checked by a separate proof-kernel implementation.

Current evidence:
- verification/release/report.json and axioms.json
- verification/roundtrip/report.json and axioms.json
- verification/principal_signatures.log
- verification/predecessor_sources.json

Draft failures and their corrections are documented in DEVELOPMENT_NOTES.md, with
raw diagnostics in verification/development_v0.2.0/. The final production runs have
no unresolved compiler failure. No literature-novelty claim is made.
