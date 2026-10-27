import KomorebiVerification.PaperII.ReleaseSmithDVR
import Mathlib.Data.Matrix.Block
import Mathlib.LinearAlgebra.Matrix.ToLin

/-! Rectangular Smith fibres: actual active, free-column and zero-row coordinates. -/
set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperII.SmithDVR
open IsLocalRing
open scoped Matrix
universe u
variable {O : Type u} [CommRing O]

/-- The actual reduced rectangular diagonal map, including every free column and zero row. -/
def rectangularDiagonal (pi : O) (L : Nat) {r f z : Nat} (s : Fin r → Nat)
    (x : (Fin r ⊕ Fin f) → QuotientAt pi L) : (Fin r ⊕ Fin z) → QuotientAt pi L :=
  Sum.elim (fun i => multiplyPower pi (s i) L (x (.inl i))) (fun _ => 0)

abbrev RectangularFiber (pi : O) (L : Nat) {r f z : Nat} (s : Fin r → Nat)
    (b : (Fin r ⊕ Fin z) → O) :=
  {x : (Fin r ⊕ Fin f) → QuotientAt pi L //
    rectangularDiagonal pi L s x = fun i => (powerIdeal pi L).mkQ (b i)}

theorem quotient_target_zero_iff (pi : O) (L : Nat) (b : O) :
    (powerIdeal pi L).mkQ b = 0 ↔ pi ^ L ∣ b := by
  rw [Submodule.mkQ_apply, Submodule.Quotient.mk_eq_zero, powerIdeal, Ideal.mem_span_singleton]

/-- Explicit product decomposition of a diagonal solution fibre. -/
def rectangularFiberEquiv (pi : O) (L : Nat) {r f z : Nat} (s : Fin r → Nat)
    (b : (Fin r ⊕ Fin z) → O) (hz : ∀ i : Fin z, pi ^ L ∣ b (.inr i)) :
    RectangularFiber (f := f) pi L s b ≃
      (∀ i : Fin r, ScalarFiber pi (s i) L (b (.inl i))) × (Fin f → QuotientAt pi L) where
  toFun x := ⟨fun i => ⟨x.val (.inl i), congrFun x.property (.inl i)⟩,
    fun i => x.val (.inr i)⟩
  invFun x := ⟨Sum.elim (fun i => (x.1 i).val) x.2, by
    funext i
    cases i with
    | inl i => exact (x.1 i).property
    | inr i => exact ((quotient_target_zero_iff pi L _).mpr (hz i)).symm⟩
  left_inv x := by
    apply Subtype.ext
    funext i
    cases i <;> rfl
  right_inv x := by
    apply Prod.ext
    · funext i
      apply Subtype.ext
      rfl
    · rfl

theorem rectangularFiber_nonempty_iff (pi : O) (L : Nat) {r f z : Nat}
    (s : Fin r → Nat) (b : (Fin r ⊕ Fin z) → O) :
    Nonempty (RectangularFiber (f := f) pi L s b) ↔
      (∀ i : Fin r, pi ^ min (s i) L ∣ b (.inl i)) ∧
      (∀ i : Fin z, pi ^ L ∣ b (.inr i)) := by
  constructor
  · rintro ⟨x⟩
    constructor
    · intro i
      apply (scalarFiber_nonempty_iff pi (s i) L _).mp
      exact ⟨⟨x.val (.inl i), congrFun x.property (.inl i)⟩⟩
    · intro i
      apply (quotient_target_zero_iff pi L _).mp
      exact (congrFun x.property (.inr i)).symm
  · rintro ⟨ha, hz⟩
    exact ⟨(rectangularFiberEquiv pi L s b hz).symm
      ⟨fun i => Classical.choice ((scalarFiber_nonempty_iff pi (s i) L _).mpr (ha i)),
       fun _ => 0⟩⟩

/-- Every independent free column contributes q^L; no square/full-rank hypothesis occurs. -/
theorem rectangularFiber_card [IsDomain O] [IsDiscreteValuationRing O]
    [Finite (ResidueField O)] (pi : O) (hpi : Irreducible pi) (L : Nat)
    {r f z : Nat} (s : Fin r → Nat) (b : (Fin r ⊕ Fin z) → O)
    (ha : ∀ i : Fin r, pi ^ min (s i) L ∣ b (.inl i))
    (hz : ∀ i : Fin z, pi ^ L ∣ b (.inr i)) :
    Nat.card (RectangularFiber (f := f) pi L s b) =
      Nat.card (ResidueField O) ^ (f * L + ∑ i : Fin r, min (s i) L) := by
  rw [Nat.card_congr (rectangularFiberEquiv (f := f) pi L s b hz), Nat.card_prod,
    Nat.card_pi, Nat.card_fun, Nat.card_fin, quotientAt_card pi hpi]
  simp_rw [scalarFiber_card pi hpi _ _ _ (ha _)]
  rw [Finset.prod_pow_eq_pow_sum, ← pow_mul, ← pow_add, Nat.mul_comm L f, Nat.add_comm]

/-- Integral rectangular diagonal matrix giving the preceding coordinate formula. -/
def rectangularMatrix (pi : O) {r f z : Nat} (s : Fin r → Nat) :
    Matrix (Fin r ⊕ Fin z) (Fin r ⊕ Fin f) O :=
  Matrix.fromBlocks (Matrix.diagonal (fun i => pi ^ s i)) 0 0 0

/-- Reducing the displayed integral diagonal matrix gives the actual quotient map. -/
theorem rectangularMatrix_mulVec (pi : O) (L : Nat) {r f z : Nat} (s : Fin r → Nat)
    (x : (Fin r ⊕ Fin f) → QuotientAt pi L) :
    (rectangularMatrix (f := f) (z := z) pi s).map (Ideal.Quotient.mk (powerIdeal pi L)) *ᵥ x =
      rectangularDiagonal pi L s x := by
  funext i
  cases i with
  | inl i =>
      simp [rectangularMatrix, rectangularDiagonal, Matrix.mulVec, dotProduct,
        Matrix.fromBlocks, Matrix.diagonal, multiplyPower, Algebra.smul_def, apply_ite, ite_mul]
  | inr i =>
      simp [rectangularMatrix, rectangularDiagonal, Matrix.mulVec, dotProduct, Matrix.fromBlocks]

end Komorebi.PaperII.SmithDVR
#print axioms Komorebi.PaperII.SmithDVR.rectangularFiber_nonempty_iff
#print axioms Komorebi.PaperII.SmithDVR.rectangularFiber_card
