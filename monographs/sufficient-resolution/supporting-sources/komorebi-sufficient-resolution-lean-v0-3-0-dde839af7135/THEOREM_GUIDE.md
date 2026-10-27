# Formula-to-source guide — cumulative v0.2.0

Sections 1–6 document the unchanged original block. The 57 new theorem declarations
are mapped to formulas in [BLOCK_02_THEOREMS.md](BLOCK_02_THEOREMS.md).


Notation: `S * T` applies `T` first. `i :: w` is chronological and applies
`T_i` before the remainder of the word. Statements below use their actual
Lean hypotheses, not stronger prose interpretations.

## 1. Exact representation with redundant coordinates

Let `a_X : X → V_X`, `s_X : V_X → X`, and `s_X a_X = I_X`.
Write `E_X = a_X s_X`, `K(T) = a_Y T s_X`, and `D(K) = s_Y K a_X`.

- `Resolution.projector_idempotent`: `E_X E_X = E_X`.
- `Resolution.fixed_iff_realizable`: `E_X v = v` iff `v = a_X x` for some `x`.
- `Resolution.decode_encode`: `D(K(T)) = T`.
- `Resolution.encode_decode`: `K(D(K)) = E_Y K E_X`.
- `Resolution.compatible_iff_existsUnique`: `E_Y K E_X = K` iff a unique global
  linear map has encoded kernel `K`.
- `Resolution.kernelEquiv` constructs both directions as an actual equivalence.
- `Resolution.encode_comp`: `K(ST) = K(S) K(T)`.

Scope: modules over a semiring, with additive commutative monoids. No finite
dimension or orthogonality is assumed. This representation result presupposes
the displayed split reconstruction maps. It does not produce arithmetic objects.

## 2. Compression and composition defects

Let `C : X → Z`, `R : Z → X`, `C R = I_Z`.
Set `P = R C`, `Q = I_X - P`, `Phi(T) = C T R` and
`Delta(S,T) = Phi(ST) - Phi(S) Phi(T)`.

- `SplitCompression.defect_factorization`:
  `Delta(S,T) = C S Q T R`.
- `SplitCompression.multiplicative_iff_hidden_return_zero`:
  exact multiplicativity for this pair iff that hidden return is zero.
- `SplitCompression.defect_coherence`:
  `Delta(S,T) Phi(U) + Delta(ST,U) = Phi(S) Delta(T,U) + Delta(S,TU)`.
- `SplitCompression.power_defect`:
  `Phi(T^(m+n)) - Phi(T^m) Phi(T^n) = C T^m Q T^n R`.
- `SplitCompression.powers_exact_of_lift_intertwining`:
  if `T R = R Phi(T)`, then `Phi(T^n) = Phi(T)^n` for every natural `n`.
- `SplitCompression.defect_then`:
  `Delta_21(S,T) = Phi_2(Delta_1(S,T)) + Delta_2(Phi_1(S),Phi_1(T))`.

These are identities over commutative-ring modules. The splitting is not assumed
orthogonal. Vanishing at one depth does not imply vanishing at every depth.

## 3. Linear globalization obstruction

For `G --A--> V --delta--> W`, assume `delta A = 0` when interpreting all global
realizations as compatible. Define

`H = ker(delta) / {v in ker(delta) : v belongs to range(A)}`.

- `Globalization.realizable_compatible`: `range(A) ≤ ker(delta)` under the chain condition.
- `Globalization.obstructionClass_zero_iff`: a compatible vector's actual quotient
  class is zero iff it has a preimage under `A`.
- `Globalization.all_obstructions_zero_iff_exact`: all classes vanish iff
  `range(A) = ker(delta)`, under the chain condition.
- `Globalization.unique_realization_of_zero`: a zero class has a unique realization
  provided `A` is injective.
- `Globalization.resolution_range_eq_kernel`: for a split resolution,
  `range(a) = ker(I-a s)`.

The quotient is not just a Boolean label. No theorem here says this quotient
vanishes for an arbitrary supplied presentation.

## 4. Transporting obstructions between presentations

A `PresentationMap` contains maps `F`, `L`, `M` satisfying
`L A = A' F` and `delta' L = M delta`.

- `PresentationMap.kernelMap` restricts `L` to compatible vectors.
- `PresentationMap.kernelMap_preserves_realizability` verifies that realizable
  vectors are carried to realizable vectors.
- `PresentationMap.obstructionMap` is the induced map `H → H'`.
- `PresentationMap.obstructionMap_class` gives its formula on classes.
- `PresentationMap.obstructionMap_compose` proves composition.
- `PresentationMap.transports_zero_obstruction` gives forward preservation.
- `PresentationMap.reflects_zero_obstruction` gives reflection only if the
  induced obstruction map is injective.

Thus local algebraic correspondences do not automatically supply globalization
or reflection. The necessary diagram data and extra injectivity are visible.

## 5. The behaviorally sufficient quotient

For arbitrary allowed endomorphisms `T_i` and observation `O`, set

`N = {x : for every finite word w, O(T_w x)=0}`.

- `Behavioral.invisible` constructs `N` as a submodule.
- `Behavioral.invisible_invariant` proves invariance under every `T_i`.
- `Behavioral.invariant_submodule_le_invisible` proves maximality among invariant
  submodules contained in `ker O`.
- `Behavioral.induced` and `Behavioral.observation` construct genuine quotient
  operations and observations on `X/N`.
- `Behavioral.all_future_observations_preserved` proves fidelity for every finite word.
- `Behavioral.quotient_eq_iff_same_future` characterizes equal quotient states by
  equal future observations.
- `Behavioral.exact_model_kernel_le`: if another model `q` intertwines all operations
  and factors the observation, then `ker q ≤ N`.
- `Behavioral.modelQuotientComparison` constructs the resulting comparison map.

The allowed operator alphabet need not be finite. The all-word condition is not
replaced by a sampled word list. Learning those operators from finite data is not
covered by the theorem.

## 6. Exact delayed return example

On rational triples, use `L(y,z1,z2)=(z1,z2,y)`, `C(y,z1,z2)=y`, `R(y)=(y,0,0)`.
The formal example proves

`Phi(L)=0`, `Phi(L^2)=0`, `Phi(L^3)=I`.

`Examples.correct_through_depth_two` and `Examples.fails_at_depth_three` therefore
establish a counterexample to extrapolating closure from the first two depths.
`Examples.delayed_return_defect` identifies the returning defect as the identity.

## Updated deferred claims from the brainstorm

Quantitative Hilbert-space error decomposition and norms; positivity-constrained
realizability; continuous-time Volterra/semigroup analysis; finite-dimensional behavioral
termination/minimal-dimension bounds; nonlinear
operads; categorical descent beyond the explicitly constructed linear
presentation maps; arithmetic existence and Langlands correspondence.

The discrete-memory and finite Cayley–Hamilton obligations formerly listed as
deferred are completed in v0.2.0. See BLOCK_02_THEOREMS.md for their exact scope.


## Block 03 continuation

The finite-observation horizon, dimension-minimality, actual finite-coordinate model,
finite minimality certificates and noncommuting example are mapped in
`BLOCK_03_THEOREMS.md`. All earlier source contracts are preserved.
