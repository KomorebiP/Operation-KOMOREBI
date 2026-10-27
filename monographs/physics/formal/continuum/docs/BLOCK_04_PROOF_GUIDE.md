# Block 04 — Tensor atlases, reduced states and information transport

Komorebi Physics Lean v0.4.0. Source: *Projector-Refinement Physics: Complete Unified Theory*, 550 pages, physical PDF pages 24–25 (printed 11–12). The authoritative cumulative result is `verification/final/report.json`. The partial-trace and entanglement infrastructure extends the literal source block and is identified separately below.

## Scope and declaration counts

| New module | Theorems | Definitions | Role |
|---|---:|---:|---|
| `TensorAtlas` | 17 | 1 | Actual tensor atlas, marginal identities, joint probabilities and derivatives |
| `PartialTrace` | 32 | 2 | Actual reduced matrices, positivity, trace, algebra and derivatives |
| `InformationTransport` | 12 | 3 | Shannon, real-order moments and Rényi derivatives from actual trajectories |
| `EntanglementWitness` | 5 | 2 | Finite product-mixture obstruction via partial transpose |
| `QuantumInformationExamples` | 28 | 7 | Exact Bell-state and information-rate witnesses and counterexamples |
| **Block 04** | **94** | **15** | 66 general/support and 28 exact-example theorem declarations |

The cumulative inventory contains **304 theorems**, **372 named declarations**, and **20 mathematical modules**. The 210 previous theorem declarations and all 15 previous mathematical source files are preserved unchanged and freshly recompiled. Counts describe formal declarations, including support lemmas, not independent discoveries or a full-edition completion percentage.

## 1. Constructing the actual tensor atlas: (4.23)–(4.28)

For finite matrix spaces with complete orthogonal atlases P and Q, `MixedTransfer.MatrixAtlas.tensor` constructs

    R_(i,j) = P_i ⊗ₖ Q_j.

The symbol ⊗ₖ is the actual matrix Kronecker product indexed by pairs. The construction proves Hermiticity, the complete resolution, and

    R_(i,j) R_(k,l) = if (i,j)=(k,l) then R_(i,j) else 0.

These laws are not assumed as fields for a separately postulated joint atlas. The proof uses Kronecker multiplication and the original fine-atlas laws. The proof-bearing construction is included in the axiom audit.

`tensor_sum_right_proj` and `tensor_sum_left_proj` prove

    ∑ j, R_(i,j) = P_i ⊗ₖ I,
    ∑ i, R_(i,j) = I ⊗ₖ Q_j.

`tensor_coarsen_fst_proj` and `tensor_coarsen_snd_proj` identify those expressions with the actual Block 03 coarsening construction. Thus forgetting a subsystem label is genuinely a coarse projector resolution, not merely a diagrammatic convention.

For **every joint matrix** rho, including nonproduct inputs, the complex trace identities are

    ∑ j, Tr(R_(i,j) rho) = Tr((P_i ⊗ₖ I) rho),
    ∑ i, Tr(R_(i,j) rho) = Tr((I ⊗ₖ Q_j) rho).

These are `tensor_marginal_left_trace` and `tensor_marginal_right_trace`. They need neither product-state factorization nor positivity. Under Hermiticity, the previous `probability_cast` theorem identifies the real-valued probability definition with the literal complex trace. Under rho ≥ 0 and Tr(rho)=1, `tensor_probability_normalized` proves nonnegative normalized joint probabilities bounded above by one.

`tensor_product_probability` proves factorization **only when the input is an actual product of two Hermitian matrices**. No factorization theorem is asserted for an arbitrary joint state. `tensor_hasDerivAt_probability` connects the constructed joint atlas to the actual joint matrix evolution from Block 03; its Hamiltonian need not be a sum of uncoupled local generators.

## 2. Actual partial traces: additional infrastructure

The two reduced matrices are defined entrywise, not axiomatized:

    PartialTrace.left  rho a b = ∑ u, rho (a,u) (b,u),
    PartialTrace.right rho u v = ∑ a, rho (a,u) (a,v).

The proofs establish additivity, scalar compatibility, adjoint compatibility, Hermiticity, and

    Tr(left rho) = Tr(rho) = Tr(right rho).

Positive semidefiniteness is proved by writing each partial trace as a finite sum of principal submatrices. Consequently, PSD and trace-one input yield PSD and trace-one reduced states. This is a theorem about the reduction of an already positive matrix; it is **not** a positivity-preservation theorem for an ODE from initial data.

The product identities retain the trace of the discarded factor:

    left(A ⊗ₖ B)  = Tr(B) • A,
    right(A ⊗ₖ B) = Tr(A) • B.

Dropping that factor is valid only after appropriate normalization. The exact identity example gives left(I₂ ⊗ₖ I₂)=2I₂.

Local multiplication and remote cyclicity identities are also proved, with operator order retained. These are algebraic ingredients for later subsystem dynamics. They are not being counted as a separately completed open-system closure or no-signalling program.

`trace_local_left`, `trace_local_right`, `probability_left` and `probability_right` connect the source marginal formulas to the actual reduced states:

    p_i^A = Re Tr(P_i left(rho)),
    p_j^B = Re Tr(Q_j right(rho)).

Given an actual matrix derivative `HasDerivAt rho v t`, the entrywise derivative and finite-sum chain prove

    HasDerivAt (fun s => left (rho s)) (left v) t,
    HasDerivAt (fun s => right (rho s)) (right v) t.

No derivative of the reduced state is independently assumed. All these results are explicitly finite-dimensional.

## 3. A genuine correlated and entangled joint-state witness

The Bell density is constructed exactly as

    rho_B = (1/2) (|00>+|11>)(<00|+<11|).

All entries are zero or rational complex numbers. Lean proves PSD, trace one, and rho_B²=rho_B. Both actual partial traces are I₂/2, and those reduced matrices are not idempotent.

For the two coordinate atlases, the joint probability table is

    [[1/2, 0],
     [0, 1/2]],

while both marginal probability vectors are (1/2,1/2). In particular p_00=1/2, not the product 1/4. The joint density differs from the tensor product of its marginals. The dephased diagonal state diag(1/2,0,0,1/2) is separately proved PSD and trace one, has the same two reduced states, and differs from the coherent Bell density. Thus matching marginals does not recover the joint coherences.

### Stronger than simply showing nonfactorization

`EntanglementWitness.HasFiniteProductDecomposition` explicitly means the existence of a finite representation

    rho = ∑ r, w_r (|u_r><u_r| ⊗ₖ |v_r><v_r|),   w_r ≥ 0.

There is no normalization restriction on local vectors or weights. This is a larger cone than normalized convex mixtures of product pure states. We do not claim a separately formalized equivalence with every abstract definition of separability.

The partial transpose is constructed by swapping the second-factor matrix indices. Entrywise calculation proves that the partial transpose of a pure product is the rank-one matrix of u ⊗ conjugate(v), hence PSD. Finite nonnegative sums are then PSD as well. **Positive partial transpose is derived from the decomposition, not an input field of the decomposition.**

For w=|01>-|10>, the exact Bell calculation proves

    w* PT_B(rho_B) w = -1.

This violates PSD. `bell_not_finite_product_mixture` therefore excludes **every finite nonnegative product-pure-state mixture**, not just rho_A ⊗ rho_B. These are exact mathematical checks, not a claim of a newly discovered entanglement criterion or empirical evidence.

## 4. Actual packet information derivatives: (4.35)–(4.44)

For a finite index set, assume actual component derivatives p_i' = ∑_j J_ij at a time t and current antisymmetry J_ij=-J_ji. The central weighted-sum theorem proves

    ∑ i, g_i ∑ j, J_ij = (1/2) ∑ i,j, J_ij (g_i-g_j).

`hasDerivAt_functional` combines this proved identity with the actual chain rule for a general differentiable scalar functional. At the abstract level, component balance is explicitly an input. In the matrix specializations below, that input is discharged from the original density-matrix evolution.

### Shannon packet entropy

With strictly positive p_i(t),

    S(p) = -∑ i, p_i log(p_i),
    S'   = -∑ i, (1+log(p_i)) p_i'
         = -(1/2) ∑ i,j, J_ij log(p_i/p_j).

The first derivative is derived by differentiating x log x; the second comes from antisymmetric symmetrization. Strict positivity is an explicit hypothesis at the differentiation time. The derivative and logarithm domain are not supplied as a preproved entropy-balance field.

This is **packet/measurement Shannon entropy**, not the von Neumann entropy of the joint density operator. Antisymmetry alone gives an identity, not a sign for entropy production.

### Arbitrary fixed real-order moments

For every fixed real q on the same positive domain,

    M_q(p) = ∑ i, p_i^q,
    M_q'   = (q/2) ∑ i,j, J_ij (p_i^(q-1)-p_j^(q-1)).

The exponent is the actual real power, not a natural-number-only surrogate. Negative real q are included because bases are strictly positive. The order q is fixed while differentiating in time.

### Rényi derivative with its missing domain condition made explicit

For a nonempty finite family, positivity proves M_q>0. With **q≠1**,

    H_q(p) = log(M_q(p))/(1-q),
    H_q'   = q/[2(1-q) M_q(p)] ∑ i,j, J_ij (p_i^(q-1)-p_j^(q-1)).

The positive moment is proved and used to discharge the logarithm denominator. The source's displayed denominator is not interpreted at q=1. Lean's totalized division does not supply the Shannon limit, and that limit is not proved in this release.

Normalization ∑p_i=1 is not needed for these derivative identities as identities of functions on the positive orthant. It is required when interpreting them as entropies of a probability distribution. The quantum application obtains normalized probabilities from an independently positive trace-one density.

### Direct connection to the original quantum dynamics

`MatrixAtlas.hasDerivAt_packet_entropy`, `hasDerivAt_packet_powerSum` and `hasDerivAt_packet_renyi` start from Hermitian H and rho(t), the original equation

    HasDerivAt rho (generator H (rho t)) t,

and strict packet positivity. They instantiate the old proved probability derivatives and current antisymmetry, then apply the new information theorems. They do **not** assume a separate entropy evolution equation.

A PSD state may have zero packet probabilities. The Bell coordinate joint table above has two zeros, so it does not meet the strict-positivity hypothesis for this joint entropy-derivative theorem. No blanket differentiability at zero probability is asserted.

## 5. Exact information-rate and rejection tests

At t=0, use the actual affine trajectories

    p_0(t)=1/4+a t,    p_1(t)=3/4-a t,
    J_01=a,           J_10=-a.

Lean proves their actual component derivatives, antisymmetric current, normalized total, and strict positivity at t=0. The general theorems yield exact rates

    S'(0)=a log 3,    M_2'(0)=-a,    H_2'(0)=8a/5.

Choosing a=1 gives a positive Shannon rate; choosing a=-1 gives a negative rate. The affine trajectories are local witnesses and are not claimed to remain positive at every real time.

Eight new isolated invalid controls reject: universal joint probability factorization, joint reconstruction from marginals, a finite product-mixture representation of the Bell density, omission of the partial-trace normalization factor, the wrong Shannon sign, a universal entropy-increase claim, the wrong Rényi factor, and removal of current antisymmetry from weighted balance. Expected proof diagnostics are checked; imports, timeouts and tool failures do not qualify as successful rejection.

## 6. Verification and remaining boundaries

The cumulative verifier rebuilds all 20 mathematical modules plus the aggregate, audits 372 named declarations, checks all 23 invalid controls, and checks byte preservation of all 15 previous mathematical source modules. Only `propext`, `Classical.choice` and `Quot.sound` are permitted dependencies. Active proofs contain no admissions or custom axioms.

Lean is 4.34.0-rc2; Mathlib is pinned to `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. All nine dependency repositories are checked for exact revisions and clean tracked trees. Imported Lean/Mathlib compiled caches are used, not independently rebuilt wholesale. Runtime restoration support, but not the multi-gigabyte runtime, is included.

This block does not prove ODE existence/uniqueness, density positivity from initial data, q=1 or zero-probability entropy limits, general entropy monotonicity, infinite-dimensional partial traces, countable/unbounded limits, Lindblad reduction, gravity, cosmology or empirical adequacy. The next literal source target is Chapter 4.7, equations (4.45)–(4.52).
