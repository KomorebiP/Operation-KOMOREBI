# AVOC v0.40.0 development failures and obstructions

## Mathematical obstructions retained

- Equal per-position success marginals do not establish the binomial count law.
  ObservationStream's correlated pair gives both marginals 1/2 but count-one mass 0.
- Outcome-dependent consuming censoring can change the target success probability.
  ObservationCensoring proves the fair success-only retention example.
- Conditioning on sample completion can bias the count law even when the gate
  depends only on preceding reports. ObservationCensoring proves the two-bit
  example; exact oracle/reviewer records show failures for the actual intervals.
- None of these obstructions refutes the final unconditional bad-issuance bound.
  They explain why the final target and deployment gate are stated as they are.

## Development compilation records

All failed attempts were retained with logs and source/import hashes.
Stream attempts 01,03,04,07,10,11 exposed elaboration/cardinality simplification,
complement lemma, deprecated-name, closed-goal, or unused-simp issues. The final
stream 12 build passes. See stream_notes.md for individual diagnoses.

Censoring's first attempt failed on unused simplification arguments; its final
module passes. Reveal's first build exposed an unused DecidableEq section
variable; it was scoped correctly and the final module passes.

Root observed_policy_initial failed on unused Fintype section variables and
insufficient monadic simplification before subst. Variables were scoped to the
probability theorem and simplification corrected. observed_policy_second passes.
policy_initial failed only the ambiguous-open-namespace linter; the fully
qualified namespace fixes it. policy_shared passes. No linter was disabled.

These are development failures, not successful proof rejections. Intentional
negative tests are separate and must reach their false proposition. No project
axiom, admitted proof, native_decide, or unsafe theorem was used to repair them.

## Verification-infrastructure findings

Independent review found that an empty required JSON object could bypass checks
behind a truthiness guard, and a negative-test validator initially allowed any
nonzero exit, including a crash. The loader now requires a nonempty expected
container type; negatives require Lean exit 1 and substantive proof diagnostics.
Fourteen isolated mutation probes confirm those cases reject. The exact findings,
script revisions, and outcomes are retained in observation_review_gate_mutations.

The original v0.39 ZIP still had a v0.38 README heading and v0.38 root
AUDIT.json/SOURCE_PROVENANCE.json beside correct v0.39 release records. Active
metadata and continuation/gap pointers are refreshed to v0.40; exact prior bytes
are preserved in provenance/v0.39_release_top. The older missing-v0.36-source
provenance boundary is retained. No inherited non-audit theorem
source was changed to achieve this release.

The first source scan also matched inherited identifiers named `admit` as if
they were proof tactics. Its report is preserved. The corrected scanner matches
selected tactic/declaration patterns after masking comments/strings; it remains
a heuristic source check. Warnings-as-errors builds and the exact axiom audit
are separate admission safeguards. No inherited identifier was renamed.

Historical failed or partial runs are never counted as final passing evidence.
