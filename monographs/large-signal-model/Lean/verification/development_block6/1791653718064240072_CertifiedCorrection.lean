import KomorebiLSM.RobustFiniteDomains
import Mathlib.Analysis.Normed.Group.Basic

/-! P41: a feasible finite witness, statistical set membership, and correction
error are separate conditions. No true-domain coverage is inferred from feasibility. -/
set_option autoImplicit false
namespace Komorebi.LSM.CertifiedCorrection
open scoped BigOperators
open FiniteInstruments PositiveLift
variable {E A O J : Type*} [AddCommGroup E] [Module ℝ E] [Fintype O] [Fintype J]

/-- These are finite feasibility constraints, not assumed future probabilities. -/
structure FeasiblePoint (V : (J → ℝ) →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) where
  family : A × O → E →ₗ[ℝ] E
  lift : A × O → Matrix J J ℝ
  nonneg : ∀ s i j, 0 ≤ lift s i j
  intertwining : ∀ s, (family s).comp V = V.comp (lift s).mulVecLin
  mass_one : ∀ a x, ∑ o, l (family (a,o) x) = l x
  initial : E
  initialCoefficients : J → ℝ
  initialPrior : FiniteBayes.IsPrior initialCoefficients
  initial_eq : V initialCoefficients = initial

namespace FeasiblePoint
variable [DecidableEq J] {V : (J → ℝ) →ₗ[ℝ] E} {l : E →ₗ[ℝ] ℝ}
variable (p : FeasiblePoint (A := A) (O := O) V l)

theorem valid_family : RobustDomains.ValidFamily (hull V) l p.family :=
  ⟨fun s => (positive_lift_iff V (p.family s)).mpr
    ⟨p.lift s,p.nonneg s,p.intertwining s⟩,p.mass_one⟩

omit [DecidableEq J] in
theorem initial_mem (hn : l.comp V = mass) : p.initial ∈ normalizedHull V l := by
  rw [← p.initial_eq,normalizedHull_eq_prior_image V l hn]
  exact ⟨p.initialCoefficients,p.initialPrior,rfl⟩

theorem all_word_probabilities (hn : l.comp V = mass) (w : List (A × O)) :
    0 ≤ l (wordAction p.family w p.initial) ∧ l (wordAction p.family w p.initial) ≤ 1 := by
  rw [← p.initial_eq]
  exact (finite_positive_lift_certificate p.family V l hn p.mass_one
    p.lift p.intertwining p.nonneg p.initialCoefficients p.initialPrior).2.2 w

end FeasiblePoint

/-- A covered true model with a fixed-domain witness supplies a feasible point. -/
theorem feasible_of_certified_member
    (V : (J → ℝ) →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (U : Set ((A × O → E →ₗ[ℝ] E) × E))
    (B : A × O → E →ₗ[ℝ] E) (z : E) (hU : (B,z) ∈ U)
    (M : A × O → Matrix J J ℝ) (hp : ∀ s i j, 0 ≤ M s i j)
    (he : ∀ s, (B s).comp V = V.comp (M s).mulVecLin)
    (hm : ∀ a x, ∑ o, l (B (a,o) x) = l x)
    (a₀ : J → ℝ) (ha₀ : FiniteBayes.IsPrior a₀) (hz : V a₀ = z) :
    ∃ p : FeasiblePoint V l, (p.family,p.initial) ∈ U :=
  ⟨⟨B,M,hp,he,hm,z,a₀,ha₀,hz⟩,hU⟩

/-- One normed-space argument applies to both operators and initial states. -/
theorem two_center_error {X : Type*} [SeminormedAddCommGroup X]
    (truth center corrected : X) (ε : ℝ)
    (ht : ‖truth-center‖ ≤ ε) (hc : ‖corrected-center‖ ≤ ε) :
    ‖corrected-truth‖ ≤ 2*ε := by
  calc
    ‖corrected-truth‖ = ‖(corrected-center)-(truth-center)‖ := by congr 1; abel
    _ ≤ ‖corrected-center‖ + ‖truth-center‖ := norm_sub_le _ _
    _ ≤ 2*ε := by linarith

end Komorebi.LSM.CertifiedCorrection
