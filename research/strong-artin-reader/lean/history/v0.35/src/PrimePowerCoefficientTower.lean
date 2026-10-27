import MixedCharacteristicUniqueStep

/-! The actual positive prime-power coefficient tower. Recursive moduli keep each
transition definitionally equal to the previously verified Z/(mp) -> Z/m map. -/
noncomputable section
namespace Komorebi.StrongArtin.FrobeniusTower
open MixedCharacteristic

@[reducible] def modulus (p : ℕ) : ℕ → ℕ
  | 0 => p
  | r+1 => modulus p r * p

@[simp] theorem modulus_zero (p : ℕ) : modulus p 0 = p := rfl
@[simp] theorem modulus_succ (p r : ℕ) : modulus p (r+1) = modulus p r * p := rfl

theorem modulus_eq_pow (p r : ℕ) : modulus p r = p^(r+1) := by
  induction r with
  | zero => simp
  | succ r ih =>
    rw [modulus_succ, ih]
    exact (pow_succ p (r+1)).symm

theorem prime_dvd_modulus (p r : ℕ) : p ∣ modulus p r := by
  rw [modulus_eq_pow]
  exact dvd_pow_self p (Nat.succ_ne_zero r)

theorem modulus_ne_zero (p r : ℕ) [Fact (Nat.Prime p)] : modulus p r ≠ 0 := by
  rw [modulus_eq_pow]
  exact pow_ne_zero _ (Fact.out : Nat.Prime p).ne_zero

instance (p r : ℕ) [Fact (Nat.Prime p)] : NeZero (modulus p r) :=
  ⟨modulus_ne_zero p r⟩

abbrev Coeff (p r : ℕ) := ZMod (modulus p r)
abbrev MatrixUnits (p : ℕ) (n : Type) [Fintype n] [DecidableEq n] (r : ℕ) :=
  (Matrix n n (Coeff p r))ˣ

def coefficientDown (p r : ℕ) : Coeff p (r+1) →+* Coeff p r :=
  reduction p (modulus p r)

def coefficientResidue (p r : ℕ) : Coeff p r →+* ZMod p :=
  ZMod.castHom (prime_dvd_modulus p r) _

@[simp] theorem coefficientResidue_zero (p : ℕ) :
    coefficientResidue p 0 = RingHom.id (ZMod p) := by
  apply Subsingleton.elim

@[simp] theorem coefficientResidue_down (p r : ℕ) :
    (coefficientResidue p r).comp (coefficientDown p r) = coefficientResidue p (r+1) := by
  apply Subsingleton.elim

variable (p : ℕ) (n : Type) [Fintype n] [DecidableEq n]

def down (r : ℕ) : MatrixUnits p n (r+1) →* MatrixUnits p n r :=
  Units.map (coefficientDown p r).mapMatrix.toMonoidHom

def red (r : ℕ) : MatrixUnits p n r →* (Matrix n n (ZMod p))ˣ :=
  Units.map (coefficientResidue p r).mapMatrix.toMonoidHom

@[simp] theorem red_zero (F : MatrixUnits p n 0) : red p n 0 F = F := by
  apply Units.ext
  ext i j
  change coefficientResidue p 0 ((F : Matrix n n _) i j) = _
  rw [coefficientResidue_zero]
  rfl

@[simp] theorem red_down (r : ℕ) (F : MatrixUnits p n (r+1)) :
    red p n r (down p n r F) = red p n (r+1) F := by
  apply Units.ext
  ext i j
  exact congrArg (fun f : Coeff p (r+1) →+* ZMod p => f ((F : Matrix n n _) i j))
    (coefficientResidue_down p r)

@[simp] theorem layer_residualFrobenius (r : ℕ) (F : MatrixUnits p n (r+1)) :
    residualFrobenius p (modulus p r) n F = red p n (r+1) F := by
  apply Units.ext
  ext i j
  exact congrArg (fun f : Coeff p (r+1) →+* ZMod p => f ((F : Matrix n n _) i j))
    (Subsingleton.elim (residue p (modulus p r)) (coefficientResidue p (r+1)))

/-- The next-level original root exists uniquely; its condition is checked modulo p. -/
theorem unique_next_root [Fact (Nat.Prime p)] (r d : ℕ)
    (F : MatrixUnits p n r) (U : MatrixUnits p n (r+1))
    (hU : down p n r U = F^d)
    (hN : Nonresonant n (red p n r F) d) :
    ∃! F' : MatrixUnits p n (r+1), down p n r F' = F ∧ F'^d = U := by
  let D := matrixDatum p (modulus p r) (prime_dvd_modulus p r) n
  obtain ⟨F0, hF0⟩ := lift_lower_frobenius p (modulus p r) (prime_dvd_modulus p r) n F
  have hdown : down p n r F0 = F := Units.ext hF0
  have hres : residualFrobenius p (modulus p r) n F0 = red p n r F := by
    exact (layer_residualFrobenius p n r F0).trans
      ((red_down p n r F0).symm.trans (congrArg (red p n r) hdown))
  have hU' : D.q U.val = D.q (F0^d).val := by
    have h := hU.trans (congrArg (fun x : MatrixUnits p n r => x^d) hdown.symm)
    exact congrArg Units.val (h.trans (map_pow (down p n r) F0 d).symm)
  obtain ⟨x, hx, hu⟩ := mixed_unique_power_lift p (modulus p r) (prime_dvd_modulus p r)
    (modulus_ne_zero p r) n F0 U d (hres ▸ hN) hU'
  refine ⟨x, ⟨(Units.ext hx.1).trans hdown, hx.2⟩, ?_⟩
  intro y hy
  apply hu y
  exact ⟨congrArg Units.val (hy.1.trans hdown.symm), hy.2⟩

end Komorebi.StrongArtin.FrobeniusTower
