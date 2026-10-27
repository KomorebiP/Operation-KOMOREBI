import KomorebiLSM.Polynomial
import KomorebiLSM.DefectPropagation
import Mathlib.Analysis.Normed.Module.Multilinear.Basic

/-! P20: all ordered packet tuples, an explicit omitted sum and bounded-domain
Lipschitz control. No nonlinear independent-packet rule is assumed. -/
set_option autoImplicit false
open scoped BigOperators
namespace Komorebi.LSM.PacketApproximation
universe u v w
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable {X : Type v} [NormedAddCommGroup X] [NormedSpace 𝕜 X]
variable {Y : Type w} [NormedAddCommGroup Y] [NormedSpace 𝕜 Y]
variable {I : Type*} [Fintype I]

/-- A bound on B restricted to the specified product of packet ranges. -/
def HasPacketBound {m : ℕ} (P : I → X →L[𝕜] X)
    (B : ContinuousMultilinearMap 𝕜 (fun _ : Fin m => X) Y)
    (f : Fin m → I) (beta : ℝ) : Prop :=
  ∀ v : Fin m → X, (∀ k, v k ∈ LinearMap.range (P (f k)).toLinearMap) →
    ‖B v‖ ≤ beta*∏ k, ‖v k‖

theorem projected_packet_bound {m : ℕ} (P : I → X →L[𝕜] X)
    (B : ContinuousMultilinearMap 𝕜 (fun _ : Fin m => X) Y)
    (f : Fin m → I) {beta : ℝ} (bound : HasPacketBound P B f beta) (v : Fin m → X) :
    ‖B (fun k => P (f k) (v k))‖ ≤ beta*∏ k, ‖P (f k) (v k)‖ := by
  apply bound
  intro k
  exact ⟨v k,rfl⟩

theorem contractive_packet_norm (P : X →L[𝕜] X) (bound : ‖P‖ ≤ 1) (x : X) :
    ‖P x‖ ≤ ‖x‖ := by
  exact (P.le_opNorm x).trans (by simpa using mul_le_mul_of_nonneg_right bound (norm_nonneg x))

theorem packet_multilinear_bound {m : ℕ} (P : I → X →L[𝕜] X)
    (contractive : ∀ i, ‖P i‖ ≤ 1)
    (B : ContinuousMultilinearMap 𝕜 (fun _ : Fin m => X) Y)
    (f : Fin m → I) {beta : ℝ} (hbeta : 0 ≤ beta)
    (bound : HasPacketBound P B f beta) (v : Fin m → X) :
    ‖B (fun k => P (f k) (v k))‖ ≤ beta*∏ k, ‖v k‖ := by
  apply (projected_packet_bound P B f bound v).trans
  apply mul_le_mul_of_nonneg_left _ hbeta
  exact Finset.prod_le_prod (fun _ _ => norm_nonneg _)
    (fun k _ => contractive_packet_norm _ (contractive _) (v k))

/-- Telescoping multilinearity gives the degree factor. -/
theorem packet_term_lipschitz {m : ℕ} (P : I → X →L[𝕜] X)
    (contractive : ∀ i, ‖P i‖ ≤ 1)
    (B : ContinuousMultilinearMap 𝕜 (fun _ : Fin (m+1) => X) Y)
    (f : Fin (m+1) → I) {beta R : ℝ} (hbeta : 0 ≤ beta) (hR : 0 ≤ R)
    (bound : HasPacketBound P B f beta) (x y : X) (hx : ‖x‖ ≤ R) (hy : ‖y‖ ≤ R) :
    ‖B (fun k => P (f k) x)-B (fun k => P (f k) y)‖ ≤
      ((m+1:ℕ):ℝ)*beta*R^m*‖x-y‖ := by
  let T := B.toMultilinearMap.compLinearMap (fun k => (P (f k)).toLinearMap)
  have hb : ∀ v, ‖T v‖ ≤ beta*∏ k, ‖v k‖ :=
    packet_multilinear_bound P contractive B f hbeta bound
  have h := T.norm_image_sub_le_of_bound hbeta hb (fun _ => x) (fun _ => y)
  have hmax : max ‖(fun _ : Fin (m+1) => x)‖ ‖(fun _ : Fin (m+1) => y)‖ ≤ R := by
    exact max_le ((pi_norm_le_iff_of_nonneg hR).mpr (fun _ => hx))
      ((pi_norm_le_iff_of_nonneg hR).mpr (fun _ => hy))
  have hdiff : ‖(fun _ : Fin (m+1) => x)-(fun _ : Fin (m+1) => y)‖ ≤ ‖x-y‖ := by
    exact (pi_norm_le_iff_of_nonneg (norm_nonneg _)).mpr (fun _ => le_rfl)
  simp only [Fintype.card_fin, Nat.add_sub_cancel] at h
  calc
    _ ≤ beta*(m+1:ℕ)*max ‖(fun _ : Fin (m+1) => x)‖ ‖(fun _ : Fin (m+1) => y)‖^m*
        ‖(fun _ : Fin (m+1) => x)-(fun _ : Fin (m+1) => y)‖ := h
    _ ≤ beta*(m+1:ℕ)*R^m*‖x-y‖ := by gcongr
    _ = _ := by ring

def fullPolynomial (p : ℕ)
    (B : (m : Fin p) → ContinuousMultilinearMap 𝕜 (fun _ : Fin (m.val+1) => X) Y)
    (b : Y) (x : X) : Y := b+∑ m, B m (fun _ => x)

def retainedPolynomial (p : ℕ) (P : I → X →L[𝕜] X)
    (B : (m : Fin p) → ContinuousMultilinearMap 𝕜 (fun _ : Fin (m.val+1) => X) Y)
    (keep : (m : Fin p) → Finset (Fin (m.val+1) → I)) (b : Y) (x : X) : Y :=
  b+∑ m, ∑ f ∈ keep m, B m (fun k => P (f k) x)

theorem full_ordered_expansion (p : ℕ) (P : I → X →L[𝕜] X)
    (complete : ∀ x, ∑ i, P i x=x)
    (B : (m : Fin p) → ContinuousMultilinearMap 𝕜 (fun _ : Fin (m.val+1) => X) Y)
    (b : Y) (x : X) :
    fullPolynomial p B b x = b+∑ m, ∑ f : Fin (m.val+1) → I, B m (fun k => P (f k) x) := by
  unfold fullPolynomial
  congr 1
  apply Finset.sum_congr rfl
  intro m _
  have h := (B m).toMultilinearMap.map_sum (fun (_ : Fin (m.val+1)) i => P i x)
  simpa only [complete, ContinuousMultilinearMap.coe_coe] using h

/-- The difference is literally the sum of omitted ordered interactions. -/
theorem omitted_interaction_identity (p : ℕ) (P : I → X →L[𝕜] X)
    (complete : ∀ x, ∑ i, P i x=x)
    (B : (m : Fin p) → ContinuousMultilinearMap 𝕜 (fun _ : Fin (m.val+1) => X) Y)
    (keep : (m : Fin p) → Finset (Fin (m.val+1) → I)) (b : Y) (x : X) :
    fullPolynomial p B b x-retainedPolynomial p P B keep b x =
      ∑ m, ∑ f ∈ Finset.univ \ keep m, B m (fun k => P (f k) x) := by
  classical
  rw [full_ordered_expansion p P complete B b x]
  unfold retainedPolynomial
  simp only [add_sub_add_left_eq_sub, ← Finset.sum_sub_distrib]
  apply Finset.sum_congr rfl
  intro m _
  exact (Finset.sum_sdiff_eq_sub (Finset.subset_univ (keep m))).symm

/-- Restricted block bounds and packet amplitudes yield the stated remainder. -/
theorem packet_interaction_truncation_bound (p : ℕ) (P : I → X →L[𝕜] X)
    (complete : ∀ x, ∑ i, P i x=x)
    (B : (m : Fin p) → ContinuousMultilinearMap 𝕜 (fun _ : Fin (m.val+1) => X) Y)
    (keep : (m : Fin p) → Finset (Fin (m.val+1) → I))
    (beta : (m : Fin p) → (Fin (m.val+1) → I) → ℝ)
    (bound : ∀ m f, HasPacketBound P (B m) f (beta m f)) (b : Y) (x : X) :
    ‖fullPolynomial p B b x-retainedPolynomial p P B keep b x‖ ≤
      ∑ m, ∑ f ∈ Finset.univ \ keep m, beta m f*∏ k, ‖P (f k) x‖ := by
  classical
  rw [omitted_interaction_identity p P complete B keep b x]
  apply (norm_sum_le _ _).trans
  apply Finset.sum_le_sum
  intro m _
  apply (norm_sum_le _ _).trans
  exact Finset.sum_le_sum (fun f _ => projected_packet_bound P (B m) f (bound m f) (fun _ => x))

/-- A bounded-domain norm inequality equivalent to the displayed Lipschitz bound. -/
theorem retained_polynomial_lipschitz_bound (p : ℕ) (P : I → X →L[𝕜] X)
    (contractive : ∀ i, ‖P i‖ ≤ 1)
    (B : (m : Fin p) → ContinuousMultilinearMap 𝕜 (fun _ : Fin (m.val+1) => X) Y)
    (keep : (m : Fin p) → Finset (Fin (m.val+1) → I))
    (beta : (m : Fin p) → (Fin (m.val+1) → I) → ℝ)
    (hbeta : ∀ m f, 0 ≤ beta m f)
    (bound : ∀ m f, HasPacketBound P (B m) f (beta m f))
    (b : Y) {R : ℝ} (hR : 0 ≤ R) (x y : X) (hx : ‖x‖ ≤ R) (hy : ‖y‖ ≤ R) :
    ‖retainedPolynomial p P B keep b x-retainedPolynomial p P B keep b y‖ ≤
      (∑ m, ∑ f ∈ keep m, (m.val+1:ℕ)*beta m f*R^m.val)*‖x-y‖ := by
  classical
  unfold retainedPolynomial
  simp only [add_sub_add_left_eq_sub, ← Finset.sum_sub_distrib]
  apply (norm_sum_le _ _).trans
  rw [Finset.sum_mul]
  apply Finset.sum_le_sum
  intro m _
  apply (norm_sum_le _ _).trans
  rw [Finset.sum_mul]
  exact Finset.sum_le_sum (fun f _ =>
    packet_term_lipschitz P contractive (B m) f (hbeta m f) hR (bound m f) x y hx hy)

/-- A physical-model remainder is added explicitly instead of silently equating
the polynomial with an unexpanded nonlinear law. -/
theorem additional_model_remainder (f poly approx : X → Y) (x : X) {eps tail : ℝ}
    (model_error : ‖f x-poly x‖ ≤ eps) (truncation : ‖poly x-approx x‖ ≤ tail) :
    ‖f x-approx x‖ ≤ eps+tail := by
  calc
    ‖f x-approx x‖ = ‖(f x-poly x)+(poly x-approx x)‖ := by congr 1; abel
    _ ≤ ‖f x-poly x‖+‖poly x-approx x‖ := norm_add_le _ _
    _ ≤ _ := add_le_add model_error truncation

end Komorebi.LSM.PacketApproximation
