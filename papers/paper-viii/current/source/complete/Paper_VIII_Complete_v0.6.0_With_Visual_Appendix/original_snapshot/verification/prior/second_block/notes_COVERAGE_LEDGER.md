# Paper VIII: Second Lean Block Coverage Ledger

**Author: Komorebi P.**

Source: *Packet Operator Algorithms, Exact Compilation, and GPU Realization*, strengthened edition dated August 14, 2026. The manuscript, its source package, and six upstream proof files are unchanged.

**31 of 56 named manuscript-proved results are covered. 25 remain not fully formalized. Four classical inputs remain separate.**

This block adds 69 theorem declarations in five modules. The cumulative 11 modules contain 129 theorem declarations, including 19 unchanged declarations imported from Paper VII. Five construction audits are additional, not theorem declarations. All cumulative sources were recompiled.

## Completed inventory

| Item | Result | Module | Block |
|---|---|---|---|
| 2.3 | Exact evaluation | `PacketIR` | First |
| 2.5 | Block composition | `PacketIR` | First |
| 2.6 | Adjoint and tensor semantics | `PacketIR` | First |
| 2.9 | Contract conversion | `SchedulingContracts` | Second |
| 3.1 | Dense and packet application counts | `PacketCostModels` | Second |
| 3.2 | Equal diagonal packets | `PacketCostModels` | Second |
| 3.4 | BDLR application and storage | `PacketCostModels` | Second |
| 3.6 | Streaming byte count | `PacketCostModels` | Second |
| 3.8 | Roofline lower bound | `PacketCostModels` | Second |
| 3.9 | Capacity threshold | `PacketCostModels` | Second |
| 3.10 | Materialization cost | `PacketCostModels` | Second |
| 4.2 | Sparse plus low rank application | `PacketCostModels` | Second |
| 5.1 | Exact BDLR product | `LowRankAlgebra` | First |
| 5.3 | Woodbury inversion | `LowRankAlgebra` | First |
| 5.4 | Inverse norm bound | `LowRankAlgebra` | First |
| 6.1 | Path support of powers | `TransferSupport` | First |
| 6.2 | Polynomial support | `TransferSupport` | First |
| 6.3 | Acyclic transfer nilpotence | `TransferSupport` | First |
| 8.1 | Packet perturbation certificate | `PacketPerturbation` | First |
| 8.4 | Continuous precision allocation | `ContinuousPrecision` | Second |
| 9.4 | Exact Lagrangian packet compiler | `ExactTreeCompiler` | Second |
| 9.5 | Shared compilation for an operator family | `ExactTreeCompiler` | Second |
| 9.6 | Monotone Lagrangian frontier | `ExactTreeCompiler` | Second |
| 9.7 | Supported Pareto points | `ExactTreeCompiler` | Second |
| 9.11 | Compiler stability | `TreeCompilerUpdates` | Second |
| 9.12 | Local recompilation | `TreeCompilerUpdates` | Second |
| 10.2 | Launch reduction by shape | `SchedulingContracts` | Second |
| 10.4 | Amortization threshold | `SchedulingContracts` | Second |
| 10.5 | Graph replay threshold | `SchedulingContracts` | Second |
| 10.6 | Materialization threshold | `SchedulingContracts` | Second |
| 11.3 | Fair matching is an equivalence relation | `SchedulingContracts` | Second |

## Exact hypotheses and theorem map

### 2.3 — Exact evaluation

Finite orthogonal idempotent family summing to one. Exact nonzero support, not thresholded support. Actual rectangular matrix batches are covered.

Checked names: `KomorebiPaperVIII.exact_active_evaluation`, `KomorebiPaperVIII.exact_active_action`, `KomorebiPaperVIII.exact_matrix_batch`.

### 2.5 — Block composition

Finite projector family over a ring. Relational composition gives an inclusion because nonzero path terms can cancel.

Checked names: `KomorebiPaperVIII.exact_block_composition`, `KomorebiPaperVIII.product_support_inclusion`.

### 2.6 — Adjoint and tensor semantics

Adjoint identity explicitly assumes self-adjoint projectors in a star ring. Tensor identity uses actual Kronecker products of finite matrices.

Checked names: `KomorebiPaperVIII.exact_adjoint_block`, `KomorebiPaperVIII.exact_tensor_block`.

### 2.9 — Contract conversion

Formal output conversion includes the actual decoding map and its declared time. Direct downstream composition is proved. This is a contract model, not independent validation of timings.

Checked names: `KomorebiPaperVIII.contract_conversion`, `KomorebiPaperVIII.direct_compressed_consumption`, `KomorebiPaperVIII.omitted_decode_understates_time`.

### 3.1 — Dense and packet application counts

Finite scalar address and modeled multiply-accumulate event cardinalities. Two scalar operations per coefficient/right-hand side. No device instruction claim.

Checked names: `KomorebiPaperVIII.packet_storage_count`, `KomorebiPaperVIII.packet_application_count`, `KomorebiPaperVIII.dense_storage_count`, `KomorebiPaperVIII.dense_application_count`.

### 3.2 — Equal diagonal packets

Equal widths, n = card(I)*b. Positive/nonzero denominators for real ratios. Work-ratio specialization follows from equal_bdlr_reduction at r=0.

Checked names: `KomorebiPaperVIII.equal_diagonal_storage`, `KomorebiPaperVIII.equal_diagonal_work`, `KomorebiPaperVIII.equal_block_reduction`.

### 3.4 — BDLR application and storage

Explicit diagonal and two thin factor address/event types; third kernel accumulates into the diagonal result. The actual algebraic action is the unchanged LowRankAlgebra.bdlr_apply theorem.

Checked names: `KomorebiPaperVIII.bdlr_storage_count`, `KomorebiPaperVIII.bdlr_application_count`, `KomorebiPaperVIII.equal_bdlr_storage`, `KomorebiPaperVIII.equal_bdlr_work`, `KomorebiPaperVIII.equal_bdlr_reduction`.

### 3.6 — Streaming byte count

One block read, one source read, target read and write per active edge, no interedge reuse. Count is of declared events.

Checked names: `KomorebiPaperVIII.streaming_value_count`, `KomorebiPaperVIII.streaming_byte_count`.

### 3.8 — Roofline lower bound

Time bound assumes positive peak rates and actual capacity inequalities. Work-rate bound assumes nonnegative work, positive bytes and elapsed time. These hypotheses are explicit.

Checked names: `KomorebiPaperVIII.roofline_time_bound`, `KomorebiPaperVIII.roofline_work_rate`.

### 3.9 — Capacity threshold

Dense scalar capacity equivalence uses n,M nonnegative and scalar byte size positive. BDLR natural-number storage inequality is exact; workspace memory is excluded.

Checked names: `KomorebiPaperVIII.dense_capacity_threshold`, `KomorebiPaperVIII.bdlr_capacity_threshold`.

### 3.10 — Materialization cost

Explicit dense low-rank product followed by one scalar addition per output has 2*n^2*r+n^2 modeled operations. The remainder has the exact quadratic bound n^2, stronger than the displayed big-O term; no generic implementation lower bound.

Checked names: `KomorebiPaperVIII.materialization_work_count`, `KomorebiPaperVIII.materialization_quadratic_remainder`, `KomorebiPaperVIII.dense_storage_count`.

### 4.2 — Sparse plus low rank application

Counts actual sparse-value and thin-factor address types, excluding sparse index metadata. Algebraic action follows from the upstream bdlr_apply identity, which does not require its D argument to be diagonal.

Checked names: `KomorebiPaperVIII.sparse_low_rank_storage_count`, `KomorebiPaperVIII.sparse_low_rank_work_count`.

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

Finite nonempty edge set, strictly positive sensitivities, costs, and budget. Actual sum c*log(1/eps). Feasibility, global optimality, strict inequality away from formula, and unique minimizer. No KKT or convexity result is assumed.

Checked names: `KomorebiPaperVIII.optimal_tolerance_feasible`, `KomorebiPaperVIII.precision_allocation_optimal`, `KomorebiPaperVIII.precision_allocation_strict`, `KomorebiPaperVIII.continuous_precision_unique_minimizer`.

### 9.4 — Exact Lagrangian packet compiler

Arbitrary finite branching rooted trees, independent inductively defined cuts. Returned cut attains the recurrence and beats every legal cut. Generic ordered field covers rationals and reals. No universal discovery/approximation claim.

Checked names: `KomorebiPaperVIII.CandidateTree.exact_tree_compiler`, `KomorebiPaperVIII.CandidateTree.compile_attains`, `KomorebiPaperVIII.CandidateTree.exact_lagrangian_compiler`.

### 9.5 — Shared compilation for an operator family

Exact weighted family aggregation at pruning level including setup and split overhead. Proved even without sign restrictions; intended application uses nonnegative weights.

Checked names: `KomorebiPaperVIII.CandidateTree.cutValue_weighted_family`, `KomorebiPaperVIII.CandidateTree.shared_family_compiler`.

### 9.6 — Monotone Lagrangian frontier

Any two optimal cuts, 0 <= lambda1 < lambda2; error nonincreasing and cost nondecreasing. Optimality is discharged by the constructive compiler theorem for its returned cuts.

Checked names: `KomorebiPaperVIII.CandidateTree.monotone_lagrangian_frontier`.

### 9.7 — Supported Pareto points

Positive scalarization parameter. Every true optimum is undominated. TreeCompilerUpdates.unsupported_pareto_example supplies the rational three-point unsupported-frontier inequality. Quantized-budget compiler remains unformalized.

Checked names: `KomorebiPaperVIII.CandidateTree.positive_lagrangian_pareto`.

### 9.11 — Compiler stability

Actual solved keep/split scores satisfy strict half-gap inequalities at every internal node. Entire returned cut is unchanged. Ties cannot satisfy these strict hypotheses; no robustness at ties is claimed.

Checked names: `KomorebiPaperVIII.CandidateTree.half_gap_order`, `KomorebiPaperVIII.CandidateTree.compiler_stability`.

### 9.12 — Local recompilation

Explicit one-hole context with cached sibling values. Replacing a subtree models localized data changes. Cache validity is constructed by refresh, not the new optimum. updateValue reads only new subtree score and caches on ancestor frames. Exact new global optimum and attaining cut proved.

Checked names: `KomorebiPaperVIII.CandidateTree.CachedContext.refresh_valid`, `KomorebiPaperVIII.CandidateTree.CachedContext.updateValue_correct`, `KomorebiPaperVIII.CandidateTree.CachedContext.sibling_tree_unchanged`, `KomorebiPaperVIII.CandidateTree.CachedContext.sibling_value_unchanged`, `KomorebiPaperVIII.CandidateTree.CachedContext.local_recompilation`.

### 10.2 — Launch reduction by shape

Finite grouping by complete shape signature, partition/fiberwise sum equals original output and work. One launch per active class is a backend capability assumption, not verified CUDA code.

Checked names: `KomorebiPaperVIII.shape_launch_count`, `KomorebiPaperVIII.grouped_execution_output`, `KomorebiPaperVIII.grouped_execution_work`.

### 10.4 — Amortization threshold

Actual declared setup+R*candidate vs R*baseline inequality. Positive per-use advantage; setup nonnegative for smallest natural reuse floor+1. Equality is break-even, not profitability.

Checked names: `KomorebiPaperVIII.amortization_threshold`, `KomorebiPaperVIII.no_amortization`, `KomorebiPaperVIII.integer_amortization_threshold`, `KomorebiPaperVIII.minimum_reuse_attains`.

### 10.5 — Graph replay threshold

Capture plus repeated replay vs repeated ordinary execution under replay<ordinary. Pure timing-model identity, not new GPU data.

Checked names: `KomorebiPaperVIII.graph_replay_threshold`.

### 10.6 — Materialization threshold

Nonnegative materialization cost and reuse count. Strict profitability iff explicit per-use time is lower and reuse exceeds the ratio.

Checked names: `KomorebiPaperVIII.materialization_threshold`.

### 11.3 — Fair matching is an equivalence relation

Equality of complete case, output, correctness reference, and timing-scope metadata. No inference of actual timing accuracy from matching metadata.

Checked names: `KomorebiPaperVIII.fair_match_iff_eq`, `KomorebiPaperVIII.fair_matching_equivalence`.

## Remaining proved-item inventory

| Item | Result | Lean status |
|---|---|---|
| 4.1 | Equal block banded count | Not yet fully formalized |
| 4.3 | Circulant spectral representation | Not yet fully formalized |
| 4.4 | Toeplitz circulant embedding | Not yet fully formalized |
| 4.5 | Kronecker modewise application | Not yet fully formalized |
| 4.6 | Equal tensor factors | Not yet fully formalized |
| 4.7 | Walsh Hadamard recursion | Not yet fully formalized |
| 5.2 | Rank growth in a product chain | Not yet fully formalized |
| 5.6 | Small core recompression | Not yet fully formalized |
| 5.8 | Product chain perturbation | Not yet fully formalized |
| 5.9 | Certified repeated recompression | Not yet fully formalized |
| 6.5 | Level schedule for a triangular solve | Not yet fully formalized |
| 6.6 | Sequential depth | Not yet fully formalized |
| 6.7 | Inverse support lies in the transitive closure | Not yet fully formalized |
| 6.8 | Schur support inclusion | Not yet fully formalized |
| 7.2 | Invariant packet Krylov decomposition | Not yet fully formalized |
| 7.3 | Approximate packet Krylov bound | Not yet fully formalized |
| 7.4 | Block Jacobi condition bound | Not yet fully formalized |
| 7.6 | Certified packet preconditioning | Not yet fully formalized |
| 8.3 | Mixed precision product chain | Not yet fully formalized |
| 8.5 | Clipped precision allocation | Not yet fully formalized |
| 8.7 | Exact discrete precision program | Not yet fully formalized |
| 9.2 | Exact block discovery certificate | Not yet fully formalized |
| 9.8 | Quantized budget dynamic program | Not yet fully formalized |
| 9.9 | Pseudo polynomial complexity | Not yet fully formalized |
| 10.3 | Acyclic schedule depth | Not yet fully formalized |

## Separate classical inputs

| Item | Standard fact |
|---|---|
| 5.5 | Eckart Young Mirsky theorem |
| 7.5 | Preconditioned conjugate gradient convergence |
| 8.2 | Floating point matrix product model |
| 9.1 | Simultaneous spectral decomposition |

## Interpretation boundaries

The tree recurrence optimizes only finite candidate trees with additive local scores. It does not discover a universally optimal representation. The returned-cut wrapper is proved correct, but its implementation complexity is not claimed; it can recompute subtree scores during cut construction. The cached ancestor update reads precomputed sibling values and has its own correctness theorem.

Continuous allocation is a real-valued mathematical optimizer, not an executable IEEE precision-selection routine. Its strictly positive budget and nonempty edge set are explicit. Clipped allocation and both quantized-budget programs remain unformalized.

Count theorems use concrete finite address/event types under the stated model. They do not certify GPU instruction counts, launch APIs, timing accuracy, cache behavior, or correctness of a CUDA backend. The contract comparison results formalize a declared protocol, not an independent measurement audit.

The exact-rational executable suite checks 600 compiler cases against 85,320 exhaustively enumerated pruning scores, plus 600 cached updates against full recomputation. These are tests, not additional theorem declarations. The original 37,392-check CPU numerical suite was not rerun in this block. No GPU benchmarks, prior full papers, or all imported Mathlib proofs were rechecked.
