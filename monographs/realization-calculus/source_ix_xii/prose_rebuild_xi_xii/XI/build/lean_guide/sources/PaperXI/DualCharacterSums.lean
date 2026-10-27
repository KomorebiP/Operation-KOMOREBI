import PaperXI.SchrodingerTrace
import PaperXI.SchrodingerSeparation
import PaperXI.HeisenbergDimension

/-! Literal finite character orthogonality on a vector space and its full dual. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.DualCharacters
open scoped Classical

variable {K X : Type*} [Field K] [AddCommGroup X] [Module K X]

/-- Orthogonality over points, including the trivial functional. -/
theorem sum_over_points [Fintype X] {ψ : AddChar K ℂ} (hψ : ψ ≠ 1)
    (ξ : Module.Dual K X) :
    (∑ a : X, ψ (ξ a)) = if ξ = 0 then (Fintype.card X : ℂ) else 0 := by
  by_cases hξ : ξ = 0
  · simp [hξ]
  · simp [hξ, SchrodingerTrace.sum_functional_character hψ hξ]

/-- Evaluation at a point as an additive character of the full dual. -/
def evaluationCharacter (ψ : AddChar K ℂ) (a : X) : AddChar (Module.Dual K X) ℂ :=
  ψ.compAddMonoidHom
    { toFun := fun ξ => ξ a
      map_zero' := by simp
      map_add' := by intros; simp }

@[simp] theorem evaluationCharacter_apply (ψ : AddChar K ℂ) (a : X)
    (ξ : Module.Dual K X) : evaluationCharacter ψ a ξ = ψ (ξ a) := rfl

theorem evaluationCharacter_ne_one {ψ : AddChar K ℂ} (hψ : ψ ≠ 1)
    {a : X} (ha : a ≠ 0) : evaluationCharacter ψ a ≠ 1 := by
  obtain ⟨ξ, hξ⟩ := SchrodingerSeparation.exists_dual_character_ne hψ ha
  intro h
  apply hξ
  have hh := congrArg (fun χ : AddChar (Module.Dual K X) ℂ => χ ξ) h
  simpa using hh

/-- Orthogonality over the actual full linear dual. -/
theorem sum_over_dual [Fintype (Module.Dual K X)] {ψ : AddChar K ℂ}
    (hψ : ψ ≠ 1) (a : X) :
    (∑ ξ : Module.Dual K X, ψ (ξ a)) =
      if a = 0 then (Fintype.card (Module.Dual K X) : ℂ) else 0 := by
  by_cases ha : a = 0
  · simp [ha]
  · simpa [ha] using
      AddChar.sum_eq_zero_of_ne_one (evaluationCharacter_ne_one hψ ha)

/-- Cardinalities agree without any assumption on the complex target space. -/
theorem card_dual [FiniteDimensional K X] [Fintype X]
    [Fintype (Module.Dual K X)] : Fintype.card (Module.Dual K X) = Fintype.card X := by
  simpa only [Nat.card_eq_fintype_card] using
    HeisenbergDimension.natCard_dual (K := K) (X := X)

end PaperXI.DualCharacters
