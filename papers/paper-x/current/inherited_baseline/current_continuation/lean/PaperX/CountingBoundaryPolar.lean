import PaperX.RayCountingGeometry
import Mathlib.Analysis.SpecialFunctions.Complex.Arg

set_option autoImplicit false
noncomputable section

namespace PaperX.CountingBoundaryPolar

open NumberField NumberField.InfinitePlace NumberField.mixedEmbedding
open NumberField.mixedEmbedding.fundamentalCone
open NumberField.Units.dirichletUnitTheorem
open PaperX.RayCountingGeometry
open scoped Classical

variable (K : Type*) [Field K] [NumberField K]

abbrev RealPlace := {w : InfinitePlace K // IsReal w}
abbrev ComplexPlace := {w : InfinitePlace K // IsComplex w}
abbrev Coordinate := InfinitePlace K ⊕ ComplexPlace K
abbrev Parameters := Coordinate K → ℝ
abbrev Signs := RealPlace K → Bool

theorem coordinate_card : Fintype.card (Coordinate K) = Module.finrank ℚ K := by
  rw [Fintype.card_sum, card_eq_nrRealPlaces_add_nrComplexPlaces]
  change nrRealPlaces K + nrComplexPlaces K + nrComplexPlaces K = _
  have h := card_add_two_mul_card_eq_rank K
  omega

open scoped Classical in
def shape (u : Parameters K) : realSpace K :=
  fun w => if w = w₀ then 0 else u (Sum.inl w)

def radius (u : Parameters K) : ℝ := u (Sum.inl w₀)
def angle (u : Parameters K) (w : ComplexPlace K) : ℝ :=
  -Real.pi + (2 * Real.pi) * u (Sum.inr w)

def moduli (u : Parameters K) : realSpace K :=
  radius K u • expMapBasis (shape K u)

def polarChart (s : Signs K) (u : Parameters K) : mixedSpace K :=
  (fun w => (if s w then -1 else 1) * moduli K u w.1,
   fun w => (moduli K u w.1 : ℂ) * Complex.exp ((angle K u w : ℂ) * Complex.I))

theorem shape_contDiff : ContDiff ℝ 1 (shape K) := by
  classical
  apply contDiff_pi.mpr
  intro w
  dsimp [shape]
  split_ifs
  · exact contDiff_const
  · exact contDiff_apply ℝ ℝ _

theorem moduli_contDiff : ContDiff ℝ 1 (moduli K) := by
  exact (contDiff_apply ℝ ℝ (Sum.inl w₀)).smul
    ((expMapBasis_contDiff K).comp (shape_contDiff K))

theorem polarChart_contDiff (s : Signs K) : ContDiff ℝ 1 (polarChart K s) := by
  apply ContDiff.prodMk
  · apply contDiff_pi.mpr
    intro w
    exact contDiff_const.mul ((contDiff_apply ℝ ℝ w.1).comp (moduli_contDiff K))
  · apply contDiff_pi.mpr
    intro w
    apply ContDiff.mul
    · exact Complex.ofRealCLM.contDiff.comp
        ((contDiff_apply ℝ ℝ w.1).comp (moduli_contDiff K))
    · apply ContDiff.cexp
      exact (Complex.ofRealCLM.contDiff.comp
        (contDiff_const.add (contDiff_const.mul (contDiff_apply ℝ ℝ (Sum.inr w))))).mul contDiff_const

theorem polarChart_lipschitz (s : Signs K) : ∃ C : NNReal,
    LipschitzOnWith C (polarChart K s) (Set.Icc (0 : Parameters K) 1) := by
  apply (polarChart_contDiff K s).contDiffOn.exists_lipschitzOnWith (by decide)
  · exact convex_Icc _ _
  · exact isCompact_Icc

/-- The physical radial coordinate includes the origin smoothly. -/
theorem polarChart_radius_zero (s : Signs K) {u : Parameters K}
    (hu : radius K u = 0) : polarChart K s u = 0 := by
  ext w <;> simp [polarChart, moduli, hu]

end PaperX.CountingBoundaryPolar
