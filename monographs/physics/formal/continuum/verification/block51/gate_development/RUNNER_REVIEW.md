# Runner review and self-checks

The runner was prepared for the frozen centered Dirac extension. No final
production acceptance run was executed by the runner author before handoff.

## Executed checks

- The command-line entry point parses and displays its required arguments.
- The compact JSON auditor compiled and audited all 47 environment constants
  belonging to the accepted generator module. These comprise explicit named
  declarations and generated helpers, not 47 new theorems.
- The isolated placeholder was rejected by strict compilation with the intended
  `declaration uses sorry` diagnostic.
- The isolated custom-axiom module compiled successfully, then failed recursive
  policy auditing on `PhysicsPolicyControl.injected`.
- The timeout test deliberately printed an otherwise matching rejection
  diagnostic and then exceeded its time allowance. The command was correctly
  classified as FAIL. The harness self-check passed because the timeout was
  excluded from accepted negative controls.
- Unknown imports, unknown identifiers, ambiguity, parser failures, resource
  exhaustion and segmentation faults are excluded from accepted rejections.
- The merged 21-control manifest passed path, file and regex checks.
- The 26-module local import closure is ordered with every local dependency
  before its importer. All active source files pass the forbidden-token screen.

Raw self-check sources, commands, exits and logs are retained in `selfcheck01/`
and `selfcheck02/`. The latter contains an intentionally failing timeout-command
record. It is a test of the harness's refusal policy, not failed mathematics.

## Acceptance boundaries

The final run must start in a new output directory after source freeze. Each
local object is generated from the copied source closure. The runtime's shipped
manifest is checked at both endpoints except for explicitly recorded mutable
Git indexes. The final receipt requires stable source, generated auditor,
production-object and command-log hashes, all expected control outcomes, the
recursive declaration audit and actual imported-environment kernel replay.

The compiler and external Mathlib dependencies are reused. Their checked byte
identity does not constitute an independent rebuild or a second proof kernel.
The runner does not validate empirical physics or extend any mathematical claim
beyond the source theorem's hypotheses.
