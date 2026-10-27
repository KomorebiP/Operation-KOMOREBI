import Mathlib.NumberTheory.NumberField.CanonicalEmbedding.NormLeOne
import Mathlib.Analysis.Calculus.ContDiff.RCLike

/-!
Concrete geometry of the existing ordinary unit cone. This module locates its frontier in
parameter faces and gives a Lipschitz physical radial parametrization on the normalized box.
It does not yet construct the sign/angle boundary atlas in mixed space or count lattice points.
-/

set_option autoImplicit false
noncomputable section

namespace PaperX.RayCountingGeometry

open NumberField NumberField.InfinitePlace NumberField.mixedEmbedding
open NumberField.mixedEmbedding.fundamentalCone
open NumberField.Units.dirichletUnitTheorem
open scoped Pointwise

variable (K : Type*) [Field K] [NumberField K]

/-- Every nonzero boundary point comes from a boundary point of the logarithmic parameter set. -/
theorem frontier_moduli {x : mixedSpace K} (hx : x ∈ frontier (normLeOne K)) :
    x = 0 ∨ ∃ y : realSpace K,
      y ∈ frontier (paramSet K) ∧ expMapBasis y = normAtAllPlaces x := by
  have hc := closure_normLeOne_subset K hx.1
  change normAtAllPlaces x ∈ compactSet K at hc
  rw [compactSet_eq_union] at hc
  rcases hc with ⟨y, hy, heq⟩ | hz
  · right
    refine ⟨y, ⟨hy, ?_⟩, heq⟩
    intro hi
    exact hx.2 (subset_interior_normLeOne K ⟨y, hi, heq⟩)
  · left
    apply forall_normAtPlace_eq_zero_iff.mp
    intro w
    exact congrFun (Set.mem_singleton_iff.mp hz) w

/-- The parameter frontier consists only of the radial top or faces of the unit box. -/
theorem frontier_parameter_faces {y : realSpace K} (hy : y ∈ frontier (paramSet K)) :
    y w₀ = 0 ∨ ∃ w : InfinitePlace K, w ≠ w₀ ∧ (y w = 0 ∨ y w = 1) := by
  classical
  have hb : ∀ w, y w ∈ (if w = w₀ then Set.Iic 0 else Set.Icc 0 1) := by
    simpa only [closure_paramSet, Set.mem_univ_pi] using hy.1
  by_contra hn
  push Not at hn
  apply hy.2
  rw [interior_paramSet, Set.mem_univ_pi]
  intro w
  by_cases hw : w = w₀
  · subst w
    simp only [ite_true, Set.mem_Iio]
    exact lt_of_le_of_ne (by simpa using hb w₀) hn.1
  · simp only [hw, ite_false, Set.mem_Ioo]
    have hbw : 0 ≤ y w ∧ y w ≤ 1 := by simpa [hw] using hb w
    exact ⟨lt_of_le_of_ne hbw.1 (Ne.symm (hn.2 w hw).1),
      lt_of_le_of_ne hbw.2 (hn.2 w hw).2⟩

open scoped Classical in
/-- The normalized shape box from the actual fundamental-cone coordinates. -/
def shapeBox : Set (realSpace K) :=
  Set.univ.pi fun w => if w = w₀ then {0} else Set.Icc 0 1

theorem shapeBox_compact : IsCompact (shapeBox K) := by
  classical
  apply isCompact_univ_pi
  intro w
  split_ifs
  · exact isCompact_singleton
  · exact isCompact_Icc

theorem shapeBox_convex : Convex ℝ (shapeBox K) := by
  classical
  apply convex_pi
  intro w _
  split_ifs
  · exact convex_singleton 0
  · exact convex_Icc 0 1

/-- Radial compactification uses a physical scalar, with no logarithm at the origin. -/
def radialChart (p : ℝ × realSpace K) : realSpace K := p.1 • expMapBasis p.2

theorem expMapBasis_contDiff : ContDiff ℝ 1 (expMapBasis : realSpace K → realSpace K) := by
  apply contDiff_pi.mpr
  intro w
  simp only [expMapBasis_apply, expMap_apply]
  exact (contDiff_const.mul
    ((contDiff_apply ℝ ℝ w).comp (completeBasis K).equivFunL.symm.contDiff)).exp

theorem radialChart_contDiff : ContDiff ℝ 1 (radialChart K) :=
  contDiff_fst.smul ((expMapBasis_contDiff K).comp contDiff_snd)

theorem radialChart_lipschitz : ∃ C : NNReal,
    LipschitzOnWith C (radialChart K) (Set.Icc (0 : ℝ) 1 ×ˢ shapeBox K) := by
  apply (radialChart_contDiff K).contDiffOn.exists_lipschitzOnWith (by decide)
  · exact (convex_Icc 0 1).prod (shapeBox_convex K)
  · exact isCompact_Icc.prod (shapeBox_compact K)

theorem radialChart_image :
    radialChart K '' (Set.Icc 0 1 ×ˢ shapeBox K) = compactSet K := by
  ext y
  simp only [Set.mem_image, Set.mem_prod, radialChart, compactSet, shapeBox,
    Set.mem_smul, exists_exists_and_eq_and]
  constructor
  · rintro ⟨⟨t, z⟩, ⟨ht, hz⟩, rfl⟩
    exact ⟨t, ht, z, hz, rfl⟩
  · rintro ⟨t, ht, z, hz, rfl⟩
    exact ⟨(t, z), ⟨ht, hz⟩, rfl⟩

/-- Nonzero boundary moduli lie on the radial top or a face of the compact unit box. -/
theorem frontier_radial_faces {x : mixedSpace K} (hx : x ∈ frontier (normLeOne K)) :
    x = 0 ∨ ∃ t : ℝ, ∃ z : realSpace K,
      t ∈ Set.Ioc 0 1 ∧ z ∈ shapeBox K ∧
      (t = 1 ∨ ∃ w : InfinitePlace K, w ≠ w₀ ∧ (z w = 0 ∨ z w = 1)) ∧
      radialChart K (t, z) = normAtAllPlaces x := by
  classical
  rcases frontier_moduli K hx with hzero | ⟨y, hy, heq⟩
  · exact Or.inl hzero
  have hb : ∀ w, y w ∈ (if w = w₀ then Set.Iic 0 else Set.Icc 0 1) := by
    simpa only [closure_paramSet, Set.mem_univ_pi] using hy.1
  right
  refine ⟨Real.exp (y w₀), fun w => if w = w₀ then 0 else y w, ?_, ?_, ?_, ?_⟩
  · exact ⟨Real.exp_pos _, Real.exp_le_one_iff.mpr (by simpa using hb w₀)⟩
  · rw [shapeBox, Set.mem_univ_pi]
    intro w
    by_cases hw : w = w₀
    · simp [hw]
    · simpa [hw] using hb w
  · rcases frontier_parameter_faces K hy with hr | ⟨w, hw, hwf⟩
    · exact Or.inl (by simp [hr])
    · exact Or.inr ⟨w, hw, by simpa [hw] using hwf⟩
  · exact (expMapBasis_apply'' y).symm.trans heq

end PaperX.RayCountingGeometry
