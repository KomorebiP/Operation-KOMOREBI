import PaperX.NormResidueMellinAttachment
import PaperX.RealAxisMellinPole

/-! Pole-rigidity assembly for the actual ideal norm-character Mellin factors.

The arithmetic Euler-product identity and the two nonzero residue limits remain
explicit hypotheses.  The endpoint regularity of every norm-character factor is
proved from the scalar-unit counting criteria. -/

set_option autoImplicit false
noncomputable section

open Ideal NumberField Filter Asymptotics
open scoped nonZeroDivisors Classical Topology BigOperators

namespace PaperX.NormResidueLattice

variable (K : Type*) [Field K] [NumberField K]

/-- Once the arithmetic product identity and its nonzero simple-pole residues
are supplied, the checked norm-character power savings force the exponent to be
one and every endpoint Mellin value to be nonzero. -/
theorem normCharacter_pole_criterion_of_scalar_units
    {ι : Type*} [Fintype ι]
    (C : ι → ClassGroup (𝓞 K))
    (J : ι → (Ideal (𝓞 K))⁰)
    (m : ι → ℕ)
    (χ : ∀ i, ZMod (m i) →*₀ ℂ)
    (hJ : ∀ i, ClassGroup.mk0 (J i) = (C i)⁻¹)
    (hm : ∀ i, m i ≠ 0)
    (hχ : ∀ i, (χ i).toMonoidHom.comp (Units.coeHom (ZMod (m i))) ≠ 1)
    (hdeg : ∀ i, (Module.finrank ℚ K).Coprime (m i).totient)
    (hJcop : ∀ i, (absNorm ((J i : (Ideal (𝓞 K))⁰) : Ideal (𝓞 K))).Coprime (m i))
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
    (normCharacterMellin_sub_isBigO_of_scalar_units K
      (hJ i) (m i) (hm i) (χ i) (hχ i) (hdeg i) (hJcop i))

end PaperX.NormResidueLattice
