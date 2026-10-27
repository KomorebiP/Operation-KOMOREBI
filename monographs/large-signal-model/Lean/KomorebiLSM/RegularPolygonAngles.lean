import Mathlib.Analysis.SpecialFunctions.Complex.Circle
import Mathlib.Algebra.Order.Round
import Mathlib.Tactic

/-! Exact vertices, angle rounding and directional support of a regular polygon. -/
set_option autoImplicit false
namespace Komorebi.LSM.RegularPolygon
open scoped ComplexConjugate RealInnerProductSpace
open Set

noncomputable def vertex (n : ℕ) (j : Fin n) : ℂ :=
  Circle.exp (2*Real.pi*(j:ℝ)/(n:ℝ))

theorem vertex_norm (n : ℕ) (j : Fin n) : ‖vertex n j‖=1 := Circle.norm_coe _

/-- Every integer-indexed vertex equals a member of the actual finite vertex family. -/
theorem int_vertex_mem {n : ℕ} (hn : 0<n) (k : ℤ) :
    (Circle.exp (2*Real.pi*(k:ℝ)/(n:ℝ)) : ℂ) ∈ range (vertex n) := by
  have hnZ : (0:ℤ)<n := by exact_mod_cast hn
  have hnR : (n:ℝ) ≠ 0 := by exact_mod_cast Nat.ne_of_gt hn
  have hnonneg : 0 ≤ k % (n:ℤ) := Int.emod_nonneg k (ne_of_gt hnZ)
  have hlt : (k % (n:ℤ)).toNat < n := by
    have h : (k % (n:ℤ)).toNat < (n:ℤ) := by
      rw [Int.toNat_of_nonneg hnonneg]
      exact Int.emod_lt_of_pos k hnZ
    exact_mod_cast h
  let j : Fin n := ⟨(k % (n:ℤ)).toNat,hlt⟩
  have hjZ : ((j:ℕ):ℤ) = k % (n:ℤ) := Int.toNat_of_nonneg hnonneg
  have hj := congrArg (Int.castRingHom ℝ) hjZ
  simp only [Int.coe_castRingHom, Int.cast_natCast] at hj
  refine ⟨j, ?_⟩
  change (Circle.exp (2*Real.pi*(j:ℝ)/(n:ℝ)) : ℂ) = _
  apply congrArg (fun u : Circle => (u:ℂ))
  apply Circle.exp_eq_exp.mpr
  refine ⟨-(k/(n:ℤ)), ?_⟩
  have he := Int.emod_add_mul_ediv k (n:ℤ)
  have her := congrArg (Int.castRingHom ℝ) he
  simp only [map_add, map_mul, Int.coe_castRingHom, Int.cast_natCast] at her
  rw [hj]
  simp only [Int.cast_neg]
  field_simp [hnR]
  linear_combination her

/-- Some vertex angle is at angular distance at most `pi/n` from any real angle. -/
theorem nearest_angle {n : ℕ} (hn : 0<n) (θ : ℝ) :
    ∃ k : ℤ, |2*Real.pi*(k:ℝ)/(n:ℝ)-θ| ≤ Real.pi/(n:ℝ) := by
  let k : ℤ := round ((n:ℝ)*θ/(2*Real.pi))
  refine ⟨k, ?_⟩
  have hr := abs_sub_round ((n:ℝ)*θ/(2*Real.pi))
  have hnR : (0:ℝ)<n := by exact_mod_cast hn
  have hp : (0:ℝ)<2*Real.pi := by positivity
  have he : 2*Real.pi*(k:ℝ)/(n:ℝ)-θ =
      -(2*Real.pi/(n:ℝ))*((n:ℝ)*θ/(2*Real.pi)-(k:ℝ)) := by
    field_simp [ne_of_gt hnR, Real.pi_ne_zero]
    ring
  rw [he, abs_mul, abs_neg, abs_of_pos (div_pos hp hnR)]
  calc
    _ ≤ (2*Real.pi/(n:ℝ))*(1/2) := mul_le_mul_of_nonneg_left hr (by positivity)
    _ = _ := by ring

/-- Directional support of a unit complex exponential, including the zero vector. -/
theorem inner_exp (v : ℂ) (θ : ℝ) :
    inner ℝ v (Circle.exp θ : ℂ) = ‖v‖*Real.cos (θ-Complex.arg v) := by
  have hr := Complex.norm_mul_cos_arg v
  have hi := Complex.norm_mul_sin_arg v
  rw [Complex.inner]
  have he : ((Circle.exp θ : ℂ)*conj v).re = Real.cos θ*v.re+Real.sin θ*v.im := by
    simp [Circle.coe_exp, Complex.exp_mul_I, Complex.mul_re,
      ← Complex.ofReal_cos, ← Complex.ofReal_sin]
  rw [he,Real.cos_sub,←hr,←hi]
  ring

/-- Every linear direction has support at least `norm(v)*cos(pi/n)`
on an actual vertex of the finite regular polygon. -/
theorem support_lower (n : ℕ) (hn : 3≤n) (v : ℂ) :
    ∃ j : Fin n, ‖v‖*Real.cos (Real.pi/(n:ℝ)) ≤ inner ℝ v (vertex n j) := by
  have hn0 : 0<n := by omega
  have hn1 : (1:ℝ)≤n := by exact_mod_cast (by omega : 1≤n)
  obtain ⟨k,hk⟩ := nearest_angle hn0 (Complex.arg v)
  obtain ⟨j,hj⟩ := int_vertex_mem hn0 k
  refine ⟨j, ?_⟩
  rw [hj, inner_exp]
  have hπ : Real.pi/(n:ℝ) ≤ Real.pi := div_le_self Real.pi_nonneg hn1
  have hc : Real.cos (Real.pi/(n:ℝ)) ≤
      Real.cos (2*Real.pi*(k:ℝ)/(n:ℝ)-Complex.arg v) := by
    simpa only [Real.cos_abs] using
      Real.cos_le_cos_of_nonneg_of_le_pi
        (abs_nonneg (2*Real.pi*(k:ℝ)/(n:ℝ)-Complex.arg v)) hπ hk
  exact mul_le_mul_of_nonneg_left hc (norm_nonneg v)

end Komorebi.LSM.RegularPolygon
