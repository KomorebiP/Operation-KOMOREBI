import PaperX.IdealClassQuantitativeTheorem

/-!
# Actual ideal sums weighted by ordinary ideal classes

The sums range over nonzero integral ideals subject to their actual absolute norm.
Grouping by the ordinary ideal class is an exact finite identity at every real threshold.
-/
set_option autoImplicit false
noncomputable section

open Ideal NumberField
open scoped nonZeroDivisors Classical BigOperators

namespace PaperX.IdealClassCharacter

open PaperX.IdealClassQuantitative

variable (K : Type*) [Field K] [NumberField K]

/-- The actual set of bounded nonzero integral ideals is finite at every real threshold. -/
instance boundedIdeals_finite (X : ℝ) :
    Finite {I : (Ideal (𝓞 K))⁰ // (absNorm (I : Ideal (𝓞 K)) : ℝ) ≤ X} := by
  have : Finite {I : (Ideal (𝓞 K))⁰ // absNorm (I : Ideal (𝓞 K)) ≤ ⌊X⌋₊} :=
    finite_setOfPred_absNorm_le₀ ⌊X⌋₊
  exact Finite.of_injective
    (fun I => (⟨I.val, Nat.le_floor I.property⟩ :
      {I : (Ideal (𝓞 K))⁰ // absNorm (I : Ideal (𝓞 K)) ≤ ⌊X⌋₊}))
    (fun _ _ h => Subtype.ext (congrArg
      (fun I : {I : (Ideal (𝓞 K))⁰ // absNorm (I : Ideal (𝓞 K)) ≤ ⌊X⌋₊} => I.val) h))

/-- A finite sum over actual ideals, with the coefficient given by the ideal class. -/
def weightedSum (w : ClassGroup (𝓞 K) → ℂ) (X : ℝ) : ℂ :=
  letI := Fintype.ofFinite {I : (Ideal (𝓞 K))⁰ //
    (absNorm (I : Ideal (𝓞 K)) : ℝ) ≤ X}
  ∑ I : {I : (Ideal (𝓞 K))⁰ // (absNorm (I : Ideal (𝓞 K)) : ℝ) ≤ X},
    w (ClassGroup.mk0 I.val)

/-- Exact grouping of the ideal sum by ordinary ideal class. -/
theorem weightedSum_eq_sum_classCount (w : ClassGroup (𝓞 K) → ℂ) (X : ℝ) :
    weightedSum K w X = ∑ C, w C * (classCount K C X : ℂ) := by
  let := Fintype.ofFinite {I : (Ideal (𝓞 K))⁰ //
    (absNorm (I : Ideal (𝓞 K)) : ℝ) ≤ X}
  unfold weightedSum
  rw [← Fintype.sum_fiberwise (fun I : {I : (Ideal (𝓞 K))⁰ //
    (absNorm (I : Ideal (𝓞 K)) : ℝ) ≤ X} => ClassGroup.mk0 I.val)]
  apply Finset.sum_congr rfl
  intro C _
  have he := Equiv.subtypeSubtypeEquivSubtypeInter
    (fun I : (Ideal (𝓞 K))⁰ => (absNorm (I : Ideal (𝓞 K)) : ℝ) ≤ X)
    (fun I => ClassGroup.mk0 I = C)
  have hc : classCount K C X =
      Fintype.card {I : {I : (Ideal (𝓞 K))⁰ //
        (absNorm (I : Ideal (𝓞 K)) : ℝ) ≤ X} // ClassGroup.mk0 I.val = C} := by
    rw [classCount, ← Nat.card_congr he, Nat.card_eq_fintype_card]
  simp only [hc]
  simp_rw [show ∀ I : {I : {I : (Ideal (𝓞 K))⁰ //
    (absNorm (I : Ideal (𝓞 K)) : ℝ) ≤ X} // ClassGroup.mk0 I.val = C},
    w (ClassGroup.mk0 I.val.val) = w C from fun I => congrArg w I.property]
  simp [mul_comm]

/-- Every nontrivial complex character of a finite group has zero total sum. -/
theorem sum_character_eq_zero {G : Type*} [Group G] [Fintype G]
    (χ : G →* ℂ) (hχ : χ ≠ 1) : ∑ g, χ g = 0 := by
  obtain ⟨a, ha⟩ : ∃ a, χ a ≠ 1 := by
    by_contra h
    push Not at h
    exact hχ (MonoidHom.ext fun a => by simpa using h a)
  have hs : χ a * ∑ g, χ g = ∑ g, χ g := by
    rw [Finset.mul_sum]
    simp_rw [← map_mul]
    exact Fintype.sum_equiv (Equiv.mulLeft a) _ _ (fun _ => rfl)
  have hz : (χ a - 1) * ∑ g, χ g = 0 := by
    rw [sub_mul, one_mul, hs, sub_self]
  exact (mul_eq_zero.mp hz).resolve_left (sub_ne_zero.mpr ha)

end PaperX.IdealClassCharacter
