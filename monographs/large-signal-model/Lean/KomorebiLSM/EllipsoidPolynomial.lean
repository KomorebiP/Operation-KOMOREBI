import KomorebiLSM.OrientedEllipsoid
import KomorebiLSM.ContinuousRecords

/-! Finite polynomial/SOS witnesses for the oriented quadratic certificate. -/
set_option autoImplicit false
namespace Komorebi.LSM.OrientedEllipsoid
open scoped BigOperators Matrix Polynomial
open MeasureTheory
variable {D : Type*} [Fintype D] [DecidableEq D]

/-- The literal matrix action as a continuous linear map, with no extra positivity field. -/
noncomputable def matrixOperator : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ →ₗ[ℝ]
    (State D →L[ℝ] State D) :=
  LinearMap.toContinuousLinearMap.toLinearMap.comp Matrix.toLin'.toLinearMap

@[simp] theorem matrixOperator_apply (B : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ) (z : State D) :
    matrixOperator B z = B *ᵥ z := rfl

noncomputable def matrixPolynomial {n : ℕ}
    (B : Fin n → Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ) :
    Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ[X] :=
  fun i j => Polynomial.ofFn n (fun k => B k i j)

omit [Fintype D] [DecidableEq D] in
theorem matrixPolynomial_eval {n : ℕ} (B : Fin n → Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ)
    (u : ℝ) : PolynomialGram.evalMatrix (matrixPolynomial B) u = ∑ k : Fin n, u^(k:ℕ) • B k := by
  ext i j
  simp [matrixPolynomial,PolynomialGram.evalMatrix,UniformIntervalMoments.eval_ofFn,
    Matrix.sum_apply,Matrix.smul_apply,mul_comm]

noncomputable def polynomialOperator {n : ℕ}
    (B : Fin n → Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ) : ℝ → State D →L[ℝ] State D :=
  PolynomialGram.operatorPolynomial (fun k => matrixOperator (B k))

theorem polynomialOperator_matrix {n : ℕ}
    (B : Fin n → Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ) (u : ℝ) :
    polynomialOperator B u = matrixOperator (PolynomialGram.evalMatrix (matrixPolynomial B) u) := by
  rw [matrixPolynomial_eval,map_sum]
  simp only [map_smul]
  rfl

/-- A finite check of scalar coefficients, including the coefficients above neither degree. -/
theorem scalar_coefficient_identity (p q : ℝ[X]) (bound : ℕ)
    (hp : p.natDegree≤bound) (hq : q.natDegree≤bound)
    (hc : ∀ k : Fin (bound+1),p.coeff k=q.coeff k) : p=q := by
  ext k
  by_cases hk : k<bound+1
  · exact hc ⟨k,hk⟩
  · rw [Polynomial.coeff_eq_zero_of_natDegree_lt (lt_of_le_of_lt hp (by omega)),
      Polynomial.coeff_eq_zero_of_natDegree_lt (lt_of_le_of_lt hq (by omega))]

noncomputable def scalarSOS {n m : ℕ} (f : Fin n → ℝ[X]) (g : Fin m → ℝ[X]) : ℝ[X] :=
  (∑ i,(f i)^2) + (1-Polynomial.X^2)*(∑ j,(g j)^2)

theorem scalarSOS_nonneg {n m : ℕ} (f : Fin n → ℝ[X]) (g : Fin m → ℝ[X])
    (u : ℝ) (hu : u∈Set.Icc (-1 : ℝ) 1) : 0≤(scalarSOS f g).eval u := by
  have hfactor : 0≤1-u^2 := by nlinarith [hu.1,hu.2]
  simp only [scalarSOS,Polynomial.eval_add,Polynomial.eval_finsetSum,Polynomial.eval_pow,
    Polynomial.eval_mul,Polynomial.eval_sub,Polynomial.eval_one,Polynomial.eval_X]
  exact add_nonneg (Finset.sum_nonneg (fun i _ => sq_nonneg _))
    (mul_nonneg hfactor (Finset.sum_nonneg (fun j _ => sq_nonneg _)))

/-- Scalar interval SOS identities are checked by finitely many actual coefficients. -/
structure ScalarCertificate (p : ℝ[X]) where
  terms0 : ℕ
  terms1 : ℕ
  square0 : Fin terms0 → ℝ[X]
  square1 : Fin terms1 → ℝ[X]
  bound : ℕ
  degree_left : p.natDegree≤bound
  degree_right : (scalarSOS square0 square1).natDegree≤bound
  coefficients : ∀ k : Fin (bound+1),p.coeff k=(scalarSOS square0 square1).coeff k

theorem ScalarCertificate.nonneg {p : ℝ[X]} (cert : ScalarCertificate p)
    (u : ℝ) (hu : u∈Set.Icc (-1 : ℝ) 1) : 0≤p.eval u := by
  rw [scalar_coefficient_identity p _ cert.bound cert.degree_left cert.degree_right cert.coefficients]
  exact scalarSOS_nonneg cert.square0 cert.square1 u hu

noncomputable def betaPolynomial (c : D → ℝ)
    (P : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ[X]) : ℝ[X] :=
  P (Sum.inl ()) (Sum.inl ()) + ∑ i,Polynomial.C (c i)*P (Sum.inl ()) (Sum.inr i)

noncomputable def dualPolynomial (H : Matrix D D ℝ)
    (P : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ[X]) : ℝ[X] :=
  ∑ i,∑ j,Polynomial.C (H⁻¹ i j)*P (Sum.inl ()) (Sum.inr i)*P (Sum.inl ()) (Sum.inr j)

omit [DecidableEq D] in
theorem betaPolynomial_eval (c : D → ℝ)
    (P : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ[X]) (u : ℝ) :
    (betaPolynomial c P).eval u = beta c (PolynomialGram.evalMatrix P u) := by
  simp [Polynomial.eval_finsetSum,betaPolynomial,beta,massConstant,massSpatial,PolynomialGram.evalMatrix,dotProduct,mul_comm]

theorem dualPolynomial_eval (H : Matrix D D ℝ)
    (P : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ[X]) (u : ℝ) :
    (dualPolynomial H P).eval u = massSpatial (PolynomialGram.evalMatrix P u) ⬝ᵥ
      (H⁻¹ *ᵥ massSpatial (PolynomialGram.evalMatrix P u)) := by
  simp only [dualPolynomial,Polynomial.eval_finsetSum,Polynomial.eval_mul,Polynomial.eval_C,
    dotProduct,Matrix.mulVec,massSpatial,PolynomialGram.evalMatrix,Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro i _
  apply Finset.sum_congr rfl
  intro j _
  ring

noncomputable def quadraticPolynomial (c : D → ℝ) (H : Matrix D D ℝ)
    (P : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ[X]) (tau : ℝ[X]) :
    Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ[X] :=
  P.transpose * PolynomialGram.constantMatrix (Q c H) * P -
    tau • PolynomialGram.constantMatrix (Q c H)

omit [Fintype D] [DecidableEq D] in
theorem evalMatrix_sub (P T : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ[X]) (u : ℝ) :
    PolynomialGram.evalMatrix (P-T) u = PolynomialGram.evalMatrix P u - PolynomialGram.evalMatrix T u := by
  ext i j
  change (P i j-T i j).eval u = (P i j).eval u - (T i j).eval u
  exact Polynomial.eval_sub (P i j) (T i j) u

theorem quadraticPolynomial_eval (c : D → ℝ) (H : Matrix D D ℝ)
    (P : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ[X]) (tau : ℝ[X]) (u : ℝ) :
    PolynomialGram.evalMatrix (quadraticPolynomial c H P tau) u =
      (PolynomialGram.evalMatrix P u).transpose * Q c H * PolynomialGram.evalMatrix P u -
        tau.eval u • Q c H := by
  rw [quadraticPolynomial,evalMatrix_sub,PolynomialGram.evalMatrix_mul,
    PolynomialGram.evalMatrix_mul,PolynomialGram.evalMatrix_transpose,
    PolynomialGram.evalMatrix_constant,PolynomialGram.evalMatrix_scalar,
    PolynomialGram.evalMatrix_constant]

/-- Finite scalar SOS and matrix-Gram coefficient checks certify the complete interval. -/
structure PolynomialCertificate (c : D → ℝ) (H : Matrix D D ℝ) {A : Type*} {n : ℕ}
    (B : A → Fin n → Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ) (q bound : ℕ) where
  tau : A → ℝ[X]
  tauSOS : ∀ a,ScalarCertificate (tau a)
  betaSOS : ∀ a,ScalarCertificate (betaPolynomial c (matrixPolynomial (B a)))
  orientationSOS : ∀ a,ScalarCertificate
    ((betaPolynomial c (matrixPolynomial (B a)))^2-dualPolynomial H (matrixPolynomial (B a)))
  gram0 : A → Matrix (Fin (q+1) × (Unit ⊕ D)) (Fin (q+1) × (Unit ⊕ D)) ℝ
  gram1 : A → Matrix (Fin q × (Unit ⊕ D)) (Fin q × (Unit ⊕ D)) ℝ
  gram0_positive : ∀ a,(gram0 a).PosSemidef
  gram1_positive : ∀ a,(gram1 a).PosSemidef
  degree_left : ∀ a i j,(quadraticPolynomial c H (matrixPolynomial (B a)) (tau a) i j).natDegree≤bound
  degree_right : ∀ a i j,(PolynomialGram.intervalGramPolynomial q (gram0 a) (gram1 a) i j).natDegree≤bound
  coefficients : ∀ a i j (k : Fin (bound+1)),
    (quadraticPolynomial c H (matrixPolynomial (B a)) (tau a) i j).coeff k =
      (PolynomialGram.intervalGramPolynomial q (gram0 a) (gram1 a) i j).coeff k
  mass_moments : ∀ a i,mass ((∑ k : Fin n,UniformIntervalMoments.moment k • matrixOperator (B a k))
    (Pi.basisFun ℝ (Unit ⊕ D) i))=mass (Pi.basisFun ℝ (Unit ⊕ D) i)

/-- A full polynomial-family quadratic witness constructs the literal P52 instrument. -/
noncomputable def polynomialDensityInstrument (c : D → ℝ) (H : Matrix D D ℝ)
    (hH : H.PosDef) {A : Type*} {n : ℕ}
    (B : A → Fin n → Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ)
    (branches : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 →
      BranchCertificate c H (PolynomialGram.evalMatrix (matrixPolynomial (B a)) u))
    (hm : ∀ a z,mass ((∑ k : Fin n,UniformIntervalMoments.moment k • matrixOperator (B a k)) z)=mass z) :
    ContinuousInstrument.DensityInstrument (A := A) (probabilityCone c H hH)
      UniformIntervalMoments.measure where
  op a := polynomialOperator (B a)
  measurable_op a := (PolynomialGram.operatorPolynomial_continuous
    (fun k => matrixOperator (B a k))).measurable
  integrable_op a := PolynomialGram.operatorPolynomial_integrable (fun k => matrixOperator (B a k))
  positive a := by
    filter_upwards [PolynomialGram.uniform_ae_interval] with u hu
    intro z hz
    change polynomialOperator (B a) u z∈cone c H
    rw [polynomialOperator_matrix,matrixOperator_apply]
    exact BranchCertificate.preserves hH (branches a u hu) hz
  mass_preserving a z := by
    change mass ((∫ u,PolynomialGram.operatorPolynomial (fun k => matrixOperator (B a k)) u
      ∂UniformIntervalMoments.measure) z)=mass z
    rw [PolynomialGram.operatorPolynomial_integral]
    exact hm a z

@[simp] theorem polynomialDensityInstrument_op (c : D → ℝ) (H : Matrix D D ℝ)
    (hH : H.PosDef) {A : Type*} {n : ℕ}
    (B : A → Fin n → Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ)
    (branches : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 →
      BranchCertificate c H (PolynomialGram.evalMatrix (matrixPolynomial (B a)) u))
    (hm : ∀ a z,mass ((∑ k : Fin n,UniformIntervalMoments.moment k • matrixOperator (B a k)) z)=mass z)
    (a : A) (u : ℝ) :
    (polynomialDensityInstrument c H hH B branches hm).op a u =
      matrixOperator (PolynomialGram.evalMatrix (matrixPolynomial (B a)) u) :=
  polynomialOperator_matrix (B a) u

namespace PolynomialCertificate
variable {c : D → ℝ} {H : Matrix D D ℝ} {A : Type*} {n q bound : ℕ}
  {B : A → Fin n → Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ}
  (cert : PolynomialCertificate c H B q bound)
include cert

/-- Finite SOS/coefficient data imply every hypothesis at every interval point. -/
noncomputable def branch (a : A) (u : ℝ) (hu : u∈Set.Icc (-1 : ℝ) 1) :
    BranchCertificate c H (PolynomialGram.evalMatrix (matrixPolynomial (B a)) u) where
  tau := (cert.tau a).eval u
  remainder := PolynomialGram.intervalGram q (cert.gram0 a) (cert.gram1 a) u
  tau_nonneg := (cert.tauSOS a).nonneg u hu
  remainder_positive := PolynomialGram.interval_gram_positive q (cert.gram0 a) (cert.gram1 a)
    (cert.gram0_positive a) (cert.gram1_positive a) u hu
  identity := by
    have he := (PolynomialGram.polynomial_identity_finite
      (quadraticPolynomial c H (matrixPolynomial (B a)) (cert.tau a))
      (PolynomialGram.intervalGramPolynomial q (cert.gram0 a) (cert.gram1 a)) bound
      (cert.degree_left a) (cert.degree_right a)).mpr (cert.coefficients a) u
    rwa [quadraticPolynomial_eval,PolynomialGram.intervalGramPolynomial_eval] at he
  beta_nonneg := by
    simpa only [betaPolynomial_eval] using (cert.betaSOS a).nonneg u hu
  orientation := by
    simpa only [Polynomial.eval_sub,Polynomial.eval_pow,betaPolynomial_eval,dualPolynomial_eval]
      using (cert.orientationSOS a).nonneg u hu

/-- The finite basis moment checks imply the exact integrated mass functional identity. -/
theorem mass_preserving (a : A) (z : State D) :
    mass ((∑ k : Fin n,UniformIntervalMoments.moment k • matrixOperator (B a k)) z)=mass z :=
  (PolynomialGram.moment_mass_finite (Pi.basisFun ℝ (Unit ⊕ D)) mass
    (fun k => matrixOperator (B a k))).mpr (cert.mass_moments a) z

noncomputable def instrument (hH : H.PosDef) :
    ContinuousInstrument.DensityInstrument (A := A) (probabilityCone c H hH)
      UniformIntervalMoments.measure :=
  polynomialDensityInstrument c H hH B cert.branch cert.mass_preserving

@[simp] theorem instrument_op (hH : H.PosDef) (a : A) (u : ℝ) :
    (cert.instrument hH).op a u = matrixOperator
      (PolynomialGram.evalMatrix (matrixPolynomial (B a)) u) :=
  polynomialDensityInstrument_op c H hH B cert.branch cert.mass_preserving a u

/-- Positivity is pointwise on the entire closed interval, including its endpoints. -/
theorem preserves (hH : H.PosDef) (a : A) (u : ℝ) (hu : u∈Set.Icc (-1 : ℝ) 1)
    {z : State D} (hz : z∈cone c H) : polynomialOperator (B a) u z∈cone c H := by
  rw [polynomialOperator_matrix,matrixOperator_apply]
  exact BranchCertificate.preserves hH (cert.branch a u hu) hz

/-- Every literal finite product of interval observation operators stays in the actual cone. -/
theorem word_cone (hH : H.PosDef) (word : List (A × ℝ))
    (hword : ∀ s∈word,s.2∈Set.Icc (-1 : ℝ) 1) {z : State D} (hz : z∈cone c H) :
    FiniteInstruments.wordAction (fun s : A × ℝ => (polynomialOperator (B s.1) s.2).toLinearMap)
      word z∈cone c H := by
  induction word generalizing z with
  | nil => exact hz
  | cons s word ih =>
    apply ih (fun t ht => hword t (List.mem_cons_of_mem s ht))
    exact cert.preserves hH s.1 s.2 (hword s (List.mem_cons_self)) hz

/-- Finite-word densities are nonnegative, without incorrectly bounding point densities by one. -/
theorem word_mass_nonneg (hH : H.PosDef) (word : List (A × ℝ))
    (hword : ∀ s∈word,s.2∈Set.Icc (-1 : ℝ) 1) {z : State D} (hz : z∈cone c H) :
    0≤mass (FiniteInstruments.wordAction
      (fun s : A × ℝ => (polynomialOperator (B s.1) s.2).toLinearMap) word z) :=
  (probabilityCone c H hH).mass_nonneg (cert.word_cone hH word hword hz)

/-- The complete finite observation measures have total mass one at every horizon. -/
theorem observation_law_probability (hH : H.PosDef) (actions : ℕ → A)
    (z : State D) (hz : z∈cone c H) (hm : mass z=1) (horizon : ℕ) :
    IsProbabilityMeasure (ContinuousRecords.observationLaw (cert.instrument hH) actions z horizon) :=
  ContinuousRecords.observationLaw_probability (cert.instrument hH) actions ⟨z,hz,hm⟩ horizon

/-- Arbitrary common measurable randomized history policies give genuine normalized joint laws. -/
theorem record_law_probability [Fintype A] [MeasurableSpace A] [MeasurableSingletonClass A]
    (hH : H.PosDef) (policy : ContinuousRecords.Policy (A := A) (Y := ℝ))
    (z : State D) (hz : z∈cone c H) (hm : mass z=1) (horizon : ℕ) :
    IsProbabilityMeasure (ContinuousRecords.recordLaw (cert.instrument hH) policy z horizon) :=
  ContinuousRecords.recordLaw_probability (cert.instrument hH) policy ⟨z,hz,hm⟩ horizon

/-- The normalized laws are the literal prefix marginals of every longer finite law. -/
theorem record_law_prefix [Fintype A] [MeasurableSpace A] [MeasurableSingletonClass A]
    (hH : H.PosDef) (policy : ContinuousRecords.Policy (A := A) (Y := ℝ))
    (z : State D) (hz : z∈cone c H) (horizon extra : ℕ) :
    (ContinuousRecords.recordLaw (cert.instrument hH) policy z (horizon+extra)).map
      (ContinuousRecords.truncate horizon extra)=
      ContinuousRecords.recordLaw (cert.instrument hH) policy z horizon :=
  ContinuousRecords.recordLaw_prefix (cert.instrument hH) policy hz horizon extra
end PolynomialCertificate

end Komorebi.LSM.OrientedEllipsoid
