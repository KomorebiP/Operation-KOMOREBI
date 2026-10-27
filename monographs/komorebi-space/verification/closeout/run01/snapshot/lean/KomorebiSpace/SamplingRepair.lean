import KomorebiSpace.ResidualSampling
import KomorebiSpace.ResidualNaturality

set_option autoImplicit false

/-!
# Quantitative comparison of the two sampling / repair routes

This instantiates the cochain comparison with the actual Banach tower
resampling maps. Sections of the fine and coarse differential are explicit
inputs. Their existence is not claimed for arbitrary contractive towers.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace BanachTower
open SplitDefect
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable (X Y : BanachTower.{u,v} 𝕜)
variable (hX : ∀ n, ‖X.down n‖ ≤ 1) (hY : ∀ n, ‖Y.down n‖ ≤ 1)
variable (φ : ℕ → ℕ) (hφ : Monotone φ)
variable (M : ℕ) (hgap : ∀ n, φ (n+1) - φ n ≤ M)

def samplingDefectMap : DefectMap (differential X Y)
    (differential (resample X hX φ hφ) (resample Y hY φ hφ)) where
  candidate := sampleCLM X Y hX hY φ hφ
  residual := residualSampleCLM X Y hX hY φ hφ M hgap
  commutes := resampling_chain X Y hX hY φ hφ M hgap

variable (A : Section (differential X Y))
variable (B : Section (differential (resample X hX φ hφ) (resample Y hY φ hφ)))

/-- This is exactly the mismatch of the previously constructed sampling maps. -/
def samplingMismatch := (samplingDefectMap X Y hX hY φ hφ M hgap).mismatch A B

theorem samplingMismatch_exact (r : Residuals X Y) :
    differential (resample X hX φ hφ) (resample Y hY φ hφ)
      (samplingMismatch X Y hX hY φ hφ M hgap A B r) = 0 :=
  (samplingDefectMap X Y hX hY φ hφ M hgap).mismatch_exact A B r

theorem sampling_repair_formula (f : Candidates X Y) :
    B.project (sampleCLM X Y hX hY φ hφ f) -
      sampleCLM X Y hX hY φ hφ (A.project f) =
    samplingMismatch X Y hX hY φ hφ M hgap A B (differential X Y f) :=
  (samplingDefectMap X Y hX hY φ hφ M hgap).repair_change A B f

/-- The mismatch vanishes on exact inputs, irrespective of the chosen sections. -/
theorem sampling_repairs_agree_on_exact (f : Candidates X Y) (hf : Exact X Y f) :
    B.project (sampleCLM X Y hX hY φ hφ f) =
      sampleCLM X Y hX hY φ hφ (A.project f) := by
  rw [A.project_fixes _ ((exact_iff_differential_zero X Y f).mp hf)]
  exact B.project_fixes _ ((exact_iff_differential_zero _ _ _).mp
    (sample_exact X Y hX hY φ hφ f hf))

theorem samplingMismatch_opNorm :
    ‖samplingMismatch X Y hX hY φ hφ M hgap A B‖ ≤ ‖A.lift‖ + (M : ℝ)*‖B.lift‖ := by
  apply ((samplingDefectMap X Y hX hY φ hφ M hgap).mismatch_opNorm A B).trans
  change ‖sampleCLM X Y hX hY φ hφ‖ * ‖A.lift‖ +
    ‖B.lift‖ * ‖residualSampleCLM X Y hX hY φ hφ M hgap‖ ≤ _
  calc
    _ ≤ 1 * ‖A.lift‖ + ‖B.lift‖ * (M : ℝ) := add_le_add
      (mul_le_mul_of_nonneg_right (sampleCLM_opNorm X Y hX hY φ hφ) (norm_nonneg _))
      (mul_le_mul_of_nonneg_left (residualSampleCLM_opNorm X Y hX hY φ hφ M hgap)
        (norm_nonneg _))
    _ = _ := by ring

include hgap in
theorem sampling_repair_bound (f : Candidates X Y) :
    ‖B.project (sampleCLM X Y hX hY φ hφ f) -
      sampleCLM X Y hX hY φ hφ (A.project f)‖ ≤
        (‖A.lift‖ + (M : ℝ)*‖B.lift‖) * ‖differential X Y f‖ := by
  rw [sampling_repair_formula X Y hX hY φ hφ M hgap]
  exact ((samplingMismatch X Y hX hY φ hφ M hgap A B).le_opNorm _).trans
    (mul_le_mul_of_nonneg_right (samplingMismatch_opNorm X Y hX hY φ hφ M hgap A B)
      (norm_nonneg _))

include hgap in
/-- The discrepancy tends to zero, though equality at each finite stage is not automatic. -/
theorem sampling_repair_discrepancy_tendsto_zero (f : ℕ → Candidates X Y)
    (hf : Filter.Tendsto (fun k => differential X Y (f k)) Filter.atTop (nhds 0)) :
    Filter.Tendsto (fun k => B.project (sampleCLM X Y hX hY φ hφ (f k)) -
      sampleCLM X Y hX hY φ hφ (A.project (f k))) Filter.atTop (nhds 0) :=
  (samplingDefectMap X Y hX hY φ hφ M hgap).repair_discrepancy_tendsto_zero A B f hf

/-- Exact naturality holds precisely when the sections intertwine the two sampling maps. -/
theorem sampling_repair_natural_iff :
    (∀ f, B.project (sampleCLM X Y hX hY φ hφ f) =
      sampleCLM X Y hX hY φ hφ (A.project f)) ↔
      (sampleCLM X Y hX hY φ hφ).comp A.lift =
        B.lift.comp (residualSampleCLM X Y hX hY φ hφ M hgap) :=
  (samplingDefectMap X Y hX hY φ hφ M hgap).repair_natural_iff A B

end BanachTower
end KomorebiSpace
end
