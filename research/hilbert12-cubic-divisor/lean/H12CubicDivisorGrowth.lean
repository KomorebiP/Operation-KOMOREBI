import H12PrincipalDivisor

/-! Universal arithmetic certificates for cubic divisor growth.
These are coefficient facts; no gamma, complex-order, theta-growth,
convergence, or arithmetic special-value equality is assumed here.
-/
namespace H12CubicDivisorGrowth
open H12PrincipalDivisor

theorem positive_pivot (b c : Int) (h : 2*b < 3*c) : 0 < pivot b c := by
  unfold pivot
  omega

theorem chamber_wall (a b j : Int) (ha : a ≤ 0) (hb : 0 < b) (hj : 0 < j) :
    wall a b j = 1 := by
  unfold wall step
  split <;> split <;> split <;> omega

theorem chamber_order (a b c : Int) (ha : a ≤ 0) (hb : 0 < b)
    (hc : 2*b < 3*c) : correctionOrder a b c = weight c := by
  have hp := positive_pivot b c hc
  simp [correctionOrder,chamber_wall a b (pivot b c) ha hb hp]

def zeroPoint (n i j k : Int) : V := (-i,j,5*(n+k))
def polePoint (n i j k r : Int) : V := (-i,j,5*(n+k)-r)

theorem zero_family_order (n i j k : Int) (hn : 0 < n)
    (hi : 0 < i) (hj : 0 < j) (hjn : j ≤ n) (hk : 0 < k) :
    correctionOrder (-i) j (5*(n+k)) = 4 := by
  rw [chamber_order (-i) j (5*(n+k)) (by omega) hj (by omega)]
  have hr : (5*(n+k))%5=0 := by omega
  simp [weight,hr]

theorem pole_family_order (n i j k r : Int) (hn : 0 < n)
    (hi : 0 < i) (hj : 0 < j) (hjn : j ≤ n) (hk : 0 < k)
    (hr : 1 ≤ r) (hr4 : r ≤ 4) :
    correctionOrder (-i) j (5*(n+k)-r) = -1 := by
  rw [chamber_order (-i) j (5*(n+k)-r) (by omega) hj (by omega)]
  unfold weight
  split <;> omega

theorem zero_family_injective (n i j k i' j' k' : Int)
    (h : zeroPoint n i j k = zeroPoint n i' j' k') :
    i=i' ∧ j=j' ∧ k=k' := by
  have h0 := congrArg Prod.fst h
  have h1 := congrArg (fun v : V => v.2.1) h
  have h2 := congrArg (fun v : V => v.2.2) h
  simp [zeroPoint] at h0 h1 h2
  omega

theorem pole_family_injective (n i j k r i' j' k' r' : Int)
    (hr : 1 ≤ r) (hr4 : r ≤ 4) (hr' : 1 ≤ r') (hr4' : r' ≤ 4)
    (h : polePoint n i j k r = polePoint n i' j' k' r') :
    i=i' ∧ j=j' ∧ k=k' ∧ r=r' := by
  have h0 := congrArg Prod.fst h
  have h1 := congrArg (fun v : V => v.2.1) h
  have h2 := congrArg (fun v : V => v.2.2) h
  simp [polePoint] at h0 h1 h2
  omega

theorem families_disjoint (n i j k i' j' k' r : Int)
    (hr : 1 ≤ r) (hr4 : r ≤ 4) :
    zeroPoint n i j k ≠ polePoint n i' j' k' r := by
  intro h
  have h2 := congrArg (fun v : V => v.2.2) h
  simp [zeroPoint,polePoint] at h2
  omega

theorem zero_box_bounds (n i j k : Int) (_hn : 1 ≤ n)
    (hi : 1 ≤ i) (hin : i ≤ n) (hj : 1 ≤ j) (hjn : j ≤ n)
    (hk : 1 ≤ k) (hkn : k ≤ n) :
    -n ≤ (zeroPoint n i j k).1 ∧ (zeroPoint n i j k).1 < 0 ∧
    0 < (zeroPoint n i j k).2.1 ∧ (zeroPoint n i j k).2.1 ≤ n ∧
    5*n < (zeroPoint n i j k).2.2 ∧ (zeroPoint n i j k).2.2 ≤ 10*n := by
  simp [zeroPoint]
  omega

theorem pole_box_bounds (n i j k r : Int) (_hn : 1 ≤ n)
    (hi : 1 ≤ i) (hin : i ≤ n) (hj : 1 ≤ j) (hjn : j ≤ n)
    (hk : 1 ≤ k) (hkn : k ≤ n) (hr : 1 ≤ r) (hr4 : r ≤ 4) :
    -n ≤ (polePoint n i j k r).1 ∧ (polePoint n i j k r).1 < 0 ∧
    0 < (polePoint n i j k r).2.1 ∧ (polePoint n i j k r).2.1 ≤ n ∧
    5*n < (polePoint n i j k r).2.2 ∧ (polePoint n i j k r).2.2 < 10*n := by
  simp [polePoint]
  omega

theorem origin_not_in_families (n i j k r : Int) (hi : 0 < i) :
    zeroPoint n i j k ≠ (0,0,0) ∧ polePoint n i j k r ≠ (0,0,0) := by
  constructor <;> intro h
  all_goals
    have hh := congrArg Prod.fst h
    simp [zeroPoint,polePoint] at hh
    omega

end H12CubicDivisorGrowth
