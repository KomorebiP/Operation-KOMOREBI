# Paper VIII: First Lean Block Coverage Ledger

**Author: Komorebi P.**

Source edition: *Packet Operator Algorithms, Exact Compilation, and GPU Realization*, strengthened edition of August 14, 2026. The source register labels complete proof environments, not machine verification. This ledger adds an independent Lean status without altering the manuscript.

**10 of 56 manuscript-proved results fully covered. 46 remain not fully covered, including one boundary-only audit. Four classical inputs are separate.**

The source has 85 numbered records: 28 theorems, 11 propositions, 17 corollaries, 20 definitions, five remarks, and four standard facts.

## Checked results

| Item | Source result | Module |
|---|---|---|
| 2.3 | Exact evaluation | `PacketIR` |
| 2.5 | Block composition | `PacketIR` |
| 2.6 | Adjoint and tensor semantics | `PacketIR` |
| 5.1 | Exact BDLR product | `LowRankAlgebra` |
| 5.3 | Woodbury inversion | `LowRankAlgebra` |
| 5.4 | Inverse norm bound | `LowRankAlgebra` |
| 6.1 | Path support of powers | `TransferSupport` |
| 6.2 | Polynomial support | `TransferSupport` |
| 6.3 | Acyclic transfer nilpotence | `TransferSupport` |
| 8.1 | Packet perturbation certificate | `PacketPerturbation` |

## Exact assumptions and coverage

### 2.3 — Exact evaluation
Finite orthogonal idempotent family summing to one. Exact nonzero support, not thresholded support. Actual rectangular matrix batches are covered.

Checked names: `KomorebiPaperVIII.exact_active_evaluation`, `KomorebiPaperVIII.exact_active_action`, `KomorebiPaperVIII.exact_matrix_batch`.

### 2.5 — Block composition
Finite projector family over a ring. Relational composition gives an inclusion because nonzero path terms can cancel.

Checked names: `KomorebiPaperVIII.exact_block_composition`, `KomorebiPaperVIII.product_support_inclusion`.

### 2.6 — Adjoint and tensor semantics
Adjoint identity explicitly assumes self-adjoint projectors in a star ring. Tensor identity uses actual Kronecker products of finite matrices.

Checked names: `KomorebiPaperVIII.exact_adjoint_block`, `KomorebiPaperVIII.exact_tensor_block`.

### 5.1 — Exact BDLR product
Finite rectangular factors over a field with involution. Diagonal closure and actual correction rank are proved. No materialization or timing claim.

Checked names: `KomorebiPaperVIII.packet_diagonal_product`, `KomorebiPaperVIII.bdlr_product`, `KomorebiPaperVIII.bdlr_product_rank_bound`.

### 5.3 — Woodbury inversion
Both D and I+V* D^{-1} U are units. The update is proved invertible. Ordinary matrix inverse and arbitrary right-hand-side batches. Uses Mathlib classical Woodbury identity.

Checked names: `KomorebiPaperVIII.bdlr_woodbury`, `KomorebiPaperVIII.bdlr_update_isUnit`, `KomorebiPaperVIII.bdlr_woodbury_solve`.

### 5.4 — Inverse norm bound
Real or complex matrices with the Hilbert-space L2 operator norm, including rectangular factors. Same two invertibility assumptions as 5.3.

Checked names: `KomorebiPaperVIII.bdlr_inverse_norm_bound`.

### 6.1 — Path support of powers
Recursive finite sum over active paths equals the actual block of A^n. Includes length zero explicitly.

Checked names: `KomorebiPaperVIII.power_path_expansion`, `KomorebiPaperVIII.power_block_zero_of_no_path`, `KomorebiPaperVIII.power_support_inclusion`.

### 6.2 — Polynomial support
Actual finite polynomial sum in an algebra. Support contained in the union over powers, including the constant term.

Checked names: `KomorebiPaperVIII.polynomial_support_inclusion`, `KomorebiPaperVIII.polynomial_zero_of_no_paths`.

### 6.3 — Acyclic transfer nilpotence
Absence of paths of length h+1 forces A^(h+1)=0. Also derived from a supplied strictly increasing topological level certificate. No graph-level construction algorithm is claimed.

Checked names: `KomorebiPaperVIII.nilpotent_of_path_bound`, `KomorebiPaperVIII.nilpotent_of_topological_levels`.

### 8.1 — Packet perturbation certificate
Actual continuous linear maps and their operator norm. Source support is assumed only for errors, a weaker sufficient hypothesis. Vector and uniform operator bounds. Not an IEEE/CUDA implementation verification.

Checked names: `KomorebiPaperVIII.packet_perturbation_bound`, `KomorebiPaperVIII.packet_relative_perturbation_bound`, `KomorebiPaperVIII.packet_operator_perturbation_bound`, `KomorebiPaperVIII.contractive_packet_operator_bound`.

### 8.4 — Continuous precision allocation
Missing positive-budget hypothesis established. Existence, optimality, and uniqueness of the corrected minimizer are not formalized in this block.

Checked names: `KomorebiPaperVIII.positive_allocation_budget`, `KomorebiPaperVIII.no_positive_allocation_nonpositive_budget`, `KomorebiPaperVIII.one_edge_zero_budget_infeasible`.

## Complete remaining inventory

| Item | Result | Status |
|---|---|---|
| 2.9 | Contract conversion | not yet formalized |
| 3.1 | Dense and packet application counts | not yet formalized |
| 3.2 | Equal diagonal packets | not yet formalized |
| 3.4 | BDLR application and storage | not yet formalized |
| 3.6 | Streaming byte count | not yet formalized |
| 3.8 | Roofline lower bound | not yet formalized |
| 3.9 | Capacity threshold | not yet formalized |
| 3.10 | Materialization cost | not yet formalized |
| 4.1 | Equal block banded count | not yet formalized |
| 4.2 | Sparse plus low rank application | not yet formalized |
| 4.3 | Circulant spectral representation | not yet formalized |
| 4.4 | Toeplitz circulant embedding | not yet formalized |
| 4.5 | Kronecker modewise application | not yet formalized |
| 4.6 | Equal tensor factors | not yet formalized |
| 4.7 | Walsh Hadamard recursion | not yet formalized |
| 5.2 | Rank growth in a product chain | not yet formalized |
| 5.6 | Small core recompression | not yet formalized |
| 5.8 | Product chain perturbation | not yet formalized |
| 5.9 | Certified repeated recompression | not yet formalized |
| 6.5 | Level schedule for a triangular solve | not yet formalized |
| 6.6 | Sequential depth | not yet formalized |
| 6.7 | Inverse support lies in the transitive closure | not yet formalized |
| 6.8 | Schur support inclusion | not yet formalized |
| 7.2 | Invariant packet Krylov decomposition | not yet formalized |
| 7.3 | Approximate packet Krylov bound | not yet formalized |
| 7.4 | Block Jacobi condition bound | not yet formalized |
| 7.6 | Certified packet preconditioning | not yet formalized |
| 8.3 | Mixed precision product chain | not yet formalized |
| 8.4 | Continuous precision allocation | boundary audit only |
| 8.5 | Clipped precision allocation | not yet formalized |
| 8.7 | Exact discrete precision program | not yet formalized |
| 9.2 | Exact block discovery certificate | not yet formalized |
| 9.4 | Exact Lagrangian packet compiler | not yet formalized |
| 9.5 | Shared compilation for an operator family | not yet formalized |
| 9.6 | Monotone Lagrangian frontier | not yet formalized |
| 9.7 | Supported Pareto points | not yet formalized |
| 9.8 | Quantized budget dynamic program | not yet formalized |
| 9.9 | Pseudo polynomial complexity | not yet formalized |
| 9.11 | Compiler stability | not yet formalized |
| 9.12 | Local recompilation | not yet formalized |
| 10.2 | Launch reduction by shape | not yet formalized |
| 10.3 | Acyclic schedule depth | not yet formalized |
| 10.4 | Amortization threshold | not yet formalized |
| 10.5 | Graph replay threshold | not yet formalized |
| 10.6 | Materialization threshold | not yet formalized |
| 11.3 | Fair matching is an equivalence relation | not yet formalized |

## Classical inputs not independently formalized in this block

| Item | Standard fact |
|---|---|
| 5.5 | Eckart Young Mirsky theorem |
| 7.5 | Preconditioned conjugate gradient convergence |
| 8.2 | Floating point matrix product model |
| 9.1 | Simultaneous spectral decomposition |

## Counting and trust boundary

The five new modules contain 41 theorem declarations. The unchanged `QuantumPacketCore.lean` contains 19 reused declarations and was freshly compiled. All 60 declarations have individual axiom audits. `coordinatePackets` is one separately audited constructed object, not a theorem. Supporting lemmas and regression examples do not each count as source-paper theorems.

The run uses the ordinary Lean checker and compiled pinned Mathlib imports. It does not rebuild or independently recheck all Mathlib proofs, prove correctness of CUDA code, reproduce GPU timing measurements, or finish the remaining optimization and numerical-analysis results.
