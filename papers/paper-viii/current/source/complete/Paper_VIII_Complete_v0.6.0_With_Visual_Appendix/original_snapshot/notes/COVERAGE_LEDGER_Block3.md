# Paper VIII coverage ledger — Third checked block

**Author: Komorebi P.**

Source: strengthened manuscript dated 2026-08-14. Numbering is that of the unchanged manuscript.

**40 of 56 manuscript-proved items are checked. 16 remain not fully formalized. Four classical inputs are tracked separately.**

This is an item count, not a difficulty-weighted completion percentage. There are 197 theorem declarations across 18 modules and 12 separate construction audits.

## Complete named-item inventory

| Item | Type | Title | Lean status | Main module |
|---|---|---|---|---|
| 2.3 | theorem | Exact evaluation | checked | PacketIR |
| 2.5 | theorem | Block composition | checked | PacketIR |
| 2.6 | corollary | Adjoint and tensor semantics | checked | PacketIR |
| 2.9 | proposition | Contract conversion | checked | SchedulingContracts |
| 3.1 | theorem | Dense and packet application counts | checked | PacketCostModels |
| 3.2 | corollary | Equal diagonal packets | checked | PacketCostModels |
| 3.4 | theorem | BDLR application and storage | checked | PacketCostModels |
| 3.6 | proposition | Streaming byte count | checked | PacketCostModels |
| 3.8 | theorem | Roofline lower bound | checked | PacketCostModels |
| 3.9 | corollary | Capacity threshold | checked | PacketCostModels |
| 3.10 | proposition | Materialization cost | checked | PacketCostModels |
| 4.1 | proposition | Equal block banded count | not_yet_formalized | — |
| 4.2 | proposition | Sparse plus low rank application | checked | PacketCostModels |
| 4.3 | theorem | Circulant spectral representation | not_yet_formalized | — |
| 4.4 | corollary | Toeplitz circulant embedding | not_yet_formalized | — |
| 4.5 | theorem | Kronecker modewise application | not_yet_formalized | — |
| 4.6 | corollary | Equal tensor factors | not_yet_formalized | — |
| 4.7 | theorem | Walsh Hadamard recursion | not_yet_formalized | — |
| 5.1 | theorem | Exact BDLR product | checked | LowRankAlgebra |
| 5.2 | corollary | Rank growth in a product chain | checked | LowRankChains |
| 5.3 | theorem | Woodbury inversion | checked | LowRankAlgebra |
| 5.4 | corollary | Inverse norm bound | checked | LowRankAlgebra |
| 5.5 | standardfact | Eckart Young Mirsky theorem | external_input_not_independently_formalized | — |
| 5.6 | theorem | Small core recompression | not_yet_formalized | — |
| 5.8 | theorem | Product chain perturbation | checked | ProductChainError |
| 5.9 | theorem | Certified repeated recompression | checked | ProductChainError |
| 6.1 | theorem | Path support of powers | checked | TransferSupport |
| 6.2 | corollary | Polynomial support | checked | TransferSupport |
| 6.3 | corollary | Acyclic transfer nilpotence | checked | TransferSupport |
| 6.5 | theorem | Level schedule for a triangular solve | not_yet_formalized | — |
| 6.6 | corollary | Sequential depth | not_yet_formalized | — |
| 6.7 | theorem | Inverse support lies in the transitive closure | not_yet_formalized | — |
| 6.8 | proposition | Schur support inclusion | not_yet_formalized | — |
| 7.2 | proposition | Invariant packet Krylov decomposition | checked | KrylovPackets |
| 7.3 | theorem | Approximate packet Krylov bound | checked | KrylovPackets |
| 7.4 | theorem | Block Jacobi condition bound | not_yet_formalized | — |
| 7.5 | standardfact | Preconditioned conjugate gradient convergence | external_input_not_independently_formalized | — |
| 7.6 | corollary | Certified packet preconditioning | not_yet_formalized | — |
| 8.1 | theorem | Packet perturbation certificate | checked | PacketPerturbation |
| 8.2 | standardfact | Floating point matrix product model | external_input_not_independently_formalized | — |
| 8.3 | corollary | Mixed precision product chain | checked | ProductChainError |
| 8.4 | theorem | Continuous precision allocation | checked | ContinuousPrecision |
| 8.5 | theorem | Clipped precision allocation | not_yet_formalized | — |
| 8.7 | theorem | Exact discrete precision program | checked | DiscretePrecision |
| 9.1 | standardfact | Simultaneous spectral decomposition | external_input_not_independently_formalized | — |
| 9.2 | proposition | Exact block discovery certificate | not_yet_formalized | — |
| 9.4 | theorem | Exact Lagrangian packet compiler | checked | ExactTreeCompiler |
| 9.5 | corollary | Shared compilation for an operator family | checked | ExactTreeCompiler |
| 9.6 | proposition | Monotone Lagrangian frontier | checked | ExactTreeCompiler |
| 9.7 | corollary | Supported Pareto points | checked | ExactTreeCompiler |
| 9.8 | theorem | Quantized budget dynamic program | checked | QuantizedTreeCompiler |
| 9.9 | corollary | Pseudo polynomial complexity | checked | StoredBudgetCompiler |
| 9.11 | theorem | Compiler stability | checked | TreeCompilerUpdates |
| 9.12 | theorem | Local recompilation | checked | TreeCompilerUpdates |
| 10.2 | proposition | Launch reduction by shape | checked | SchedulingContracts |
| 10.3 | theorem | Acyclic schedule depth | not_yet_formalized | — |
| 10.4 | theorem | Amortization threshold | checked | SchedulingContracts |
| 10.5 | corollary | Graph replay threshold | checked | SchedulingContracts |
| 10.6 | corollary | Materialization threshold | checked | SchedulingContracts |
| 11.3 | proposition | Fair matching is an equivalence relation | checked | SchedulingContracts |

## Exact checked scopes and theorem witnesses

### 2.3 — Exact evaluation

Finite orthogonal idempotent family summing to one. Exact nonzero support, not thresholded support. Actual rectangular matrix batches are covered.

- `KomorebiPaperVIII.exact_active_evaluation`
- `KomorebiPaperVIII.exact_active_action`
- `KomorebiPaperVIII.exact_matrix_batch`

### 2.5 — Block composition

Finite projector family over a ring. Relational composition gives an inclusion because nonzero path terms can cancel.

- `KomorebiPaperVIII.exact_block_composition`
- `KomorebiPaperVIII.product_support_inclusion`

### 2.6 — Adjoint and tensor semantics

Adjoint identity explicitly assumes self-adjoint projectors in a star ring. Tensor identity uses actual Kronecker products of finite matrices.

- `KomorebiPaperVIII.exact_adjoint_block`
- `KomorebiPaperVIII.exact_tensor_block`

### 2.9 — Contract conversion

Formal output conversion includes the actual decoding map and its declared time. Direct downstream composition is proved. This is a contract model, not independent validation of timings.

- `KomorebiPaperVIII.contract_conversion`
- `KomorebiPaperVIII.direct_compressed_consumption`
- `KomorebiPaperVIII.omitted_decode_understates_time`

### 3.1 — Dense and packet application counts

Finite scalar address and modeled multiply-accumulate event cardinalities. Two scalar operations per coefficient/right-hand side. No device instruction claim.

- `KomorebiPaperVIII.packet_storage_count`
- `KomorebiPaperVIII.packet_application_count`
- `KomorebiPaperVIII.dense_storage_count`
- `KomorebiPaperVIII.dense_application_count`

### 3.2 — Equal diagonal packets

Equal widths, n = card(I)*b. Positive/nonzero denominators for real ratios. Work-ratio specialization follows from equal_bdlr_reduction at r=0.

- `KomorebiPaperVIII.equal_diagonal_storage`
- `KomorebiPaperVIII.equal_diagonal_work`
- `KomorebiPaperVIII.equal_block_reduction`

### 3.4 — BDLR application and storage

Explicit diagonal and two thin factor address/event types; third kernel accumulates into the diagonal result. The actual algebraic action is the unchanged LowRankAlgebra.bdlr_apply theorem.

- `KomorebiPaperVIII.bdlr_storage_count`
- `KomorebiPaperVIII.bdlr_application_count`
- `KomorebiPaperVIII.equal_bdlr_storage`
- `KomorebiPaperVIII.equal_bdlr_work`
- `KomorebiPaperVIII.equal_bdlr_reduction`

### 3.6 — Streaming byte count

One block read, one source read, target read and write per active edge, no interedge reuse. Count is of declared events.

- `KomorebiPaperVIII.streaming_value_count`
- `KomorebiPaperVIII.streaming_byte_count`

### 3.8 — Roofline lower bound

Time bound assumes positive peak rates and actual capacity inequalities. Work-rate bound assumes nonnegative work, positive bytes and elapsed time. These hypotheses are explicit.

- `KomorebiPaperVIII.roofline_time_bound`
- `KomorebiPaperVIII.roofline_work_rate`

### 3.9 — Capacity threshold

Dense scalar capacity equivalence uses n,M nonnegative and scalar byte size positive. BDLR natural-number storage inequality is exact; workspace memory is excluded.

- `KomorebiPaperVIII.dense_capacity_threshold`
- `KomorebiPaperVIII.bdlr_capacity_threshold`

### 3.10 — Materialization cost

Explicit dense low-rank product followed by one scalar addition per output has 2*n^2*r+n^2 modeled operations. The remainder has the exact quadratic bound n^2, stronger than the displayed big-O term; no generic implementation lower bound.

- `KomorebiPaperVIII.materialization_work_count`
- `KomorebiPaperVIII.materialization_quadratic_remainder`
- `KomorebiPaperVIII.dense_storage_count`

### 4.2 — Sparse plus low rank application

Counts actual sparse-value and thin-factor address types, excluding sparse index metadata. Algebraic action follows from the upstream bdlr_apply identity, which does not require its D argument to be diagonal.

- `KomorebiPaperVIII.sparse_low_rank_storage_count`
- `KomorebiPaperVIII.sparse_low_rank_work_count`

### 5.1 — Exact BDLR product

Finite rectangular factors over a field with involution. Diagonal closure and actual correction rank are proved. No materialization or timing claim.

- `KomorebiPaperVIII.packet_diagonal_product`
- `KomorebiPaperVIII.bdlr_product`
- `KomorebiPaperVIII.bdlr_product_rank_bound`

### 5.2 — Rank growth in a product chain

Actual variable-rank thin matrix factors are constructed for every length, including zero rank and the empty product. The correction matrix rank is bounded by the sum of factor widths. Packet diagonality of the base product is derived.

- `KomorebiPaperVIII.chainFactors_correct`
- `KomorebiPaperVIII.bdlr_chain_rank_bound`
- `KomorebiPaperVIII.packet_diagonal_chain`

### 5.3 — Woodbury inversion

Both D and I+V* D^{-1} U are units. The update is proved invertible. Ordinary matrix inverse and arbitrary right-hand-side batches. Uses Mathlib classical Woodbury identity.

- `KomorebiPaperVIII.bdlr_woodbury`
- `KomorebiPaperVIII.bdlr_update_isUnit`
- `KomorebiPaperVIII.bdlr_woodbury_solve`

### 5.4 — Inverse norm bound

Real or complex matrices with the Hilbert-space L2 operator norm, including rectangular factors. Same two invertibility assumptions as 5.3.

- `KomorebiPaperVIII.bdlr_inverse_norm_bound`

### 5.8 — Product chain perturbation

Actual ordered products in a normed ring with norm-one identity. Includes the empty chain. The displayed finite sum uses perturbed suffix norms and exact prefix norms. This covers operators on nonzero normed spaces, without a commutativity assumption.

- `KomorebiPaperVIII.product_chain_perturbation`
- `KomorebiPaperVIII.product_chain_error_bound`

### 5.9 — Certified repeated recompression

Actual left-multiplied iterates with additive post-product residuals in a normed ring. Both actual residual norms and arbitrary certified error budgets are supported, including the empty iteration.

- `KomorebiPaperVIII.repeated_recompression_bound`
- `KomorebiPaperVIII.repeated_recompression_actual_error`

### 6.1 — Path support of powers

Recursive finite sum over active paths equals the actual block of A^n. Includes length zero explicitly.

- `KomorebiPaperVIII.power_path_expansion`
- `KomorebiPaperVIII.power_block_zero_of_no_path`
- `KomorebiPaperVIII.power_support_inclusion`

### 6.2 — Polynomial support

Actual finite polynomial sum in an algebra. Support contained in the union over powers, including the constant term.

- `KomorebiPaperVIII.polynomial_support_inclusion`
- `KomorebiPaperVIII.polynomial_zero_of_no_paths`

### 6.3 — Acyclic transfer nilpotence

Absence of paths of length h+1 forces A^(h+1)=0. Also derived from a supplied strictly increasing topological level certificate. No graph-level construction algorithm is claimed.

- `KomorebiPaperVIII.nilpotent_of_path_bound`
- `KomorebiPaperVIII.nilpotent_of_topological_levels`

### 7.2 — Invariant packet Krylov decomposition

Actual bounded linear maps and spans of finite power orbits. Commutation with the complete finite projector family gives the power expansion and Krylov inclusion. Local spaces lie in the actual projector ranges and their sum is direct. No equality of the global and local Krylov spaces is asserted.

- `KomorebiPaperVIII.invariant_packet_power_expansion`
- `KomorebiPaperVIII.invariant_packet_krylov`
- `KomorebiPaperVIII.local_krylov_direct`

### 7.3 — Approximate packet Krylov bound

Positive integer power, actual operator norm, and actual Metric.infDist to the sum of local Krylov spaces. Membership of the comparison vector D^j v is derived from packet diagonality. The power estimate also allows a trivial normed ring.

- `KomorebiPaperVIII.approximate_packet_power_bound`
- `KomorebiPaperVIII.approximate_packet_krylov_distance`

### 8.1 — Packet perturbation certificate

Actual continuous linear maps and their operator norm. Source support is assumed only for errors, a weaker sufficient hypothesis. Vector and uniform operator bounds. Not an IEEE/CUDA implementation verification.

- `KomorebiPaperVIII.packet_perturbation_bound`
- `KomorebiPaperVIII.packet_relative_perturbation_bound`
- `KomorebiPaperVIII.packet_operator_perturbation_bound`
- `KomorebiPaperVIII.contractive_packet_operator_bound`

### 8.3 — Mixed precision product chain

Stagewise packet bounds are uniform operator-norm certificates on a nonzero normed space, not vector-specific bounds reused as operator norms. The exact-product perturbation theorem propagates those certificates. Vector error follows by multiplying the operator bound by the input norm.

- `KomorebiPaperVIII.mixed_precision_product_chain`
- `KomorebiPaperVIII.chain_action_error`

### 8.4 — Continuous precision allocation

Finite nonempty edge set, strictly positive sensitivities, costs, and budget. Actual sum c*log(1/eps). Feasibility, global optimality, strict inequality away from formula, and unique minimizer. No KKT or convexity result is assumed.

- `KomorebiPaperVIII.optimal_tolerance_feasible`
- `KomorebiPaperVIII.precision_allocation_optimal`
- `KomorebiPaperVIII.precision_allocation_strict`
- `KomorebiPaperVIII.continuous_precision_unique_minimizer`

### 8.7 — Exact discrete precision program

Independent legal assignments choose one listed option per edge. Nonnegative integer weights and exact ordered-field costs. Exact-weight states plus the final budget scan give the optimum with attainment or exact infeasibility. The residual-budget subtraction is guarded. StoredBudgetCompiler proves the actual array-backed implementation equal to this specification.

- `KomorebiPaperVIII.BudgetDP.discrete_precision_program`
- `KomorebiPaperVIII.BudgetDP.discreteBudget_some_iff`
- `KomorebiPaperVIII.BudgetDP.discreteBudget_none_iff`
- `KomorebiPaperVIII.BudgetDP.storedDiscreteBudget_correct`

### 9.4 — Exact Lagrangian packet compiler

Arbitrary finite branching rooted trees, independent inductively defined cuts. Returned cut attains the recurrence and beats every legal cut. Generic ordered field covers rationals and reals. No universal discovery/approximation claim.

- `KomorebiPaperVIII.CandidateTree.exact_tree_compiler`
- `KomorebiPaperVIII.CandidateTree.compile_attains`
- `KomorebiPaperVIII.CandidateTree.exact_lagrangian_compiler`

### 9.5 — Shared compilation for an operator family

Exact weighted family aggregation at pruning level including setup and split overhead. Proved even without sign restrictions; intended application uses nonnegative weights.

- `KomorebiPaperVIII.CandidateTree.cutValue_weighted_family`
- `KomorebiPaperVIII.CandidateTree.shared_family_compiler`

### 9.6 — Monotone Lagrangian frontier

Any two optimal cuts, 0 <= lambda1 < lambda2; error nonincreasing and cost nondecreasing. Optimality is discharged by the constructive compiler theorem for its returned cuts.

- `KomorebiPaperVIII.CandidateTree.monotone_lagrangian_frontier`

### 9.7 — Supported Pareto points

Positive scalarization parameter. Every true optimum is undominated. TreeCompilerUpdates.unsupported_pareto_example supplies the rational three-point unsupported-frontier inequality. Quantized-budget compiler remains unformalized.

- `KomorebiPaperVIII.CandidateTree.positive_lagrangian_pareto`

### 9.8 — Quantized budget dynamic program

The actual candidate tree and independent Cut type from the previous block, with arbitrary nonempty finite branching. Min-plus convolution over integer weights proves lower bounds, attainment, and infeasibility. StoredBudgetCompiler certifies the actual cached array-backed output. The implementation returns the minimum cost, not a backtracked cut.

- `KomorebiPaperVIII.CandidateTree.budgetTable_correct`
- `KomorebiPaperVIII.CandidateTree.quantized_budget_compiler`
- `KomorebiPaperVIII.CandidateTree.compileBudget_some_iff`
- `KomorebiPaperVIII.CandidateTree.compileBudget_none_iff`
- `KomorebiPaperVIII.CandidateTree.storedBudget_minimum`

### 9.9 — Pseudo polynomial complexity

Array-backed tables cache child results. Concrete convolution candidate indices have at most (B+1)^2 elements. The declared unit-cost tabulation model is bounded by nodeCount*(3*(B+1)+(B+1)^2). Root minimum scan is an additional linear pass. This is pseudo-polynomial in numeric B and does not count exact-arithmetic bit complexity, compiler internals, or hardware instructions.

- `KomorebiPaperVIII.CandidateTree.merge_trial_count`
- `KomorebiPaperVIII.CandidateTree.merge_trial_bound`
- `KomorebiPaperVIII.CandidateTree.tabulation_pseudopolynomial`

### 9.11 — Compiler stability

Actual solved keep/split scores satisfy strict half-gap inequalities at every internal node. Entire returned cut is unchanged. Ties cannot satisfy these strict hypotheses; no robustness at ties is claimed.

- `KomorebiPaperVIII.CandidateTree.half_gap_order`
- `KomorebiPaperVIII.CandidateTree.compiler_stability`

### 9.12 — Local recompilation

Explicit one-hole context with cached sibling values. Replacing a subtree models localized data changes. Cache validity is constructed by refresh, not the new optimum. updateValue reads only new subtree score and caches on ancestor frames. Exact new global optimum and attaining cut proved.

- `KomorebiPaperVIII.CandidateTree.CachedContext.refresh_valid`
- `KomorebiPaperVIII.CandidateTree.CachedContext.updateValue_correct`
- `KomorebiPaperVIII.CandidateTree.CachedContext.sibling_tree_unchanged`
- `KomorebiPaperVIII.CandidateTree.CachedContext.sibling_value_unchanged`
- `KomorebiPaperVIII.CandidateTree.CachedContext.local_recompilation`

### 10.2 — Launch reduction by shape

Finite grouping by complete shape signature, partition/fiberwise sum equals original output and work. One launch per active class is a backend capability assumption, not verified CUDA code.

- `KomorebiPaperVIII.shape_launch_count`
- `KomorebiPaperVIII.grouped_execution_output`
- `KomorebiPaperVIII.grouped_execution_work`

### 10.4 — Amortization threshold

Actual declared setup+R*candidate vs R*baseline inequality. Positive per-use advantage; setup nonnegative for smallest natural reuse floor+1. Equality is break-even, not profitability.

- `KomorebiPaperVIII.amortization_threshold`
- `KomorebiPaperVIII.no_amortization`
- `KomorebiPaperVIII.integer_amortization_threshold`
- `KomorebiPaperVIII.minimum_reuse_attains`

### 10.5 — Graph replay threshold

Capture plus repeated replay vs repeated ordinary execution under replay<ordinary. Pure timing-model identity, not new GPU data.

- `KomorebiPaperVIII.graph_replay_threshold`

### 10.6 — Materialization threshold

Nonnegative materialization cost and reuse count. Strict profitability iff explicit per-use time is lower and reuse exceeds the ratio.

- `KomorebiPaperVIII.materialization_threshold`

### 11.3 — Fair matching is an equivalence relation

Equality of complete case, output, correctness reference, and timing-scope metadata. No inference of actual timing accuracy from matching metadata.

- `KomorebiPaperVIII.fair_match_iff_eq`
- `KomorebiPaperVIII.fair_matching_equivalence`

## Remaining items

4.1 — Equal block banded count.
4.3 — Circulant spectral representation.
4.4 — Toeplitz circulant embedding.
4.5 — Kronecker modewise application.
4.6 — Equal tensor factors.
4.7 — Walsh Hadamard recursion.
5.6 — Small core recompression.
6.5 — Level schedule for a triangular solve.
6.6 — Sequential depth.
6.7 — Inverse support lies in the transitive closure.
6.8 — Schur support inclusion.
7.4 — Block Jacobi condition bound.
7.6 — Certified packet preconditioning.
8.5 — Clipped precision allocation.
9.2 — Exact block discovery certificate.
10.3 — Acyclic schedule depth.
