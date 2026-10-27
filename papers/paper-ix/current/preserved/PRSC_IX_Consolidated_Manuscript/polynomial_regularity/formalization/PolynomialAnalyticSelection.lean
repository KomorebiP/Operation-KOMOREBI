module
public import PolynomialAnalyticImplicit

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialAnalyticSelection
open Filter Set
open scoped Topology
open PolynomialParameterSystem PolynomialAnalyticEvaluation PolynomialAnalyticImplicit

variable {𝕜 : Type*} [NontriviallyNormedField 𝕜]
variable {e k : ℕ}

/-- Continuity places a supplied local root selection inside the unique local
graph, so its germ agrees with the constructed solution germ. -/
theorem continuous_selection_eventually_eq
    (P : (Fin (e + k) → 𝕜) → (Fin e → 𝕜))
    (g ψ : (Fin k → 𝕜) → (Fin e → 𝕜))
    (t₀ : Fin k → 𝕜) (y₀ : Fin e → 𝕜)
    (U : Set (Fin k → 𝕜)) (V : Set (Fin e → 𝕜))
    (hU : IsOpen U) (hV : IsOpen V) (ht : t₀ ∈ U) (hy : y₀ ∈ V)
    (hgraph : ∀ t ∈ U, ∀ y ∈ V, P (join y t) = 0 ↔ y = ψ t)
    (hg : ContinuousAt g t₀) (hg₀ : g t₀ = y₀)
    (hroot : ∀ᶠ t in 𝓝 t₀, P (join (g t) t) = 0) :
    g =ᶠ[𝓝 t₀] ψ := by
  have hgV : ∀ᶠ t in 𝓝 t₀, g t ∈ V := by
    apply hg.preimage_mem_nhds
    exact hV.mem_nhds (hg₀ ▸ hy)
  filter_upwards [hU.mem_nhds ht, hgV, hroot] with t ht' hgt hrt
  exact (hgraph t ht' (g t) hgt).mp hrt

variable [CompleteSpace 𝕜]

/-- Every continuous local root selection through a nonsingular point has the
analytic implicit germ and the actual derivative -J⁻¹K. No analyticity or
derivative hypothesis on the supplied selection is needed. -/
theorem continuous_selection_regularity
    (F : Fin e → MvPolynomial (Fin (e + k)) 𝕜)
    (a : Fin (e + k) → 𝕜)
    (hJ : IsUnit (PolynomialJointSystem.solvedJacobian F a))
    (g : (Fin k → 𝕜) → (Fin e → 𝕜))
    (hg : ContinuousAt g (freePart a)) (hg₀ : g (freePart a) = solvedPart a)
    (hroot : ∀ᶠ t in 𝓝 (freePart a), evalSystem F (join (g t) t) = 0) :
    AnalyticAt 𝕜 g (freePart a) ∧
      HasStrictFDerivAt g
        (matrixCLM (-((PolynomialJointSystem.solvedJacobian F a)⁻¹ *
          PolynomialJointSystem.parameterJacobian F a))) (freePart a) := by
  have hF : evalSystem F a = 0 := by
    simpa only [hg₀, join_parts] using hroot.self_of_nhds
  obtain ⟨ψ, U, V, hU, hV, ht, hy, _hψ₀, hψ, _hψV, hgraph, hdψ⟩ :=
    exists_analytic_implicit F a hF hJ
  have heq := continuous_selection_eventually_eq (evalSystem F) g ψ
    (freePart a) (solvedPart a) U V hU hV ht hy hgraph hg hg₀ hroot
  exact ⟨(hψ (freePart a) ht).congr heq.symm, hdψ.congr_of_eventuallyEq heq.symm⟩

/-- On an open parameter set, any continuous exact root selection with
invertible solved Jacobian is analytic everywhere on that set, with its actual
implicit derivative at every point. -/
theorem continuous_selection_analyticOnNhd
    (F : Fin e → MvPolynomial (Fin (e + k)) 𝕜)
    (g : (Fin k → 𝕜) → (Fin e → 𝕜)) (U : Set (Fin k → 𝕜))
    (hU : IsOpen U) (hg : ContinuousOn g U)
    (hroot : ∀ t ∈ U, evalSystem F (join (g t) t) = 0)
    (hJ : ∀ t ∈ U, IsUnit (PolynomialJointSystem.solvedJacobian F (join (g t) t))) :
    AnalyticOnNhd 𝕜 g U ∧
      ∀ t ∈ U, HasStrictFDerivAt g
        (matrixCLM (-((PolynomialJointSystem.solvedJacobian F (join (g t) t))⁻¹ *
          PolynomialJointSystem.parameterJacobian F (join (g t) t)))) t := by
  have hpoint (t : Fin k → 𝕜) (ht : t ∈ U) := by
    have hrt : ∀ᶠ u in 𝓝 t, evalSystem F (join (g u) u) = 0 := by
      filter_upwards [hU.mem_nhds ht] with u hu using hroot u hu
    have hgt : ContinuousAt g t := hg.continuousAt (hU.mem_nhds ht)
    have h := continuous_selection_regularity F (join (g t) t) (hJ t ht) g
      (by simpa only [freePart_join] using hgt)
      (by simp only [freePart_join, solvedPart_join])
      (by simpa only [freePart_join] using hrt)
    exact h
  exact ⟨fun t ht => by simpa only [freePart_join] using (hpoint t ht).1,
    fun t ht => by simpa only [freePart_join] using (hpoint t ht).2⟩

end Komorebi.PolynomialAnalyticSelection
