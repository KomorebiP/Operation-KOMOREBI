import KomorebiPadic.AdaptivePartitionCertificate

/-!
# Integer area and a global work-queue potential

One split consumes one node and conserves the number of integer points.
The potential 2*area-1 therefore bounds all visits in a full binary refinement.
-/
namespace KomorebiPadic

/-- Number of integer points for a valid closed parameter box. -/
def ParameterBox.area (b : ParameterBox) : ℕ :=
  (b.rhi - b.rlo + 1) * (b.hhi - b.hlo + 1)

/-- Capacity for visits, including this node and every possible descendant. -/
def ParameterBox.nodeCapacity (b : ParameterBox) : ℕ := 2 * b.area - 1

theorem parameterBox_area_pos (b : ParameterBox) : 0 < b.area := by
  exact Nat.mul_pos (Nat.succ_pos _) (Nat.succ_pos _)

theorem parameterBox_nodeCapacity_pos (b : ParameterBox) : 0 < b.nodeCapacity := by
  have := parameterBox_area_pos b
  simp only [ParameterBox.nodeCapacity]
  omega

/-- A legal inclusive bisection exactly conserves integer area. -/
theorem parameterBox_split_area {b : ParameterBox} (hb : b.Valid)
    (hs : 0 < b.span) : b.split.1.area + b.split.2.area = b.area := by
  have hv := parameterBox_split_valid_and_decreases hb hs
  simp only [ParameterBox.Valid] at hb hv
  by_cases hr : b.rlo < b.rhi
  · simp only [ParameterBox.split, hr, ↓reduceIte, ParameterBox.area] at hv ⊢
    have hw : ((b.rlo + b.rhi) / 2 - b.rlo + 1) +
        (b.rhi - ((b.rlo + b.rhi) / 2 + 1) + 1) = b.rhi - b.rlo + 1 := by omega
    rw [← Nat.add_mul, hw]
  · simp only [ParameterBox.split, hr, ↓reduceIte, ParameterBox.area] at hv ⊢
    have hw : ((b.hlo + b.hhi) / 2 - b.hlo + 1) +
        (b.hhi - ((b.hlo + b.hhi) / 2 + 1) + 1) = b.hhi - b.hlo + 1 := by omega
    rw [← Nat.mul_add, hw]

/-- The sum of child capacities is exactly one less than the parent's. -/
theorem parameterBox_split_nodeCapacity {b : ParameterBox} (hb : b.Valid)
    (hs : 0 < b.span) :
    b.split.1.nodeCapacity + b.split.2.nodeCapacity + 1 = b.nodeCapacity := by
  have ha := parameterBox_split_area hb hs
  have h1 := parameterBox_area_pos b.split.1
  have h2 := parameterBox_area_pos b.split.2
  simp only [ParameterBox.nodeCapacity]
  omega

/-- Sum of capacities of the pending queue. -/
def pendingNodeCapacity : List ParameterBox → ℕ
  | [] => 0
  | b :: bs => b.nodeCapacity + pendingNodeCapacity bs

theorem pendingNodeCapacity_eq_zero_iff (bs : List ParameterBox) :
    pendingNodeCapacity bs = 0 ↔ bs = [] := by
  cases bs with
  | nil => simp [pendingNodeCapacity]
  | cons b bs =>
    have := parameterBox_nodeCapacity_pos b
    simp only [pendingNodeCapacity, List.cons_ne_nil, iff_false]
    omega

end KomorebiPadic
