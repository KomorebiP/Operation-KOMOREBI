# Paper VII finite theorem ledger

**Release:** v0.6.0. **Author:** Komorebi P.

All 19 named finite-sector items have Lean coverage under the exact assumptions recorded below. This is a finite-item inventory, not a line-by-line claim about every sentence or calculation in the preserved original manuscript. All five continuum conjectures remain unproved.

| Item | Kind | Title | Status |
|---|---|---|---|
| 2.1 | Theorem | Orbit dimension of one quantum seed | LEAN_CHECKED |
| 2.2 | Theorem | Quantum seed-rank formula | LEAN_CHECKED |
| 2.3 | Corollary | Local orbit and Schmidt rank | LEAN_CHECKED |
| 2.4 | Theorem | One seed for the computational basis | LEAN_CHECKED |
| 3.1 | Theorem | Cyclic quantum projectors | LEAN_CHECKED |
| 3.2 | Theorem | Tensor/polyphase refinement | LEAN_CHECKED |
| 4.1 | Theorem | Exact circuit path expansion | LEAN_CHECKED |
| 4.2 | Theorem | Packetwise unitarity conservation | LEAN_CHECKED |
| 5.1 | Theorem | Exact symmetry packets | LEAN_CHECKED |
| 5.2 | Theorem | Commutator leakage bound | LEAN_CHECKED |
| 6.1 | Theorem | Moving-frame Hamiltonian | LEAN_CHECKED |
| 6.3 | Theorem | Canonical packet connection | LEAN_CHECKED |
| 6.4 | Classical input | Projected connection | LEAN_CHECKED |
| 7.1 | Theorem | Block-diagonal measurement invariance | LEAN_CHECKED |
| 7.2 | Classical input | Finite Kraus channel | LEAN_CHECKED |
| 8.1 | Classical input | Finite Knill-Laflamme criterion | LEAN_CHECKED |
| 9.1 | Theorem | Exact Feshbach resolvent | LEAN_CHECKED |
| 10.1 | Theorem | Finite Euclidean transfer | LEAN_CHECKED |
| 11.1 | Theorem | Low-mode second-order bound | LEAN_CHECKED |

## 2.1: Orbit dimension of one quantum seed
Actual matrix multiplication orbit, explicit equivalence with independently chosen rows, d times rank(C), and full-rank cyclicity when d is nonempty. No orbit-dimension hypothesis is assumed.

Principal declaration: `KomorebiPaperVII.SeedOrbit.span_orbit_dimension`.

## 2.2: Quantum seed-rank formula
Actual sums of k matrix actions, full-column-rank seed construction, simultaneous finite direct-sum generation, and an IsLeast proof for max_i ceil(m_i/d_i). Every d_i is positive. Empty block families use supremum 0.

Principal declaration: `KomorebiPaperVII.SeedOrbit.quantum_seed_rank`.

## 2.3: Local orbit and Schmidt rank
Actual Kronecker local action in standard product coordinates. Schmidt rank is independently defined as minimum product-vector decomposition length, with its equality to matrix rank proved. Derives local orbit dimension and equivalence with full support of the actual B-reduced matrix; the full-orbit equivalence assumes a nonempty A index.

Principal declaration: `KomorebiPaperVII.SeedOrbit.local_orbit_reduced_support`.

## 2.4: One seed for the computational basis
Explicit local Pauli X addressing for every n, including n=0. The constructed gate word sends the zero seed to the standard coordinate basis, with linear independence, span and cardinality 2^n.

Principal declaration: `KomorebiPaperVII.ComputationalSeed.circuit_seed_basis`.

## 3.1: Cyclic quantum projectors
Constructs the primitive complex character and rho(r)=S^val(r) from S^N=1 for every N>0, including N=1. Proves exact exponential-root coefficient formula, character orthogonality, multiplication, completeness, eigenaction, and self-adjointness for unitary S. Includes a concrete complex-matrix theorem.

Principal declaration: `KomorebiPaperVII.CyclicProjectors.finite_cyclic_projectors`.

## 3.2: Tensor/polyphase refinement
Arbitrary finite tensor factors and dimensions. Proves tensor product multiplication, identity, adjoint and sum laws, then orthogonality, completeness and self-adjointness after grouping by total residue for N>0.

Principal declaration: `KomorebiPaperVII.TensorRefinement.tensor_polyphase_refinement`.

## 4.1: Exact circuit path expansion
Arbitrary finite gate list, corner expansion and complete reconstruction.

## 4.2: Packetwise unitarity conservation
Both identities in a star ring, plus concrete complex-matrix specializations.

## 5.1: Exact symmetry packets
Generator blocks and actual exponential; zero cross-packet transfer.

## 5.2: Commutator leakage bound
Actual exponential with self-adjoint H and orthogonal P. Proves the Hilbert operator-norm bound for all real times, without nonzero-rank or nonempty-matrix assumptions. Also proves observable-conjugation Lipschitz continuity, the cap at one, and a symmetry-breaking perturbation estimate.

Principal declaration: `KomorebiPaperVII.Leakage.matrix_commutator_leakage_bound`.

## 6.1: Moving-frame Hamiltonian
Entrywise actual real derivatives of finite complex matrices and vectors. Constructs y=U*psi and its derivative, verifies the transformed Schrodinger equation and Hermiticity. The effective-Hamiltonian Hermiticity conclusion explicitly assumes H*=H.

Principal declaration: `KomorebiPaperVII.MovingFrames.moving_frame_coordinates`.

## 6.3: Canonical packet connection
Actual derivatives in a normed real star algebra with continuous star. Differentiates projector multiplication, completeness and self-adjointness to prove both formulas for C, skew-adjointness and [C,P_b]=dot(P_b). Does not include manifold curvature.

Principal declaration: `KomorebiPaperVII.Connection.canonical_connection_of_hasDerivAt`.

## 6.4: Projected connection
Smooth real boundaryless parameter manifolds modeled on a complete normed space; complete real normed fibers, including finite quantum spaces through underlying real calculus. Constructs the actual range total space, open local product homeomorphisms, smooth fiber-linear transitions, inverse and cocycle laws, and locally constant rank. Proves local smooth-section equivalence, the actual global covariant derivative, connection laws and gauge gluing. Derives curvature using actual manifold derivatives and the actual Lie bracket, and proves tensoriality. Uses an explicit smooth atlas rather than a packaged Mathlib ContMDiffVectorBundle instance. No global chart, pre-existing range-bundle atlas or curvature identity is assumed.

Principal declaration: `KomorebiPaperVII.ManifoldCurvature.projected_connection_curvature`.

## 7.1: Block-diagonal measurement invariance
Trace duality, measurement invariance and trace preservation for finite complex matrices.

## 7.2: Finite Kraus channel
Finite complex matrix Kraus map: linearity, positivity, trace preservation under sum(K* K)=I, identity-tensor amplification at every finite auxiliary dimension, complete positivity and density-matrix preservation.

Principal declaration: `KomorebiPaperVII.Kraus.channel_completely_positive`.

## 8.1: Finite Knill-Laflamme criterion
Full finite complex-matrix Knill-Laflamme criterion. Constructs a total completely positive trace-preserving recovery from general positive semidefinite Gram data using actual spectral diagonalization, positive-eigenvalue support and proof that null errors vanish. Derives necessity from actual recovery via rank-one Kraus rigidity. Proves equivalence for normalized code density matrices, preservation with arbitrary finite references, the unnormalized error-family criterion with an explicit nonnegative scale, and correction of every normalized channel in the same error span by the same recovery. Zero code is handled separately. This is a mathematical, noncomputable spectral construction, not a numerical decoder implementation.

Principal declaration: `KomorebiPaperVII.KnillLaflamme.state_correctable_iff_gram`.

## 9.1: Exact Feshbach resolvent
Corrected: eliminated block AND full resolvent matrix invertible. Paper VI proof reused.

## 10.1: Finite Euclidean transfer
Actual power-series matrix exponential, identified with continuous functional calculus. Constructs the minimum eigenvalue on a nonempty finite state space, proves positive definiteness, semigroup composition, and real and complex spectrum containment in (0,1] for nonnegative time.

Principal declaration: `KomorebiPaperVII.EuclideanTransfer.finite_euclidean_transfer`.

## 11.1: Low-mode second-order bound
Explicit h != 0; stronger all-real-frequency bound with constant 1/12. Paper VI proof reused.

## Conjectures and preserved amendments
The five continuum conjectures are not theorem targets in the finite ledger. Earlier corrections, notably the full-resolvent invertibility assumption for the Feshbach identity, remain part of the checked interpretation. The unchanged original PDF has not been silently rewritten. See the earlier supplements and the first-block amendments.
