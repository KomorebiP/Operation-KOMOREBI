import MixedCharacteristicMatrixKernel

/-! The canonical additive kernel coordinates have the expected integer-division
formula. They do not require or imply a splitting of the coefficient extension. -/
noncomputable section
namespace Komorebi.StrongArtin.MixedCharacteristic
variable (p m : ℕ)

@[simp] theorem layerEmbedding_natCast (a : ℕ) :
    layerEmbedding p m (a : ZMod p) = (m : Upper p m) * (a : Upper p m) := by
  simpa using layerEmbedding_intCast p m (a : ℤ)

theorem layerEmbedding_from_val [NeZero p] (z : ZMod p) :
    layerEmbedding p m z = ((m*z.val : ℕ) : Upper p m) := by
  calc
    layerEmbedding p m z = layerEmbedding p m (z.val : ZMod p) := by rw [ZMod.natCast_zmod_val]
    _ = _ := by rw [layerEmbedding_natCast, Nat.cast_mul]

theorem layerEmbedding_value [NeZero p] (hm : m ≠ 0) (z : ZMod p) :
    (layerEmbedding p m z).val = m*z.val := by
  rw [layerEmbedding_from_val]
  exact ZMod.val_natCast_of_lt
    (Nat.mul_lt_mul_of_pos_left (ZMod.val_lt z) (Nat.pos_of_ne_zero hm))

theorem layerEquiv_inverse_division [NeZero p] (hm : m ≠ 0) (x : Layer p m) :
    (layerEquiv p m hm).symm x = (x.val.val / m : ZMod p) := by
  let z := (layerEquiv p m hm).symm x
  have he : layerEmbedding p m z = x.val :=
    congrArg Subtype.val ((layerEquiv p m hm).apply_symm_apply x)
  have hv : x.val.val = m*z.val := by
    rw [← he, layerEmbedding_value p m hm]
  rw [hv, Nat.mul_div_cancel_left _ (Nat.pos_of_ne_zero hm), ZMod.natCast_zmod_val]

/-- Entrywise division by m computes the actual matrix-kernel coordinates. -/
theorem kernelCoordinates_division [NeZero p] (hpm : p ∣ m) (hm : m ≠ 0)
    (n : Type) [Fintype n] [DecidableEq n]
    (X : (matrixDatum p m hpm n).Kernel) (i j : n) :
    kernelCoordinates p m hpm n hm X i j = ( (X.val i j).val / m : ZMod p) := by
  let z := kernelCoordinates p m hpm n hm X i j
  have he : layerEmbedding p m z = X.val i j :=
    congrFun (congrFun (congrArg Subtype.val (embedding_coordinates p m hpm n hm X)) i) j
  have hv : (X.val i j).val = m*z.val := by rw [← he, layerEmbedding_value p m hm]
  rw [hv, Nat.mul_div_cancel_left _ (Nat.pos_of_ne_zero hm), ZMod.natCast_zmod_val]

/-- No additive retraction of the layer embedding exists when p divides m.
The construction above is not smuggling in a split mixed-characteristic ring. -/
theorem no_additive_layer_retraction [Fact (Nat.Prime p)] (hpm : p ∣ m) :
    ¬ ∃ f : Upper p m →+ ZMod p, Function.LeftInverse f (layerEmbedding p m) := by
  rintro ⟨f,hf⟩
  have h := hf 1
  rw [show (1 : ZMod p) = (1 : ℕ) by simp, layerEmbedding_natCast] at h
  simp only [Nat.cast_one,mul_one] at h
  have hmz : (m : ZMod p) = 0 := (ZMod.natCast_eq_zero_iff m p).2 hpm
  have hz := f.map_nsmul m (1 : Upper p m)
  simp only [nsmul_eq_mul, mul_one, hmz, zero_mul] at hz
  exact one_ne_zero (h.symm.trans hz)

end Komorebi.StrongArtin.MixedCharacteristic
