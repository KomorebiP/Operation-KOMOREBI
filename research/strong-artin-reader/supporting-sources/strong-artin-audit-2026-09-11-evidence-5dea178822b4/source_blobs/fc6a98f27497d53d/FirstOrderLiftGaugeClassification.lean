import FirstOrderRepresentationLifts

/-!
# Gauge classification of actual first-order representation lifts

Actual square-zero lifts of a representation carry a canonical adjoint `H¹`
class. Two lifts define the same class exactly when their infinitesimal
coordinates differ by a gauge tangent, and every `H¹` class is represented by
an actual square-zero lift.
-/

namespace Komorebi.StrongArtin.FirstOrderLiftGaugeClassification

open Representation
open groupCohomology
open Komorebi.StrongArtin.RepresentationTangentCocycles
open Komorebi.StrongArtin.RepresentationGaugeH1
open Komorebi.StrongArtin.FirstOrderRepresentationLifts

noncomputable section

universe u

variable {k G V : Type u} [CommRing k] [Group G]
  [AddCommGroup V] [Module k V]

/-- The adjoint first-cohomology class of an actual square-zero lift. -/
def h1ClassOfLift (rho : Representation k G V) :
    FirstOrderLift rho → H1 (AdRep rho) :=
  fun L => tangentToH1 rho (tangentOfLift rho L)

/-- Gauge equivalence of actual first-order lifts: their infinitesimal
coordinates differ by an infinitesimal strict-conjugation direction. -/
def GaugeEquivalent (rho : Representation k G V)
    (L₁ L₂ : FirstOrderLift rho) : Prop :=
  tangentOfLift rho L₂ - tangentOfLift rho L₁ ∈ gaugeRange rho

/-- Two actual first-order lifts have the same adjoint `H¹` class exactly when
they are gauge equivalent. -/
theorem h1ClassOfLift_eq_iff_gaugeEquivalent
    (rho : Representation k G V) (L₁ L₂ : FirstOrderLift rho) :
    h1ClassOfLift rho L₁ = h1ClassOfLift rho L₂ ↔
      GaugeEquivalent rho L₁ L₂ := by
  rw [GaugeEquivalent, ← ker_tangentToH1 rho]
  rw [LinearMap.mem_ker]
  change tangentToH1 rho (tangentOfLift rho L₁) =
      tangentToH1 rho (tangentOfLift rho L₂) ↔
    tangentToH1 rho (tangentOfLift rho L₂ - tangentOfLift rho L₁) = 0
  rw [map_sub, sub_eq_zero]
  exact eq_comm

/-- Gauge equivalence can be expressed by one explicit infinitesimal
conjugation generator. -/
theorem gaugeEquivalent_iff_exists_generator
    (rho : Representation k G V) (L₁ L₂ : FirstOrderLift rho) :
    GaugeEquivalent rho L₁ L₂ ↔
      ∃ Y : Module.End k V,
        tangentOfLift rho L₂ =
          tangentOfLift rho L₁ + gaugeTangent rho Y := by
  rw [GaugeEquivalent]
  constructor
  · rintro ⟨Y, hY⟩
    refine ⟨Y, ?_⟩
    calc
      tangentOfLift rho L₂ =
          (tangentOfLift rho L₂ - tangentOfLift rho L₁) +
            tangentOfLift rho L₁ := by abel
      _ = gaugeTangent rho Y + tangentOfLift rho L₁ := by rw [← hY]
      _ = tangentOfLift rho L₁ + gaugeTangent rho Y := add_comm _ _
  · rintro ⟨Y, hY⟩
    refine ⟨Y, ?_⟩
    calc
      gaugeTangent rho Y =
          (tangentOfLift rho L₁ + gaugeTangent rho Y) -
            tangentOfLift rho L₁ := by abel
      _ = tangentOfLift rho L₂ - tangentOfLift rho L₁ := by rw [← hY]

/-- Gauge equivalence is reflexive. -/
theorem gaugeEquivalent_refl
    (rho : Representation k G V) (L : FirstOrderLift rho) :
    GaugeEquivalent rho L L := by
  rw [← h1ClassOfLift_eq_iff_gaugeEquivalent]

/-- Gauge equivalence is symmetric. -/
theorem gaugeEquivalent_symm
    (rho : Representation k G V) {L₁ L₂ : FirstOrderLift rho}
    (h : GaugeEquivalent rho L₁ L₂) :
    GaugeEquivalent rho L₂ L₁ := by
  rw [← h1ClassOfLift_eq_iff_gaugeEquivalent] at h ⊢
  exact h.symm

/-- Gauge equivalence is transitive. -/
theorem gaugeEquivalent_trans
    (rho : Representation k G V) {L₁ L₂ L₃ : FirstOrderLift rho}
    (h₁₂ : GaugeEquivalent rho L₁ L₂)
    (h₂₃ : GaugeEquivalent rho L₂ L₃) :
    GaugeEquivalent rho L₁ L₃ := by
  rw [← h1ClassOfLift_eq_iff_gaugeEquivalent] at h₁₂ h₂₃ ⊢
  exact h₁₂.trans h₂₃

/-- Every adjoint `H¹` class is represented by an actual square-zero
representation lift. -/
theorem h1ClassOfLift_surjective (rho : Representation k G V) :
    Function.Surjective (h1ClassOfLift rho) := by
  intro c
  rcases tangentToH1_surjective rho c with ⟨delta, hdelta⟩
  refine ⟨liftOfTangent rho delta, ?_⟩
  change tangentToH1 rho (tangentOfLift rho (liftOfTangent rho delta)) = c
  have ht : tangentOfLift rho (liftOfTangent rho delta) = delta :=
    (tangentEquivFirstOrderLift rho).left_inv delta
  rw [ht]
  exact hdelta

/-- First-order strict-equivalence classes of actual representation lifts are
classified exactly by adjoint `H¹`: the class map is surjective and its fibres
are the gauge-equivalence classes. -/
theorem firstOrderLift_classification
    (rho : Representation k G V) :
    Function.Surjective (h1ClassOfLift rho) ∧
      ∀ L₁ L₂ : FirstOrderLift rho,
        h1ClassOfLift rho L₁ = h1ClassOfLift rho L₂ ↔
          GaugeEquivalent rho L₁ L₂ :=
  ⟨h1ClassOfLift_surjective rho,
    h1ClassOfLift_eq_iff_gaugeEquivalent rho⟩

end

end Komorebi.StrongArtin.FirstOrderLiftGaugeClassification

#print axioms Komorebi.StrongArtin.FirstOrderLiftGaugeClassification.h1ClassOfLift_eq_iff_gaugeEquivalent
#print axioms Komorebi.StrongArtin.FirstOrderLiftGaugeClassification.firstOrderLift_classification
