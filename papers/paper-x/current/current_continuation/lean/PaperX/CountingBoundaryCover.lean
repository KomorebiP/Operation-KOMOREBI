import PaperX.CountingBoundaryPolar

set_option autoImplicit false
noncomputable section

namespace PaperX.CountingBoundaryPolar

open NumberField NumberField.InfinitePlace NumberField.mixedEmbedding
open NumberField.mixedEmbedding.fundamentalCone
open NumberField.Units.dirichletUnitTheorem
open PaperX.RayCountingGeometry
open scoped Classical

variable (K : Type*) [Field K] [NumberField K]

def signs (x : mixedSpace K) : Signs K := fun w => decide (x.1 w < 0)

def parameters (t : ℝ) (z : realSpace K) (x : mixedSpace K) : Parameters K :=
  Sum.elim (fun w => if w = w₀ then t else z w)
    (fun w => (Complex.arg (x.2 w) + Real.pi) / (2 * Real.pi))

theorem parameters_radius (t : ℝ) (z : realSpace K) (x : mixedSpace K) :
    radius K (parameters K t z x) = t := by simp [radius, parameters]

theorem parameters_shape (t : ℝ) {z : realSpace K} (hz : z ∈ shapeBox K)
    (x : mixedSpace K) : shape K (parameters K t z x) = z := by
  ext w
  have hb := (Set.mem_univ_pi.mp hz) w
  by_cases hw : w = w₀
  · subst w
    simpa [shape, parameters] using (show z w₀ = 0 from by simpa [shapeBox] using hb).symm
  · simp [shape, parameters, hw]

theorem parameters_angle (t : ℝ) (z : realSpace K) (x : mixedSpace K)
    (w : ComplexPlace K) : angle K (parameters K t z x) w = Complex.arg (x.2 w) := by
  dsimp [angle, parameters]
  have hp : 2 * Real.pi ≠ 0 := mul_ne_zero (by norm_num) Real.pi_ne_zero
  field_simp
  ring

theorem parameters_mem_cube {t : ℝ} (ht : t ∈ Set.Icc (0 : ℝ) 1)
    {z : realSpace K} (hz : z ∈ shapeBox K) (x : mixedSpace K) :
    parameters K t z x ∈ Set.Icc (0 : Parameters K) 1 := by
  constructor
  · intro i
    rcases i with w | w
    · dsimp [parameters]
      split_ifs with hw
      · exact ht.1
      · have hb := (Set.mem_univ_pi.mp hz) w
        exact (show z w ∈ Set.Icc (0 : ℝ) 1 from by simpa [shapeBox, hw] using hb).1
    · dsimp [parameters]
      exact div_nonneg (by linarith [Complex.neg_pi_lt_arg (x.2 w)]) (by positivity)
  · intro i
    rcases i with w | w
    · dsimp [parameters]
      split_ifs with hw
      · exact ht.2
      · have hb := (Set.mem_univ_pi.mp hz) w
        exact (show z w ∈ Set.Icc (0 : ℝ) 1 from by simpa [shapeBox, hw] using hb).2
    · dsimp [parameters]
      apply (div_le_one (by positivity : (0 : ℝ) < 2 * Real.pi)).mpr
      linarith [Complex.arg_le_pi (x.2 w)]

theorem parameters_reconstruct {t : ℝ} {z : realSpace K}
    (hz : z ∈ shapeBox K) (x : mixedSpace K)
    (hm : radialChart K (t, z) = normAtAllPlaces x) :
    polarChart K (signs K x) (parameters K t z x) = x := by
  have hm' : moduli K (parameters K t z x) = normAtAllPlaces x := by
    rw [moduli, parameters_radius, parameters_shape K t hz]
    exact hm
  apply Prod.ext
  · funext w
    simp only [polarChart, hm', normAtAllPlaces_apply,
      normAtPlace_apply_of_isReal w.prop, signs]
    by_cases hw : x.1 w < 0
    · simp [hw, Real.norm_eq_abs, abs_of_neg hw]
    · simp [hw, Real.norm_eq_abs, abs_of_nonneg (le_of_not_gt hw)]
  · funext w
    simp only [polarChart, hm', parameters_angle, normAtAllPlaces_apply,
      normAtPlace_apply_of_isComplex w.prop]
    exact Complex.norm_mul_exp_arg_mul_I (x.2 w)

/-- Every actual boundary point is a signed polar chart of a cube face. -/
theorem frontier_cube_faces {x : mixedSpace K} (hx : x ∈ frontier (normLeOne K)) :
    ∃ s : Signs K, ∃ u : Parameters K,
      u ∈ Set.Icc (0 : Parameters K) 1 ∧
      (∃ w : InfinitePlace K, u (Sum.inl w) = 0 ∨ u (Sum.inl w) = 1) ∧
      polarChart K s u = x := by
  rcases frontier_radial_faces K hx with hzero | ⟨t, z, ht, hz, hf, hm⟩
  · subst x
    refine ⟨fun _ => false, 0, ⟨le_rfl, ?_⟩, ⟨w₀, Or.inl rfl⟩, ?_⟩
    · intro i; norm_num
    · exact polarChart_radius_zero K _ rfl
  · refine ⟨signs K x, parameters K t z x, parameters_mem_cube K ⟨ht.1.le, ht.2⟩ hz x,
      ?_, parameters_reconstruct K hz x hm⟩
    rcases hf with htop | ⟨w, hw, hface⟩
    · exact ⟨w₀, Or.inr (by simp [parameters, htop])⟩
    · exact ⟨w, by simpa [parameters, hw] using hface⟩

end PaperX.CountingBoundaryPolar
