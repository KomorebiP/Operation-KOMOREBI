module
public import Euler.LocalRootTransport
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler

lemma dyadicBall_iff_residue (a x : D) (k : ℕ) :
    x∈dyadicBall a k ↔ redPow k x=redPow k a := by
  have hz : redPow k (x-a)=0 ↔ (2:D)^k ∣ x-a := by
    rw [← RingHom.mem_ker,PadicInt.ker_toZModPow,Ideal.mem_span_singleton]
    norm_num
  rw [← sub_eq_zero,← map_sub,hz]
  constructor
  · rintro ⟨y,rfl⟩
    exact ⟨y,by simp [dyadicChart]⟩
  · rintro ⟨y,hy⟩
    refine ⟨y,?_⟩
    simp only [dyadicChart]
    rw [← hy]
    ring

lemma dyadicBall_mono (a : D) {k m : ℕ} (h : k≤m) :
    dyadicBall a m⊆dyadicBall a k := by
  rintro x ⟨y,rfl⟩
  refine ⟨(2:D)^(m-k)*y,?_⟩
  unfold dyadicChart
  rw [← mul_assoc,← pow_add,Nat.add_sub_of_le h]

lemma dyadicBall_translate_center (a : D) (k : ℕ) (z : D) :
    dyadicBall (a+(2:D)^k*z) k=dyadicBall a k := by
  ext x
  rw [dyadicBall_iff_residue,dyadicBall_iff_residue]
  have hp : redPow k ((2:D)^k)=0 := by
    rw [map_pow]
    have ht : redPow k (2:D)=(2:ZMod (2^k)) := map_ofNat (redPow k) 2
    rw [ht]
    change ((2:ℕ):ZMod (2^k))^k=0
    rw [← Nat.cast_pow]
    exact ZMod.natCast_self _
  simp [hp]

lemma skeletonDepth_le (j i m : ℕ) (hm : 0 < m)
    (hi : i < 2^m) (hj : j-1-i < 2^m) : skeletonDepth j i≤m := by
  have hh : max i (j-1-i)<2^m := max_lt hi hj
  have hl := Nat.log_lt_of_lt_pow' (by omega : m≠0) hh
  unfold skeletonDepth
  omega

/-- The finite canonical separating balls cover the whole dyadic unit disc. -/
theorem skeleton_balls_cover (j : ℕ) (hj : 2≤j) (x : D) :
    ∃ i:ℕ, i < j ∧ x∈dyadicBall (i:D) (skeletonDepth j i) := by
  let m:=Nat.log 2 (j-1)
  let h:=2^m
  have hh : 0 < h := by dsimp [h];positivity
  have hlow : h<j := by
    have := Nat.pow_log_le_self 2 (show j-1≠0 by omega)
    change h≤j-1 at this
    omega
  have hupp : j≤2*h := by
    have := Nat.lt_pow_succ_log_self (by decide : 1<(2:ℕ)) (j-1)
    change j-1<2^(m+1) at this
    rw [pow_succ] at this
    change j-1<h*2 at this
    omega
  let u:ℕ:=(redPow (m+1) x).val
  have hu : u<2*h := by
    have ht := (redPow (m+1) x).val_lt
    change u<2^(m+1) at ht
    rw [pow_succ] at ht
    change u<h*2 at ht
    omega
  have hx : x∈dyadicBall (u:D) (m+1) := by
    rw [dyadicBall_iff_residue,map_natCast]
    exact (ZMod.natCast_zmod_val _).symm
  by_cases hij : u<j
  · refine ⟨u,hij,dyadicBall_mono _ ?_ hx⟩
    apply skeletonDepth_le j u (m+1) (by omega)
    · simpa only [pow_succ,show (2:ℕ)^m=h from rfl,Nat.mul_comm] using hu
    · have hlt : j-1-u<2*h := by omega
      simpa only [pow_succ,show (2:ℕ)^m=h from rfl,Nat.mul_comm] using hlt
  · have hju : j≤u := by omega
    let i:=u-h
    have hil : i<j := by dsimp [i];omega
    have him : i<h := by dsimp [i];omega
    have hjm : j-1-i<h := by dsimp [i];omega
    have hm : 0<m := by
      by_contra hn
      have hm0 : m=0 := by omega
      have hh1 : h=1 := by simp [h,hm0]
      omega
    have hik : skeletonDepth j i≤m := skeletonDepth_le j i m hm him hjm
    have hieq : (u:D)=(i:D)+(2:D)^m*1 := by
      have huhi : u=i+h := by dsimp [i];omega
      rw [huhi,Nat.cast_add]
      simp only [h,Nat.cast_pow,Nat.cast_ofNat,mul_one]
    refine ⟨i,hil,dyadicBall_mono _ hik ?_⟩
    have hx' := dyadicBall_mono (u:D) (by omega : m≤m+1) hx
    rw [hieq,dyadicBall_translate_center] at hx'
    exact hx'

/-- Any two distinct skeleton centers are farther apart than either separating scale. -/
lemma skeleton_difference_lt (j i l : ℕ) (hi : i < j) (hl : l < j) (hil : i<l) :
    0<l-i ∧ l-i<2^(skeletonDepth j i) ∧ l-i<2^(skeletonDepth j l) := by
  have h1 := (skeletonDepth_bounds j i).2
  have h2 := (skeletonDepth_bounds j l).1
  omega

/-- No dyadic point belongs to two different canonical skeleton balls. -/
theorem skeleton_balls_disjoint (j i l : ℕ) (hi : i < j) (hl : l < j) (hne : i≠l) :
    Disjoint (dyadicBall (i:D) (skeletonDepth j i))
      (dyadicBall (l:D) (skeletonDepth j l)) := by
  suffices hs : ∀ i l, i<j → l<j → i<l →
      ∀ x:D, x∈dyadicBall (i:D) (skeletonDepth j i) →
        x∈dyadicBall (l:D) (skeletonDepth j l) → False by
    rw [Set.disjoint_left]
    intro x hx hy
    rcases lt_or_gt_of_ne hne with h | h
    · exact hs i l hi hl h x hx hy
    · exact hs l i hl hi h x hy hx
  intro i l hi hl hil x hx hy
  let k:=min (skeletonDepth j i) (skeletonDepth j l)
  have hxk:=dyadicBall_mono (i:D) (min_le_left (skeletonDepth j i) (skeletonDepth j l)) hx
  have hyk:=dyadicBall_mono (l:D) (min_le_right (skeletonDepth j i) (skeletonDepth j l)) hy
  have he : redPow k (l:D)=redPow k (i:D) :=
    ((dyadicBall_iff_residue _ _ _).mp hyk).symm.trans
      ((dyadicBall_iff_residue _ _ _).mp hxk)
  have hz : ((l-i:ℕ):ZMod (2^k))=0 := by
    rw [Nat.cast_sub (by omega),← map_natCast (redPow k),← map_natCast (redPow k),he,sub_self]
  have hdvd : 2^k ∣ l-i := (ZMod.natCast_eq_zero_iff (l-i) (2^k)).mp hz
  have hlt := skeleton_difference_lt j i l hi hl hil
  have hklt : l-i<2^k := by
    dsimp [k]
    rcases le_total (skeletonDepth j i) (skeletonDepth j l) with h | h
    · simpa only [min_eq_left h] using hlt.2.1
    · simpa only [min_eq_right h] using hlt.2.2
  have := Nat.le_of_dvd hlt.1 hdvd
  omega

end Komorebi.Euler
