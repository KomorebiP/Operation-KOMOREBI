module
public import KomorebiPhysics.HarmonicSurrogates
public import KomorebiPhysics.L2DominatedLimits
public import Mathlib.Analysis.Complex.RealDeriv
public import Mathlib.Analysis.SpecialFunctions.ExpDeriv
public import Mathlib.Analysis.SpecialFunctions.Trigonometric.Bounds

/-! Strong time continuity and maximal-domain invariance of the constructed
spectral phase group. No boundedness of the real spectrum is assumed. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace SpectralEvolution
open Filter BoundedSpectral HarmonicSurrogates
open scoped Topology BigOperators lp

variable (eig : ℕ → ℝ)

def evolution (t : ℝ) : Space →L[ℂ] Space := diagonal (phaseSymbol eig t)

theorem evolution_apply (t : ℝ) (x : Space) (n : ℕ) :
    evolution eig t x n = phaseSymbol eig t n * x n := rfl

/-- An actual scalar derivative of each phase coefficient. This is NOT yet
the Hilbert-space derivative. -/
theorem phase_hasDerivAt (t : ℝ) (n : ℕ) :
    HasDerivAt (fun s : ℝ => phaseSymbol eig s n)
      ((-Complex.I) * (eig n : ℂ) * phaseSymbol eig t n) t := by
  have h := (((hasDerivAt_id t).neg.mul_const (eig n)).ofReal_comp.mul_const Complex.I).cexp
  simpa [phaseSymbol_apply, mul_assoc, mul_comm, mul_left_comm] using h

theorem coordinate_hasDerivAt (x : Space) (t : ℝ) (n : ℕ) :
    HasDerivAt (fun s => evolution eig s x n)
      ((-Complex.I) * (eig n : ℂ) * (evolution eig t x n)) t := by
  simpa only [evolution_apply, mul_assoc] using (phase_hasDerivAt eig t n).mul_const (x n)

theorem coordinate_norm (t : ℝ) (x : Space) (n : ℕ) :
    ‖evolution eig t x n‖ = ‖x n‖ := by
  rw [evolution_apply, norm_mul, phaseSymbol_norm, one_mul]

/-- All l2 states have norm-continuous orbits, even outside the generator domain. -/
theorem continuous_orbit (x : Space) : Continuous (fun t => evolution eig t x) := by
  apply continuous_iff_continuousAt.mpr
  intro t
  apply L2DominatedLimits.tendsto_of_vector_bound ((2 : ℂ) • x)
  · intro n
    exact (coordinate_hasDerivAt eig x t n).continuousAt
  · apply Filter.Eventually.of_forall
    intro s n
    calc
      ‖evolution eig s x n - evolution eig t x n‖ ≤
          ‖evolution eig s x n‖ + ‖evolution eig t x n‖ := norm_sub_le _ _
      _ = ‖((2 : ℂ) • x) n‖ := by
        simp only [coordinate_norm, lp.coeFn_smul, Pi.smul_apply, norm_smul]
        norm_num
        ring

theorem norm_preserved (t : ℝ) (x : Space) : ‖evolution eig t x‖ = ‖x‖ :=
  phase_preserves_norm eig t x

theorem norm_difference (t : ℝ) (x y : Space) :
    ‖evolution eig t x - evolution eig t y‖ = ‖x-y‖ := by
  rw [← map_sub, norm_preserved]

/-- The actual orbit remains in the maximal weighted l2 domain. -/
theorem domain_preserved (t : ℝ) (x : (DiagonalDomain.operator eig).domain) :
    evolution eig t (x : Space) ∈ DiagonalDomain.domain eig := by
  change Memℓp (fun n => (eig n : ℂ) * evolution eig t (x : Space) n) 2
  convert lp.memℓp (evolution eig t (DiagonalDomain.operator eig x)) using 1
  funext n
  simp only [evolution_apply, DiagonalDomain.operator_apply]
  ring

/-- Domain-valued evolution, with membership supplied by the preceding proof. -/
def domainEvolution (t : ℝ) (x : (DiagonalDomain.operator eig).domain) :
    (DiagonalDomain.operator eig).domain := ⟨evolution eig t x, domain_preserved eig t x⟩

theorem domainEvolution_coe (t : ℝ) (x : (DiagonalDomain.operator eig).domain) :
    (domainEvolution eig t x : Space) = evolution eig t x := rfl

/-- The generator and evolution commute on the true maximal domain. -/
theorem operator_commutes (t : ℝ) (x : (DiagonalDomain.operator eig).domain) :
    DiagonalDomain.operator eig (domainEvolution eig t x) =
      evolution eig t (DiagonalDomain.operator eig x) := by
  apply lp.ext
  funext n
  simp only [DiagonalDomain.operator_apply, domainEvolution_coe, evolution_apply]
  ring

theorem evolution_zero (x : Space) : evolution eig 0 x = x := by
  exact congrArg (fun A : Space →L[ℂ] Space => A x) (phase_zero eig)

theorem evolution_add (s t : ℝ) (x : Space) :
    evolution eig (s+t) x = evolution eig s (evolution eig t x) := by
  exact congrArg (fun A : Space →L[ℂ] Space => A x) (phase_add eig s t)

theorem evolution_inverse (t : ℝ) (x : Space) :
    evolution eig (-t) (evolution eig t x) = x := by
  rw [← evolution_add, neg_add_cancel, evolution_zero]

theorem domain_iff (t : ℝ) (x : Space) :
    evolution eig t x ∈ DiagonalDomain.domain eig ↔ x ∈ DiagonalDomain.domain eig := by
  constructor
  · intro hx
    simpa only [evolution_inverse] using domain_preserved eig (-t) ⟨_, hx⟩
  · intro hx
    exact domain_preserved eig t ⟨x, hx⟩

theorem domainEvolution_zero (x : (DiagonalDomain.operator eig).domain) :
    domainEvolution eig 0 x = x := by
  apply Subtype.ext
  exact evolution_zero eig x

theorem domainEvolution_add (s t : ℝ) (x : (DiagonalDomain.operator eig).domain) :
    domainEvolution eig (s+t) x = domainEvolution eig s (domainEvolution eig t x) := by
  apply Subtype.ext
  exact evolution_add eig s t x

theorem graphNorm_preserved (t : ℝ) (x : (DiagonalDomain.operator eig).domain) :
    GraphDomain.graphNorm (DiagonalDomain.operator eig) (domainEvolution eig t x) =
      GraphDomain.graphNorm (DiagonalDomain.operator eig) x := by
  have he := GraphDomain.graphNorm_sq (DiagonalDomain.operator eig) (domainEvolution eig t x)
  rw [operator_commutes, domainEvolution_coe, norm_preserved, norm_preserved,
    ← GraphDomain.graphNorm_sq] at he
  exact (sq_eq_sq₀ (GraphDomain.graphNorm_nonneg _ _) (GraphDomain.graphNorm_nonneg _ _)).mp he

/-- Strong time continuity also holds in the actual graph norm on D(H). -/
theorem graph_continuity (x : (DiagonalDomain.operator eig).domain) (t : ℝ) :
    Tendsto (fun s => GraphDomain.graphNorm (DiagonalDomain.operator eig)
      (domainEvolution eig s x - domainEvolution eig t x)) (𝓝 t) (𝓝 0) := by
  apply (GraphDomain.graph_convergence_iff _ _ _).mpr
  constructor
  · exact (continuous_orbit eig (x : Space)).continuousAt
  · simpa only [operator_commutes] using
      (continuous_orbit eig (DiagonalDomain.operator eig x)).tendsto t

/-- A uniform coordinate increment bound, essential for a dominated slope proof. -/
theorem phase_increment_bound (s t : ℝ) (n : ℕ) :
    ‖phaseSymbol eig s n - phaseSymbol eig t n‖ ≤ |s-t| * |eig n| := by
  have he : phaseSymbol eig s n - phaseSymbol eig t n =
      phaseSymbol eig t n * (Complex.exp (Complex.I * ((-(s-t)*eig n : ℝ) : ℂ)) - 1) := by
    simp only [phaseSymbol_apply, mul_sub, mul_one, ← Complex.exp_add]
    congr 2
    push_cast
    ring
  rw [he, norm_mul, phaseSymbol_norm, one_mul]
  simpa only [Real.norm_eq_abs, abs_mul, abs_neg] using
    (Real.norm_exp_I_mul_ofReal_sub_one_le (x := -(s-t)*eig n))

theorem coordinate_increment_bound (s t : ℝ) (x : Space) (n : ℕ) :
    ‖evolution eig s x n - evolution eig t x n‖ ≤ |s-t| * (|eig n| * ‖x n‖) := by
  simp only [evolution_apply, ← sub_mul, norm_mul]
  have h := mul_le_mul_of_nonneg_right (phase_increment_bound eig s t n) (norm_nonneg (x n))
  simpa only [mul_assoc] using h

end SpectralEvolution
end KomorebiPhysics
