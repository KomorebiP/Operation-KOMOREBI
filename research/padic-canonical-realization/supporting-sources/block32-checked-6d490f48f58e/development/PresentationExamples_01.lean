import KomorebiPadic.PresentedReachableMask
import Mathlib.Tactic.FinCases

/-! # Restriction witnesses for invariant-factor presentations
Equal cardinality need not mean equal module type. Conversely, the same module
signature does not select a basis or one literal transition matrix.
-/
namespace KomorebiPadic
namespace FiniteModulePresentation
noncomputable section

/-- A concrete one-factor presentation, not a choice from the existence theorem. -/
def cyclicFour : Presentation 2 2 (ZMod 4) where
  Index := Fin 1
  indexFintype := inferInstance
  exponent _ := 2
  positive _ := by decide
  bounded _ := le_rfl
  equiv :=
    { toFun := fun x _ => x
      invFun := fun x => x 0
      left_inv := fun _ => rfl
      right_inv := by intro x; funext i; fin_cases i; rfl
      map_add' := fun _ _ => rfl }

def elementaryFour : Presentation 2 2 (Fin 2 → ZMod 2) where
  Index := Fin 2
  indexFintype := inferInstance
  exponent _ := 1
  positive _ := by decide
  bounded _ := by decide
  equiv := AddEquiv.refl _

theorem cyclicFour_signature : signature cyclicFour = {2} := by decide +kernel

theorem elementaryFour_signature : signature elementaryFour = {1,1} := by decide +kernel

/-- Equal state cardinalities do not determine an invariant-factor signature. -/
theorem equal_cardinality_not_isomorphic :
    Nat.card (ZMod 4) = Nat.card (Fin 2 → ZMod 2) ∧
      ¬ Nonempty (ZMod 4 ≃+ (Fin 2 → ZMod 2)) := by
  constructor
  · simp [Nat.card_fun]
  · rintro ⟨f⟩
    have h := signature_congr (by decide : 1 < 2) cyclicFour elementaryFour f
    rw [cyclicFour_signature, elementaryFour_signature] at h
    have hc := congrArg Multiset.card h
    norm_num at hc

/-- An explicit coordinate permutation. -/
def swapFive : (Fin 2 → ZMod 5) ≃+ (Fin 2 → ZMod 5) where
  toFun x := ![x 1,x 0]
  invFun x := ![x 1,x 0]
  left_inv x := by funext i; fin_cases i <;> rfl
  right_inv x := by funext i; fin_cases i <;> rfl
  map_add' x y := by funext i; fin_cases i <;> rfl

def identityFivePresentation : Presentation 5 1 (Fin 2 → ZMod 5) where
  Index := Fin 2
  indexFintype := inferInstance
  exponent _ := 1
  positive _ := by decide
  bounded _ := le_rfl
  equiv := AddEquiv.refl _

def swappedFivePresentation : Presentation 5 1 (Fin 2 → ZMod 5) where
  Index := Fin 2
  indexFintype := inferInstance
  exponent _ := 1
  positive _ := by decide
  bounded _ := le_rfl
  equiv := swapFive

def nilpotentFive : (Fin 2 → ZMod 5) →ₗ[ZMod (5^1)] (Fin 2 → ZMod 5) where
  toFun x := ![x 1,0]
  map_add' x y := by funext i; fin_cases i <;> simp
  map_smul' a x := by funext i; fin_cases i <;> simp

/-- The same invariant factors can have distinct, conjugate matrix entries. -/
theorem signature_does_not_choose_matrix :
    signature identityFivePresentation = signature swappedFivePresentation ∧
      entry identityFivePresentation nilpotentFive 0 1 = 1 ∧
      entry swappedFivePresentation nilpotentFive 0 1 = 0 := by
  refine ⟨signature_unique (by decide) _ _, ?_⟩
  decide +kernel

/-- At zero precision every cyclic presentation has no nontrivial factor. -/
theorem zero_precision_index_empty {p : ℕ} {V : Type*} [AddCommGroup V]
    (P : Presentation p 0 V) : IsEmpty P.Index := by
  refine ⟨fun i => ?_⟩
  have h0 := P.positive i
  have h1 := P.bounded i
  omega

/-- Positive factors at precision one have exactly one p-adic digit. -/
theorem precision_one_exponents {p : ℕ} {V : Type*} [AddCommGroup V]
    (P : Presentation p 1 V) (i : P.Index) : P.exponent i = 1 := by
  have h0 := P.positive i
  have h1 := P.bounded i
  omega

end
end FiniteModulePresentation
end KomorebiPadic
