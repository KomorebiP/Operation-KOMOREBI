module
public import PolynomialParameterPath
public import PolynomialParameterSystem

@[expose] public section
noncomputable section
set_option autoImplicit false

open Filter Topology

namespace Komorebi.PolynomialPrescribedTowerLimit
open Komorebi.PolynomialObstruction Komorebi.PolynomialPadicLift
open Komorebi.PolynomialParameterSystem

variable {m k e : ℕ}

/-- Completion preserves prescribed parameter coordinates. The existence of the
compatible polynomial tower is an explicit hypothesis of this helper. -/
theorem prescribed_tower_limit (p L : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin (m+k)) ℤ)
    (z : ℕ → Fin (m+k) → ℤ) (t : ℕ → Fin k → ℤ) (τ : Fin k → ℤ_[p])
    (hroot : ∀ n i, (p : ℤ)^(L+n) ∣ evalSystem F (z n) i)
    (hstep : ∀ n i, (p : ℤ)^(L+n) ∣ (z (n+1) - z n) i)
    (hfree : ∀ n, freePart (z n) = t n)
    (htlim : Tendsto (fun n i => (t n i : ℤ_[p])) atTop (𝓝 τ)) :
    ∃ b : Fin (m+k) → ℤ_[p],
      Tendsto (fun n i => (z n i : ℤ_[p])) atTop (𝓝 b) ∧
      (∀ n i, (p : ℤ_[p])^(L+n) ∣ b i - (z n i : ℤ_[p])) ∧
      (∀ i, padicEval p F b i = 0) ∧ freePart b = τ := by
  obtain ⟨b, hlim, hprecision⟩ :=
    PadicTowerLimit.compatible_vector_tower_limit p L z hstep
  refine ⟨b, hlim, hprecision, polynomial_tower_limit_root p L F z b hroot hlim, ?_⟩
  funext i
  have hb := tendsto_pi_nhds.mp hlim (Fin.natAdd m i)
  have ht := tendsto_pi_nhds.mp htlim i
  have hseq : (fun n => (z n (Fin.natAdd m i) : ℤ_[p])) =
      (fun n => (t n i : ℤ_[p])) := by
    funext n
    exact congrArg (fun a : ℤ => (a : ℤ_[p])) (congrFun (hfree n) i)
  rw [hseq] at hb
  exact tendsto_nhds_unique hb ht

#print axioms prescribed_tower_limit

end Komorebi.PolynomialPrescribedTowerLimit
