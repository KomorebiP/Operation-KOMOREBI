# PRISM packet compiler

## 1. Input graph

The compiler accepts a typed graph containing seed objects, packet and atlas descriptors, transfer edges, parent and child relations, nonlinear nodes, memory nodes, output contracts, error budgets, and reconstruction certificates.

## 2. Shared Packet IR

Packet IR records:

- representation form
- packet addresses and parent relations
- operator payload or factor references
- shape class and precision
- output contract
- dependency and replay region
- certificate plan

The same IR lowers to the CUDA compatibility backend or the PRISM backend.

## 3. Routing pass

A packet route is considered only when the representation reduces arithmetic, storage, data movement, launch count, or repeated setup. Generic dense operators with weak structure remain on a generic path. Uncertain cases are profiled under the same output contract.

## 4. Legality

The compiler checks:

1. packet completeness for every exact synthesis
2. shape compatibility for every transfer
3. exact parent and child reconstruction
4. analysis and synthesis pairing
5. output-contract support
6. certificate requirements
7. precision and rounding support

## 5. Representation planning

The compiler may choose:

- explicit dense leaf
- block diagonal
- regular block sparse
- low rank
- BDLR
- Kronecker factors
- sparse factor chain
- transform-domain plan
- recursive packet split

PMR-GEMM uses a Bellman recurrence on a finite candidate tree. The generic leaf remains available as the fallback.

## 6. Shape classes and packet warps

Equal shapes are grouped into packet warps. Irregular work is grouped only when gather, scatter, padding, and divergence cost less than separate execution.

## 7. Precision allocation

Every transfer edge carries a sensitivity weight. The compiler allocates a continuous error budget, maps it to supported formats, reserves wide accumulation where needed, and checks the graph-level budget before emission.

## 8. Placement

Placement keeps together parent and child packets, BDLR blocks and factor rows, transform stages sharing a stream, small-solver chains, and Bayesian models sharing one design matrix.

## 9. Backend lowering

### CUDA backend

The CUDA route uses grouped or batched matrix kernels, asynchronous copies, CUDA Graph replay, FFT and sparse libraries, stream-ordered memory, compressed factors, and packetwise residuals.

### PRISM backend

The PRISM route emits packet-warps, representation-router decisions, PSM placement, resident factor and solver state, Packet Seed Commands, and certificate-gated commit records.

## 10. Local refinement

A local refinement replaces one parent task by a child DAG. Remote descriptors remain unchanged when their packet interfaces do not change.

## 11. Output

The compiler emits packet and atlas tables, transfer descriptors, packet-warps, command entries, placement, routing, replay regions, completion tokens, certificate policy, and an expected cost report.

## 12. Conformance tests

A compiler implementation must pass exact reconstruction, transform round trip, output-contract legality, PMR planning, local refinement locality, error accounting, deterministic replay, reject-path routing, and certificate-gated commit tests.
