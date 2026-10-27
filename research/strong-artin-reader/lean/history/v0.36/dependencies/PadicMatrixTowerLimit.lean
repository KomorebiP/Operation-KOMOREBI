import CompatibleFrobeniusRoots
import Mathlib.NumberTheory.Padics.RingHoms

/-! Assembly of compatible positive Z/p-power coordinates into genuine p-adic
integers. The resulting matrix limit retains its compatible inverse. -/
noncomputable section
namespace Komorebi.StrongArtin.FrobeniusTower
variable (p : ℕ) [Fact (Nat.Prime p)]

/-- Reduction from the genuine p-adic integers to the recursive positive modulus. -/
def padicCoefficient (r : ℕ) : ℤ_[p] →+* Coeff p r :=
  (ZMod.ringEquivCongr (modulus_eq_pow p r).symm).toRingHom.comp (PadicInt.toZModPow (r+1))

def integralRepresentatives (a : ∀ r, Coeff p r) : ℕ → ℤ
  | 0 => 0
  | r+1 => (a r).val

theorem representative_compatibility (a : ∀ r, Coeff p r)
    (ha : ∀ r, coefficientDown p r (a (r+1)) = a r) :
    ∀ i, (p : ℤ)^i ∣ integralRepresentatives p a (i+1) - integralRepresentatives p a i := by
  intro i
  cases i with
  | zero => simp [integralRepresentatives]
  | succ r =>
    change (p : ℤ)^(r+1) ∣ ((a (r+1)).val : ℤ) - (a r).val
    rw [← Nat.cast_pow, ← modulus_eq_pow p r, ← ZMod.intCast_eq_intCast_iff_dvd_sub]
    push_cast
    rw [ZMod.natCast_zmod_val]
    calc
      a r = coefficientDown p r (a (r+1)) := (ha r).symm
      _ = ((a (r+1)).val : Coeff p r) := by
        change ZMod.cast (a (r+1)) = _
        exact ZMod.cast_eq_val _

def scalarLimit (a : ∀ r, Coeff p r)
    (ha : ∀ r, coefficientDown p r (a (r+1)) = a r) : ℤ_[p] :=
  PadicInt.ofIntSeq (integralRepresentatives p a)
    (PadicInt.isCauSeq_padicNorm_of_pow_dvd_sub _ p (representative_compatibility p a ha))

theorem scalarLimit_spec (a : ∀ r, Coeff p r)
    (ha : ∀ r, coefficientDown p r (a (r+1)) = a r) (r : ℕ) :
    padicCoefficient p r (scalarLimit p a ha) = a r := by
  have h := PadicInt.toZModPow_ofIntSeq_of_pow_dvd_sub
    (integralRepresentatives p a) p (representative_compatibility p a ha) (r+1)
  change (ZMod.ringEquivCongr (modulus_eq_pow p r).symm)
    ((scalarLimit p a ha).toZModPow (r+1)) = a r
  rw [show (scalarLimit p a ha).toZModPow (r+1) =
    (integralRepresentatives p a (r+1) : ZMod (p^(r+1))) from h]
  change (ZMod.ringEquivCongr (modulus_eq_pow p r).symm)
    (((a r).val : ℤ) : ZMod (p^(r+1))) = a r
  rw [map_intCast, Int.cast_natCast]
  exact ZMod.natCast_zmod_val _

theorem padicCoefficient_ext {x y : ℤ_[p]}
    (h : ∀ r, padicCoefficient p r x = padicCoefficient p r y) : x = y := by
  apply PadicInt.ext_of_toZModPow.mp
  intro r
  cases r with
  | zero => exact @Subsingleton.elim (ZMod 1) _ _ _
  | succ r => exact (ZMod.ringEquivCongr (modulus_eq_pow p r).symm).injective (h r)

theorem padicCoefficient_down (x : ℤ_[p]) (r : ℕ) :
    coefficientDown p r (padicCoefficient p (r+1) x) = padicCoefficient p r x := by
  have hc : (coefficientDown p r).comp
    (ZMod.ringEquivCongr (modulus_eq_pow p (r+1)).symm).toRingHom =
    (ZMod.ringEquivCongr (modulus_eq_pow p r).symm).toRingHom.comp
      (ZMod.castHom (pow_dvd_pow p (Nat.le_succ (r+1))) _) := Subsingleton.elim _ _
  have h := congrArg (fun f => f (x.toZModPow (r+2))) hc
  simpa [padicCoefficient, PadicInt.cast_toZModPow] using h

variable (n : Type) [Fintype n] [DecidableEq n]

def matrixLimit (M : ∀ r, Matrix n n (Coeff p r))
    (hM : ∀ r, (coefficientDown p r).mapMatrix (M (r+1)) = M r) : Matrix n n ℤ_[p] :=
  fun i j => scalarLimit p (fun r => M r i j)
    (fun r => congrFun (congrFun (hM r) i) j)

theorem matrixLimit_spec (M : ∀ r, Matrix n n (Coeff p r))
    (hM : ∀ r, (coefficientDown p r).mapMatrix (M (r+1)) = M r) (r : ℕ) :
    (padicCoefficient p r).mapMatrix (matrixLimit p n M hM) = M r := by
  ext i j
  exact scalarLimit_spec p _ _ r

theorem padicMatrix_ext {X Y : Matrix n n ℤ_[p]}
    (h : ∀ r, (padicCoefficient p r).mapMatrix X = (padicCoefficient p r).mapMatrix Y) : X = Y := by
  ext i j
  apply padicCoefficient_ext p
  intro r
  exact congrFun (congrFun (h r) i) j

def padicUnitReduction (r : ℕ) : (Matrix n n ℤ_[p])ˣ →* MatrixUnits p n r :=
  Units.map (padicCoefficient p r).mapMatrix.toMonoidHom

theorem padicUnitReduction_compatible (F : (Matrix n n ℤ_[p])ˣ) :
    Compatible p n (fun r => padicUnitReduction p n r F) := by
  intro r
  apply Units.ext
  ext i j
  exact padicCoefficient_down p (F.val i j) r

theorem padicUnit_ext {F G : (Matrix n n ℤ_[p])ˣ}
    (h : ∀ r, padicUnitReduction p n r F = padicUnitReduction p n r G) : F = G := by
  apply Units.ext
  apply padicMatrix_ext p n
  intro r
  exact congrArg Units.val (h r)

omit [Fact (Nat.Prime p)] in
theorem unitValues_compatible (F : ∀ r, MatrixUnits p n r) (hF : Compatible p n F) :
    ∀ r, (coefficientDown p r).mapMatrix (F (r+1)).val = (F r).val := by
  intro r
  exact congrArg Units.val (hF r)

omit [Fact (Nat.Prime p)] in
theorem unitInverses_compatible (F : ∀ r, MatrixUnits p n r) (hF : Compatible p n F) :
    ∀ r, (coefficientDown p r).mapMatrix ((F (r+1))⁻¹).val = ((F r)⁻¹).val := by
  intro r
  change (down p n r ((F (r+1))⁻¹)).val = _
  rw [map_inv, hF r]

/-- Assemble both the matrices and their compatible inverses. -/
def unitLimit (F : ∀ r, MatrixUnits p n r) (hF : Compatible p n F) :
    (Matrix n n ℤ_[p])ˣ where
  val := matrixLimit p n (fun r => (F r).val) (unitValues_compatible p n F hF)
  inv := matrixLimit p n (fun r => ((F r)⁻¹).val) (unitInverses_compatible p n F hF)
  val_inv := by
    apply padicMatrix_ext p n
    intro r
    rw [map_mul, matrixLimit_spec, matrixLimit_spec, map_one]
    exact (F r).val_inv
  inv_val := by
    apply padicMatrix_ext p n
    intro r
    rw [map_mul, matrixLimit_spec, matrixLimit_spec, map_one]
    exact (F r).inv_val

@[simp] theorem unitLimit_spec (F : ∀ r, MatrixUnits p n r) (hF : Compatible p n F) (r : ℕ) :
    padicUnitReduction p n r (unitLimit p n F hF) = F r := by
  apply Units.ext
  exact matrixLimit_spec p n (fun s => (F s).val) (unitValues_compatible p n F hF) r

end Komorebi.StrongArtin.FrobeniusTower
