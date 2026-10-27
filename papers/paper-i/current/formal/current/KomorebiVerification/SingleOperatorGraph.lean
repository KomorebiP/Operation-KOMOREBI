import KomorebiVerification.MathlibImports
import KomorebiVerification.PathGraphKrylov
import KomorebiVerification.SeedRankBasics

/-!
# Single-operator and graph seed rank

This file isolates the algebraic content of the single-operator results in
Paper I.  Generation by `k[T]` is represented literally: each seed may be
acted on by an arbitrary polynomial in `T`, and the resulting vectors are
added.  The main theorem proves the maximum-geometric-multiplicity formula
from explicit primary-decomposition data.  Keeping the decomposition data as
hypotheses cleanly separates the elementary generator argument checked here
from the classical Jordan/primary-decomposition theorem.

The final section gives graph-facing consequences, including the already
constructive all-size path certificate and an exact two-seed criterion for
cycles from their standard spectral certificate.
-/

set_option autoImplicit false

namespace Komorebi.SingleOperatorGraph

open scoped BigOperators
open Polynomial

universe u v w

section PolynomialGeneration

variable {k : Type u} [Field k]
variable {X : Type v} [AddCommGroup X] [Module k X]

/-- Evaluate a polynomial in `T` at a vector `x`. -/
noncomputable def evalVector (T : Module.End k X) (x : X) : k[X] →ₗ[k] X :=
  (LinearMap.applyₗ x).comp (aeval T).toLinearMap

@[simp]
theorem evalVector_apply (T : Module.End k X) (x : X) (p : k[X]) :
    evalVector T x p = aeval T p x :=
  rfl

/-- The presentation map for a finite or infinite family of operator seeds. -/
noncomputable def seedPresentation {ι : Type w} (T : Module.End k X)
    (v : ι → X) : (ι →₀ k[X]) →ₗ[k] X :=
  Finsupp.lsum k fun i ↦ evalVector T (v i)

/-- All polynomial translates of a family of seeds. -/
noncomputable def orbitFamily {ι : Type w} (T : Module.End k X) (v : ι → X) :
    ι × k[X] → X :=
  fun ip ↦ aeval T ip.2 (v ip.1)

/-- A family generates under the polynomial algebra `k[T]`. -/
def FamilyGenerates {ι : Type w} (T : Module.End k X) (v : ι → X) : Prop :=
  Submodule.span k (Set.range (orbitFamily T v)) = ⊤

/-- There are at most `r` operator seeds. -/
def SeedNumberLE (T : Module.End k X) (r : ℕ) : Prop :=
  ∃ v : Fin r → X, FamilyGenerates T v

/-- Intertwining `T` with a scalar automatically intertwines every polynomial in `T`. -/
theorem eval_intertwining_of_map_T_eq_smul
    {Y : Type w} [AddCommGroup Y] [Module k Y]
    (T : Module.End k X) (q : X →ₗ[k] Y) (eigenvalue : k)
    (hT : ∀ x : X, q (T x) = eigenvalue • q x) :
    ∀ (p : k[X]) (x : X),
      q (aeval T p x) = p.eval eigenvalue • q x := by
  have hpow : ∀ (n : ℕ) (x : X),
      q ((T ^ n) x) = eigenvalue ^ n • q x := by
    intro n x
    induction n with
    | zero => simp
    | succ n ih =>
        rw [pow_succ', Module.End.mul_apply, hT, ih]
        simp [pow_succ', smul_smul]
  intro p x
  induction p using Polynomial.induction_on' with
  | add p q hp hq => simp [map_add, hp, hq, add_smul]
  | monomial n a =>
      simp [aeval_monomial, hpow, smul_smul]

/-- Polynomial functional calculus on a single eigenvector. -/
theorem aeval_apply_of_eigenvector
    (T : Module.End k X) (eigenvalue : k) (x : X)
    (hx : T x = eigenvalue • x) (p : k[X]) :
    aeval T p x = p.eval eigenvalue • x := by
  have hpow : ∀ n : ℕ, (T ^ n) x = eigenvalue ^ n • x := by
    intro n
    induction n with
    | zero => simp
    | succ n ih =>
        rw [pow_succ', Module.End.mul_apply, ih, map_smul, hx]
        simp [pow_succ', smul_smul, mul_comm]
  induction p using Polynomial.induction_on' with
  | add p q hp hq => simp [map_add, hp, hq, add_smul]
  | monomial n a => simp [aeval_monomial, hpow, smul_smul, mul_comm]

/--
A scalar quotient gives the geometric-multiplicity lower bound.  This is the
precise Nakayama-style obstruction used in the paper: after passing to a
quotient on which `T` is the scalar `λ`, every polynomial orbit of one seed
collapses to the line through that seed's image.
-/
theorem finrank_le_card_of_generates_of_scalar_factor
    {Y : Type w} [AddCommGroup Y] [Module k Y] [FiniteDimensional k Y]
    {ι : Type*} [Fintype ι]
    (T : Module.End k X) (v : ι → X) (q : X →ₗ[k] Y) (hq : Function.Surjective q)
    (eigenvalue : k)
    (hintertwine : ∀ (p : k[X]) (x : X),
      q (aeval T p x) = p.eval eigenvalue • q x)
    (hgen : FamilyGenerates T v) :
    Module.finrank k Y ≤ Fintype.card ι := by
  have hspan : Submodule.span k (Set.range fun i ↦ q (v i)) = ⊤ := by
    apply top_unique
    intro y _hy
    obtain ⟨x, rfl⟩ := hq y
    have hx : x ∈ Submodule.span k (Set.range (orbitFamily T v)) := by
      rw [hgen]
      trivial
    refine Submodule.span_induction (p := fun z _ ↦
      q z ∈ Submodule.span k (Set.range fun i ↦ q (v i))) ?_ ?_ ?_ ?_ hx
    · intro z hz
      obtain ⟨⟨i, p⟩, rfl⟩ := hz
      change q (aeval T p (v i)) ∈ _
      rw [hintertwine]
      exact Submodule.smul_mem _ _
        (Submodule.subset_span (Set.mem_range_self i))
    · simp
    · intro x y _ _ hx hy
      simpa using Submodule.add_mem _ hx hy
    · intro a x _ hx
      simpa using Submodule.smul_mem _ a hx
  exact finrank_le_of_span_eq_top (R := k) hspan

/-- The geometric-multiplicity obstruction in coordinate form. -/
theorem multiplicity_le_of_generates
    {ι : Type*} [Fintype ι]
    (T : Module.End k X) (v : ι → X) (m : ℕ)
    (q : X →ₗ[k] (Fin m → k)) (hq : Function.Surjective q) (eigenvalue : k)
    (hintertwine : ∀ (p : k[X]) (x : X),
      q (aeval T p x) = p.eval eigenvalue • q x)
    (hgen : FamilyGenerates T v) :
    m ≤ Fintype.card ι := by
  simpa [Module.finrank_pi] using
    finrank_le_card_of_generates_of_scalar_factor T v q hq eigenvalue hintertwine hgen

/-- The span of polynomial translates is invariant under the operator. -/
theorem operator_mem_span_orbit_of_mem
    {ι : Type*} (T : Module.End k X) (v : ι → X) {x : X}
    (hx : x ∈ Submodule.span k (Set.range (orbitFamily T v))) :
    T x ∈ Submodule.span k (Set.range (orbitFamily T v)) := by
  classical
  refine Submodule.span_induction (p := fun z _ ↦
    T z ∈ Submodule.span k (Set.range (orbitFamily T v))) ?_ ?_ ?_ ?_ hx
  · intro z hz
    obtain ⟨⟨i, p⟩, rfl⟩ := hz
    apply Submodule.subset_span
    refine ⟨(i, Polynomial.X * p), ?_⟩
    simp [orbitFamily, map_mul, Module.End.mul_apply]
  · simp
  · intro x y _ _ hx hy
    simpa using Submodule.add_mem _ hx hy
  · intro a x _ hx
    simpa using Submodule.smul_mem _ a hx

/--
The polynomial-orbit span is closed under every polynomial in `T`, not only
under `T` itself.  This is the key closure fact behind the comparison with the
actual image algebra `k[T]` below.
-/
theorem aeval_mem_span_orbit_of_mem
    {iota : Type*} (T : Module.End k X) (v : iota → X) (p : k[X]) {x : X}
    (hx : x ∈ Submodule.span k (Set.range (orbitFamily T v))) :
    aeval T p x ∈ Submodule.span k (Set.range (orbitFamily T v)) := by
  classical
  refine Submodule.span_induction (p := fun z _ ↦
    aeval T p z ∈ Submodule.span k (Set.range (orbitFamily T v))) ?_ ?_ ?_ ?_ hx
  · intro z hz
    obtain ⟨⟨i, q⟩, rfl⟩ := hz
    apply Submodule.subset_span
    refine ⟨(i, p * q), ?_⟩
    simp [orbitFamily, map_mul, Module.End.mul_apply]
  · simp
  · intro x y _ _ hx hy
    simpa using Submodule.add_mem _ hx hy
  · intro a x _ hx
    simpa using Submodule.smul_mem _ a hx

/-- The concrete image algebra generated by the single operator `T`. -/
def operatorAlgebra (T : Module.End k X) : Subalgebra k (Module.End k X) :=
  Algebra.adjoin k {T}

/--
The algebraic span of a seed family over the genuine image algebra `k[T]`,
after restriction of scalars to `k`, is exactly its polynomial-orbit span.
This proves the comparison rather than postulating it.
-/
theorem restrictScalars_span_operatorAlgebra_eq_span_orbit
    {iota : Type*} (T : Module.End k X) (v : iota → X) :
    (Submodule.span (operatorAlgebra T) (Set.range v)).restrictScalars k =
      Submodule.span k (Set.range (orbitFamily T v)) := by
  classical
  let P : Submodule (operatorAlgebra T) X :=
    { carrier := Submodule.span k (Set.range (orbitFamily T v))
      zero_mem' := Submodule.zero_mem _
      add_mem' := fun hx hy ↦ Submodule.add_mem _ hx hy
      smul_mem' := by
        intro a x hx
        have ha : (a : Module.End k X) ∈ Algebra.adjoin k ({T} : Set (Module.End k X)) :=
          a.property
        rw [Algebra.adjoin_singleton_eq_range_aeval] at ha
        obtain ⟨p, hp⟩ := ha
        have hpx := aeval_mem_span_orbit_of_mem T v p hx
        change (a : Module.End k X) x ∈
          Submodule.span k (Set.range (orbitFamily T v))
        rw [← hp]
        exact hpx }
  apply le_antisymm
  · change Submodule.span (operatorAlgebra T) (Set.range v) ≤ P
    apply Submodule.span_le.2
    rintro _ ⟨i, rfl⟩
    change v i ∈ Submodule.span k (Set.range (orbitFamily T v))
    apply Submodule.subset_span
    refine ⟨(i, 1), ?_⟩
    simp [orbitFamily]
  · apply Submodule.span_le.2
    rintro _ ⟨⟨i, p⟩, rfl⟩
    change aeval T p (v i) ∈
      (Submodule.span (operatorAlgebra T) (Set.range v)).restrictScalars k
    let a : operatorAlgebra T :=
      ⟨aeval T p, Polynomial.aeval_mem_adjoin_singleton k T⟩
    have hv : v i ∈ Submodule.span (operatorAlgebra T) (Set.range v) :=
      Submodule.subset_span (Set.mem_range_self i)
    have hav := Submodule.smul_mem
      (Submodule.span (operatorAlgebra T) (Set.range v)) a hv
    change a • v i ∈ Submodule.span (operatorAlgebra T) (Set.range v)
    exact hav

/--
A seed family generates by polynomial orbits iff it generates as a module over
the actual image algebra `k[T]`.
-/
theorem familyGenerates_iff_operatorAlgebra_familyGenerates
    {iota : Type*} (T : Module.End k X) (v : iota → X) :
    FamilyGenerates T v ↔
      Komorebi.SeedRankBasics.FamilyGenerates (operatorAlgebra T) X v := by
  rw [FamilyGenerates, Komorebi.SeedRankBasics.FamilyGenerates,
    Komorebi.SeedRankBasics.Generates,
    ← restrictScalars_span_operatorAlgebra_eq_span_orbit T v]
  exact Submodule.restrictScalars_eq_top_iff k (operatorAlgebra T) X

/-- The corresponding exact comparison for the natural `at most n` predicate. -/
theorem seedNumberLE_iff_operatorAlgebra_family
    (T : Module.End k X) (n : ℕ) :
    SeedNumberLE T n ↔
      ∃ v : Fin n → X,
        Komorebi.SeedRankBasics.FamilyGenerates (operatorAlgebra T) X v := by
  simp only [SeedNumberLE, familyGenerates_iff_operatorAlgebra_familyGenerates]

/--
An exact natural-valued polynomial seed number is the canonical
`seedFinrank` of the image algebra `k[T]`.  Finite generation is derived from
the upper-bound half of `hLeast`; it is not an additional assumption.
-/
theorem operatorAlgebra_seedFinrank_eq_of_seedNumber_isLeast
    (T : Module.End k X) (R : ℕ)
    (hLeast : IsLeast {r : ℕ | SeedNumberLE T r} R) :
    Komorebi.SeedRankBasics.seedFinrank (operatorAlgebra T) X = R := by
  classical
  obtain ⟨v, hvPolynomial⟩ := hLeast.1
  have hvAlgebra :=
    (familyGenerates_iff_operatorAlgebra_familyGenerates T v).mp hvPolynomial
  change Submodule.span (operatorAlgebra T) (Set.range v) = ⊤ at hvAlgebra
  have hfg : (⊤ : Submodule (operatorAlgebra T) X).FG := by
    rw [Submodule.fg_def]
    exact ⟨Set.range v, Set.finite_range v, hvAlgebra⟩
  let _ : Module.Finite (operatorAlgebra T) X := Module.finite_def.mpr hfg
  apply Nat.le_antisymm
  · change (⊤ : Submodule (operatorAlgebra T) X).spanFinrank ≤ R
    rw [← hvAlgebra]
    refine (Submodule.spanFinrank_span_le_ncard_of_finite
      (Set.finite_range v)).trans ?_
    rw [← Nat.card_coe_set_eq]
    simpa using Finite.card_range_le v
  · obtain ⟨s, hsCard, hsSpan⟩ :=
      Submodule.FG.exists_span_finset_card_eq_spanFinrank
        (R := operatorAlgebra T) (M := X) Module.Finite.fg_top
    let w : Fin s.card → X := fun i ↦ ((s.equivFin).symm i : s)
    have hrange : Set.range w = (s : Set X) := by
      ext x
      constructor
      · rintro ⟨i, rfl⟩
        exact ((s.equivFin).symm i).property
      · intro hx
        refine ⟨s.equivFin ⟨x, hx⟩, ?_⟩
        simp [w]
    have hwAlgebra :
        Komorebi.SeedRankBasics.FamilyGenerates (operatorAlgebra T) X w := by
      change Submodule.span (operatorAlgebra T) (Set.range w) = ⊤
      rw [hrange, hsSpan]
    have hwPolynomial : FamilyGenerates T w :=
      (familyGenerates_iff_operatorAlgebra_familyGenerates T w).mpr hwAlgebra
    have hmin : R ≤ s.card := hLeast.2 ⟨w, hwPolynomial⟩
    rw [Komorebi.SeedRankBasics.seedFinrank, ← hsCard]
    exact hmin

/--
Cardinal-valued form of the same bridge: the canonical seed rank of `X` as a
module over the image algebra `k[T]` is the finite cardinal `R`.
-/
theorem operatorAlgebra_seedRank_eq_of_seedNumber_isLeast
    (T : Module.End k X) (R : ℕ)
    (hLeast : IsLeast {r : ℕ | SeedNumberLE T r} R) :
    Komorebi.SeedRankBasics.seedRank (operatorAlgebra T) X = (R : Cardinal) := by
  classical
  obtain ⟨v, hvPolynomial⟩ := hLeast.1
  have hvAlgebra :=
    (familyGenerates_iff_operatorAlgebra_familyGenerates T v).mp hvPolynomial
  change Submodule.span (operatorAlgebra T) (Set.range v) = ⊤ at hvAlgebra
  have hfg : (⊤ : Submodule (operatorAlgebra T) X).FG := by
    rw [Submodule.fg_def]
    exact ⟨Set.range v, Set.finite_range v, hvAlgebra⟩
  let _ : Module.Finite (operatorAlgebra T) X := Module.finite_def.mpr hfg
  rw [Komorebi.SeedRankBasics.seedRank_eq_seedFinrank,
    operatorAlgebra_seedFinrank_eq_of_seedNumber_isLeast T R hLeast]

/-- A spanning Krylov orbit is, in particular, a one-seed polynomial presentation. -/
theorem familyGenerates_singleton_of_pow_span_eq_top
    (T : Module.End k X) (x : X)
    (hpow : Submodule.span k (Set.range fun n : ℕ ↦ (T ^ n) x) = ⊤) :
    FamilyGenerates T (fun _ : Fin 1 ↦ x) := by
  rw [FamilyGenerates]
  apply top_unique
  rw [← hpow]
  apply Submodule.span_le.2
  rintro _ ⟨n, rfl⟩
  apply Submodule.subset_span
  refine ⟨((0 : Fin 1), Polynomial.X ^ n), ?_⟩
  simp [orbitFamily]

/-- A nonzero module cannot be generated by the empty seed family. -/
theorem not_seedNumberLE_zero [Nontrivial X] (T : Module.End k X) :
    ¬ SeedNumberLE T 0 := by
  rintro ⟨v, hv⟩
  have hempty : Set.range (orbitFamily T v) = ∅ := by
    ext x
    simp
  rw [FamilyGenerates, hempty, Submodule.span_empty] at hv
  exact bot_ne_top hv

/-- On a nonzero module, a cyclic vector makes one the exact seed number. -/
theorem seedNumber_one_isLeast_of_cyclic [Nontrivial X]
    (T : Module.End k X) (hcyclic : SeedNumberLE T 1) :
    IsLeast {r : ℕ | SeedNumberLE T r} 1 := by
  constructor
  · exact hcyclic
  · intro r hr
    have hr0 : r ≠ 0 := by
      intro h
      subst r
      exact not_seedNumberLE_zero T hr
    omega

/-- The zero module has exact operator seed number zero, matching the paper's convention. -/
theorem seedNumber_zero_isLeast_of_subsingleton [Subsingleton X]
    (T : Module.End k X) :
    IsLeast {r : ℕ | SeedNumberLE T r} 0 := by
  constructor
  · refine ⟨Fin.elim0, ?_⟩
    rw [FamilyGenerates]
    subsingleton
  · intro r _hr
    exact Nat.zero_le r

end PolynomialGeneration

section PrimaryDecomposition

variable {k : Type u} [Field k]
variable {X : Type v} [AddCommGroup X] [Module k X]
variable {Λ : Type w} [Fintype Λ]

/--
The `a`th padded sum of the `a`th cyclic block generator in every primary
packet.  Blocks with index at most `a` contribute zero.
-/
noncomputable def paddedBlockSum (R : ℕ) (multiplicity : Λ → ℕ)
    (blockGenerator : ∀ eigen : Λ, Fin (multiplicity eigen) → X)
    (a : Fin R) : X :=
  ∑ eigen : Λ,
    if h : a.val < multiplicity eigen then
      blockGenerator eigen ⟨a.val, h⟩
    else 0

/--
The upper half of the Jordan argument.  If all cyclic block generators
generate, and polynomial primary projectors recover every block generator
from the corresponding padded sum, then `R` padded sums generate.
-/
theorem paddedBlockSums_generate
    (T : Module.End k X) (R : ℕ) (multiplicity : Λ → ℕ)
    (blockGenerator : ∀ eigen : Λ, Fin (multiplicity eigen) → X)
    (hbound : ∀ eigen, multiplicity eigen ≤ R)
    (hblocks : FamilyGenerates T
      (fun z : Σ eigen : Λ, Fin (multiplicity eigen) =>
        blockGenerator z.1 z.2))
    (hextract : ∀ (eigen : Λ) (j : Fin (multiplicity eigen)),
      ∃ p : k[X],
        aeval T p
          (paddedBlockSum R multiplicity blockGenerator
            ⟨j.val, lt_of_lt_of_le j.isLt (hbound eigen)⟩) =
          blockGenerator eigen j) :
    FamilyGenerates T (paddedBlockSum R multiplicity blockGenerator) := by
  classical
  rw [FamilyGenerates]
  apply top_unique
  intro x _hx
  have hx : x ∈ Submodule.span k
      (Set.range (orbitFamily T
        (fun z : Σ eigen : Λ, Fin (multiplicity eigen) =>
          blockGenerator z.1 z.2))) := by
    rw [hblocks]
    trivial
  refine Submodule.span_induction (p := fun z _ ↦
    z ∈ Submodule.span k
      (Set.range (orbitFamily T
        (paddedBlockSum R multiplicity blockGenerator)))) ?_ ?_ ?_ ?_ hx
  · intro z hz
    obtain ⟨⟨⟨eigen, j⟩, q⟩, rfl⟩ := hz
    obtain ⟨p, hp⟩ := hextract eigen j
    let a : Fin R := ⟨j.val, lt_of_lt_of_le j.isLt (hbound eigen)⟩
    have horbit :
        aeval T (q * p)
            (paddedBlockSum R multiplicity blockGenerator a) ∈
          Set.range (orbitFamily T
            (paddedBlockSum R multiplicity blockGenerator)) := by
      exact ⟨(a, q * p), rfl⟩
    apply Submodule.subset_span at horbit
    rw [orbitFamily]
    change aeval T q (blockGenerator eigen j) ∈ _
    rw [← hp, ← Module.End.mul_apply, ← map_mul]
    exact horbit
  · exact Submodule.zero_mem _
  · intro x y _ _ hx hy
    exact Submodule.add_mem _ hx hy
  · intro c x _ hx
    exact Submodule.smul_mem _ c hx

/--
Exact single-operator seed number from explicit primary/Jordan data.

`q eigen` is the semisimple top
`X_eigen / (T-eigenvalue)X_eigen`; its dimension is the number of Jordan
blocks.  `hextract` is supplied by the Chinese-remainder primary projectors.
Thus these hypotheses are precisely the two classical decomposition facts
used in the paper, while both generator inequalities are proved here.
-/
theorem singleOperator_seedNumber_isLeast_of_primary_decomposition
    (T : Module.End k X) (R : ℕ)
    (multiplicity : Λ → ℕ) (eigenvalue : Λ → k)
    (blockGenerator : ∀ eigen : Λ, Fin (multiplicity eigen) → X)
    (hbound : ∀ eigen, multiplicity eigen ≤ R)
    (maxEigen : Λ) (hmax : multiplicity maxEigen = R)
    (hblocks : FamilyGenerates T
      (fun z : Σ eigen : Λ, Fin (multiplicity eigen) =>
        blockGenerator z.1 z.2))
    (hextract : ∀ (eigen : Λ) (j : Fin (multiplicity eigen)),
      ∃ p : k[X],
        aeval T p
          (paddedBlockSum R multiplicity blockGenerator
            ⟨j.val, lt_of_lt_of_le j.isLt (hbound eigen)⟩) =
          blockGenerator eigen j)
    (q : ∀ eigen : Λ, X →ₗ[k] (Fin (multiplicity eigen) → k))
    (hq : ∀ eigen, Function.Surjective (q eigen))
    (hqT : ∀ (eigen : Λ) (p : k[X]) (x : X),
      q eigen (aeval T p x) = p.eval (eigenvalue eigen) • q eigen x) :
    IsLeast {r : ℕ | SeedNumberLE T r} R := by
  constructor
  · exact ⟨paddedBlockSum R multiplicity blockGenerator,
      paddedBlockSums_generate T R multiplicity blockGenerator hbound hblocks hextract⟩
  · intro r hr
    obtain ⟨v, hv⟩ := hr
    have hle := multiplicity_le_of_generates T v (multiplicity maxEigen)
      (q maxEigen) (hq maxEigen) (eigenvalue maxEigen) (hqT maxEigen) hv
    simpa [hmax] using hle

/--
Literal canonical-invariant form of the primary-decomposition theorem.  The
two equalities transfer the proved natural minimum to Mathlib's
`spanFinrank`/`spanRank` definitions for the genuine image algebra `k[T]`.
-/
theorem singleOperator_operatorAlgebra_seedRanks_eq_of_primary_decomposition
    (T : Module.End k X) (R : ℕ)
    (multiplicity : Λ → ℕ) (eigenvalue : Λ → k)
    (blockGenerator : ∀ eigen : Λ, Fin (multiplicity eigen) → X)
    (hbound : ∀ eigen, multiplicity eigen ≤ R)
    (maxEigen : Λ) (hmax : multiplicity maxEigen = R)
    (hblocks : FamilyGenerates T
      (fun z : Σ eigen : Λ, Fin (multiplicity eigen) ↦
        blockGenerator z.1 z.2))
    (hextract : ∀ (eigen : Λ) (j : Fin (multiplicity eigen)),
      ∃ p : k[X],
        aeval T p
          (paddedBlockSum R multiplicity blockGenerator
            ⟨j.val, lt_of_lt_of_le j.isLt (hbound eigen)⟩) =
          blockGenerator eigen j)
    (q : ∀ eigen : Λ, X →ₗ[k] (Fin (multiplicity eigen) → k))
    (hq : ∀ eigen, Function.Surjective (q eigen))
    (hqT : ∀ (eigen : Λ) (p : k[X]) (x : X),
      q eigen (aeval T p x) = p.eval (eigenvalue eigen) • q eigen x) :
    Komorebi.SeedRankBasics.seedFinrank (operatorAlgebra T) X = R ∧
      Komorebi.SeedRankBasics.seedRank (operatorAlgebra T) X = (R : Cardinal) := by
  let hLeast := singleOperator_seedNumber_isLeast_of_primary_decomposition
    T R multiplicity eigenvalue blockGenerator hbound maxEigen hmax hblocks
      hextract q hq hqT
  exact ⟨operatorAlgebra_seedFinrank_eq_of_seedNumber_isLeast T R hLeast,
    operatorAlgebra_seedRank_eq_of_seedNumber_isLeast T R hLeast⟩

/-- One operator is cyclic when one polynomial seed suffices. -/
def HasCyclicVector (T : Module.End k X) : Prop :=
  SeedNumberLE T 1

/-- Every represented eigenspace has dimension one. -/
def AllGeometricMultiplicitiesOne (geometricMultiplicity : Λ → ℕ) : Prop :=
  ∀ eigen, geometricMultiplicity eigen = 1

/-- The represented Jordan form has exactly one block for every eigenvalue. -/
def OneJordanBlockPerEigenvalue (blockMultiplicity : Λ → ℕ) : Prop :=
  ∀ eigen, blockMultiplicity eigen = 1

/-- A positive exact seed number is one exactly when the operator is cyclic. -/
theorem hasCyclicVector_iff_seedNumber_eq_one
    (T : Module.End k X) (R : ℕ) (hR : 0 < R)
    (hLeast : IsLeast {r : ℕ | SeedNumberLE T r} R) :
    HasCyclicVector T ↔ R = 1 := by
  constructor
  · intro hcyc
    exact Nat.eq_one_of_dvd_one (Nat.dvd_one.mpr (Nat.le_antisymm (hLeast.2 hcyc) hR))
  · rintro rfl
    exact hLeast.1

omit [Fintype Λ] in
/--
The exact cyclic/nonderogatory criterion in block language.  Positivity says
that every listed eigenvalue actually occurs; `hmax` says one of them realizes
the maximum geometric multiplicity.
-/
theorem hasCyclicVector_iff_one_block_per_eigenvalue
    (T : Module.End k X) (R : ℕ) (multiplicity : Λ → ℕ)
    (hpositive : ∀ eigen, 0 < multiplicity eigen)
    (hbound : ∀ eigen, multiplicity eigen ≤ R)
    (maxEigen : Λ) (hmax : multiplicity maxEigen = R)
    (hLeast : IsLeast {r : ℕ | SeedNumberLE T r} R) :
    HasCyclicVector T ↔ ∀ eigen, multiplicity eigen = 1 := by
  have hR : 0 < R := by simpa [← hmax] using hpositive maxEigen
  rw [hasCyclicVector_iff_seedNumber_eq_one T R hR hLeast]
  constructor
  · intro hOne eigen
    apply Nat.le_antisymm
    · simpa [hOne] using hbound eigen
    · exact hpositive eigen
  · intro hall
    exact hmax.symm.trans (hall maxEigen)

omit [Fintype Λ] in
/--
Four-way cyclic-matrix criterion once the standard canonical-form polynomial
bridge is supplied.  The bridge is exactly the classical statement that the
minimal and characteristic polynomials agree iff there is one Jordan block
for each eigenvalue.
-/
theorem cyclic_matrix_criterion_of_primary_decomposition
    [FiniteDimensional k X]
    (T : Module.End k X) (R : ℕ) (multiplicity : Λ → ℕ)
    (hpositive : ∀ eigen, 0 < multiplicity eigen)
    (hbound : ∀ eigen, multiplicity eigen ≤ R)
    (maxEigen : Λ) (hmax : multiplicity maxEigen = R)
    (hLeast : IsLeast {r : ℕ | SeedNumberLE T r} R)
    (hpoly : minpoly k T = T.charpoly ↔
      ∀ eigen, multiplicity eigen = 1) :
    HasCyclicVector T ↔
      (∀ eigen, multiplicity eigen = 1) ∧ minpoly k T = T.charpoly := by
  rw [hasCyclicVector_iff_one_block_per_eigenvalue
    T R multiplicity hpositive hbound maxEigen hmax hLeast]
  constructor
  · intro h
    exact ⟨h, hpoly.mpr h⟩
  · exact fun h ↦ h.1

omit [Fintype Λ] in
/--
The cyclic-matrix criterion as a literal four-condition equivalence chain:
cyclic vector, geometric multiplicity one, one Jordan block per eigenvalue,
and equality of minimal and characteristic polynomials.  The middle bridge
records the canonical-form fact that geometric multiplicity counts Jordan
blocks; the final bridge is the remaining minpoly/charpoly classification
fact.
-/
theorem cyclic_matrix_four_way_iff_of_primary_decomposition
    [FiniteDimensional k X]
    (T : Module.End k X) (R : ℕ)
    (geometricMultiplicity blockMultiplicity : Λ → ℕ)
    (hpositive : ∀ eigen, 0 < geometricMultiplicity eigen)
    (hbound : ∀ eigen, geometricMultiplicity eigen ≤ R)
    (maxEigen : Λ) (hmax : geometricMultiplicity maxEigen = R)
    (hLeast : IsLeast {r : ℕ | SeedNumberLE T r} R)
    (hgeometric_eq_blocks : ∀ eigen,
      geometricMultiplicity eigen = blockMultiplicity eigen)
    (hpoly : minpoly k T = T.charpoly ↔
      OneJordanBlockPerEigenvalue blockMultiplicity) :
    (HasCyclicVector T ↔
        AllGeometricMultiplicitiesOne geometricMultiplicity) ∧
      (AllGeometricMultiplicitiesOne geometricMultiplicity ↔
        OneJordanBlockPerEigenvalue blockMultiplicity) ∧
      (OneJordanBlockPerEigenvalue blockMultiplicity ↔
        minpoly k T = T.charpoly) := by
  have hcyclic : HasCyclicVector T ↔
      AllGeometricMultiplicitiesOne geometricMultiplicity := by
    exact hasCyclicVector_iff_one_block_per_eigenvalue
      T R geometricMultiplicity hpositive hbound maxEigen hmax hLeast
  have hmiddle : AllGeometricMultiplicitiesOne geometricMultiplicity ↔
      OneJordanBlockPerEigenvalue blockMultiplicity := by
    constructor
    · intro h eigen
      rw [← hgeometric_eq_blocks eigen]
      exact h eigen
    · intro h eigen
      rw [hgeometric_eq_blocks eigen]
      exact h eigen
  exact ⟨hcyclic, hmiddle, hpoly.symm⟩

end PrimaryDecomposition

section Diagonalizable

variable {k : Type u} [Field k]
variable {X : Type v} [AddCommGroup X] [Module k X]
variable {Λ : Type w} [Fintype Λ]

/-- Every basis is an operator-generating family, using constant polynomials. -/
theorem basis_generates_under_operator
    {I : Type*} [Fintype I] (T : Module.End k X) (b : Module.Basis I k X) :
    FamilyGenerates T b := by
  rw [FamilyGenerates]
  apply top_unique
  rw [← b.span_eq]
  apply Submodule.span_mono
  rintro _ ⟨i, rfl⟩
  refine ⟨(i, 1), ?_⟩
  simp [orbitFamily]

/-- Coordinates in one eigenspace packet of a basis indexed by eigenvalue and multiplicity. -/
noncomputable def basisPacketCoordinate
    (multiplicity : Λ → ℕ)
    (b : Module.Basis (Σ eigen : Λ, Fin (multiplicity eigen)) k X)
    (eigen : Λ) : X →ₗ[k] (Fin (multiplicity eigen) → k) :=
  LinearMap.pi fun j ↦
    (Finsupp.lapply (R := k) (M := k)
      (⟨eigen, j⟩ : Σ eigen : Λ, Fin (multiplicity eigen))).comp
      b.repr.toLinearMap

omit [Fintype Λ] in
@[simp]
theorem basisPacketCoordinate_apply
    (multiplicity : Λ → ℕ)
    (b : Module.Basis (Σ eigen : Λ, Fin (multiplicity eigen)) k X)
    (eigen : Λ) (x : X) (j : Fin (multiplicity eigen)) :
    basisPacketCoordinate multiplicity b eigen x j =
      b.repr x ⟨eigen, j⟩ :=
  rfl

omit [Fintype Λ] in
/-- Every basis packet-coordinate map is onto. -/
theorem basisPacketCoordinate_surjective
    (multiplicity : Λ → ℕ)
    (b : Module.Basis (Σ eigen : Λ, Fin (multiplicity eigen)) k X)
    (eigen : Λ) :
    Function.Surjective (basisPacketCoordinate multiplicity b eigen) := by
  classical
  intro y
  let x : X := ∑ j : Fin (multiplicity eigen), y j • b ⟨eigen, j⟩
  refine ⟨x, ?_⟩
  funext j
  simp [basisPacketCoordinate, x, Finsupp.single_apply]

omit [Fintype Λ] in
/-- Packet coordinates intertwine a diagonal operator with its eigenvalue. -/
theorem basisPacketCoordinate_map_T
    (T : Module.End k X) (multiplicity : Λ → ℕ) (eigenvalue : Λ → k)
    (b : Module.Basis (Σ eigen : Λ, Fin (multiplicity eigen)) k X)
    (hEigen : ∀ z : Σ eigen : Λ, Fin (multiplicity eigen),
      T (b z) = eigenvalue z.1 • b z)
    (eigen : Λ) (x : X) :
    basisPacketCoordinate multiplicity b eigen (T x) =
      eigenvalue eigen • basisPacketCoordinate multiplicity b eigen x := by
  classical
  have hmap :
      (basisPacketCoordinate multiplicity b eigen).comp T =
        eigenvalue eigen • basisPacketCoordinate multiplicity b eigen := by
    apply b.ext
    intro z
    rcases z with ⟨other, j⟩
    by_cases h : other = eigen
    · subst other
      simp [basisPacketCoordinate, hEigen]
    · ext a
      simp [basisPacketCoordinate, hEigen, h]
  exact LinearMap.congr_fun hmap x

/--
For a diagonalizable operator, the seed number is the maximum eigenspace
multiplicity.  The input `hproject` is an explicit Lagrange spectral-projector
certificate; distinct eigenvalues supply it in the usual diagonalization
theorem.
-/
theorem diagonalizable_seedNumber_isLeast
    (T : Module.End k X) (R : ℕ)
    (multiplicity : Λ → ℕ) (eigenvalue : Λ → k)
    (b : Module.Basis (Σ eigen : Λ, Fin (multiplicity eigen)) k X)
    (hEigen : ∀ z : Σ eigen : Λ, Fin (multiplicity eigen),
      T (b z) = eigenvalue z.1 • b z)
    (hbound : ∀ eigen, multiplicity eigen ≤ R)
    (maxEigen : Λ) (hmax : multiplicity maxEigen = R)
    (projectorPolynomial : Λ → k[X])
    (hproject : ∀ (eigen : Λ) (j : Fin (multiplicity eigen)),
      aeval T (projectorPolynomial eigen)
        (paddedBlockSum R multiplicity (fun e j ↦ b ⟨e, j⟩)
          ⟨j.val, lt_of_lt_of_le j.isLt (hbound eigen)⟩) =
        b ⟨eigen, j⟩) :
    IsLeast {r : ℕ | SeedNumberLE T r} R := by
  let q : ∀ eigen : Λ, X →ₗ[k] (Fin (multiplicity eigen) → k) :=
    fun eigen ↦ basisPacketCoordinate multiplicity b eigen
  refine singleOperator_seedNumber_isLeast_of_primary_decomposition
    T R multiplicity eigenvalue (fun eigen j ↦ b ⟨eigen, j⟩)
    hbound maxEigen hmax ?_ ?_ q ?_ ?_
  · exact basis_generates_under_operator T b
  · intro eigen j
    exact ⟨projectorPolynomial eigen, hproject eigen j⟩
  · intro eigen
    exact basisPacketCoordinate_surjective multiplicity b eigen
  · intro eigen
    exact eval_intertwining_of_map_T_eq_smul T (q eigen) (eigenvalue eigen)
      (basisPacketCoordinate_map_T T multiplicity eigenvalue b hEigen eigen)

/--
The projector certificate in `diagonalizable_seedNumber_isLeast` is automatic
when the listed eigenvalues are distinct: Lagrange interpolation constructs
the spectral projectors.
-/
theorem diagonalizable_seedNumber_isLeast_of_distinct_eigenvalues
    (T : Module.End k X) (R : ℕ)
    (multiplicity : Λ → ℕ) (eigenvalue : Λ → k)
    (b : Module.Basis (Σ eigen : Λ, Fin (multiplicity eigen)) k X)
    (hEigen : ∀ z : Σ eigen : Λ, Fin (multiplicity eigen),
      T (b z) = eigenvalue z.1 • b z)
    (heigenvalue : Function.Injective eigenvalue)
    (hbound : ∀ eigen, multiplicity eigen ≤ R)
    (maxEigen : Λ) (hmax : multiplicity maxEigen = R) :
    IsLeast {r : ℕ | SeedNumberLE T r} R := by
  classical
  let projectorPolynomial : Λ → k[X] := fun eigen ↦
    Lagrange.interpolate Finset.univ eigenvalue
      (fun other ↦ if other = eigen then 1 else 0)
  have hprojector (eigen other : Λ) :
      (projectorPolynomial eigen).eval (eigenvalue other) =
        if other = eigen then 1 else 0 := by
    dsimp [projectorPolynomial]
    exact Lagrange.eval_interpolate_at_node
      (fun other ↦ if other = eigen then 1 else 0)
      heigenvalue.injOn (Finset.mem_univ other)
  apply diagonalizable_seedNumber_isLeast T R multiplicity eigenvalue b hEigen
    hbound maxEigen hmax projectorPolynomial
  intro eigen j
  rw [paddedBlockSum, map_sum]
  rw [Finset.sum_eq_single eigen]
  · simp only [j.isLt, dite_true]
    rw [aeval_apply_of_eigenvector T (eigenvalue eigen) (b ⟨eigen, j⟩)
      (hEigen ⟨eigen, j⟩) (projectorPolynomial eigen)]
    rw [hprojector]
    simp
  · intro other _hmem hne
    by_cases hj : j.val < multiplicity other
    · simp only [hj, dite_true]
      rw [aeval_apply_of_eigenvector T (eigenvalue other)
        (b ⟨other, ⟨j.val, hj⟩⟩) (hEigen ⟨other, ⟨j.val, hj⟩⟩)
        (projectorPolynomial eigen)]
      rw [hprojector]
      simp [hne]
    · simp [hj]
  · simp

/-- A symmetric/diagonalizable graph operator inherits the same maximum-eigenspace formula. -/
theorem graph_seedNumber_eq_max_eigenspace_multiplicity
    (adjacency : Module.End k X) (R : ℕ)
    (multiplicity : Λ → ℕ) (eigenvalue : Λ → k)
    (eigenbasis : Module.Basis (Σ eigen : Λ, Fin (multiplicity eigen)) k X)
    (hEigen : ∀ z : Σ eigen : Λ, Fin (multiplicity eigen),
      adjacency (eigenbasis z) = eigenvalue z.1 • eigenbasis z)
    (hbound : ∀ eigen, multiplicity eigen ≤ R)
    (maxEigen : Λ) (hmax : multiplicity maxEigen = R)
    (projectorPolynomial : Λ → k[X])
    (hproject : ∀ (eigen : Λ) (j : Fin (multiplicity eigen)),
      aeval adjacency (projectorPolynomial eigen)
        (paddedBlockSum R multiplicity (fun e j ↦ eigenbasis ⟨e, j⟩)
          ⟨j.val, lt_of_lt_of_le j.isLt (hbound eigen)⟩) =
        eigenbasis ⟨eigen, j⟩) :
    IsLeast {r : ℕ | SeedNumberLE adjacency r} R :=
  diagonalizable_seedNumber_isLeast adjacency R multiplicity eigenvalue eigenbasis
    hEigen hbound maxEigen hmax projectorPolynomial hproject

/--
Graph seed rank equals maximum eigenspace multiplicity from a diagonalization
with distinct eigenvalue labels; spectral projectors are constructed internally.
-/
theorem graph_seedNumber_eq_max_eigenspace_multiplicity_of_distinct
    (adjacency : Module.End k X) (R : ℕ)
    (multiplicity : Λ → ℕ) (eigenvalue : Λ → k)
    (eigenbasis : Module.Basis (Σ eigen : Λ, Fin (multiplicity eigen)) k X)
    (hEigen : ∀ z : Σ eigen : Λ, Fin (multiplicity eigen),
      adjacency (eigenbasis z) = eigenvalue z.1 • eigenbasis z)
    (heigenvalue : Function.Injective eigenvalue)
    (hbound : ∀ eigen, multiplicity eigen ≤ R)
    (maxEigen : Λ) (hmax : multiplicity maxEigen = R) :
    IsLeast {r : ℕ | SeedNumberLE adjacency r} R :=
  diagonalizable_seedNumber_isLeast_of_distinct_eigenvalues adjacency R
    multiplicity eigenvalue eigenbasis hEigen heigenvalue hbound maxEigen hmax

end Diagonalizable

section PathGraph

variable {k : Type u} [Field k]

/-- The all-size endpoint Krylov certificate is an exact one-seed result for paths. -/
theorem path_endpoint_seedNumber_isLeast_one (n : ℕ) :
    IsLeast {r : ℕ |
      SeedNumberLE (Komorebi.PathGraphKrylov.pathStep k n) r} 1 := by
  have hpow := Komorebi.PathGraphKrylov.endpoint_isCyclic (R := k) n
  rw [Komorebi.PathGraphKrylov.IsCyclic] at hpow
  have hcyclic :
      SeedNumberLE (Komorebi.PathGraphKrylov.pathStep k n) 1 := by
    refine ⟨fun _ : Fin 1 ↦ Komorebi.PathGraphKrylov.endpoint k n, ?_⟩
    exact familyGenerates_singleton_of_pow_span_eq_top
      (Komorebi.PathGraphKrylov.pathStep k n)
      (Komorebi.PathGraphKrylov.endpoint k n) hpow
  exact seedNumber_one_isLeast_of_cyclic
    (Komorebi.PathGraphKrylov.pathStep k n) hcyclic

end PathGraph

section CycleGraph

variable {k : Type u} [Field k]

/-- The adjacency operator of the simple cycle on `n + 3` vertices. -/
def cycleAdjacency (n : ℕ) : Module.End k (Fin (n + 3) → k) :=
  LinearMap.pi fun i : Fin (n + 3) ↦
    (LinearMap.proj ((finRotate (n + 3)).symm i) :
      (Fin (n + 3) → k) →ₗ[k] k) +
    (LinearMap.proj (finRotate (n + 3) i) :
      (Fin (n + 3) → k) →ₗ[k] k)

@[simp]
theorem cycleAdjacency_apply (n : ℕ) (x : Fin (n + 3) → k)
    (i : Fin (n + 3)) :
    cycleAdjacency n x i =
      x ((finRotate (n + 3)).symm i) + x (finRotate (n + 3) i) := by
  simp [cycleAdjacency]

/-- Adjacency sends a vertex delta to the sum of its two neighboring deltas. -/
theorem cycleAdjacency_basisFun (n : ℕ) (j : Fin (n + 3)) :
    cycleAdjacency (k := k) n (Pi.basisFun k (Fin (n + 3)) j) =
      Pi.basisFun k (Fin (n + 3)) (finRotate (n + 3) j) +
        Pi.basisFun k (Fin (n + 3)) ((finRotate (n + 3)).symm j) := by
  ext i
  simp [cycleAdjacency, Pi.basisFun_apply, Pi.single_apply,
    eq_sub_iff_add_eq, eq_comm, add_comm]

/-- Two adjacent vertex deltas, used as the canonical two seeds of a cycle. -/
noncomputable def cycleSeeds (n : ℕ) : Fin 2 → (Fin (n + 3) → k) :=
  fun a ↦ Pi.basisFun k (Fin (n + 3)) ⟨a.val, by omega⟩

/-- Two adjacent vertices generate every finite simple cycle adjacency module. -/
theorem cycleSeeds_generate (n : ℕ) :
    FamilyGenerates (cycleAdjacency (k := k) n) (cycleSeeds (k := k) n) := by
  classical
  let S : Submodule k (Fin (n + 3) → k) :=
    Submodule.span k (Set.range
      (orbitFamily (cycleAdjacency (k := k) n) (cycleSeeds (k := k) n)))
  have hzero : Pi.basisFun k (Fin (n + 3)) (0 : Fin (n + 3)) ∈ S := by
    apply Submodule.subset_span
    refine ⟨((0 : Fin 2), 1), ?_⟩
    simp [orbitFamily, cycleSeeds]
  have hone : Pi.basisFun k (Fin (n + 3)) (1 : Fin (n + 3)) ∈ S := by
    apply Submodule.subset_span
    refine ⟨((1 : Fin 2), 1), ?_⟩
    simp [orbitFamily, cycleSeeds]
  have hvertex : ∀ m : ℕ, ∀ hm : m < n + 3,
      Pi.basisFun k (Fin (n + 3)) ⟨m, hm⟩ ∈ S := by
    intro m
    induction m using Nat.twoStepInduction with
    | zero =>
        intro hm
        simpa using hzero
    | one =>
        intro hm
        simpa using hone
    | more m hm0 hm1 =>
        intro hm2
        have hm0' : m < n + 3 := by omega
        have hm1' : m + 1 < n + 3 := by omega
        let j0 : Fin (n + 3) := ⟨m, hm0'⟩
        let j1 : Fin (n + 3) := ⟨m + 1, hm1'⟩
        let j2 : Fin (n + 3) := ⟨m + 2, hm2⟩
        have hj0 : Pi.basisFun k (Fin (n + 3)) j0 ∈ S := hm0 hm0'
        have hj1 : Pi.basisFun k (Fin (n + 3)) j1 ∈ S := hm1 hm1'
        have hstep : cycleAdjacency (k := k) n
            (Pi.basisFun k (Fin (n + 3)) j1) ∈ S :=
          operator_mem_span_orbit_of_mem
            (cycleAdjacency (k := k) n) (cycleSeeds (k := k) n) hj1
        have hnext : finRotate (n + 3) j1 = j2 := by
          simpa [j1, j2] using
            (finRotate_of_lt (n := n + 2) (k := m + 1) (by omega))
        have hprev : (finRotate (n + 3)).symm j1 = j0 := by
          apply Fin.ext
          rw [coe_finRotate_symm_of_ne_zero]
          · simp [j0, j1]
          · exact Fin.ne_of_val_ne (by simp [j1])
        rw [cycleAdjacency_basisFun, hnext, hprev] at hstep
        have hsub := Submodule.sub_mem S hstep hj0
        simpa [j0, j2] using hsub
  rw [FamilyGenerates]
  change S = ⊤
  apply top_unique
  rw [← (Pi.basisFun k (Fin (n + 3))).span_eq]
  apply Submodule.span_le.2
  rintro _ ⟨j, rfl⟩
  exact hvertex j.val j.isLt

/-- The Fourier row with ratio `z` on a cycle. -/
def cycleFourierRow (n : ℕ) (z : k) : (Fin (n + 3) → k) →ₗ[k] k where
  toFun x := ∑ i : Fin (n + 3), z ^ i.val * x i
  map_add' x y := by
    simp only [Pi.add_apply, mul_add, Finset.sum_add_distrib]
  map_smul' a x := by
    simp only [Pi.smul_apply, smul_eq_mul]
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro i hi
    simp only [RingHom.id_apply]
    ring

@[simp]
theorem cycleFourierRow_basisFun (n : ℕ) (z : k) (j : Fin (n + 3)) :
    cycleFourierRow n z (Pi.basisFun k (Fin (n + 3)) j) = z ^ j.val := by
  classical
  simp [cycleFourierRow, Pi.basisFun_apply, Pi.single_apply]

/-- The two conjugate Fourier rows associated with `z` and `z⁻¹`. -/
def cycleFourierFactor (n : ℕ) (z : k) :
    (Fin (n + 3) → k) →ₗ[k] (Fin 2 → k) :=
  LinearMap.pi fun a ↦ if a = 0 then cycleFourierRow n z else cycleFourierRow n z⁻¹

@[simp]
theorem cycleFourierFactor_zero (n : ℕ) (z : k) (x : Fin (n + 3) → k) :
    cycleFourierFactor n z x 0 = cycleFourierRow n z x := by
  simp [cycleFourierFactor]

@[simp]
theorem cycleFourierFactor_one (n : ℕ) (z : k) (x : Fin (n + 3) → k) :
    cycleFourierFactor n z x 1 = cycleFourierRow n z⁻¹ x := by
  simp [cycleFourierFactor]

/-- Distinct Fourier characters give an onto two-dimensional scalar factor. -/
theorem cycleFourierFactor_surjective (n : ℕ) (z : k) (hz : z ≠ z⁻¹) :
    Function.Surjective (cycleFourierFactor n z) := by
  classical
  intro y
  let d : k := z - z⁻¹
  have hd : d ≠ 0 := sub_ne_zero.mpr hz
  let bcoef : k := (y 0 - y 1) / d
  let acoef : k := y 0 - z * bcoef
  let x : Fin (n + 3) → k :=
    acoef • Pi.basisFun k (Fin (n + 3)) (0 : Fin (n + 3)) +
      bcoef • Pi.basisFun k (Fin (n + 3)) (1 : Fin (n + 3))
  refine ⟨x, ?_⟩
  funext i
  fin_cases i
  · change cycleFourierFactor n z x 0 = y 0
    rw [cycleFourierFactor_zero]
    simp only [x, map_add, map_smul, cycleFourierRow_basisFun]
    simp [acoef, bcoef]
    ring
  · change cycleFourierFactor n z x 1 = y 1
    rw [cycleFourierFactor_one]
    simp only [x, map_add, map_smul, cycleFourierRow_basisFun]
    simp [Nat.mod_eq_of_lt (by omega : 1 < n + 3)]
    dsimp [acoef, bcoef]
    field_simp [d, hd]
    ring

/-- The elementary root-of-unity recurrence behind the cycle Fourier eigenvectors. -/
theorem cycle_root_neighbor_identity (n : ℕ) (z : k)
    (hroot : z ^ (n + 3) = 1) (j : Fin (n + 3)) :
    z ^ (finRotate (n + 3) j).val +
        z ^ ((finRotate (n + 3)).symm j).val =
      (z + z⁻¹) * z ^ j.val := by
  have hz0 : z ≠ 0 := by
    intro hz
    subst z
    norm_num at hroot
  have hpred : z ^ (n + 2) = z⁻¹ := by
    apply (mul_right_cancel₀ hz0)
    have hpow := pow_sub_one_mul (n := n + 3) (by omega) z
    simp only [show n + 3 - 1 = n + 2 by omega] at hpow
    rw [hpow, hroot]
    simp [hz0]
  have hpred2 : z ^ (n + 1) = (z⁻¹) ^ 2 := by
    apply (mul_right_cancel₀ hz0)
    rw [← pow_succ, hpred]
    field_simp [hz0]
  by_cases hlast : j = Fin.last (n + 2)
  · subst j
    have hprev : ((finRotate (n + 3)).symm (Fin.last (n + 2))).val = n + 1 := by
      rw [coe_finRotate_symm_of_ne_zero]
      · simp
      · exact Fin.ne_of_val_ne (by simp)
    rw [finRotate_last, hprev]
    simp [hpred, hpred2]
    field_simp [hz0]
  · by_cases hzero : j = 0
    · subst j
      have hprev : (finRotate (n + 3)).symm (0 : Fin (n + 3)) =
          Fin.last (n + 2) := by
        apply (finRotate (n + 3)).injective
        simp
      rw [finRotate_apply_zero, hprev]
      simp [hpred, Nat.mod_eq_of_lt (by omega : 1 < n + 3)]
    · have hnext := coe_finRotate_of_ne_last hlast
      have hprev := coe_finRotate_symm_of_ne_zero hzero
      rw [hnext, hprev]
      have hjpos : 0 < j.val := by
        apply Nat.pos_of_ne_zero
        intro hj
        apply hzero
        exact Fin.ext hj
      have hj : j.val = (j.val - 1) + 1 := by omega
      have hj2 : j.val + 1 = (j.val - 1) + 2 := by omega
      have hp1 : z ^ (j.val + 1) = z ^ (j.val - 1) * z ^ 2 := by
        rw [hj2, pow_add]
      have hp0 : z ^ j.val = z ^ (j.val - 1) * z := by
        exact (congrArg (fun t : ℕ ↦ z ^ t) hj).trans (pow_succ z (j.val - 1))
      rw [hp1, hp0]
      field_simp [hz0]

/-- A root-of-unity Fourier row is a left eigenvector of cycle adjacency. -/
theorem cycleFourierRow_map_adjacency (n : ℕ) (z : k)
    (hroot : z ^ (n + 3) = 1) (x : Fin (n + 3) → k) :
    cycleFourierRow n z (cycleAdjacency n x) =
      (z + z⁻¹) * cycleFourierRow n z x := by
  have hmaps :
      (cycleFourierRow n z).comp (cycleAdjacency n) =
        (z + z⁻¹) • cycleFourierRow n z := by
    apply (Pi.basisFun k (Fin (n + 3))).ext
    intro j
    change cycleFourierRow n z
      (cycleAdjacency n (Pi.basisFun k (Fin (n + 3)) j)) =
        (z + z⁻¹) * cycleFourierRow n z (Pi.basisFun k (Fin (n + 3)) j)
    rw [cycleAdjacency_basisFun]
    simp only [map_add, cycleFourierRow_basisFun]
    exact cycle_root_neighbor_identity n z hroot j
  exact LinearMap.congr_fun hmaps x

/-- The two Fourier rows form a two-dimensional scalar quotient of cycle adjacency. -/
theorem cycleFourierFactor_map_adjacency (n : ℕ) (z : k)
    (hroot : z ^ (n + 3) = 1) (x : Fin (n + 3) → k) :
    cycleFourierFactor n z (cycleAdjacency n x) =
      (z + z⁻¹) • cycleFourierFactor n z x := by
  funext a
  fin_cases a
  · change cycleFourierRow n z (cycleAdjacency n x) =
      (z + z⁻¹) * cycleFourierRow n z x
    exact cycleFourierRow_map_adjacency n z hroot x
  · change cycleFourierRow n z⁻¹ (cycleAdjacency n x) =
      (z + z⁻¹) * cycleFourierRow n z⁻¹ x
    rw [cycleFourierRow_map_adjacency]
    · simp [add_comm]
    · simpa [inv_pow] using congrArg Inv.inv hroot

/--
For every field containing a non-real `N`th root of unity, the cycle on
`N = n + 3` vertices has exact operator seed number two.
-/
theorem cycle_seedNumber_isLeast_two_of_root (n : ℕ) (z : k)
    (hroot : z ^ (n + 3) = 1) (hz : z ≠ z⁻¹) :
    IsLeast {r : ℕ | SeedNumberLE (cycleAdjacency (k := k) n) r} 2 := by
  constructor
  · exact ⟨cycleSeeds (k := k) n, cycleSeeds_generate (k := k) n⟩
  · intro r hr
    obtain ⟨v, hv⟩ := hr
    have hle := multiplicity_le_of_generates
      (cycleAdjacency (k := k) n) v 2 (cycleFourierFactor n z)
      (cycleFourierFactor_surjective n z hz) (z + z⁻¹)
      (eval_intertwining_of_map_T_eq_smul
        (cycleAdjacency (k := k) n) (cycleFourierFactor n z) (z + z⁻¹)
        (cycleFourierFactor_map_adjacency n z hroot)) hv
    simpa using hle

/-- A primitive root of order at least three is distinct from its inverse. -/
theorem primitiveRoot_ne_inv (n : ℕ) (z : k)
    (hprimitive : IsPrimitiveRoot z (n + 3)) : z ≠ z⁻¹ := by
  have hz0 : z ≠ 0 := (hprimitive.isUnit (by omega)).ne_zero
  have hpred : z ^ (n + 2) = z⁻¹ := by
    apply (mul_right_cancel₀ hz0)
    have hpow := pow_sub_one_mul (n := n + 3) (by omega) z
    simp only [show n + 3 - 1 = n + 2 by omega] at hpow
    rw [hpow, hprimitive.pow_eq_one]
    simp [hz0]
  intro h
  have hpowers : z ^ 1 = z ^ (n + 2) := by
    calc
      z ^ 1 = z := pow_one z
      _ = z⁻¹ := h
      _ = z ^ (n + 2) := hpred.symm
  have hexponents := hprimitive.pow_inj
    (i := 1) (j := n + 2) (by omega) (by omega) hpowers
  omega

/-- The canonical complex primitive root used for the cycle spectrum. -/
noncomputable def complexCycleRoot (n : ℕ) : ℂ :=
  Complex.exp (2 * Real.pi * Complex.I / (n + 3))

/-- Every simple complex cycle `C_N`, `N ≥ 3`, has seed rank exactly two. -/
theorem complex_cycle_seedNumber_isLeast_two (n : ℕ) :
    IsLeast {r : ℕ |
      SeedNumberLE (cycleAdjacency (k := ℂ) n) r} 2 := by
  have hprimitive : IsPrimitiveRoot (complexCycleRoot n) (n + 3) := by
    simpa [complexCycleRoot] using
      Complex.isPrimitiveRoot_exp (n + 3) (by omega)
  exact cycle_seedNumber_isLeast_two_of_root n (complexCycleRoot n)
    hprimitive.pow_eq_one (primitiveRoot_ne_inv n (complexCycleRoot n) hprimitive)

end CycleGraph

end Komorebi.SingleOperatorGraph

#print axioms Komorebi.SingleOperatorGraph.singleOperator_seedNumber_isLeast_of_primary_decomposition
#print axioms Komorebi.SingleOperatorGraph.restrictScalars_span_operatorAlgebra_eq_span_orbit
#print axioms Komorebi.SingleOperatorGraph.operatorAlgebra_seedFinrank_eq_of_seedNumber_isLeast
#print axioms Komorebi.SingleOperatorGraph.operatorAlgebra_seedRank_eq_of_seedNumber_isLeast
#print axioms Komorebi.SingleOperatorGraph.singleOperator_operatorAlgebra_seedRanks_eq_of_primary_decomposition
#print axioms Komorebi.SingleOperatorGraph.cyclic_matrix_criterion_of_primary_decomposition
#print axioms Komorebi.SingleOperatorGraph.cyclic_matrix_four_way_iff_of_primary_decomposition
#print axioms Komorebi.SingleOperatorGraph.graph_seedNumber_eq_max_eigenspace_multiplicity
#print axioms Komorebi.SingleOperatorGraph.graph_seedNumber_eq_max_eigenspace_multiplicity_of_distinct
#print axioms Komorebi.SingleOperatorGraph.path_endpoint_seedNumber_isLeast_one
#print axioms Komorebi.SingleOperatorGraph.complex_cycle_seedNumber_isLeast_two
