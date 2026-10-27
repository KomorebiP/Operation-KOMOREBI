import Mathlib.NumberTheory.Niven
import Mathlib.Topology.Instances.AddCircle.DenseSubgroup
import Mathlib.Analysis.SpecialFunctions.Complex.Circle
import Mathlib.Topology.Algebra.Group.SubmonoidClosure

set_option autoImplicit false
namespace Komorebi.LSM.RotationDensity

/-- The exact rational unit complex number used by the rotation model. -/
noncomputable def rotation : Circle :=
  ⟨⟨3/5,4/5⟩, by
    apply mem_sphere_zero_iff_norm.mpr
    apply (sq_eq_sq₀ (norm_nonneg _) (by norm_num : (0:ℝ)≤1)).mp
    norm_num [← Complex.normSq_eq_norm_sq, Complex.normSq_apply]⟩

@[simp] theorem rotation_coe_re : (rotation : ℂ).re = 3/5 := rfl
@[simp] theorem rotation_coe_im : (rotation : ℂ).im = 4/5 := rfl

theorem rotation_arg_cos : Real.cos (Complex.arg (rotation : ℂ)) = 3/5 := by
  rw [Complex.cos_arg rotation.coe_ne_zero, Circle.norm_coe, div_one, rotation_coe_re]

/-- Its angle is not a rational fraction of a turn. -/
theorem rotation_arg_irrational :
    Irrational (Complex.arg (rotation : ℂ)/(2*Real.pi)) := by
  intro h
  obtain ⟨q,hq⟩ := h
  have harg : Complex.arg (rotation : ℂ) = (2*q : ℚ)*Real.pi := by
    have hp : 2*Real.pi ≠ 0 := by positivity
    have he := (div_eq_iff hp).mp hq.symm
    push_cast
    nlinarith
  have hc := niven ⟨2*q,harg⟩ (⟨(3/5:ℚ), by rw [rotation_arg_cos]; norm_num⟩)
  rw [rotation_arg_cos] at hc
  norm_num at hc

/-- No positive power of the actual rational rotation is the identity. -/
theorem rotation_pow_ne_one (n : ℕ) (hn : 0<n) : rotation^n ≠ 1 := by
  intro h
  have he : Circle.exp ((n:ℝ)*Complex.arg (rotation : ℂ)) = 1 := by
    rw [Circle.exp_natCast_mul, Circle.exp_arg, h]
  obtain ⟨k,hk⟩ := Circle.exp_eq_one.mp he
  apply rotation_arg_irrational
  refine ⟨(k:ℚ)/n, ?_⟩
  have hnR : (n:ℝ) ≠ 0 := by exact_mod_cast Nat.ne_of_gt hn
  have hpi : Real.pi ≠ 0 := Real.pi_ne_zero
  push_cast
  field_simp
  nlinarith

/-- Integer powers are dense via the additive circle and Niven's theorem. -/
theorem rotation_integer_dense : DenseRange (fun n : ℤ => rotation^n) := by
  have hd := AddCircle.denseRange_zsmul_coe_iff.mpr rotation_arg_irrational
  let e := AddCircle.homeomorphCircle (T := 2*Real.pi) (by positivity : 2*Real.pi ≠ 0)
  have hm := e.surjective.denseRange.comp hd e.continuous
  convert hm using 1
  funext n
  change rotation^n = e (n • (Complex.arg (rotation : ℂ) : AddCircle (2*Real.pi)))
  rw [show e = AddCircle.homeomorphCircle (T := 2*Real.pi) (by positivity) from rfl,
    AddCircle.homeomorphCircle_apply, AddCircle.toCircle_zsmul, AddCircle.toCircle_apply_mk]
  simp only [div_self (by positivity : 2*Real.pi ≠ 0), one_mul, Circle.exp_arg]

/-- Forward, nonnegative powers are dense; negative time is not an input. -/
theorem rotation_forward_dense : DenseRange (fun n : ℕ => rotation^n) :=
  denseRange_zpow_iff_pow.mp rotation_integer_dense

/-- The topological closure is the entire actual unit circle. -/
theorem rotation_forward_closure :
    closure (Set.range (fun n : ℕ => rotation^n)) = Set.univ :=
  rotation_forward_dense.closure_range

/-- Any closed property holding on the forward orbit holds on the whole circle. -/
theorem forward_closed_property (P : Circle → Prop) (hclosed : IsClosed {u | P u})
    (horbit : ∀ n : ℕ, P (rotation^n)) (u : Circle) : P u :=
  rotation_forward_dense.induction_on u hclosed horbit

/-- Starting at any unit spatial direction gives a dense forward orbit. -/
theorem rotation_orbit_dense (u : Circle) : DenseRange (fun n : ℕ => rotation^n*u) :=
  (Homeomorph.mulRight u).surjective.denseRange.comp rotation_forward_dense
    (Homeomorph.mulRight u).continuous

end Komorebi.LSM.RotationDensity
