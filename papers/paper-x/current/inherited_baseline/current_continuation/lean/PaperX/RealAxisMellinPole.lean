import PaperX.RealAxisMellinMoment
import PaperX.RealAxisPoleRigidity

/-! Assembly of the real-axis integral and pole arguments. The required
arithmetic product identity and summatory-function bounds remain hypotheses. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.RealAxisMellinPole
open Filter Asymptotics MeasureTheory Set
open scoped Topology

/-- The real and complex casts of the real endpoint parameter have the same norm. -/
theorem isBigO_complex_scale_iff {f : ℝ → ℂ} {l : Filter ℝ} :
    f =O[l] (fun h : ℝ => (h : ℂ)) ↔ f =O[l] (fun h : ℝ => h) := by
  simp only [Asymptotics.isBigO_iff, Complex.norm_real]

/-- Power-saving bounds on the supplied summatory functions suffice for the
pole-product conclusion without complex analytic continuation. -/
theorem index_one_and_mellin_values_nonzero {ι : Type*} [Fintype ι]
    (S : ι → ℝ → ℂ) (C r : ι → ℝ) (p Z : ℝ → ℂ) (P Q : ℂ) (d : ℕ)
    (hS : ∀ i, AEStronglyMeasurable (S i) (volume.restrict (Ioi 1)))
    (hr : ∀ i, r i < 1)
    (hbound : ∀ i x, 1 < x → ‖S i x‖ ≤ C i * x ^ r i)
    (hp : Tendsto (fun h : ℝ => (h : ℂ) * p h) (𝓝[>] 0) (𝓝 P)) (hP : P ≠ 0)
    (hZ : Tendsto (fun h : ℝ => (h : ℂ) * Z h) (𝓝[>] 0) (𝓝 Q)) (hQ : Q ≠ 0)
    (hid : Z =ᶠ[𝓝[>] 0] fun h =>
      (p h * ∏ i, RealAxisMellinMoment.mellinIntegral (S i) h) ^ d) :
    d = 1 ∧ ∀ i, RealAxisMellinMoment.mellinIntegral (S i) 0 ≠ 0 := by
  apply RealAxisPoleRigidity.right_endpoint_index_one_and_factors_nonzero
    p Z (fun i => RealAxisMellinMoment.mellinIntegral (S i)) P Q d hp hP hZ hQ _ hid
  intro i
  exact isBigO_complex_scale_iff.mpr
    (RealAxisMellinMoment.mellinIntegral_sub_isBigO_of_power_bound (hS i) (hr i) (hbound i))

end PaperX.RealAxisMellinPole
