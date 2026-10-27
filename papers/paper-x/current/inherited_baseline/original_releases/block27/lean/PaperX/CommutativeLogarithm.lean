import PaperX.NilpotentSeries
import PaperX.FiniteLogarithm

set_option autoImplicit false

namespace PaperX.CommutativeLogarithm

open PaperX.NilpotentSeries
open scoped BigOperators

variable {A : Type*} [CommRing A] [Algebra ℚ A]

theorem eval_log {u : A} (hu : IsNilpotent (u - 1)) :
    eval (u - 1) (PowerSeries.log A) = FiniteLogarithm.log u := by
  obtain ⟨k, hk⟩ := hu
  rw [eval_eq_sum hk, FiniteLogarithm.log_eq_sum hk]
  apply Finset.sum_congr rfl
  intro n _
  by_cases hn : n = 0
  · subst n
    simp
  · simp [PowerSeries.coeff_log, hn, Algebra.smul_def]

theorem subst_log {u : A} (hu : IsNilpotent (u - 1)) :
    (PowerSeries.log A).subst (PowerSeries.C (u - 1)) =
      PowerSeries.C (FiniteLogarithm.log u) := by
  rw [subst_C_eq_C_eval hu, eval_log hu]

theorem subst_exp {a : A} (ha : IsNilpotent a) :
    (PowerSeries.exp A).subst (PowerSeries.C a) = PowerSeries.C (IsNilpotent.exp a) := by
  rw [subst_C_eq_C_eval ha, eval_exp ha]

/-- The finite logarithm recovers a nilpotent element with no bound on its nilpotency class. -/
theorem log_exp {a : A} (ha : IsNilpotent a) :
    FiniteLogarithm.log (IsNilpotent.exp a) = a := by
  have h := PowerSeries.subst_comp_subst_apply
    (PowerSeries.HasSubst.exp_sub_one (A := A)) (hasSubst_C ha) (PowerSeries.log A)
  rw [PowerSeries.subst_log_exp_sub_one, PowerSeries.subst_X (hasSubst_C ha),
    PowerSeries.subst_sub (hasSubst_C ha), subst_exp ha] at h
  have hone : (1 : PowerSeries A).subst (PowerSeries.C a) = 1 := by
    rw [← PowerSeries.coe_substAlgHom (hasSubst_C ha), map_one]
  rw [hone, ← map_one PowerSeries.C, ← map_sub, subst_log ha.isNilpotent_exp_sub_one] at h
  exact (PowerSeries.C_injective h).symm

/-- Exponentiation recovers every unipotent element from its finite logarithm. -/
theorem exp_log {u : A} (hu : IsNilpotent (u - 1)) :
    IsNilpotent.exp (FiniteLogarithm.log u) = u := by
  have h := PowerSeries.subst_comp_subst_apply
    (PowerSeries.HasSubst.log (A := A)) (hasSubst_C hu) (PowerSeries.exp A)
  rw [PowerSeries.subst_exp_log, PowerSeries.subst_add (hasSubst_C hu),
    PowerSeries.subst_X (hasSubst_C hu), subst_log hu] at h
  have hone : (1 : PowerSeries A).subst (PowerSeries.C (u - 1)) = 1 := by
    rw [← PowerSeries.coe_substAlgHom (hasSubst_C hu), map_one]
  rw [hone, subst_exp (FiniteLogarithm.isNilpotent_log hu)] at h
  have hc := congrArg (PowerSeries.constantCoeff (R := A)) h
  simpa using hc.symm

end PaperX.CommutativeLogarithm
