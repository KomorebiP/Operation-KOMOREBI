import PaperXI.BilinearHeisenberg
import Mathlib.Algebra.CharP.Two

/-! Actual changes of central section and the square obstruction in characteristic
two. These statements concern the middle groups, not just their commutator forms. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HeisenbergCochain
open BilinearHeisenberg
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
variable (c d : LinearMap.BilinForm K V)

/-- A normalized coboundary constructs a genuine central-extension isomorphism. -/
def equiv (f : V → K) (_h0 : f 0 = 0)
    (hf : ∀ x y, d x y - c x y = f (x + y) - f x - f y) :
    Element c ≃* Element d where
  toFun h := ⟨h.vector, h.central + f h.vector⟩
  invFun h := ⟨h.vector, h.central - f h.vector⟩
  left_inv h := by ext <;> simp
  right_inv h := by ext <;> simp
  map_mul' h k := by
    ext
    · rfl
    · change h.central + k.central + c h.vector k.vector + f (h.vector + k.vector) =
        (h.central + f h.vector) + (k.central + f k.vector) + d h.vector k.vector
      linear_combination -(hf h.vector k.vector)

@[simp] theorem equiv_center (f : V → K) (h0 : f 0 = 0)
    (hf : ∀ x y, d x y - c x y = f (x + y) - f x - f y) (z : Multiplicative K) :
    equiv c d f h0 hf (i c z) = i d z := by
  ext <;> simp [equiv, h0]

@[simp] theorem equiv_vector (f : V → K) (h0 : f 0 = 0)
    (hf : ∀ x y, d x y - c x y = f (x + y) - f x - f y) (h : Element c) :
    (equiv c d f h0 hf h).vector = h.vector := rfl

section CharacteristicTwo
variable [CharP K 2]

/-- All lifts of a quotient vector have the same square, calculated from c. -/
theorem square (h : Element c) :
    h * h = i c (Multiplicative.ofAdd (c h.vector h.vector)) := by
  ext
  · change h.vector + h.vector = 0
    rw [← two_smul K, show (2 : K) = 0 from CharP.cast_eq_zero K 2, zero_smul]
  · change h.central + h.central + c h.vector h.vector = c h.vector h.vector
    rw [CharTwo.add_self_eq_zero, zero_add]

/-- A center- and quotient-preserving isomorphism must preserve the diagonal
factor set. Thus the alternating commutator alone does not determine the extension. -/
theorem diagonal_preserved (e : Element c ≃* Element d)
    (he : ∀ z, e (i c z) = i d z)
    (hq : ∀ h, (e h).vector = h.vector) (v : V) : c v v = d v v := by
  let h : Element c := ⟨v, 0⟩
  have hm := e.map_mul h h
  rw [square, he, square] at hm
  have hv := congrArg Element.central hm
  change c h.vector h.vector = d (e h).vector (e h).vector at hv
  rw [hq] at hv
  exact hv

theorem no_equiv_of_diagonal_mismatch (v : V) (hv : c v v ≠ d v v) :
    ¬ ∃ e : Element c ≃* Element d,
      (∀ z, e (i c z) = i d z) ∧ (∀ h, (e h).vector = h.vector) := by
  rintro ⟨e, he, hq⟩
  exact hv (diagonal_preserved c d e he hq v)

end CharacteristicTwo
end PaperXI.HeisenbergCochain
