# Extension notes

This revision pushes the symmetry-collapse program only where the existing framework supports a rigorous extension.

## Added theorem families

### 1. Moving-packet theorem

A fixed conserved sector is sufficient but not necessary. Exact classical simulation remains polynomial when the state follows an efficiently computable sequence of polynomial-dimensional subspaces and the rectangular gate updates between their coordinate bases are efficient.

### 2. Moving-frame corollary

A time-dependent frame can convert a moving packet into one fixed reference packet. The result explicitly excludes the circular choice obtained by encoding the full quantum evolution into the frame itself.

### 3. Sparse packet-transfer theorem

Sector-changing gates are allowed. The decisive quantity is the total dimension of all packets reachable at each time, not exact conservation of one label.

### 4. Schur-commutant theorem

For fixed local dimension, permutation-invariant mixed states and permutation-covariant dynamics can be represented by polynomially many Schur carrier blocks. Exponential symmetric-group multiplicity spaces occur only as identity factors. The qubit record requires `O(n^3)` parameters.

### 5. Scaling phase diagram

The explicit fixed-charge representation exhibits a sequence of regimes:

- bounded particles or holes: polynomial;
- logarithmically many: quasipolynomial;
- `n^alpha`, with `0 < alpha < 1`: subexponential;
- finite density: exponential.

## Deliberate stopping point

The revision does not claim:

- an efficient algorithm for discovering arbitrary hidden moving frames;
- a collapse of generic quantum circuits or BQP to P;
- that Schur-Weyl coordinates alone make arbitrary local circuits easy;
- that a symmetry label is sufficient without efficient initialization, updates, measurement, and leakage control.

The new results enlarge the exact classical-collapse class while preserving the boundary created by global cross-packet interference.
