module
public import Euler.LocalAnalyticTools
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

/-- The shifted Hasse tail before the constant term is restored. -/
def lowerAffineTail (f : Series) (a : D) (k : ℕ) : Series :=
  mk (fun n => ((2:D)^k)^n * rjet (n+1) f a)

@[simp] lemma coeff_lowerAffineTail (f : Series) (a : D) (k n : ℕ) :
    coeff n (lowerAffineTail f a k)=((2:D)^k)^n*rjet (n+1) f a := by
  simp [lowerAffineTail]

lemma lowerAffineTail_restricted (f : Series) (a : D) (k : ℕ) (hk : 0<k) :
    Restricted (lowerAffineTail f a k) := by
  rw [restricted_iff]
  apply squeeze_zero (g := fun n => ‖(2:D)^k‖^n) (fun _ => norm_nonneg _)
  · intro n
    rw [coeff_lowerAffineTail,norm_mul,norm_pow]
    exact mul_le_of_le_one_right (by positivity) (PadicInt.norm_le_one _)
  · apply tendsto_pow_atTop_nhds_zero_of_lt_one (norm_nonneg _)
    rw [norm_pow,norm_two]
    exact pow_lt_one₀ (by norm_num) (by norm_num) (by omega)

lemma lowerAffineTail_red (f : Series) (a : D) (k : ℕ) (hk : 0<k) :
    PowerSeries.map red (lowerAffineTail f a k)=C (red (rjet 1 f a)) := by
  ext n
  cases n with
  | zero => simp [coeff_lowerAffineTail]
  | succ n => simp [coeff_lowerAffineTail,map_mul,map_pow,show k≠0 by omega]

/-- The integral chart obtained after an exact known center content is removed.
The constant w is constrained by f(a)=2^s*w in the evaluation theorem below. -/
def normalizedLowerChart (f : Series) (a : D) (k s : ℕ) (w : D) : Series :=
  C w+C ((2:D)^(k-s))*X*lowerAffineTail f a k

lemma normalizedLowerChart_restricted (f : Series) (a : D) (k s : ℕ) (w : D)
    (hk : 0<k) : Restricted (normalizedLowerChart f a k s w) := by
  unfold normalizedLowerChart
  exact PowerSeries.isRestricted.add 1 (PowerSeries.isRestricted_C 1 _)
    (PowerSeries.isRestricted.mul 1
      (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _)
        (by simpa using polynomial_restricted (Polynomial.X:Polynomial D)))
      (lowerAffineTail_restricted f a k hk))

/-- Coefficientwise exact normalization, including the infinite Taylor tail. -/
theorem normalizedLowerChart_identity (f : Series) (a : D) (k s : ℕ) (w : D)
    (hs : s≤k) (hw : reval f a=(2:D)^s*w) :
    C ((2:D)^s)*normalizedLowerChart f a k s w=
      restrictedAffine f a ((2:D)^k) := by
  ext n
  cases n with
  | zero => simp [normalizedLowerChart,coeff_restrictedAffine,rjet_zero,hw]
  | succ n =>
    simp only [normalizedLowerChart,mul_assoc,map_add,coeff_C,coeff_C_mul,
      coeff_succ_X_mul,coeff_lowerAffineTail,coeff_restrictedAffine,Nat.succ_ne_zero,
      ite_false,zero_add]
    rw [← mul_assoc,← mul_assoc,← pow_add,Nat.add_sub_of_le hs,pow_succ]
    ring

/-- The normalized chart evaluates the original function, with no formal composition shortcut. -/
theorem normalizedLowerChart_reval {f : Series} (hf : Restricted f) (a : D)
    (k s : ℕ) (w : D) (hk : 0<k) (hs : s≤k)
    (hw : reval f a=(2:D)^s*w) (y : D) :
    reval f (a+(2:D)^k*y)=(2:D)^s*reval (normalizedLowerChart f a k s w) y := by
  rw [← restrictedAffine_reval hf a ((2:D)^k) y,
    ← normalizedLowerChart_identity f a k s w hs hw,
    reval_C_mul (normalizedLowerChart_restricted f a k s w hk)]

lemma normalizedLowerChart_red_shallow (f : Series) (a : D) (k s : ℕ) (w : D)
    (hs : s<k) :
    PowerSeries.map red (normalizedLowerChart f a k s w)=C (red w) := by
  rw [normalizedLowerChart,map_add,map_mul,map_mul,map_C,map_C,map_pow,
    red_two,zero_pow (by omega : k-s≠0),map_zero,zero_mul,zero_mul,add_zero]

lemma normalizedLowerChart_red_root (f : Series) (a : D) (k : ℕ) (w : D)
    (hk : 0<k) (hd : red (rjet 1 f a)=1) :
    PowerSeries.map red (normalizedLowerChart f a k k w)=X+C (red w) := by
  rw [normalizedLowerChart,map_add,map_mul,map_mul,map_C,map_X,
    lowerAffineTail_red f a k hk,hd,map_one]
  simp [add_comm]

/-- A center divisible by its ball radius, with odd slope, has a unique simple lower root. -/
theorem normalizedLowerChart_root_atlas (f : Series)
    (a : D) (k : ℕ) (w : D) (hk : 0<k) (hd : red (rjet 1 f a)=1) :
    ∃ z:D, reval (normalizedLowerChart f a k k w) z=0 ∧
      ‖deriv (qeval (normalizedLowerChart f a k k w)) (z:ℚ_[2])‖=1 ∧
      (∀ y:D, reval (normalizedLowerChart f a k k w) y=0 ↔ y=z) ∧
      (∀ y:D, ‖reval (normalizedLowerChart f a k k w) y‖=‖y-z‖) := by
  exact restricted_affine_atlas (normalizedLowerChart_restricted f a k k w hk)
    (red w) (normalizedLowerChart_red_root f a k w hk hd)

end Komorebi.Euler
