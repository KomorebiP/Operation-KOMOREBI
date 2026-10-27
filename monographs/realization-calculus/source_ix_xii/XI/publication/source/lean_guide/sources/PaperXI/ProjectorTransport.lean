import Mathlib.LinearAlgebra.Pi
import Mathlib.Tactic

/-! Exact reindexing law underlying the Frobenius covariance in Proposition 3.1.
This does not yet prove Fourier idempotence or the Weil-group realization.
The character weight transforms by the inverse permutation. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ProjectorTransport
open scoped BigOperators

variable {K V G : Type*} [Field K] [AddCommGroup V] [Module K V] [Fintype G]

theorem weighted_sum_conjugation (e : G ≃ G) (F : V ≃ₗ[K] V)
    (T : G → Module.End K V) (w : G → K)
    (h : ∀ g, F.conj (T g) = T (e g)) :
    F.conj (∑ g, w g • T g) = ∑ g, w (e.symm g) • T g := by
  simp only [map_sum, map_smul, h]
  simpa using (Equiv.sum_comp e (fun g => w (e.symm g) • T g))

theorem normalized_sum_conjugation (e : G ≃ G) (F : V ≃ₗ[K] V)
    (T : G → Module.End K V) (w : G → K) (c : K)
    (h : ∀ g, F.conj (T g) = T (e g)) :
    F.conj (c • ∑ g, w g • T g) = c • ∑ g, w (e.symm g) • T g := by
  rw [map_smul, weighted_sum_conjugation e F T w h]

end PaperXI.ProjectorTransport
