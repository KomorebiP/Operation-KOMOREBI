# Failure ledger — v0.24

## Mathematical failures of proposed shortcuts

1. Residual syzygy coefficients cannot in general be frozen as exact nonlinear relations. Lean counterexample: `(x,x^2)` over Z/8Z.
2. Ambient power-divisibility cannot in general be transferred into a submodule. Lean counterexample: `2R` in Z/4Z.

These invalidate shortcuts, not Strong Artin or the prior linear exact-sequence theorems.

## Tool and proof-engineering failures

- The first interactive runtime-restoration command failed with `StreamingExecNotEnabledContainerError`. The ordinary synchronous restoration subsequently assembled the exact runtime hash and extracted successfully.
- One multi-module development wrapper timed out after six recorded successful modules; no running process remained. Remaining modules were explicitly rerun in smaller batches. No interrupted wrapper was counted as a complete pass.
- Rejected draft errors included an over-eager `ext` tactic splitting a product, unused-section/sequence linter failures under warnings-as-errors, a missing `Decidable` reduction through a submodule definition, and a typeclass/namespace mismatch in extension of raw evaluations. The final extension uses `Subspace.dualLift` explicitly.

### Recorded nonzero compiler attempts

- `SyzygyAugmentedImage`: RC=1, source `cdc0a90d14842f1f43b7ce3ad04a2ec278b061ab6ffdeb67617ceb7a4c6e812a`, log `verification/development/SyzygyAugmentedImage_1789165425506997980.log`.
- `SyzygyBoundaryExamples`: RC=1, source `ced1e60dfb4de5e8bc1d4fa884130ce50ef3b5977b242527aeae5e997806f08f`, log `verification/development/SyzygyBoundaryExamples_1789165643563249510.log`.
- `IntrinsicCompatibleTarget`: RC=1, source `1fd912a4f45b6ebc00471ca14506f14afce8ed6a208333625677dd3ee5878bc7`, log `verification/development/IntrinsicCompatibleTarget_1789165820515670157.log`.
- `IntrinsicCompatibleTarget`: RC=1, source `d6847b462e876946d79f04a95582cbfcd47e65f3b89ed1aac0f414c1aba06444`, log `verification/development/IntrinsicCompatibleTarget_1789165874114700609.log`.
- `IntrinsicCompatibleTarget`: RC=1, source `009795aca0f05b69e81626c3a42f85e3655dca6c559b7bc745092ce041532a57`, log `verification/development/IntrinsicCompatibleTarget_1789165904872114242.log`.
- `MovingRedundancyReduction`: RC=1, source `15d43b0423a60b99d911088f86aa5bdce056cbf8281f14a1fc517c3752568886`, log `verification/development/MovingRedundancyReduction_1789165993451916478.log`.

Compiler output from rejected drafts may contain `sorryAx` for unresolved goals. Those drafts were not promoted. Final sources and every accepted axiom audit must contain no `sorryAx`.
