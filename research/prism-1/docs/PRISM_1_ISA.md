# PRISM Packet Seed Command specification

## 1. Command delivery

The first implementation uses a memory-resident 256-bit command ring. RISC-V management cores prepare packet and transfer descriptors, write commands, and ring a doorbell. A later implementation may map common operations into vendor-defined RISC-V custom encoding space.

The queue is the stable interface. Engine details may change without changing the graph model.

## 2. Command states

A command moves through the following states:

1. queued
2. ready
3. running
4. provisional
5. committed, replayed, or aborted

A command becomes ready when its dependency token is satisfied and its source packets are valid. Kernel completion creates a provisional destination. The destination becomes committed only after the declared certificate passes.

## 3. Command header

Each command contains:

- opcode
- source packet ID
- destination packet ID
- atlas ID
- representation form
- output contract
- shape class
- precision tag
- dependency token
- completion token
- payload pointer
- residual or certificate pointer

The packed layout in the RTL skeleton is provisional. The semantic fields are part of the architecture contract.

## 4. Packet commands

| Command | Meaning |
|---|---|
| `PLOAD` | Load or prefetch a packet working set |
| `PSELECT` | Apply a declared selector |
| `PSPLIT` | Replace a parent packet with child packets |
| `PCOARSEN` | Reconstruct a parent from a complete child family |
| `PGATHER` | Gather indexed or masked packet elements |
| `PSCATTER` | Scatter packet values into synthesis coordinates |
| `PTRACE` | Record a packet norm, trace, or energy |

## 5. Transform commands

| Command | Meaning |
|---|---|
| `FFT_STAGE` | Execute configured complex butterflies |
| `DCT_STAGE` | Execute cosine-transform butterflies |
| `FWHT_STAGE` | Execute Hadamard butterflies |
| `WAVELET_LIFT` | Execute predict, update, and scale steps |
| `POLYPHASE` | Extract, permute, or interleave phase channels |
| `ATLAS_SYNTH` | Apply a declared inverse or canonical frame synthesis |

## 6. Transfer commands

| Command | Meaning |
|---|---|
| `BLK_GEMM` | Apply a shape-class batch of transfer blocks |
| `BLK_SPARSE` | Apply a regular packet-edge group |
| `BDLR_APPLY` | Apply `D + U V*` without materialization |
| `BDLR_COMPOSE` | Produce compressed product factors |
| `WOODBURY` | Solve a BDLR system with packet solves and a small correction |
| `PACKET_SOLVE` | Solve independent local packet systems |
| `PMR_PLAN` | Select or replay a mixed-representation product plan |
| `MATERIALIZE` | Create an explicit array only under the explicit-array output contract |

## 7. Solver and recovery commands

| Command | Meaning |
|---|---|
| `GRAM_BUILD` | Build a packet Gram matrix |
| `CHOLESKY` | Factor a small positive system |
| `QR` | Factor a small rectangular system |
| `SVD_SMALL` | Estimate rank and singular vectors |
| `HANKEL_BUILD` | Stream moments into a Hankel matrix |
| `ANNIHILATOR` | Solve annihilating-filter equations |
| `ROOT_PHASE` | Recover physical roots from decimated channels |
| `VANDERMONDE` | Recover amplitudes from roots and moments |

## 8. Nonlinear and inference commands

| Command | Meaning |
|---|---|
| `PAIR_INTERACT` | Evaluate quadratic packet interactions |
| `VOLTERRA` | Apply a finite Volterra memory packet |
| `DELAY_UPDATE` | Advance finite-delay state |
| `BAYES_FIT` | Fit a shape-class batch of conjugate regressions |
| `BAYES_SCORE` | Evaluate predictive evidence |
| `MIXTURE_REDUCE` | Compute posterior moments and disagreement |

## 9. Graph commands

| Command | Meaning |
|---|---|
| `GRAPH_LOAD` | Load a transfer graph descriptor |
| `GRAPH_RUN` | Execute ready commands by dependency token |
| `GRAPH_REFINE` | Replace one packet task with a local child DAG |
| `GRAPH_REPLAY` | Replay a deterministic graph region |
| `GRAPH_ABORT` | Stop a region after an exception or certificate failure |

## 10. Certificate commands

| Command | Meaning |
|---|---|
| `RESIDUAL` | Form direct minus reconstructed output |
| `NORM_BOUND` | Accumulate a packet error bound |
| `ORTHO_CHECK` | Check energy or annihilation identities |
| `MARGIN_CHECK` | Check a branch, rank, or separation margin |
| `COMMIT` | Publish a result after the required checks pass |

## 11. Completion record

A completion record contains:

- completion token
- final state
- cycle count
- bytes moved
- exception code
- residual summary
- certificate pointer

A provisional result cannot satisfy a downstream dependency token.

## 12. Determinism

Deterministic mode fixes the reduction tree, solver order, and replay order. It may reduce throughput. It is intended for bring-up, regression testing, exact replay, and certificate comparison.

## 13. Exceptions

The minimum exception set includes:

- invalid packet descriptor
- missing dependency token
- unsupported shape
- unsupported numerical format
- packet-directory protection error
- solver nonconvergence
- certificate failure
- replay limit reached
- uncorrectable memory or link error
