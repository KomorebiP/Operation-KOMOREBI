import Mathlib.Algebra.Polynomial.Coeff
import Mathlib.Algebra.Polynomial.Eval.Coeff
import Mathlib.Data.Finsupp.Basic
import Mathlib.Data.Nat.ModEq

/-!
# Residue projectors on actual finite polynomials

The coefficient filter below preserves finite support. It acts on `R[X]`,
not on arbitrary infinite coefficient sequences. Its algebraic laws require
only a semiring of coefficients. Reconstruction requires a positive modulus,
and refinement requires divisibility of the moduli.
-/

set_option autoImplicit false

open scoped BigOperators Polynomial

namespace Komorebi.Polynomial.Packets

variable {R S : Type*} [Semiring R] [Semiring S]

/-- Retain the coefficients whose degrees have residue `r` modulo `N`. -/
noncomputable def packet (N r : ℕ) (p : R[X]) : R[X] :=
  Polynomial.ofFinsupp (AddMonoidAlgebra.ofCoeff
    (p.coeff.filter (fun k => k % N = r)))

@[simp] theorem coeff_packet (N r : ℕ) (p : R[X]) (k : ℕ) :
    (packet N r p).coeff k = if k % N = r then p.coeff k else 0 := rfl

@[simp] theorem packet_zero (N r : ℕ) : packet N r (0 : R[X]) = 0 := by
  ext k
  simp

theorem packet_add (N r : ℕ) (p q : R[X]) :
    packet N r (p + q) = packet N r p + packet N r q := by
  ext k
  by_cases h : k % N = r <;> simp [h]

theorem packet_smul (N r : ℕ) (a : R) (p : R[X]) :
    packet N r (a • p) = a • packet N r p := by
  ext k
  by_cases h : k % N = r <;> simp [h]

/-- The finite coefficient filter is a linear endomorphism. -/
noncomputable def packetLinear (N r : ℕ) : R[X] →ₗ[R] R[X] where
  toFun := packet N r
  map_add' := packet_add N r
  map_smul' a p := packet_smul N r a p

@[simp] theorem packetLinear_apply (N r : ℕ) (p : R[X]) :
    packetLinear N r p = packet N r p := rfl

theorem packet_sum {I : Type*} (N r : ℕ) (s : Finset I) (f : I → R[X]) :
    packet N r (∑ i ∈ s, f i) = ∑ i ∈ s, packet N r (f i) :=
  map_sum (packetLinear N r) f s

theorem packet_monomial (N r k : ℕ) (a : R) :
    packet N r (Polynomial.monomial k a) =
      if k % N = r then Polynomial.monomial k a else 0 := by
  ext n
  by_cases hkn : k = n
  · subst n
    by_cases h : k % N = r <;> simp [h]
  · by_cases h : k % N = r <;> simp [Polynomial.coeff_monomial, h, hkn]

theorem packet_X_pow (N r k : ℕ) :
    packet N r (Polynomial.X ^ k : R[X]) =
      if k % N = r then Polynomial.X ^ k else 0 := by
  simpa only [Polynomial.monomial_one_right_eq_X_pow] using
    (packet_monomial (R := R) N r k 1)

/-- The projector is explicitly a finite sum of the retained monomials. -/
theorem packet_eq_sum (N r : ℕ) (p : R[X]) :
    packet N r p =
      ∑ k ∈ p.support, if k % N = r then Polynomial.monomial k (p.coeff k) else 0 := by
  conv_lhs => rw [← Polynomial.sum_monomial_eq p]
  simp only [Polynomial.sum_def, packet_sum, packet_monomial]

theorem packet_idempotent (N r : ℕ) (p : R[X]) :
    packet N r (packet N r p) = packet N r p := by
  ext k
  by_cases h : k % N = r <;> simp [h]

theorem packet_orthogonal (N : ℕ) {r s : ℕ} (hrs : r ≠ s) (p : R[X]) :
    packet N r (packet N s p) = 0 := by
  ext k
  by_cases h : k % N = r <;> simp [h, hrs]

theorem packet_reconstruct {N : ℕ} (hN : 0 < N) (p : R[X]) :
    (∑ r ∈ Finset.range N, packet N r p) = p := by
  ext k
  rw [Polynomial.finsetSum_coeff, Finset.sum_eq_single (k % N)]
  · simp
  · intro r _ hr
    simp [Ne.symm hr]
  · intro h
    exact False.elim (h (Finset.mem_range.mpr (Nat.mod_lt k hN)))

theorem packet_refined_packet {N M : ℕ} (hNM : N ∣ M)
    (r s : ℕ) (p : R[X]) :
    packet N r (packet M s p) =
      if s % N = r then packet M s p else 0 := by
  ext k
  by_cases hks : k % M = s
  · have hkn : k % N = s % N := by
      rw [← Nat.mod_mod_of_dvd k hNM, hks]
    by_cases hsr : s % N = r <;> simp [hks, hkn, hsr]
  · by_cases hsr : s % N = r <;> simp [hks, hsr]

theorem packet_refinement {N M : ℕ} (hM : 0 < M) (hNM : N ∣ M)
    (r : ℕ) (p : R[X]) :
    packet N r p =
      ∑ s ∈ Finset.range M, if s % N = r then packet M s p else 0 := by
  conv_lhs => rw [← packet_reconstruct hM p]
  rw [packet_sum]
  apply Finset.sum_congr rfl
  intro s _
  exact packet_refined_packet hNM r s p

/-- Extending coefficients commutes with residue projection. -/
theorem packet_map (f : R →+* S) (N r : ℕ) (p : R[X]) :
    (packet N r p).map f = packet N r (p.map f) := by
  ext k
  by_cases h : k % N = r <;> simp [h]

end Komorebi.Polynomial.Packets
