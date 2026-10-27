module
public import KummerSequences
public import HurwitzDworkClosure
public import ExponentialSection
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.DyadicFourKernel
open PowerSeries KummerSequences

/-- Every denominator is an actual odd 2-adic unit. -/
theorem affine_isUnit (a b n:ℕ) : IsUnit (((2*a*n+(2*b+1)):ℕ):ℤ_[2]) := by
  rw [PadicInt.isUnit_iff,PadicInt.norm_natCast_eq_one_iff]
  apply Nat.prime_two.coprime_iff_not_dvd.mpr
  simp [Nat.dvd_iff_mod_eq_zero,Nat.add_mod,Nat.mul_mod]

def affineUnit (a b n:ℕ) : ℤ_[2]ˣ := (affine_isUnit a b n).unit
@[simp] theorem affineUnit_coe (a b n:ℕ) :
    (affineUnit a b n:ℤ_[2]) = ((2*a*n+(2*b+1):ℕ):ℤ_[2]) :=
  (affine_isUnit a b n).unit_spec

def invAffine (a b n:ℕ) : ℤ_[2] := ((affineUnit a b n)⁻¹:ℤ_[2]ˣ)

theorem invAffine_cancel (a b n:ℕ) :
    ((2*a:ℕ):ℤ_[2])*(n:ℤ_[2])*invAffine a b n +
      ((2*b+1:ℕ):ℤ_[2])*invAffine a b n=1 := by
  rw [←add_mul]
  have he : ((2*a:ℕ):ℤ_[2])*(n:ℤ_[2])+((2*b+1:ℕ):ℤ_[2]) =
      (affineUnit a b n:ℤ_[2]) := by simp only [affineUnit_coe,Nat.cast_add,Nat.cast_mul]
  rw [he,invAffine]
  simp

theorem invAffine_coe (a b n:ℕ) :
    (invAffine a b n:ℚ_[2]) = (((2*a*n+(2*b+1):ℕ):ℚ_[2]))⁻¹ := by
  have he := invAffine_cancel a b n
  have hc := congrArg (fun x:ℤ_[2] => (x:ℚ_[2])) he
  change ((2*a:ℕ):ℚ_[2])*(n:ℚ_[2])*(invAffine a b n:ℚ_[2])+
    ((2*b+1:ℕ):ℚ_[2])*(invAffine a b n:ℚ_[2])=1 at hc
  rw [←add_mul] at hc
  have hz : ((2*a:ℕ):ℚ_[2])*(n:ℚ_[2])+((2*b+1:ℕ):ℚ_[2])≠0 := by
    have hn : 2*a*n+(2*b+1) ≠0 := by omega
    exact_mod_cast hn
  have h : (invAffine a b n:ℚ_[2]) =
      (((2*a:ℕ):ℚ_[2])*(n:ℚ_[2])+((2*b+1:ℕ):ℚ_[2]))⁻¹ :=
    (mul_eq_one_iff_eq_inv₀ hz).mp (by rw [mul_comm]; exact hc)
  simpa only [Nat.cast_add,Nat.cast_mul] using h

theorem invAffine_kummer (a b:ℕ) : Kummer (2:ℤ_[2]) (invAffine a b) := by
  apply kummer_inverse (2:ℤ_[2]) (fun n => ((2*a:ℕ):ℤ_[2])*(n:ℤ_[2])+((2*b+1:ℕ):ℤ_[2]))
  · intro n; simpa only [add_mul,mul_assoc] using invAffine_cancel a b n
  · apply affine_kummer
    exact ⟨(a:ℤ_[2]), by simp⟩

/-- The four normalized source sequences, built from explicit odd affine inverses. -/
def sourcePacket (j:ℕ) : ℕ→ℤ_[2] :=
  match j with
  | 0 => fun _ => 1
  | 1 => invAffine 2 0
  | 2 => fun n => invAffine 2 0 n*invAffine 1 0 n
  | _ => fun n => (3:ℤ_[2])*(invAffine 2 0 n*invAffine 1 0 n*invAffine 2 1 n)

theorem source_kummer (j:ℕ) : Kummer (2:ℤ_[2]) (sourcePacket j) := by
  cases j with
  | zero => exact constant_kummer _ _
  | succ j =>
    cases j with
    | zero => exact invAffine_kummer _ _
    | succ j =>
      cases j with
      | zero => exact kummer_mul _ (invAffine_kummer _ _) (invAffine_kummer _ _)
      | succ j => exact kummer_mul _ (constant_kummer _ _) (kummer_mul _
          (kummer_mul _ (invAffine_kummer _ _) (invAffine_kummer _ _)) (invAffine_kummer _ _))

/-- The explicit sources are identified with the original binomial denominator, not renamed. -/
theorem source_coe (j n:ℕ) (hj:j<4) :
    (sourcePacket j n:ℚ_[2]) = (((4*n+j).choose (4*n):ℕ):ℚ_[2])⁻¹ := by
  have h2 : (((4*n+2).choose (4*n):ℕ):ℚ_[2]) = (4*(n:ℚ_[2])+1)*(2*(n:ℚ_[2])+1) := by
    have h := Nat.choose_mul_succ_eq (4*n+1) (4*n)
    rw [Nat.choose_succ_self_right,show 4*n+1+1-4*n=2 by omega] at h
    have hq := congrArg (fun a:ℕ => (a:ℚ_[2])) h
    norm_num only [Nat.cast_mul,Nat.cast_add,Nat.cast_one,Nat.cast_ofNat] at hq
    change (4*(n:ℚ_[2])+1)*(4*(n:ℚ_[2])+1+1) =
      (((4*n+2).choose (4*n):ℕ):ℚ_[2])*2 at hq
    linear_combination -hq/2
  have h3 : (3:ℚ_[2])*(((4*n+3).choose (4*n):ℕ):ℚ_[2]) =
      (4*(n:ℚ_[2])+1)*(2*(n:ℚ_[2])+1)*(4*(n:ℚ_[2])+3) := by
    have h := Nat.choose_mul_succ_eq (4*n+2) (4*n)
    rw [show 4*n+2+1-4*n=3 by omega] at h
    have hq := congrArg (fun a:ℕ => (a:ℚ_[2])) h
    norm_num only [Nat.cast_mul,Nat.cast_add,Nat.cast_one,Nat.cast_ofNat] at hq
    change (((4*n+2).choose (4*n):ℕ):ℚ_[2])*(4*(n:ℚ_[2])+2+1) =
      (((4*n+3).choose (4*n):ℕ):ℚ_[2])*3 at hq
    rw [h2] at hq
    linear_combination -hq
  have h1n : (4*(n:ℚ_[2])+1)≠0 := by exact_mod_cast (show 4*n+1≠0 by omega)
  have h2n : (2*(n:ℚ_[2])+1)≠0 := by exact_mod_cast (show 2*n+1≠0 by omega)
  have h3n : (4*(n:ℚ_[2])+3)≠0 := by exact_mod_cast (show 4*n+3≠0 by omega)
  interval_cases j
  · simp [sourcePacket]
  · simp only [sourcePacket,invAffine_coe,Nat.choose_succ_self_right]
  · simp only [sourcePacket,PadicInt.coe_mul,invAffine_coe]
    norm_num only [Nat.mul_zero,Nat.zero_add,Nat.reduceMul,Nat.cast_add,Nat.cast_mul,Nat.cast_ofNat] 
    rw [h2,mul_inv_rev]
    ring
  · simp only [sourcePacket,PadicInt.coe_mul,invAffine_coe]
    norm_num only [Nat.mul_zero,Nat.zero_add,Nat.reduceMul,Nat.cast_add,Nat.cast_mul,Nat.cast_ofNat,Nat.reduceAdd]
    have hc: (((4*n+3).choose (4*n):ℕ):ℚ_[2])≠0 :=
      Nat.cast_ne_zero.mpr (Nat.choose_ne_zero (by omega))
    change (3:ℚ_[2])*((4*(n:ℚ_[2])+1)⁻¹*(2*(n:ℚ_[2])+1)⁻¹*
      (4*(n:ℚ_[2])+3)⁻¹) = (((4*n+3).choose (4*n):ℕ):ℚ_[2])⁻¹
    apply (mul_eq_one_iff_eq_inv₀ hc).mp
    calc
      _ = (3*(((4*n+3).choose (4*n):ℕ):ℚ_[2])) *
        ((4*(n:ℚ_[2])+1)⁻¹*(2*(n:ℚ_[2])+1)⁻¹*(4*(n:ℚ_[2])+3)⁻¹) := by ring
      _ = _ := by rw [h3]
      _ = ((4*(n:ℚ_[2])+1)*(4*(n:ℚ_[2])+1)⁻¹)*
        ((2*(n:ℚ_[2])+1)*(2*(n:ℚ_[2])+1)⁻¹)*
        ((4*(n:ℚ_[2])+3)*(4*(n:ℚ_[2])+3)⁻¹) := by ring
      _ = 1 := by rw [mul_inv_cancel₀ h1n,mul_inv_cancel₀ h2n,mul_inv_cancel₀ h3n]; ring
end KomorebiPaperIX.DyadicFourKernel
