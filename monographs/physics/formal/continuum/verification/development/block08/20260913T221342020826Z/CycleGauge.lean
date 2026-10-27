module

public import KomorebiPhysics.EffectRefinement
public import Mathlib.Tactic.FinCases

/-! Chapter 5.5 (5.33)--(5.34). The ambiguity of antisymmetric currents
is characterized by zero-row-sum cycles. The generator-induced representative
is not claimed unique from continuity alone. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics.CycleGauge
open scoped BigOperators
variable {I : Type*} [Fintype I]

/-- A finite antisymmetric, divergence-free current. -/
def IsCycle (K : I → I → ℝ) : Prop :=
  (∀ i j, K i j = -K j i) ∧ (∀ i, ∑ j, K i j = 0)

theorem add_antisymm (J K : I → I → ℝ)
    (hJ : ∀ i j, J i j = -J j i) (hK : IsCycle K) :
    ∀ i j, (J i j + K i j) = -(J j i + K j i) := by
  intro i j
  rw [hJ i j, hK.1 i j]
  ring

/-- The literal continuity-preserving gauge identity. -/
theorem add_row_sum (J K : I → I → ℝ) (hK : IsCycle K) (i : I) :
    (∑ j, (J i j + K i j)) = ∑ j, J i j := by
  rw [Finset.sum_add_distrib, hK.2 i, add_zero]

/-- Conversely, two antisymmetric currents have equal divergence iff their difference is a cycle. -/
theorem difference_cycle_iff (J L : I → I → ℝ)
    (hJ : ∀ i j, J i j = -J j i) (hL : ∀ i j, L i j = -L j i) :
    IsCycle (fun i j => L i j - J i j) ↔ ∀ i, (∑ j, L i j) = ∑ j, J i j := by
  constructor
  · intro h i
    have hi := h.2 i
    simpa only [Finset.sum_sub_distrib, sub_eq_zero] using hi
  · intro h
    constructor
    · intro i j
      rw [hL i j, hJ i j]
      ring
    · intro i
      rw [Finset.sum_sub_distrib, h i, sub_self]

theorem cycle_add (K L : I → I → ℝ) (hK : IsCycle K) (hL : IsCycle L) :
    IsCycle (fun i j => K i j + L i j) := by
  exact ⟨add_antisymm K L hK.1 hL, fun i => by rw [add_row_sum K L hL i, hK.2]⟩

theorem cycle_scale (c : ℝ) (K : I → I → ℝ) (hK : IsCycle K) :
    IsCycle (fun i j => c * K i j) := by
  constructor
  · intro i j
    rw [hK.1 i j]
    ring
  · intro i
    rw [← Finset.mul_sum, hK.2 i, mul_zero]

/-- A cycle has zero net flux through every finite subsystem boundary. -/
theorem boundary_zero [DecidableEq I] (K : I → I → ℝ) (hK : IsCycle K) (C : Finset I) :
    (∑ i ∈ C, ∑ j ∈ Cᶜ, K i j) = 0 := by
  rw [← UniversalBalance.boundary_sum K hK.1 C]
  simp only [hK.2, Finset.sum_const_zero]

/-- Exact address coarsening cannot turn a pure cycle into a nonzero divergence. -/
theorem coarse_cycle {J : Type*} [Fintype J] [DecidableEq J]
    (f : I → J) (K : I → I → ℝ) (hK : IsCycle K) :
    IsCycle (fun a b => ∑ i ∈ Atlas.fiber f a, ∑ j ∈ Atlas.fiber f b, K i j) := by
  constructor
  · exact UniversalBalance.coarse_antisymm f K hK.1
  · intro a
    rw [UniversalBalance.coarse_row_sum]
    simp only [hK.2, Finset.sum_const_zero]

/-- Actual Born continuity remains unchanged after adding a cycle. -/
theorem hasDerivAt_gauged_probability {H : Type*} [NormedAddCommGroup H]
    [InnerProductSpace ℂ H] (F : EffectAtlas H I) (A : H →L[ℂ] H) (hA : IsSkew A)
    {ψ : ℝ → H} {t : ℝ} (hψ : HasDerivAt ψ (A (ψ t)) t)
    (K : I → I → ℝ) (hK : IsCycle K) (i : I) :
    HasDerivAt (fun s => F.probability (ψ s) i)
      (∑ j, (F.current A (ψ t) i j + K i j)) t := by
  rw [add_row_sum _ _ hK]
  exact F.hasDerivAt_probability A hA hψ i

/-- A nonzero exact three-label cycle. -/
def triangle : Fin 3 → Fin 3 → ℝ :=
  ![![0, 1, -1], ![-1, 0, 1], ![1, -1, 0]]

theorem triangle_isCycle : IsCycle triangle := by
  constructor
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [triangle]
  · intro i
    fin_cases i <;> norm_num [triangle, Fin.sum_univ_three]

theorem triangle_nonzero : triangle ≠ 0 := by
  intro h
  have he := congrArg (fun K : Fin 3 → Fin 3 → ℝ => K 0 1) h
  norm_num [triangle] at he

end KomorebiPhysics.CycleGauge
