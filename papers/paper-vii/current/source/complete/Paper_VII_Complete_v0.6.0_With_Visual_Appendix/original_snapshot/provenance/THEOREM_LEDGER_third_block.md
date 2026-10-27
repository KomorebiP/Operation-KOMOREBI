# Paper VII finite coverage ledger

**Release:** v0.3.0, checked third block. **Author:** Komorebi P.

16 of 19 named finite items checked. Three finite items and all five continuum conjectures remain unproved in this release. Counts are not difficulty-weighted.

| Item | Title | Status | Module | First checked |
|---|---|---|---|---|
| 2.1 | Orbit dimension of one quantum seed | LEAN_CHECKED | SeedOrbit | v0.3.0 |
| 2.2 | Quantum seed-rank formula | LEAN_CHECKED | SeedOrbit | v0.3.0 |
| 2.3 | Local orbit and Schmidt rank | LEAN_CHECKED | SeedOrbit | v0.3.0 |
| 2.4 | One seed for the computational basis | LEAN_CHECKED | ComputationalSeed | v0.2.0 |
| 3.1 | Cyclic quantum projectors | LEAN_CHECKED | CyclicProjectors | v0.3.0 |
| 3.2 | Tensor/polyphase refinement | LEAN_CHECKED | TensorRefinement | v0.2.0 |
| 4.1 | Exact circuit path expansion | LEAN_CHECKED | QuantumPacketCore | v0.1.0 |
| 4.2 | Packetwise unitarity conservation | LEAN_CHECKED | QuantumPacketCore | v0.1.0 |
| 5.1 | Exact symmetry packets | LEAN_CHECKED | QuantumPacketCore | v0.1.0 |
| 5.2 | Commutator leakage bound | NOT_CHECKED_IN_THIS_RELEASE | - | - |
| 6.1 | Moving-frame Hamiltonian | LEAN_CHECKED | MovingFrames | v0.2.0 |
| 6.3 | Canonical packet connection | LEAN_CHECKED | CanonicalConnection | v0.2.0 |
| 6.4 | Projected connection | NOT_CHECKED_IN_THIS_RELEASE | - | - |
| 7.1 | Block-diagonal measurement invariance | LEAN_CHECKED | QuantumPacketCore | v0.1.0 |
| 7.2 | Finite Kraus channel | LEAN_CHECKED | KrausChannels | v0.2.0 |
| 8.1 | Finite Knill-Laflamme criterion | NOT_CHECKED_IN_THIS_RELEASE | - | - |
| 9.1 | Exact Feshbach resolvent | LEAN_CHECKED | SchurFeshbach | v0.1.0 |
| 10.1 | Finite Euclidean transfer | LEAN_CHECKED | EuclideanTransfer | v0.3.0 |
| 11.1 | Low-mode second-order bound | LEAN_CHECKED | LowModeConvergence | v0.1.0 |

## 2.1 - Orbit dimension of one quantum seed
Actual matrix multiplication orbit, explicit equivalence with independently chosen rows, d times rank(C), and full-rank cyclicity when d is nonempty. No orbit-dimension hypothesis is assumed.

## 2.2 - Quantum seed-rank formula
Actual sums of k matrix actions, full-column-rank seed construction, simultaneous finite direct-sum generation, and an IsLeast proof for max_i ceil(m_i/d_i). Every d_i is positive. Empty block families use supremum 0.

## 2.3 - Local orbit and Schmidt rank
Actual Kronecker local action in standard product coordinates. Schmidt rank is independently defined as minimum product-vector decomposition length, with its equality to matrix rank proved. Derives local orbit dimension and equivalence with full support of the actual B-reduced matrix; the full-orbit equivalence assumes a nonempty A index.

## 2.4 - One seed for the computational basis
Explicit local Pauli X addressing for every n, including n=0. The constructed gate word sends the zero seed to the standard coordinate basis, with linear independence, span and cardinality 2^n.

## 3.1 - Cyclic quantum projectors
Constructs the primitive complex character and rho(r)=S^val(r) from S^N=1 for every N>0, including N=1. Proves exact exponential-root coefficient formula, character orthogonality, multiplication, completeness, eigenaction, and self-adjointness for unitary S. Includes a concrete complex-matrix theorem.

## 3.2 - Tensor/polyphase refinement
Arbitrary finite tensor factors and dimensions. Proves tensor product multiplication, identity, adjoint and sum laws, then orthogonality, completeness and self-adjointness after grouping by total residue for N>0.

## 4.1 - Exact circuit path expansion
Arbitrary finite gate list, corner expansion and complete reconstruction.

## 4.2 - Packetwise unitarity conservation
Both identities in a star ring, plus concrete complex-matrix specializations.

## 5.1 - Exact symmetry packets
Generator blocks and actual exponential; zero cross-packet transfer.

## 5.2 - Commutator leakage bound
Quantitative Duhamel/norm estimate not supplied by the exact-commutation theorem.

## 6.1 - Moving-frame Hamiltonian
Entrywise actual real derivatives of finite complex matrices and vectors. Constructs y=U*psi and its derivative, verifies the transformed Schrodinger equation and Hermiticity. The effective-Hamiltonian Hermiticity conclusion explicitly assumes H*=H.

## 6.3 - Canonical packet connection
Actual derivatives in a normed real star algebra with continuous star. Differentiates projector multiplication, completeness and self-adjointness to prove both formulas for C, skew-adjointness and [C,P_b]=dot(P_b). Does not include manifold curvature.

## 6.4 - Projected connection
Range bundle, differential forms and curvature remain.

## 7.1 - Block-diagonal measurement invariance
Trace duality, measurement invariance and trace preservation for finite complex matrices.

## 7.2 - Finite Kraus channel
Finite complex matrix Kraus map: linearity, positivity, trace preservation under sum(K* K)=I, identity-tensor amplification at every finite auxiliary dimension, complete positivity and density-matrix preservation.

## 8.1 - Finite Knill-Laflamme criterion
Both necessity and constructive recovery remain.

## 9.1 - Exact Feshbach resolvent
Corrected: eliminated block AND full resolvent matrix invertible. Paper VI proof reused.

## 10.1 - Finite Euclidean transfer
Actual power-series matrix exponential, identified with continuous functional calculus. Constructs the minimum eigenvalue on a nonempty finite state space, proves positive definiteness, semigroup composition, and real and complex spectrum containment in (0,1] for nonnegative time.

## 11.1 - Low-mode second-order bound
Explicit h != 0; stronger all-real-frequency bound with constant 1/12. Paper VI proof reused.
