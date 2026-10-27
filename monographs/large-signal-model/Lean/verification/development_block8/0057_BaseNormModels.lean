import KomorebiLSM.InstrumentContraction
import KomorebiLSM.FiniteTV

/-! The constructed norm is connected to the previously checked finite lifts.
Injective synthesis gives the exact coefficient l1 norm; redundancy gives only an upper bound. -/
set_option autoImplicit false
namespace Komorebi.LSM.BaseNorm
open scoped BigOperators
open FiniteInstruments FiniteBayes PositiveLift
variable {E J : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [FiniteDimensional ℝ E] [Fintype J] [DecidableEq J]

/-- Every normalized full-row-rank positive-lift domain supplies the norm construction. -/
noncomputable def finiteCone (V : (J → ℝ) →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (hn : l.comp V=mass) (hs : Function.Surjective V) : ProbabilityCone E where
  carrier := hull V
  zero_mem := hull_zero V
  add_mem := hull_add V
  smul_mem := hull_smul V
  spans := hull_spans V hs
  mass := l
  mass_pos := fun hx hne => hull_strict_mass V l hn _ hx hne
  closed := hull_closed V l hn

theorem finiteCone_base (V : (J → ℝ) →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (hn : l.comp V=mass) (hs : Function.Surjective V) :
    (finiteCone V l hn hs).base=convexHull ℝ (Set.range (generator V)) :=
  normalizedHull_eq_convexHull V l hn

omit [NormedAddCommGroup E] [NormedSpace ℝ E] [FiniteDimensional ℝ E] [DecidableEq J] in
theorem positive_negative_parts (x : J → ℝ) :
    x=(fun j => max (x j) 0)-(fun j => max (-x j) 0) ∧
    mass (fun j => max (x j) 0)+mass (fun j => max (-x j) 0)=FiniteTV.l1 x := by
  constructor
  · funext j
    change x j=max (x j) 0-max (-x j) 0
    by_cases hx : 0 ≤ x j
    · rw [max_eq_left hx,max_eq_right (neg_nonpos.mpr hx)]; ring
    · have hn : x j ≤ 0 := le_of_not_ge hx
      rw [max_eq_right hn,max_eq_left (neg_nonneg.mpr hn)]; ring
  · rw [mass_apply,mass_apply,← Finset.sum_add_distrib]
    apply Finset.sum_congr rfl
    intro j _
    by_cases hx : 0 ≤ x j
    · rw [max_eq_left hx,max_eq_right (neg_nonpos.mpr hx),abs_of_nonneg hx]; ring
    · have hn : x j ≤ 0 := le_of_not_ge hx
      rw [max_eq_right hn,max_eq_left (neg_nonneg.mpr hn),abs_of_nonpos hn]; ring

/-- Any signed coefficient representation gives an upper bound, not necessarily the minimum. -/
theorem value_synthesis_le_l1 (V : (J → ℝ) →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (hn : l.comp V=mass) (hs : Function.Surjective V) (x : J → ℝ) :
    (finiteCone V l hn hs).value (V x) ≤ FiniteTV.l1 x := by
  obtain ⟨he,hm⟩ := positive_negative_parts x
  let a : J → ℝ := fun j => max (x j) 0
  let b : J → ℝ := fun j => max (-x j) 0
  have ha : V a ∈ (finiteCone V l hn hs).carrier := ⟨a,fun j => le_max_right _ _,rfl⟩
  have hb : V b ∈ (finiteCone V l hn hs).carrier := ⟨b,fun j => le_max_right _ _,rfl⟩
  have h := (finiteCone V l hn hs).value_le_cost (x := V x) ha hb
    (by rw [← map_sub]; exact congrArg V he)
  have hma : l (V a)=mass a := by simpa only [← mass_apply] using normalized_mass V l hn a
  have hmb : l (V b)=mass b := by simpa only [← mass_apply] using normalized_mass V l hn b
  change _ ≤ l (V a)+l (V b) at h
  rw [hma,hmb] at h
  exact h.trans_eq hm

/-- Injective synthesis makes the upper bound an equality. -/
theorem value_synthesis_eq_l1 (V : (J → ℝ) →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (hn : l.comp V=mass) (hs : Function.Surjective V) (hi : Function.Injective V) (x : J → ℝ) :
    (finiteCone V l hn hs).value (V x)=FiniteTV.l1 x := by
  apply le_antisymm (value_synthesis_le_l1 V l hn hs x)
  apply (finiteCone V l hn hs).le_value
  rintro u ⟨a,ha,rfl⟩ v ⟨b,hb,rfl⟩ he
  have hx : x=a-b := hi (by rw [map_sub]; exact he)
  have h := FiniteTV.l1_sub_le a b
  rw [FiniteTV.l1_of_nonneg a ha,FiniteTV.l1_of_nonneg b hb] at h
  change FiniteTV.l1 x ≤ l (V a)+l (V b)
  rw [normalized_mass V l hn,normalized_mass V l hn]
  simpa only [hx,mass_apply] using h

/-- The manuscript's invertible-atlas formula, using its actual inverse. -/
theorem value_invertible_synthesis (V : (J → ℝ) ≃ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (hn : l.comp V.toLinearMap=mass) (x : E) :
    (finiteCone V.toLinearMap l hn V.surjective).value x=FiniteTV.l1 (V.symm x) := by
  simpa only [LinearEquiv.coe_coe,LinearEquiv.apply_symm_apply] using
    value_synthesis_eq_l1 V.toLinearMap l hn V.surjective V.injective (V.symm x)

/-- The ordinary orthant, constructed through the finite positive-lift interface. -/
noncomputable def orthant (J : Type*) [Fintype J] [DecidableEq J] : ProbabilityCone (J → ℝ) :=
  finiteCone LinearMap.id mass (by simp) Function.surjective_id

@[simp] theorem orthant_carrier (x : J → ℝ) : x ∈ (orthant J).carrier ↔ ∀ j, 0 ≤ x j := by
  constructor
  · rintro ⟨a,ha,he⟩; simpa only [LinearMap.id_apply] using he ▸ ha
  · intro hx; exact ⟨x,hx,rfl⟩

@[simp] theorem orthant_value (x : J → ℝ) : (orthant J).value x=FiniteTV.l1 x := by
  simpa only [orthant,LinearMap.id_apply] using
    value_synthesis_eq_l1 (LinearMap.id : (J → ℝ) →ₗ[ℝ] (J → ℝ)) mass
      (by simp) Function.surjective_id Function.injective_id x

/-- A scalar probability cone for exact record-law examples. -/
noncomputable def scalarCone : ProbabilityCone ℝ where
 carrier := {x : ℝ | 0 ≤ x}
 zero_mem := by change (0 : ℝ) ≤ 0; exact le_rfl
 add_mem := by
  intro x y hx hy
  change (0 : ℝ) ≤ x at hx
  change (0 : ℝ) ≤ y at hy
  change (0 : ℝ) ≤ x+y
  exact add_nonneg hx hy
 smul_mem := by
  intro a ha x hx
  change (0 : ℝ) ≤ x at hx
  change (0 : ℝ) ≤ a*x
  exact mul_nonneg ha hx
 spans := by
  apply top_unique
  intro x _
  have h : (1 : ℝ) ∈ Submodule.span ℝ {x : ℝ | 0 ≤ x} := Submodule.subset_span (by norm_num)
  simpa using Submodule.smul_mem (Submodule.span ℝ {x : ℝ | 0 ≤ x}) x h
 mass := LinearMap.id
 mass_pos := by
  intro x hx hn
  change (0 : ℝ) ≤ x at hx
  change (0 : ℝ) < x
  exact lt_of_le_of_ne hx (Ne.symm hn)
 closed := isClosed_le continuous_const continuous_id

@[simp] theorem scalar_value (x : ℝ) : scalarCone.value x=|x| := by
  by_cases hx : 0 ≤ x
  · exact (scalarCone.value_on_cone hx).trans (abs_of_nonneg hx).symm
  · have hn : 0 ≤ -x := neg_nonneg.mpr (le_of_not_ge hx)
    have h := scalarCone.value_on_cone hn
    rw [scalarCone.value_neg] at h
    exact h.trans (abs_of_neg (lt_of_not_ge hx)).symm

end Komorebi.LSM.BaseNorm
