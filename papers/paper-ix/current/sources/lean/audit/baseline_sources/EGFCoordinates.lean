module

public import ResiduePackets
public import Mathlib.RingTheory.PowerSeries.Inverse
public import Mathlib.Data.Nat.Choose.Cast
public import Mathlib.Algebra.BigOperators.NatAntidiagonal

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.EGF

open PowerSeries

variable {K : Type*} [Field K] [CharZero K]

def encode (a : ℕ → K) : PowerSeries K :=
  PowerSeries.mk (fun n => a n / (n.factorial : K))

def decode (A : PowerSeries K) : ℕ → K :=
  fun n => PowerSeries.coeff n A * (n.factorial : K)

omit [CharZero K] in
@[simp] theorem encode_coeff (a : ℕ → K) (n : ℕ) :
    coeff n (encode a) = a n / (n.factorial : K) := by simp [encode]

@[simp] theorem decode_encode (a : ℕ → K) : decode (encode a) = a := by
  funext n
  simp [decode, Nat.factorial_ne_zero]

@[simp] theorem encode_decode (A : PowerSeries K) : encode (decode A) = A := by
  ext n
  simp [decode, Nat.factorial_ne_zero]

omit [CharZero K] in
theorem encode_add (a b : ℕ → K) : encode (a+b) = encode a + encode b := by
  ext n
  simp [add_div]

omit [CharZero K] in
theorem decode_add (A B : PowerSeries K) : decode (A+B) = decode A + decode B := by
  funext n
  simp [decode, add_mul]

omit [CharZero K] in
@[simp] theorem encode_zero : encode (0 : ℕ → K) = 0 := by ext n; simp

omit [CharZero K] in
@[simp] theorem decode_zero : decode (0 : PowerSeries K) = 0 := by funext n; simp [decode]

theorem egf_product (h a : ℕ → K) (n : ℕ) :
    decode (encode h * encode a) n =
      ∑ r ∈ Finset.range (n+1), (n.choose r : K) * h r * a (n-r) := by
  simp only [decode, coeff_mul, Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk,
    encode_coeff, Finset.sum_mul]
  apply Finset.sum_congr rfl
  intro r hr
  rw [Nat.cast_choose K (Finset.mem_range_succ_iff.mp hr)]
  ring

def transfer (H : PowerSeries K) (a : ℕ → K) : ℕ → K := decode (H * encode a)

theorem transfer_comp (H J : PowerSeries K) (a : ℕ → K) :
    transfer H (transfer J a) = transfer (H*J) a := by
  simp [transfer, mul_assoc]

@[simp] theorem transfer_one (a : ℕ → K) : transfer 1 a = a := by simp [transfer]

omit [CharZero K] in
theorem transfer_add (H : PowerSeries K) (a b : ℕ → K) :
    transfer H (a+b) = transfer H a + transfer H b := by
  simp [transfer, encode_add, mul_add, decode_add]

omit [CharZero K] in
@[simp] theorem transfer_zero (H : PowerSeries K) : transfer H 0 = 0 := by simp [transfer]

omit [CharZero K] in
theorem transfer_sum {ι : Type*} (H : PowerSeries K) (s : Finset ι) (a : ι → ℕ → K) :
    transfer H (∑ i ∈ s, a i) = ∑ i ∈ s, transfer H (a i) := by
  classical
  induction s using Finset.induction_on with
  | empty => simp
  | @insert i s hi ih => simp [Finset.sum_insert hi, transfer_add, ih]

/-- The inverse is constructed by the power-series inverse, not a supplied inverse law. -/
def coordinateEquiv (h : ℕ → K) (h0 : h 0 = 1) : (ℕ → K) ≃ (ℕ → K) where
  toFun := transfer (encode h)
  invFun := transfer (encode h)⁻¹
  left_inv a := by
    rw [transfer_comp, PowerSeries.inv_mul_cancel, transfer_one]
    simp [← coeff_zero_eq_constantCoeff, h0]
  right_inv a := by
    rw [transfer_comp, PowerSeries.mul_inv_cancel, transfer_one]
    simp [← coeff_zero_eq_constantCoeff, h0]

theorem coordinate_forward (h a : ℕ → K) (h0 : h 0 = 1) (n : ℕ) :
    coordinateEquiv h h0 a n = ∑ r ∈ Finset.range (n+1), (n.choose r : K)*h r* a (n-r) :=
  egf_product h a n

theorem coordinate_inverse (h a : ℕ → K) (h0 : h 0 = 1) (n : ℕ) :
    (coordinateEquiv h h0).symm a n =
      ∑ r ∈ Finset.range (n+1), (n.choose r : K)*decode (encode h)⁻¹ r* a (n-r) := by
  have hp := egf_product (decode (encode h)⁻¹) a n
  simpa [coordinateEquiv, transfer] using hp

theorem inverse_constant_one (h : ℕ → K) (h0 : h 0 = 1) :
    decode (encode h)⁻¹ 0 = 1 := by
  simp [decode, coeff_zero_eq_constantCoeff, encode, h0]

def transportedPacket (h : ℕ → K) (h0 : h 0 = 1) (N j : ℕ) (a : ℕ → K) : ℕ → K :=
  coordinateEquiv h h0 (ResiduePackets.packet N j ((coordinateEquiv h h0).symm a))

theorem transported_idempotent (h : ℕ → K) (h0 : h 0 = 1) (N j : ℕ) (a : ℕ → K) :
    transportedPacket h h0 N j (transportedPacket h h0 N j a) = transportedPacket h h0 N j a := by
  simp [transportedPacket]

theorem transported_orthogonal (h : ℕ → K) (h0 : h 0 = 1) (N i j : ℕ)
    (hij : i ≠ j) (a : ℕ → K) :
    transportedPacket h h0 N i (transportedPacket h h0 N j a) = 0 := by
  simp only [transportedPacket, Equiv.symm_apply_apply,
    ResiduePackets.packet_orthogonal N i j hij]
  exact transfer_zero _

theorem transported_reconstruction (h : ℕ → K) (h0 : h 0 = 1) {N : ℕ}
    (hN : 0 < N) (a : ℕ → K) : ∑ j ∈ Finset.range N, transportedPacket h h0 N j a = a := by
  change (∑ j ∈ Finset.range N, transfer (encode h)
    (ResiduePackets.packet N j ((coordinateEquiv h h0).symm a))) = a
  rw [← transfer_sum, ResiduePackets.packet_reconstruction hN]
  exact (coordinateEquiv h h0).apply_symm_apply a

def matrixEntry (h : ℕ → K) (n q : ℕ) : K :=
  if q ≤ n then (n.choose q : K) * h (n-q) else 0

omit [CharZero K] in
theorem matrix_diagonal (h : ℕ → K) (h0 : h 0 = 1) (n : ℕ) : matrixEntry h n n = 1 := by
  simp [matrixEntry, h0]

omit [CharZero K] in
theorem matrix_above_diagonal (h : ℕ → K) {n q : ℕ} (hq : n < q) : matrixEntry h n q = 0 := by
  simp [matrixEntry, Nat.not_le.mpr hq]

end KomorebiPaperIX.EGF
