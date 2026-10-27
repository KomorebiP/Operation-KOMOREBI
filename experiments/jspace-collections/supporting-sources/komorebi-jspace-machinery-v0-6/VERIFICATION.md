# Machinery verification

Author: **Komorebi P.** · 2026-09-05

The v0.6 engineering verification passes **21 behavioral tests and 23 live command-line checks**. These validate authored machinery and execution semantics. They are not learning benchmarks or an ARC score.

## Recorded workflow

The supplied grid contains a three-cell pattern, a destination marker, and an unrelated distractor. A parameterized function reads the original scene, extracts the pattern, rotates it, resolves the destination marker, and writes the transformed patch back into a copy of the scene.

| Check | Observed result |
|---|---|
| Initial crop/rotate/place computation | Matches the independently specified expected grid |
| Original scene preservation | Input values and the original-output view remain unchanged |
| Changing rotation from one to two quarter turns | Exactly two result cells differ |
| Edit inspection | Changed intermediate values include the transformed patch and resulting grid |
| Preview | Produces a comparison without committing a revision |
| Pure-operation cache on the recorded edit | Six native results reused, four native operations recomputed |
| Invalid destination near the canvas edge | Bounds failure, with the bank unchanged |
| Disabled copy with an empty source selection | Returns the original scene without evaluating the invalid extraction |
| Undo and checkout | Reproduce the original and edited results |
| Save and reload | Replays four revisions and restores four named workspaces |

Cache counts describe this specific warmed-cache demonstration. They are not a general performance or speedup claim.

The scalar example produces approximately −6 from the frozen learned product kernel and approximately 2 after four learned-addition steps of 0.25 from 1. The authored comparison and conditional selection produce maximum(−3, 2) = 2. Floating-point kernel outputs are retained rather than rounded to exact arithmetic.

## Behavioral coverage

The test suite checks:

- Distinct types for colors, integer counts, scalars, flags, grids and masks.
- Explicit subtraction operand order and reusable-function rebinding.
- Preservation of the original scene during extraction and placement.
- Lazy conditional execution, zero-iteration behavior, and execution budgets.
- Rejection of cyclic dependencies, missing bindings, and recursive definitions.
- Masked-copy alignment and limited writes.
- Atomic rejection of failed edits.
- Preview, independent forks, undo, checkout, and computation-graph edits.
- Cache reuse under unchanged arguments and recomputation under changed ones.
- Stale revision detection, operation-identity checks, and persisted-history replay.
- Protection against overwriting an unrelated existing bank or bypassing an active writer lock.
- Copy isolation in returned definitions and additive function-library extension.

The live command-line checks cover initialization, empty banks, run, fork, preview, input edit, intermediate-value inspection, dependency inspection, trace export, invalid-type rejection, undo, checkout, function definition, registry inspection, workspace creation from files, program replacement, branch comparison, history, listing, and overwrite rejection.

The first command-line audit stopped because a check incorrectly required a particular order for a dependency list after canonical JSON serialization. The check now compares dependency membership. Argument roles were already named and execution did not depend on JSON key order. This correction changed the audit, not the runtime's computations.

## Provenance and persistence

The v0.5 kernel implementation, seed-0 checkpoint, and accepted-channel catalog are byte-identical to their files in the bundled prior release. The complete prior ZIP is also preserved unchanged, with SHA-256:

```text
7a6d40824b8cbafaeacfc7e363462ede866c0e5800925c1e02e8ab1e60071794
```

The current registry distinguishes **17 supplied native operations**, **three frozen learned kernels**, and **two authored reusable functions**. It does not claim that all 22 entries were learned.

Saved revisions include snapshot hashes, recorded outputs, operation identities, and parent references. Loading replays every stored revision. Categorical outputs must match exactly. Scalar comparisons allow an absolute difference of 10⁻⁹ to accommodate small numerical differences between runtimes. There is no automatic repair of changed meanings or corrupted snapshots.

## Scope

No model training, automated program discovery, new learned representation, broad grid-solver evaluation, or ARC benchmark was performed. Programs and control flow in these demonstrations are authored. The earlier 24-dimensional latent-state interface remains available through the bundled v0.5 release, without an automatic migration into the new typed runtime.

Python execution was tested on Linux. The PowerShell wrapper was inspected but not executed on Windows. Broader scaling, long histories, and concurrent multi-user operation are unmeasured.

Machine-readable results are in `results/verification.json`, individual test results in `results/tests.txt`, and full example states and traces in `examples/recorded_run/`.
