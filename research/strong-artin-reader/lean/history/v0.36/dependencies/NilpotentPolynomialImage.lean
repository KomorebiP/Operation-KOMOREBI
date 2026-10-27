import OperatorNormPolynomial
import Mathlib.RingTheory.Nilpotent.Basic

/-! Polynomial functional calculus on a nilpotent primary block. -/
noncomputable section
namespace Komorebi.StrongArtin.NonsemisimpleNorm
open Polynomial
variable {k V : Type*} [Field k] [AddCommGroup V] [Module k V]

theorem end_unit_bijective {U : Module.End k V} (hU : IsUnit U) :
    Function.Bijective U := by
  obtain ⟨u, rfl⟩ := hU
  constructor
  · intro x y h
    have hc := congrArg (fun z => (↑(u⁻¹) : Module.End k V) z) h
    simpa only [← Module.End.mul_apply, Units.inv_mul, Module.End.one_apply] using hc
  · intro y
    refine ⟨(↑(u⁻¹) : Module.End k V) y, ?_⟩
    change ((↑u : Module.End k V) * ↑(u⁻¹)) y = y
    simp

/-- A polynomial nonzero at lambda is invertible on a nilpotent lambda-primary block. -/
theorem aeval_isUnit_of_primary (T : Module.End k V) (lam : k)
    (hN : IsNilpotent (T - algebraMap k (Module.End k V) lam))
    (f : k[X]) (hf : f.eval lam ≠ 0) : IsUnit (aeval T f) := by
  obtain ⟨g, hg⟩ := (X_sub_C_dvd_sub_C_eval (p := f) (a := lam))
  have hv := congrArg (aeval T) hg
  simp only [map_sub, map_mul, aeval_X, aeval_C] at hv
  have hc : Commute (T - algebraMap k (Module.End k V) lam) (aeval T g) := by
    have h := (Commute.all (X - C lam) g).map (aeval T).toRingHom
    simpa using h
  have hn : IsNilpotent (aeval T f - algebraMap k (Module.End k V) (f.eval lam)) := by
    rw [hv]
    exact hc.isNilpotent_mul_right hN
  have hu : IsUnit (algebraMap k (Module.End k V) (f.eval lam)) :=
    (isUnit_iff_ne_zero.mpr hf).map (algebraMap k (Module.End k V))
  have h := hn.isUnit_add_left_of_commute hu
    (Algebra.commutes (f.eval lam) (aeval T f - algebraMap k (Module.End k V) (f.eval lam))).symm
  simpa only [add_sub_cancel] using h

/-- An exact root factorization computes image and kernel on a primary block. -/
theorem aeval_range_ker_of_root_factor (T : Module.End k V) (lam : k)
    (hN : IsNilpotent (T - algebraMap k (Module.End k V) lam))
    (f g : k[X]) (e : ℕ) (hf : f = (X - C lam)^e * g) (hg : g.eval lam ≠ 0) :
    LinearMap.range (aeval T f) = LinearMap.range ((T - algebraMap k (Module.End k V) lam)^e) ∧
    LinearMap.ker (aeval T f) = LinearMap.ker ((T - algebraMap k (Module.End k V) lam)^e) := by
  have hu := end_unit_bijective (aeval_isUnit_of_primary T lam hN g hg)
  have hv : aeval T f = (T - algebraMap k (Module.End k V) lam)^e * aeval T g := by
    simp [hf]
  have hc : Commute ((T - algebraMap k (Module.End k V) lam)^e) (aeval T g) := by
    have h := (Commute.all ((X - C lam)^e) g).map (aeval T).toRingHom
    simpa using h
  constructor
  · rw [hv]
    exact LinearMap.range_comp_of_range_eq_top _ (LinearMap.range_eq_top.mpr hu.2)
  · rw [hv, hc.eq]
    exact LinearMap.ker_comp_of_ker_eq_bot _ (LinearMap.ker_eq_bot.mpr hu.1)

end Komorebi.StrongArtin.NonsemisimpleNorm
