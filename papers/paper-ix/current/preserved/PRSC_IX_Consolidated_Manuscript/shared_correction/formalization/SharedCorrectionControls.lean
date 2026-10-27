module

public import SharedCorrection
public import Mathlib.Data.ZMod.Basic
public import Mathlib.Tactic.NormNum

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.SharedCorrectionControls

open SharedCorrection

abbrev Two := ZMod 2
abbrev identity : Two →ₗ[Two] Two := LinearMap.id
abbrev leftCoordinate : (Two × Two) →ₗ[Two] Two := LinearMap.fst Two Two Two
abbrev rightCoordinate : (Two × Two) →ₗ[Two] Two := LinearMap.snd Two Two Two

/-- Separate solvability does not imply that one correction solves both targets. -/
theorem separately_solvable_but_incompatible :
    (∃ u : Two, identity u = 0) ∧ (∃ v : Two, identity v = 1) ∧
      ¬ ∃ w : Two, identity w = 0 ∧ identity w = 1 := by
  refine ⟨⟨0, rfl⟩, ⟨1, rfl⟩, ?_⟩
  rintro ⟨w, hw0, hw1⟩
  have h : (0 : Two) = 1 := hw0.symm.trans hw1
  norm_num at h

/-- The common quotient detects that incompatibility for the actual two maps. -/
theorem identical_maps_distinguish_targets :
    (Submodule.Quotient.mk (0 : Two) : Common identity identity) ≠
      Submodule.Quotient.mk (1 : Two) := by
  intro h
  have hw := (quotient_mk_eq_iff_common identity identity 0 1).mp h
  exact separately_solvable_but_incompatible.2.2 hw

/-- Independent coordinates admit a common correction for every pair of targets. -/
theorem independent_targets_have_equal_labels (a b : Two) :
    (Submodule.Quotient.mk (a, 0) : Common leftCoordinate rightCoordinate) =
      Submodule.Quotient.mk (0, b) := by
  apply (quotient_mk_eq_iff_common leftCoordinate rightCoordinate (a, 0) (0, b)).mpr
  exact ⟨(a, b), rfl, rfl⟩

/-- For independent coordinates the joint image fills the entire product of ranges. -/
theorem independent_joint_range_top :
    LinearMap.range (joint leftCoordinate rightCoordinate) = ⊤ := by
  ext z
  simp only [Submodule.mem_top, iff_true]
  refine ⟨(z.1.val, z.2.val), ?_⟩
  apply Prod.ext <;> apply Subtype.ext <;> rfl

/-- A zero left map contributes no compatibility restriction. -/
theorem zero_left_identifies_all (u v : Two) :
    (Submodule.Quotient.mk u : Common (0 : Two →ₗ[Two] Two) identity) =
      Submodule.Quotient.mk v := by
  apply (quotient_mk_eq_iff_common (0 : Two →ₗ[Two] Two) identity u v).mpr
  exact ⟨v, rfl, rfl⟩

/-- Evaluation of an arbitrary sequence at a specified coordinate. -/
def evaluateCoordinate (n : ℕ) : (ℕ → Two) →ₗ[Two] Two where
  toFun f := f n
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

/-- Finite local target implies a finite quotient even for the full sequence domain. -/
theorem sequence_domain_common_finite :
    Infinite (ℕ → Two) ∧ Finite (Common (evaluateCoordinate 0) (evaluateCoordinate 1)) := by
  constructor
  · infer_instance
  · exact common_finite_of_left (evaluateCoordinate 0) (evaluateCoordinate 1)

end Komorebi.SharedCorrectionControls

#print axioms Komorebi.SharedCorrectionControls.separately_solvable_but_incompatible
#print axioms Komorebi.SharedCorrectionControls.identical_maps_distinguish_targets
#print axioms Komorebi.SharedCorrectionControls.independent_targets_have_equal_labels
#print axioms Komorebi.SharedCorrectionControls.independent_joint_range_top
#print axioms Komorebi.SharedCorrectionControls.zero_left_identifies_all
#print axioms Komorebi.SharedCorrectionControls.sequence_domain_common_finite
