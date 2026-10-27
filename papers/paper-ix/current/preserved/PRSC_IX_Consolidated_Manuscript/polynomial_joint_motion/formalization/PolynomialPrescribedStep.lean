module
public import PolynomialPrescribedCounts
public import PolynomialSurjectiveStep

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialPrescribedStep
open Komorebi.NativeAffine Komorebi.PolynomialObstruction
open Komorebi.PolynomialDigitBridge Komorebi.PolynomialPrescribedSystem
open Komorebi.PolynomialPrescribedLifts
open Komorebi.PolynomialParameterSystem (freePart join)
variable {m k e : ℕ}

/-- Congruent integer points have the same actual solved-coordinate Jacobian. -/
theorem solvedJacobian_eq (q : ℕ) (F : Fin e → MvPolynomial (Fin (m + k)) ℤ)
    (x y : Fin (m + k) → ℤ) (hxy : ∀ i, (q : ℤ) ∣ y i - x i) :
    solvedJacobian q F y = solvedJacobian q F x := by
  have h := PolynomialSurjectiveStep.digitJacobian_eq q F x y hxy
  apply LinearMap.ext
  intro u
  have hu := congrArg (fun A : (Fin (m + k) → ZMod q) →ₗ[ZMod q] (Fin e → ZMod q) =>
    A (join u 0)) h
  simpa only [digitJacobian_join, map_zero, add_zero] using hu

/-- A positive-depth correction preserves the actual solved block. -/
theorem solvedJacobian_shift_eq (q L : ℕ) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x s : Fin (m + k) → ℤ) :
    solvedJacobian q F (x + (q : ℤ)^L • s) = solvedJacobian q F x := by
  apply solvedJacobian_eq
  intro i
  change (q : ℤ) ∣ x i + (q : ℤ)^L * s i - x i
  rw [add_sub_cancel_left]
  exact dvd_mul_of_dvd_left (dvd_pow_self (q : ℤ) (by omega : L ≠ 0)) _

/-- Solved-block surjectivity removes every prescribed one-step obstruction. -/
theorem obstruction_zero (q : ℕ)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (hJ : Function.Surjective (solvedJacobian q F x))
    (r : Fin e → ℤ) (v : Fin k → ZMod q) :
    PolynomialPrescribedSystem.obstruction q F x r v = 0 := by
  apply (prescribed_digits_nonempty_iff q F x r v).mp
  obtain ⟨u, hu⟩ := hJ (-(parameterResidual q F x r v))
  exact ⟨⟨u, by change parameterResidual q F x r v + solvedJacobian q F x u = 0
                rw [hu, add_neg_cancel]⟩⟩

/-- Every compatible integer parameter target is attained exactly by an actual
next root. Its integer correction retains the supplied parameter quotient,
rather than replacing that quotient by a canonical residue representative. -/
theorem one_step_lift (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (hx : ∀ i, (q : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (solvedJacobian q F x))
    (t : Fin k → ℤ) (ht : ∀ j, (q : ℤ)^L ∣ t j - freePart x j) :
    ∃ y : Fin (m + k) → ℤ,
      (∀ i, (q : ℤ)^L ∣ (y - x) i) ∧
      (∀ i, (q : ℤ)^(L+1) ∣ evalSystem F y i) ∧
      freePart y = t ∧ solvedJacobian q F y = solvedJacobian q F x := by
  choose w hw using ht
  obtain ⟨r, hr⟩ := residual_exists q L F x hx
  obtain ⟨u, hu⟩ := hJ (-(parameterResidual q F x r (reduction q k w)))
  have hcorr : reduction q e r + digitJacobian q F x (join u (reduction q k w)) = 0 := by
    apply (prescribed_equation_iff q F x r (reduction q k w) u).mp
    rw [hu, add_neg_cancel]
  let s : Fin (m + k) → ℤ := join (integerLift q u) w
  have hs : reduction q (m + k) s = join u (reduction q k w) := by
    ext i
    refine Fin.addCases (fun j => ?_) (fun j => ?_) i
    · change ((join (integerLift q u) w (Fin.castAdd k j) : ℤ) : ZMod q) = _
      simpa only [PolynomialParameterSystem.join_solved, reduction, LinearMap.coe_mk,
        AddHom.coe_mk] using
        congrFun (reduction_integerLift q hq u) j
    · simp only [reduction, LinearMap.coe_mk, AddHom.coe_mk, s,
        PolynomialParameterSystem.join_free]
  refine ⟨x + (q : ℤ)^L • s,
    (same_residue_iff ((q : ℤ)^L) x _).mpr ⟨s, rfl⟩, ?_, ?_,
    solvedJacobian_shift_eq q L hL F x s⟩
  · apply (next_level_iff_digit q L hq hL F x r hr s).mpr
    rw [map_add, ← reduction_jacobian, hs]
    exact hcorr
  · ext j
    change x (Fin.natAdd m j) + (q : ℤ)^L * s (Fin.natAdd m j) = t j
    dsimp only [s]
    rw [PolynomialParameterSystem.join_free]
    have hj := hw j
    change t j - x (Fin.natAdd m j) = (q : ℤ)^L * w j at hj
    omega

/-- Surjectivity of the solved block forces its rank to be the equation count. -/
theorem solved_rank (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (hJ : Function.Surjective (solvedJacobian p F x)) :
    FiniteFiberCounts.rank p (solvedJacobian p F x) = e := by
  unfold FiniteFiberCounts.rank
  rw [LinearMap.range_eq_top.mpr hJ, finrank_top, Module.finrank_fin_fun]

/-- The exponent m-e is nonnegative as a consequence of solved-block surjectivity. -/
theorem solved_dimension (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (hJ : Function.Surjective (solvedJacobian p F x)) : e ≤ m := by
  simpa only [Module.finrank_fin_fun] using
    LinearMap.finrank_le_finrank_of_surjective hJ

/-- Every parameter digit has exactly p^(m-e) distinct actual next-level residue
lifts when the actual solved block is surjective. -/
theorem prescribed_lift_card (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (solvedJacobian p F x)) (v : Fin k → ZMod p) :
    Nat.card (PrescribedLifts p L F x v) = p ^ (m - e) := by
  obtain ⟨r, hr⟩ := residual_exists p L F x hx
  rw [PolynomialPrescribedCounts.lift_card p L hL F x r hr v,
    ite_eq_left (obstruction_zero p F x hJ r v), solved_rank p F x hJ]

end Komorebi.PolynomialPrescribedStep
