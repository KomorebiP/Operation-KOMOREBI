import MatrixInverseCertificate
import NCPowerLocalImage
import Mathlib.Algebra.Group.Commute.Units

namespace Komorebi.StrongArtin.MatrixHensel
noncomputable section
open scoped Matrix.Norms.Elementwise
attribute [local instance] padicMatrixNormedRing padicMatrixUltra padicMatrixComplete

variable {p : ℕ} [Fact p.Prime]
variable {ι : Type*} [Fintype ι] [DecidableEq ι] [Nonempty ι]

theorem precision_contracts (s m : ℕ) (hsm : s < m) :
    (p : ℝ)^s * (p : ℝ)^(-(m : ℤ)) < 1 := by
  have hp : (1 : ℝ) < p := by exact_mod_cast (Fact.out : p.Prime).one_lt
  rw [← zpow_natCast, ← zpow_add₀ (ne_of_gt (lt_trans zero_lt_one hp)), ← zpow_zero (p : ℝ)]
  apply (zpow_lt_zpow_iff_right₀ hp).mpr
  omega

theorem matrix_power_exists_iff (A U : Matrix ι ι (PadicInt p)) (d s m : ℕ)
    (hsm : s < m) (B : Matrix (ι × ι) (ι × ι) (PadicInt p))
    (hc : InverseCertificate (integralMatrix A) d s B) :
    (∃ F : Matrix ι ι (PadicInt p), F^d = U ∧
      (PadicInt.toZModPow m).mapMatrix F = (PadicInt.toZModPow m).mapMatrix A) ↔
    (PadicInt.toZModPow (m+s)).mapMatrix (integralAction B (U - A^d)) = 0 := by
  have hp : (1 : ℝ) < p := by exact_mod_cast (Fact.out : p.Prime).one_lt
  have hρ : 0 ≤ (p : ℝ)^(-(m : ℤ)) := (zpow_pos (lt_trans zero_lt_one hp) _).le
  have hρ1 : (p : ℝ)^(-(m : ℤ)) ≤ 1 := by
    rw [← zpow_zero (p : ℝ)]
    apply (zpow_le_zpow_iff_right₀ hp).mpr
    omega
  have hdelta : integralMatrix (U-A^d) = integralMatrix U - (integralMatrix A)^d := by
    change PadicInt.Coe.ringHom.mapMatrix (U-A^d) = _
    rw [map_sub, map_pow]
    rfl
  rw [← inverse_norm_iff_congruence B s m, hdelta]
  have hlocal := power_ball_exists_iff (integralMatrix A) (integralMatrix U) d
    (integralMatrix_norm_le A) (inverseLinear B s).toAddMonoidHom
    (inverseCertificate_left _ d s B hc) (inverseCertificate_right _ d s B hc)
    ((p : ℝ)^s) ((p : ℝ)^(-(m : ℤ))) (by positivity) hρ hρ1
    (precision_contracts s m hsm) (inverseLinear_norm B s)
  constructor
  · rintro ⟨F, hF, hFA⟩
    apply hlocal.mp
    refine ⟨integralMatrix F, ?_, (matrix_reduction_iff_norm m F A).mp hFA⟩
    rw [← integralMatrix_pow, hF]
  · intro h
    obtain ⟨X, hX, hXA⟩ := hlocal.mpr h
    have hnorm : ‖X‖ ≤ 1 := by
      have he : X = (X-integralMatrix A) + integralMatrix A := by abel
      rw [he]
      exact norm_add_bound (hXA.trans hρ1) (integralMatrix_norm_le A)
    let F : Matrix ι ι (PadicInt p) := fun i j =>
      ⟨X i j, (Matrix.norm_entry_le_entrywise_sup_norm X).trans hnorm⟩
    have hF : integralMatrix F = X := rfl
    refine ⟨F, ?_, ?_⟩
    · apply integralMatrix_injective
      rw [integralMatrix_pow, hF, hX]
    · apply (matrix_reduction_iff_norm m F A).mpr
      rw [hF]
      exact hXA

theorem matrix_power_unique_iff (A U : Matrix ι ι (PadicInt p)) (d s m : ℕ)
    (hsm : s < m) (B : Matrix (ι × ι) (ι × ι) (PadicInt p))
    (hc : InverseCertificate (integralMatrix A) d s B) :
    (∃! F : Matrix ι ι (PadicInt p), F^d = U ∧
      (PadicInt.toZModPow m).mapMatrix F = (PadicInt.toZModPow m).mapMatrix A) ↔
    (PadicInt.toZModPow (m+s)).mapMatrix (integralAction B (U - A^d)) = 0 := by
  constructor
  · intro h
    exact (matrix_power_exists_iff A U d s m hsm B hc).mp h.exists
  · intro h
    obtain ⟨F, hF, hFA⟩ := (matrix_power_exists_iff A U d s m hsm B hc).mpr h
    have hp : (1 : ℝ) < p := by exact_mod_cast (Fact.out : p.Prime).one_lt
    have hρ : 0 ≤ (p : ℝ)^(-(m : ℤ)) := (zpow_pos (lt_trans zero_lt_one hp) _).le
    have hρ1 : (p : ℝ)^(-(m : ℤ)) ≤ 1 := by
      rw [← zpow_zero (p : ℝ)]
      apply (zpow_le_zpow_iff_right₀ hp).mpr
      omega
    have hnorm := (inverse_norm_iff_congruence B s m (U-A^d)).mpr h
    have hdelta : integralMatrix (U-A^d) = integralMatrix U - (integralMatrix A)^d := by
      change PadicInt.Coe.ringHom.mapMatrix (U-A^d) = _
      rw [map_sub, map_pow]
      rfl
    rw [hdelta] at hnorm
    obtain ⟨X, _, huniq⟩ := (power_ball_image (integralMatrix A) (integralMatrix U) d
      (integralMatrix_norm_le A) (inverseLinear B s).toAddMonoidHom
      (inverseCertificate_left _ d s B hc) (inverseCertificate_right _ d s B hc)
      ((p : ℝ)^s) ((p : ℝ)^(-(m : ℤ))) (by positivity) hρ hρ1
      (precision_contracts s m hsm) (inverseLinear_norm B s)).mpr hnorm
    have hFeq : integralMatrix F = X := huniq _
      ⟨by rw [← integralMatrix_pow, hF], (matrix_reduction_iff_norm m F A).mp hFA⟩
    refine ⟨F, ⟨hF, hFA⟩, ?_⟩
    intro G hG
    apply integralMatrix_injective
    exact (huniq _ ⟨by rw [← integralMatrix_pow, hG.1],
      (matrix_reduction_iff_norm m G A).mp hG.2⟩).trans hFeq.symm

/-- The root is an actual matrix-ring unit when the target is a unit. -/
theorem matrix_unit_root_iff (A U : (Matrix ι ι (PadicInt p))ˣ) (d s m : ℕ)
    (hd : d ≠ 0) (hsm : s < m) (B : Matrix (ι × ι) (ι × ι) (PadicInt p))
    (hc : InverseCertificate (integralMatrix A.val) d s B) :
    (∃! F : (Matrix ι ι (PadicInt p))ˣ, F^d = U ∧
      (PadicInt.toZModPow m).mapMatrix F.val = (PadicInt.toZModPow m).mapMatrix A.val) ↔
    (PadicInt.toZModPow (m+s)).mapMatrix (integralAction B (U.val - A.val^d)) = 0 := by
  constructor
  · rintro ⟨F, hF, _⟩
    apply (matrix_power_exists_iff A.val U.val d s m hsm B hc).mp
    refine ⟨F.val, ?_, hF.2⟩
    simpa using congrArg Units.val hF.1
  · intro h
    obtain ⟨X, hX, hu⟩ := (matrix_power_unique_iff A.val U.val d s m hsm B hc).mpr h
    have hXu : IsUnit X := (isUnit_pow_iff hd).mp (hX.1.symm ▸ U.isUnit)
    obtain ⟨F, hF⟩ := hXu
    refine ⟨F, ⟨?_, ?_⟩, ?_⟩
    · apply Units.ext
      simpa [hF] using hX.1
    · simpa [hF] using hX.2
    · intro G hG
      apply Units.ext
      rw [hF]
      apply hu
      exact ⟨by simpa using congrArg Units.val hG.1, hG.2⟩

end
end Komorebi.StrongArtin.MatrixHensel
