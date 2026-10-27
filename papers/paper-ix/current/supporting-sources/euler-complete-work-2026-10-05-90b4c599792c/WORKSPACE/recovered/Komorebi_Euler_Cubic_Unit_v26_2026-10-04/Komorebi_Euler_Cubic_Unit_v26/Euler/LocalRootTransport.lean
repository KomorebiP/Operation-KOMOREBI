module
public import Euler.SkeletonLocalEvaluation
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries

/-- Affine local coordinates, with the scaling retained rather than hidden in a root name. -/
def dyadicChart (a : D) (k : ℕ) (y : D) : D := a+(2:D)^k*y

def dyadicBall (a : D) (k : ℕ) : Set D := Set.range (dyadicChart a k)

lemma dyadicChart_injective (a : D) (k : ℕ) : Function.Injective (dyadicChart a k) := by
  intro x y he
  apply mul_left_cancel₀ (pow_ne_zero k (by norm_num : (2:D)≠0))
  exact add_left_cancel he

lemma dyadicChart_sub (a : D) (k : ℕ) (x y : D) :
    dyadicChart a k x-dyadicChart a k y=(2:D)^k*(x-y) := by
  simp only [dyadicChart]
  ring

/-- Transfer a complete affine coefficient certificate to a scaled analytic ball. -/
theorem restricted_scaled_root_atlas {g f : Series} (hg : Restricted g) (hf : Restricted f)
    (a : D) (k d : ℕ) (hk : 0 < k) (c : F₂)
    (hmap : PowerSeries.map red f=X+C c)
    (he : ∀ y:D, reval g (dyadicChart a k y)=(2:D)^(k+d)*reval f y) :
    ∃ α:D, α∈dyadicBall a k ∧ reval g α=0 ∧
      ‖deriv (qeval g) (α:ℚ_[2])‖=‖(2:D)^d‖ ∧
      (∀ x∈dyadicBall a k, reval g x=0 ↔ x=α) ∧
      (∀ x∈dyadicBall a k, ‖reval g x‖=‖(2:D)^d‖*‖x-α‖) := by
  obtain ⟨β,hβ,hβd,hu,hn⟩ := restricted_affine_atlas hf c hmap
  let α:=dyadicChart a k β
  have hscale : ‖(2:D)^k‖<1 := by
    rw [norm_pow,norm_two]
    exact pow_lt_one₀ (by norm_num) (by norm_num) (by omega)
  have hd := restricted_chart_derivative hg hf a ((2:D)^k) ((2:D)^(k+d)) hscale he β
  have hdc : deriv (qeval g) (α:ℚ_[2])=
      (2:ℚ_[2])^d*deriv (qeval f) (β:ℚ_[2]) := by
    apply mul_right_cancel₀ (pow_ne_zero k (by norm_num : (2:ℚ_[2])≠0))
    change deriv (qeval g) ((a+(2:D)^k*β:D):ℚ_[2])*(2:ℚ_[2])^k=_
    simpa only [PadicInt.coe_pow,PadicInt.coe_mul,show ((2:D):ℚ_[2])=(2:ℚ_[2]) from rfl,pow_add,
      mul_comm,mul_left_comm,mul_assoc] using hd
  refine ⟨α,⟨β,rfl⟩,?_,?_,?_,?_⟩
  · rw [he,hβ,mul_zero]
  · rw [hdc,norm_mul,hβd,mul_one]
    rfl
  · intro x hx
    obtain ⟨y,rfl⟩ := hx
    rw [he,mul_eq_zero]
    have hpow : (2:D)^(k+d)≠0 := pow_ne_zero _ (by norm_num)
    simp only [hpow,false_or,hu]
    exact ⟨fun h => by subst y; rfl,fun h => dyadicChart_injective a k h⟩
  · intro x hx
    obtain ⟨y,rfl⟩ := hx
    rw [he,norm_mul,hn,show dyadicChart a k y-α=(2:D)^k*(y-β) from
      dyadicChart_sub a k y β,norm_mul,pow_add,norm_mul]
    ring

/-- The root displacement is determined by the normalized chart's constant value. -/
theorem restricted_scaled_root_displacement {g f : Series} (hg : Restricted g)
    (hf : Restricted f) (a : D) (k d e : ℕ) (hk : 0 < k) (c : F₂)
    (hmap : PowerSeries.map red f=X+C c)
    (he : ∀ y:D, reval g (dyadicChart a k y)=(2:D)^(k+d)*reval f y)
    (hzero : ‖reval f 0‖=‖(2:D)^e‖) :
    ∃ α:D, α∈dyadicBall a k ∧ reval g α=0 ∧
      ‖α-a‖=‖(2:D)^(k+e)‖ := by
  obtain ⟨α,hαb,hα,_,_,hn⟩ := restricted_scaled_root_atlas hg hf a k d hk c hmap he
  have ha : a∈dyadicBall a k := ⟨0,by simp [dyadicChart]⟩
  have hna:=hn a ha
  have he0:=he 0
  simp only [dyadicChart,mul_zero,add_zero] at he0
  rw [he0,norm_mul,hzero] at hna
  have hnon : ‖(2:D)^d‖≠0 := norm_ne_zero_iff.mpr (pow_ne_zero d (by norm_num))
  have hz : ‖a-α‖=‖(2:D)^(k+e)‖ := by
    apply mul_left_cancel₀ hnon
    rw [← hna,pow_add,pow_add,norm_mul,norm_mul]
    ring
  exact ⟨α,hαb,hα,by simpa only [norm_sub_rev] using hz⟩

end Komorebi.Euler
