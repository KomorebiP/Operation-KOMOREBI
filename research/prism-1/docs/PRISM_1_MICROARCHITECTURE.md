# Komorebi PRISM-1 microarchitecture

## 1. Architectural thesis

PRISM-1 executes the cheapest valid representation of a typed operator graph. It does not preserve a dense matrix unless the requested output is the explicit array.

## 2. Package

The reference package contains four compute chiplets, one I/O and control die, and four HBM4 stacks. The I/O die carries host attachment, RISC-V management cores, global scheduling, telemetry, protection, and package control.

## 3. Compute chiplet

Each compute chiplet contains:

- 16 Packet Streaming Multiprocessors in a 4 by 4 mesh
- 64 execution groups
- 8 transform engines
- 4 resident small-solver engines
- 1 exact-arithmetic cluster
- 16 MiB shared SRAM
- package-facing UCIe routers

## 4. Packet Streaming Multiprocessor

Each multiprocessor contains:

- packet-warp front end
- representation router
- descriptor and atlas cache
- four execution groups
- 2 MiB packet scratchpad in four banked regions
- asynchronous projector and polyphase DMA
- mesh interface
- certificate and commit path

## 5. Execution group

Each execution group contains a 16 by 16 matrix array and programmable vector lanes. It handles grouped block work, low-rank contractions, Kronecker mode products, sparse-factor stages, selectors, reductions, and generic leaves.

## 6. Representation router

The router dispatches block work to matrix lanes, factor work to contraction paths, transform plans to the shared transform fabric, algebraic systems to resident solvers, and unsupported leaves to the generic path.

## 7. Command path

A packet warp issues when dependencies and source packets are ready. Execution writes a provisional packet. The commit controller releases that packet only after its declared certificate passes.

## 8. Packet directory and scoreboard

The packet directory records location, representation form, validity, provisional state, committed state, precision, provenance, and replay region. Only committed packets release completion tokens.

## 9. Transform engines

The transform fabric shares butterfly, permutation, lifting, and selector hardware for FFT, DCT, FWHT, Haar, biorthogonal lifting, and polyphase transforms.

## 10. Small solvers

Resident solvers handle Cholesky, QR, Jacobi-style SVD, Hankel rank, annihilators, polynomial roots, Vandermonde systems, Woodbury corrections, and small Bayesian fits. FP64 is the default for rank and phase decisions.

## 11. Memory hierarchy

HBM stores exact archives, cold factors, large graphs, and history. Shared SRAM stores active graphs and reusable representations. PSM scratchpads store local blocks, factor panels, transform stages, solver panels, and residuals.

An exact archive may be a transform tuple, factor graph, sparse chain, packet tree, edge geometry, or explicit sample field. Completeness does not require a dense matrix.

## 12. Mixed precision and certificates

Every edge carries precision and sensitivity. The certificate path accumulates graph-level bounds with wide arithmetic. Deterministic mode fixes reduction order and replay.

## 13. Local refinement

The scheduler stores the parent interface separately from the child implementation. Refinement replaces only the local parent region and its incident edges.

## 14. Unknown-edge recovery

Fourier moments stream through polyphase grouping, Hankel construction, rank estimation, annihilator solution, physical phase recovery, Vandermonde amplitudes, native edge synthesis, and residual checks.

## 15. PR-LASM path

Exact archives remain distinct from macro, meso, and micro predictive states. Mechanism families share resident feature matrices. Exact replay edges remain separate from probabilistic predictions.

## 16. Reliability

Descriptor tables, token state, representation tags, and certificate records require ECC or parity. A local PSM fault invalidates the destination packet and descendants. Package-wide reset is reserved for loss of directory or scheduler coherence.

## 17. Negative controls

The compiler must route generic dense work, small one-off graphs, and irregular no-reuse workloads to CUDA or another generic path when the PRISM route is not cheaper.
