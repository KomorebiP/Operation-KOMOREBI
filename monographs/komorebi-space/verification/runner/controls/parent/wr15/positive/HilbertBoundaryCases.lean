import KomorebiSpace.CoordinateCovector

set_option autoImplicit false

open Module Matrix KomorebiSpace KomorebiSpace.CoordinateCovector

noncomputable section

private def scaledBasis : Basis Unit ℝ ℝ :=
  (Basis.singleton Unit ℝ).map (LinearEquiv.smulOfNeZero ℝ ℝ 2 (by norm_num))

private theorem scaledBasis_apply (i : Unit) : scaledBasis i = 2 := by
  simp [scaledBasis]

private def residualBasis : OrthonormalBasis Unit ℝ ℝ :=
  OrthonormalBasis.singleton Unit ℝ

-- A full basis with vector 2 is not orthonormal: its actual Gram entry is 4.
-- Negative alpha is allowed in this algebraic identity. For c=1/4, T=0 and
-- alpha=-2, the actual Hilbert normal residual is -1 and the equation covector
-- is -2. The inverse-Gram certificate is 1, not the raw covector square 4.
example :
    let q := normalResidual
      (operatorMatrix scaledBasis residualBasis (0 : ℝ →L[ℝ] ℝ))
      (gram scaledBasis) (-2) (fun _ => 1 / 4) (orthonormalCoordinates residualBasis 0)
    gram scaledBasis () () = 4 ∧
      q () = -2 ∧
      dotProduct q ((gram scaledBasis)⁻¹ *ᵥ q) = 1 ∧
      synthesis scaledBasis ((gram scaledBasis)⁻¹ *ᵥ q) = -1 := by
  dsimp only
  have hs : synthesis scaledBasis (fun _ => (1 / 4 : ℝ)) = 1 / 2 := by
    norm_num [synthesis_eq_sum, scaledBasis_apply]
  have hg : RegularizedHilbertRepair.gradient (0 : ℝ →L[ℝ] ℝ) (-2) 0
      (synthesis scaledBasis (fun _ => 1 / 4)) = -1 := by
    rw [hs]
    norm_num [RegularizedHilbertRepair.gradient, RegularizedHilbertRepair.normal_apply]
  have hn := gradient_norm_sq_eq_normalResidual scaledBasis residualBasis
    (0 : ℝ →L[ℝ] ℝ) (-2) (fun _ => 1 / 4) 0
  have hr := gradient_eq_synthesis_inverse_normalResidual scaledBasis residualBasis
    (0 : ℝ →L[ℝ] ℝ) (-2) (fun _ => 1 / 4) 0
  constructor
  · simp only [gram, scaledBasis_apply]
    change (2 : ℝ) * 2 = 4
    norm_num
  constructor
  · rw [normalResidual_eq_pairings, hg]
    simp only [pairings, scaledBasis_apply]
    change (-1 : ℝ) * 2 = -2
    norm_num
  constructor
  · rw [← hn, hg]
    norm_num
  · rw [← hr, hg]

-- The actual zero-dimensional Euclidean Hilbert space has an empty full basis.
-- Both the computed equation certificate and the original Hilbert norm apply
-- without adding a nonempty-index or positive-parameter premise.
example (α r : ℝ) (c : Fin 0 → ℝ) :
    let B := (EuclideanSpace.basisFun (Fin 0) ℝ).toBasis
    let T : EuclideanSpace ℝ (Fin 0) →L[ℝ] ℝ := 0
    let q := normalResidual (operatorMatrix B residualBasis T) (gram B) α c
      (orthonormalCoordinates residualBasis r)
    ‖RegularizedHilbertRepair.gradient T α r (synthesis B c)‖ ^ 2 =
        dotProduct q ((gram B)⁻¹ *ᵥ q) ∧
      ‖RegularizedHilbertRepair.gradient T α r (synthesis B c)‖ ^ 2 = 0 := by
  dsimp only
  constructor
  · exact gradient_norm_sq_eq_normalResidual _ _ _ _ _ _
  · exact norm_sq_eq_zero_of_empty_basis
      (EuclideanSpace.basisFun (Fin 0) ℝ).toBasis _
