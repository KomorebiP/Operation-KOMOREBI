# Paper VIII Mathematical Record Register

This register was generated from the final Annals source and auxiliary file. The proof status records whether a complete proof environment follows the result in the manuscript. It does not substitute for independent specialist validation.

## Summary

- **Theorem**: 28
- **Proposition**: 11
- **Lemma**: 0
- **Corollary**: 17
- **Definition**: 20
- **Example**: 0
- **Remark**: 5
- **Standard Fact**: 4
- **Total numbered records**: 85
- **Internally proved results**: 56
- **Missing proof environments**: 0

## Complete register

| No. | Type | Title | Label | Page | Section | Proof status |
|---:|---|---|---|---:|---|---|
| 2.1 | Definition | Packet layout | `def:packet_layout` | 4 | Packet operator representations / Exact semantics | not applicable |
| 2.2 | Definition | Packet operator representation | `def:packet_ir` | 4 | Packet operator representations / Exact semantics | not applicable |
| 2.3 | Theorem | Exact evaluation | `thm:exact_evaluation` | 4 | Packet operator representations / Exact semantics | complete |
| 2.4 | Definition | Support graph | `def:support_graph` | 5 | Packet operator representations / Exact semantics | not applicable |
| 2.5 | Theorem | Block composition | `thm:block_composition` | 5 | Packet operator representations / Exact semantics | complete |
| 2.6 | Corollary | Adjoint and tensor semantics | `cor:adjoint_tensor` | 6 | Packet operator representations / Exact semantics | complete |
| 2.7 | Definition | Output contract | `def:output_contract` | 6 | Packet operator representations / Output contracts | not applicable |
| 2.8 | Definition | Timing scope | `def:timing_scope` | 6 | Packet operator representations / Output contracts | not applicable |
| 2.9 | Proposition | Contract conversion | `prop:contract_conversion` | 6 | Packet operator representations / Output contracts | complete |
| 2.10 | Remark | Untitled | `rem:semantic_boundary` | 6 | Packet operator representations / Output contracts | not applicable |
| 3.1 | Theorem | Dense and packet application counts | `thm:packet_counts` | 7 | Arithmetic, storage, and data movement | complete |
| 3.2 | Corollary | Equal diagonal packets | `cor:equal_blocks` | 7 | Arithmetic, storage, and data movement | complete |
| 3.3 | Definition | Block diagonal plus low rank operator | `def:bdlr` | 7 | Arithmetic, storage, and data movement | not applicable |
| 3.4 | Theorem | BDLR application and storage | `thm:bdlr_counts` | 7 | Arithmetic, storage, and data movement | complete |
| 3.5 | Definition | One pass streaming model | `def:streaming_model` | 8 | Arithmetic, storage, and data movement | not applicable |
| 3.6 | Proposition | Streaming byte count | `prop:streaming_bytes` | 9 | Arithmetic, storage, and data movement | complete |
| 3.7 | Definition | Arithmetic intensity | `def:intensity` | 9 | Arithmetic, storage, and data movement | not applicable |
| 3.8 | Theorem | Roofline lower bound | `thm:roofline` | 9 | Arithmetic, storage, and data movement | complete |
| 3.9 | Corollary | Capacity threshold | `cor:capacity` | 9 | Arithmetic, storage, and data movement | complete |
| 3.10 | Proposition | Materialization cost | `prop:materialization_cost` | 10 | Arithmetic, storage, and data movement | complete |
| 4.1 | Proposition | Equal block banded count | `prop:block_banded_count` | 10 | Structured packet primitives | complete |
| 4.2 | Proposition | Sparse plus low rank application | `prop:sparse_low_rank` | 11 | Structured packet primitives | complete |
| 4.3 | Theorem | Circulant spectral representation | `thm:circulant` | 11 | Structured packet primitives | complete |
| 4.4 | Corollary | Toeplitz circulant embedding | `cor:toeplitz_embedding` | 12 | Structured packet primitives | complete |
| 4.5 | Theorem | Kronecker modewise application | `thm:kronecker_apply` | 12 | Structured packet primitives | complete |
| 4.6 | Corollary | Equal tensor factors | `cor:tensor_modewise` | 12 | Structured packet primitives | complete |
| 4.7 | Theorem | Walsh Hadamard recursion | `thm:walsh_hadamard` | 13 | Structured packet primitives | complete |
| 5.1 | Theorem | Exact BDLR product | `thm:bdlr_product` | 13 | Exact low rank algebra and recompression / Products and inverses | complete |
| 5.2 | Corollary | Rank growth in a product chain | `cor:rank_growth` | 14 | Exact low rank algebra and recompression / Products and inverses | complete |
| 5.3 | Theorem | Woodbury inversion | `thm:woodbury` | 14 | Exact low rank algebra and recompression / Products and inverses | complete |
| 5.4 | Corollary | Inverse norm bound | `cor:inverse_norm` | 15 | Exact low rank algebra and recompression / Products and inverses | complete |
| 5.5 | Standard Fact | Eckart Young Mirsky theorem | `fact:eym` | 15 | Exact low rank algebra and recompression / Optimal factor recompression | external |
| 5.6 | Theorem | Small core recompression | `thm:small_core_recompression` | 15 | Exact low rank algebra and recompression / Optimal factor recompression | complete |
| 5.7 | Remark | Untitled | `rem:recompression_work` | 16 | Exact low rank algebra and recompression / Optimal factor recompression | not applicable |
| 5.8 | Theorem | Product chain perturbation | `thm:product_chain_error` | 17 | Exact low rank algebra and recompression / Optimal factor recompression | complete |
| 5.9 | Theorem | Certified repeated recompression | `cor:recompression_chain` | 17 | Exact low rank algebra and recompression / Optimal factor recompression | complete |
| 6.1 | Theorem | Path support of powers | `thm:path_support` | 18 | Sparse transfer graphs and schedules / Support under algebraic operations | complete |
| 6.2 | Corollary | Polynomial support | `cor:polynomial_support` | 18 | Sparse transfer graphs and schedules / Support under algebraic operations | complete |
| 6.3 | Corollary | Acyclic transfer nilpotence | `cor:acyclic_nilpotence` | 18 | Sparse transfer graphs and schedules / Support under algebraic operations | complete |
| 6.4 | Definition | Topological level | `def:topological_level` | 18 | Sparse transfer graphs and schedules / Block triangular solves | not applicable |
| 6.5 | Theorem | Level schedule for a triangular solve | `thm:level_schedule` | 18 | Sparse transfer graphs and schedules / Block triangular solves | complete |
| 6.6 | Corollary | Sequential depth | `cor:sequential_depth` | 19 | Sparse transfer graphs and schedules / Block triangular solves | complete |
| 6.7 | Theorem | Inverse support lies in the transitive closure | `thm:inverse_support` | 19 | Sparse transfer graphs and schedules / Fill under elimination | complete |
| 6.8 | Proposition | Schur support inclusion | `prop:schur_fill` | 20 | Sparse transfer graphs and schedules / Fill under elimination | complete |
| 7.1 | Definition | Krylov space | `def:krylov` | 21 | Krylov methods and packet preconditioning | not applicable |
| 7.2 | Proposition | Invariant packet Krylov decomposition | `prop:krylov_invariant` | 21 | Krylov methods and packet preconditioning | complete |
| 7.3 | Theorem | Approximate packet Krylov bound | `thm:approx_krylov` | 21 | Krylov methods and packet preconditioning | complete |
| 7.4 | Theorem | Block Jacobi condition bound | `thm:block_jacobi` | 22 | Krylov methods and packet preconditioning | complete |
| 7.5 | Standard Fact | Preconditioned conjugate gradient convergence | `fact:cg` | 22 | Krylov methods and packet preconditioning | external |
| 7.6 | Corollary | Certified packet preconditioning | `cor:certified_pcg` | 22 | Krylov methods and packet preconditioning | complete |
| 8.1 | Theorem | Packet perturbation certificate | `thm:packet_error` | 23 | Packetwise mixed precision / One operator | complete |
| 8.2 | Standard Fact | Floating point matrix product model | `fact:rounding` | 23 | Packetwise mixed precision / One operator | external |
| 8.3 | Corollary | Mixed precision product chain | `cor:mixed_chain` | 24 | Packetwise mixed precision / Several operators | complete |
| 8.4 | Theorem | Continuous precision allocation | `thm:continuous_precision` | 24 | Packetwise mixed precision / Continuous allocation | complete |
| 8.5 | Theorem | Clipped precision allocation | `thm:clipped_precision` | 24 | Packetwise mixed precision / Continuous allocation | complete |
| 8.6 | Definition | Discrete precision option | `def:dtype_option` | 25 | Packetwise mixed precision / Discrete data types | not applicable |
| 8.7 | Theorem | Exact discrete precision program | `thm:discrete_precision` | 26 | Packetwise mixed precision / Discrete data types | complete |
| 8.8 | Remark | Untitled | `rem:dtype_boundary` | 26 | Packetwise mixed precision / Discrete data types | not applicable |
| 9.1 | Standard Fact | Simultaneous spectral decomposition | `fact:simultaneous` | 26 | Discovery and exact packet compilation / Exact spectral discovery | external |
| 9.2 | Proposition | Exact block discovery certificate | `prop:block_discovery_certificate` | 26 | Discovery and exact packet compilation / Exact spectral discovery | complete |
| 9.3 | Definition | Candidate representation tree | `def:candidate_tree` | 27 | Discovery and exact packet compilation / Candidate packet trees | not applicable |
| 9.4 | Theorem | Exact Lagrangian packet compiler | `thm:tree_compiler` | 27 | Discovery and exact packet compilation / Candidate packet trees | complete |
| 9.5 | Corollary | Shared compilation for an operator family | `cor:shared_compiler` | 28 | Discovery and exact packet compilation / Candidate packet trees | complete |
| 9.6 | Proposition | Monotone Lagrangian frontier | `prop:lagrangian_frontier` | 29 | Discovery and exact packet compilation / Candidate packet trees | complete |
| 9.7 | Corollary | Supported Pareto points | `cor:supported_pareto` | 29 | Discovery and exact packet compilation / Candidate packet trees | complete |
| 9.8 | Theorem | Quantized budget dynamic program | `thm:budget_compiler` | 30 | Discovery and exact packet compilation / An exact error budget compiler | complete |
| 9.9 | Corollary | Pseudo polynomial complexity | `cor:budget_complexity` | 30 | Discovery and exact packet compilation / An exact error budget compiler | complete |
| 9.10 | Definition | Decision gap | `def:decision_gap` | 30 | Discovery and exact packet compilation / Decision stability and local updates | not applicable |
| 9.11 | Theorem | Compiler stability | `thm:compiler_stability` | 30 | Discovery and exact packet compilation / Decision stability and local updates | complete |
| 9.12 | Theorem | Local recompilation | `thm:local_recompilation` | 31 | Discovery and exact packet compilation / Decision stability and local updates | complete |
| 9.13 | Remark | Boundary of the compiler theorem | `rem:compiler_boundary` | 31 | Discovery and exact packet compilation / Decision stability and local updates | not applicable |
| 10.1 | Definition | Shape class | `def:shape_class` | 31 | Device scheduling and amortization / Shape classes | not applicable |
| 10.2 | Proposition | Launch reduction by shape | `prop:shape_launch` | 31 | Device scheduling and amortization / Shape classes | complete |
| 10.3 | Theorem | Acyclic schedule depth | `thm:dag_depth` | 32 | Device scheduling and amortization / Critical path | complete |
| 10.4 | Theorem | Amortization threshold | `thm:amortization` | 32 | Device scheduling and amortization / One time costs | complete |
| 10.5 | Corollary | Graph replay threshold | `cor:graph_threshold` | 33 | Device scheduling and amortization / One time costs | complete |
| 10.6 | Corollary | Materialization threshold | `cor:materialization_threshold` | 33 | Device scheduling and amortization / One time costs | complete |
| 11.1 | Definition | Case signature | `def:case_signature` | 33 | Benchmark contracts and measurement protocol | not applicable |
| 11.2 | Definition | Fair match | `def:fair_match` | 33 | Benchmark contracts and measurement protocol | not applicable |
| 11.3 | Proposition | Fair matching is an equivalence relation | `prop:fair_equivalence` | 33 | Benchmark contracts and measurement protocol | complete |
| 11.4 | Definition | Representation gain | `def:representation_gain` | 33 | Benchmark contracts and measurement protocol | not applicable |
| 11.5 | Definition | Device gain | `def:device_gain` | 34 | Benchmark contracts and measurement protocol | not applicable |
| 11.6 | Definition | Kernel gain | `def:kernel_gain` | 34 | Benchmark contracts and measurement protocol | not applicable |
| 11.7 | Definition | Amortization gain | `def:amortization_gain` | 34 | Benchmark contracts and measurement protocol | not applicable |
| 11.8 | Remark | Logical work rate | `rem:logical_gflops` | 34 | Benchmark contracts and measurement protocol | not applicable |
