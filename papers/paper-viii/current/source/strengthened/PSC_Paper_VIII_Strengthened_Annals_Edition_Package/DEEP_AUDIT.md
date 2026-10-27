# Paper VIII deep mathematical audit

## Audit objective

This audit checks whether the final article states finite mathematical results under hypotheses sufficient for the proofs given. It also checks whether empirical statements are confined to the recorded benchmark corpus.

The audit is internal. It is not a substitute for independent peer review.

## Overall result

The final source contains 56 internally proved results and 56 complete proof environments. Four standard facts are identified as external inputs. No theorem target remains unresolved inside the article.

The deepest original additions are the exact finite tree compiler, the quantized error budget compiler, the compact small core recompression theorem, and the separation of operator contracts from timing scopes. These results are stated for finite models with additive local costs and errors. Their boundaries are explicit.

## Representation semantics

### Exact evaluation

The packet representation is defined by actual linear maps

```text
B_{beta alpha}: X_alpha → X_beta
```

and evaluation is the sum of their coordinate inclusions. Exact reconstruction follows by inserting the complete coordinate identity on both sides of an operator.

### Composition

Block composition is ordinary matrix multiplication over the packet index. The support conclusion is an inclusion because distinct path contributions can cancel.

### Contracts

The output contract proposition is logically necessary. A compressed factor representation and an explicit matrix are different returned objects. The article counts decoding or materialization when the comparison requires explicit output.

## Cost models

### Arithmetic counts

The operation counts use a declared model of two operations for one multiply and one add. They are representation counts rather than timing predictions.

### Streaming traffic

The byte count is tied to the one pass model stated in the definition. It does not claim a communication lower bound and does not assume cache reuse across edges.

### Roofline statement

The lower bound follows directly from peak modeled operation rate and bandwidth. The article treats it as a necessary bound, not an exact execution law.

### Materialization

The explicit BDLR materialization count includes the dense product of an `n × r` factor with an `r × n` factor. The result is correctly distinguished from compressed application.

## Structured primitives

The formulas for block banded storage, sparse plus low rank application, circulant diagonalization, Toeplitz embedding, Kronecker application, and Walsh Hadamard recursion were checked against direct finite implementations.

The Toeplitz embedding uses a length `2n` circulant vector and zero pads the input to the same length. The first `n` circular convolution entries reproduce the Toeplitz product.

The Kronecker identity uses column major vectorization and the transpose on the right factor exactly as stated.

## Low rank algebra

### Product closure

The BDLR product formula was expanded term by term. The two terms sharing the right factor are grouped correctly. The other cross term uses `D_B^* V_A` so that its adjoint is `V_A^* D_B`.

### Woodbury inversion

The hypotheses require invertibility of both the packet diagonal part and the small Schur matrix. The proof checks the proposed inverse algebraically.

### Small core recompression

The theorem uses compact QR factorizations. This matters when the input factors are rank deficient or have different column ranks. The core matrix is rectangular when the two factor ranks differ. The outer orthonormal factors preserve the nonzero singular values and every unitarily invariant norm. The Eckart Young Mirsky theorem therefore applies to the small core.

### Error propagation

Two different error models are separated.

1. Product chain perturbation treats each multiplicative factor as perturbed.
2. Repeated recompression treats an additive error inserted after each partial multiplication.

The second statement has its own inhomogeneous recurrence. It is not obtained by a loose substitution into the first theorem.

## Transfer graphs

### Path support

Powers are expanded by inserting the packet identity between every pair of factors. Acyclic strict transfer support therefore gives nilpotence after the longest path length.

### Triangular scheduling

The level theorem assumes a directed acyclic dependency graph, invertible diagonal blocks, and a topological ordering. Blocks in the same source removal level have no dependency edge between them.

### Inverse support

For a starting packet, the direct sum of all reachable packets is invariant under the operator. In finite dimension, the restriction of an invertible operator to this invariant subspace is onto it. The inverse therefore cannot leave the reachable set.

### Schur fill

The hidden inverse can connect only hidden packets joined by a hidden path. A retained Schur correction can therefore appear only along a retained to hidden path, a hidden transitive connection, and a hidden to retained path. The result is an inclusion because cancellation remains possible.

## Krylov and preconditioning

The invariant packet Krylov statement uses exact commutation with the packet projectors.

The approximate Krylov bound follows from the telescoping identity

```text
A^j − D^j = sum A^(j−1−k) K D^k.
```

The block Jacobi theorem is stated for Hermitian positive definite operators and normalized Hermitian coupling with norm below one. The conjugate gradient corollary uses the symmetric preconditioned matrix

```text
D^(−1/2) A D^(−1/2).
```

This avoids an imprecise statement involving a generally nonsymmetric left preconditioned matrix.

## Mixed precision

### Packet certificate

Every local perturbation is required to act only on its declared source packet. The resulting vector bound is a direct sum of local operator sensitivities.

### Continuous allocation

The objective is strictly convex on the positive orthant. The equality constraint gives the stated Lagrange multiplier and unique minimizer.

### Clipped allocation

The Karush Kuhn Tucker form is correct. The weighted tolerance sum is continuous and nonincreasing in the multiplier. At the maximal feasible tolerance the minimizer remains unique even though the multiplier representation is not unique, which the statement records.

### Discrete assignment

Unreachable and negative dynamic programming states are assigned infinite cost. The recurrence therefore enumerates exactly one precision option per edge and returns the minimum cost under the integer budget.

## Discovery and compilation

### Spectral discovery

The article uses simultaneous spectral decomposition only for commuting normal matrices. Arbitrary operators are not claimed to possess a discoverable common spectral packet system.

The a posteriori block certificate is exact in Frobenius norm because distinct blocks are orthogonal in the Hilbert Schmidt inner product.

### Lagrangian compiler

A terminal node has only the keep option. An internal node has exactly two choices: keep the node or split into independent child subproblems. The recurrence therefore has exact optimal substructure.

The original draft needed a separate terminal rule. It is present in the final theorem.

### Frontier monotonicity

The proof compares the two optimality inequalities at distinct Lagrange parameters. It establishes that increasing the error penalty cannot increase optimal error and cannot decrease optimal cost. The statement holds for arbitrary selected optimizers at the two parameters.

### Quantized budget compiler

The table stores minimum cost at each exact integer error. A split is a min plus convolution of the child tables. Taking the minimum over all root errors no larger than the budget gives the exact constrained optimum.

### Stability and local recompilation

The decision stability theorem assumes a bound directly on the final keep and split scores. It does not infer that bound from arbitrary primitive perturbations.

Local recompilation follows the dependency graph of the tree dynamic program. Changes inside one subtree affect that subtree and the unique ancestor chain to the root.

### Boundary

The proof depends on a finite tree and additive local models. Overlapping decompositions, nonlocal cache terms, and globally coupled ranks can destroy optimal substructure. The article makes no approximation claim in those settings.

## Scheduling and amortization

The shape class launch result assumes backend support for one batched array or pointer list per class. Without that hypothesis, a shape class need not correspond to one launch.

The acyclic depth theorem assumes unit duration tasks and unlimited concurrent resources. Its conclusion is not presented as a finite processor scheduling theorem.

The reuse thresholds follow by comparing one time setup plus candidate cost with repeated baseline cost. Strict inequality is handled by the floor plus one formula.

## Measurement audit

The sanitized JSON corpus contains:

- 154 rows
- 16 suites
- 74 CPU rows
- 80 GPU rows

Every numerical value quoted in the article is checked against that corpus by the deterministic verifier. The corpus retains negative controls and does not discard slower candidate methods.

The strongest recorded matched block result is 14.8919 times the device resident dense GPU row for the declared case. The article does not generalize this value beyond the recorded case signature.

## Issues found and corrected during the audit

1. The candidate tree recurrence initially lacked a separate terminal node rule.
2. The repeated recompression estimate was initially treated as if it were an ordinary factor perturbation. It now has its own additive recurrence.
3. Small core recompression initially assumed a square full rank core. It now uses compact QR and allows a rectangular core.
4. The packet perturbation theorem initially omitted the source packet support condition.
5. The Krylov space was initially used before it was defined.
6. The preconditioned conjugate gradient statement was rewritten using the symmetric preconditioned operator.
7. Unreachable states in the discrete precision program are now assigned infinite cost.
8. The tree compiler now distinguishes terminal and internal nodes.
9. The Schur fill statement now depends on a proved inverse support theorem.
10. The shape class result now assumes an available batched backend.
11. The acyclic scheduling theorem now states its unit task and unlimited concurrency assumptions.
12. Fair matching now requires identical case signatures, outputs, references, and timing scopes.
13. The capacity threshold now refers only to representation storage.
14. Broad novelty language was removed from the introduction.

## Residual review priorities

Independent reviewers should concentrate on:

- whether the tree cost and error model captures the intended downstream applications
- numerical stability of the factor QR and small core singular value calculations in finite precision
- conditioning and cancellation in practical BDLR product chains
- portability and fairness of the measured device comparisons
- historical relation between the compiler theorem and best basis or model selection dynamic programs

No internal gap was found after the final correction pass, but independent specialist review remains necessary.
