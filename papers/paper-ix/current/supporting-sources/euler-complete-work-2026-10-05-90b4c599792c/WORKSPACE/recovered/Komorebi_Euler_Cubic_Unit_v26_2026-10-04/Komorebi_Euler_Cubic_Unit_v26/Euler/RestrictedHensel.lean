module
public import Euler.RestrictedCalculus
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

abbrev res : D →+* F₂ := redPow 1

lemma res_zero_iff_norm_le_half (x : D) : res x=0 ↔ ‖x‖≤(1/2:ℝ) := by
  simpa using redPow_zero_iff_norm 1 x

lemma res_zero_iff_norm_lt_one (x : D) : res x=0 ↔ ‖x‖<1 := by
  have h := PadicInt.norm_le_pow_iff_norm_lt_pow_add_one (p:=2) x (-1)
  norm_num at h
  exact (res_zero_iff_norm_le_half x).trans h

lemma res_nonzero_norm_one (x : D) (h : res x ≠ 0) : ‖x‖=1 := by
  apply le_antisymm (PadicInt.norm_le_one _)
  apply le_of_not_gt
  intro hn
  exact h ((res_zero_iff_norm_lt_one x).mpr hn)

lemma norm_sub_le_half_of_res_eq {x y : D} (h : res x=res y) :
    ‖x-y‖≤(1/2:ℝ) := by
  apply (res_zero_iff_norm_le_half _).mp
  simp only [map_sub, h, sub_self]

lemma res_rjet_one {f : PowerSeries D} (hf : Restricted f) (p : Polynomial F₂)
    (hp : ∀ n, res (coeff n f)=p.coeff n) (x : D) :
    res (rjet 1 f x)=p.derivative.eval (res x) := by
  simpa only [Polynomial.hasseDeriv_one] using rjet_residue_polynomial hf 1 p hp 1 x

lemma norm_sub_le_max_D (x y : D) : ‖x-y‖≤max ‖x‖ ‖y‖ := by
  simpa only [sub_eq_add_neg, norm_neg] using IsUltrametricDist.norm_add_le_max x (-y)

/-- Analytic Hensel lifting for an arbitrary restricted dyadic power series.
The proof contracts on the closed residue ball; no polynomial approximation is used. -/
theorem restricted_hensel_simple_residue
    {f : PowerSeries D} (hf : Restricted f) (p : Polynomial F₂)
    (hp : ∀ n, res (coeff n f)=p.coeff n) (a : D)
    (hval : p.eval (res a)=0) (hder : p.derivative.eval (res a) ≠ 0) :
    ∃ z : D, reval f z=0 ∧ res z=res a ∧
      deriv (qeval f) (z:ℚ_[2]) ≠ 0 ∧
      ∀ w : D, reval f w=0 → res w=res a → w=z := by
  have hunit : IsUnit (rjet 1 f a) := by
    apply PadicInt.isUnit_iff.mpr
    apply res_nonzero_norm_one
    rwa [res_rjet_one hf p hp]
  let u : Dˣ := hunit.unit
  have hu : (u:D)=rjet 1 f a := hunit.unit_spec
  let v : D := (↑(u⁻¹):D)
  have hvnorm : ‖v‖=1 := PadicInt.norm_units _
  have hvne : v ≠ 0 := Units.ne_zero _
  have hvu : v*rjet 1 f a=1 := by rw [← hu]; exact Units.inv_mul u
  let N : D → D := fun x => x-v*reval f x
  have hvalx (x : D) (hx : res x=res a) : res (reval f x)=0 := by
    rw [reval_residue_polynomial hf 1 p hp, hx, hval]
  have hderx (x : D) (hx : res x=res a) : res (rjet 1 f x)=res (rjet 1 f a) := by
    rw [res_rjet_one hf p hp, res_rjet_one hf p hp, hx]
  have hmap (x : D) (hx : res x=res a) : res (N x)=res a := by
    simp only [N, map_sub, map_mul, hvalx x hx, mul_zero, sub_zero, hx]
  have hc (x y : D) (hx : res x=res a) (hy : res y=res a) :
      ‖N x-N y‖≤(1/2:ℝ)*‖x-y‖ := by
    have hh : ‖x-y‖≤(1/2:ℝ) := norm_sub_le_half_of_res_eq (hx.trans hy.symm)
    have hsmall : ‖1-v*rjet 1 f y‖≤(1/2:ℝ) := by
      apply (res_zero_iff_norm_le_half _).mp
      have hz := congrArg res hvu
      simp only [map_mul, map_one] at hz
      simp only [map_sub, map_one, map_mul, hderx y hy, hz, sub_self]
    have he : ‖reval f x-reval f y-(x-y)*rjet 1 f y‖≤‖x-y‖^2 :=
      reval_first_order_error hf y x
    have hid : N x-N y=(x-y)*(1-v*rjet 1 f y)-
        v*(reval f x-reval f y-(x-y)*rjet 1 f y) := by dsimp [N]; ring
    rw [hid]
    apply (norm_sub_le_max_D _ _).trans
    apply max_le
    · rw [norm_mul, mul_comm]
      exact mul_le_mul_of_nonneg_right hsmall (norm_nonneg _)
    · rw [norm_mul, hvnorm, one_mul]
      exact he.trans (by nlinarith [norm_nonneg (x-y)])
  let S := {x : D // res x=res a}
  have : Nonempty S := ⟨⟨a,rfl⟩⟩
  have hclosed : IsClosed {x : D | res x=res a} :=
    isClosed_eq (continuous_redPow 1) continuous_const
  have : CompleteSpace S := hclosed.isComplete.completeSpace_coe
  let T : S → S := fun x => ⟨N x, hmap x x.property⟩
  have hcontr : ContractingWith (1/2:NNReal) T := by
    constructor
    · norm_num
    · apply LipschitzWith.of_dist_le_mul
      intro x y
      change ‖N x.val-N y.val‖≤((1/2:NNReal):ℝ)*‖x.val-y.val‖
      simpa only [NNReal.coe_div, NNReal.coe_one, NNReal.coe_ofNat] using hc x y x.property y.property
  let z : S := hcontr.fixedPoint T
  have hz : N z.val=z.val := congrArg Subtype.val hcontr.fixedPoint_isFixedPt
  have hzval : reval f z.val=0 := by
    have hm : v*reval f z.val=0 := by
      have hsub := sub_eq_self.mp hz
      exact hsub
    exact (mul_eq_zero.mp hm).resolve_left hvne
  refine ⟨z.val,hzval,z.property,?_,?_⟩
  · rw [deriv_qeval hf]
    apply PadicInt.coe_ne_zero.mpr
    intro hzero
    have hr := hderx z.val z.property
    rw [hzero, map_zero, res_rjet_one hf p hp] at hr
    exact hder hr.symm
  · intro w hw hwa
    have hwfix : Function.IsFixedPt T (⟨w,hwa⟩:S) := by
      apply Subtype.ext
      change w-v*reval f w=w
      rw [hw, mul_zero, sub_zero]
    exact congrArg Subtype.val (hcontr.fixedPoint_unique hwfix)

/-- The actual infinite evaluation preserves dyadic distances on a simple residue ball. -/
theorem restricted_isometry_on_simple_residue
    {f : PowerSeries D} (hf : Restricted f) (p : Polynomial F₂)
    (hp : ∀ n, res (coeff n f)=p.coeff n) (x y : D)
    (hxy : res x=res y) (hd : p.derivative.eval (res y) ≠ 0) :
    ‖reval f x-reval f y‖=‖x-y‖ := by
  by_cases heq : x=y
  · subst x
    simp
  have hpos : 0<‖x-y‖ := norm_pos_iff.mpr (sub_ne_zero.mpr heq)
  have hh : ‖x-y‖≤(1/2:ℝ) := norm_sub_le_half_of_res_eq hxy
  have hd1 : ‖rjet 1 f y‖=1 := by
    apply res_nonzero_norm_one
    rwa [res_rjet_one hf p hp]
  have herr := reval_first_order_error hf y x
  have hstrict : ‖reval f x-reval f y-(x-y)*rjet 1 f y‖<‖(x-y)*rjet 1 f y‖ := by
    rw [norm_mul, hd1, mul_one]
    apply herr.trans_lt
    nlinarith
  have hn := PadicInt.norm_eq_of_norm_add_lt_right (z1:=reval f x-reval f y)
    (z2:= -((x-y)*rjet 1 f y)) (by simpa only [← sub_eq_add_neg, norm_neg] using hstrict)
  simpa only [norm_neg, norm_mul, hd1, mul_one] using hn

/-- A residue certificate with no multiple residue root excludes every analytic critical zero. -/
theorem restricted_no_critical_root_of_residue
    {f : PowerSeries D} (hf : Restricted f) (p : Polynomial F₂)
    (hp : ∀ n, res (coeff n f)=p.coeff n)
    (h : ∀ y, p.eval y=0 → p.derivative.eval y ≠ 0) :
    ∀ x : D, reval f x=0 → deriv (qeval f) (x:ℚ_[2]) ≠ 0 := by
  intro x hx
  rw [deriv_qeval hf]
  apply PadicInt.coe_ne_zero.mpr
  intro hz
  have hv : p.eval (res x)=0 := by
    rw [← reval_residue_polynomial hf 1 p hp x, hx, map_zero]
  apply h (res x) hv
  rw [← res_rjet_one hf p hp, hz, map_zero]

/-- Infinite-series version of the binary quadratic certificate.  The source can have
arbitrarily many nonzero higher coefficients, provided they converge and reduce to zero. -/
theorem restricted_two_simple_roots
    {f : PowerSeries D} (hf : Restricted f)
    (hp : ∀ n, res (coeff n f)=(Polynomial.X^2+Polynomial.X : Polynomial F₂).coeff n) :
    ∃ a b : D, res a=0 ∧ res b=1 ∧ a ≠ b ∧
      (∀ x : D, reval f x=0 ↔ x=a ∨ x=b) ∧
      (∀ x : D, reval f x=0 → deriv (qeval f) (x:ℚ_[2]) ≠ 0) := by
  let p : Polynomial F₂ := Polynomial.X^2+Polynomial.X
  have hval (x : D) : p.eval (res x)=0 := by
    simpa [p] using (quadratic514_split_mod2 (res x)).1
  have hder (x : D) : p.derivative.eval (res x)=1 := by
    have ht : (2:F₂)=0 := by decide +kernel
    norm_num [p, ht]
    exact Or.inl ht
  obtain ⟨a,ha,hra,_,hua⟩ := restricted_hensel_simple_residue hf p hp 0
    (hval 0) (by rw [hder]; decide)
  obtain ⟨b,hb,hrb,_,hub⟩ := restricted_hensel_simple_residue hf p hp 1
    (hval 1) (by rw [hder]; decide)
  simp only [map_zero] at hra
  simp only [map_one] at hrb
  refine ⟨a,b,hra,hrb,?_,?_,?_⟩
  · intro hab
    have hc := congrArg res hab
    rw [hra,hrb] at hc
    norm_num at hc
  · intro x
    constructor
    · intro hx
      rcases binary_value (res x) with h0 | h1
      · exact Or.inl (hua x hx (by simpa using h0))
      · exact Or.inr (hub x hx (by simpa using h1))
    · rintro (rfl | rfl)
      · exact ha
      · exact hb
  · apply restricted_no_critical_root_of_residue hf p hp
    intro y _
    have hd : p.derivative.eval y=1 := by
      have ht : (2:F₂)=0 := by decide +kernel
      norm_num [p, ht]
      exact Or.inl ht
    rw [hd]
    decide

/-- Exact normalized root-distance law, not only existence or uniqueness. -/
theorem restricted_root_distance
    {f : PowerSeries D} (hf : Restricted f) (p : Polynomial F₂)
    (hp : ∀ n, res (coeff n f)=p.coeff n) (a x : D)
    (ha : reval f a=0) (hxa : res x=res a)
    (hd : p.derivative.eval (res a) ≠ 0) :
    ‖reval f x‖=‖x-a‖ := by
  simpa only [ha, sub_zero] using restricted_isometry_on_simple_residue hf p hp x a hxa hd

end Komorebi.Euler
