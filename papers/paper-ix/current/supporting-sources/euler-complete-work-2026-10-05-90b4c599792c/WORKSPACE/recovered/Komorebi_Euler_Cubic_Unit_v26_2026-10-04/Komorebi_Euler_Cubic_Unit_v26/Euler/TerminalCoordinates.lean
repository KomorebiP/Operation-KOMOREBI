module
public import Euler.BinaryWallArithmetic
public import Euler.ResidualMinimum
@[expose] public section
noncomputable section
namespace Komorebi.Euler

/-- Exact power of two at the last globally minimizing packet. -/
def terminalWallExponent (r : ℕ) : ℕ :=
  padicValNat 2 (r+residualTerminalIndex r)

/-- Actual odd part, not an assumed wall parameter. -/
def terminalWallMultiplier (r : ℕ) : ℕ :=
  (r+residualTerminalIndex r).divMaxPow 2

lemma terminalWall_factor (r : ℕ) :
    terminalWallMultiplier r*2^(terminalWallExponent r)=r+residualTerminalIndex r :=
  Nat.divMaxPow_mul_pow_padicValNat _ _

lemma terminalWallMultiplier_odd (r : ℕ) (hr : 0<r) :
    terminalWallMultiplier r % 2=1 := by
  have h : ¬2∣terminalWallMultiplier r :=
    Nat.not_dvd_divMaxPow (by decide) (by omega)
  have hn : terminalWallMultiplier r % 2≠0 := by
    simpa only [Nat.dvd_iff_mod_eq_zero] using h
  omega

lemma terminalWallMultiplier_pos (r : ℕ) (hr : 0<r) :
    0<terminalWallMultiplier r := by
  have h := terminalWallMultiplier_odd r hr
  omega

/-- The last minimum lies strictly before the next full binary block. -/
theorem residualTerminalIndex_lt_wallPower (r : ℕ) (hr : 0<r) :
    residualTerminalIndex r < 2^(terminalWallExponent r) := by
  let j:=residualTerminalIndex r
  let L:=terminalWallExponent r
  let b:=terminalWallMultiplier r
  have hb : b%2=1 := terminalWallMultiplier_odd r hr
  have hbpos : 0<b := terminalWallMultiplier_pos r hr
  have he : b*2^L=r+j := terminalWall_factor r
  have hp : 0<2^L := by positivity
  by_contra hn
  change ¬j<2^L at hn
  have hjp : 2^L≤j := by omega
  have hm : b*2^L=(b-1)*2^L+2^L := by
    rw [← Nat.succ_mul]
    congr 1
    omega
  have heq : r+(j-2^L)=(b-1)*2^L := by omega
  have hsj : binaryDigitSum (r+j)=binaryDigitSum b := by
    rw [← he,binaryDigitSum_mul_pow]
  have hs0 : binaryDigitSum (r+(j-2^L))=binaryDigitSum (b-1) := by
    rw [heq,binaryDigitSum_mul_pow]
  have hs := binaryDigitSum_odd b hb
  have hmin := residualCarryMinimum_le r (j-2^L) hr
  have ht : residualCarryCost r j=residualCarryMinimum r := residualTerminalIndex_cost r
  unfold residualCarryCost at ht hmin
  rw [hsj] at ht
  rw [hs0] at hmin
  omega

/-- Canonical wall coordinates of the constructed carry minimum. -/
theorem terminalWall_representation (r : ℕ) (hr : 0<r) :
    r=terminalWallMultiplier r*2^(terminalWallExponent r)-residualTerminalIndex r ∧
    terminalWallMultiplier r%2=1 ∧
    residualTerminalIndex r<2^(terminalWallExponent r) := by
  refine ⟨?_,terminalWallMultiplier_odd r hr,residualTerminalIndex_lt_wallPower r hr⟩
  rw [terminalWall_factor,Nat.add_sub_cancel]

lemma terminalWall_digit_sum (r : ℕ) (hr : 0<r)
    (hj : 0<residualTerminalIndex r) :
    binaryDigitSum r+binaryDigitSum (residualTerminalIndex r-1)+1=
      binaryDigitSum (terminalWallMultiplier r)+terminalWallExponent r := by
  have h := binaryDigitSum_wall (terminalWallMultiplier r) (terminalWallExponent r)
    (residualTerminalIndex r) (terminalWallMultiplier_odd r hr) hj
    (residualTerminalIndex_lt_wallPower r hr)
  rw [terminalWall_factor,Nat.add_sub_cancel] at h
  exact h

/-- Every lower packet has a carry cost depending only on the terminal label. -/
def terminalLowerCost (j q : ℕ) : ℤ :=
  3*(q:ℤ)+(binaryDigitSum (j-1):ℤ)-(binaryDigitSum (j-q-1):ℤ)

@[simp] lemma terminalLowerCost_zero (j : ℕ) : terminalLowerCost j 0=0 := by
  simp [terminalLowerCost]

lemma residualCarryCost_before_terminal (r q : ℕ) (hr : 0<r)
    (hq : q<residualTerminalIndex r) :
    residualCarryCost r q=terminalLowerCost (residualTerminalIndex r) q := by
  let j:=residualTerminalIndex r
  let L:=terminalWallExponent r
  let b:=terminalWallMultiplier r
  have hp : j<2^L := residualTerminalIndex_lt_wallPower r hr
  have he : b*2^L=r+j := terminalWall_factor r
  have hs := binaryDigitSum_wall b L (j-q) (terminalWallMultiplier_odd r hr)
    (by dsimp [j];omega) (by dsimp [j] at *;omega)
  have heq : b*2^L-(j-q)=r+q := by dsimp [j] at *;omega
  rw [heq] at hs
  have hs0 := terminalWall_digit_sum r hr (by omega)
  unfold residualCarryCost terminalLowerCost
  dsimp [j,L,b] at hs
  omega

/-- Exact value of the minimum in its binary wall coordinates. -/
theorem residualCarryMinimum_wall (r : ℕ) (hr : 0<r)
    (hj : 0<residualTerminalIndex r) :
    residualCarryMinimum r=
      3*(residualTerminalIndex r:ℤ)+1+
      (binaryDigitSum (residualTerminalIndex r-1):ℤ)-(terminalWallExponent r:ℤ) := by
  have hs := terminalWall_digit_sum r hr hj
  have he : binaryDigitSum (r+residualTerminalIndex r)=
      binaryDigitSum (terminalWallMultiplier r) := by
    rw [← terminalWall_factor,binaryDigitSum_mul_pow]
  have ht := residualTerminalIndex_cost r
  unfold residualCarryCost at ht
  rw [he] at ht
  omega

end Komorebi.Euler
