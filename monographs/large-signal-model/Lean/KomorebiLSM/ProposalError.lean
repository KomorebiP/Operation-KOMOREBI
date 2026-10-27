import KomorebiLSM.SingularPerturbation
import KomorebiLSM.EuclideanMatrixNorms

set_option autoImplicit false

namespace Komorebi.LSM.ProposalError
open scoped Matrix

section Abstract
variable {E F : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
  [NormedAddCommGroup F] [InnerProductSpace ℝ F]
  [FiniteDimensional ℝ E] [FiniteDimensional ℝ F]

/-- The last domain-indexed singular value. In dimension zero this is zero. -/
noncomputable def leastSingular (L : E →L[ℝ] F) : ℝ :=
  L.toLinearMap.singularValues (Module.finrank ℝ E - 1)

theorem leastSingular_nonneg (L : E →L[ℝ] F) : 0 ≤ leastSingular L :=
  L.toLinearMap.singularValues_nonneg _

/-- The least singular value controls every domain vector, including a zero-dimensional domain. -/
theorem leastSingular_mul_norm_le (L : E →L[ℝ] F) (x : E) :
    leastSingular L * ‖x‖ ≤ ‖L x‖ := by
  have ht : Spectral.rightHead L.toLinearMap (Module.finrank ℝ E) le_rfl = ⊤ :=
    Submodule.eq_top_of_finrank_eq (Spectral.rightHead_finrank _ _ _)
  exact Spectral.lower_on_rightHead _ _ le_rfl x (by rw [ht]; trivial)

/-- Actual singular values obey the operator perturbation bound. -/
theorem leastSingular_sub_le (L K : E →L[ℝ] F) (e : ℝ) (he : ‖L-K‖ ≤ e) :
    leastSingular L - e ≤ leastSingular K := by
  have h := Spectral.singularValue_le_add_norm L K (Module.finrank ℝ E - 1)
  change leastSingular L ≤ leastSingular K + ‖L-K‖ at h
  linarith

/-- Residual and operator error give an a posteriori solution error. -/
theorem residual_error (L K : E →L[ℝ] F) (x x₀ : E) (b : F) (e : ℝ)
    (hpert : ‖L-K‖ ≤ e) (hgap : e < leastSingular L) (hexact : K x₀ = b) :
    ‖x-x₀‖ ≤ (‖L x-b‖ + e*‖x‖) / (leastSingular L-e) := by
  have hlower := leastSingular_mul_norm_le K (x-x₀)
  have hs := leastSingular_sub_le L K e hpert
  have hres : K (x-x₀) = (L x-b) - (L-K) x := by
    simp only [map_sub, sub_apply, hexact]
    abel
  have hu := norm_sub_le (L x-b) ((L-K) x)
  rw [← hres] at hu
  have hn : ‖(L-K) x‖ ≤ e*‖x‖ :=
    (ContinuousLinearMap.le_opNorm _ _).trans
      (mul_le_mul_of_nonneg_right hpert (norm_nonneg _))
  apply (le_div_iff₀ (sub_pos.mpr hgap)).mpr
  have hh := mul_le_mul_of_nonneg_right hs (norm_nonneg (x-x₀))
  nlinarith

theorem reference_injective (L K : E →L[ℝ] F) (e : ℝ)
    (hpert : ‖L-K‖ ≤ e) (hgap : e < leastSingular L) : Function.Injective K := by
  intro x y hxy
  have hl := leastSingular_mul_norm_le K (x-y)
  have hs := leastSingular_sub_le L K e hpert
  have hp : 0 < leastSingular K := by linarith
  have hz : K (x-y) = 0 := by simp [hxy]
  rw [hz, norm_zero] at hl
  have : ‖x-y‖ = 0 := by nlinarith [norm_nonneg (x-y)]
  exact sub_eq_zero.mp (norm_eq_zero.mp this)
end Abstract

section Matrices
variable {D : Type*} [Fintype D] [DecidableEq D]

/-- Symmetric matrices with their entrywise Euclidean (Frobenius) inner product. -/
def symmetricSpace (D : Type*) [Fintype D] :
    Submodule ℝ (EuclideanSpace ℝ (D × D)) where
  carrier := {H | ∀ i j, H (i,j) = H (j,i)}
  zero_mem' := by simp
  add_mem' := by intro H K hH hK i j; simp [hH i j, hK i j]
  smul_mem' := by intro a H hH i j; simp [hH i j]

abbrev Symmetric (D : Type*) [Fintype D] := symmetricSpace D

/-- The literal matrix represented by a symmetric Frobenius vector. -/
def matrix (H : Symmetric D) : Matrix D D ℝ := fun i j => H.val (i,j)

omit [DecidableEq D] in
@[simp] theorem matrix_add (H K : Symmetric D) : matrix (H+K) = matrix H+matrix K := rfl
omit [DecidableEq D] in
@[simp] theorem matrix_sub (H K : Symmetric D) : matrix (H-K) = matrix H-matrix K := rfl
omit [DecidableEq D] in
@[simp] theorem matrix_smul (a : ℝ) (H : Symmetric D) : matrix (a•H) = a•matrix H := rfl

omit [DecidableEq D] in
theorem matrix_symmetric (H : Symmetric D) : (matrix H)ᵀ = matrix H := by
  ext i j
  exact H.property j i

/-- The actual invariant-form/trace linear map, with the Euclidean product norm. -/
noncomputable def constraintLinear (A : Matrix D D ℝ) :
    Symmetric D →ₗ[ℝ] EuclideanSpace ℝ ((D × D) ⊕ Unit) where
  toFun H := WithLp.toLp 2 (Sum.elim
    (fun ij => (Aᵀ * matrix H * A - matrix H) ij.1 ij.2)
    (fun _ => Matrix.trace (matrix H)))
  map_add' H K := by
    ext x
    cases x with
    | inl ij => simp [Matrix.mul_add, Matrix.add_mul]; ring
    | inr u => simp [Matrix.trace_add]
  map_smul' a H := by
    ext x
    cases x with
    | inl ij => simp; ring
    | inr u => simp [Matrix.trace_smul]

noncomputable def constraint (A : Matrix D D ℝ) :
    Symmetric D →L[ℝ] EuclideanSpace ℝ ((D × D) ⊕ Unit) :=
  (constraintLinear A).toContinuousLinearMap

@[simp] theorem constraint_matrix (A : Matrix D D ℝ) (H : Symmetric D) (i j : D) :
    constraint A H (Sum.inl (i,j)) = (Aᵀ * matrix H * A - matrix H) i j := rfl

@[simp] theorem constraint_trace (A : Matrix D D ℝ) (H : Symmetric D) :
    constraint A H (Sum.inr ()) = Matrix.trace (matrix H) := rfl

/-- The trace-normalized invariant-form target `(0,1)`. -/
noncomputable def target : EuclideanSpace ℝ ((D × D) ⊕ Unit) :=
  WithLp.toLp 2 (Sum.elim (fun _ => 0) (fun _ => 1))

noncomputable def residual (A : Matrix D D ℝ) (H : Symmetric D) :=
  constraint A H - (target : EuclideanSpace ℝ ((D × D) ⊕ Unit))

open EuclideanMatrixNorms

omit [DecidableEq D] in
theorem frobenius_matrix (H : Symmetric D) : frobenius (matrix H) = ‖H‖ := by
  rfl

omit [DecidableEq D] in
/-- A zero trace coordinate does not alter the Frobenius norm. -/
theorem zero_trace_norm (B : Matrix D D ℝ) :
    ‖(WithLp.toLp 2 (Sum.elim (fun ij : D × D => B ij.1 ij.2)
      (fun _ : Unit => (0 : ℝ))) : EuclideanSpace ℝ ((D × D) ⊕ Unit))‖ = frobenius B := by
  have hs : ‖(WithLp.toLp 2 (Sum.elim (fun ij : D × D => B ij.1 ij.2)
      (fun _ : Unit => (0 : ℝ))) : EuclideanSpace ℝ ((D × D) ⊕ Unit))‖ ^ 2 =
      frobenius B ^ 2 := by
    rw [EuclideanSpace.real_norm_sq_eq, frobenius_sq]
    simp [Fintype.sum_sum_type, Fintype.sum_prod_type]
  nlinarith [norm_nonneg (WithLp.toLp 2 (Sum.elim (fun ij : D × D => B ij.1 ij.2)
      (fun _ : Unit => (0 : ℝ))) : EuclideanSpace ℝ ((D × D) ⊕ Unit)), frobenius_nonneg B]

theorem constraint_difference_norm (A B : Matrix D D ℝ) (H : Symmetric D) :
    ‖(constraint A-constraint B) H‖ =
      frobenius (Aᵀ * matrix H * A - Bᵀ * matrix H * B) := by
  have he : (constraint A-constraint B) H =
      WithLp.toLp 2 (Sum.elim
        (fun ij : D × D => (Aᵀ * matrix H * A - Bᵀ * matrix H * B) ij.1 ij.2)
        (fun _ : Unit => (0 : ℝ))) := by
    ext x
    cases x with
    | inl ij =>
      rcases ij with ⟨i,j⟩
      simp
    | inr u => cases u; simp
  rw [he, zero_trace_norm]

/-- The trace cancels, so the actual induced perturbation is bounded by Euclidean matrix errors. -/
theorem constraint_perturbation (A B : Matrix D D ℝ) :
    ‖constraint A-constraint B‖ ≤
      (spectralNorm A + spectralNorm B) * spectralNorm (A-B) := by
  apply ContinuousLinearMap.opNorm_le_bound _
    (mul_nonneg (add_nonneg (spectralNorm_nonneg A) (spectralNorm_nonneg B))
      (spectralNorm_nonneg (A-B)))
  intro H
  rw [constraint_difference_norm]
  simpa only [frobenius_matrix, mul_assoc] using frobenius_congruence_sub_le A B (matrix H)

/-- The proposal error uses the literal invariant-form map, not an assumed residual identity. -/
theorem invariant_form_error (Ahat Astar : Matrix D D ℝ) (Hhat Hstar : Symmetric D)
    (eM : ℝ) (hpert : ‖constraint Ahat - constraint Astar‖ ≤ eM)
    (hgap : eM < leastSingular (constraint Ahat))
    (hexact : constraint Astar Hstar = target) :
    ‖Hhat-Hstar‖ ≤ (‖residual Ahat Hhat‖ + eM*‖Hhat‖) /
      (leastSingular (constraint Ahat)-eM) :=
  residual_error _ _ _ _ _ _ hpert hgap hexact

/-- Literal Frobenius form of the a posteriori invariant-form error bound. -/
theorem invariant_form_frobenius_error (Ahat Astar : Matrix D D ℝ)
    (Hhat Hstar : Symmetric D) (eM : ℝ)
    (hpert : ‖constraint Ahat-constraint Astar‖ ≤ eM)
    (hgap : eM < leastSingular (constraint Ahat))
    (hexact : constraint Astar Hstar = target) :
    frobenius (matrix Hhat-matrix Hstar) ≤
      (‖residual Ahat Hhat‖+eM*frobenius (matrix Hhat)) /
      (leastSingular (constraint Ahat)-eM) := by
  simpa only [← matrix_sub, frobenius_matrix] using
    invariant_form_error Ahat Astar Hhat Hstar eM hpert hgap hexact

/-- The exact target equation is precisely invariance and trace one. -/
theorem constraint_eq_target_iff (A : Matrix D D ℝ) (H : Symmetric D) :
    constraint A H = target ↔ Aᵀ*matrix H*A = matrix H ∧ Matrix.trace (matrix H) = 1 := by
  constructor
  · intro he
    constructor
    · have hz : Aᵀ*matrix H*A-matrix H = 0 := by
        ext i j
        have h := congrArg (fun x : EuclideanSpace ℝ ((D × D) ⊕ Unit) => x (Sum.inl (i,j))) he
        simpa only [constraint_matrix, target, WithLp.toLp_ofLp, Sum.elim_inl,
          Matrix.sub_apply, Matrix.zero_apply] using h
      exact sub_eq_zero.mp hz
    · have h := congrArg (fun x : EuclideanSpace ℝ ((D × D) ⊕ Unit) => x (Sum.inr ())) he
      exact h
  · rintro ⟨hinv,htr⟩
    ext x
    cases x with
    | inl ij =>
      rcases ij with ⟨i,j⟩
      simp [hinv, target]
    | inr u => cases u; simpa [target] using htr

/-- A matrix-budget version derives the needed map budget from actual matrices. -/
theorem invariant_form_matrix_budget (Ahat Astar : Matrix D D ℝ)
    (Hhat Hstar : Symmetric D) (eM : ℝ)
    (hbudget : (spectralNorm Ahat+spectralNorm Astar)*spectralNorm (Ahat-Astar) ≤ eM)
    (hgap : eM < leastSingular (constraint Ahat))
    (hinv : Astarᵀ*matrix Hstar*Astar = matrix Hstar) (htrace : Matrix.trace (matrix Hstar)=1) :
    frobenius (matrix Hhat-matrix Hstar) ≤
      (‖residual Ahat Hhat‖+eM*frobenius (matrix Hhat)) /
      (leastSingular (constraint Ahat)-eM) :=
  invariant_form_frobenius_error _ _ _ _ _
    ((constraint_perturbation _ _).trans hbudget) hgap
    ((constraint_eq_target_iff _ _).mpr ⟨hinv,htrace⟩)

/-- This is exactly the Euclidean product of Frobenius residual and trace. -/
theorem constraint_norm_sq (A : Matrix D D ℝ) (H : Symmetric D) :
    ‖constraint A H‖ ^ 2 = frobenius (Aᵀ*matrix H*A-matrix H)^2 +
      (Matrix.trace (matrix H))^2 := by
  rw [EuclideanSpace.real_norm_sq_eq, frobenius_sq]
  simp [Fintype.sum_sum_type, Fintype.sum_prod_type, constraint, constraintLinear]

/-- The center is the actual nonsingular-inverse formula, in Euclidean coordinates. -/
noncomputable def fixedCenter (A : Matrix D D ℝ) (b : D → ℝ) : EuclideanSpace ℝ D :=
  WithLp.toLp 2 ((1-A)⁻¹ *ᵥ b)

theorem fixedCenter_equation (A : Matrix D D ℝ) (b : D → ℝ)
    (hunit : IsUnit (1-A).det) :
    Matrix.toEuclideanCLM (𝕜 := ℝ) (1-A) (fixedCenter A b) = WithLp.toLp 2 b := by
  change WithLp.toLp 2 ((1-A) *ᵥ ((1-A)⁻¹ *ᵥ b)) = _
  rw [Matrix.mulVec_mulVec, Matrix.mul_nonsing_inv _ hunit, Matrix.one_mulVec]

theorem center_operator_perturbation (A B : Matrix D D ℝ) :
    ‖Matrix.toEuclideanCLM (𝕜 := ℝ) (1-A) - Matrix.toEuclideanCLM (𝕜 := ℝ) (1-B)‖ =
      spectralNorm (A-B) := by
  rw [← map_sub]
  have he : (1-A)-(1-B) = -(A-B) := by abel
  rw [he, map_neg, norm_neg]
  rfl

/-- The fixed-center estimate uses actual inverse centers and actual spectral perturbation. -/
theorem fixed_center_error (Ahat Astar : Matrix D D ℝ) (bhat bstar : D → ℝ)
    (hhat : IsUnit (1-Ahat).det) (hstar : IsUnit (1-Astar).det)
    (eA eb : ℝ) (hA : spectralNorm (Ahat-Astar) ≤ eA)
    (hb : ‖(WithLp.toLp 2 (bhat-bstar) : EuclideanSpace ℝ D)‖ ≤ eb)
    (hgap : eA < leastSingular (Matrix.toEuclideanCLM (𝕜 := ℝ) (1-Ahat))) :
    ‖fixedCenter Ahat bhat-fixedCenter Astar bstar‖ ≤
      (eb+eA*‖fixedCenter Ahat bhat‖) /
        (leastSingular (Matrix.toEuclideanCLM (𝕜 := ℝ) (1-Ahat))-eA) := by
  have hpert : ‖Matrix.toEuclideanCLM (𝕜 := ℝ) (1-Ahat) -
      Matrix.toEuclideanCLM (𝕜 := ℝ) (1-Astar)‖ ≤ eA := by
    rw [center_operator_perturbation]
    exact hA
  have he := residual_error (E := EuclideanSpace ℝ D) (F := EuclideanSpace ℝ D)
    (Matrix.toEuclideanCLM (𝕜 := ℝ) (1-Ahat))
    (Matrix.toEuclideanCLM (𝕜 := ℝ) (1-Astar))
    (fixedCenter Ahat bhat) (fixedCenter Astar bstar) (WithLp.toLp 2 bstar)
    eA hpert hgap (fixedCenter_equation Astar bstar hstar)
  rw [fixedCenter_equation Ahat bhat hhat] at he
  have hbres : ‖(WithLp.toLp 2 bhat : EuclideanSpace ℝ D)-WithLp.toLp 2 bstar‖ ≤ eb := hb
  exact he.trans ((div_le_div_iff_of_pos_right (sub_pos.mpr hgap)).mpr (by linarith))

end Matrices

end Komorebi.LSM.ProposalError
