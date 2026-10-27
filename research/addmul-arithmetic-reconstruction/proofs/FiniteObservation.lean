import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FieldSimp
import Mathlib.Basic.Real.Basic

set_option autoImplicit false

/-!
Block 03: filtered additive reconstruction under *any* correction constant
on three indistinguishable modular observations.
The arithmetic periodicity that produces the three observations is
proved in the mathematical note and checked by the Python harness.
-/
namespace KomorebiAddMul.Block03

/-- The annihilator kills one additive scaling and one correction constant.
    In an arithmetic instance `u = p^L`, `v = q^L`, `A = p^k`, `B = q^k`.
    No assumption is made on how the common correction `κ` was computed. -/
theorem filter_identity (u v A B lam kap : ℝ) :
    u * (B - lam*A - kap)
      - (u+1) * (B*v - lam*A*u - kap)
      + (B*v^2 - lam*A*u^2 - kap)
    = B*(v-1)*(v-u) := by
  ring

/-- Exact reconstruction on three indistinguishable finite observations
    forces a vanishing annihilator. -/
theorem exact_repair_requires_zero (u v A B lam kap : ℝ)
    (h0 : B = lam*A + kap)
    (h1 : B*v = lam*A*u + kap)
    (h2 : B*v^2 = lam*A*u^2 + kap) :
    B*(v-1)*(v-u) = 0 := by
  have z0 : B-lam*A-kap=0 := by linarith
  have z1 : B*v-lam*A*u-kap=0 := by linarith
  have z2 : B*v^2-lam*A*u^2-kap=0 := by linarith
  rw [← filter_identity u v A B lam kap, z0, z1, z2]
  ring

/-- Sharp general *lower bound* over three sampled observations.
    No compactness, integrality or continuity of the correction is assumed:
    it is simply required to agree at the three indistinguishable inputs. -/
theorem finite_observation_lower_bound
    (u v A B lam kap M : ℝ)
    (hu : 0 ≤ u)
    (h0 : |B - lam*A - kap| ≤ M)
    (h1 : |B*v - lam*A*u - kap| ≤ M)
    (h2 : |B*v^2 - lam*A*u^2 - kap| ≤ M) :
    |B*(v-1)*(v-u)| ≤ 2*(u+1)*M := by
  have h0a := (abs_le.mp h0).1
  have h0b := (abs_le.mp h0).2
  have h1a := (abs_le.mp h1).1
  have h1b := (abs_le.mp h1).2
  have h2a := (abs_le.mp h2).1
  have h2b := (abs_le.mp h2).2
  have hu1 : 0 ≤ u+1 := by linarith
  have a_upper := mul_le_mul_of_nonneg_left h0b hu
  have a_lower := mul_le_mul_of_nonneg_left h0a hu
  have b_upper := mul_le_mul_of_nonneg_left h1b hu1
  have b_lower := mul_le_mul_of_nonneg_left h1a hu1
  have filter_eq := filter_identity u v A B lam kap
  apply abs_le.mpr
  constructor <;> nlinarith

/-- An explicit witness achieves equality on the three points. -/
theorem finite_observation_sharp_witness
    (u v A B : ℝ) (hAu : A*(u-1) ≠ 0) (hup : u+1 ≠ 0) :
    ∃ lam kap t : ℝ,
      2*(u+1)*t = B*(v-1)*(v-u) ∧
      B-lam*A-kap = t ∧
      B*v-lam*A*u-kap = -t ∧
      B*v^2-lam*A*u^2-kap = t := by
  let t : ℝ := B*(v-1)*(v-u)/(2*(u+1))
  let lam : ℝ := (B*(v-1)+2*t)/(A*(u-1))
  let kap : ℝ := B-t-lam*A
  refine ⟨lam,kap,t,?_,?_,?_,?_⟩
  · dsimp [t]; field_simp [hup]
  · dsimp [kap]; ring
  · have hh : lam*(A*(u-1))=B*(v-1)+2*t := by
      change (B*(v-1)+2*t)/(A*(u-1)) * (A*(u-1)) = B*(v-1)+2*t
      exact div_mul_cancel₀ _ hAu
    dsimp [kap]
    nlinarith
  · have hh : lam*(A*(u-1))=B*(v-1)+2*t := by
      change (B*(v-1)+2*t)/(A*(u-1)) * (A*(u-1)) = B*(v-1)+2*t
      exact div_mul_cancel₀ _ hAu
    have ht : 2*(u+1)*t=B*(v-1)*(v-u) := by
      dsimp [t]
      field_simp [hup]
    have hhs := congrArg (fun x : ℝ => x*(u+1)) hh
    dsimp [kap]
    nlinarith [hhs,ht]

end KomorebiAddMul.Block03

-- Verification/Axiom audit (part of reproducible source).
#print axioms KomorebiAddMul.Block03.filter_identity
#print axioms KomorebiAddMul.Block03.exact_repair_requires_zero
#print axioms KomorebiAddMul.Block03.finite_observation_lower_bound
#print axioms KomorebiAddMul.Block03.finite_observation_sharp_witness
