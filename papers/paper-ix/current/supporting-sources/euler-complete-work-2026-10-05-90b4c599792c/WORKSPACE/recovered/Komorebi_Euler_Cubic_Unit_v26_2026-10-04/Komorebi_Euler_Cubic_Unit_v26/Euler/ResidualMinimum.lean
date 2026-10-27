module
public import Euler.ResidualCarry
public import Mathlib.Data.Finset.Max
@[expose] public section
noncomputable section
namespace Komorebi.Euler

/-- A proved finite search domain, not a numerical cutoff chosen by a checker. -/
def residualCarryRange (r : ℕ) : Finset ℕ :=
  Finset.range ((binaryDigitSum r-1)/3+1)

lemma residualCarryRange_zero (r : ℕ) : 0∈residualCarryRange r := by
  simp [residualCarryRange]

def residualCarryValues (r : ℕ) : Finset ℤ :=
  (residualCarryRange r).image (residualCarryCost r)

lemma residualCarryValues_nonempty (r : ℕ) : (residualCarryValues r).Nonempty := by
  exact Finset.Nonempty.image ⟨0,residualCarryRange_zero r⟩ _

/-- The actual global minimum for positive residual depths. -/
def residualCarryMinimum (r : ℕ) : ℤ :=
  (residualCarryValues r).min' (residualCarryValues_nonempty r)

lemma residualCarryMinimum_le_in_range (r q : ℕ) (hq : q∈residualCarryRange r) :
    residualCarryMinimum r≤residualCarryCost r q := by
  exact Finset.min'_le _ _ (Finset.mem_image.mpr ⟨q,hq,rfl⟩)

lemma residualCarryMinimum_nonpos (r : ℕ) : residualCarryMinimum r≤0 := by
  simpa only [residualCarryCost_zero] using
    residualCarryMinimum_le_in_range r 0 (residualCarryRange_zero r)

/-- No packet beyond the finite search can beat the constructed minimum. -/
theorem residualCarryMinimum_le (r q : ℕ) (hr : 0<r) :
    residualCarryMinimum r≤residualCarryCost r q := by
  by_cases hq : q∈residualCarryRange r
  · exact residualCarryMinimum_le_in_range r q hq
  · have hbound : (binaryDigitSum r-1)/3<q := by
      simpa only [residualCarryRange,Finset.mem_range,not_lt,Nat.succ_le_iff] using hq
    exact (residualCarryMinimum_nonpos r).trans (le_of_lt (residualCarryCost_positive_after r q hr hbound))

lemma residualCarryMinimum_attained (r : ℕ) :
    ∃ q∈residualCarryRange r, residualCarryCost r q=residualCarryMinimum r := by
  have h := Finset.min'_mem (residualCarryValues r) (residualCarryValues_nonempty r)
  exact Finset.mem_image.mp h

/-- All minimizing packet indices in the certified search range. -/
def residualMinimizers (r : ℕ) : Finset ℕ :=
  (residualCarryRange r).filter (fun q => residualCarryCost r q=residualCarryMinimum r)

lemma residualMinimizers_nonempty (r : ℕ) : (residualMinimizers r).Nonempty := by
  obtain ⟨q,hq,he⟩ := residualCarryMinimum_attained r
  exact ⟨q,Finset.mem_filter.mpr ⟨hq,he⟩⟩

/-- The last, not the first, globally minimizing packet. -/
def residualTerminalIndex (r : ℕ) : ℕ :=
  (residualMinimizers r).max' (residualMinimizers_nonempty r)

lemma residualTerminalIndex_mem (r : ℕ) : residualTerminalIndex r∈residualMinimizers r :=
  Finset.max'_mem _ _

theorem residualTerminalIndex_cost (r : ℕ) :
    residualCarryCost r (residualTerminalIndex r)=residualCarryMinimum r :=
  (Finset.mem_filter.mp (residualTerminalIndex_mem r)).2

theorem residualTerminalIndex_bound (r : ℕ) :
    residualTerminalIndex r≤(binaryDigitSum r-1)/3 := by
  have h := (Finset.mem_filter.mp (residualTerminalIndex_mem r)).1
  simpa only [residualCarryRange,Finset.mem_range,Nat.lt_succ_iff] using h

/-- The definition captures every global minimizer, including those not supplied by a caller. -/
theorem mem_residualMinimizers_iff (r q : ℕ) (hr : 0<r) :
    q∈residualMinimizers r ↔ residualCarryCost r q=residualCarryMinimum r := by
  constructor
  · exact fun h => (Finset.mem_filter.mp h).2
  · intro h
    apply Finset.mem_filter.mpr
    refine ⟨?_,h⟩
    have hb := residualCarryCost_nonpositive_bound r q hr (h.le.trans (residualCarryMinimum_nonpos r))
    simpa only [residualCarryRange,Finset.mem_range,Nat.lt_succ_iff] using hb

/-- Every later packet has strictly greater carry cost. -/
theorem residualCarryCost_after_terminal (r q : ℕ) (hr : 0<r)
    (hq : residualTerminalIndex r<q) : residualCarryMinimum r<residualCarryCost r q := by
  have hle := residualCarryMinimum_le r q hr
  by_contra hn
  have he : residualCarryCost r q=residualCarryMinimum r := by omega
  have hm := (mem_residualMinimizers_iff r q hr).mpr he
  have hb := Finset.le_max' (residualMinimizers r) q hm
  change q≤residualTerminalIndex r at hb
  omega

end Komorebi.Euler
