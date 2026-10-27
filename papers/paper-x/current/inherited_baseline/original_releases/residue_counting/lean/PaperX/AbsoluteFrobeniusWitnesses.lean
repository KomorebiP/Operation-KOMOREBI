import PaperX.AbsoluteIntegralFrobenius
import Mathlib.RepresentationTheory.Character

/-! Actual absolute arithmetic Frobenius witnesses indexed by rational primes.
The prime ideal, stabilizer membership and residue action are stored together.
These records do not assert that their global elements are unramified in Qbar. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.AbsoluteFrobeniusWitnesses
open PaperX.AbsoluteIntegralFrobenius
open scoped Pointwise

abbrev RationalPrime := {p : ℕ // p.Prime}

/-- Arithmetic p-power Frobenius at an actual prime of the algebraic integers. -/
structure Witness (p : ℕ) where
  primeIdeal : Ideal IntegralClosure
  isMaximal : primeIdeal.IsMaximal
  liesOver : primeIdeal.LiesOver (Ideal.span {(p : ℤ)})
  element : GQ
  stabilizes : element ∈ MulAction.stabilizer GQ primeIdeal
  residue : ∀ x : IntegralClosure, Ideal.Quotient.mk primeIdeal (element • x) =
    (Ideal.Quotient.mk primeIdeal x) ^ p

/-- Existence is derived from the actual integral-closure construction. -/
theorem witness_nonempty (p : ℕ) [Fact p.Prime] : Nonempty (Witness p) := by
  obtain ⟨Q, hQ, hQp, σ, hσ⟩ := exists_frobenius p
  exact ⟨⟨Q, hQ, hQp, σ.val, σ.property, hσ⟩⟩

/-- A fixed prime-indexed choice of actual arithmetic witnesses. -/
def chosenWitness (p : RationalPrime) : Witness p.val := by
  let : Fact p.val.Prime := ⟨p.property⟩
  exact Classical.choice (witness_nonempty p.val)

section Conjugation
variable {R G : Type*} [CommRing R] [Group G] [MulSemiringAction G R]

/-- Conjugating an arithmetic residue action conjugates its prime ideal. -/
theorem residue_conjugate (Q : Ideal R) (p : ℕ) (γ a : G)
    (hγ : ∀ x : R, Ideal.Quotient.mk Q (γ • x) = (Ideal.Quotient.mk Q x) ^ p) :
    ∀ x : R, Ideal.Quotient.mk (a • Q) ((a * γ * a⁻¹) • x) =
      (Ideal.Quotient.mk (a • Q) x) ^ p := by
  intro x
  rw [← map_pow, Ideal.Quotient.eq]
  rw [Ideal.mem_pointwise_smul_iff_inv_smul_mem, smul_sub, smul_pow']
  have h' := hγ (a⁻¹ • x)
  rw [← map_pow] at h'
  have h := Ideal.Quotient.eq.mp h'
  simpa only [mul_smul, inv_smul_smul] using h

/-- Equal residue actions at a fixed actual prime differ by its inertia. -/
theorem same_residue_div_mem_inertia (Q : Ideal R) (γ δ : G)
    (hγ : γ ∈ MulAction.stabilizer G Q)
    (h : ∀ x : R, Ideal.Quotient.mk Q (δ • x) = Ideal.Quotient.mk Q (γ • x)) :
    γ⁻¹ * δ ∈ Q.inertia G := by
  intro x
  change (γ⁻¹ * δ) • x - x ∈ Q
  have hm : δ • x - γ • x ∈ Q := Ideal.Quotient.eq.mp (h x)
  have hs : γ⁻¹ • Q = Q := (MulAction.stabilizer G Q).inv_mem hγ
  have hh := Ideal.smul_mem_pointwise_smul γ⁻¹ _ Q hm
  simpa only [hs, smul_sub, inv_smul_smul, mul_smul] using hh

end Conjugation
end PaperX.AbsoluteFrobeniusWitnesses
