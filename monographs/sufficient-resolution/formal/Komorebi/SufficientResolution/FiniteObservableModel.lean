import Komorebi.SufficientResolution.FiniteHorizon
import Komorebi.SufficientResolution.BehavioralMinimality
import Mathlib.Data.Finset.Union
import Mathlib.Data.Fintype.List
import Mathlib.LinearAlgebra.Pi

/-!
# A finite observation-coordinate realization

A finite operation alphabet is explicitly enumerated through the proven horizon.
The model state space is the range of that finite observation map, not the full
product of arbitrary observation tables.  Its dynamics are transported from the
actual behavioral quotient; the equivalence and full word fidelity are proved.
-/

set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.FiniteObservableModel

open Behavioral FiniteHorizon BehavioralMinimality Module

universe uK uX uY uZ uI
variable (I : Type uI) [Fintype I] [DecidableEq I]

/-- An explicit finite enumeration, retaining every word through depth n. -/
def wordsUpTo : ℕ → Finset (List I)
  | 0 => {[]}
  | n + 1 => {[]} ∪ Finset.univ.biUnion (fun i : I => (wordsUpTo n).image (List.cons i))

 theorem mem_wordsUpTo (n : ℕ) (w : List I) :
    w ∈ wordsUpTo I n ↔ w.length ≤ n := by
  induction n generalizing w with
  | zero => simp [wordsUpTo, List.length_eq_zero_iff]
  | succ n ih =>
    cases w with
    | nil => simp [wordsUpTo]
    | cons i w => simp [wordsUpTo, ih]

 theorem wordsUpTo_mono {m n : ℕ} (h : m ≤ n) :
    wordsUpTo I m ⊆ wordsUpTo I n := by
  intro w hw
  exact (mem_wordsUpTo I n w).mpr (((mem_wordsUpTo I m w).mp hw).trans h)

/-- A genuinely finite coordinate index, including the empty observation word. -/
abbrev ObservationIndex (n : ℕ) := {w : List I // w ∈ wordsUpTo I n}

variable {I}
variable {K : Type uK} [Field K]
variable {X : Type uX} [AddCommGroup X] [Module K X]
variable {Y : Type uY} [AddCommGroup Y] [Module K Y]
variable (T : I → X →ₗ[K] X) (O : X →ₗ[K] Y)

/-- A linear map into finitely many specified future observations. -/
def observeUpTo (n : ℕ) : X →ₗ[K] (ObservationIndex I n → Y) :=
  LinearMap.pi (fun w => O.comp (wordOp T w.val))

@[simp] theorem observeUpTo_apply (n : ℕ) (x : X) (w : ObservationIndex I n) :
    observeUpTo T O n x w = O (wordOp T w.val x) := rfl

 theorem observeUpTo_eq_iff (n : ℕ) (x y : X) :
    observeUpTo T O n x = observeUpTo T O n y ↔
      ∀ w : List I, w.length ≤ n → O (wordOp T w x) = O (wordOp T w y) := by
  constructor
  · intro h w hw
    exact congrFun h ⟨w, (mem_wordsUpTo I n w).mpr hw⟩
  · intro h
    funext w
    exact h w.val ((mem_wordsUpTo I n w.val).mp w.property)

 theorem ker_observeUpTo (n : ℕ) :
    LinearMap.ker (observeUpTo T O n) = visibleKernel T O n := by
  ext x
  constructor
  · intro hx w hw
    exact congrFun (show observeUpTo T O n x = 0 from hx)
      ⟨w, (mem_wordsUpTo I n w).mpr hw⟩
  · intro hx
    change observeUpTo T O n x = 0
    funext w
    exact hx w.val ((mem_wordsUpTo I n w.val).mp w.property)

variable [FiniteDimensional K X]

/-- The sharper a priori bound uses only the initially invisible dimension. -/
abbrev horizon := finrank K (LinearMap.ker O)

 theorem ker_complete_observation :
    LinearMap.ker (observeUpTo T O (horizon O)) = invisible T O := by
  rw [ker_observeUpTo]
  exact visibleKernel_stabilizes T O

/-- Only realizable observation tables are states of the finite-coordinate model. -/
abbrev ObservableState := LinearMap.range (observeUpTo T O (horizon O))

/-- Actual finite observation coordinates of a fine state. -/
def coordinateMap : X →ₗ[K] ObservableState T O :=
  (observeUpTo T O (horizon O)).rangeRestrict

omit [FiniteDimensional K X] in
 theorem coordinateMap_surjective : Function.Surjective (coordinateMap T O) := by
  rintro ⟨v, hv⟩
  obtain ⟨x, hx⟩ := hv
  exact ⟨x, Subtype.ext hx⟩

/-- Finite observation coordinates realize exactly the all-future quotient. -/
def observableEquiv : State T O ≃ₗ[K] ObservableState T O :=
  (Submodule.quotEquivOfEq (invisible T O)
    (LinearMap.ker (observeUpTo T O (horizon O))) (ker_complete_observation T O).symm).trans
      (observeUpTo T O (horizon O)).quotKerEquivRange

@[simp] theorem observableEquiv_quotient (x : X) :
    observableEquiv T O (quotientMap T O x) = coordinateMap T O x := rfl

 theorem coordinateMap_eq_iff_same_future (x y : X) :
    coordinateMap T O x = coordinateMap T O y ↔
      ∀ w : List I, O (wordOp T w x) = O (wordOp T w y) := by
  rw [← observableEquiv_quotient, ← observableEquiv_quotient,
    (observableEquiv T O).injective.eq_iff, quotient_eq_iff_same_future]

/-- Each allowed operation acts on the actual finite observation range. -/
def coordinateDynamics (i : I) : ObservableState T O →ₗ[K] ObservableState T O :=
  (observableEquiv T O).toLinearMap.comp
    ((induced T O i).comp (observableEquiv T O).symm.toLinearMap)

/-- The current observation is recovered exactly from finite coordinates. -/
def coordinateObservation : ObservableState T O →ₗ[K] Y :=
  (observation T O).comp (observableEquiv T O).symm.toLinearMap

@[simp] theorem coordinateDynamics_on_state (i : I) (x : X) :
    coordinateDynamics T O i (coordinateMap T O x) = coordinateMap T O (T i x) := by
  change observableEquiv T O (induced T O i
    ((observableEquiv T O).symm (coordinateMap T O x))) = _
  rw [← observableEquiv_quotient T O x, LinearEquiv.symm_apply_apply,
    induced_quotient, observableEquiv_quotient]

@[simp] theorem coordinateObservation_on_state (x : X) :
    coordinateObservation T O (coordinateMap T O x) = O x := by
  change observation T O ((observableEquiv T O).symm (coordinateMap T O x)) = _
  rw [← observableEquiv_quotient T O x, LinearEquiv.symm_apply_apply,
    observation_quotient]

 theorem coordinateDynamics_word (w : List I) (x : X) :
    wordOp (coordinateDynamics T O) w (coordinateMap T O x) =
      coordinateMap T O (wordOp T w x) := by
  induction w generalizing x with
  | nil => rfl
  | cons i w ih =>
    simp only [wordOp_cons, Module.End.mul_apply, coordinateDynamics_on_state, ih]

/-- The constructed finite-coordinate model preserves every future observation. -/
 theorem coordinate_all_future_fidelity (w : List I) (x : X) :
    coordinateObservation T O
      (wordOp (coordinateDynamics T O) w (coordinateMap T O x)) =
      O (wordOp T w x) := by
  rw [coordinateDynamics_word, coordinateObservation_on_state]

 theorem coordinate_dimension :
    finrank K (ObservableState T O) = finrank K X - finrank K (invisible T O) := by
  rw [← (observableEquiv T O).finrank_eq, finrank_state]

variable {Z : Type uZ} [AddCommGroup Z] [Module K Z] [FiniteDimensional K Z]

/-- Minimality applies to all exact linear competitors, not only coordinate models. -/
 theorem coordinate_dimension_le_exact_model
    (q : X →ₗ[K] Z) (U : I → Z →ₗ[K] Z) (V : Z →ₗ[K] Y)
    (hT : ∀ i : I, q.comp (T i) = (U i).comp q) (hO : V.comp q = O) :
    finrank K (ObservableState T O) ≤ finrank K Z := by
  rw [← (observableEquiv T O).finrank_eq]
  exact finrank_state_le_model T O q U V hT hO

end Komorebi.SufficientResolution.FiniteObservableModel
