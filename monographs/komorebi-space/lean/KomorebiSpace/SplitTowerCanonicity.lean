import KomorebiSpace.SplitDefectCharts
import KomorebiSpace.SplitTowerCoordinates

set_option autoImplicit false

/-!
# Canonicity for the actual split-tower differential

Two valid target splittings yield different possible repairs but the same
exact core, residual space, and subspace of seed-plus-kernel profiles.
The intrinsic exact-core charts change by bounded triangular shears.
-/
universe u v
noncomputable section
open scoped NNReal ENNReal
namespace KomorebiSpace
namespace BanachTower
namespace Splitting
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable (X : BanachTower.{u,v} 𝕜) {Y : BanachTower.{u,v} 𝕜}
variable (L M N : Splitting Y)

/-- The seed-plus-innovation profile space has a splitting-independent description. -/
theorem semanticSpace_characterization (f : Candidates X Y) :
    f ∈ L.semanticSpace X ↔ ∀ n, (Y.down n).comp (f (n+1)) = 0 := by
  rw [L.mem_semanticSpace X]
  constructor
  · intro hf n
    have hn := congrArg (fun a : Candidates X Y => a (n+1)) hf
    change L.innovation X f n = f (n+1) at hn
    rw [← hn]
    exact L.innovation_down X f n
  · intro hf
    apply lp.ext
    funext n
    cases n with
    | zero => rfl
    | succ n =>
      change f (n+1) - (L.up n).comp ((Y.down n).comp (f (n+1))) = f (n+1)
      rw [hf n]
      simp

/-- Profile values depend on the splitting, but their possible-value subspace does not. -/
theorem semanticSpace_eq : L.semanticSpace X = M.semanticSpace X := by
  ext f
  rw [L.semanticSpace_characterization X, M.semanticSpace_characterization X]

@[simp] theorem observable_cross (f : Candidates X Y) :
    L.observable X (M.observable X f) = M.observable X f := by
  apply (L.mem_semanticSpace X _).mp
  rw [L.semanticSpace_eq X M]
  exact (M.mem_semanticSpace X _).mpr (M.observable_idempotent X f)

variable (hL : (L.bound : ℝ) * X.bound < 1)
variable (hM : (M.bound : ℝ) * X.bound < 1)
variable (hN : (N.bound : ℝ) * X.bound < 1)

/-- The previously constructed correction is a section of the actual differential. -/
def defectSection : SplitDefect.Section (differential X Y) where
  lift := L.correction X hL
  right_inv := L.differential_correction X hL

@[simp] theorem defectSection_project (f : Candidates X Y) :
    (L.defectSection X hL).project f = L.repair X hL f := rfl

/-- The first factor here is the intrinsic exact core, independent of L. -/
def coreCoordinates : Candidates X Y ≃L[𝕜]
    (SplitDefect.Core (differential X Y) × Residuals X Y) :=
  (L.defectSection X hL).chart

@[simp] theorem coreCoordinates_exact (f : Candidates X Y) :
    (L.coreCoordinates X hL f).1.val = L.repair X hL f := rfl

@[simp] theorem coreCoordinates_residual (f : Candidates X Y) :
    (L.coreCoordinates X hL f).2 = differential X Y f := rfl

/-- A change of splitting does not change the residual coordinate. -/
def coreTransition : (SplitDefect.Core (differential X Y) × Residuals X Y) ≃L[𝕜]
    (SplitDefect.Core (differential X Y) × Residuals X Y) :=
  (L.defectSection X hL).transition (M.defectSection X hM)

theorem coreTransition_formula (z : SplitDefect.Core (differential X Y) × Residuals X Y) :
    L.coreTransition X M hL hM z =
      (z.1 + (L.defectSection X hL).difference (M.defectSection X hM) z.2, z.2) :=
  (L.defectSection X hL).transition_formula (M.defectSection X hM) z

theorem coreTransition_cocycle (z : SplitDefect.Core (differential X Y) × Residuals X Y) :
    M.coreTransition X N hM hN (L.coreTransition X M hL hM z) =
      L.coreTransition X N hL hN z :=
  (L.defectSection X hL).transition_cocycle (M.defectSection X hM)
    (N.defectSection X hN) z

/-- Difference of two corrections is an exact transport family. -/
theorem correction_difference_exact (r : Residuals X Y) :
    Exact X Y (L.correction X hL r - M.correction X hM r) := by
  apply (exact_iff_differential_zero X Y _).mpr
  simp

theorem repair_change (f : Candidates X Y) :
    M.repair X hM f - L.repair X hL f =
      (L.correction X hL - M.correction X hM) (differential X Y f) := by
  simp only [repair_apply, sub_apply]
  abel

theorem repair_change_norm (f : Candidates X Y) :
    ‖M.repair X hM f - L.repair X hL f‖ ≤
      ‖L.correction X hL - M.correction X hM‖ * ‖differential X Y f‖ := by
  rw [L.repair_change X M hL hM f]
  exact (L.correction X hL - M.correction X hM).le_opNorm _

theorem repair_change_gain_bound (f : Candidates X Y) :
    ‖M.repair X hM f - L.repair X hL f‖ ≤
      (L.gain X + M.gain X) * ‖differential X Y f‖ := by
  apply (L.repair_change_norm X M hL hM f).trans
  apply mul_le_mul_of_nonneg_right _ (norm_nonneg _)
  exact (norm_sub_le _ _).trans
    (add_le_add (L.correction_opNorm X hL) (M.correction_opNorm X hM))

@[simp] theorem repair_cross (f : Candidates X Y) :
    L.repair X hL (M.repair X hM f) = M.repair X hM f :=
  L.repair_fixes_exact X hL _ (M.repair_exact X hM f)

theorem repairs_commute_iff :
    (L.repair X hL).comp (M.repair X hM) =
      (M.repair X hM).comp (L.repair X hL) ↔
    L.repair X hL = M.repair X hM :=
  (L.defectSection X hL).projects_commute_iff (M.defectSection X hM)

/-- Two charts coincide on exact inputs even when their repairs differ elsewhere. -/
theorem repairs_agree_on_exact (f : Candidates X Y) (hf : Exact X Y f) :
    L.repair X hL f = M.repair X hM f := by
  rw [L.repair_fixes_exact X hL f hf, M.repair_fixes_exact X hM f hf]

end Splitting
end BanachTower
end KomorebiSpace
end
