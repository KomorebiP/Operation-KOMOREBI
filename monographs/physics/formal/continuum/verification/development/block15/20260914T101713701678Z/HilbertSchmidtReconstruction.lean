module
public import KomorebiPhysics.HilbertSchmidtCore

/-! Section 6.8: actual Hilbert--Schmidt convergence under strongly converging
self-adjoint contractions. Dominated convergence is applied to proved summable
squared column norms; right approximation uses the proved adjoint invariance. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace HilbertSchmidtReconstruction
open Filter StrongReconstruction HilbertSchmidtCore
open scoped Topology BigOperators
variable {H I α : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]
variable {l : Filter α}

/-- Left HS convergence follows from actual dominated convergence of columns. -/
theorem left_energy_tendsto (b : HilbertBasis I ℂ H) (S : α → H →L[ℂ] H)
    (hS : ∀ a, ‖S a‖ ≤ 1) (hs : ∀ x, Tendsto (fun a => S a x) l (𝓝 x))
    (X : H →L[ℂ] H) (hX : IsHS b X) :
    Tendsto (fun a => energy b ((S a-1)*X)) l (𝓝 0) := by
  have hd : Summable (fun i => 4*‖X (b i)‖^2) := hX.mul_left 4
  have hc : ∀ i, Tendsto (fun a => ‖((S a-1)*X) (b i)‖^2) l (𝓝 0) := by
    intro i
    simpa only [mul_apply_eq_comp, sub_apply, one_apply_eq_self, sub_self,
      norm_zero, ne_eq, OfNat.ofNat_ne_zero, not_false_eq_true, zero_pow] using
      (((hs (X (b i))).sub_const (X (b i))).norm.pow 2)
  have hb : ∀ᶠ a in l, ∀ i, ‖‖((S a-1)*X) (b i)‖^2‖ ≤ 4*‖X (b i)‖^2 := by
    apply Eventually.of_forall
    intro a i
    rw [Real.norm_eq_abs, abs_of_nonneg (sq_nonneg _)]
    have he : ‖((S a-1)*X) (b i)‖ ≤ 2*‖X (b i)‖ := by
      change ‖S a (X (b i))-X (b i)‖ ≤ _
      have ht := norm_sub_le (S a (X (b i))) (X (b i))
      have hb := contraction_apply (S a) (hS a) (X (b i))
      linarith
    nlinarith [_root_.norm_nonneg (((S a-1)*X) (b i)), _root_.norm_nonneg (X (b i))]
  simpa only [energy, tsum_zero] using
    tendsto_tsum_of_dominated_convergence (g := fun _ : I => (0 : ℝ)) hd hc hb

theorem left_norm_tendsto (b : HilbertBasis I ℂ H) (S : α → H →L[ℂ] H)
    (hS : ∀ a, ‖S a‖ ≤ 1) (hs : ∀ x, Tendsto (fun a => S a x) l (𝓝 x))
    (X : H →L[ℂ] H) (hX : IsHS b X) :
    Tendsto (fun a => hsNorm b ((S a-1)*X)) l (𝓝 0) := by
  simpa only [hsNorm, Function.comp_def, Real.sqrt_zero] using
    Real.continuous_sqrt.continuousAt.tendsto.comp (left_energy_tendsto b S hS hs X hX)

variable [CompleteSpace H]

/-- Self-adjointness converts the right error to the left error of X*. -/
theorem right_norm_eq (b : HilbertBasis I ℂ H) (S X : H →L[ℂ] H)
    (hsa : IsSelfAdjoint S) (hX : IsHS b X) :
    hsNorm b (X*(S-1)) = hsNorm b ((S-1)*star X) := by
  rw [← norm_adjoint b (X*(S-1)) (right_mem b (S-1) X hX)]
  rw [star_mul, star_sub, hsa.star_eq, star_one]

theorem right_norm_tendsto (b : HilbertBasis I ℂ H) (S : α → H →L[ℂ] H)
    (hS : ∀ a, ‖S a‖ ≤ 1) (hs : ∀ x, Tendsto (fun a => S a x) l (𝓝 x))
    (hsa : ∀ a, IsSelfAdjoint (S a))
    (X : H →L[ℂ] H) (hX : IsHS b X) :
    Tendsto (fun a => hsNorm b (X*(S a-1))) l (𝓝 0) := by
  simp_rw [right_norm_eq b _ X (hsa _) hX]
  exact left_norm_tendsto b S hS hs (star X) (adjoint_mem b b X hX)

theorem compression_mem (b : HilbertBasis I ℂ H) (S X : H →L[ℂ] H)
    (hX : IsHS b X) : IsHS b (compression S X) :=
  right_mem b S (S*X) (left_mem b S X hX)

theorem compression_error_mem (b : HilbertBasis I ℂ H) (S X : H →L[ℂ] H)
    (hX : IsHS b X) : IsHS b (compression S X-X) :=
  sub_mem b _ X (compression_mem b S X hX) hX

theorem compression_error_bound (b : HilbertBasis I ℂ H) (S X : H →L[ℂ] H)
    (hS : ‖S‖ ≤ 1) (hX : IsHS b X) :
    hsNorm b (compression S X-X) ≤ hsNorm b (X*(S-1)) + hsNorm b ((S-1)*X) := by
  rw [error_identity, mul_assoc]
  have hR := right_mem b (S-1) X hX
  have hL := left_mem b (S-1) X hX
  apply (add_norm_le b _ _ (left_mem b S _ hR) hL).trans
  exact add_le_add ((left_norm_bound b S _ hR).trans (by
    nlinarith [HilbertSchmidtCore.norm_nonneg b (X*(S-1))])) le_rfl

/-- The source's full two-sided Hilbert--Schmidt reconstruction theorem. -/
theorem compression_norm_tendsto (b : HilbertBasis I ℂ H) (S : α → H →L[ℂ] H)
    (hS : ∀ a, ‖S a‖ ≤ 1) (hs : ∀ x, Tendsto (fun a => S a x) l (𝓝 x))
    (hsa : ∀ a, IsSelfAdjoint (S a))
    (X : H →L[ℂ] H) (hX : IsHS b X) :
    Tendsto (fun a => hsNorm b (compression (S a) X-X)) l (𝓝 0) := by
  exact squeeze_zero (fun a => HilbertSchmidtCore.norm_nonneg b _)
    (fun a => compression_error_bound b (S a) X (hS a) hX) (by
      simpa using (right_norm_tendsto b S hS hs hsa X hX).add (left_norm_tendsto b S hS hs X hX))

/-- HS convergence also supplies operator-norm convergence, without a separate compactness input. -/
theorem compression_opNorm_tendsto (b : HilbertBasis I ℂ H) (S : α → H →L[ℂ] H)
    (hS : ∀ a, ‖S a‖ ≤ 1) (hs : ∀ x, Tendsto (fun a => S a x) l (𝓝 x))
    (hsa : ∀ a, IsSelfAdjoint (S a))
    (X : H →L[ℂ] H) (hX : IsHS b X) :
    Tendsto (fun a => ‖compression (S a) X-X‖) l (𝓝 0) :=
  squeeze_zero (fun _ => _root_.norm_nonneg _)
    (fun a => opNorm_le b _ (compression_error_mem b (S a) X hX))
    (compression_norm_tendsto b S hS hs hsa X hX)

end HilbertSchmidtReconstruction
end KomorebiPhysics
