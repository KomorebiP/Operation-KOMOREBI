# Paper VIII proof audit

## Structural result

The final source contains:

- 28 theorem environments
- 11 proposition environments
- 17 corollary environments
- 56 complete proof environments
- 4 standard facts cited as external input
- 0 theorem, proposition, or corollary environments without a following proof

The result and proof counts agree exactly.

## Dependency classes

### Direct finite algebra

These proofs use coordinate identities, finite matrix multiplication, norm inequalities, or induction:

- exact packet evaluation
- block composition
- adjoint and tensor semantics
- dense and packet counts
- BDLR counts
- block banded and sparse plus low rank counts
- circulant, Toeplitz, Kronecker, and Walsh Hadamard formulas
- BDLR product and Woodbury inversion
- path support and triangular scheduling
- inverse support and Schur fill
- Krylov decomposition
- packet perturbation
- reuse thresholds

### External standard inputs

The manuscript identifies four external facts rather than reproducing them:

1. Eckart Young Mirsky optimal low rank approximation
2. Preconditioned conjugate gradient convergence
3. Standard floating point matrix product perturbation model
4. Simultaneous spectral decomposition of commuting normal matrices

Each external fact is cited where used.

### Convex and dynamic optimization

The precision and compiler proofs use:

- strict convexity and Lagrange multipliers
- Karush Kuhn Tucker conditions
- exact finite dynamic programming
- induction on rooted trees
- min plus convolution
- comparison of two optimality inequalities

### Empirical claims

Measured claims are not presented as proofs. They are checked against the sanitized corpus in the deterministic verifier.

## Proof specific checks

### Small core recompression

The proof is valid for compact QR factors whose ranks may differ. The singular value problem is taken on the rectangular core. No full column rank assumption is hidden.

### Repeated recompression

The final theorem uses

```text
D_j = A_j D_(j−1) + E_j
```

and expands this recurrence exactly. This is the correct model for additive error introduced after each partial product.

### Inverse support

The proof uses finite dimensionality when it concludes that an injective restriction to an invariant subspace is onto that subspace. This hypothesis is present in the article through the finite packet layout.

### Clipped precision allocation

The proof accounts for active upper bounds. The multiplier can fail to be unique at the maximal endpoint, but the optimizer remains unique. The statement records this exception.

### Lagrangian tree compiler

The final theorem explicitly handles terminal nodes. Every internal pruning is either the keep option or the union of one pruning from each child.

### Compiler stability

The theorem assumes a perturbation bound on the computed keep and split scores. It does not claim that arbitrary changes in primitive data automatically satisfy this bound.

### Fair matching

The proposition concerns equality of complete metadata tuples. It does not say that rows with merely similar dimensions are fairly matched.

## Cross reference audit

- 125 labels are present and all are unique.
- Every internal reference resolves.
- Every citation key resolves.
- All 26 bibliography entries are cited.

## Proof boundary

The completed proof environments establish the statements under their printed hypotheses. They do not establish historical novelty, practical stability beyond the stated norm bounds, or performance portability beyond the recorded benchmark environment.
