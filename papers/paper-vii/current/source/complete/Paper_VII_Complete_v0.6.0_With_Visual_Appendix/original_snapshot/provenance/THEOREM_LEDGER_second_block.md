# Paper VII: cumulative theorem ledger

Author: Komorebi P.

**v0.2.0: 11 of 19 finite named items checked. Eight finite items and five continuum conjectures remain unchecked.**

The release has 82 Lean theorem declarations. Fifty are new in this block. Supporting lemmas and concrete specializations are included in these counts. They are not 82 separate manuscript items.

| Item | Result | Status | Module |
|---|---|---|---|
| 2.1 | Orbit dimension of one quantum seed | NOT_CHECKED_IN_THIS_RELEASE | Not supplied |
| 2.2 | Quantum seed-rank formula | NOT_CHECKED_IN_THIS_RELEASE | Not supplied |
| 2.3 | Local orbit and Schmidt rank | NOT_CHECKED_IN_THIS_RELEASE | Not supplied |
| 2.4 | One seed for the computational basis | LEAN_CHECKED | ComputationalSeed |
| 3.1 | Cyclic quantum projectors | NOT_CHECKED_IN_THIS_RELEASE | Not supplied |
| 3.2 | Tensor/polyphase refinement | LEAN_CHECKED | TensorRefinement |
| 4.1 | Exact circuit path expansion | LEAN_CHECKED | QuantumPacketCore |
| 4.2 | Packetwise unitarity conservation | LEAN_CHECKED | QuantumPacketCore |
| 5.1 | Exact symmetry packets | LEAN_CHECKED | QuantumPacketCore |
| 5.2 | Commutator leakage bound | NOT_CHECKED_IN_THIS_RELEASE | Not supplied |
| 6.1 | Moving-frame Hamiltonian | LEAN_CHECKED | MovingFrames |
| 6.3 | Canonical packet connection | LEAN_CHECKED | CanonicalConnection |
| 6.4 | Projected connection | NOT_CHECKED_IN_THIS_RELEASE | Not supplied |
| 7.1 | Block-diagonal measurement invariance | LEAN_CHECKED | QuantumPacketCore |
| 7.2 | Finite Kraus channel | LEAN_CHECKED | KrausChannels |
| 8.1 | Finite Knill-Laflamme criterion | NOT_CHECKED_IN_THIS_RELEASE | Not supplied |
| 9.1 | Exact Feshbach resolvent | LEAN_CHECKED | SchurFeshbach |
| 10.1 | Finite Euclidean transfer | NOT_CHECKED_IN_THIS_RELEASE | Not supplied |
| 11.1 | Low-mode second-order bound | LEAN_CHECKED | LowModeConvergence |

## Exact coverage and limitations

### 2.1 — Orbit dimension of one quantum seed
Matrix orbit and dimension argument not checked in this block.

### 2.2 — Quantum seed-rank formula
Minimum seed count and direct-sum construction remain.

### 2.3 — Local orbit and Schmidt rank
Tensor coefficient identification and Schmidt-rank bridge remain.

### 2.4 — One seed for the computational basis
Explicit local Pauli X addressing for every n, including n=0. The constructed gate word sends the zero seed to the standard coordinate basis, with linear independence, span and cardinality 2^n.

### 3.1 — Cyclic quantum projectors
General finite-order character projector construction remains.

### 3.2 — Tensor/polyphase refinement
Arbitrary finite tensor factors and dimensions. Proves tensor product multiplication, identity, adjoint and sum laws, then orthogonality, completeness and self-adjointness after grouping by total residue for N>0.

### 4.1 — Exact circuit path expansion
Arbitrary finite gate list, corner expansion and complete reconstruction.

### 4.2 — Packetwise unitarity conservation
Both identities in a star ring, plus concrete complex-matrix specializations.

### 5.1 — Exact symmetry packets
Generator blocks and actual exponential; zero cross-packet transfer.

### 5.2 — Commutator leakage bound
Quantitative Duhamel/norm estimate not supplied by the exact-commutation theorem.

### 6.1 — Moving-frame Hamiltonian
Entrywise actual real derivatives of finite complex matrices and vectors. Constructs y=U*psi and its derivative, verifies the transformed Schrodinger equation and Hermiticity. The effective-Hamiltonian Hermiticity conclusion explicitly assumes H*=H.

### 6.3 — Canonical packet connection
Actual derivatives in a normed real star algebra with continuous star. Differentiates projector multiplication, completeness and self-adjointness to prove both formulas for C, skew-adjointness and [C,P_b]=dot(P_b). Does not include manifold curvature.

### 6.4 — Projected connection
Range bundle, differential forms and curvature remain.

### 7.1 — Block-diagonal measurement invariance
Trace duality, measurement invariance and trace preservation for finite complex matrices.

### 7.2 — Finite Kraus channel
Finite complex matrix Kraus map: linearity, positivity, trace preservation under sum(K* K)=I, identity-tensor amplification at every finite auxiliary dimension, complete positivity and density-matrix preservation.

### 8.1 — Finite Knill-Laflamme criterion
Both necessity and constructive recovery remain.

### 9.1 — Exact Feshbach resolvent
Corrected: eliminated block AND full resolvent matrix invertible. Paper VI proof reused.

### 10.1 — Finite Euclidean transfer
Positivity, spectral interval and semigroup assertions remain.

### 11.1 — Low-mode second-order bound
Explicit h != 0; stronger all-real-frequency bound with constant 1/12. Paper VI proof reused.

## Separate continuum boundary
Conjectures 12.1–12.5 are not proved by this release. The first-block Feshbach invertibility correction and constraint-compression audit remain in force.
