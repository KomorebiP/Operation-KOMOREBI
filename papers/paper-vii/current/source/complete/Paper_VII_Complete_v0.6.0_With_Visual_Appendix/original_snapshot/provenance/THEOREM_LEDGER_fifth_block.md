# Paper VII coverage ledger: checked fifth block

**18 of 19 named finite-sector items are fully Lean checked.** Item 6.4 remains partial. The five continuum conjectures are outside this finite ledger and remain unproved.

Declaration totals include supporting lemmas and specializations: 256 across 20 modules, with 55 new declarations in this block.

| Item | Title | Status | Principal module |
|---|---|---|---|
| 2.1 | Orbit dimension of one quantum seed | Complete | SeedOrbit |
| 2.2 | Quantum seed-rank formula | Complete | SeedOrbit |
| 2.3 | Local orbit and Schmidt rank | Complete | SeedOrbit |
| 2.4 | One seed for the computational basis | Complete | ComputationalSeed |
| 3.1 | Cyclic quantum projectors | Complete | CyclicProjectors |
| 3.2 | Tensor/polyphase refinement | Complete | TensorRefinement |
| 4.1 | Exact circuit path expansion | Complete | QuantumPacketCore |
| 4.2 | Packetwise unitarity conservation | Complete | QuantumPacketCore |
| 5.1 | Exact symmetry packets | Complete | QuantumPacketCore |
| 5.2 | Commutator leakage bound | Complete | LeakageBound |
| 6.1 | Moving-frame Hamiltonian | Complete | MovingFrames |
| 6.3 | Canonical packet connection | Complete | CanonicalConnection |
| 6.4 | Projected connection | Partial | ProjectedCurvature |
| 7.1 | Block-diagonal measurement invariance | Complete | QuantumPacketCore |
| 7.2 | Finite Kraus channel | Complete | KrausChannels |
| 8.1 | Finite Knill-Laflamme criterion | Complete | QuantumStateBridge |
| 9.1 | Exact Feshbach resolvent | Complete | SchurFeshbach |
| 10.1 | Finite Euclidean transfer | Complete | EuclideanTransfer |
| 11.1 | Low-mode second-order bound | Complete | LowModeConvergence |

## Exact scopes

### 2.1 — Orbit dimension of one quantum seed
Actual matrix multiplication orbit, explicit equivalence with independently chosen rows, d times rank(C), and full-rank cyclicity when d is nonempty. No orbit-dimension hypothesis is assumed.

Main declaration: `KomorebiPaperVII.SeedOrbit.span_orbit_dimension`.

### 2.2 — Quantum seed-rank formula
Actual sums of k matrix actions, full-column-rank seed construction, simultaneous finite direct-sum generation, and an IsLeast proof for max_i ceil(m_i/d_i). Every d_i is positive. Empty block families use supremum 0.

Main declaration: `KomorebiPaperVII.SeedOrbit.quantum_seed_rank`.

### 2.3 — Local orbit and Schmidt rank
Actual Kronecker local action in standard product coordinates. Schmidt rank is independently defined as minimum product-vector decomposition length, with its equality to matrix rank proved. Derives local orbit dimension and equivalence with full support of the actual B-reduced matrix; the full-orbit equivalence assumes a nonempty A index.

Main declaration: `KomorebiPaperVII.SeedOrbit.local_orbit_reduced_support`.

### 2.4 — One seed for the computational basis
Explicit local Pauli X addressing for every n, including n=0. The constructed gate word sends the zero seed to the standard coordinate basis, with linear independence, span and cardinality 2^n.

Main declaration: `KomorebiPaperVII.ComputationalSeed.circuit_seed_basis`.

### 3.1 — Cyclic quantum projectors
Constructs the primitive complex character and rho(r)=S^val(r) from S^N=1 for every N>0, including N=1. Proves exact exponential-root coefficient formula, character orthogonality, multiplication, completeness, eigenaction, and self-adjointness for unitary S. Includes a concrete complex-matrix theorem.

Main declaration: `KomorebiPaperVII.CyclicProjectors.finite_cyclic_projectors`.

### 3.2 — Tensor/polyphase refinement
Arbitrary finite tensor factors and dimensions. Proves tensor product multiplication, identity, adjoint and sum laws, then orthogonality, completeness and self-adjointness after grouping by total residue for N>0.

Main declaration: `KomorebiPaperVII.TensorRefinement.tensor_polyphase_refinement`.

### 4.1 — Exact circuit path expansion
Arbitrary finite gate list, corner expansion and complete reconstruction.

### 4.2 — Packetwise unitarity conservation
Both identities in a star ring, plus concrete complex-matrix specializations.

### 5.1 — Exact symmetry packets
Generator blocks and actual exponential; zero cross-packet transfer.

### 5.2 — Commutator leakage bound
Actual exponential with self-adjoint H and orthogonal P. Proves the Hilbert operator-norm bound for all real times, without nonzero-rank or nonempty-matrix assumptions. Also proves observable-conjugation Lipschitz continuity, the cap at one, and a symmetry-breaking perturbation estimate.

Main declaration: `KomorebiPaperVII.Leakage.matrix_commutator_leakage_bound`.

### 6.1 — Moving-frame Hamiltonian
Entrywise actual real derivatives of finite complex matrices and vectors. Constructs y=U*psi and its derivative, verifies the transformed Schrodinger equation and Hermiticity. The effective-Hamiltonian Hermiticity conclusion explicitly assumes H*=H.

Main declaration: `KomorebiPaperVII.MovingFrames.moving_frame_coordinates`.

### 6.3 — Canonical packet connection
Actual derivatives in a normed real star algebra with continuous star. Differentiates projector multiplication, completeness and self-adjointness to prove both formulas for C, skew-adjointness and [C,P_b]=dot(P_b). Does not include manifold curvature.

Main declaration: `KomorebiPaperVII.Connection.canonical_connection_of_hasDerivAt`.

### 6.4 — Projected connection
Actual Frechet derivatives and actual vector fields on arbitrary normed parameter spaces. Proves range preservation, connection Leibniz rule, the full Lie-bracket curvature formula, bilinearity and alternation, and pullback under differentiable reparameterization. The global smooth range-bundle construction and chart gluing over arbitrary manifolds are not formalized.

Main declaration: `KomorebiPaperVII.Curvature.projected_connection_curvature`.

### 7.1 — Block-diagonal measurement invariance
Trace duality, measurement invariance and trace preservation for finite complex matrices.

### 7.2 — Finite Kraus channel
Finite complex matrix Kraus map: linearity, positivity, trace preservation under sum(K* K)=I, identity-tensor amplification at every finite auxiliary dimension, complete positivity and density-matrix preservation.

Main declaration: `KomorebiPaperVII.Kraus.channel_completely_positive`.

### 8.1 — Finite Knill-Laflamme criterion
Full finite complex-matrix Knill-Laflamme criterion. Constructs a total completely positive trace-preserving recovery from general positive semidefinite Gram data using actual spectral diagonalization, positive-eigenvalue support and proof that null errors vanish. Derives necessity from actual recovery via rank-one Kraus rigidity. Proves equivalence for normalized code density matrices, preservation with arbitrary finite references, the unnormalized error-family criterion with an explicit nonnegative scale, and correction of every normalized channel in the same error span by the same recovery. Zero code is handled separately. This is a mathematical, noncomputable spectral construction, not a numerical decoder implementation.

Main declaration: `KomorebiPaperVII.KnillLaflamme.state_correctable_iff_gram`.

### 9.1 — Exact Feshbach resolvent
Corrected: eliminated block AND full resolvent matrix invertible. Paper VI proof reused.

### 10.1 — Finite Euclidean transfer
Actual power-series matrix exponential, identified with continuous functional calculus. Constructs the minimum eigenvalue on a nonempty finite state space, proves positive definiteness, semigroup composition, and real and complex spectrum containment in (0,1] for nonnegative time.

Main declaration: `KomorebiPaperVII.EuclideanTransfer.finite_euclidean_transfer`.

### 11.1 — Low-mode second-order bound
Explicit h != 0; stronger all-real-frequency bound with constant 1/12. Paper VI proof reused.

