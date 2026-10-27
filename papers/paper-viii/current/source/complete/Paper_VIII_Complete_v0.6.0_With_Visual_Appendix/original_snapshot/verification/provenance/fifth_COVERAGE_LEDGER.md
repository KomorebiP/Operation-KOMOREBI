# Paper VIII formal coverage ledger

**Author: Komorebi P.**

Release v0.5.0. 55 of 56 manuscript-proved entries are covered. Four classical inputs are tracked separately. Source theorem-to-Lean correspondence is a manual mathematical review, not an automatic semantic-equivalence theorem.

## 2.3 — Exact evaluation

**checked**

Finite orthogonal idempotent family summing to one. Exact nonzero support, not thresholded support. Actual rectangular matrix batches are covered.

Targets: `KomorebiPaperVIII.exact_active_evaluation`, `KomorebiPaperVIII.exact_active_action`, `KomorebiPaperVIII.exact_matrix_batch`.

## 2.5 — Block composition

**checked**

Finite projector family over a ring. Relational composition gives an inclusion because nonzero path terms can cancel.

Targets: `KomorebiPaperVIII.exact_block_composition`, `KomorebiPaperVIII.product_support_inclusion`.

## 2.6 — Adjoint and tensor semantics

**checked**

Adjoint identity explicitly assumes self-adjoint projectors in a star ring. Tensor identity uses actual Kronecker products of finite matrices.

Targets: `KomorebiPaperVIII.exact_adjoint_block`, `KomorebiPaperVIII.exact_tensor_block`.

## 2.9 — Contract conversion

**checked**

Formal output conversion includes the actual decoding map and its declared time. Direct downstream composition is proved. This is a contract model, not independent validation of timings.

Targets: `KomorebiPaperVIII.contract_conversion`, `KomorebiPaperVIII.direct_compressed_consumption`, `KomorebiPaperVIII.omitted_decode_understates_time`.

## 3.1 — Dense and packet application counts

**checked**

Finite scalar address and modeled multiply-accumulate event cardinalities. Two scalar operations per coefficient/right-hand side. No device instruction claim.

Targets: `KomorebiPaperVIII.packet_storage_count`, `KomorebiPaperVIII.packet_application_count`, `KomorebiPaperVIII.dense_storage_count`, `KomorebiPaperVIII.dense_application_count`.

## 3.2 — Equal diagonal packets

**checked**

Equal widths, n = card(I)*b. Positive/nonzero denominators for real ratios. Work-ratio specialization follows from equal_bdlr_reduction at r=0.

Targets: `KomorebiPaperVIII.equal_diagonal_storage`, `KomorebiPaperVIII.equal_diagonal_work`, `KomorebiPaperVIII.equal_block_reduction`.

## 3.4 — BDLR application and storage

**checked**

Explicit diagonal and two thin factor address/event types; third kernel accumulates into the diagonal result. The actual algebraic action is the unchanged LowRankAlgebra.bdlr_apply theorem.

Targets: `KomorebiPaperVIII.bdlr_storage_count`, `KomorebiPaperVIII.bdlr_application_count`, `KomorebiPaperVIII.equal_bdlr_storage`, `KomorebiPaperVIII.equal_bdlr_work`, `KomorebiPaperVIII.equal_bdlr_reduction`.

## 3.6 — Streaming byte count

**checked**

One block read, one source read, target read and write per active edge, no interedge reuse. Count is of declared events.

Targets: `KomorebiPaperVIII.streaming_value_count`, `KomorebiPaperVIII.streaming_byte_count`.

## 3.8 — Roofline lower bound

**checked**

Time bound assumes positive peak rates and actual capacity inequalities. Work-rate bound assumes nonnegative work, positive bytes and elapsed time. These hypotheses are explicit.

Targets: `KomorebiPaperVIII.roofline_time_bound`, `KomorebiPaperVIII.roofline_work_rate`.

## 3.9 — Capacity threshold

**checked**

Dense scalar capacity equivalence uses n,M nonnegative and scalar byte size positive. BDLR natural-number storage inequality is exact; workspace memory is excluded.

Targets: `KomorebiPaperVIII.dense_capacity_threshold`, `KomorebiPaperVIII.bdlr_capacity_threshold`.

## 3.10 — Materialization cost

**checked**

Explicit dense low-rank product followed by one scalar addition per output has 2*n^2*r+n^2 modeled operations. The remainder has the exact quadratic bound n^2, stronger than the displayed big-O term; no generic implementation lower bound.

Targets: `KomorebiPaperVIII.materialization_work_count`, `KomorebiPaperVIII.materialization_quadratic_remainder`, `KomorebiPaperVIII.dense_storage_count`.

## 4.1 — Equal block banded count

**checked**

Actual band address subtype in Fin p x Fin p. Count p*(2*w+1)-w*(w+1) proved from finite sums under w<p. Explicit stored-scalar and multiply/accumulate event types give b^2*N and 2*q*b^2*N. The manuscript substitution p=n/b additionally needs b>0 and exact divisibility. No hardware operation timing claim.

Targets: `KomorebiPaperVIII.banded_block_count`, `KomorebiPaperVIII.banded_storage_count`, `KomorebiPaperVIII.banded_operation_count`.

## 4.2 — Sparse plus low rank application

**checked**

Counts actual sparse-value and thin-factor address types, excluding sparse index metadata. Algebraic action follows from the upstream bdlr_apply identity, which does not require its D argument to be diagonal.

Targets: `KomorebiPaperVIII.sparse_low_rank_storage_count`, `KomorebiPaperVIII.sparse_low_rank_work_count`.

## 4.3 — Circulant spectral representation

**checked**

Actual circulant and unitary-normalized Fourier matrix on ZMod n for every n>0. The exponential formula, both unitarity identities, exact diagonalization and two-transform application are checked. No FFT complexity or hardware execution is claimed.

Targets: `KomorebiPaperVIII.fourier_matrix_exponential`, `KomorebiPaperVIII.fourier_unitary`, `KomorebiPaperVIII.circulant_spectral_representation`, `KomorebiPaperVIII.circulant_fourier_application`.

## 4.4 — Toeplitz circulant embedding

**checked**

Actual complex Toeplitz matrix, explicitly reversed generator of length n+n and Fin.addCases zero padding for n>0. The diagonal uses c[0]; r[0] is irrelevant. Neither symmetry nor Hermiticity is assumed.

Targets: `KomorebiPaperVIII.toeplitz_circulant_block`, `KomorebiPaperVIII.toeplitz_embedding_action`, `KomorebiPaperVIII.toeplitz_generator_first_half`, `KomorebiPaperVIII.toeplitz_generator_middle`.

## 4.5 — Kronecker modewise application

**checked**

Actual column-major Matrix.vec and actual Kronecker products; the right factor uses transpose, not adjoint. Arithmetic and factor-storage counts are cardinalities of finite address/event types.

Targets: `KomorebiPaperVIII.kronecker_modewise`, `KomorebiPaperVIII.kronecker_modewise_work`, `KomorebiPaperVIII.kronecker_factor_storage`.

## 4.6 — Equal tensor factors

**checked**

Actual arbitrary-length recursive tensor matrix and slice-by-slice contraction. Exact event count 2*k*d^(k+1) and storage k*d^2; includes k=0 and d=0. Model charges two operations per multiply-accumulate.

Targets: `KomorebiPaperVIII.tensor_dimension`, `KomorebiPaperVIII.tensor_apply_correct`, `KomorebiPaperVIII.tensor_modewise_work`, `KomorebiPaperVIII.tensor_factor_storage`.

## 4.7 — Walsh Hadamard recursion

**checked**

Recursively constructed complex Walsh matrices and actual sum/difference butterfly. Proves ordinary-transpose orthogonality, algorithm correctness and exactly N*log2(N) additions/subtractions for N=2^k, including N=1.

Targets: `KomorebiPaperVIII.walsh_orthogonal`, `KomorebiPaperVIII.walsh_apply_correct`, `KomorebiPaperVIII.walsh_operation_count`, `KomorebiPaperVIII.walsh_log_operation_count`.

## 5.1 — Exact BDLR product

**checked**

Finite rectangular factors over a field with involution. Diagonal closure and actual correction rank are proved. No materialization or timing claim.

Targets: `KomorebiPaperVIII.packet_diagonal_product`, `KomorebiPaperVIII.bdlr_product`, `KomorebiPaperVIII.bdlr_product_rank_bound`.

## 5.2 — Rank growth in a product chain

**checked**

Actual variable-rank thin matrix factors are constructed for every length, including zero rank and the empty product. The correction matrix rank is bounded by the sum of factor widths. Packet diagonality of the base product is derived.

Targets: `KomorebiPaperVIII.chainFactors_correct`, `KomorebiPaperVIII.bdlr_chain_rank_bound`, `KomorebiPaperVIII.packet_diagonal_chain`.

## 5.3 — Woodbury inversion

**checked**

Both D and I+V* D^{-1} U are units. The update is proved invertible. Ordinary matrix inverse and arbitrary right-hand-side batches. Uses Mathlib classical Woodbury identity.

Targets: `KomorebiPaperVIII.bdlr_woodbury`, `KomorebiPaperVIII.bdlr_update_isUnit`, `KomorebiPaperVIII.bdlr_woodbury_solve`.

## 5.4 — Inverse norm bound

**checked**

Real or complex matrices with the Hilbert-space L2 operator norm, including rectangular factors. Same two invertibility assumptions as 5.3.

Targets: `KomorebiPaperVIII.bdlr_inverse_norm_bound`.

## 5.5 — Eckart Young Mirsky theorem

**external_input_not_independently_formalized**

Classical input is external; not independently formalized here.

## 5.6 — Small core recompression

**not_yet_formalized**

Remaining formalization target.

## 5.8 — Product chain perturbation

**checked**

Actual ordered products in a normed ring with norm-one identity. Includes the empty chain. The displayed finite sum uses perturbed suffix norms and exact prefix norms. This covers operators on nonzero normed spaces, without a commutativity assumption.

Targets: `KomorebiPaperVIII.product_chain_perturbation`, `KomorebiPaperVIII.product_chain_error_bound`.

## 5.9 — Certified repeated recompression

**checked**

Actual left-multiplied iterates with additive post-product residuals in a normed ring. Both actual residual norms and arbitrary certified error budgets are supported, including the empty iteration.

Targets: `KomorebiPaperVIII.repeated_recompression_bound`, `KomorebiPaperVIII.repeated_recompression_actual_error`.

## 6.1 — Path support of powers

**checked**

Recursive finite sum over active paths equals the actual block of A^n. Includes length zero explicitly.

Targets: `KomorebiPaperVIII.power_path_expansion`, `KomorebiPaperVIII.power_block_zero_of_no_path`, `KomorebiPaperVIII.power_support_inclusion`.

## 6.2 — Polynomial support

**checked**

Actual finite polynomial sum in an algebra. Support contained in the union over powers, including the constant term.

Targets: `KomorebiPaperVIII.polynomial_support_inclusion`, `KomorebiPaperVIII.polynomial_zero_of_no_paths`.

## 6.3 — Acyclic transfer nilpotence

**checked**

Absence of paths of length h+1 forces A^(h+1)=0. Also derived from a supplied strictly increasing topological level certificate. No graph-level construction algorithm is claimed.

Targets: `KomorebiPaperVIII.nilpotent_of_path_bound`, `KomorebiPaperVIII.nilpotent_of_topological_levels`.

## 6.5 — Level schedule for a triangular solve

**checked**

Actual well-founded forward substitution and stage evaluator in dependent, possibly unequal block spaces. Finite acyclic graph, invertible local diagonal maps, and arbitrary linear edge transfers. No precomputed solution or topological schedule is assumed. Stages read only predecessors and solve the original block equations at canonical depth.

Targets: `KomorebiPaperVIII.DAG.Graph.solve_correct`, `KomorebiPaperVIII.DAG.Graph.solve_unique`, `KomorebiPaperVIII.DAG.Graph.triangular_bijective`, `KomorebiPaperVIII.DAG.Graph.stagedSolve_correct_through`, `KomorebiPaperVIII.DAG.Graph.level_schedule_solves`.

## 6.6 — Sequential depth

**checked**

Canonical predecessor-max levels are constructed from acyclicity through strict ancestor-cardinality decrease. For nonempty finite graphs, attained maximum equals one plus longest edge-path length. Empty graph has depth zero. This is an ideal unit-task schedule, not a hardware timing theorem.

Targets: `KomorebiPaperVIII.DAG.Graph.level_attained`, `KomorebiPaperVIII.DAG.Graph.path_length_le_depth`, `KomorebiPaperVIII.DAG.Graph.depth_attained`, `KomorebiPaperVIII.DAG.Graph.empty_depth`.

## 6.7 — Inverse support lies in the transitive closure

**checked**

Actual reachable packet subspace in a finite-dimensional algebra is invariant. A left inverse makes the restricted forward map injective, hence surjective, yielding inverse invariance. Actual nonsingular matrix inverse specialization. Reachability is reflexive: zero-length paths are included. No inverse-support hypothesis is assumed.

Targets: `KomorebiPaperVIII.inverse_block_zero_of_no_path`, `KomorebiPaperVIII.inverse_support_inclusion`, `KomorebiPaperVIII.matrix_inverse_support`.

## 6.8 — Schur support inclusion

**checked**

Actual rectangular retained-hidden factors and nonsingular hidden matrix inverse. Nonzero Schur block implies a direct retained edge or nonzero entrance, reachable hidden path (possibly zero length), and nonzero exit. Only support inclusion is asserted; cancellation may remove a permitted block.

Targets: `KomorebiPaperVIII.schur_correction_expansion`, `KomorebiPaperVIII.schur_correction_support`, `KomorebiPaperVIII.schur_support_inclusion`, `KomorebiPaperVIII.schur_zero_of_no_route`.

## 7.2 — Invariant packet Krylov decomposition

**checked**

Actual bounded linear maps and spans of finite power orbits. Commutation with the complete finite projector family gives the power expansion and Krylov inclusion. Local spaces lie in the actual projector ranges and their sum is direct. No equality of the global and local Krylov spaces is asserted.

Targets: `KomorebiPaperVIII.invariant_packet_power_expansion`, `KomorebiPaperVIII.invariant_packet_krylov`, `KomorebiPaperVIII.local_krylov_direct`.

## 7.3 — Approximate packet Krylov bound

**checked**

Positive integer power, actual operator norm, and actual Metric.infDist to the sum of local Krylov spaces. Membership of the comparison vector D^j v is derived from packet diagonality. The power estimate also allows a trivial normed ring.

Targets: `KomorebiPaperVIII.approximate_packet_power_bound`, `KomorebiPaperVIII.approximate_packet_krylov_distance`.

## 7.4 — Block Jacobi condition bound

**checked**

Nonempty finite complex matrices, D positive definite and D+K positive definite. D^(-1/2) is the actual inverse of CFC.sqrt D. With ||D^(-1/2) K D^(-1/2)||_2 <= eta <1, proves the condition product ||B||_2*||B^(-1)||_2 <=(1+eta)/(1-eta). Norms are the Euclidean operator norm. The inverse estimate does not require a separately assumed Hermitian perturbation.

Targets: `KomorebiPaperVIII.invSqrt_isUnit`, `KomorebiPaperVIII.invSqrt_normalizes`, `KomorebiPaperVIII.normalized_decomposition`, `KomorebiPaperVIII.block_jacobi_condition`.

## 7.5 — Preconditioned conjugate gradient convergence

**external_input_not_independently_formalized**

Classical input is external; not independently formalized here.

## 7.6 — Certified packet preconditioning

**checked**

Monotonicity of the actual sqrt-based CG factor and its value at the normalized matrix condition number. Propagates an explicit classical energy-error estimate to the certified eta bound. Classical input 7.5 (CG convergence algorithm theorem) is not reproved or silently assumed as a new axiom.

Targets: `KomorebiPaperVIII.matrix_condition_ge_one`, `KomorebiPaperVIII.cgFactor_mono`, `KomorebiPaperVIII.certified_packet_factor`, `KomorebiPaperVIII.certified_energy_error`.

## 8.1 — Packet perturbation certificate

**checked**

Actual continuous linear maps and their operator norm. Source support is assumed only for errors, a weaker sufficient hypothesis. Vector and uniform operator bounds. Not an IEEE/CUDA implementation verification.

Targets: `KomorebiPaperVIII.packet_perturbation_bound`, `KomorebiPaperVIII.packet_relative_perturbation_bound`, `KomorebiPaperVIII.packet_operator_perturbation_bound`, `KomorebiPaperVIII.contractive_packet_operator_bound`.

## 8.2 — Floating point matrix product model

**external_input_not_independently_formalized**

Classical input is external; not independently formalized here.

## 8.3 — Mixed precision product chain

**checked**

Stagewise packet bounds are uniform operator-norm certificates on a nonzero normed space, not vector-specific bounds reused as operator norms. The exact-product perturbation theorem propagates those certificates. Vector error follows by multiplying the operator bound by the input norm.

Targets: `KomorebiPaperVIII.mixed_precision_product_chain`, `KomorebiPaperVIII.chain_action_error`.

## 8.4 — Continuous precision allocation

**checked**

Finite nonempty edge set, strictly positive sensitivities, costs, and budget. Actual sum c*log(1/eps). Feasibility, global optimality, strict inequality away from formula, and unique minimizer. No KKT or convexity result is assumed.

Targets: `KomorebiPaperVIII.optimal_tolerance_feasible`, `KomorebiPaperVIII.precision_allocation_optimal`, `KomorebiPaperVIII.precision_allocation_strict`, `KomorebiPaperVIII.continuous_precision_unique_minimizer`.

## 8.5 — Clipped precision allocation

**checked**

Finite nonempty set; strictly positive sensitivities, costs and caps; 0<budget<=total capped tolerance. Existence by IVT; global strict supporting-log inequality and unique minimizing vector. Unique positive multiplier only strictly below the maximum; endpoint nonuniqueness checked.

Targets: `KomorebiPaperVIII.clipped_scale_exists`, `KomorebiPaperVIII.clipped_unique_minimizer`, `KomorebiPaperVIII.clipped_multiplier_exists_unique`, `KomorebiPaperVIII.clipped_endpoint_nonunique_multiplier`.

## 8.7 — Exact discrete precision program

**checked**

Independent legal assignments choose one listed option per edge. Nonnegative integer weights and exact ordered-field costs. Exact-weight states plus the final budget scan give the optimum with attainment or exact infeasibility. The residual-budget subtraction is guarded. StoredBudgetCompiler proves the actual array-backed implementation equal to this specification.

Targets: `KomorebiPaperVIII.BudgetDP.discrete_precision_program`, `KomorebiPaperVIII.BudgetDP.discreteBudget_some_iff`, `KomorebiPaperVIII.BudgetDP.discreteBudget_none_iff`, `KomorebiPaperVIII.BudgetDP.storedDiscreteBudget_correct`.

## 9.1 — Simultaneous spectral decomposition

**external_input_not_independently_formalized**

Classical input is external; not independently formalized here.

## 9.2 — Exact block discovery certificate

**checked**

Actual finite complex matrices and arbitrary complete orthogonal projector family, not only standard coordinate projectors. Hilbert-Schmidt orthogonality via adjoint products and cyclic trace proves the squared Frobenius residual identity. Separate Euclidean operator-norm triangle inequality certificate. This certifies a supplied packet system, not autonomous discovery.

Targets: `KomorebiPaperVIII.compression_residual`, `KomorebiPaperVIII.block_trace_orthogonal`, `KomorebiPaperVIII.discovery_frobenius_certificate`, `KomorebiPaperVIII.discovery_operator_certificate`.

## 9.4 — Exact Lagrangian packet compiler

**checked**

Arbitrary finite branching rooted trees, independent inductively defined cuts. Returned cut attains the recurrence and beats every legal cut. Generic ordered field covers rationals and reals. No universal discovery/approximation claim.

Targets: `KomorebiPaperVIII.CandidateTree.exact_tree_compiler`, `KomorebiPaperVIII.CandidateTree.compile_attains`, `KomorebiPaperVIII.CandidateTree.exact_lagrangian_compiler`.

## 9.5 — Shared compilation for an operator family

**checked**

Exact weighted family aggregation at pruning level including setup and split overhead. Proved even without sign restrictions; intended application uses nonnegative weights.

Targets: `KomorebiPaperVIII.CandidateTree.cutValue_weighted_family`, `KomorebiPaperVIII.CandidateTree.shared_family_compiler`.

## 9.6 — Monotone Lagrangian frontier

**checked**

Any two optimal cuts, 0 <= lambda1 < lambda2; error nonincreasing and cost nondecreasing. Optimality is discharged by the constructive compiler theorem for its returned cuts.

Targets: `KomorebiPaperVIII.CandidateTree.monotone_lagrangian_frontier`.

## 9.7 — Supported Pareto points

**checked**

Positive scalarization parameter. Every true optimum is undominated. TreeCompilerUpdates.unsupported_pareto_example supplies the rational three-point unsupported-frontier inequality. Quantized-budget compiler remains unformalized.

Targets: `KomorebiPaperVIII.CandidateTree.positive_lagrangian_pareto`.

## 9.8 — Quantized budget dynamic program

**checked**

The actual candidate tree and independent Cut type from the previous block, with arbitrary nonempty finite branching. Min-plus convolution over integer weights proves lower bounds, attainment, and infeasibility. StoredBudgetCompiler certifies the actual cached array-backed output. The implementation returns the minimum cost, not a backtracked cut.

Targets: `KomorebiPaperVIII.CandidateTree.budgetTable_correct`, `KomorebiPaperVIII.CandidateTree.quantized_budget_compiler`, `KomorebiPaperVIII.CandidateTree.compileBudget_some_iff`, `KomorebiPaperVIII.CandidateTree.compileBudget_none_iff`, `KomorebiPaperVIII.CandidateTree.storedBudget_minimum`.

## 9.9 — Pseudo polynomial complexity

**checked**

Array-backed tables cache child results. Concrete convolution candidate indices have at most (B+1)^2 elements. The declared unit-cost tabulation model is bounded by nodeCount*(3*(B+1)+(B+1)^2). Root minimum scan is an additional linear pass. This is pseudo-polynomial in numeric B and does not count exact-arithmetic bit complexity, compiler internals, or hardware instructions.

Targets: `KomorebiPaperVIII.CandidateTree.merge_trial_count`, `KomorebiPaperVIII.CandidateTree.merge_trial_bound`, `KomorebiPaperVIII.CandidateTree.tabulation_pseudopolynomial`.

## 9.11 — Compiler stability

**checked**

Actual solved keep/split scores satisfy strict half-gap inequalities at every internal node. Entire returned cut is unchanged. Ties cannot satisfy these strict hypotheses; no robustness at ties is claimed.

Targets: `KomorebiPaperVIII.CandidateTree.half_gap_order`, `KomorebiPaperVIII.CandidateTree.compiler_stability`.

## 9.12 — Local recompilation

**checked**

Explicit one-hole context with cached sibling values. Replacing a subtree models localized data changes. Cache validity is constructed by refresh, not the new optimum. updateValue reads only new subtree score and caches on ancestor frames. Exact new global optimum and attaining cut proved.

Targets: `KomorebiPaperVIII.CandidateTree.CachedContext.refresh_valid`, `KomorebiPaperVIII.CandidateTree.CachedContext.updateValue_correct`, `KomorebiPaperVIII.CandidateTree.CachedContext.sibling_tree_unchanged`, `KomorebiPaperVIII.CandidateTree.CachedContext.sibling_value_unchanged`, `KomorebiPaperVIII.CandidateTree.CachedContext.local_recompilation`.

## 10.2 — Launch reduction by shape

**checked**

Finite grouping by complete shape signature, partition/fiberwise sum equals original output and work. One launch per active class is a backend capability assumption, not verified CUDA code.

Targets: `KomorebiPaperVIII.shape_launch_count`, `KomorebiPaperVIII.grouped_execution_output`, `KomorebiPaperVIII.grouped_execution_work`.

## 10.3 — Acyclic schedule depth

**checked**

Finite acyclic task graph, unit positive-integer stages, dependency precedence, and unlimited concurrency. Constructed canonical level schedule is pointwise earliest and has minimal makespan; its depth is attained by an actual path when nonempty. Empty graph depth is zero. No weighted-task/resource-limited scheduling claim.

Targets: `KomorebiPaperVIII.DAG.Graph.level_valid`, `KomorebiPaperVIII.DAG.Graph.level_minimal`, `KomorebiPaperVIII.DAG.Graph.optimal_depth`, `KomorebiPaperVIII.DAG.Graph.depth_attained`, `KomorebiPaperVIII.DAG.Graph.same_level_independent`, `KomorebiPaperVIII.DAG.Graph.empty_depth`.

## 10.4 — Amortization threshold

**checked**

Actual declared setup+R*candidate vs R*baseline inequality. Positive per-use advantage; setup nonnegative for smallest natural reuse floor+1. Equality is break-even, not profitability.

Targets: `KomorebiPaperVIII.amortization_threshold`, `KomorebiPaperVIII.no_amortization`, `KomorebiPaperVIII.integer_amortization_threshold`, `KomorebiPaperVIII.minimum_reuse_attains`.

## 10.5 — Graph replay threshold

**checked**

Capture plus repeated replay vs repeated ordinary execution under replay<ordinary. Pure timing-model identity, not new GPU data.

Targets: `KomorebiPaperVIII.graph_replay_threshold`.

## 10.6 — Materialization threshold

**checked**

Nonnegative materialization cost and reuse count. Strict profitability iff explicit per-use time is lower and reuse exceeds the ratio.

Targets: `KomorebiPaperVIII.materialization_threshold`.

## 11.3 — Fair matching is an equivalence relation

**checked**

Equality of complete case, output, correctness reference, and timing-scope metadata. No inference of actual timing accuracy from matching metadata.

Targets: `KomorebiPaperVIII.fair_match_iff_eq`, `KomorebiPaperVIII.fair_matching_equivalence`.
