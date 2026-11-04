import KomorebiPolynomial.FallingPackets

/-!
# Multiplication transported through falling-factorial coordinates

The product below is the concrete operation `Φ (Φ⁻¹ p * Φ⁻¹ q)` from the
reader demonstration. It acts on finite rational polynomials. Ordinary polynomial
multiplication is used inside the source coordinates; the transported product
has its own multiplication laws on the target coordinates. Its residue packets
multiply by exact finite cyclic convolution.
-/

set_option autoImplicit false

open Polynomial
open scoped BigOperators

namespace Komorebi.Polynomial.FallingProduct

open Komorebi.Polynomial.FallingFactorial
open Komorebi.Polynomial.Packets
open Komorebi.Polynomial.FallingPackets

/-- The actual product transported by the constructed falling-factorial equivalence. -/
noncomputable def fallingProduct (p q : ℚ[X]) : ℚ[X] :=
  fallingEquiv (fallingEquiv.symm p * fallingEquiv.symm q)

/-- The transported product agrees with multiplication in source coordinates. -/
theorem fallingProduct_on_coordinates (p q : ℚ[X]) :
    fallingProduct (fallingEquiv p) (fallingEquiv q) = fallingEquiv (p * q) := by
  simp [fallingProduct]

theorem fallingProduct_assoc (p q r : ℚ[X]) :
    fallingProduct (fallingProduct p q) r = fallingProduct p (fallingProduct q r) := by
  simp [fallingProduct, mul_assoc]

theorem fallingProduct_comm (p q : ℚ[X]) : fallingProduct p q = fallingProduct q p := by
  simp [fallingProduct, mul_comm]

@[simp] theorem fallingProduct_one_left (p : ℚ[X]) : fallingProduct 1 p = p := by
  have h1 : fallingEquiv.symm (1 : ℚ[X]) = 1 := by
    simpa using fallingEquiv_symm_descPochhammer 0
  simp [fallingProduct, h1]

@[simp] theorem fallingProduct_one_right (p : ℚ[X]) : fallingProduct p 1 = p := by
  rw [fallingProduct_comm, fallingProduct_one_left]

theorem fallingProduct_add_left (p q r : ℚ[X]) :
    fallingProduct (p + q) r = fallingProduct p r + fallingProduct q r := by
  simp [fallingProduct, add_mul]

theorem fallingProduct_add_right (p q r : ℚ[X]) :
    fallingProduct p (q + r) = fallingProduct p q + fallingProduct p r := by
  simp [fallingProduct, mul_add]

theorem fallingProduct_smul_left (a : ℚ) (p q : ℚ[X]) :
    fallingProduct (a • p) q = a • fallingProduct p q := by
  simp [fallingProduct]

theorem fallingProduct_smul_right (a : ℚ) (p q : ℚ[X]) :
    fallingProduct p (a • q) = a • fallingProduct p q := by
  simp [fallingProduct]

/-- The transported multiplication packaged as a rational bilinear map. -/
noncomputable def fallingProductBilinear : ℚ[X] →ₗ[ℚ] ℚ[X] →ₗ[ℚ] ℚ[X] where
  toFun p :=
    { toFun := fallingProduct p
      map_add' := fallingProduct_add_right p
      map_smul' := fun a q => fallingProduct_smul_right a p q }
  map_add' p q := by
    apply LinearMap.ext
    intro r
    exact fallingProduct_add_left p q r
  map_smul' a p := by
    apply LinearMap.ext
    intro q
    exact fallingProduct_smul_left a p q

/-- Falling-factorial degrees add under the transported product. -/
theorem fallingProduct_descPochhammer (a b : ℕ) :
    fallingProduct (descPochhammer ℚ a) (descPochhammer ℚ b) =
      descPochhammer ℚ (a + b) := by
  simp [fallingProduct, ← pow_add]

/-- The smallest nontrivial transported product is `X (X - 1)`. -/
theorem fallingProduct_X_X :
    fallingProduct (X : ℚ[X]) X = X * (X - 1) := by
  calc
    fallingProduct (X : ℚ[X]) X = descPochhammer ℚ 2 := by
      simpa using fallingProduct_descPochhammer 1 1
    _ = X * (X - 1) := by
      simpa using descPochhammer_succ_right ℚ 1

/-- Transported multiplication differs from ordinary multiplication on `X, X`. -/
theorem fallingProduct_ne_mul :
    fallingProduct (X : ℚ[X]) X ≠ X * X := by
  rw [fallingProduct_X_X]
  intro h
  have heval := congrArg (fun p : ℚ[X] => p.eval 1) h
  norm_num at heval

/-- Source-coordinate packet degrees add modulo the modulus under multiplication.
This homogeneous-product statement also covers zero and noncanonical packets. -/
theorem packet_mul_packet {R : Type*} [Semiring R] (N r a b : ℕ) (p q : R[X]) :
    packet N r (packet N a p * packet N b q) =
      if (a + b) % N = r then packet N a p * packet N b q else 0 := by
  induction p using Polynomial.induction_on' with
  | add p₁ p₂ ih₁ ih₂ =>
    simp only [packet_add, add_mul, ih₁, ih₂]
    by_cases h : (a + b) % N = r <;> simp [h]
  | monomial n c =>
    induction q using Polynomial.induction_on' with
    | add q₁ q₂ ih₁ ih₂ =>
      simp only [packet_add, mul_add, ih₁, ih₂]
      by_cases h : (a + b) % N = r <;> simp [h]
    | monomial m d =>
      by_cases hn : n % N = a
      · by_cases hm : m % N = b
        · have hnm : (n + m) % N = (a + b) % N := by
            rw [Nat.add_mod, hn, hm]
          simp [packet_monomial, hn, hm, monomial_mul_monomial, hnm]
        · simp [packet_monomial, hm]
      · simp [packet_monomial, hn]

/-- Ordinary finite coefficient packets multiply by exact cyclic convolution.
The modulus is positive; the output index may be any natural number. -/
theorem packet_cyclic_convolution {R : Type*} [Semiring R] {N : ℕ}
    (hN : 0 < N) (r : ℕ) (p q : R[X]) :
    packet N r (p * q) =
      ∑ a ∈ Finset.range N, ∑ b ∈ Finset.range N,
        if (a + b) % N = r then packet N a p * packet N b q else 0 := by
  conv_lhs => rw [← packet_reconstruct hN p, ← packet_reconstruct hN q]
  rw [Finset.sum_mul_sum, packet_sum]
  simp only [packet_sum, packet_mul_packet]

/-- The reader demonstration's cyclic convolution law for the actual transported
product and the actual falling-factorial packet projectors. -/
theorem fallingPacket_cyclic_convolution {N : ℕ} (hN : 0 < N)
    (r : ℕ) (p q : ℚ[X]) :
    fallingPacket N r (fallingProduct p q) =
      ∑ a ∈ Finset.range N, ∑ b ∈ Finset.range N,
        if (a + b) % N = r then
          fallingProduct (fallingPacket N a p) (fallingPacket N b q) else 0 := by
  simp only [fallingPacket_apply, fallingProduct, LinearEquiv.symm_apply_apply]
  rw [packet_cyclic_convolution hN]
  simp only [map_sum]
  apply Finset.sum_congr rfl
  intro a _
  apply Finset.sum_congr rfl
  intro b _
  split_ifs <;> simp

end Komorebi.Polynomial.FallingProduct
