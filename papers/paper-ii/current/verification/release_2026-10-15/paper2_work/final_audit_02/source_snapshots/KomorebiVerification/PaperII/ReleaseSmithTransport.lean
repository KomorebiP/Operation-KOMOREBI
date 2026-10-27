import KomorebiVerification.PaperII.ReleaseSmithRectangular

/-! Invertible Smith row/column changes on the actual quotient matrix fibres. -/
set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperII.SmithDVR
open scoped Matrix
universe u
section Change
variable {R : Type u} [CommRing R]
variable {m n : Type*} [Fintype m] [DecidableEq m] [Fintype n] [DecidableEq n]

/-- The genuine coordinate equivalence carried by a matrix unit. -/
def matrixUnitEquiv (U : (Matrix n n R)ˣ) : (n → R) ≃ₗ[R] (n → R) :=
  Matrix.toLin'OfInv (show (↑U⁻¹ : Matrix n n R) * ↑U = 1 by exact U.inv_val)
    (show (↑U : Matrix n n R) * ↑U⁻¹ = 1 by exact U.val_inv)

@[simp] theorem matrixUnitEquiv_apply (U : (Matrix n n R)ˣ) (x : n → R) :
    matrixUnitEquiv U x = (↑U : Matrix n n R) *ᵥ x := rfl

abbrev MatrixFiber (M : Matrix m n R) (b : m → R) := {x : n → R // M *ᵥ x = b}

/-- Explicit fibre equivalence induced by UMV=D, with the transformed target Ub. -/
def smithMatrixFiberEquiv (M : Matrix m n R) (U : (Matrix m m R)ˣ)
    (V : (Matrix n n R)ˣ) (D : Matrix m n R)
    (hsmith : (↑U : Matrix m m R) * M * V.val = D) (b : m → R) :
    MatrixFiber M b ≃ MatrixFiber D ((↑U : Matrix m m R) *ᵥ b) where
  toFun x := ⟨(matrixUnitEquiv V).symm x.val, by
    rw [← hsmith, ← Matrix.mulVec_mulVec, ← Matrix.mulVec_mulVec]
    change (↑U : Matrix m m R) *ᵥ
      (M *ᵥ matrixUnitEquiv V ((matrixUnitEquiv V).symm x.val)) = _
    rw [LinearEquiv.apply_symm_apply, x.property]⟩
  invFun y := ⟨matrixUnitEquiv V y.val, by
    apply (matrixUnitEquiv U).injective
    change (↑U : Matrix m m R) *ᵥ (M *ᵥ ((↑V : Matrix n n R) *ᵥ y.val)) = _
    rw [Matrix.mulVec_mulVec, Matrix.mulVec_mulVec, hsmith]
    exact y.property⟩
  left_inv x := by apply Subtype.ext; exact LinearEquiv.apply_symm_apply _ _
  right_inv y := by apply Subtype.ext; exact LinearEquiv.symm_apply_apply _ _
end Change

section Integral
variable {O : Type u} [CommRing O]
variable {m n : Type*} [Fintype m] [DecidableEq m] [Fintype n] [DecidableEq n]

/-- Reducing an integral matrix unit gives an actual unit over O/(pi^L). -/
def quotientMatrixUnit (pi : O) (L : Nat) (U : (Matrix n n O)ˣ) :
    (Matrix n n (QuotientAt pi L))ˣ :=
  Units.map ((Ideal.Quotient.mk (powerIdeal pi L)).mapMatrix).toMonoidHom U

@[simp] theorem quotientMatrixUnit_val (pi : O) (L : Nat) (U : (Matrix n n O)ˣ) :
    (↑(quotientMatrixUnit pi L U) : Matrix n n (QuotientAt pi L)) =
      (↑U : Matrix n n O).map (Ideal.Quotient.mk (powerIdeal pi L)) := rfl

/-- The equation UMV=D survives reduction; it is not replaced by a fibre-count hypothesis. -/
theorem quotient_smith_identity (pi : O) (L : Nat) (M : Matrix m n O)
    (U : (Matrix m m O)ˣ) (V : (Matrix n n O)ˣ) (D : Matrix m n O)
    (hsmith : (↑U : Matrix m m O) * M * V.val = D) :
    (↑(quotientMatrixUnit pi L U) : Matrix m m (QuotientAt pi L)) *
      M.map (Ideal.Quotient.mk (powerIdeal pi L)) * (quotientMatrixUnit pi L V).val =
      D.map (Ideal.Quotient.mk (powerIdeal pi L)) := by
  simp only [quotientMatrixUnit_val, ← Matrix.map_mul, hsmith]

/-- Actual integral-congruence solution fibre. -/
abbrev CongruenceFiber (pi : O) (L : Nat) (M : Matrix m n O) (b : m → O) :=
  MatrixFiber (M.map (Ideal.Quotient.mk (powerIdeal pi L)))
    (fun i => (powerIdeal pi L).mkQ (b i))

/-- The fibre of the original matrix is explicitly equivalent to its rectangular Smith fibre. -/
def smithCongruenceEquiv (pi : O) (L : Nat) {r f z : Nat}
    (M : Matrix (Fin r ⊕ Fin z) (Fin r ⊕ Fin f) O)
    (U : (Matrix (Fin r ⊕ Fin z) (Fin r ⊕ Fin z) O)ˣ)
    (V : (Matrix (Fin r ⊕ Fin f) (Fin r ⊕ Fin f) O)ˣ)
    (s : Fin r → Nat) (hsmith : U.val * M * V.val = rectangularMatrix pi s)
    (b : (Fin r ⊕ Fin z) → O) :
    CongruenceFiber pi L M b ≃ RectangularFiber (f := f) pi L s (U.val *ᵥ b) := by
  let e := smithMatrixFiberEquiv
    (M.map (Ideal.Quotient.mk (powerIdeal pi L))) (quotientMatrixUnit pi L U)
    (quotientMatrixUnit pi L V)
    ((rectangularMatrix (f := f) (z := z) pi s).map (Ideal.Quotient.mk (powerIdeal pi L)))
    (quotient_smith_identity pi L M U V _ hsmith)
    (fun i => (powerIdeal pi L).mkQ (b i))
  refine e.trans (Equiv.subtypeEquivRight ?_)
  intro x
  rw [rectangularMatrix_mulVec]
  have ht : (quotientMatrixUnit pi L U).val *ᵥ
      (fun i => (powerIdeal pi L).mkQ (b i)) =
      (fun i => (powerIdeal pi L).mkQ ((U.val *ᵥ b) i)) := by
    funext i
    exact (RingHom.map_mulVec (Ideal.Quotient.mk (powerIdeal pi L)) U.val b i).symm
  rw [ht]

/-- General DVR Smith obstruction theorem, retaining all rectangular zero rows. -/
theorem smith_congruence_nonempty_iff (pi : O) (L : Nat) {r f z : Nat}
    (M : Matrix (Fin r ⊕ Fin z) (Fin r ⊕ Fin f) O)
    (U : (Matrix (Fin r ⊕ Fin z) (Fin r ⊕ Fin z) O)ˣ)
    (V : (Matrix (Fin r ⊕ Fin f) (Fin r ⊕ Fin f) O)ˣ)
    (s : Fin r → Nat) (hsmith : U.val * M * V.val = rectangularMatrix pi s)
    (b : (Fin r ⊕ Fin z) → O) :
    Nonempty (CongruenceFiber pi L M b) ↔
      (∀ i : Fin r, pi ^ min (s i) L ∣ (U.val *ᵥ b) (.inl i)) ∧
      (∀ i : Fin z, pi ^ L ∣ (U.val *ᵥ b) (.inr i)) := by
  rw [(smithCongruenceEquiv pi L M U V s hsmith b).nonempty_congr]
  exact rectangularFiber_nonempty_iff pi L s _

/-- The exact number of solutions is q^((n-r)L+sum min(s_i,L)). -/
theorem smith_congruence_card [IsDomain O] [IsDiscreteValuationRing O]
    [Finite (IsLocalRing.ResidueField O)] (pi : O) (hpi : Irreducible pi) (L : Nat)
    {r f z : Nat} (M : Matrix (Fin r ⊕ Fin z) (Fin r ⊕ Fin f) O)
    (U : (Matrix (Fin r ⊕ Fin z) (Fin r ⊕ Fin z) O)ˣ)
    (V : (Matrix (Fin r ⊕ Fin f) (Fin r ⊕ Fin f) O)ˣ)
    (s : Fin r → Nat) (hsmith : U.val * M * V.val = rectangularMatrix pi s)
    (b : (Fin r ⊕ Fin z) → O)
    (ha : ∀ i : Fin r, pi ^ min (s i) L ∣ (U.val *ᵥ b) (.inl i))
    (hz : ∀ i : Fin z, pi ^ L ∣ (U.val *ᵥ b) (.inr i)) :
    Nat.card (CongruenceFiber pi L M b) =
      Nat.card (IsLocalRing.ResidueField O) ^ (f * L + ∑ i : Fin r, min (s i) L) := by
  rw [Nat.card_congr (smithCongruenceEquiv pi L M U V s hsmith b)]
  exact rectangularFiber_card pi hpi L s _ ha hz
end Integral
end Komorebi.PaperII.SmithDVR
#print axioms Komorebi.PaperII.SmithDVR.smith_congruence_nonempty_iff
#print axioms Komorebi.PaperII.SmithDVR.smith_congruence_card
