import Mathlib.RepresentationTheory.Invariants
import Mathlib.Analysis.InnerProductSpace.Basic

/-! Literal finite group averages and their invariant and orthogonal projection properties. -/
set_option autoImplicit false
noncomputable section
open scoped BigOperators
namespace PaperXI.FiniteAverage
variable {G V : Type*} [Group G] [Fintype G] [AddCommGroup V] [Module ℂ V]

def average (ρ : Representation ℂ G V) : V →ₗ[ℂ] V :=
  (Fintype.card G : ℂ)⁻¹ • ∑ g : G, ρ g

@[simp] theorem average_apply (ρ : Representation ℂ G V) (v : V) :
    average ρ v = (Fintype.card G : ℂ)⁻¹ • ∑ g : G, ρ g v := by
  simp [average, LinearMap.sum_apply]

theorem card_ne_zero : (Fintype.card G : ℂ) ≠ 0 := by
  exact_mod_cast Fintype.card_ne_zero

theorem invariant (ρ : Representation ℂ G V) (v : V) :
    average ρ v ∈ ρ.invariants := by
  intro g
  simp only [average_apply, map_smul, map_sum, ← Module.End.mul_apply, ← map_mul]
  rw [Function.Bijective.sum_comp (Group.mulLeft_bijective g) (fun h => ρ h v)]

theorem fixes (ρ : Representation ℂ G V) {v : V} (hv : v ∈ ρ.invariants) :
    average ρ v = v := by
  rw [average_apply]
  have hf (g : G) : ρ g v = v := hv g
  simp only [hf, Finset.sum_const, Finset.card_univ]
  rw [← Nat.cast_smul_eq_nsmul ℂ, smul_smul, inv_mul_cancel₀ (card_ne_zero (G := G)), one_smul]

theorem idempotent (ρ : Representation ℂ G V) :
    (average ρ).comp (average ρ) = average ρ := by
  ext v
  exact fixes ρ (invariant ρ v)

theorem range_eq (ρ : Representation ℂ G V) :
    LinearMap.range (average ρ) = ρ.invariants := by
  ext v
  constructor
  · rintro ⟨w, rfl⟩
    exact invariant ρ w
  · intro hv
    exact ⟨v, fixes ρ hv⟩

section Inner
variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℂ E]

theorem self_adjoint (ρ : Representation ℂ G E)
    (hunitary : ∀ g x y, inner ℂ (ρ g x) (ρ g y) = inner ℂ x y) (x y : E) :
    inner ℂ (average ρ x) y = inner ℂ x (average ρ y) := by
  have hmove (g : G) : inner ℂ (ρ g x) y = inner ℂ x (ρ g⁻¹ y) := by
    simpa only [ρ.self_inv_apply] using hunitary g x (ρ g⁻¹ y)
  simp only [average_apply, inner_smul_left, inner_smul_right, sum_inner, inner_sum]
  simp only [map_inv₀, map_natCast]
  congr 1
  simp_rw [hmove]
  exact Function.Bijective.sum_comp (Equiv.inv G).bijective (fun g => inner ℂ x (ρ g y))

theorem residual_orthogonal (ρ : Representation ℂ G E)
    (hunitary : ∀ g x y, inner ℂ (ρ g x) (ρ g y) = inner ℂ x y)
    (x : E) {y : E} (hy : y ∈ ρ.invariants) :
    inner ℂ (x - average ρ x) y = 0 := by
  rw [inner_sub_left, self_adjoint ρ hunitary, fixes ρ hy, sub_self]

end Inner
end PaperXI.FiniteAverage
