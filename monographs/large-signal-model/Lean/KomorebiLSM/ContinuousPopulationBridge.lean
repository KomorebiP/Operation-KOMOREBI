import KomorebiLSM.FiniteMomentIdentification
import KomorebiLSM.CertifiedTemplate

/-! P61's population-to-instrument bridge. The dimension and degree are the
declared finite state and coefficient types. The population core is square in
that supplied dimension; no rank or degree discovery is inferred from it. -/
set_option autoImplicit false
namespace Komorebi.LSM.ContinuousPopulationBridge
open Matrix
open scoped BigOperators

abbrev State (r : ℕ) := Fin r → ℝ
abbrev Operator (r : ℕ) := Matrix (Fin r) (Fin r) ℝ

/-- The literal finite matrix action as a continuous linear map. -/
noncomputable def matrixCLM {r : ℕ} : Operator r →ₗ[ℝ] (State r →L[ℝ] State r) :=
  LinearMap.toContinuousLinearMap.toLinearMap.comp Matrix.toLin'.toLinearMap

@[simp] theorem matrixCLM_apply {r : ℕ} (B : Operator r) (z : State r) :
    matrixCLM B z=B *ᵥ z := rfl

variable {r degree : ℕ} {A : Type*}

noncomputable def originalCoefficients (C : A → Fin (degree+1) → Operator r)
    (a : A) (k : Fin (degree+1)) : State r →L[ℝ] State r := matrixCLM (C a k)

/-- These are the actual inverse-moment population-table coefficients. -/
noncomputable def fittedCoefficients (T S : Operator r)
    (C : A → Fin (degree+1) → Operator r) (a : A) (k : Fin (degree+1)) :
    State r →L[ℝ] State r :=
  matrixCLM (FiniteMomentIdentification.reconstructedCoefficient
    (FiniteMomentIdentification.populationCore T S)
    (FiniteMomentIdentification.populationTable T S (C a)) k)

/-- The coordinate isomorphism is derived from the true square population
core, rather than supplied as an identification conclusion. -/
noncomputable def populationEquiv (T S : Operator r)
    (hcore : IsUnit (FiniteMomentIdentification.populationCore T S)) :
    State r ≃ₗ[ℝ] State r :=
  LinearEquiv.ofBijective T.mulVecLin
    ⟨Matrix.mulVec_injective_iff_isUnit.mpr
        (FiniteMomentIdentification.core_factors_isUnit T S hcore).1,
      Matrix.mulVec_surjective_iff_isUnit.mpr
        (FiniteMomentIdentification.core_factors_isUnit T S hcore).1⟩

@[simp] theorem populationEquiv_apply (T S : Operator r)
    (hcore : IsUnit (FiniteMomentIdentification.populationCore T S)) (z : State r) :
    populationEquiv T S hcore z=T *ᵥ z := rfl

theorem populationEquiv_symm_apply (T S : Operator r)
    (hcore : IsUnit (FiniteMomentIdentification.populationCore T S)) (z : State r) :
    (populationEquiv T S hcore).symm z=T⁻¹ *ᵥ z := by
  apply (populationEquiv T S hcore).injective
  rw [LinearEquiv.apply_symm_apply,populationEquiv_apply,Matrix.mulVec_mulVec,
    Matrix.mul_nonsing_inv T ((Matrix.isUnit_iff_isUnit_det T).mp
      (FiniteMomentIdentification.core_factors_isUnit T S hcore).1),Matrix.one_mulVec]

/-- Exact reconstruction is proved coefficient by coefficient. -/
theorem fitted_coefficient_identification (T S : Operator r)
    (hcore : IsUnit (FiniteMomentIdentification.populationCore T S))
    (C : A → Fin (degree+1) → Operator r) (a : A) (k : Fin (degree+1)) :
    fittedCoefficients T S C a k=matrixCLM (T * C a k * T⁻¹) := by
  rw [fittedCoefficients,FiniteMomentIdentification.reconstructedCoefficient_eq T S hcore]

/-- Integrating the declared polynomial coefficient family and evaluating the
continuous operator gives the same literal matrix density. -/
theorem polynomial_matrix_density (C : Fin (degree+1) → Operator r) (u : ℝ) :
    PolynomialGram.operatorPolynomial (fun k => matrixCLM (C k)) u=
      matrixCLM (FiniteMomentIdentification.density C u) := by
  rw [FiniteMomentIdentification.density,map_sum]
  simp only [map_smul]
  rfl

theorem fitted_density_identification (T S : Operator r)
    (hcore : IsUnit (FiniteMomentIdentification.populationCore T S))
    (C : A → Fin (degree+1) → Operator r) (a : A) (u : ℝ) :
    PolynomialGram.operatorPolynomial (fittedCoefficients T S C a) u=
      matrixCLM (T * FiniteMomentIdentification.density (C a) u * T⁻¹) := by
  change PolynomialGram.operatorPolynomial
    (fun k => matrixCLM (FiniteMomentIdentification.reconstructedCoefficient
      (FiniteMomentIdentification.populationCore T S)
      (FiniteMomentIdentification.populationTable T S (C a)) k)) u=_
  rw [polynomial_matrix_density,FiniteMomentIdentification.reconstructed_density_eq T S hcore]

/-- The coefficient matching used by exact atlas transport is derived from
the population reconstruction formula, rather than assumed. -/
theorem population_coefficient_match (T S : Operator r)
    (hcore : IsUnit (FiniteMomentIdentification.populationCore T S))
    (C : A → Fin (degree+1) → Operator r) (a : A) (k : Fin (degree+1)) (z : State r) :
    fittedCoefficients T S C a k (populationEquiv T S hcore z)=
      populationEquiv T S hcore (originalCoefficients C a k z) := by
  rw [fitted_coefficient_identification T S hcore,populationEquiv_apply,matrixCLM_apply,
    originalCoefficients,matrixCLM_apply,populationEquiv_apply]
  rw [← Matrix.mulVec_mulVec,FiniteMomentIdentification.initial_test_coordinates T S hcore,
    ← Matrix.mulVec_mulVec]

/-- The inverse atlas recovers the literal original coefficient family too.
No inverse operator or record-law match is an assumed identification field. -/
theorem population_inverse_coefficient_match (T S : Operator r)
    (hcore : IsUnit (FiniteMomentIdentification.populationCore T S))
    (C : A → Fin (degree+1) → Operator r) (a : A) (k : Fin (degree+1)) (x : State r) :
    originalCoefficients C a k ((populationEquiv T S hcore).symm x)=
      (populationEquiv T S hcore).symm (fittedCoefficients T S C a k x) := by
  apply (populationEquiv T S hcore).injective
  rw [LinearEquiv.apply_symm_apply]
  have h := population_coefficient_match T S hcore C a k ((populationEquiv T S hcore).symm x)
  simpa only [LinearEquiv.apply_symm_apply] using h.symm

/-- Every finite fine-observation word has the reconstructed test coordinates,
not only the finitely many moments used to identify the coefficients. -/
theorem fitted_word_coordinates (T S : Operator r)
    (hcore : IsUnit (FiniteMomentIdentification.populationCore T S))
    (C : A → Fin (degree+1) → Operator r) (word : List (A × ℝ)) (z : State r) :
    FiniteInstruments.wordAction
      (fun s : A × ℝ => (PolynomialGram.operatorPolynomial (fittedCoefficients T S C s.1) s.2).toLinearMap)
      word (T *ᵥ z)=T *ᵥ FiniteMomentIdentification.wordState
        (fun a => FiniteMomentIdentification.density (C a)) word z := by
  induction word generalizing z with
  | nil => rfl
  | cons s word ih =>
    rw [FiniteInstruments.wordAction_cons,LinearMap.comp_apply,
      fitted_density_identification T S hcore]
    change FiniteInstruments.wordAction
      (fun t : A × ℝ => (PolynomialGram.operatorPolynomial (fittedCoefficients T S C t.1) t.2).toLinearMap)
      word ((T * FiniteMomentIdentification.density (C s.1) s.2 * T⁻¹) *ᵥ (T *ᵥ z))=_
    rw [← Matrix.mulVec_mulVec,FiniteMomentIdentification.initial_test_coordinates T S hcore,
      ← Matrix.mulVec_mulVec,ih]
    rfl

/-- A checked mass-row coordinate identity carries all represented word
likelihoods. No stochastic validity or likelihood equality is an input field. -/
theorem fitted_word_likelihood (T S : Operator r)
    (hcore : IsUnit (FiniteMomentIdentification.populationCore T S))
    (C : A → Fin (degree+1) → Operator r)
    (l lhat : State r →ₗ[ℝ] ℝ) (hmass : lhat.comp T.mulVecLin=l)
    (word : List (A × ℝ)) (z : State r) :
    lhat (FiniteInstruments.wordAction
      (fun s : A × ℝ => (PolynomialGram.operatorPolynomial (fittedCoefficients T S C s.1) s.2).toLinearMap)
      word (T *ᵥ z))=
      l (FiniteMomentIdentification.wordState (fun a => FiniteMomentIdentification.density (C a)) word z) := by
  rw [fitted_word_coordinates T S hcore]
  exact congrArg (fun L : State r →ₗ[ℝ] ℝ => L
    (FiniteMomentIdentification.wordState (fun a => FiniteMomentIdentification.density (C a)) word z)) hmass

end Komorebi.LSM.ContinuousPopulationBridge
