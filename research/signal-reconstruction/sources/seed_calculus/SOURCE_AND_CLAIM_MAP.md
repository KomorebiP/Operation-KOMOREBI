# Source and Claim Map

**Work:** Projector-Resolved Seed Calculus from Seed to Reconstruction: Seven Complete Worked Realizations  
**Edition:** Complete seed-to-finish edition  
**Author:** Komorebi P.

## A. Complete dependency chain

The new first part develops the calculus in the following order.

### A1. Primitive seed and fixed grammar

- **Defined:** a typed seed system consists of an ambient space, a primitive seed family, a fixed admissible operator grammar, declared relations, packet families, and completion data.
- **Proved:** the generated hull is the span or closure of all admissible operator words applied to the seed family.
- **Proved:** seed rank is the minimum number of primitive generators under the declared grammar.
- **Master certificate:** for `s=e_0` and the cyclic shift `U` on `C^8`, the orbit matrix has rank eight, so one seed generates the full ambient space.
- **Primary source:** `proof_atlas/foundations.py`.
- **Figures:** `38_seed_to_reconstruction_pipeline` through `42_relation_quotient`.

### A2. Relations and quotient normal forms

- **Defined:** the free operator-word presentation and its quotient by declared relations.
- **Proved:** the relation `U^8=I` reduces every operator word to a unique representative of degree below eight in the cyclic model.
- **Certificate:** relation residual `0`.
- **Primary source:** `proof_atlas/foundations.py`.

### A3. Addresses and packet projectors

- **Defined:** coordinate, parity, residue-modulo-four, and Fourier addresses.
- **Proved:** each address family produces pairwise-annihilating projectors summing to the identity.
- **Proved:** coarse packets reconstruct from compatible fine descendants.
- **Certificate:** spatial and Fourier completeness residuals `0`.
- **Figures:** `43_address_refinement_tree`, `44_object_analysis_synthesis`, and `56_master_fourier_packets`.

### A4. Transfer algebra and path calculus

- **Proved:** for a complete packet family,
  \[
  T=\sum_{\alpha,\beta}P_\beta T P_\alpha.
  \]
- **Proved:** transfer blocks multiply by summing over intermediate packet addresses.
- **Proved:** the full block representation preserves sums, products, identities, and adjoints.
- **Master operator:** `T=2I-U+3U^2`.
- **Certificates:** transfer reconstruction and path residuals `0`.
- **Figures:** `45_transfer_support`, `46_operator_spatial_fourier`, `47_packet_path_sum`.

### A5. Refinement, coarsening, and transform atlases

- **Proved:** exact parent-child incidence gives inverse coordinate refinement and coarsening maps on complete packet ranges.
- **Proved:** an invertible transform `V` pulls ordinary coordinate selectors back to projectors `V^{-1}E_alpha V`.
- **Proved:** a weighted direct sum of unitary spatial, Fourier, and Haar atlases is a finite tight frame with explicit canonical synthesis.
- **Certificate:** multi-atlas residual `0`.
- **Figures:** `48_refinement_incidence`, `49_transform_atlas_portfolio`, `50_multi_atlas_tight_frame`.

### A6. Nonlinear interaction packets and obstruction packets

- **Proved:** a multilinear map decomposes into all source-packet interaction tensors followed by output projection.
- **Master nonlinear map:** `N(x)=x+(Ux)⊙(U^3x)`.
- **Certificate:** nonlinear packet reconstruction residual `0`.
- **Proved:** in finite Hilbert space, a correction datum is solvable exactly when its cokernel obstruction packet vanishes.
- **Certificates:** solvable obstruction `0`; blocked obstruction `(-1/3,-1/3,1/3)`.
- **Figures:** `51_nonlinear_hypergraph`, `52_obstruction_geometry`, `57_master_nonlinear_reconstruction`.

### A7. Completion and final reconstruction

- **Proved under stated hypotheses:** finite packet decompositions extend from a dense invariant core when the projectors and relevant operators extend continuously and the packet sum converges in the declared topology.
- **Boundary:** unbounded operators require domain preservation and closedness or closability; these conditions are stated rather than hidden.
- **Figures:** `53_completion_refinement_tower`, `54_master_example_pipeline`, `58_certificate_dashboard`, `60_theorem_dependency_ladder`.

## B. Seven retained worked areas

### B1. Finite linear algebra

- **Proved:** exact object reconstruction in `Q^6`.
- **Proved:** exact reconstruction of an operator from nine transfer blocks.
- **Proved:** exact packet path/product law for a second operator.
- **Proved:** exact parent-child refinement.
- **Sources:** `proof_atlas/linear.py`, `proof_atlas/details.py`.

### B2. Signals

- **Proved:** order-2 and order-4 polyphase extraction/interleaving.
- **Proved:** exact orthonormal Haar analysis and synthesis.
- **Proved:** exact unitary DFT reconstruction.
- **Proved:** completeness, idempotence, and mutual annihilation of Fourier-band projectors.
- **Sources:** `proof_atlas/signal.py`, `proof_atlas/details.py`.

### B3. Quantum information

- **Proved:** Bell-state preparation by Hadamard and CNOT.
- **Proved:** exact four-route parity path reconstruction, including zero routes.
- **Proved:** reduced one-qubit density matrix `I/2` and entropy one bit.
- **Sources:** `proof_atlas/quantum.py`, `proof_atlas/details.py`.

### B4. Probability and Bayesian coarsening

- **Proved:** conditional expectation is a weighted orthogonal projector.
- **Proved:** exact Bayesian coarsening when likelihoods are packet-constant.
- **Proved:** the finite necessary-and-sufficient sufficiency criterion.
- **Proved:** exact factorization of the information-loss defect.
- **Sources:** `proof_atlas/bayes.py`, `proof_atlas/details.py`.

### B5. Closed forms and arithmetic sequence

- **Proved:** root-sum, real trigonometric-exponential, and hypergeometric forms of the order-five signed denominator.
- **Proved:** reciprocal-square integer recurrence and independent composition formula.
- **Proved:** parameter-polynomial family for arbitrary reciprocal order.
- **Boundary:** the sequence is an exact candidate record; historical novelty is not asserted without a complete comparison.
- **Sources:** `proof_atlas/arithmetic.py`, `proof_atlas/details.py`.

### B6. Coupled-oscillator physics

- **Proved:** exact symmetric/antisymmetric spectral projectors and normal-mode solution.
- **Proved:** physical-coordinate reconstruction, ODE satisfaction, and energy partition.
- **Sources:** `proof_atlas/physics.py`, `proof_atlas/details.py`.

### B7. Nonlinear packets and holonomy

- **Proved:** exact even/odd packet reconstruction of a nonlinear memory-one filter.
- **Proved:** rational flat-holonomy telescoping.
- **Negative control:** a perturbed edge yields exact obstruction norm squared `8/5`.
- **Sources:** `proof_atlas/nonlinear_geometry.py`, `proof_atlas/details.py`.

## C. Independent verification layers

- `tests/test_foundations.py` - eleven seed-to-finish tests.
- `tests/test_proofs.py` - seven primary domain tests.
- `tests/test_z_independent_audit.py` - seven independent re-derivations.
- `tests/test_detailed_derivations.py` - seven detailed step audits.
- Final suite: **32/32 passed**.

## D. Figure and document map

- Figures `00`-`37`: retained detailed domain atlas.
- Figures `38`-`60`: new seed-to-reconstruction foundation atlas.
- Total: **61 vector-PDF and 61 PNG figures**.
- Final manuscript: **140 pages**.
- Complete render and contact sheet: `Projector_Resolved_Seed_Calculus_Seed_to_Reconstruction_Contact_Sheet.png`.

## E. Exact claim boundary

The manuscript proves the finite calculus and the explicitly stated completion theorem under its hypotheses. It does not claim that every object in every category has finite seed rank, that every unbounded operator respects every packet family, that every statistical packet can be learned consistently, or that the displayed physics examples determine a universal physical theory. The value of the work is the exact dependency-ordered construction, the nontrivial seven-area realization, the negative controls, and the explicit location of the hypotheses needed beyond finite dimension.
