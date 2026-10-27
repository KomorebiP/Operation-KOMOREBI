import Mathlib.Analysis.Meromorphic.Order
import Mathlib.Tactic

/-! The local pole argument needed for a cyclotomic Euler-product proof.
These are actual analytic/meromorphic functions. No arithmetic L-function
attachment, Euler product, or analytic continuation is asserted here. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.CyclotomicPoleRigidity
open Filter
open scoped Topology

/-- A natural power of a meromorphic function can have a simple pole only
when the exponent is one. -/
theorem exponent_one_of_simple_pole {f : ℂ → ℂ} {z : ℂ} {d : ℕ}
    (hf : MeromorphicAt f z)
    (hp : meromorphicOrderAt (fun w => f w ^ d) z = (-1 : WithTop ℤ)) :
    d = 1 := by
  rw [show (fun w => f w ^ d) = f ^ d from rfl, meromorphicOrderAt_pow hf] at hp
  have hi := congrArg (fun a : WithTop ℤ => a.untopD 0) hp
  simp only [WithTop.untopD_zero_mul] at hi
  change (d : ℤ) * (meromorphicOrderAt f z).untopD 0 = -1 at hi
  have hd : (0 : ℤ) ≤ d := Nat.cast_nonneg d
  have hm : (meromorphicOrderAt f z).untopD 0 < 0 := by
    by_contra h
    have := mul_nonneg hd (le_of_not_gt h)
    omega
  have he : (d : ℤ) = 1 := by nlinarith
  exact_mod_cast he

/-- Multiplication by an analytic factor preserves a supplied simple pole
only if that factor is nonzero at the point. -/
theorem analytic_factor_nonzero_of_simple_pole {p a : ℂ → ℂ} {z : ℂ}
    (hp : MeromorphicAt p z) (ha : AnalyticAt ℂ a z)
    (hpo : meromorphicOrderAt p z = (-1 : WithTop ℤ))
    (hprod : meromorphicOrderAt (fun w => p w * a w) z = (-1 : WithTop ℤ)) :
    a z ≠ 0 := by
  rw [show (fun w => p w * a w) = p * a from rfl,
    meromorphicOrderAt_mul hp ha.meromorphicAt, hpo] at hprod
  change ((-1 : ℤ) : WithTop ℤ) + meromorphicOrderAt a z =
    ((-1 : ℤ) : WithTop ℤ) at hprod
  have hao : meromorphicOrderAt a z = 0 := by
    cases h : meromorphicOrderAt a z with
    | top =>
      simp only [h, add_top] at hprod
      exact False.elim (WithTop.top_ne_coe hprod)
    | coe k =>
      rw [h] at hprod
      have hk : (-1 : ℤ) + k = -1 := by exact_mod_cast hprod
      have hk0 : k = 0 := by omega
      simp [hk0]
  obtain ⟨c, hc, hl⟩ := tendsto_ne_zero_of_meromorphicOrderAt_eq_zero
    ha.meromorphicAt hao
  have he : a z = c := tendsto_nhds_unique
    ha.continuousAt.continuousWithinAt.tendsto hl
  simpa [he] using hc

/-- A finite analytic Euler-factor family cannot cancel a simple pole when
the entire product, raised to an unknown natural index, again has a simple pole.
The index and all nonvanishing conclusions are derived. -/
theorem index_one_and_factors_nonzero {ι : Type*} [Fintype ι]
    (p : ℂ → ℂ) (a : ι → ℂ → ℂ) (z : ℂ) (d : ℕ)
    (hp : MeromorphicAt p z) (ha : ∀ i, AnalyticAt ℂ (a i) z)
    (hpo : meromorphicOrderAt p z = (-1 : WithTop ℤ))
    (hwhole : meromorphicOrderAt
      (fun w => (p w * ∏ i, a i w) ^ d) z = (-1 : WithTop ℤ)) :
    d = 1 ∧ ∀ i, a i z ≠ 0 := by
  classical
  have hA : AnalyticAt ℂ (fun w => ∏ i, a i w) z :=
    by fun_prop
  have hd := exponent_one_of_simple_pole (hp.mul hA.meromorphicAt) hwhole
  refine ⟨hd, ?_⟩
  have hprod : meromorphicOrderAt (fun w => p w * ∏ i, a i w) z =
      (-1 : WithTop ℤ) := by simpa [hd] using hwhole
  have hn := analytic_factor_nonzero_of_simple_pole hp hA hpo hprod
  exact fun i => (Finset.prod_ne_zero_iff.mp hn) i (Finset.mem_univ i)

/-- The criterion accepts a punctured-neighborhood product identity with a
second supplied meromorphic function of simple-pole order. -/
theorem index_one_and_factors_nonzero_of_identity {ι : Type*} [Fintype ι]
    (p Z : ℂ → ℂ) (a : ι → ℂ → ℂ) (z : ℂ) (d : ℕ)
    (hp : MeromorphicAt p z) (ha : ∀ i, AnalyticAt ℂ (a i) z)
    (hpo : meromorphicOrderAt p z = (-1 : WithTop ℤ))
    (hZo : meromorphicOrderAt Z z = (-1 : WithTop ℤ))
    (hidentity : Z =ᶠ[𝓝[≠] z] fun w => (p w * ∏ i, a i w) ^ d) :
    d = 1 ∧ ∀ i, a i z ≠ 0 := by
  apply index_one_and_factors_nonzero p a z d hp ha hpo
  rw [← meromorphicOrderAt_congr hidentity]
  exact hZo

end PaperX.CyclotomicPoleRigidity
