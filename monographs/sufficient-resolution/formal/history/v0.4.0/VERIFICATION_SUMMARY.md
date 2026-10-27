# Verification summary — Sufficient Resolution v0.4.0

**Passed. 13 September 2026.**

| Check | Result |
|---|---|
| Fresh predecessor source rebuild, axiom audit and kernel replay | Pass: 190 theorems, 263 named declarations, 16 modules |
| Prior production proof files preserved | All 16 byte-identical |
| Cumulative clean compilation with warnings as errors | Pass: 22 modules plus import root |
| Theorem/lemma declarations | 272, including 82 additions |
| Explicitly named declarations audited | 357, including 94 additions |
| Transitive axiom allowlist | Only propext, Classical.choice, Quot.sound |
| Same-kernel replay through leanchecker | Pass: all 22 production modules |
| Deliberately false proof | Rejected |
| Deliberate placeholder | Rejected |
| Deliberate custom axiom | Detected and rejected by the audit allowlist |
| New exact rational assertions | 7,509 pass across 30 systems and 370 words |
| New negative controls | 10 invalid or underestimated inputs rejected |
| Earlier exact example checks | All pass |
| Earlier discrete-memory controls | 1,307 assertions across 20 systems pass |
| Earlier observable-model controls | 1,657 assertions across 30 systems pass; ten negative controls rejected |
| Extracted-source clean rebuild and axiom audit | Pass again: 272 theorems, 357 named declarations |
| Extracted-source same-kernel replay | Pass again: 22 modules |
| Execution inputs equal across both new runs | All 35 source/script/configuration files match |
| Original inputs unchanged during both runs | Pass |
| Version-1 computation manifests | Source/result hashes validated for both runs |

The new finite controls use exact rational matrices with the induced infinity norm.
They cover fine dimension 0–4, reduced dimension 0–3, output dimension 0–2,
operation alphabets 0–2 and all tested words through length 4. Scalar identities
are checked through length 12, with Bernoulli growth controls through length 29.
The deterministic seed is 20260913. Zero state, empty alphabet, zero readout,
noncommuting order, initial mismatch, multilevel error and split re-encoding are
included. The recursive majorant is compared with independently assembled
prefix/injection/suffix sums. Bounded controls do not establish the universal
claims; the Lean declarations do that under their printed hypotheses.

## Formal trust boundary

Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
Mathlib HEAD aeb72f1e9981b6d35b426b16dca7759be3e7ba06. All nine dependency HEAD
revisions match the manifest. Cached imported artifacts are reused, not independently
reconstructed. Replay uses the same Lean kernel, not an independently implemented
checker or comparator challenge.

Production sources contain no sorry, admit, custom axioms, unsafe declarations or
native_decide. The named-declaration counter does not inflate generated projections
or instances. The theorem counter includes supporting lemmas and examples, not
independent discoveries.

## Evidence

`verification/release/report.json`, `verification/roundtrip/report.json` and their
per-command logs contain actual command arrays, exit status, timing and source hashes.
`verification/ROUNDTRIP_SOURCE_MATCH.json` records the 35 identical execution inputs.
`verification/PREDECESSOR_PRESERVATION.json` records the 16 unchanged proof files.
`verification/PRINCIPAL_SIGNATURES_v0.4.0.log` prints the actual principal types.
`verification/CONTRACT_REVIEW_v0.4.0.md` records the mathematical statement review.

The source checkpoint was extracted without .lake build objects, then rebuilt and
replayed. The final archive adds the resulting evidence and updated documentation;
its executed proof/test/configuration inputs remain byte-identical. Final ZIP CRC
and member hashes are checked separately and are not confused with proof validity.

Both manifests use the retained version-1 schema, with supplementary before/after
input hashes in report.json. That is a documented provenance limit, not a version-2
bounded-runner claim. Lean commands ran serially with a per-command timeout of 180
seconds and one Lean thread. A separate hard memory cap was not imposed.

## Failures and corrections

Initial drafts failed on deprecated continuous-map application lemmas, a polynomial
tactic step, the side of an addition-monotonicity lemma, and an over-eager scalar
extensionality rule. The proofs were corrected with current APIs and explicit
algebra/extensionality; intended hypotheses were not weakened and no warning checks
were disabled. An interactive extraction-session request was unsupported, so a
logged noninteractive extraction restored the runtime successfully. Draft diagnostics
and corrected reruns are retained. No unresolved production compilation or verification
failure remains.

The deliberately proved unbounded-error example is a mathematical boundary result,
not a failed implementation or a counterexample to the stability theorem.
