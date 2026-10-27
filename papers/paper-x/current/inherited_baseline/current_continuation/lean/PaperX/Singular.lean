import PaperX.Counting
import Mathlib.Algebra.Order.Floor.Div

/-!
Exact solutions to x^e = 0 in a DVR quotient. The count is derived by an
explicit equivalence with an ideal image; it is not stipulated as a model.
The exponent e is required to be positive.
-/
set_option autoImplicit false
namespace PaperX.Singular
open IsLocalRing IsDiscreteValuationRing

variable {O : Type*} [CommRing O] [IsDomain O] [IsDiscreteValuationRing O]

/-- Membership in a maximal-ideal power is measured by the actual DVR valuation. -/
theorem mem_power_iff (x : O) (m : ℕ) :
    x ∈ maximalIdeal O ^ m ↔ (m : ℕ∞) ≤ addVal O x := by
  obtain ⟨p, hp⟩ := exists_irreducible O
  rw [hp.maximalIdeal_eq, Ideal.span_singleton_pow, Ideal.mem_span_singleton,
    ← addVal_le_iff_dvd, hp.addVal_pow]

/-- The ceiling threshold is at most m for every positive exponent. -/
theorem ceil_threshold_le (m e : ℕ) (he : 0 < e) : m ⌈/⌉ e ≤ m := by
  apply (ceilDiv_le_iff_le_mul he).mpr
  nlinarith

/-- The exact valuation threshold, including the zero representative. -/
theorem power_mem_iff (x : O) (m e : ℕ) (he : 0 < e) :
    x ^ e ∈ maximalIdeal O ^ m ↔ x ∈ maximalIdeal O ^ (m ⌈/⌉ e) := by
  by_cases hx : x = 0
  · simp [hx, Nat.ne_of_gt he]
  · obtain ⟨p, hp⟩ := exists_irreducible O
    obtain ⟨n, u, hu⟩ := eq_unit_mul_pow_irreducible hx hp
    rw [mem_power_iff, mem_power_iff, addVal_pow, hu, addVal_def' u hp n]
    simp only [nsmul_eq_mul, ← Nat.cast_mul, ENat.natCast_le_natCast]
    exact (ceilDiv_le_iff_le_mul he).symm

/-- Actual roots in the quotient ring. -/
def Roots (m e : ℕ) := {x : O ⧸ maximalIdeal O ^ m // x ^ e = 0}

/-- For quotient representatives, the root condition equals an ideal-image condition. -/
theorem root_iff_coordinate (m e : ℕ) (he : 0 < e)
    (x : O ⧸ maximalIdeal O ^ m) :
    x ^ e = 0 ↔ x ∈ Submodule.map (maximalIdeal O ^ m).mkQ
      (maximalIdeal O ^ (m ⌈/⌉ e)) := by
  obtain ⟨a, rfl⟩ := Ideal.Quotient.mk_surjective x
  rw [← map_pow, Ideal.Quotient.eq_zero_iff_mem, power_mem_iff a m e he]
  change a ∈ maximalIdeal O ^ (m ⌈/⌉ e) ↔
    a ∈ Submodule.comap (maximalIdeal O ^ m).mkQ
      (Submodule.map (maximalIdeal O ^ m).mkQ (maximalIdeal O ^ (m ⌈/⌉ e)))
  rw [Submodule.comap_map_eq, Submodule.ker_mkQ,
    sup_eq_left.mpr (Ideal.pow_le_pow_right (ceil_threshold_le m e he))]

/-- The identity on the ambient quotient restricts to this exact equivalence. -/
noncomputable def rootsEquivCoordinate (m e : ℕ) (he : 0 < e) :
    Roots (O := O) m e ≃ PaperX.Counting.Coordinate (maximalIdeal O) m (m ⌈/⌉ e) :=
  Equiv.subtypeEquivRight (root_iff_coordinate m e he)

/-- Exact singular-power count over every DVR with finite residue field. -/
theorem singular_root_count [Finite (O ⧸ maximalIdeal O)] (m e : ℕ) (he : 0 < e) :
    Nat.card (Roots (O := O) m e) =
      Nat.card (O ⧸ maximalIdeal O) ^ (m - (m ⌈/⌉ e)) := by
  rw [Nat.card_congr (rootsEquivCoordinate (O := O) m e he)]
  exact PaperX.Counting.coordinate_count (maximalIdeal O) (not_a_field O) m (m ⌈/⌉ e)

omit [IsDiscreteValuationRing O] in
/-- The increasing finite counts do not imply several roots in the complete DVR. -/
theorem only_zero_integral_root (x : O) (e : ℕ) (he : 0 < e) : x ^ e = 0 ↔ x = 0 := by
  exact pow_eq_zero_iff (Nat.ne_of_gt he)

/-- If an integral value is a root at every precision, it is zero. -/
theorem compatible_integral_root_zero (x : O) (e : ℕ) (he : 0 < e)
    (h : ∀ m, Ideal.Quotient.mk (maximalIdeal O ^ m) x ^ e = 0) : x = 0 := by
  have hz : x ^ e = 0 := by
    apply (IsHausdorff.eq_iff_smodEq (I := maximalIdeal O)).mpr
    intro m
    simpa only [SModEq.zero, Ideal.smul_eq_mul, Ideal.mul_top] using
      (Ideal.Quotient.eq_zero_iff_mem.mp (by simpa only [map_pow] using h m))
  exact (only_zero_integral_root x e he).mp hz

/-- An entire compatible root tower is the zero tower. No completeness assumption
is needed: a root at depth e*m already reduces to zero at depth m. -/
theorem compatible_root_family_zero (e : ℕ) (he : 0 < e)
    (x : (m : ℕ) → O ⧸ maximalIdeal O ^ m)
    (hcompat : ∀ {m n : ℕ} (h : m ≤ n),
      Ideal.Quotient.factorPow (maximalIdeal O) h (x n) = x m)
    (hroot : ∀ m, x m ^ e = 0) : ∀ m, x m = 0 := by
  intro m
  have hm : m ≤ e*m := by nlinarith
  obtain ⟨y, hy⟩ := Ideal.Quotient.mk_surjective (x (e*m))
  have hmem : y ^ e ∈ maximalIdeal O ^ (e*m) := by
    apply Ideal.Quotient.eq_zero_iff_mem.mp
    simpa only [map_pow, hy] using hroot (e*m)
  have hdepth := (power_mem_iff y (e*m) e he).mp hmem
  have hceil : (e*m) ⌈/⌉ e = m := smul_ceilDiv he m
  rw [hceil] at hdepth
  rw [← hcompat hm, ← hy]
  change Ideal.Quotient.mk (maximalIdeal O ^ m) y = 0
  exact Ideal.Quotient.eq_zero_iff_mem.mpr hdepth

end PaperX.Singular
