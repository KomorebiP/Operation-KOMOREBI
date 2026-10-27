import PaperXI.TranslationAverage

/-! Orthogonal averaging for the actual finite-sum Hermitian pairing on functions. -/
set_option autoImplicit false
noncomputable section
open scoped BigOperators
namespace PaperXI.FiniteFunctionAverage
open TranslationAverage
variable {G X : Type*} [Group G] [Fintype G] [Fintype X]

theorem pairing_average_left (ρ : Representation ℂ G (X → ℂ)) (f h : X → ℂ) :
    pairing (FiniteAverage.average ρ f) h =
      (Fintype.card G : ℂ)⁻¹ * ∑ g : G, pairing (ρ g f) h := by
  simp only [pairing, FiniteAverage.average_apply, Pi.smul_apply, Finset.sum_apply,
    smul_eq_mul, star_mul, star_inv₀, star_natCast, star_sum,
    Finset.mul_sum, Finset.sum_mul]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro g hg
  apply Finset.sum_congr rfl
  intro u hu
  ring

theorem pairing_average_right (ρ : Representation ℂ G (X → ℂ)) (f h : X → ℂ) :
    pairing f (FiniteAverage.average ρ h) =
      (Fintype.card G : ℂ)⁻¹ * ∑ g : G, pairing f (ρ g h) := by
  simp only [pairing, FiniteAverage.average_apply, Pi.smul_apply, Finset.sum_apply,
    smul_eq_mul, Finset.mul_sum]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro g hg
  apply Finset.sum_congr rfl
  intro u hu
  ring

theorem self_adjoint (ρ : Representation ℂ G (X → ℂ))
    (hunitary : ∀ g f h, pairing (ρ g f) (ρ g h) = pairing f h) (f h : X → ℂ) :
    pairing (FiniteAverage.average ρ f) h = pairing f (FiniteAverage.average ρ h) := by
  have hmove (g : G) : pairing (ρ g f) h = pairing f (ρ g⁻¹ h) := by
    simpa only [ρ.self_inv_apply] using hunitary g f (ρ g⁻¹ h)
  rw [pairing_average_left, pairing_average_right]
  congr 1
  simp_rw [hmove]
  exact Function.Bijective.sum_comp (Equiv.inv G).bijective (fun g => pairing f (ρ g h))

theorem residual_orthogonal (ρ : Representation ℂ G (X → ℂ))
    (hunitary : ∀ g f h, pairing (ρ g f) (ρ g h) = pairing f h)
    (f : X → ℂ) {h : X → ℂ} (hh : h ∈ ρ.invariants) :
    pairing (f - FiniteAverage.average ρ f) h = 0 := by
  have hsub (a b c : X → ℂ) : pairing (a-b) c = pairing a c - pairing b c := by
    simp [pairing, star_sub, sub_mul, Finset.sum_sub_distrib]
  rw [hsub, self_adjoint ρ hunitary, FiniteAverage.fixes ρ hh, sub_self]

end PaperXI.FiniteFunctionAverage
