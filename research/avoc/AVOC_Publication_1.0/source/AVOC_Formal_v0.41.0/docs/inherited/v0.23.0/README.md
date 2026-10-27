# AVOC Formal v0.23.0 — verified component-upgrade campaigns

This release adds a protected promotion gate and a checked executable component
specialization. A valid upgrade must preserve its declared contract, match the
current parent/revision and fixed authority identifiers, fit the charged budget,
and improve the fixed utility by its switch charge plus a positive margin.

The generic theory accepts arbitrary adaptive proposers. The delivered executable
is deliberately narrower: a read-only replay of a fixed immutable three-entry
catalogue. It does not generate new code, change the live research backend, replace
an LLM, or demonstrate multi-generation autonomous improvement.

The concrete improvement replaces an action-only retry dynamic-program evaluator
with its already-proved threshold specialization under `Retry.NoRevival`. It does
NOT replace the old full advisor report, which also returns an exact value.

Start with `FORMAL_THEORY.md`, `PROOF_BOUNDARY.md` and `REPRODUCE.md`.
New sources: `VerifiedUpgrade.lean`, `UpgradeSpecialization.lean`,
`UpgradeRuntime.lean`, `tools/UpgradeMain.lean`, `tools/run_upgrade_campaign.py`.

The release inherits the entire v0.22 source tree. New verification evidence is in
`results/v0.23.0`; earlier logs remain historical. No runtime or dependency binaries
are redistributed. The separate source-and-history bundle through v0.22 is unchanged.
