import KomorebiSpace.CoordinateBasisChange
import KomorebiSpace.ProtectedRegularizedRepair
import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.LinearAlgebra.Matrix.PosDef
import Mathlib.LinearAlgebra.Matrix.ToLin

set_option autoImplicit false

/-!
# Coordinate covectors in an arbitrary full Hilbert basis

The basis is a basis of the entire correction space.  Coefficients and
covectors are finite real coordinate functions; every norm in the certificate
is the original Hilbert norm.  No nonemptiness assumption is made on the basis
index, so the zero-dimensional correction space is included.
-/

noncomputable section
universe u v w
namespace KomorebiSpace.CoordinateCovector
open Module
open scoped RealInnerProductSpace Matrix

variable {ι : Type u} [Fintype ι]
variable {H : Type v} [NormedAddCommGroup H] [InnerProductSpace ℝ H]

/-- Synthesis in a full, possibly nonorthonormal basis. -/
def synthesis (B : Basis ι ℝ H) (c : ι → ℝ) : H := B.equivFun.symm c

/-- The coordinate covector of a vector consists of its pairings with the basis. -/
def pairings (B : Basis ι ℝ H) (x : H) : ι → ℝ := fun i => ⟪B i, x⟫

/-- The Gram matrix uses the actual Hilbert inner product. -/
def gram (B : Basis ι ℝ H) : Matrix ι ι ℝ := fun i j => ⟪B i, B j⟫

theorem synthesis_eq_sum (B : Basis ι ℝ H) (c : ι → ℝ) :
    synthesis B c = ∑ i, c i • B i := by
  exact B.equivFun_symm_apply c

theorem synthesis_injective (B : Basis ι ℝ H) : Function.Injective (synthesis B) :=
  B.equivFun.symm.injective

theorem pairings_synthesis (B : Basis ι ℝ H) (c : ι → ℝ) :
    pairings B (synthesis B c) = (gram B) *ᵥ c := by
  ext i
  simp [pairings, synthesis_eq_sum, gram, Matrix.mulVec, dotProduct, inner_sum,
    real_inner_smul_right, mul_comm]

theorem inner_synthesis (B : Basis ι ℝ H) (c : ι → ℝ) (x : H) :
    ⟪synthesis B c, x⟫ = dotProduct c (pairings B x) := by
  simp [synthesis_eq_sum, pairings, dotProduct, sum_inner, real_inner_smul_left]

theorem gram_posDef (B : Basis ι ℝ H) : (gram B).PosDef := by
  classical
  refine Matrix.PosDef.of_dotProduct_mulVec_pos ?_ ?_
  · ext i j
    simp [Matrix.conjTranspose_apply, gram, real_inner_comm]
  · intro c hc
    have hz : synthesis B c ≠ 0 := by
      intro h
      apply hc
      exact B.equivFun.symm.injective (h.trans (map_zero B.equivFun.symm).symm)
    have hp := real_inner_self_pos.mpr hz
    rw [inner_synthesis, pairings_synthesis] at hp
    simpa using hp

variable [DecidableEq ι]

theorem gram_isUnit (B : Basis ι ℝ H) : IsUnit (gram B) := (gram_posDef B).isUnit

theorem inverse_gram_pairings (B : Basis ι ℝ H) (x : H) :
    (gram B)⁻¹ *ᵥ pairings B x = B.equivFun x := by
  have h : pairings B x = gram B *ᵥ B.equivFun x := by
    rw [← pairings_synthesis]
    simp [synthesis]
  rw [h, Matrix.mulVec_mulVec,
    Matrix.nonsing_inv_mul _ ((gram B).isUnit_iff_isUnit_det.mp (gram_isUnit B)),
    Matrix.one_mulVec]

theorem reconstruct (B : Basis ι ℝ H) (x : H) :
    x = synthesis B ((gram B)⁻¹ *ᵥ pairings B x) := by
  rw [inverse_gram_pairings]
  simp [synthesis]

theorem norm_sq_pairings (B : Basis ι ℝ H) (x : H) :
    ‖x‖ ^ 2 = dotProduct (pairings B x) ((gram B)⁻¹ *ᵥ pairings B x) := by
  rw [← real_inner_self_eq_norm_sq]
  conv_lhs => lhs; rw [reconstruct B x]
  rw [inner_synthesis, dotProduct_comm]

omit [DecidableEq ι] in
/-- The coordinate quadratic uses the Euclidean inner product, never the Pi norm. -/
theorem dotProduct_eq_euclidean_inner (c d : ι → ℝ) :
    dotProduct c d = inner ℝ (WithLp.toLp 2 c : EuclideanSpace ℝ ι)
      (WithLp.toLp 2 d) := by
  simp [PiLp.inner_apply, dotProduct, mul_comm]

/-- An empty full basis gives the zero scalar certificate in the original norm. -/
theorem norm_sq_eq_zero_of_empty_basis [IsEmpty ι] (B : Basis ι ℝ H) (x : H) :
    ‖x‖ ^ 2 = 0 := by
  rw [norm_sq_pairings B]
  simp [dotProduct]

/-- Pairings with the changed full basis transform covariantly. -/
theorem pairings_changedBasis (B : Basis ι ℝ H) (C : Matrix ι ι ℝ)
    (hC : IsUnit C) (x : H) :
    pairings (changedBasis B C hC) x = Cᵀ *ᵥ pairings B x := by
  ext i
  change ⟪changedBasis B C hC i, x⟫ = _
  rw [changedBasis_apply]
  change ⟪synthesis B (fun j => C j i), x⟫ = _
  rw [inner_synthesis]
  rfl

/-- The Gram of the actual changed full basis is the matrix congruence CᵀGC. -/
theorem gram_changedBasis (B : Basis ι ℝ H) (C : Matrix ι ι ℝ)
    (hC : IsUnit C) :
    gram (changedBasis B C hC) = Cᵀ * gram B * C := by
  ext i j
  change ⟪changedBasis B C hC i, changedBasis B C hC j⟫ = _
  rw [changedBasis_apply, changedBasis_apply]
  change ⟪synthesis B (fun k => C k i), synthesis B (fun k => C k j)⟫ = _
  rw [inner_synthesis, pairings_synthesis]
  simp only [dotProduct, Matrix.mulVec, Matrix.mul_apply, Matrix.transpose_apply]
  simp_rw [Finset.mul_sum, Finset.sum_mul]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro k _
  apply Finset.sum_congr rfl
  intro l _
  ring

section OrthonormalCoordinates
variable {κ : Type w} [Fintype κ]

/-- Coordinates in an orthonormal basis, used only for the residual space. -/
def orthonormalCoordinates {Y : Type*} [NormedAddCommGroup Y]
    [InnerProductSpace ℝ Y] (e : OrthonormalBasis κ ℝ Y) (y : Y) : κ → ℝ :=
  fun j => ⟪e j, y⟫

/-- Columns of an arbitrary basis in orthonormal Hilbert coordinates. -/
def basisMatrix (e : OrthonormalBasis κ ℝ H) (B : Basis ι ℝ H) : Matrix κ ι ℝ :=
  fun j i => ⟪e j, B i⟫

omit [Fintype ι] [DecidableEq ι] in
theorem gram_eq_transpose_mul (e : OrthonormalBasis κ ℝ H) (B : Basis ι ℝ H) :
    gram B = (basisMatrix e B)ᵀ * basisMatrix e B := by
  ext i j
  change ⟪B i, B j⟫ = ∑ k, ⟪e k, B i⟫ * ⟪e k, B j⟫
  rw [← e.sum_inner_mul_inner (B i) (B j)]
  apply Finset.sum_congr rfl
  intro k _
  rw [real_inner_comm (B i) (e k)]

variable {Y : Type*} [NormedAddCommGroup Y] [InnerProductSpace ℝ Y]

/-- The literal observation matrix has columns equal to the observed basis vectors. -/
def operatorMatrix (B : Basis ι ℝ H) (e : OrthonormalBasis κ ℝ Y)
    (T : H →L[ℝ] Y) : Matrix κ ι ℝ := fun j i => ⟪e j, T (B i)⟫

omit [DecidableEq ι] in
theorem operatorMatrix_synthesis (B : Basis ι ℝ H) (e : OrthonormalBasis κ ℝ Y)
    (T : H →L[ℝ] Y) (c : ι → ℝ) :
    orthonormalCoordinates e (T (synthesis B c)) = operatorMatrix B e T *ᵥ c := by
  ext j
  simp [orthonormalCoordinates, synthesis_eq_sum, operatorMatrix, map_sum,
    Matrix.mulVec, dotProduct, inner_sum, real_inner_smul_right, mul_comm]

/-- The observation matrix of the changed full basis is SC. -/
theorem operatorMatrix_changedBasis (B : Basis ι ℝ H) (e : OrthonormalBasis κ ℝ Y)
    (T : H →L[ℝ] Y) (C : Matrix ι ι ℝ) (hC : IsUnit C) :
    operatorMatrix (changedBasis B C hC) e T = operatorMatrix B e T * C := by
  ext j i
  change ⟪e j, T (changedBasis B C hC i)⟫ = _
  rw [changedBasis_apply]
  exact congrFun (operatorMatrix_synthesis B e T (fun k => C k i)) j

/-- The computed residual in the changed basis is exactly Cᵀq. -/
theorem computed_normalResidual_changedBasis
    (B : Basis ι ℝ H) (e : OrthonormalBasis κ ℝ Y) (T : H →L[ℝ] Y)
    (C : Matrix ι ι ℝ) (hC : IsUnit C) (α : ℝ) (c : ι → ℝ) (r : Y) :
    normalResidual (operatorMatrix (changedBasis B C hC) e T)
        (gram (changedBasis B C hC)) α (C⁻¹ *ᵥ c) (orthonormalCoordinates e r) =
      Cᵀ *ᵥ normalResidual (operatorMatrix B e T) (gram B) α c
        (orthonormalCoordinates e r) := by
  rw [operatorMatrix_changedBasis, gram_changedBasis]
  exact normalResidual_basis_change _ _ _ hC _ _ _

/-- WR15 invariance for two actual full bases of the same Hilbert space. -/
theorem computed_certificate_changedBasis
    (B : Basis ι ℝ H) (e : OrthonormalBasis κ ℝ Y) (T : H →L[ℝ] Y)
    (C : Matrix ι ι ℝ) (hC : IsUnit C) (α : ℝ) (c : ι → ℝ) (r : Y) :
    let B' := changedBasis B C hC
    let q' := normalResidual (operatorMatrix B' e T) (gram B') α (C⁻¹ *ᵥ c)
      (orthonormalCoordinates e r)
    let q := normalResidual (operatorMatrix B e T) (gram B) α c
      (orthonormalCoordinates e r)
    dotProduct q' ((gram B')⁻¹ *ᵥ q') = dotProduct q ((gram B)⁻¹ *ᵥ q) := by
  dsimp only
  rw [operatorMatrix_changedBasis, gram_changedBasis]
  exact normalResidual_certificate_basis_change _ _ _ hC _ _ _

variable [CompleteSpace H] [CompleteSpace Y]

omit [Fintype ι] [DecidableEq ι] in
theorem pairings_adjoint (B : Basis ι ℝ H) (e : OrthonormalBasis κ ℝ Y)
    (T : H →L[ℝ] Y) (y : Y) :
    pairings B (T.adjoint y) = (operatorMatrix B e T)ᵀ *ᵥ orthonormalCoordinates e y := by
  ext i
  change ⟪B i, T.adjoint y⟫ = ∑ j, ⟪e j, T (B i)⟫ * ⟪e j, y⟫
  rw [ContinuousLinearMap.adjoint_inner_right, ← e.sum_inner_mul_inner (T (B i)) y]
  apply Finset.sum_congr rfl
  intro j _
  rw [real_inner_comm (T (B i)) (e j)]

omit [DecidableEq ι] in
/-- The displayed normal-equation residual is derived to be the covector of the
accepted Hilbert normal residual; this is not an additional assumption. -/
theorem normalResidual_eq_pairings (B : Basis ι ℝ H) (e : OrthonormalBasis κ ℝ Y)
    (T : H →L[ℝ] Y) (α : ℝ) (c : ι → ℝ) (r : Y) :
    normalResidual (operatorMatrix B e T) (gram B) α c (orthonormalCoordinates e r) =
      pairings B (RegularizedHilbertRepair.gradient T α r (synthesis B c)) := by
  have hT := pairings_adjoint B e T (T (synthesis B c))
  rw [operatorMatrix_synthesis] at hT
  have hr := pairings_adjoint B e T r
  have hG := pairings_synthesis B c
  ext i
  simp only [normalResidual, Matrix.add_mulVec, Matrix.smul_mulVec,
    ← Matrix.mulVec_mulVec, Pi.sub_apply, Pi.add_apply,
    Pi.smul_apply, smul_eq_mul]
  change _ = ⟪B i, T.adjoint (T (synthesis B c)) + α • synthesis B c - T.adjoint r⟫
  rw [inner_sub_right, inner_add_right, real_inner_smul_right]
  rw [← congrFun hT i, ← congrFun hr i, ← congrFun hG i]
  rfl

/-- WR15: the actual normal residual is obtained by the inverse Gram metric. -/
theorem gradient_eq_synthesis_inverse_normalResidual
    (B : Basis ι ℝ H) (e : OrthonormalBasis κ ℝ Y)
    (T : H →L[ℝ] Y) (α : ℝ) (c : ι → ℝ) (r : Y) :
    RegularizedHilbertRepair.gradient T α r (synthesis B c) =
      synthesis B ((gram B)⁻¹ *ᵥ
        normalResidual (operatorMatrix B e T) (gram B) α c (orthonormalCoordinates e r)) := by
  rw [normalResidual_eq_pairings]
  exact reconstruct B _

/-- WR15: the Gram-corrected scalar is the squared original Hilbert norm. -/
theorem gradient_norm_sq_eq_normalResidual
    (B : Basis ι ℝ H) (e : OrthonormalBasis κ ℝ Y)
    (T : H →L[ℝ] Y) (α : ℝ) (c : ι → ℝ) (r : Y) :
    ‖RegularizedHilbertRepair.gradient T α r (synthesis B c)‖ ^ 2 =
      dotProduct
        (normalResidual (operatorMatrix B e T) (gram B) α c (orthonormalCoordinates e r))
        ((gram B)⁻¹ *ᵥ
          normalResidual (operatorMatrix B e T) (gram B) α c (orthonormalCoordinates e r)) := by
  rw [normalResidual_eq_pairings]
  exact norm_sq_pairings B _

end OrthonormalCoordinates

section ProtectedKernel
variable {E Y Z : Type*}
variable [NormedAddCommGroup E] [InnerProductSpace ℝ E] [CompleteSpace E]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
variable [NormedAddCommGroup Z] [NormedSpace ℝ Z]
variable {κ η : Type*} [Fintype κ] [Fintype η]
variable (D : E →L[ℝ] Y) (p : E →L[ℝ] Z)

omit [Fintype ι] [DecidableEq ι] in
/-- The accepted gradient is the projected ambient normal residual on the whole kernel. -/
theorem protected_gradient_eq_projected (α : ℝ) (r : Y) (a : p.ker) :
    RegularizedHilbertRepair.gradient (ProtectedHilbertRepair.restricted D p) α r a =
      p.ker.orthogonalProjectionOnto (D.adjoint (D a.val - r)) + α • a := by
  rw [← ProtectedRegularizedRepair.restricted_adjoint, map_sub]
  unfold RegularizedHilbertRepair.gradient
  rw [RegularizedHilbertRepair.normal_apply]
  change _ = ((ProtectedHilbertRepair.restricted D p).adjoint
    ((ProtectedHilbertRepair.restricted D p) a) -
    (ProtectedHilbertRepair.restricted D p).adjoint r) + α • a
  abel

omit [Fintype ι] [DecidableEq ι] [CompleteSpace E] in
/-- The arbitrary full kernel basis has the literal ambient Gram matrix BᵀB. -/
theorem protected_gram_eq_transpose_mul (B : Basis ι ℝ p.ker)
    (eE : OrthonormalBasis η ℝ E) :
    gram B = (operatorMatrix B eE p.ker.subtypeL)ᵀ *
      operatorMatrix B eE p.ker.subtypeL := by
  ext i j
  change ⟪(B i).val, (B j).val⟫ =
    ∑ k, ⟪eE k, (B i).val⟫ * ⟪eE k, (B j).val⟫
  rw [← eE.sum_inner_mul_inner (B i).val (B j).val]
  apply Finset.sum_congr rfl
  intro k _
  rw [real_inner_comm (B i).val (eE k)]

omit [Fintype ι] [DecidableEq ι] [CompleteSpace E] [CompleteSpace Y] in
/-- In ambient and residual orthonormal coordinates, the observation matrix is dB. -/
theorem protected_operatorMatrix_eq_mul (B : Basis ι ℝ p.ker)
    (eE : OrthonormalBasis η ℝ E) (eY : OrthonormalBasis κ ℝ Y) :
    operatorMatrix B eY (ProtectedHilbertRepair.restricted D p) =
      operatorMatrix eE.toBasis eY D * operatorMatrix B eE p.ker.subtypeL := by
  ext j i
  change ⟪eY j, D (B i).val⟫ =
    ∑ k, ⟪eY j, D (eE k)⟫ * ⟪eE k, (B i).val⟫
  conv_lhs => rw [← eE.sum_repr' (B i).val]
  simp only [map_sum, map_smul, inner_sum, real_inner_smul_right]
  apply Finset.sum_congr rfl
  intro k _
  exact mul_comm _ _

/-- WR15 on the actual protected kernel: g=B G⁻¹q, with q computed from S=dB. -/
theorem protected_gradient_eq_synthesis_inverse_normalResidual
    (B : Basis ι ℝ p.ker) (eY : OrthonormalBasis κ ℝ Y)
    (α : ℝ) (c : ι → ℝ) (r : Y) :
    p.ker.orthogonalProjectionOnto (D.adjoint (D (synthesis B c).val - r)) +
        α • synthesis B c =
      synthesis B ((gram B)⁻¹ *ᵥ
        normalResidual (operatorMatrix B eY (ProtectedHilbertRepair.restricted D p))
          (gram B) α c (orthonormalCoordinates eY r)) := by
  rw [← protected_gradient_eq_projected]
  exact gradient_eq_synthesis_inverse_normalResidual B eY _ α c r

/-- WR15 retains the ambient Hilbert norm, including for the zero kernel. -/
theorem protected_gradient_norm_sq_eq_normalResidual
    (B : Basis ι ℝ p.ker) (eY : OrthonormalBasis κ ℝ Y)
    (α : ℝ) (c : ι → ℝ) (r : Y) :
    ‖(p.ker.orthogonalProjectionOnto (D.adjoint (D (synthesis B c).val - r))).val +
        α • (synthesis B c).val‖ ^ 2 =
      dotProduct
        (normalResidual (operatorMatrix B eY (ProtectedHilbertRepair.restricted D p))
          (gram B) α c (orthonormalCoordinates eY r))
        ((gram B)⁻¹ *ᵥ
          normalResidual (operatorMatrix B eY (ProtectedHilbertRepair.restricted D p))
            (gram B) α c (orthonormalCoordinates eY r)) := by
  have h := gradient_norm_sq_eq_normalResidual B eY
    (ProtectedHilbertRepair.restricted D p) α c r
  rw [protected_gradient_eq_projected] at h
  exact h

end ProtectedKernel

end KomorebiSpace.CoordinateCovector
