module
public import Euler.TerminalCoordinates
@[expose] public section
noncomputable section
namespace Komorebi.Euler

/-- The finite lower minimum includes the constant packet. The zero label is harmless. -/
def terminalLowerRange (j : ℕ) : Finset ℕ := Finset.range (max j 1)

lemma terminalLowerRange_nonempty (j : ℕ) : (terminalLowerRange j).Nonempty := by
  refine ⟨0,?_⟩
  simp [terminalLowerRange]

/-- Minimum of the lower packet costs, independent of the multiplier. -/
def terminalLowerMinimum (j : ℕ) : ℤ :=
  ((terminalLowerRange j).image (terminalLowerCost j)).min'
    ((terminalLowerRange_nonempty j).image _)

lemma terminalLowerMinimum_le (j q : ℕ) (hq : q<j) :
    terminalLowerMinimum j≤terminalLowerCost j q := by
  apply Finset.min'_le
  exact Finset.mem_image.mpr ⟨q,Finset.mem_range.mpr (by omega),rfl⟩

lemma terminalLowerMinimum_attained (j : ℕ) (hj : 0<j) :
    ∃ q<j, terminalLowerCost j q=terminalLowerMinimum j := by
  have h := Finset.min'_mem ((terminalLowerRange j).image (terminalLowerCost j))
    ((terminalLowerRange_nonempty j).image _)
  obtain ⟨q,hq,he⟩ := Finset.mem_image.mp h
  refine ⟨q,?_,he⟩
  simpa only [terminalLowerRange,Finset.mem_range,max_eq_left (by omega : 1≤j)] using hq

lemma terminalLowerMinimum_nonpos (j : ℕ) (hj : 0<j) :
    terminalLowerMinimum j≤0 := by
  simpa only [terminalLowerCost_zero] using terminalLowerMinimum_le j 0 hj

/-- The origin of a wall is a natural number; no negative cutoffs are truncated. -/
def terminalWallOrigin (j : ℕ) : ℕ :=
  (3*(j:ℤ)+1+(binaryDigitSum (j-1):ℤ)-terminalLowerMinimum j).toNat

lemma terminalWallOrigin_cast (j : ℕ) (hj : 0<j) :
    (terminalWallOrigin j:ℤ)=
      3*(j:ℤ)+1+(binaryDigitSum (j-1):ℤ)-terminalLowerMinimum j := by
  apply Int.toNat_of_nonneg
  have h := terminalLowerMinimum_nonpos j hj
  omega

lemma residualCarryMinimum_le_lower (r : ℕ) (hr : 0<r)
    (hj : 0<residualTerminalIndex r) :
    residualCarryMinimum r≤terminalLowerMinimum (residualTerminalIndex r) := by
  obtain ⟨q,hq,he⟩ := terminalLowerMinimum_attained (residualTerminalIndex r) hj
  rw [← he,← residualCarryCost_before_terminal r q hr hq]
  exact residualCarryMinimum_le r q hr

/-- The canonical carry scale is never before its lower-packet wall. -/
theorem terminalWallOrigin_le_exponent (r : ℕ) (hr : 0<r)
    (hj : 0<residualTerminalIndex r) :
    terminalWallOrigin (residualTerminalIndex r)≤terminalWallExponent r := by
  have hm := residualCarryMinimum_le_lower r hr hj
  rw [residualCarryMinimum_wall r hr hj] at hm
  have ho := terminalWallOrigin_cast (residualTerminalIndex r) hj
  omega

def terminalWallDistance (r : ℕ) : ℕ :=
  terminalWallExponent r-terminalWallOrigin (residualTerminalIndex r)

lemma terminalWallExponent_eq (r : ℕ) (hr : 0<r)
    (hj : 0<residualTerminalIndex r) :
    terminalWallExponent r=
      terminalWallOrigin (residualTerminalIndex r)+terminalWallDistance r := by
  have h := terminalWallOrigin_le_exponent r hr hj
  dsimp [terminalWallDistance]
  omega

/-- Exact carry normalization in wall-distance coordinates. -/
theorem residualCarryMinimum_eq_lower_sub_distance (r : ℕ) (hr : 0<r)
    (hj : 0<residualTerminalIndex r) :
    residualCarryMinimum r=
      terminalLowerMinimum (residualTerminalIndex r)-(terminalWallDistance r:ℤ) := by
  rw [residualCarryMinimum_wall r hr hj,terminalWallExponent_eq r hr hj,
    Nat.cast_add,terminalWallOrigin_cast _ hj]
  ring

/-- Euler wall coordinates with a proved nonnegative distance. -/
theorem terminalWall_full_representation (r : ℕ) (hr : 0<r)
    (hj : 0<residualTerminalIndex r) :
    r=terminalWallMultiplier r*
      2^(terminalWallOrigin (residualTerminalIndex r)+terminalWallDistance r)-
      residualTerminalIndex r := by
  rw [← terminalWallExponent_eq r hr hj]
  exact (terminalWall_representation r hr).1

/-- Binary complexity separates terminal degree, wall distance, and the odd address. -/
theorem terminalWall_binary_complexity (r : ℕ) (hr : 0<r)
    (hj : 0<residualTerminalIndex r) :
    (binaryDigitSum r:ℤ)=
      (binaryDigitSum (terminalWallMultiplier r):ℤ)+3*(residualTerminalIndex r:ℤ)-
      terminalLowerMinimum (residualTerminalIndex r)+(terminalWallDistance r:ℤ) := by
  have hs := terminalWall_digit_sum r hr hj
  have he := terminalWallExponent_eq r hr hj
  have ho := terminalWallOrigin_cast (residualTerminalIndex r) hj
  omega

/-- At a positive wall distance the terminal packet is the unique minimizer. -/
theorem residualMinimizers_singleton_of_distance_pos (r : ℕ) (hr : 0<r)
    (hj : 0<residualTerminalIndex r) (hd : 0<terminalWallDistance r) :
    residualMinimizers r={residualTerminalIndex r} := by
  ext q
  rw [mem_residualMinimizers_iff r q hr,Finset.mem_singleton]
  constructor
  · intro hq
    have hle : q≤residualTerminalIndex r := by
      by_contra hn
      have hh := residualCarryCost_after_terminal r q hr (by omega)
      omega
    by_contra hn
    have hlt : q<residualTerminalIndex r := by omega
    have hh := terminalLowerMinimum_le (residualTerminalIndex r) q hlt
    rw [← residualCarryCost_before_terminal r q hr hlt,hq,
      residualCarryMinimum_eq_lower_sub_distance r hr hj] at hh
    omega
  · rintro rfl
    exact residualTerminalIndex_cost r

/-- At equality, all and only the lower ties join the terminal packet. -/
theorem residualMinimizers_wall_iff (r q : ℕ) (hr : 0<r)
    (hj : 0<residualTerminalIndex r) :
    q∈residualMinimizers r ↔ q=residualTerminalIndex r ∨
      (q<residualTerminalIndex r ∧ terminalWallDistance r=0 ∧
        terminalLowerCost (residualTerminalIndex r) q=
          terminalLowerMinimum (residualTerminalIndex r)) := by
  rw [mem_residualMinimizers_iff r q hr]
  constructor
  · intro hq
    by_cases he : q=residualTerminalIndex r
    · exact Or.inl he
    have hlt : q<residualTerminalIndex r := by
      by_contra hn
      have h := residualCarryCost_after_terminal r q hr (by omega)
      omega
    have hlow := terminalLowerMinimum_le (residualTerminalIndex r) q hlt
    have hc := residualCarryCost_before_terminal r q hr hlt
    have hm := residualCarryMinimum_eq_lower_sub_distance r hr hj
    exact Or.inr ⟨hlt,by omega,by omega⟩
  · rintro (rfl | ⟨hq,hd,he⟩)
    · exact residualTerminalIndex_cost r
    · rw [residualCarryCost_before_terminal r q hr hq,he,
        residualCarryMinimum_eq_lower_sub_distance r hr hj,hd,Nat.cast_zero,sub_zero]

end Komorebi.Euler
