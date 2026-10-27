# Deep mathematical audit

## Scope

The manuscript proves finite dimensional and bounded operator results. It does not claim a construction of an interacting continuum field theory, a proof of quantum gravity, an anomaly free unbounded constraint algebra, an Einstein infrared limit, or a physical massless spin two sector.

## Central theorem chain

The article follows the sequence

\[
\text{observable generation}
\longrightarrow
\text{symmetry packets}
\longrightarrow
\text{circuit paths}
\longrightarrow
\text{moving transport}
\longrightarrow
\text{operator packets}
\longrightarrow
\text{error correction}
\longrightarrow
\text{effective dynamics}
\longrightarrow
\text{finite geometry}
\longrightarrow
\text{bounded limits}.
\]

## Corrections made during the final audit

### 1. Constraint closure

Compression of a commutator to the common physical kernel was removed as a closure criterion. For self adjoint constraints that compression vanishes automatically. The final manuscript defines the obstruction by

\[
[C_a,C_b]
\quad\text{modulo}\quad
\operatorname{span}_{\mathbb C}\{C_1,\ldots,C_m\}.
\]

This quotient detects whether the declared constraint span is closed under commutators.

### 2. Moving packet leakage

The estimate is stated on a nonnegative time interval. Its exact off packet coupling is

\[
Q(t)\bigl(H(t)-iK(t)\bigr)P(t).
\]

The geometric connection term is therefore included in the coupling test.

### 3. Exact recovery

The recovery map is extended to a channel by an explicit completely positive trace preserving formula on the orthogonal complement of the syndrome support. The proof no longer relies on an informal extension statement.

### 4. Local closure after elimination

Necessity of zero retained to hidden coupling is proved by comparing the second derivatives at time zero. If every retained trajectory obeys the bare local equation, then

\[
BB^*=0,
\]

and hence \(B=0\).

### 5. Lindblad coherence

The final statement concerns independently evolving coherence components. It does not suggest that a positive density matrix can occupy an arbitrary nonzero coherence order by itself.

### 6. Periodic lattice limit

The theorem separates the fixed lattice ultraviolet limit from the refinement limit. At fixed finite dimension the spectral dimension tends to zero at both time extremes. The continuum value appears only after refinement at fixed positive diffusion time.

### 7. Bounded continuum towers

The direct limit theorem assumes a uniform operator norm bound. The common space approximation theorem assumes norm summability. The paper states explicitly that unbounded continuum Hamiltonians require domain sensitive convergence such as strong resolvent or quadratic form convergence.

## High risk proof audit

### Short packet rotations

The direct rotation is defined by the polar factor of

\[
S(\mathcal Q,\mathcal P)=\sum_aQ_aP_a.
\]

Invertibility follows from \(\|S-I\|<1\). The local expansion is

\[
\mathcal U(\mathcal P(t+h),\mathcal P(t))
=I+hK(t)+O(h^2).
\]

The accumulated product error is bounded by the sum of the squared step lengths, which is at most a constant times the mesh.

### Choi covariance

The manuscript fixes the output tensor input convention

\[
J(\Phi)=\sum_{i,j}\Phi(|i\rangle\langle j|)\otimes|i\rangle\langle j|.
\]

With this convention covariance is equivalent to invariance under \(U\otimes\overline U\).

### Error correction

The Knill Laflamme matrix is shown to be positive. Diagonalization gives orthogonal syndrome isometries. The recovery calculation uses unitary mixing of Kraus operators and trace preservation on code states.

### Feshbach reduction

The projected resolvent is obtained by block Gaussian elimination. The sign of the self energy follows from the resolvent identity in the upper half plane. Stability is controlled by two coupling differences and one hidden resolvent difference.

### Positive memory kernel

The kernel

\[
K(t)=Be^{-itD}B^*
\]

is positive definite because its finite quadratic forms are squared norms in the hidden Hilbert space.

### Reflection positivity

Every finite reflection matrix is a Gram matrix of vectors \(T^{n_j}v_j\). The theorem is finite and does not imply the remaining field theoretic reconstruction axioms.

### Heat trace convergence

Centered lattice modes obey a Gaussian lower bound independent of the lattice size. Dominated convergence applies to both the heat trace and its first spectral moment.

### Constraint refinement

Exact intertwining transports commutators and fixed structure anomalies. The approximate theorem expands the commutator difference into four controlled terms.

## Computational verification

The final suite reports

```text
Paper VII verification: 18049/18049 checks passed in 15 groups
```

The largest group checks periodic lattice dispersion and heat trace formulas across dimensions, grid sizes, and modes. Other groups test finite group projectors, circuit paths, leakage, Kato transport, channels, Lindblad evolution, error correction, Feshbach formulas, memory positivity, reflection positivity, constraint quotients, and bounded limits.

## Remaining external review priorities

1. Historical comparison of the package level synthesis with existing symmetry resolved quantum mechanics and operator algebra literature
2. Specialist review of the short rotation convergence theorem
3. Specialist review of the quotient obstruction formulation for constraints
4. Specialist review of the fixed time heat trace and spectral dimension presentation
5. Independent verification of every citation and proof before submission
