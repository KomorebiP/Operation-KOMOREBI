/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.EntireBridge
import Mathlib.Analysis.Analytic.Order

/-! # Uniqueness and exact finite basis for the entire ODE solution space -/

namespace Komorebi.PaperIV
noncomputable section

/-- Zero initial derivatives force every Taylor coefficient to vanish. -/
theorem ode_all_derivatives_zero {N : ℕ} (hN : 0 < N) (c : ℂ) (f : ℂ → ℂ)
    (hode : deriv^[N] f = fun z => c * f z)
    (hinit : ∀ k < N, deriv^[k] f 0 = 0) :
    ∀ k : ℕ, deriv^[k] f 0 = 0 := by
  intro k
  induction k using Nat.strong_induction_on with
  | h k ih =>
    by_cases hk : k < N
    · exact hinit k hk
    · have he : k = (k - N) + N := by omega
      rw [he, Function.iterate_add_apply, hode,
        ← iteratedDeriv_eq_iterate, iteratedDeriv_const_mul_field,
        iteratedDeriv_eq_iterate, ih (k - N) (by omega), mul_zero]

/-- Entire homogeneous ODE uniqueness derived from analytic order and the
identity theorem, without an ODE uniqueness certificate. -/
theorem entire_ode_zero_of_initial_zero {N : ℕ} (hN : 0 < N) (c : ℂ)
    {f : ℂ → ℂ} (hf : ∀ z, AnalyticAt ℂ f z)
    (hode : deriv^[N] f = fun z => c * f z)
    (hinit : ∀ k < N, deriv^[k] f 0 = 0) : f = 0 := by
  apply (AnalyticOnNhd.analyticOrderAt_eq_top_iff_eq_zero 0 hf).mp
  rw [ENat.eq_top_iff_forall_ge]
  intro n
  apply (natCast_le_analyticOrderAt_iff_iteratedDeriv_eq_zero (hf 0)).mpr
  intro k _
  rw [iteratedDeriv_eq_iterate]
  exact ode_all_derivatives_zero hN c f hode hinit k

/-- Two entire solutions with the same first N derivatives are identical. -/
theorem entire_ode_unique {N : ℕ} (hN : 0 < N) (c : ℂ)
    {f g : ℂ → ℂ} (hf : ∀ z, AnalyticAt ℂ f z) (hg : ∀ z, AnalyticAt ℂ g z)
    (hfode : deriv^[N] f = fun z => c * f z)
    (hgode : deriv^[N] g = fun z => c * g z)
    (hinit : ∀ k < N, deriv^[k] f 0 = deriv^[k] g 0) : f = g := by
  have hd (k : ℕ) (z : ℂ) :
      deriv^[k] (f - g) z = deriv^[k] f z - deriv^[k] g z := by
    simp only [← iteratedDeriv_eq_iterate]
    exact iteratedDeriv_sub (hf z).contDiffAt (hg z).contDiffAt
  have hzero := entire_ode_zero_of_initial_zero hN c (fun z => (hf z).sub (hg z))
    (by funext z; rw [hd, hfode, hgode]; simp only [Pi.sub_apply]; ring)
    (by intro k hk; rw [hd, hinit k hk, sub_self])
  funext z
  have hz := congrFun hzero z
  exact sub_eq_zero.mp hz

/-- A linear combination of the transfer basis, with ordinary complex coefficients. -/
def transferCombination (N : ℕ) (omega lambda : ℂ) (b : Fin N → ℂ) (z : ℂ) : ℂ :=
  ∑ j : Fin N, b j * entireTransfer N j.val omega lambda z

theorem analyticAt_transferCombination (N : ℕ) (omega lambda : ℂ)
    (b : Fin N → ℂ) (z : ℂ) : AnalyticAt ℂ (transferCombination N omega lambda b) z := by
  unfold transferCombination
  have h := Finset.analyticAt_sum (N := Finset.univ) (f := fun j : Fin N => fun z =>
    b j * entireTransfer N j.val omega lambda z)
    (fun j _ => analyticAt_const.mul (analyticAt_entireTransfer N j.val omega lambda z))
  simpa only [Finset.sum_fn] using h

theorem transferCombination_derivative (N k : ℕ) (omega lambda : ℂ)
    (b : Fin N → ℂ) (z : ℂ) :
    deriv^[k] (transferCombination N omega lambda b) z =
      ∑ j : Fin N, b j * deriv^[k] (entireTransfer N j.val omega lambda) z := by
  rw [← iteratedDeriv_eq_iterate]
  unfold transferCombination
  simp only [← iteratedDeriv_eq_iterate]
  rw [iteratedDeriv_fun_sum (fun j _ =>
    (analyticAt_const.mul (analyticAt_entireTransfer N j.val omega lambda z)).contDiffAt)]
  simp only [iteratedDeriv_const_mul_field]

theorem transferCombination_ode {N : ℕ} {omega : ℂ}
    (homega : IsPrimitiveRoot omega N) (lambda : ℂ) (b : Fin N → ℂ) :
    deriv^[N] (transferCombination N omega lambda b) =
      fun z => lambda ^ N * transferCombination N omega lambda b z := by
  funext z
  rw [transferCombination_derivative]
  simp only [entireTransfer_ode homega, transferCombination, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro j _
  ring

theorem transferCombination_initial {N : ℕ} (hN : 0 < N)
    {omega : ℂ} (homega : IsPrimitiveRoot omega N) (lambda : ℂ)
    (b : Fin N → ℂ) (k : Fin N) :
    deriv^[k.val] (transferCombination N omega lambda b) 0 = b k * lambda ^ k.val := by
  rw [transferCombination_derivative]
  have ht (j : Fin N) := entireTransfer_initial_data hN j.isLt k.isLt homega lambda
  simp_rw [ht]
  rw [Finset.sum_eq_single k]
  · simp
  · intro j _ hj
    have hne : k.val ≠ j.val := by intro h; exact hj (Fin.ext h.symm)
    simp [hne]
  · simp

/-- The exact solution formula for every entire solution of y^(N)=lambda^N y. -/
theorem entireTransfer_solution_expansion {N : ℕ} (hN : 0 < N)
    {omega lambda : ℂ} (homega : IsPrimitiveRoot omega N) (hlambda : lambda ≠ 0)
    {f : ℂ → ℂ} (hf : ∀ z, AnalyticAt ℂ f z)
    (hode : deriv^[N] f = fun z => lambda ^ N * f z) :
    f = transferCombination N omega lambda
      (fun j => deriv^[j.val] f 0 / lambda ^ j.val) := by
  apply entire_ode_unique hN (lambda ^ N) hf
    (analyticAt_transferCombination N omega lambda _) hode
    (transferCombination_ode homega lambda _)
  intro k hk
  have h := transferCombination_initial hN homega lambda
    (fun j => deriv^[j.val] f 0 / lambda ^ j.val) (⟨k, hk⟩ : Fin N)
  rw [h]
  simp [pow_ne_zero k hlambda]

/-- The coefficients in the solution expansion are unique, proving independence. -/
theorem transferCombination_injective {N : ℕ} (hN : 0 < N)
    {omega lambda : ℂ} (homega : IsPrimitiveRoot omega N) (hlambda : lambda ≠ 0) :
    Function.Injective (transferCombination N omega lambda) := by
  intro b d h
  funext k
  have he := congrArg (fun f : ℂ → ℂ => deriv^[k.val] f 0) h
  rw [transferCombination_initial hN homega, transferCombination_initial hN homega] at he
  exact mul_right_cancel₀ (pow_ne_zero k.val hlambda) he

/-- A linear combination in the signed basis. -/
def signedCombination (N : ℕ) (omega rho : ℂ) (b : Fin N → ℂ) (z : ℂ) : ℂ :=
  ∑ j : Fin N, b j * entireSigned N j.val omega rho z

theorem signedCombination_eq_transfer (N : ℕ) (omega rho : ℂ) (b : Fin N → ℂ) :
    signedCombination N omega rho b =
      transferCombination N omega rho (fun j => b j / rho ^ j.val) := by
  funext z
  unfold signedCombination transferCombination entireSigned
  apply Finset.sum_congr rfl
  intro j _
  simp only [div_eq_mul_inv]
  ring

/-- The signed sections span every entire solution of y^(N) = -y. -/
theorem entireSigned_solution_expansion {N : ℕ} (hN : 0 < N)
    {omega rho : ℂ} (homega : IsPrimitiveRoot omega N) (hrho : rho ^ N = -1)
    {f : ℂ → ℂ} (hf : ∀ z, AnalyticAt ℂ f z)
    (hode : deriv^[N] f = fun z => -f z) :
    f = signedCombination N omega rho (fun j => deriv^[j.val] f 0) := by
  have hr : rho ≠ 0 := by
    intro h
    simp [h, hN.ne'] at hrho
  rw [signedCombination_eq_transfer]
  apply entireTransfer_solution_expansion hN homega hr hf
  simpa only [hrho, neg_one_mul] using hode

/-- Signed solution coefficients are unique; the signed sections are independent. -/
theorem signedCombination_injective {N : ℕ} (hN : 0 < N)
    {omega rho : ℂ} (homega : IsPrimitiveRoot omega N) (hrho : rho ^ N = -1) :
    Function.Injective (signedCombination N omega rho) := by
  have hr : rho ≠ 0 := by
    intro h
    simp [h, hN.ne'] at hrho
  intro b d h
  rw [signedCombination_eq_transfer, signedCombination_eq_transfer] at h
  have he := transferCombination_injective hN homega hr h
  funext j
  exact (div_left_inj' (pow_ne_zero j.val hr)).mp (congrFun he j)

end
end Komorebi.PaperIV
