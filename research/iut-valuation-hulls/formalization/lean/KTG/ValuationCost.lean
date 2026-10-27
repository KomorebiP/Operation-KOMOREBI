import Lean
import KTG.ValuationHulls

/-!
# Exact exponent and normalization cost in a DVR diagonal-lattice model

For ideals pi^a O and pi^b O, the smallest ideal containing both has
exponent min(a,b); its enlargement exponent relative to pi^a O is
`a-min(a,b)`.  This encodes the precise index cost in integer units. It
is deliberately a local toy model, not an assertion about IUT hulls.
-/

namespace KTG
namespace ValuationBridge

/-- Largest exponent of an ideal containing both pi^a O and pi^b O. -/
def hullExponent (a b : Nat) : Nat := min a b

/-- The exact minimal cost of enlarging pi^a O enough to contain pi^b O. -/
def enlargementCost (a b : Nat) : Nat := a - hullExponent a b

/-- The proposed hull exponent contains both ideals. -/
theorem hullExponent_feasible (a b : Nat) :
    hullExponent a b ≤ a ∧ hullExponent a b ≤ b := by
  exact ⟨Nat.min_le_left _ _, Nat.min_le_right _ _⟩

/-- Any common-containing ideal must have exponent no greater than min(a,b). -/
theorem hullExponent_maximal (a b c : Nat)
    (ha : c ≤ a) (hb : c ≤ b) : c ≤ hullExponent a b := by
  exact Nat.le_min.mpr ⟨ha, hb⟩

/-- Optimality: no other common-containing ideal can have a smaller
index/volume enlargement cost than the minimal hull. -/
theorem enlargementCost_optimal (a b c : Nat)
    (ha : c ≤ a) (hb : c ≤ b) :
    enlargementCost a b ≤ a - c := by
  unfold enlargementCost
  have h := hullExponent_maximal a b c ha hb
  omega

/-- If the source ideal is already larger, there is zero enlargement. -/
theorem enlargementCost_zero_of_le (a b : Nat) (h : a ≤ b) :
    enlargementCost a b = 0 := by
  simp [enlargementCost, hullExponent, Nat.min_eq_left h]

/-- If the source ideal is deeper, the cost equals the valuation gap. -/
theorem enlargementCost_eq_sub (a b : Nat) (h : b ≤ a) :
    enlargementCost a b = a - b := by
  simp [enlargementCost, hullExponent, Nat.min_eq_right h]

/-- A theta depth s*m (s>=1) versus a q-pilot depth m requires
exactly (s-1)*m units of volume enlargement. -/
theorem power_weight_cost (s m : Nat) (hs : 1 ≤ s) :
    enlargementCost (s * m) m = (s - 1) * m := by
  have hm : m ≤ s * m := by
    simpa using Nat.mul_le_mul_right m hs
  calc
    enlargementCost (s * m) m = s * m - m :=
      enlargementCost_eq_sub _ _ hm
    _ = (s - 1) * m := by simp [Nat.sub_mul]

/-- Sum of minimal enlargement exponents for independent diagonal factors. -/
def totalEnlargementCost (s : List Nat) (m : Nat) : Nat :=
  (s.map (fun j => enlargementCost (j * m) m)).sum

/-- Exact positive slope across all tensor/summand coordinates. -/
theorem totalEnlargementCost_exact
    (s : List Nat) (m : Nat)
    (hs : ∀ j, j ∈ s → 1 ≤ j) :
    totalEnlargementCost s m = (s.map (fun j => j - 1)).sum * m := by
  induction s with
  | nil => simp [totalEnlargementCost]
  | cons j rest ih =>
      have hj : 1 ≤ j := hs j (by simp)
      have hrest : ∀ k, k ∈ rest → 1 ≤ k := by
        intro k hk
        exact hs k (by simp [hk])
      simp only [totalEnlargementCost, List.map_cons, List.sum_cons]
      rw [power_weight_cost j m hj]
      have hrest_eq :
          (rest.map (fun j => enlargementCost (j * m) m)).sum =
            (rest.map (fun j => j - 1)).sum * m := by
        simpa only [totalEnlargementCost] using ih hrest
      rw [hrest_eq]
      exact (Nat.add_mul _ _ _).symm

/-- Example: weights 1,4,9, and q-height m=3 yield exact index exponent 33. -/
example : totalEnlargementCost [1, 4, 9] 3 = 33 := by decide

/-- The grade loss grows linearly: for positive total slope `d`, it
cannot be uniformly bounded as m increases. -/
theorem weighted_cost_unbounded
    (s : List Nat) (d : Nat)
    (hs : ∀ j, j ∈ s → 1 ≤ j)
    (hd : (s.map (fun j => j - 1)).sum = d)
    (hdpos : 0 < d) (C : Nat) :
    C < totalEnlargementCost s (C + 1) := by
  rw [totalEnlargementCost_exact s (C + 1) hs, hd]
  have h : 1 ≤ d := hdpos
  have hmul : 1 * (C + 1) ≤ d * (C + 1) :=
    Nat.mul_le_mul_right (C + 1) h
  omega

end ValuationBridge
end KTG
