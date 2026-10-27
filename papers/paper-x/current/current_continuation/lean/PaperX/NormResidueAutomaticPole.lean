import PaperX.NormResidueAutomaticCounting
import PaperX.RealAxisMellinPole

/-!
# Automatic-representative pole-rigidity assembly

The ideal-class representative is constructed internally for each character.
Thus the pole-rigidity theorem exposes only the scalar-unit arithmetic
criterion, degree--totient coprimality, and the genuinely external arithmetic
Euler-product data.
-/

set_option autoImplicit false
noncomputable section

open Ideal NumberField Filter Asymptotics
open scoped NumberField nonZeroDivisors Classical Topology BigOperators

namespace PaperX.NormResidueLattice

variable (K : Type*) [Field K] [NumberField K]

/-- Pole rigidity with automatic coprime inverse-class representatives. -/
theorem normCharacter_pole_criterion_of_scalar_units_autoRep
    {ι : Type*} [Fintype ι]
    (C : ι → ClassGroup (𝓞 K))
    (m : ι → ℕ)
    (χ : ∀ i, ZMod (m i) →*₀ ℂ)
    (hm : ∀ i, m i ≠ 0)
    (hχ : ∀ i, (χ i).toMonoidHom.comp (Units.coeHom (ZMod (m i))) ≠ 1)
    (hdeg : ∀ i, (Module.finrank ℚ K).Coprime (m i).totient)
    (p Z : ℝ → ℂ) (P Q : ℂ) (d : ℕ)
    (hp : Tendsto (fun h : ℝ => (h : ℂ) * p h) (𝓝[>] 0) (𝓝 P))
    (hP : P ≠ 0)
    (hZ : Tendsto (fun h : ℝ => (h : ℂ) * Z h) (𝓝[>] 0) (𝓝 Q))
    (hQ : Q ≠ 0)
    (hid : Z =ᶠ[𝓝[>] 0] fun h =>
      (p h * ∏ i, normCharacterMellin K (C i) (m i) (χ i) h) ^ d) :
    d = 1 ∧ ∀ i, normCharacterMellin K (C i) (m i) (χ i) 0 ≠ 0 := by
  apply PaperX.RealAxisPoleRigidity.right_endpoint_index_one_and_factors_nonzero
    p Z (fun i => normCharacterMellin K (C i) (m i) (χ i)) P Q d
    hp hP hZ hQ _ hid
  intro i
  exact PaperX.RealAxisMellinPole.isBigO_complex_scale_iff.mpr
    (normCharacterMellin_sub_isBigO_of_scalar_units_autoRep K
      (C i) (m i) (hm i) (χ i) (hχ i) (hdeg i))

end PaperX.NormResidueLattice
