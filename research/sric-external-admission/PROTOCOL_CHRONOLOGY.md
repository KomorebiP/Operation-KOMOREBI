# Protocol Chronology

```text
T0  package code, thresholds, claim tier, source lock frozen
T1  external repository checked out at exact commit
T2  required Git blobs verified and dirty tree rejected
T3  pinned checkpoint and GPT-2 revision downloaded
T4  full checkpoint and local GPT-2 payload hashed
T5  deterministic task population and group IDs frozen
T6  covariance-calibration and causal-audit groups frozen
T7  donor plans and semantic split IDs frozen
T8  pre-audit seal written
T9  calibration traces captured and covariance committed
T10 causal audit executed on disjoint audit rows
T11 causal status assigned
T12 if admitted, semantic discovery traces captured
T13 semantic calibration traces captured
T14 candidate quotient chosen
T15 quotient basis, center, thresholds, and splits sealed
T16 semantic final traces captured for the first time
T17 post-seal proof-instance witness revealed
T18 causal subspace patching executed
T19 explicit-CoT comparison revealed
T20 canonical result receipt written
```

No T16-T19 object may influence T14. The implementation records and tests the semantic chronology.
