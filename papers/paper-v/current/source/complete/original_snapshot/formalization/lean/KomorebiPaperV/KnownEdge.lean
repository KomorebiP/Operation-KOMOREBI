import Mathlib.Analysis.Normed.Group.Basic
import Mathlib.Tactic

/-!
Author: Komorebi P.
Checked source. Theorem 6.1 and Corollary 6.2 at their
algebraic/normed-group level. No edge-discovery or Lp mask theorem is asserted.
-/

open scoped BigOperators

namespace KomorebiPaperV

section Algebra
variable {E : Type*} [AddCommGroup E]

theorem known_edge_error (s j : E) (Q : E → E) :
    (s + j) - (Q s + j) = s - Q s := by
  abel

theorem estimated_edge_error (s shat j jhat : E) :
    (s + j) - (shat + jhat) = (s - shat) + (j - jhat) := by
  abel

theorem several_known_edges_error {A : Type*} (t : Finset A)
    (s : E) (j : A → E) (Q : E → E) :
    (s + ∑ a ∈ t, j a) - (Q s + ∑ a ∈ t, j a) = s - Q s := by
  exact known_edge_error s (∑ a ∈ t, j a) Q
end Algebra

section Norms
variable {E : Type*} [SeminormedAddCommGroup E]

theorem known_edge_norm (s j : E) (Q : E → E) :
    ‖(s + j) - (Q s + j)‖ = ‖s - Q s‖ := by
  rw [known_edge_error]

theorem several_known_edges_norm {A : Type*} (t : Finset A)
    (s : E) (j : A → E) (Q : E → E) :
    ‖(s + ∑ a ∈ t, j a) - (Q s + ∑ a ∈ t, j a)‖ = ‖s - Q s‖ := by
  rw [several_known_edges_error]

theorem estimated_edge_norm_bound (s shat j jhat : E) :
    ‖(s + j) - (shat + jhat)‖ ≤ ‖s - shat‖ + ‖j - jhat‖ := by
  rw [estimated_edge_error]
  exact norm_add_le _ _
end Norms

end KomorebiPaperV
