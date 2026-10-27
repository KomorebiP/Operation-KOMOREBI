import PaperX.IdealCharacterMellin
import PaperX.RealAxisMellinPole

/-! The pole criterion now uses actual ordinary class-character ideal sums.
Their growth and endpoint regularity are theorems. Residues and the arithmetic
product identity remain explicit inputs; this is not an Euler-product proof. -/

set_option autoImplicit false
noncomputable section

open NumberField Filter Asymptotics
open scoped Topology BigOperators

namespace PaperX.IdealClassCharacter

variable (K : Type*) [Field K] [NumberField K]

/-- For actual ordinary class characters, only the pole residues and product
identity remain to apply the real-axis nonvanishing and index-one argument. -/
theorem classCharacter_pole_criterion {ι : Type*} [Fintype ι]
    (χ : ι → ClassGroup (𝓞 K) →* ℂ) (hχ : ∀ i, χ i ≠ 1)
    (p Z : ℝ → ℂ) (P Q : ℂ) (d : ℕ)
    (hp : Tendsto (fun h : ℝ => (h : ℂ) * p h) (𝓝[>] 0) (𝓝 P)) (hP : P ≠ 0)
    (hZ : Tendsto (fun h : ℝ => (h : ℂ) * Z h) (𝓝[>] 0) (𝓝 Q)) (hQ : Q ≠ 0)
    (hid : Z =ᶠ[𝓝[>] 0] fun h => (p h * ∏ i, classMellin K (χ i) h) ^ d) :
    d = 1 ∧ ∀ i, classMellin K (χ i) 0 ≠ 0 := by
  apply PaperX.RealAxisPoleRigidity.right_endpoint_index_one_and_factors_nonzero
    p Z (fun i => classMellin K (χ i)) P Q d hp hP hZ hQ _ hid
  intro i
  exact PaperX.RealAxisMellinPole.isBigO_complex_scale_iff.mpr
    (characterMellin_sub_isBigO K (χ i) (hχ i))

end PaperX.IdealClassCharacter
