# Results index

## V0.3.0

| Path | Status | Purpose |
|---|---|---|
| `results/v0.3.0/INTEGRATED_FINDINGS.md` | Integrated interpretation | Primary conclusions, limitations, and next-block decision |
| `results/v0.3.0/stage_a_primary_v3/` | Sealed primary, complete, failed | 48/48 arm-seed cells, six transport pairs, 49,152,000 training examples, exact oracle pass, zero split violations |
| `results/v0.3.0/stage_a_primary_v3/GATES.json` | Authoritative frozen decision | 8/26 pass; conjunctive primary failed |
| `results/v0.3.0/stage_a_primary_v3/REPORT.md` | Generated primary report | Arm means, all frozen gates, transport summary, and interpretation boundary |
| `results/v0.3.0/stage_a_primary_v3/RECEIPT.json` | Completion receipt | Protocol/code/split hashes, grid, exact-oracle, and training-sampling accounting |
| `results/v0.3.0/stage_a_primary_v3/RECOVERY_EVENTS.json` | Operational provenance | Validation and bounded recovery after the original process was interrupted |
| `results/v0.3.0/stage_a_primary_v3/POSTHOC_DESCRIPTIVE.md` | Post-hoc descriptive | 100,000-resample seed-paired intervals; not a frozen-gate reinterpretation |
| `results/v0.3.0/stage_a_primary_v3/POSTHOC_DESCRIPTIVE.json` | Post-hoc machine record | Full seed values, contrasts, RNG derivations, and hashes |
| `results/v0.3.0/stage_a_reproducibility/` | Post-hoc verification, passed | Exact `hard_correct` seed-300 metric and parameter-tensor replay |
| `results/v0.3.0/stage_a_qualification_v3/` | Development qualification, passed | 16 cells, 16,384,000 examples, zero violations, exact oracle, 8/8 engineering gates |
| `results/v0.3.0/stage_a_calibration_8000/` | Development calibration | Four-seed 8,000-step hard-QR calibration; not primary evidence |
| `results/v0.3.0/stage_a_calibration_alternatives/` | Development comparison | Relation, composition-weight, and learned-diagonal-metric alternatives |
| `results/v0.3.0/stage_a_qualification_failed_4000/` | Incomplete negative development attempt | Disclosed 4,000-step path that did not support qualification |
| `results/v0.3.0/stage_a_qualification_superseded_preversion/` | Superseded partial | Pre-version attempt; excluded from primary evidence |
| `results/v0.3.0/stage_a_qualification_superseded_slow_sampler/` | Superseded partial | Old rejection-sampler attempt; excluded from primary evidence |
| `results/v0.3.0/stage_a_qualification/` | Stale interrupted partial | Non-authoritative output path retained for provenance; use `_v3` qualification |

The primary protocol is
`protocols/V0_3_STAGE_A_PRIMARY.json` (SHA-256
`ecd48865c7327b39b5d0b2679f2e6fc3e9509a01bce343cfe94b9b237482acaf`),
and its pre-test seal is `protocols/V0_3_STAGE_A_PRIMARY_SEAL.json`.

## Stage B v0.3 scaffolds

| Path | Status | Purpose |
|---|---|---|
| `benchmarks/sparse_affine_product/README.md` | Audited task design, no trained result | Sparse GF(5)^4 inputs, exact identifiability, closure bounds, and claim restrictions |
| `benchmarks/functional_transport/README.md` | Developmental assay design | Beyond-declared-codebook residual transport, cycle, commuting-square, and component patch metrics |
| `benchmarks/hard_operator/benchmark_parameterizations.py` | Development utility | Hard-operator parameterization timing/diagnostic benchmark |

## Prior releases

| Path | Status | Purpose |
|---|---|---|
| `results/v0.2.0/INTEGRATED_FINDINGS.md` | Prior integrated result | V0.2 frozen primary interpretation: 20/26 gates passed, overall failed |
| `results/v0.2.0/preregistered_primary/` | Prior primary | 80 arm-seed cells and five transport pairs |
| `results/v0.1.1/` | Prior developmental release | Original v0.1.1 results retained with later claim corrections |
| `archive/Komorebi_Neuralese_Operator_Workspace_v0.2.0.zip` | Preserved prior archive | SHA-256 `9bd43069b1b184943aee32465c73c2441f4842165ede5c41a9f28f5f97b9e73d` |
| `archive/Komorebi_Neuralese_Operator_Workspace_v0.1.1.zip` | Preserved prior archive | SHA-256 `2c215d33b0b3f4788da838337272c29cd3c662fbf4cfcd23bdb915432f2c91ba` |

`PRIOR_RELEASES.json` is the machine-readable archive ledger. Final package
membership and byte hashes are recorded separately in `MANIFEST.json` and
`SHA256SUMS.txt`.
