# V0.3 test and verification plan

## Automated tests

The v0.3 source suite contains 179 passing tests. It covers retained v0.1/v0.2
behavior plus:

- sign-canonical QR, exponential, Cayley, polar, and learned-diagonal
  hard-operator parameterizations
- finite, orthogonality, minimum-singular-value, norm, and transient checks
  through depth 2,048
- bit-identical raw initialization tensors across hard and soft treatments
- an independent table oracle that fails closed on reversed/corrupt action
  order
- exhaustive direct-conditioned training supports for lengths 1--4
- the rule that every nonempty contiguous training subword action is in train
- deterministic uniform-with-replacement sampling and exact support/counter
  receipts
- disjoint 60/20/20 map partitions and a separate test-conditioned full-word
  action assay
- per-gate independent-seed pass fractions
- legacy Stage A and functional Stage B transport schemas
- immutable sparse model inputs excluding supervision and audit truth
- exact GF(5)^4 inference, closure certificates, and fail-closed novelty guards

Run from the package root with `python -m pytest -q`.

## Frozen integrity and completeness

The primary protocol is
`protocols/V0_3_STAGE_A_PRIMARY.json`, SHA-256
`ecd48865c7327b39b5d0b2679f2e6fc3e9509a01bce343cfe94b9b237482acaf`.
Its pre-test seal is `protocols/V0_3_STAGE_A_PRIMARY_SEAL.json`, file SHA-256
`84c15ffcef8553288fe3e3393e7056ca0c1cfcdd8c78639f61d0adfe6d80f5c9`.
The seal binds:

- 29-file scientific-code SHA-256
  `814ea6f2301523965bf8d94dd9da8bbb598451f03e0200cae1cde2ab8de53624`
- coordinate-split SHA-256
  `3aceaac6852f88360de0851eefc43bf46331d3b4efe3a04d0f2b9dfeff455340`
- four arms, seeds 300--311, 48 cells, 26 gates, and six transport pairs
- qualification protocol SHA-256
  `0bca42f89400904180f36872aaa4fb8040c2cb848b86e50dc084eb90a47634a0`
- qualification receipt SHA-256
  `511d706bd82f910d1817e21e99aa58823e86707b5652736fd74281e2d75e7f55`

Verification must fail on any inconsistent version/digest, missing cell,
checkpoint, transport record, gate, exact-oracle success, split audit,
direct-support receipt, full-action receipt, replay/post-hoc record, sparse
closure digest, prior archive, manifest entry, or checksum. It must also fail
unless training accounting reports exactly 49,152,000 accepted primary examples
and zero split violations.

Scientific gate failure is a valid completed result. Verification must agree
with the recorded 8/26 decision, not require every gate to pass.

## Exact training supports

| Length | Valid pairs / candidates | Support SHA-256 |
|---:|---:|---|
| 1 | 25,008 / 25,008 | `265cc1737ac80cf2afcfd2261a16b5d5d8770286511c3e1b6a7bac9bb3f326cb` |
| 2 | 32,120 / 50,016 | `c1074929f34aadefb48ad52de8882afe29e388e07cb6be66ed7b71d1d343be3b` |
| 3 | 37,936 / 100,032 | `7f5ab4a82c43e918f8485e0768cd6d1dd11c7fa37ac732ccf2d3644032ecae3d` |
| 4 | 45,680 / 200,064 | `7759e2320e3f3a8992f7d5654a1f1688d5cd15bd599dc09b0cdcccdce4ee5813` |

These condition the actual sampled training language, not the unbounded
algebraic closure of all train maps.

## Qualification and primary

The retained development-only qualification at
`results/v0.3.0/stage_a_qualification_v3/` completed 16 cells, processed
16,384,000 examples with zero violations, passed the exact oracle, and passed
8/8 engineering gates. Earlier partial/unsuccessful development paths remain
disclosed and are not primary evidence.

The sealed primary at `results/v0.3.0/stage_a_primary_v3/` completed 48 cells
and six transport pairs, processed 49,152,000 examples with zero violations,
passed the exact oracle, and passed 8/26 gates. Its completed receipt SHA-256 is
`1854d622e6154a44107da80164c77c306ac7a5472583e089e6188738b9e294e7`.

The execution supervisor interrupted the original process without a scientific
`FAILED` record. The recovery utility validated existing cells before adding
only missing cells and pairs under unchanged sealed bytes.
`results/v0.3.0/stage_a_primary_v3/RECOVERY_EVENTS.json` is authoritative for
that orchestration.

## Replay and post-hoc analysis

The `hard_correct`, seed-300 replay in
`results/v0.3.0/stage_a_reproducibility/` matched every state tensor byte,
canonical state/checkpoint hashes, metrics, and semantic record exactly. The raw
`torch.save` hash differed because replay provenance metadata differs; it is
informational, not the criterion.

`results/v0.3.0/stage_a_primary_v3/POSTHOC_DESCRIPTIVE.json` contains 100,000
paired seed resamples per contrast. These intervals are exploratory and do not
replace seed-fraction gates, create p-values, or revise the primary.

## Decision rule

All gates run after the first failure. Missing/nonfinite metrics fail closed.
A gate passes only when its mean and prespecified seed fraction both pass.
Operational completion, package integrity, and scientific success are distinct.

