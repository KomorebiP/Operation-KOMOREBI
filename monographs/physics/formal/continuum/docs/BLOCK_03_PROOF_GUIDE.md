# Block 03 — Nonlinear flow, refinement towers and mixed-state transfer

Komorebi Physics Lean v0.3.0. Source: *Projector-Refinement Physics: Complete Unified Theory*, 550 pages, physical PDF pages 23–24 (printed 10–11). The authoritative machine result is `verification/final/report.json`. This guide describes mathematical consequences under explicit assumptions, not a physical validation of the later theory.

## Scope and counts

| New module | Theorem declarations | Main role |
|---|---:|---|
| `NonlinearFlow` | 9 | Actual nonlinear-flow energy derivatives and global conservation |
| `RefinementTower` | 20 | Address-map and incidence-matrix composition, actual atlas quantities |
| `MixedTransfer` | 31 | Actual density-matrix trace derivatives, probabilities, currents and coarsening |
| `UniversalBalance` | 7 | Source-driven subsystem and coarse balance |
| `ExtensionExamples` | 16 | Exact nonzero mixed-state witnesses and hypothesis-sensitivity tests |
| **Block 03** | **83** | 67 general/support theorems and 16 exact example theorems |

The cumulative library contains 210 theorem declarations: 39 recovered Paper VII, 37 Block 01, 51 Block 02 and 83 Block 03. The inventory has 263 named declarations, including structures and proof-bearing definitions. These are declaration counts, not a count of independent new physical laws or a measure of full-edition completion.

## 1. State-dependent skew flow: equations (4.1)–(4.5)

Let H be a complex inner-product space, P a finite complete orthogonal atlas, and

    A : H → ℝ → (H →L[ℂ] H).

At a particular time t the assumptions are:

    HasDerivAt ψ (A (ψ t) t (ψ t)) t
    IsSkew (A (ψ t) t).

The first assumption is the actual derivative of the original vector trajectory. The second is skew-adjointness in the inner-product sense at the operator actually visited by that trajectory. Neither an energy derivative nor a current-balance law is supplied as an assumption.

With E_i(t) = ‖P_i ψ(t)‖² and J_ij(t) = 2 Re ⟨P_i ψ(t), A(ψ(t),t)P_j ψ(t)⟩, the new module proves the derivative of E_i is the row sum of J, current antisymmetry, zero total current, zero derivative of total packet energy, and the actual subsystem boundary-flux derivative. Coarse energy derivatives follow through the actual coarse atlas constructed in Block 01.

`hasDerivAt_total` also proves the derivative of ‖ψ‖² is zero. `total_constant` and `sum_packets_constant` turn the all-real-time flow hypotheses into equality of the total quantities at any two real times by the mean value theorem.

No derivative of the generator map A is needed for these first-order statements: differentiating the energy uses ψ′, then evaluates the already-supplied flow equation at t. This does not remove the separate assumptions needed to prove existence or uniqueness of a solution. The global statements assume an actual trajectory on all of ℝ; interval and maximal-solution interfaces have not been added in this block. Skewness away from that trajectory is unnecessary for these conclusions.

## 2. Associative refinement: equations (4.16)–(4.22)

For finite address spaces I,J,K, let f:I→J and g:J→K. Define the exact fiber pushforward

    push f x a = ∑ i, if f i = a then x i else 0.

`push_comp` proves

    push g (push f x) = push (g ∘ f) x

for any additive commutative monoid of values. This includes vectors and operators as well as scalar energies. The proof is a finite rearrangement with the unique intermediate address made explicit, not an assertion that the two expressions should be interpreted as equal.

`pushList_eq` proves the corresponding arbitrary finite-depth statement for a list of maps on one fixed finite label type. Two-stage composition permits different I,J,K; the list theorem does not pretend to be a dependent tower with arbitrary changing label types.

For real incidence matrices R(f) with entries 1 when f(i)=a and 0 otherwise, `incidence_comp` proves

    R(g ∘ f) = R(g) R(f).

The scalar pushforward is proved equal to incidence-matrix multiplication. For currents define C_R(J)=R J Rᵀ. Then

    C_S(C_R(J)) = C_(SR)(J).

The matrix identity holds for arbitrary real matrices with matching dimensions. The interpretation as a genuine orthogonal-atlas coarsening is separately tied to an address map.

The actual coarse-projector construction now satisfies sequential-versus-composed equality for projectors, packet vectors, operator corners, energies and currents. `coarsen_energy_incidence` and `coarsen_current_incidence` identify actual coarse physical quantities with R E and R J Rᵀ. The derivative theorem `hasDerivAt_tower_energy` ties this algebra back to actual time differentiation.

### An explicit hypothesis boundary

Entrywise membership in {0,1} alone is not enough to define a partition. Address-map incidence also guarantees exactly one target cell for every fine sector. For the 2×2 all-ones matrix R, every entry is binary but (R R)_00=2, and R is not the incidence of any address function. These facts are proved exactly in `ExtensionExamples`. This makes the partition assumption explicit; it does not claim that arbitrary overlapping binary weights preserve orthogonality.

## 3. Mixed-state transfer: equations (4.6)–(4.15)

This part is explicitly finite-dimensional. A `MatrixAtlas n I` contains the fine projector resolution, multiplication laws and Hermiticity. Its fields do not contain probabilities, antisymmetry, continuity or positivity conclusions.

The generator is the actual matrix expression

    generator H ρ = (-i) • (H ρ - ρ H).

Define

    amplitude H ρ i j = Tr(P_i H P_j ρ),
    current H ρ i j = 2 Im amplitude H ρ i j,
    probability ρ i = Re Tr(P_i ρ).

The real-part definition is not a hidden assumption about the complex trace. `trace_probability_real` proves the trace has zero imaginary part under Hermiticity of ρ, and `probability_cast` proves the real value cast to ℂ equals the literal trace in equation (4.7).

### The conjugation step

For H†=H and ρ†=ρ, trace cyclicity and the adjoint product rule give

    Tr(P_j H P_i ρ) = conjugate(Tr(P_i H P_j ρ)).

This is `amplitude_reverse`, equation (4.14). The source page image was read: the overbar is present even though the parsed text omits it. Taking imaginary parts gives J_ij=−J_ji. Omitting the bar gives a false equality in the exact example below.

### The derivative is actually derived

Given a matrix curve ρ(t) and the input

    HasDerivAt ρ (generator H (ρ t)) t,

`hasDerivAt_entry` derives actual coordinate derivatives by continuous linear evaluation. Finite summation and scalar multiplication then prove the derivative of Tr(B ρ(t)) is Tr(B ρ′(t)) for every fixed B. Applying the real-part continuous linear map and the resolved commutator identity yields

    HasDerivAt (fun s => P.probability (ρ s) i)
      (∑ j, P.current H (ρ t) i j) t.

Only the matrix equation, Hermiticity at the base point, and atlas laws are inputs. The probability derivative and current antisymmetry are conclusions. Internal current cancellation gives the actual probability derivative of every finite subsystem as its boundary flux. The total probability derivative is zero.

`trace_constant` separately proves all-time complex-trace conservation, including state- and time-dependent H along a given trajectory. Trace of a finite commutator vanishes even without Hermiticity; the Hermiticity assumptions are used for the physical real-current interpretation and antisymmetry, not for that algebraic trace identity.

### Positivity and normalization have their own proofs

`probability_nonneg` rewrites Tr(P_i ρ) as the trace of the positive sandwich P_i† ρ P_i, using projector idempotence and trace cyclicity. Positive semidefiniteness of ρ then implies p_i≥0.

`probability_normalized` combines positivity, the derived sum identity ∑p_i=Re Tr(ρ), and Tr(ρ)=1 to prove

    ∑ i, p_i = 1,       0 ≤ p_i ≤ 1.

Positive semidefiniteness and trace one are explicit inputs here. This is not yet a theorem that an initial positive state stays positive under a constructed flow. Generator Hermiticity is proved pointwise, not substituted for a positivity-preservation argument.

### Pure states and coarsening

The rank-one matrix |ψ⟩⟨ψ| is constructed as `pureState ψ` and is proved positive semidefinite. `trace_mul_pureState` proves the quadratic-pairing trace identity. `pureState_current` then yields equation (4.15), using the standard Hermitian dot product of finite complex vectors. Normalization of ψ is not needed for the current identity itself.

The mixed-state coarse atlas is constructed with its laws proved. Its probability is the sum over fine-sector probabilities, and its current is the exact double sum of fine currents. Sequential and composed coarse projectors agree. `hasDerivAt_coarse_probability` proves the actual coarse probability derivative expanded into those fine currents.

## 4. Universal source-driven balance: equations (4.29)–(4.34)

This interface starts from explicit scalar equations q_i′=s_i+∑_j F_ij, with F antisymmetric. Unlike the preceding quantum modules, this abstraction assumes the scalar balance law; it does not claim to derive a microscopic evolution equation.

For every finite subset C, it proves

    (∑_{i∈C} q_i)′ = ∑_{i∈C} s_i + ∑_{i∈C, j∉C} F_ij.

Coarse currents remain antisymmetric, and the actual derivative of a coarse scalar quantity is its coarse source plus its coarse current row sum. The total derivative is ∑_i s_i, not automatically zero. The exact example q_0(t)=q_1(t)=t has total derivative 2 and rejects the false source-free conclusion.

## 5. Exact nonzero witness and invalid alternatives

Take the coordinate atlas on ℂ² and

    ρ = [[1/2, 1/4], [1/4, 1/2]],
    H = [[0, -i], [i, 0]].

Lean proves H and ρ are Hermitian, ρ is positive semidefinite, Tr(ρ)=1, and ρ²≠ρ. Positivity is established by an exact positive factorization, not floating eigenvalues. The currents are

    J_(0←1) = -1/2,       J_(1←0) = +1/2.

The actual affine matrix curve ρ_loc(t)=ρ+t·generator(H,ρ) has the required von Neumann derivative at t=0. Applying the general theorem produces actual probability derivatives −1/2 and +1/2 at that time. This local affine curve is not asserted to solve the equation globally or to remain positive for all real t.

Further exact theorems show why density Hermiticity, Hamiltonian Hermiticity and the trace conjugation cannot be deleted. Six new intentionally invalid compilation controls test these three boundaries, the current sign, binary overlap without partition, and deletion of sources. They are isolated under `negative_controls/`; they must fail for the intended proof diagnostic. Import errors and timeouts do not count as successful rejection tests.

## 6. Verification and limitations

The cumulative verifier removes local compiled outputs and rebuilds all 15 mathematical modules plus the aggregate. It audits all 263 named declarations in bounded module batches, including the two new proof-bearing atlas definitions. Only `propext`, `Classical.choice` and `Quot.sound` are accepted axiom dependencies. All 15 negative controls must be correctly rejected. The ten Block 02 mathematical source files are checked against preserved SHA-256 hashes.

Lean is 4.34.0-rc2, Mathlib is `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, and all nine dependency repositories must be at their clean pinned revisions. The imported Lean/Mathlib compiled cache is used, not rebuilt wholesale. The multi-gigabyte runtime is not bundled.

This block does not prove ODE existence or uniqueness, positivity preservation from initial data, infinite-dimensional trace-class results, unbounded-generator domain statements, countable-atlas limits, tensor-product mixed-state marginals, information-transport formulas, Lindblad reduction, gravity, cosmology or empirical adequacy. The immediate next source targets are (4.23)–(4.28), then (4.35)–(4.44), then (4.45)–(4.52).
