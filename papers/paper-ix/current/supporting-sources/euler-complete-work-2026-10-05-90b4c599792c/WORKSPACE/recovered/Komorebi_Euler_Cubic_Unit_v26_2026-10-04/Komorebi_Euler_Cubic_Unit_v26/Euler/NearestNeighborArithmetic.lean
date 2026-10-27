module
public import Euler.SkeletonArithmetic
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler

lemma skeletonDepth_ge_two (j i : ℕ) (hj:4≤j) (hi:i<j) :
    2≤skeletonDepth j i := by
  have hm : 2≤max i (j-1-i) := by omega
  have hl : 1≤Nat.log 2 (max i (j-1-i)) :=
    (Nat.le_log_iff_pow_le (by decide) (by omega)).mpr (by simpa using hm)
  unfold skeletonDepth
  omega

/-- The distance 2^(k-1) is the only positive distance less than 2^k
with valuation k-1.  All other distances gain at least two coefficient bits. -/
lemma skeleton_far_val_gap (n k:ℕ) (hk:0<k) (hn:0<n) (hb:n<2^k)
    (hne:n≠2^(k-1)) : padicValNat 2 n+2≤k := by
  have hv := skeletonVal_lt_of_lt_pow n k hn hb
  by_contra hgap
  have he : padicValNat 2 n=k-1 := by omega
  have hd : 2^(k-1)∣n := (padicValNat_dvd_iff_le (by omega : n≠0)).mpr (by omega)
  have hp : 2^k=2*2^(k-1) := by
    calc
      2^k = 2^((k-1)+1) := by congr 1; omega
      _ = 2*2^(k-1) := by rw [pow_succ]; omega
  have hsmall : n<2*2^(k-1) := by omega
  exact hne (Nat.eq_of_dvd_of_lt_two_mul (by omega) hd hsmall)

lemma skeleton_nearest_exists (j i : ℕ) (hj:2≤j) (hi:i<j) :
    (2^(skeletonDepth j i-1) ≤ i) ∨
    (2^(skeletonDepth j i-1) ≤ j-1-i) := by
  have hm : max i (j-1-i)≠0 := by omega
  have hp := Nat.pow_log_le_self 2 hm
  have hk : skeletonDepth j i-1=Nat.log 2 (max i (j-1-i)) := by
    simp [skeletonDepth]
  rw [hk]
  omega

lemma skeleton_near_val (k : ℕ) :
    padicValNat 2 (2^(k-1))=k-1 := by
  simp

lemma skeleton_near_oddPart (k : ℕ) :
    skeletonOddPart (2^(k-1))=1 := by
  have h := skeletonOddPart_factor (2^(k-1))
  rw [skeleton_near_val] at h
  have hp : 0<2^(k-1) := by positivity
  nlinarith

end Komorebi.Euler
