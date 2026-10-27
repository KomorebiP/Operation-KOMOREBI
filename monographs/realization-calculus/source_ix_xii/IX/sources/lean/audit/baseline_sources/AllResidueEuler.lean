module
public import AllRatiosDwork
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.AllResidueEuler
open PowerSeries SingularRatioAmice RatioSeriesSupport RatioRiccati AllRatiosDwork
open EulerSeriesInverse HurwitzDworkClosure SeriesDifferenceBridge Mahler

/-- Original unnormalized Euler series, with its literal factorial normalization. -/
def unnormalizedSeries (N : ℕ) (hN : N≠0) (j : ℕ) : PowerSeries ℚ :=
  C (j.factorial:ℚ)*expand N hN (Congruential.packetSeries N j)

/-- The original factorial-normalized packet is the Hurwitz coefficient of this series. -/
theorem decode_unnormalized (N : ℕ) (hN : N≠0) (j n : ℕ) :
    EGF.decode (unnormalizedSeries N hN j) (N*n) = Congruential.unnormalized N j n := by
  simp only [unnormalizedSeries, EGF.decode, coeff_C_mul, coeff_expand_mul,
    Congruential.packetSeries, coeff_mk, Congruential.unnormalized]
  have hn : ((N*n).factorial:ℚ)≠0 := Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero _)
  field_simp

theorem unnormalized_support (N : ℕ) (hN : N≠0) (j d : ℕ) (hd : ¬N∣d) :
    coeff d (unnormalizedSeries N hN j)=0 := by
  rw [unnormalizedSeries, coeff_C_mul, coeff_expand_of_not_dvd N hN _ hd, mul_zero]

/-- Telescoping is proved from the actual source/inverse identities, not an assumed factorization. -/
theorem unnormalized_successor (N : ℕ) (hN : N≠0) (j : ℕ) :
    unnormalizedSeries N hN (j+1)=unnormalizedSeries N hN j*ratioSeries N hN j := by
  have hi := congrArg (expand N hN) (Congruential.packet_times_kernel N j)
  simp only [map_mul, map_one] at hi
  simp only [unnormalizedSeries, ratioSeries, expanded_inverse]
  calc
    _ = C (j.factorial:ℚ)*C (j+1:ℚ)*expand N hN (Congruential.packetSeries N (j+1)) := by
      rw [Nat.factorial_succ, Nat.cast_mul, map_mul]
      push_cast
      ring
    _ = C (j.factorial:ℚ)*C (j+1:ℚ)*
        (expand N hN (Congruential.packetSeries N j)*expand N hN (Congruential.sectionKernel N j))*
        expand N hN (Congruential.packetSeries N (j+1)) := by rw [hi, mul_one]
    _ = _ := by ring

variable (p : ℕ) [Fact p.Prime]

/-- All-residue flatness of the actual Euler family. Both singular and nonsingular addresses
    are proved in preceding modules; no weightedness or flatness certificate is assumed. -/
theorem all_residue_flat (m : ℕ) (hm : m∣p-1) (hmpos : 0<m) (j : ℕ) (hj : j<m*p) :
    Flat p (rationalMap p (unnormalizedSeries (m*p)
      (Nat.mul_pos hmpos (Fact.out : p.Prime).pos).ne' j)) := by
  induction j with
  | zero =>
    simpa only [unnormalizedSeries, Nat.factorial_zero, Nat.cast_one, map_one, one_mul] using
      packet_window_flat p m 0 hm hmpos (Fact.out : p.Prime).pos
  | succ j ih =>
    rw [unnormalized_successor, rationalMap, map_mul]
    exact flat_mul p (ih (by omega)) (all_ratios_flat p m hm hmpos j hj)

/-- Integrality of every original unnormalized coefficient, including higher residue classes. -/
theorem unnormalized_integral (m j n : ℕ) (hm : m∣p-1) (hmpos : 0<m) (hj : j<m*p) :
    ((Congruential.unnormalized (m*p) j n : ℚ):ℚ_[p])∈PadicInt.subring p := by
  have H := all_residue_flat p m hm hmpos j hj 0 (m*p*n)
  change EGF.decode (rationalMap p _) (m*p*n) ∈ _ at H
  rw [decode_rationalMap, decode_unnormalized] at H
  exact H

/-- Actual integral lift used for the ideal-divisibility formulation of the global theorem. -/
def unnormalizedLift (m j : ℕ) (hm : m∣p-1) (hmpos : 0<m) (hj : j<m*p) : ℕ → ℤ_[p] :=
  packetLift p (m*p)
    (unnormalizedSeries (m*p) (Nat.mul_pos hmpos (Fact.out : p.Prime).pos).ne' j)
    (all_residue_flat p m hm hmpos j hj 0)

@[simp] theorem unnormalizedLift_coe (m j n : ℕ) (hm : m∣p-1) (hmpos : 0<m) (hj : j<m*p) :
    (unnormalizedLift p m j hm hmpos hj n : ℚ_[p]) =
      ((Congruential.unnormalized (m*p) j n : ℚ):ℚ_[p]) := by
  change EGF.decode (rationalMap p
    (unnormalizedSeries (m*p) (Nat.mul_pos hmpos (Fact.out : p.Prime).pos).ne' j)) (m*p*n) = _
  rw [decode_rationalMap, decode_unnormalized]

/-- Theorem 7.5 as nonvacuous divisibility in the actual completed ring Z_p. -/
theorem global_unnormalized_bound (m j u k n : ℕ)
    (hm : m∣p-1) (hmpos : 0<m) (hj : j<m*p) :
    (p:ℤ_[p])^(min k (m*n)) ∣
      difference (u*((p-1)/m)) k (unnormalizedLift p m j hm hmpos hj) n := by
  exact packet_divisibility p m hm hmpos
    (unnormalizedSeries (m*p) (Nat.mul_pos hmpos (Fact.out : p.Prime).pos).ne' j)
    (all_residue_flat p m hm hmpos j hj) (unnormalized_support (m*p) _ j) u k n

/-- The same theorem stated literally for the original rational coefficient function, with zero safe. -/
theorem global_unnormalized_precision (m j u k n : ℕ)
    (hm : m∣p-1) (hmpos : 0<m) (hj : j<m*p) :
    GlobalEulerBoundary.precision p ((min k (m*n):ℕ):ℤ)
      (difference (u*((p-1)/m)) k (Congruential.unnormalized (m*p) j) n) := by
  have H := packet_precision p m hm hmpos
    (unnormalizedSeries (m*p) (Nat.mul_pos hmpos (Fact.out : p.Prime).pos).ne' j)
    (all_residue_flat p m hm hmpos j hj)
    (unnormalized_support (m*p) _ j) u k n
  simpa only [decode_unnormalized] using H

/-- Normalization incurs exactly the proved factorial-valuation loss; no false no-loss extension. -/
theorem global_normalized_precision (m j u k n : ℕ)
    (hm : m∣p-1) (hmpos : 0<m) (hj : j<m*p) :
    GlobalEulerBoundary.precision p
      (((min k (m*n):ℕ):ℤ)-(padicValNat p j.factorial:ℤ))
      (difference (u*((p-1)/m)) k (Congruential.coeff (m*p) j) n) :=
  GlobalEulerBoundary.factorial_loss_transfer p (m*p) j (u*((p-1)/m)) k n _
    (global_unnormalized_precision p m j u k n hm hmpos hj)

/-- Extended valuation in Z_p assigns infinity to zero differences. -/
theorem global_unnormalized_order (m j u k n : ℕ)
    (hm : m∣p-1) (hmpos : 0<m) (hj : j<m*p) :
    (min k (m*n) : WithTop ℕ) ≤ PadicBounds.order p
      (difference (u*((p-1)/m)) k (unnormalizedLift p m j hm hmpos hj) n) :=
  (PadicBounds.nat_le_order_iff p _ _).mpr
    (global_unnormalized_bound p m j u k n hm hmpos hj)

end KomorebiPaperIX.AllResidueEuler
