import KomorebiLSM.FiniteBayes
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.LinearAlgebra.Dual.Defs

/-! Finite nonnegative probability instruments with chronological word semantics.
Mass, positivity and the restriction to positive-probability conditioning are explicit. -/
set_option autoImplicit false
namespace Komorebi.LSM.FiniteInstruments
open scoped BigOperators
open FiniteBayes
universe u v w
variable {I : Type u} {U : Type v} {O : Type w}

section Normalization
variable {E : Type*} [AddCommGroup E] [Module ℝ E]

noncomputable def normalize (l : E →ₗ[ℝ] ℝ) (x : E) : E := (l x)⁻¹ • x

theorem normalize_mass (l : E →ₗ[ℝ] ℝ) (x : E) (h : l x ≠ 0) :
    l (normalize l x) = 1 := by
  simp [normalize, h]

theorem normalize_zero_mass (l : E →ₗ[ℝ] ℝ) (x : E) (h : l x = 0) :
    normalize l x = 0 := by
  simp [normalize, h]

theorem recover_from_normalize (l : E →ₗ[ℝ] ℝ) (x : E) (h : l x ≠ 0) :
    l x • normalize l x = x := by
  simp [normalize, smul_smul, h]

end Normalization

section FiniteMass
variable [Fintype I]

noncomputable def mass : (I → ℝ) →ₗ[ℝ] ℝ := ∑ i, LinearMap.proj i

@[simp] theorem mass_apply (p : I → ℝ) : mass p = ∑ i, p i := by
  simp [mass, LinearMap.sum_apply]

theorem mass_prior (p : I → ℝ) (hp : IsPrior p) : mass p = 1 := by
  simpa only [mass_apply] using hp.2

theorem mass_nonneg (p : I → ℝ) (hp : ∀ i, 0 ≤ p i) : 0 ≤ mass p := by
  rw [mass_apply]
  exact Finset.sum_nonneg (fun i _ => hp i)

theorem normalized_prior (p : I → ℝ) (hp : ∀ i, 0 ≤ p i) (hm : 0 < mass p) :
    IsPrior (normalize mass p) := by
  refine ⟨fun i => mul_nonneg (inv_nonneg.mpr hm.le) (hp i), ?_⟩
  simpa only [mass_apply] using normalize_mass mass p (ne_of_gt hm)

theorem vector_eq_sum_pointMass [DecidableEq I] (p : I → ℝ) :
    p = ∑ i, p i • pointMass i := by
  funext j
  simp [pointMass, Finset.sum_apply, Pi.smul_apply, smul_eq_mul]

theorem point_prior [DecidableEq I] (i : I) : IsPrior (pointMass i) := by
  constructor
  · intro j; simp only [pointMass]; positivity
  · simp [pointMass]

theorem mass_pointMass [DecidableEq I] (i : I) : mass (pointMass i) = 1 :=
  mass_prior _ (point_prior i)

theorem mass_ne_zero [Nonempty I] : (mass : (I → ℝ) →ₗ[ℝ] ℝ) ≠ 0 := by
  classical
  intro h
  let i : I := Classical.choice inferInstance
  have he := mass_pointMass i
  rw [h] at he
  norm_num at he

/-- Equality on all beliefs determines a linear map on the entire vector space. -/
theorem linearMap_eq_of_priors {E : Type*} [AddCommGroup E] [Module ℝ E]
    (F G : (I → ℝ) →ₗ[ℝ] E)
    (h : ∀ p, IsPrior p → F p = G p) : F = G := by
  classical
  apply LinearMap.ext
  intro p
  rw [vector_eq_sum_pointMass p, map_sum, map_sum]
  apply Finset.sum_congr rfl
  intro i _
  simp only [map_smul, h _ (point_prior i)]

end FiniteMass

section Words
variable {X : Type*} [AddCommGroup X] [Module ℝ X] {S : Type*}

/-- Symbols are listed in time order. The head acts first. -/
def wordAction (L : S → X →ₗ[ℝ] X) : List S → X →ₗ[ℝ] X
  | [] => LinearMap.id
  | s :: w => (wordAction L w).comp (L s)

@[simp] theorem wordAction_nil (L : S → X →ₗ[ℝ] X) : wordAction L [] = LinearMap.id := rfl

@[simp] theorem wordAction_cons (L : S → X →ₗ[ℝ] X) (s : S) (w : List S) :
    wordAction L (s::w) = (wordAction L w).comp (L s) := rfl

theorem wordAction_append (L : S → X →ₗ[ℝ] X) (v w : List S) :
    wordAction L (v++w) = (wordAction L w).comp (wordAction L v) := by
  induction v with
  | nil => simp
  | cons s v ih => simp [ih, LinearMap.comp_assoc]

theorem word_intertwining {E : Type*} [AddCommGroup E] [Module ℝ E]
    (L : S → X →ₗ[ℝ] X) (B : S → E →ₗ[ℝ] E) (R : X →ₗ[ℝ] E)
    (h : ∀ s, (B s).comp R = R.comp (L s)) (w : List S) :
    (wordAction B w).comp R = R.comp (wordAction L w) := by
  induction w with
  | nil => simp
  | cons s w ih =>
    rw [wordAction_cons, wordAction_cons, LinearMap.comp_assoc, h s,
      ← LinearMap.comp_assoc, ih, LinearMap.comp_assoc]

end Words

/-- The branch entry (j,i) is joint next-state/observation probability. -/
structure Instrument (I : Type u) (U : Type v) (O : Type w) [Fintype I] [Fintype O] where
  matrix : U → O → Matrix I I ℝ
  nonneg : ∀ a o j i, 0 ≤ matrix a o j i
  mass_one : ∀ a i, ∑ o, ∑ j, matrix a o j i = 1

namespace Instrument
variable [Fintype I] [Fintype O]
variable (T : Instrument I U O)

noncomputable def branch (s : U × O) : (I → ℝ) →ₗ[ℝ] (I → ℝ) :=
  (T.matrix s.1 s.2).mulVecLin

@[simp] theorem branch_apply (s : U × O) (p : I → ℝ) (j : I) :
    T.branch s p j = ∑ i, T.matrix s.1 s.2 j i * p i := rfl

theorem branch_nonneg (s : U × O) (p : I → ℝ) (hp : ∀ i, 0 ≤ p i) :
    ∀ j, 0 ≤ T.branch s p j := by
  intro j
  exact Finset.sum_nonneg (fun i _ => mul_nonneg (T.nonneg _ _ _ _) (hp i))

theorem instrument_mass (a : U) (p : I → ℝ) :
    ∑ o, mass (T.branch (a,o) p) = mass p := by
  simp only [mass_apply, branch_apply]
  conv_lhs => arg 2; ext o; rw [Finset.sum_comm]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro i _
  simp only [← Finset.sum_mul, T.mass_one, one_mul]

theorem instrument_mass_linear (a : U) :
    ∑ o, mass.comp (T.branch (a,o)) = mass := by
  ext p
  simpa only [LinearMap.sum_apply, LinearMap.comp_apply] using T.instrument_mass a p

theorem branch_mass_nonneg (s : U × O) (p : I → ℝ) (hp : ∀ i, 0 ≤ p i) :
    0 ≤ mass (T.branch s p) := mass_nonneg _ (T.branch_nonneg s p hp)

theorem branch_mass_le (a : U) (o : O) (p : I → ℝ) (hp : ∀ i, 0 ≤ p i) :
    mass (T.branch (a,o) p) ≤ mass p := by
  rw [← T.instrument_mass a p]
  exact Finset.single_le_sum (fun o _ => T.branch_mass_nonneg (a,o) p hp) (Finset.mem_univ o)

theorem likelihood_prior (a : U) (p : I → ℝ) (hp : IsPrior p) :
    IsPrior (fun o => mass (T.branch (a,o) p)) := by
  exact ⟨fun o => T.branch_mass_nonneg (a,o) p hp.1,
    (T.instrument_mass a p).trans (mass_prior p hp)⟩

theorem branch_posterior_prior (s : U × O) (p : I → ℝ) (hp : IsPrior p)
    (h : 0 < mass (T.branch s p)) : IsPrior (normalize mass (T.branch s p)) :=
  normalized_prior _ (T.branch_nonneg s p hp.1) h

theorem word_nonneg (w : List (U × O)) (p : I → ℝ) (hp : ∀ i, 0 ≤ p i) :
    ∀ i, 0 ≤ wordAction T.branch w p i := by
  induction w generalizing p with
  | nil => exact hp
  | cons s w ih => exact ih _ (T.branch_nonneg s p hp)

theorem word_mass_le (w : List (U × O)) (p : I → ℝ) (hp : ∀ i, 0 ≤ p i) :
    mass (wordAction T.branch w p) ≤ mass p := by
  induction w generalizing p with
  | nil => exact le_rfl
  | cons s w ih =>
    exact (ih _ (T.branch_nonneg s p hp)).trans (T.branch_mass_le s.1 s.2 p hp)

theorem word_probability (w : List (U × O)) (p : I → ℝ) (hp : IsPrior p) :
    0 ≤ mass (wordAction T.branch w p) ∧ mass (wordAction T.branch w p) ≤ 1 := by
  exact ⟨mass_nonneg _ (T.word_nonneg w p hp.1),
    (T.word_mass_le w p hp.1).trans_eq (mass_prior p hp)⟩

/-- Total weight of the observation tree for a fixed action list. -/
noncomputable def observationTreeMass : List U → (I → ℝ) → ℝ
  | [], p => mass p
  | a::as, p => ∑ o, observationTreeMass as (T.branch (a,o) p)

theorem observationTreeMass_eq (as : List U) (p : I → ℝ) :
    T.observationTreeMass as p = mass p := by
  induction as generalizing p with
  | nil => rfl
  | cons a as ih =>
    change (∑ o, T.observationTreeMass as (T.branch (a,o) p)) = mass p
    simp only [ih, T.instrument_mass]

end Instrument
end Komorebi.LSM.FiniteInstruments
