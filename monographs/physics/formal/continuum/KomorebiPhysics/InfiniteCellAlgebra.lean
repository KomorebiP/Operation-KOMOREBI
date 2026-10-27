module
public import KomorebiPhysics.InfiniteCells

/-! Complement, repeated regrouping, and actual change-of-basis identities
for infinite-cell projectors. The optional transport is a self-adjoint
involution, a precisely declared subclass of unitaries. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace StrongAtlas
open Filter Classical
open scoped BigOperators Topology
variable {H I J K : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]
variable [CompleteSpace H] (P : StrongAtlas H I)

theorem cell_compl_add (C : Set I) :
    P.cell C + P.cell Cᶜ = ContinuousLinearMap.id ℂ H := by
  ext x
  apply P.eq_of_proj_eq
  intro i
  simp only [add_apply, map_add, P.proj_cell,
    ContinuousLinearMap.id_apply, Set.mem_compl_iff]
  by_cases hi : i ∈ C <;> simp [hi]

theorem cell_zero_iff (C : Set I) (x : H) :
    P.cell C x = 0 ↔ ∀ i ∈ C, P.proj i x = 0 := by
  constructor
  · intro h i hi
    have hh := P.proj_cell C i x
    rw [h, map_zero, ite_eq_left hi] at hh
    exact hh.symm
  · intro h
    rw [P.cell_apply]
    have hz : ∀ i : C, P.proj i x = 0 := fun i => h i i.property
    simp only [hz, tsum_zero]

theorem cell_fixed_iff (C : Set I) (x : H) :
    P.cell C x = x ↔ ∀ i ∉ C, P.proj i x = 0 := by
  constructor
  · intro h i hi
    have hh := P.proj_cell C i x
    rw [h, ite_eq_right hi] at hh
    exact hh
  · intro h
    apply P.eq_of_proj_eq
    intro i
    rw [P.proj_cell]
    by_cases hi : i ∈ C <;> simp [hi, h]

theorem proj_coarsen_cell (f : I → J) (D : Set J) (i : I) (x : H) :
    P.proj i ((P.coarsenInfinite f).cell D x) =
      if f i ∈ D then P.proj i x else 0 := by
  have hs := ((P.coarsenInfinite f).cell_sum D x).summable
  rw [cell_apply, (P.proj i).map_tsum hs]
  by_cases hi : f i ∈ D
  · rw [ite_eq_left hi, tsum_eq_single (⟨f i, hi⟩ : D)]
    · simp [coarsenInfinite_proj, P.proj_cell]
    · intro a ha
      have hn : f i ≠ (a : J) := fun h => ha (Subtype.ext h.symm)
      simp [coarsenInfinite_proj, P.proj_cell, hn]
  · rw [ite_eq_right hi]
    have hz : ∀ a : D, P.proj i ((P.coarsenInfinite f).proj a x) = 0 := by
      intro a
      have hn : f i ≠ (a : J) := fun h => hi (h ▸ a.property)
      simp [coarsenInfinite_proj, P.proj_cell, hn]
    simp only [hz, tsum_zero]

/-- Sequential cells are exactly preimages, even for infinite cells at both stages. -/
theorem coarsen_cell (f : I → J) (D : Set J) :
    (P.coarsenInfinite f).cell D = P.cell (f ⁻¹' D) := by
  ext x
  apply P.eq_of_proj_eq
  intro i
  simp only [P.proj_coarsen_cell, P.proj_cell, Set.mem_preimage]

theorem coarsenInfinite_comp (f : I → J) (g : J → K) (a : K) :
    ((P.coarsenInfinite f).coarsenInfinite g).proj a =
      (P.coarsenInfinite (g ∘ f)).proj a := by
  rw [coarsenInfinite_proj, P.coarsen_cell, coarsenInfinite_proj]
  rfl

theorem coarsenInfinite_comp_energy (f : I → J) (g : J → K) (x : H) (a : K) :
    ((P.coarsenInfinite f).coarsenInfinite g).energy x a =
      (P.coarsenInfinite (g ∘ f)).energy x a := by
  simp only [energy, P.coarsenInfinite_comp]

/-- A directly constructed transported atlas for a self-adjoint involution. -/
def reflect (U : H →L[ℂ] H)
    (hU : ∀ x y, inner ℂ (U x) y = inner ℂ x (U y))
    (hUU : ∀ x, U (U x) = x) : StrongAtlas H I where
  proj i := U * P.proj i * U
  idempotent i x := by
    simp only [mul_apply_eq_comp, hUU, P.idempotent]
  orthogonal i j hij x := by
    simp only [mul_apply_eq_comp, hUU, P.orthogonal i j hij, map_zero]
  selfAdjoint i x y := by
    simp only [mul_apply_eq_comp, hU, P.selfAdjoint]
  strong x := by
    have h := (P.strong (U x)).mapL U
    rw [hUU] at h
    exact h

omit [CompleteSpace H] in
theorem reflect_proj (U : H →L[ℂ] H)
    (hU : ∀ x y, inner ℂ (U x) y = inner ℂ x (U y))
    (hUU : ∀ x, U (U x) = x) (i : I) (x : H) :
    (P.reflect U hU hUU).proj i x = U (P.proj i (U x)) := rfl

theorem reflect_cell (U : H →L[ℂ] H)
    (hU : ∀ x y, inner ℂ (U x) y = inner ℂ x (U y))
    (hUU : ∀ x, U (U x) = x) (C : Set I) (x : H) :
    (P.reflect U hU hUU).cell C x = U (P.cell C (U x)) :=
  ((P.reflect U hU hUU).cell_sum C x).unique ((P.cell_sum C (U x)).mapL U)

omit [CompleteSpace H] in
theorem reflection_norm (U : H →L[ℂ] H)
    (hU : ∀ x y, inner ℂ (U x) y = inner ℂ x (U y))
    (hUU : ∀ x, U (U x) = x) (x : H) : ‖U x‖ = ‖x‖ := by
  have he : inner ℂ (U x) (U x) = inner ℂ x x := by rw [hU, hUU]
  have hn := congrArg Complex.re he
  have self (v : H) : (inner ℂ v v).re = ‖v‖ ^ 2 := inner_self_eq_norm_sq (𝕜 := ℂ) v
  simp only [self] at hn
  nlinarith [norm_nonneg (U x), norm_nonneg x]

end StrongAtlas
end KomorebiPhysics
