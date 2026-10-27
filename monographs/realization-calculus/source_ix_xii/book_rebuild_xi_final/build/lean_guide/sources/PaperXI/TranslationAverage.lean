import PaperXI.FiniteAverage
import Mathlib.LinearAlgebra.Dimension.Finrank
import Mathlib.LinearAlgebra.Pi

/-! The translation representation and its rank-one constant-function projector. -/
set_option autoImplicit false
set_option maxHeartbeats 600000
noncomputable section
open scoped BigOperators
namespace PaperXI.TranslationAverage
variable {X : Type*} [AddCommGroup X] [Fintype X]

def translation : Representation ℂ (Multiplicative X) (X → ℂ) where
  toFun x :=
    { toFun := fun f u => f (u + x.toAdd)
      map_add' := by intros; rfl
      map_smul' := by intros; rfl }
  map_one' := by ext f u; simp
  map_mul' x y := by ext f u; simp [add_assoc]

omit [Fintype X] in
@[simp] theorem translation_apply (x : Multiplicative X) (f : X → ℂ) (u : X) :
    translation x f u = f (u + x.toAdd) := rfl

def mean (f : X → ℂ) : ℂ := (Fintype.card X : ℂ)⁻¹ * ∑ u : X, f u

def constantSubmodule : Submodule ℂ (X → ℂ) :=
  LinearMap.range (LinearMap.const (R := ℂ) (ι := X) (M₂ := ℂ))

omit [AddCommGroup X] [Fintype X] in
theorem mem_constantSubmodule (f : X → ℂ) :
    f ∈ constantSubmodule ↔ ∃ c : ℂ, ∀ u, f u = c := by
  constructor
  · rintro ⟨c, hc⟩
    exact ⟨c, fun u => (congrFun hc u).symm⟩
  · rintro ⟨c, hc⟩
    exact ⟨c, funext fun u => (hc u).symm⟩

theorem average_apply (f : X → ℂ) (u : X) :
    FiniteAverage.average (translation (X := X)) f u = mean f := by
  simp only [FiniteAverage.average_apply, Pi.smul_apply, Finset.sum_apply,
    translation_apply, smul_eq_mul, mean]
  rw [Fintype.card_multiplicative]
  congr 1
  rw [Function.Bijective.sum_comp Multiplicative.toAdd.bijective (fun x : X => f (u + x))]
  exact Function.Bijective.sum_comp (AddGroup.addLeft_bijective u) f

theorem range_eq :
    LinearMap.range (FiniteAverage.average (translation (X := X))) = constantSubmodule := by
  ext f
  constructor
  · rintro ⟨g, rfl⟩
    exact (mem_constantSubmodule _).2 ⟨mean g, average_apply g⟩
  · intro hf
    rcases (mem_constantSubmodule f).1 hf with ⟨c, hc⟩
    refine ⟨f, FiniteAverage.fixes _ ?_⟩
    intro g
    ext u
    simp only [translation_apply, hc]

theorem finrank_range :
    Module.finrank ℂ (LinearMap.range (FiniteAverage.average (translation (X := X)))) = 1 := by
  rw [range_eq]
  have hinj : Function.Injective (LinearMap.const (R := ℂ) (ι := X) (M₂ := ℂ)) := by
    intro a b h
    exact congrFun h 0
  change Module.finrank ℂ (LinearMap.range (LinearMap.const (R := ℂ) (ι := X) (M₂ := ℂ))) = 1
  rw [LinearMap.finrank_range_of_inj hinj, Module.finrank_self]

/-- The standard finite-sum Hermitian pairing on the function model. -/
def pairing (f g : X → ℂ) : ℂ := ∑ u : X, star (f u) * g u

theorem pairing_translation (x : Multiplicative X) (f g : X → ℂ) :
    pairing (translation x f) (translation x g) = pairing f g := by
  simp only [pairing, translation_apply]
  exact Function.Bijective.sum_comp (AddGroup.addRight_bijective x.toAdd)
    (fun u => star (f u) * g u)

theorem pairing_self_adjoint (f g : X → ℂ) :
    pairing (FiniteAverage.average (translation (X := X)) f) g =
      pairing f (FiniteAverage.average (translation (X := X)) g) := by
  simp only [pairing, average_apply, mean, star_mul, star_inv₀, star_natCast,
    star_sum, Finset.mul_sum, Finset.sum_mul]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro u hu
  apply Finset.sum_congr rfl
  intro v hv
  ring

theorem residual_orthogonal (f : X → ℂ) {g : X → ℂ}
    (hg : g ∈ constantSubmodule) :
    pairing (f - FiniteAverage.average (translation (X := X)) f) g = 0 := by
  have hfix : FiniteAverage.average (translation (X := X)) g = g := by
    have hr : g ∈ LinearMap.range (FiniteAverage.average (translation (X := X))) := by rwa [range_eq]
    apply FiniteAverage.fixes
    rwa [FiniteAverage.range_eq] at hr
  have hsub (a b c : X → ℂ) : pairing (a-b) c = pairing a c - pairing b c := by
    simp [pairing, star_sub, sub_mul, Finset.sum_sub_distrib]
  rw [hsub, pairing_self_adjoint, hfix, sub_self]

end PaperXI.TranslationAverage
