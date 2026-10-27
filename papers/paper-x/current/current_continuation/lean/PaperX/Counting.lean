import Mathlib.RingTheory.Ideal.Norm.AbsNorm
import Mathlib.RingTheory.DiscreteValuationRing.Basic
import Mathlib.Data.Fintype.Pi
import Mathlib.Tactic

/-!
Actual finite ideal-quotient coordinates, not counts defined to equal a power.
The result works for any nonzero prime ideal of a Dedekind domain with finite
residue ring. In a DVR it applies to the maximal ideal. The additional passage
from continuous maps out of a formal power-series ring to parameter tuples is
kept separate from this finite ideal-chart counting theorem.
-/
set_option autoImplicit false
namespace PaperX.Counting

variable {O : Type*} [CommRing O] [IsDedekindDomain O]
variable (P : Ideal O) [P.IsPrime] (hP : P ≠ ⊥) [Finite (O ⧸ P)]

/-- The actual image of P^w inside O/P^m. -/
def Coordinate (m w : ℕ) := ↥(Submodule.map (P ^ m).mkQ (P ^ w))

noncomputable def residueCard : ℕ := Nat.card (O ⧸ P)

include hP

omit [Finite (O ⧸ P)] in
theorem quotient_count (m : ℕ) : Nat.card (O ⧸ P ^ m) = residueCard P ^ m := by
  exact cardQuot_pow_of_prime hP

/-- The dimension-one ideal chart, including the invisible range m <= w. -/
theorem coordinate_count (m w : ℕ) :
    Nat.card (Coordinate P m w) = residueCard P ^ (m - w) := by
  by_cases hwm : w ≤ m
  · have h := Submodule.card_quotient_mul_card_quotient
      (P ^ w) (P ^ m) (Ideal.pow_le_pow_right hwm)
    change Nat.card (Coordinate P m w) * Nat.card (O ⧸ P ^ w) =
      Nat.card (O ⧸ P ^ m) at h
    rw [quotient_count P hP w, quotient_count P hP m] at h
    have hp : residueCard P ^ w ≠ 0 := by
      exact pow_ne_zero w (show residueCard P ≠ 0 from Nat.card_pos.ne')
    apply Nat.mul_right_cancel (m := residueCard P ^ w)
    · exact Nat.pos_of_ne_zero hp
    · rw [h, ← pow_add, Nat.sub_add_cancel hwm]
  · have hle : P ^ w ≤ P ^ m := Ideal.pow_le_pow_right (by omega)
    have hz : Submodule.map (P ^ m).mkQ (P ^ w) = ⊥ := by
      apply le_antisymm _ bot_le
      rw [Submodule.map_le_iff_le_comap, Submodule.comap_bot, Submodule.ker_mkQ]
      exact hle
    simp [Coordinate, hz, Nat.sub_eq_zero_of_le (by omega : m ≤ w)]

/-- A weighted chart is a tuple of independently constrained quotient elements. -/
def WeightedChart {d : ℕ} (w : Fin d → ℕ) (m : ℕ) :=
  (i : Fin d) → Coordinate P m (w i)

/-- Exact weighted smooth-chart cardinality, for actual ideal quotients. -/
theorem weighted_chart_count {d : ℕ} (w : Fin d → ℕ) (m : ℕ) :
    Nat.card (WeightedChart P w m) = residueCard P ^ (∑ i, (m - w i)) := by
  change Nat.card ((i : Fin d) → Coordinate P m (w i)) = _
  rw [Nat.card_pi]
  simp_rw [coordinate_count P hP]
  exact (Finset.prod_pow_eq_pow_sum Finset.univ (fun i => m - w i) (residueCard P))

/-- Smooth d-dimensional positive-depth coordinates are the all-weight-one chart. -/
theorem smooth_chart_count (d m : ℕ) :
    Nat.card (WeightedChart P (fun _ : Fin d => 1) m) =
      residueCard P ^ (d * (m - 1)) := by
  rw [weighted_chart_count P hP]
  simp

/-- Written with max as in the manuscript; Nat subtraction is already truncated. -/
theorem weighted_chart_count_max {d : ℕ} (w : Fin d → ℕ) (m : ℕ) :
    Nat.card (WeightedChart P w m) =
      residueCard P ^ (∑ i, max (m - w i) 0) := by
  simpa using weighted_chart_count P hP w m

/-- Any independently established chart equivalence transfers this cardinality. -/
theorem count_via_chart {X : Type*} {d : ℕ} (w : Fin d → ℕ) (m : ℕ)
    (e : X ≃ WeightedChart P w m) :
    Nat.card X = residueCard P ^ (∑ i, (m - w i)) := by
  rw [Nat.card_congr e]
  exact weighted_chart_count P hP w m

end PaperX.Counting
