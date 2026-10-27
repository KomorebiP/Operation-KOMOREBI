import KomorebiLSM.PacketTree
import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Algebra.Module.Submodule.LinearMap

/-! P3: exact reconstruction and Pythagoras for arbitrary complete cuts
of a finite rooted tree. Only local sums and sibling orthogonality are
assumed. The complete-cut sum and energy identity are conclusions. -/
set_option autoImplicit false
open scoped BigOperators
namespace Komorebi.LSM
universe u v
variable {𝕜 : Type u} [RCLike 𝕜]
variable {E : Type v} [NormedAddCommGroup E] [InnerProductSpace 𝕜 E]

/-- Finite Pythagoras derived by expanding the inner product. -/
theorem orthogonal_sum_energy {I : Type*} [Fintype I]
    (f : I → E) (h : ∀ i j, i ≠ j → inner 𝕜 (f i) (f j) = 0) :
    ‖∑ i, f i‖ ^ 2 = ∑ i, ‖f i‖ ^ 2 := by
  classical
  have hs : inner 𝕜 (∑ i, f i) (∑ j, f j) = ∑ i, inner 𝕜 (f i) (f i) := by
    simp only [sum_inner, inner_sum]
    apply Finset.sum_congr rfl
    intro i _
    exact Finset.sum_eq_single i (fun j _ hji => h j i hji)
      (fun hi => (hi (Finset.mem_univ i)).elim)
  simp only [InnerProductSpace.norm_sq_eq_re_inner (𝕜 := 𝕜), hs, map_sum]

namespace PacketTree

/-- Sibling ranges are orthogonal at every internal node. -/
def SiblingOrthogonal : (t : PacketTree) → (Node t → E →ₗ[𝕜] E) → Prop
  | .leaf, _ => True
  | .branch _ child, P =>
      (∀ i j, i ≠ j → ∀ x y,
        inner 𝕜 (P (Sum.inr ⟨i, root (child i)⟩) x)
          (P (Sum.inr ⟨j, root (child j)⟩) y) = 0) ∧
      ∀ i, SiblingOrthogonal (child i) (fun v => P (Sum.inr ⟨i, v⟩))

/-- Evaluating a conservative tree of linear maps preserves local sums. -/
theorem conservative_apply (t : PacketTree) (P : Node t → E →ₗ[𝕜] E)
    (hc : Conservative t P) (x : E) : Conservative t (fun v => P v x) := by
  induction t with
  | leaf => trivial
  | branch n child ih =>
      refine ⟨?_, fun i => ih i _ (hc.2 i)⟩
      simpa only [LinearMap.sum_apply] using congrArg (fun L : E →ₗ[𝕜] E => L x) hc.1

/-- Pythagoras makes squared packet norms a conservative scalar label. -/
theorem conservative_energy (t : PacketTree) (P : Node t → E →ₗ[𝕜] E)
    (hc : Conservative t P) (ho : SiblingOrthogonal t P) (x : E) :
    Conservative t (fun v => ‖P v x‖ ^ 2) := by
  induction t with
  | leaf => trivial
  | branch n child ih =>
      refine ⟨?_, fun i => ih i _ (hc.2 i) (ho.2 i)⟩
      have hp := (conservative_apply (.branch n child) P hc x).1
      dsimp only at hp ⊢
      rw [hp]
      exact orthogonal_sum_energy _ (fun i j hij => ho.1 i j hij x x)

/-- P3 operator reconstruction for a complete antichain. -/
theorem complete_cut_operator (t : PacketTree) (P : Node t → E →ₗ[𝕜] E)
    (s : Node t → Bool) (cut : IsCompleteCut t s)
    (hc : Conservative t P) (hroot : P (root t) = LinearMap.id) :
    (∑ v, if s v then P v else 0) = LinearMap.id :=
  (complete_cut_sum t s P cut hc).trans hroot

/-- P3 signal reconstruction for a complete antichain. -/
theorem complete_cut_reconstruction (t : PacketTree) (P : Node t → E →ₗ[𝕜] E)
    (s : Node t → Bool) (cut : IsCompleteCut t s)
    (hc : Conservative t P) (hroot : P (root t) = LinearMap.id) (x : E) :
    (∑ v, if s v then P v x else 0) = x := by
  rw [complete_cut_sum t s _ cut (conservative_apply t P hc x), hroot]
  rfl

/-- P3 orthogonal energy identity, obtained from local sibling hypotheses. -/
theorem complete_cut_energy (t : PacketTree) (P : Node t → E →ₗ[𝕜] E)
    (s : Node t → Bool) (cut : IsCompleteCut t s)
    (hc : Conservative t P) (ho : SiblingOrthogonal t P)
    (hroot : P (root t) = LinearMap.id) (x : E) :
    (∑ v, if s v then ‖P v x‖ ^ 2 else 0) = ‖x‖ ^ 2 := by
  rw [complete_cut_sum t s _ cut (conservative_energy t P hc ho x), hroot]
  rfl

/-- A direct projector formulation supplies sibling range orthogonality. -/
theorem range_orthogonal_of_projector_products
    (P Q : E →ₗ[𝕜] E)
    (hP : ∀ x y, inner 𝕜 (P x) y = inner 𝕜 x (P y))
    (hPQ : P.comp Q = 0) (x y : E) : inner 𝕜 (P x) (Q y) = 0 := by
  rw [hP]
  have hz : P (Q y) = 0 := by
    simpa only [LinearMap.comp_apply, LinearMap.zero_apply] using
      congrArg (fun f : E →ₗ[𝕜] E => f y) hPQ
  rw [hz, inner_zero_right]

end PacketTree
end Komorebi.LSM
