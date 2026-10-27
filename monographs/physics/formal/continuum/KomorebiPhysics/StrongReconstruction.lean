module
public import Mathlib.Analysis.InnerProductSpace.Adjoint
public import Mathlib.Tactic

/-! Strong reconstruction under explicit uniform contraction bounds.
No compact, Hilbert--Schmidt or adjoint convergence is inferred at this layer. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace StrongReconstruction
open Filter
open scoped Topology
variable {H α : Type*} [NormedAddCommGroup H] [NormedSpace ℂ H]
variable {l : Filter α}

/-- The actual sandwich operator. -/
def compression (S X : H →L[ℂ] H) : H →L[ℂ] H := S * X * S

theorem error_identity (S X : H →L[ℂ] H) :
    compression S X - X = S * X * (S - 1) + (S - 1) * X := by
  unfold compression
  noncomm_ring

theorem error_apply (S X : H →L[ℂ] H) (x : H) :
    compression S X x - X x = S (X (S x - x)) + (S (X x) - X x) := by
  simp only [compression, mul_apply_eq_comp, map_sub]
  abel

theorem contraction_apply (S : H →L[ℂ] H) (hS : ‖S‖ ≤ 1) (x : H) :
    ‖S x‖ ≤ ‖x‖ :=
  (S.le_opNorm x).trans (by nlinarith [norm_nonneg x])

/-- The source's state-error estimate, with its contraction assumption explicit. -/
theorem state_error_bound (S X : H →L[ℂ] H) (hS : ‖S‖ ≤ 1) (x : H) :
    ‖compression S X x - X x‖ ≤
      ‖X‖ * ‖S x - x‖ + ‖S (X x) - X x‖ := by
  rw [error_apply]
  exact (norm_add_le _ _).trans (add_le_add
    ((contraction_apply S hS _).trans (X.le_opNorm _)) le_rfl)

theorem compression_norm_le (S X : H →L[ℂ] H) (hS : ‖S‖ ≤ 1) :
    ‖compression S X‖ ≤ ‖X‖ := by
  apply (compression S X).opNorm_le_bound (norm_nonneg X)
  intro x
  change ‖S (X (S x))‖ ≤ _
  exact (contraction_apply S hS _).trans
    ((X.le_opNorm _).trans (mul_le_mul_of_nonneg_left (contraction_apply S hS x) (norm_nonneg _)))

theorem compression_sub (S X Y : H →L[ℂ] H) :
    compression S (X - Y) = compression S X - compression S Y := by
  unfold compression
  noncomm_ring

theorem compression_lipschitz (S X Y : H →L[ℂ] H) (hS : ‖S‖ ≤ 1) :
    ‖compression S X - compression S Y‖ ≤ ‖X-Y‖ := by
  rw [← compression_sub]
  exact compression_norm_le S (X-Y) hS

/-- Approximation by an arbitrary comparison operator. This is (6.63),
without pretending that the comparison's reconstruction error already vanishes. -/
theorem comparison_bound (S X Y : H →L[ℂ] H) (hS : ‖S‖ ≤ 1) :
    ‖compression S X - X‖ ≤ 2 * ‖X - Y‖ + ‖compression S Y - Y‖ := by
  have he : compression S X - X =
      (compression S X - compression S Y) + (compression S Y - Y) + (Y-X) := by abel
  rw [he]
  have h := norm_add_le (compression S X - compression S Y) (compression S Y - Y)
  have h' := norm_add_le (compression S X - compression S Y + (compression S Y - Y)) (Y-X)
  have hn := compression_lipschitz S X Y hS
  rw [norm_sub_rev Y X] at h'
  linarith

/-- Boundedness plus strong convergence gives strong convergence of sandwiches. -/
theorem compression_strong (S : α → H →L[ℂ] H)
    (hS : ∀ a, ‖S a‖ ≤ 1) (hs : ∀ x, Tendsto (fun a => S a x) l (𝓝 x))
    (X : H →L[ℂ] H) (x : H) :
    Tendsto (fun a => compression (S a) X x) l (𝓝 (X x)) := by
  apply tendsto_iff_norm_sub_tendsto_zero.mpr
  have h1 : Tendsto (fun a => ‖X‖ * ‖S a x-x‖) l (𝓝 0) := by
    simpa using ((hs x).sub_const x).norm.const_mul ‖X‖
  have h2 : Tendsto (fun a => ‖S a (X x)-X x‖) l (𝓝 0) := by
    simpa using ((hs (X x)).sub_const (X x)).norm
  exact squeeze_zero (fun _ => norm_nonneg _) (fun a => state_error_bound (S a) X (hS a) x)
    (by simpa using h1.add h2)

/-- Strong approximation may also be applied to vectors varying with the index,
provided they converge and a uniform contraction bound is retained. -/
theorem varying_vector (S : α → H →L[ℂ] H)
    (hS : ∀ a, ‖S a‖ ≤ 1) (hs : ∀ x, Tendsto (fun a => S a x) l (𝓝 x))
    {v : α → H} {x : H} (hv : Tendsto v l (𝓝 x)) :
    Tendsto (fun a => S a (v a)) l (𝓝 x) := by
  apply tendsto_iff_norm_sub_tendsto_zero.mpr
  have hb : ∀ a, ‖S a (v a) - x‖ ≤ ‖v a-x‖ + ‖S a x-x‖ := by
    intro a
    have he : S a (v a)-x = S a (v a-x) + (S a x-x) := by rw [map_sub]; abel
    rw [he]
    exact (norm_add_le _ _).trans (add_le_add (contraction_apply (S a) (hS a) _) le_rfl)
  exact squeeze_zero (fun _ => norm_nonneg _) hb (by
    simpa using ((hv.sub_const x).norm).add (((hs x).sub_const x).norm))

/-- A changing bounded approximation with operator-norm error tending to zero
can replace the fixed operator without losing strong reconstruction. -/
theorem perturbed_compression_strong (S : α → H →L[ℂ] H)
    (hS : ∀ a, ‖S a‖ ≤ 1) (hs : ∀ x, Tendsto (fun a => S a x) l (𝓝 x))
    (X : H →L[ℂ] H) (Y : α → H →L[ℂ] H)
    (hY : Tendsto (fun a => ‖Y a-X‖) l (𝓝 0)) (x : H) :
    Tendsto (fun a => compression (S a) (Y a) x) l (𝓝 (X x)) := by
  apply tendsto_iff_norm_sub_tendsto_zero.mpr
  have hb : ∀ a, ‖compression (S a) (Y a) x-X x‖ ≤
      ‖Y a-X‖*‖x‖ + ‖compression (S a) X x-X x‖ := by
    intro a
    have he : compression (S a) (Y a) x-X x =
        (compression (S a) (Y a)-compression (S a) X) x +
        (compression (S a) X x-X x) := by simp
    rw [he]
    exact (norm_add_le _ _).trans (add_le_add
      (((compression (S a) (Y a)-compression (S a) X).le_opNorm x).trans
        (mul_le_mul_of_nonneg_right (compression_lipschitz (S a) (Y a) X (hS a)) (norm_nonneg x))) le_rfl)
  exact squeeze_zero (fun _ => norm_nonneg _) hb (by
    simpa using (hY.mul_const ‖x‖).add
      (((compression_strong S hS hs X x).sub_const (X x)).norm))

end StrongReconstruction
end KomorebiPhysics
