# PRISM-1R v0.2 Implementation Handoff

This package extends the PRISM-1R deployment blueprint into an implementation-oriented handoff.

## Contents

- `docs/`: LaTeX and compiled PDF blueprint
- `figures/`: Python-generated architecture, PSM, NoC, state-machine, deployment, and command-layout figures
- `python/`: figure generator source
- `rtl/`: SystemVerilog boundary skeletons for the generation guard and commit path
- `sim/`: minimal executable semantic reference for commit/replay behavior
- `tests/`: Python smoke tests for commit invariants

## Important status boundary

The RTL is a semantic/interface skeleton, not production RTL. It has not been synthesized, timed, placed, or power-analyzed. The command bit allocation is a candidate packing for prototyping, not a frozen ABI.

## Semantic invariants carried by this release

1. A stale generation can never commit.
2. Certificate failure cannot silently become success.
3. Uncorrectable faults force containment/abort.
4. Retryable local failures may enter replay without invalidating unrelated committed state.
5. Hardware specialization may not change the mathematical output contract.
