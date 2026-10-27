import Lean
import KTG.ValuationCost

/-!
# Discrete log-volume witness and the exact price of adjoining a pilot

This source-LOCATION motivated model mirrors the one-sided scalar comparison
at IUT III Corollary 3.12, Step (xi-f), with integral valuations replacing
actual real log-volumes. It is NOT an IUT construction. The `joint` hull here
is computed *using the pilot*, unlike the actual source-defined output hull.
This difference is deliberate: it displays the cost of a tempting repair.
-/

namespace KTG
namespace ValuationBridge

/-- Negative valuation depth: discrete toy log-volume (residue-cardinality
log scale suppressed). -/
def negativeLogDepth (a : Nat) : Int := -(Int.ofNat a)

/-- The sign reversal in the pilot/theta scalar comparison. -/
theorem negativeLogDepth_bound_iff (a b : Nat) :
    negativeLogDepth b ≤ negativeLogDepth a ↔ a ≤ b := by
  simp only [negativeLogDepth, Int.neg_le_neg_iff]
  exact Int.ofNat_le

/-- A shallower pilot (b < a) violates the *unaltered* negative-depth
comparison with the theta region of depth a. -/
theorem no_free_pilot_bound (a b : Nat) (h : b < a) :
    ¬ negativeLogDepth b ≤ negativeLogDepth a := by
  rw [negativeLogDepth_bound_iff]
  omega

/-- Enlarging the output ideal to a joint hull that *contains the pilot*
makes the discrete scalar comparison hold. This alone does not justify such
an enlargement under the actual IUT transport algorithm. -/
theorem joint_hull_restores_pilot_bound (a b : Nat) :
    negativeLogDepth b ≤ negativeLogDepth (hullExponent a b) := by
  rw [negativeLogDepth_bound_iff]
  exact (hullExponent_feasible a b).2

/-- The repair has a precise minimum numerical cost; it cannot be treated
as cost-free if the pilot depth is strictly shallower. -/
theorem nonzero_repair_cost (a b : Nat) (h : b < a) :
    0 < enlargementCost a b := by
  rw [enlargementCost_eq_sub a b (Nat.le_of_lt h)]
  omega

/-- In the `s*m` to `m` model the repair cost is exactly `(s-1)*m`. -/
theorem weighted_pilot_repair_cost (s m : Nat) (hs : 1 ≤ s) :
    enlargementCost (s * m) m = (s - 1) * m :=
  power_weight_cost s m hs

/-- A completely explicit model where the original bound fails while the
pilot-adjoined hull bound holds at strictly positive cost. -/
theorem depth_four_vs_one :
    (¬ negativeLogDepth 1 ≤ negativeLogDepth 4) ∧
      (negativeLogDepth 1 ≤ negativeLogDepth (hullExponent 4 1)) ∧
      enlargementCost 4 1 = 3 := by
  exact ⟨by decide, by decide, by decide⟩

/-- A minimal approximate-witness interface for arbitrary discrete
output values. This does not assert the existence of a source-specific IUT
witness: it makes its numerical role explicit. -/
structure DiscreteOutputComparison (X : Type) where
  admissible : X → Prop
  logValue : X → Int
  upperEndpoint : Int
  upperBound : ∀ x, admissible x → logValue x ≤ upperEndpoint

/-- A source candidate measured within `E` of the fixed q-pilot value. -/
def ApproximatePilotWitness {X : Type}
    (C : DiscreteOutputComparison X) (pilot : Int) (E : Nat) : Prop :=
  ∃ x, C.admissible x ∧ pilot ≤ C.logValue x + E

/-- A valid approximate witness transfers an upper output bound to the
pilot, with no hidden loss. This is only the numerical half of Step (xi). -/
theorem bound_from_approximate_witness {X : Type}
    (C : DiscreteOutputComparison X) (pilot : Int) (E : Nat)
    (h : ApproximatePilotWitness C pilot E) :
    pilot ≤ C.upperEndpoint + E := by
  obtain ⟨x, hx, hnear⟩ := h
  have hup := C.upperBound x hx
  omega

/-- The error must pay at least the signed deficit in the pilot/output
comparison. In particular zero-cost witness is impossible if q exceeds b. -/
theorem error_at_least_pilot_deficit {X : Type}
    (C : DiscreteOutputComparison X) (pilot : Int) (E : Nat)
    (h : ApproximatePilotWitness C pilot E) :
    pilot - C.upperEndpoint ≤ (E : Int) := by
  have hle := bound_from_approximate_witness C pilot E h
  omega

/-- Crucial quantifier discipline: a witness in one branch does not yield a
bound from another branch. The output values in the two branches differ. -/
private def chosenBranchA : DiscreteOutputComparison Unit where
  admissible := fun _ => True
  logValue := fun _ => 0
  upperEndpoint := 0
  upperBound := by intro _ _; decide

private def chosenBranchB : DiscreteOutputComparison Unit where
  admissible := fun _ => True
  logValue := fun _ => -100
  upperEndpoint := -100
  upperBound := by intro _ _; decide

/-- Branch A supports the fixed pilot at zero cost. -/
theorem branchA_exact_witness : ApproximatePilotWitness chosenBranchA 0 0 := by
  exact ⟨(), trivial, by decide⟩

/-- Branch B does NOT inherit branch A's certificate. -/
theorem branchB_no_exact_witness : ¬ ApproximatePilotWitness chosenBranchB 0 0 := by
  rintro ⟨x, _, h⟩
  cases x
  exact absurd h (by decide)

end ValuationBridge
end KTG
