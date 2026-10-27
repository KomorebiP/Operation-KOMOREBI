import MachineTheory.DiscrepancyClosure
import Mathlib.Tactic.NormNum

/-!
# Exact examples and hypothesis boundaries for Core 2.4

These examples instantiate the actual linear maps and word executor. They
separate invisible hidden dynamics, delayed observable return, one-initial-state
agreement, the reference-candidate premise and the absence of inverse recovery.
-/
namespace Komorebi.MachineTheory.CommonQuotient.Examples

noncomputable section

abbrev V2 := ℚ × ℚ
abbrev V3 := ℚ × (ℚ × ℚ)

def first3 : V3 →ₗ[ℚ] ℚ := LinearMap.fst ℚ ℚ (ℚ × ℚ)
def second3 : V3 →ₗ[ℚ] ℚ := (LinearMap.fst ℚ ℚ ℚ).comp (LinearMap.snd ℚ ℚ (ℚ × ℚ))
def third3 : V3 →ₗ[ℚ] ℚ := (LinearMap.snd ℚ ℚ ℚ).comp (LinearMap.snd ℚ ℚ (ℚ × ℚ))
def keepTwo : V3 →ₗ[ℚ] V2 := first3.prod second3

def visibleUpdate : V2 →ₗ[ℚ] V2 :=
  ((LinearMap.fst ℚ ℚ ℚ) + (LinearMap.snd ℚ ℚ ℚ)).prod (LinearMap.snd ℚ ℚ ℚ)

/-- The source's hidden third coordinate changes with the candidate. -/
def goodFamily (θ : Bool) (_ : Unit) : V3 →ₗ[ℚ] V3 :=
  (first3 + second3).prod (second3.prod ((if θ then (2 : ℚ) else 3) • third3))

/-- The real two-coordinate model, rather than an assumed quotient interface. -/
def goodModel : CommonModel goodFamily first3 where
  Carrier := V2
  addGroup := inferInstance
  module := inferInstance
  projection := keepTwo
  onto := by
    intro z
    exact ⟨(z.1, (z.2, 0)), rfl⟩
  update := fun _ => visibleUpdate
  readout := LinearMap.fst ℚ ℚ ℚ
  intertwines := by intro θ a; apply LinearMap.ext; intro v; rfl
  reads := rfl

/-- All initial vectors and all words agree, despite distinct full-state operators. -/
theorem good_agreement : ObservableAgreement goodFamily false first3 :=
  commonModel_agreement goodFamily false first3 goodModel

/-- Candidate changes at every operation preserve the protected visible result. -/
theorem good_switching (w : List (Bool × Unit)) (v : V3) :
    first3 (switchedMap goodFamily w v) = first3 (wordMap (goodFamily false) (w.map Prod.snd) v) :=
  switching_output goodFamily false first3 good_agreement w v

/-- The candidate operators themselves have not been identified. -/
theorem good_candidates_differ : goodFamily true () ≠ goodFamily false () := by
  intro h
  have hh := congrArg third3 (LinearMap.congr_fun h (0, (0, 1)))
  norm_num [goodFamily, first3, second3, third3] at hh

/-- A protected output does not require reconstructing the hidden coordinate. -/
theorem good_projection_not_injective : ¬ Function.Injective keepTwo := by
  intro h
  have hv : ((0, (0, 0)) : V3) = ((0, (0, 1)) : V3) :=
    h (a₁ := (0, (0, 0))) (a₂ := (0, (0, 1))) rfl
  have hh := congrArg (fun v : V3 => v.2.2) hv
  norm_num at hh

/-- The canonical subspace is unchanged by choosing the other actual reference. -/
theorem good_reference_independent : discrepancy goodFamily false = discrepancy goodFamily true :=
  discrepancy_reference_independent goodFamily false true

/-- The constructed finite sequence, not an assumed limit, reaches the discrepancy space. -/
theorem good_finite_closure : stage goodFamily false (Module.finrank ℚ V3) = discrepancy goodFamily false :=
  stage_finrank_eq goodFamily false

/-- Immediate invisibility need not survive one subsequent reference action. -/
def first2 : V2 →ₗ[ℚ] ℚ := LinearMap.fst ℚ ℚ ℚ
def shift2 : V2 →ₗ[ℚ] V2 := (LinearMap.snd ℚ ℚ ℚ).prod (0 : V2 →ₗ[ℚ] ℚ)
def swap2 : V2 →ₗ[ℚ] V2 := (LinearMap.snd ℚ ℚ ℚ).prod (LinearMap.fst ℚ ℚ ℚ)
def returnFamily (θ : Bool) (_ : Unit) : V2 →ₗ[ℚ] V2 := if θ then swap2 else shift2

/-- Every one-step discrepancy is invisible under the protected readout. -/
theorem immediate_invisible (θ : Bool) (a : Unit) :
    first2.comp (returnFamily θ a - returnFamily false a) = 0 := by
  cases θ <;> apply LinearMap.ext <;> intro v <;>
    simp [returnFamily, shift2, swap2, first2]

/-- But two steps reveal a difference. -/
theorem delayed_return :
    first2 (wordMap (returnFamily true) [(), ()] (1, 0)) = 1 ∧
    first2 (wordMap (returnFamily false) [(), ()] (1, 0)) = 0 := by
  norm_num [wordMap, returnFamily, shift2, swap2, first2]

/-- The universal agreement assertion fails in the immediate-invisibility example. -/
theorem no_agreement_from_immediate_invisibility : ¬ ObservableAgreement returnFamily false first2 := by
  intro h
  have hh := LinearMap.congr_fun (h true [(), ()]) (1, 0)
  norm_num [wordMap, returnFamily, shift2, swap2, first2] at hh

/-- Consequently the propagated space, unlike its unpropagated seed, is not invisible. -/
theorem propagated_visible : ¬ discrepancy returnFamily false ≤ LinearMap.ker first2 := by
  intro h
  exact no_agreement_from_immediate_invisibility
    (agreement_of_discrepancy_invisible returnFamily false first2 h)

/-- A concrete propagated difference produces unit protected output. -/
theorem propagated_difference_value :
    first2 (returnFamily false () ((returnFamily true () - returnFamily false ()) (1, 0))) = 1 := by
  norm_num [returnFamily, shift2, swap2, first2]

/-- Two nilpotent candidate dynamics agree at one initial state, but not as operators. -/
def move12 : V3 →ₗ[ℚ] V3 := (0 : V3 →ₗ[ℚ] ℚ).prod (first3.prod (0 : V3 →ₗ[ℚ] ℚ))
def move23 : V3 →ₗ[ℚ] V3 := (0 : V3 →ₗ[ℚ] ℚ).prod ((0 : V3 →ₗ[ℚ] ℚ).prod second3)
def initialFamily (θ : Bool) (_ : Unit) : V3 →ₗ[ℚ] V3 := if θ then move23 else move12
def initialVector : V3 := (1, (0, 0))

/-- Each fixed candidate has zero output on every word from this one initial vector. -/
theorem fixed_initial_output (θ : Bool) (w : List Unit) :
    third3 (wordMap (initialFamily θ) w initialVector) = 0 := by
  cases θ <;> cases w with
  | nil => rfl
  | cons a w =>
    cases w with
    | nil => rfl
    | cons b w =>
      change third3 (wordMap _ w (0 : V3)) = 0
      rw [map_zero, map_zero]

/-- Initial-state agreement genuinely holds for both fixed candidate systems. -/
theorem one_initial_agreement (θ : Bool) (w : List Unit) :
    third3 (wordMap (initialFamily θ) w initialVector) =
      third3 (wordMap (initialFamily false) w initialVector) := by
  rw [fixed_initial_output, fixed_initial_output]

/-- Switching first to move12 and then move23 reveals a protected unit. -/
theorem switched_initial_output :
    third3 (switchedMap initialFamily [(false, ()), (true, ())] initialVector) = 1 := rfl

/-- Action/candidate order matters: the reversed execution gives zero. -/
theorem switched_reverse_output :
    third3 (switchedMap initialFamily [(true, ()), (false, ())] initialVector) = 0 := rfl

/-- The all-initial-vector condition cannot be replaced by agreement at one vector. -/
theorem one_initial_is_not_enough : ¬ ObservableAgreement initialFamily false third3 := by
  intro h
  have hs := switching_output initialFamily false third3 h
    [(false, ()), (true, ())] initialVector
  rw [switched_initial_output, fixed_initial_output] at hs
  norm_num at hs

/-- A common model for supplied candidates says nothing about an unrelated reference family. -/
theorem unrelated_reference_fails :
    (LinearMap.id : ℚ →ₗ[ℚ] ℚ).comp (wordMap (fun _ : Unit => LinearMap.id) [()]) ≠
      (LinearMap.id : ℚ →ₗ[ℚ] ℚ).comp (wordMap (fun _ : Unit => 0) [()]) := by
  intro h
  have hh := LinearMap.congr_fun h 1
  norm_num [wordMap] at hh

/-- Equal candidate dynamics produce no discrepancy, including the empty action boundary. -/
theorem identical_candidates_zero {K V A Θ : Type*} [Field K] [AddCommGroup V] [Module K V]
    (F : A → V →ₗ[K] V) (θ₀ : Θ) : discrepancy (fun _ : Θ => F) θ₀ = ⊥ := by
  apply le_antisymm _ bot_le
  apply discrepancy_le
  · intro θ a v
    simp only [sub_self, LinearMap.zero_apply, Submodule.zero_mem]
  · intro a x hx
    have hx0 : x = 0 := hx
    rw [hx0, map_zero]
    exact Submodule.zero_mem _

end
end Komorebi.MachineTheory.CommonQuotient.Examples
