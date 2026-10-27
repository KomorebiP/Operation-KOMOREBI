import Mathlib.Analysis.Normed.Module.FiniteDimension
import Mathlib.Analysis.Convex.Hull
import Mathlib.Topology.Order.Compact
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

/-! The probability base norm is the infimum of actual positive decompositions.
Its algebraic laws are derived from cone closure and generation. -/
set_option autoImplicit false
namespace Komorebi.LSM.BaseNorm
open scoped BigOperators
variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]

/-- Closed, generating positive cone with a strictly positive mass functional. -/
structure ProbabilityCone (E : Type*) [NormedAddCommGroup E] [NormedSpace ℝ E] where
  carrier : Set E
  zero_mem : (0 : E) ∈ carrier
  add_mem : ∀ {x y : E}, x ∈ carrier → y ∈ carrier → x+y ∈ carrier
  smul_mem : ∀ {a : ℝ}, 0 ≤ a → ∀ {x : E}, x ∈ carrier → a • x ∈ carrier
  spans : Submodule.span ℝ carrier = ⊤
  mass : E →ₗ[ℝ] ℝ
  mass_pos : ∀ {x : E}, x ∈ carrier → x ≠ 0 → 0 < mass x
  closed : IsClosed carrier

namespace ProbabilityCone
variable (C : ProbabilityCone E)

def base : Set E := {x | x ∈ C.carrier ∧ C.mass x = 1}

theorem mass_nonneg {x : E} (hx : x ∈ C.carrier) : 0 ≤ C.mass x := by
  by_cases h : x = 0
  · simp [h]
  · exact (C.mass_pos hx h).le

theorem mass_zero_iff {x : E} (hx : x ∈ C.carrier) : C.mass x = 0 ↔ x = 0 := by
  constructor
  · intro hm
    by_contra hn
    exact (ne_of_gt (C.mass_pos hx hn)) hm
  · intro h; simp [h]

theorem convex_carrier : Convex ℝ C.carrier := by
  intro x hx y hy a b ha hb _
  exact C.add_mem (C.smul_mem ha hx) (C.smul_mem hb hy)

/-- Generation is converted to positive differences, rather than assumed as a norm law. -/
theorem exists_decomposition (x : E) : ∃ u ∈ C.carrier, ∃ v ∈ C.carrier, x = u-v := by
  have hx : x ∈ Submodule.span ℝ C.carrier := by rw [C.spans]; trivial
  induction hx using Submodule.span_induction with
  | mem x hx => exact ⟨x,hx,0,C.zero_mem,by simp⟩
  | zero => exact ⟨0,C.zero_mem,0,C.zero_mem,by simp⟩
  | add x y _ _ hx hy =>
    obtain ⟨u,hu,v,hv,rfl⟩ := hx
    obtain ⟨s,hs,t,ht,rfl⟩ := hy
    exact ⟨u+s,C.add_mem hu hs,v+t,C.add_mem hv ht,by abel⟩
  | smul a x _ hx =>
    obtain ⟨u,hu,v,hv,rfl⟩ := hx
    by_cases ha : 0 ≤ a
    · exact ⟨a • u,C.smul_mem ha hu,a • v,C.smul_mem ha hv,smul_sub a u v⟩
    · have hn : 0 ≤ -a := neg_nonneg.mpr (le_of_not_ge ha)
      refine ⟨(-a) • v,C.smul_mem hn hv,(-a) • u,C.smul_mem hn hu,?_⟩
      simp only [smul_sub,neg_smul]; abel

def costs (x : E) : Set ℝ :=
  {r | ∃ u ∈ C.carrier, ∃ v ∈ C.carrier, x = u-v ∧ r = C.mass u + C.mass v}

noncomputable def value (x : E) : ℝ := sInf (C.costs x)

theorem costs_nonempty (x : E) : (C.costs x).Nonempty := by
  obtain ⟨u,hu,v,hv,hx⟩ := C.exists_decomposition x
  exact ⟨_,u,hu,v,hv,hx,rfl⟩

theorem cost_nonneg {x : E} {r : ℝ} (hr : r ∈ C.costs x) : 0 ≤ r := by
  obtain ⟨u,hu,v,hv,_,rfl⟩ := hr
  exact add_nonneg (C.mass_nonneg hu) (C.mass_nonneg hv)

theorem costs_bddBelow (x : E) : BddBelow (C.costs x) :=
  ⟨0,fun _ h => C.cost_nonneg h⟩

theorem value_nonneg (x : E) : 0 ≤ C.value x :=
  le_csInf (C.costs_nonempty x) (fun _ h => C.cost_nonneg h)

theorem value_le_cost {x u v : E} (hu : u ∈ C.carrier) (hv : v ∈ C.carrier)
    (hx : x = u-v) : C.value x ≤ C.mass u + C.mass v :=
  csInf_le (C.costs_bddBelow x) ⟨u,hu,v,hv,hx,rfl⟩

theorem le_value {x : E} {a : ℝ}
    (h : ∀ u ∈ C.carrier, ∀ v ∈ C.carrier, x = u-v → a ≤ C.mass u+C.mass v) :
    a ≤ C.value x := by
  apply le_csInf (C.costs_nonempty x)
  rintro r ⟨u,hu,v,hv,hx,rfl⟩
  exact h u hu v hv hx

theorem abs_mass_le (x : E) : |C.mass x| ≤ C.value x := by
  apply C.le_value
  intro u hu v hv hx
  rw [hx,map_sub]
  exact abs_sub_le_iff.mpr ⟨by linarith [C.mass_nonneg hv],by linarith [C.mass_nonneg hu]⟩

theorem value_on_cone {x : E} (hx : x ∈ C.carrier) : C.value x = C.mass x := by
  apply le_antisymm
  · simpa using C.value_le_cost hx C.zero_mem (by simp : x=x-0)
  · simpa only [abs_of_nonneg (C.mass_nonneg hx)] using C.abs_mass_le x

@[simp] theorem value_zero : C.value 0 = 0 := by
  simpa using C.value_on_cone C.zero_mem

theorem value_neg_le (x : E) : C.value (-x) ≤ C.value x := by
  apply C.le_value
  intro u hu v hv hx
  have hn : -x=v-u := by rw [hx]; abel
  simpa [add_comm] using C.value_le_cost hv hu hn

@[simp] theorem value_neg (x : E) : C.value (-x) = C.value x := by
  exact le_antisymm (C.value_neg_le x) (by simpa using C.value_neg_le (-x))

theorem value_add_le (x y : E) : C.value (x+y) ≤ C.value x+C.value y := by
  have h : C.value (x+y)-C.value y ≤ C.value x := by
    apply C.le_value
    intro u hu v hv hx
    have h' : C.value (x+y)-(C.mass u+C.mass v) ≤ C.value y := by
      apply C.le_value
      intro s hs t ht hy
      have he : x+y=(u+s)-(v+t) := by rw [hx,hy]; abel
      have hb := C.value_le_cost (C.add_mem hu hs) (C.add_mem hv ht) he
      simp only [map_add] at hb
      linarith
    linarith
  linarith

theorem value_sub_le (x y : E) : C.value (x-y) ≤ C.value x+C.value y := by
  simpa only [sub_eq_add_neg,C.value_neg] using C.value_add_le x (-y)

theorem value_smul_le {a : ℝ} (ha : 0 ≤ a) (x : E) : C.value (a • x) ≤ a*C.value x := by
  by_cases hz : a=0
  · simp [hz]
  have hp : 0<a := lt_of_le_of_ne ha (Ne.symm hz)
  apply (div_le_iff₀ hp).mp
  apply C.le_value
  intro u hu v hv hx
  apply (div_le_iff₀ hp).mpr
  have he : a • x=(a • u)-(a • v) := by rw [hx,smul_sub]
  have hb := C.value_le_cost (C.smul_mem ha hu) (C.smul_mem ha hv) he
  simp only [map_smul,smul_eq_mul] at hb
  nlinarith

theorem value_smul_of_nonneg {a : ℝ} (ha : 0 ≤ a) (x : E) :
    C.value (a • x) = a*C.value x := by
  apply le_antisymm (C.value_smul_le ha x)
  by_cases hz : a=0
  · simp [hz]
  have h := C.value_smul_le (inv_nonneg.mpr ha) (a • x)
  simp only [smul_smul,inv_mul_cancel₀ hz,one_smul] at h
  have hm := mul_le_mul_of_nonneg_left h ha
  simpa only [← mul_assoc,mul_inv_cancel₀ hz,one_mul] using hm

theorem value_smul (a : ℝ) (x : E) : C.value (a • x) = |a| * C.value x := by
  by_cases ha : 0 ≤ a
  · simpa [abs_of_nonneg ha] using C.value_smul_of_nonneg ha x
  · have hn : 0 ≤ -a := neg_nonneg.mpr (le_of_not_ge ha)
    have h := C.value_smul_of_nonneg hn x
    simpa only [neg_smul,C.value_neg,abs_of_neg (lt_of_not_ge ha)] using h

theorem value_sum_le {I : Type*} (s : Finset I) (f : I → E) :
    C.value (∑ i ∈ s, f i) ≤ ∑ i ∈ s, C.value (f i) := by
  classical
  induction s using Finset.induction_on with
  | empty => simp
  | @insert i s hi ih =>
    simp only [Finset.sum_insert hi]
    exact (C.value_add_le _ _).trans (add_le_add_left ih _)

theorem value_convex : ConvexOn ℝ Set.univ C.value := by
  constructor
  · exact convex_univ
  · intro x _ y _ a b ha hb _
    simpa only [C.value_smul_of_nonneg ha,C.value_smul_of_nonneg hb,smul_eq_mul] using
      C.value_add_le (a • x) (b • y)

end ProbabilityCone
end Komorebi.LSM.BaseNorm
