import KomorebiLSM.UniformIntervalMoments
import KomorebiLSM.ContinuousInstrument
import KomorebiLSM.FiniteInstrument
import Mathlib.Analysis.Matrix.PosDef

/-! P53: polynomial interval Gram matrices and their literal Choi contraction.
The pair `(i,p)` denotes output row `i` and input column `p`. Positivity is
derived from a positive-semidefinite Choi matrix, rather than assumed of its
contraction map. -/
set_option autoImplicit false
namespace Komorebi.LSM.PolynomialGram
open Matrix MeasureTheory
open scoped BigOperators

variable {D N : Type*} [Fintype D] [Fintype N]

/-- The literal output/input-index Choi contraction. -/
noncomputable def choiAction (F : Matrix (D × D) (D × D) ℝ) :
    Matrix D D ℝ →ₗ[ℝ] Matrix D D ℝ where
  toFun X i j := ∑ p, ∑ q, F (i,p) (j,q) * X p q
  map_add' X Y := by
    ext i j
    change (∑ p, ∑ q, F (i,p) (j,q) * (X p q + Y p q)) = _ + _
    simp only [mul_add, Finset.sum_add_distrib]
  map_smul' a X := by
    ext i j
    change (∑ p, ∑ q, F (i,p) (j,q) * (a * X p q)) = a * (∑ p, ∑ q, F (i,p) (j,q) * X p q)
    simp only [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro p _
    apply Finset.sum_congr rfl
    intro q _
    ring

@[simp] theorem choiAction_apply (F : Matrix (D × D) (D × D) ℝ)
    (X : Matrix D D ℝ) (i j : D) :
    choiAction F X i j = ∑ p, ∑ q, F (i,p) (j,q) * X p q := rfl

/-- A weighted vectorized rank-one matrix contracts to its actual congruence. -/
theorem choi_rank_one (K : Matrix D D ℝ) (w : ℝ) (X : Matrix D D ℝ) :
    choiAction (fun s t => w * K s.1 s.2 * K t.1 t.2) X =
      w • (K * X * K.transpose) := by
  ext i j
  change (∑ p, ∑ q, (w * K i p * K j q) * X p q) = _
  rw [Matrix.smul_apply, AveragedCongruence.congruence_entry]
  simp only [smul_eq_mul, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro p _
  apply Finset.sum_congr rfl
  intro q _
  ring

/-- Spectral decomposition supplies nonnegative real congruence factors from
the actual positive-semidefinite matrix. Factors need not be polynomial. -/
theorem choi_factorization [DecidableEq D] {F : Matrix (D × D) (D × D) ℝ} (hF : F.PosSemidef) :
    ∃ (w : D × D → ℝ) (K : D × D → Matrix D D ℝ),
      (∀ k, 0 ≤ w k) ∧
      (∀ s t, F s t = ∑ k, w k * K k s.1 s.2 * K k t.1 t.2) ∧
      (∀ X, choiAction F X = ∑ k, w k • (K k * X * (K k).transpose)) := by
  let U : Matrix (D × D) (D × D) ℝ := hF.isHermitian.eigenvectorUnitary
  let w := hF.isHermitian.eigenvalues
  let K : D × D → Matrix D D ℝ := fun k i p => U (i,p) k
  have hentry (s t : D × D) : F s t = ∑ k, w k * K k s.1 s.2 * K k t.1 t.2 := by
    have hdiag : F = U * diagonal w * U.transpose := by
      simpa only [Unitary.conjStarAlgAut_apply, Matrix.star_eq_conjTranspose,
        Matrix.conjTranspose_eq_transpose_of_trivial, RCLike.ofReal_real_eq_id,
        Function.id_comp] using hF.isHermitian.spectral_theorem
    rw [hdiag, Matrix.mul_apply]
    simp only [Matrix.mul_diagonal, Matrix.transpose_apply]
    apply Finset.sum_congr rfl
    intro k _
    dsimp [K]
    ring
  refine ⟨w,K,hF.eigenvalues_nonneg,hentry,?_⟩
  intro X
  ext i j
  simp only [choiAction_apply, hentry, Finset.sum_mul, Matrix.sum_apply,
    Matrix.smul_apply, smul_eq_mul, AveragedCongruence.congruence_entry,
    Finset.mul_sum]
  calc
    _ = ∑ p, ∑ k, ∑ q, w k * K k i p * K k j q * X p q := by
      apply Finset.sum_congr rfl
      intro p _
      exact Finset.sum_comm
    _ = ∑ k, ∑ p, ∑ q, w k * K k i p * K k j q * X p q := Finset.sum_comm
    _ = _ := by
      apply Finset.sum_congr rfl
      intro k _
      apply Finset.sum_congr rfl
      intro p _
      apply Finset.sum_congr rfl
      intro q _
      ring

/-- Choi positivity entails positivity of the contracted map. -/
theorem choi_positive [DecidableEq D] {F : Matrix (D × D) (D × D) ℝ} (hF : F.PosSemidef)
    {X : Matrix D D ℝ} (hX : X.PosSemidef) : (choiAction F X).PosSemidef := by
  obtain ⟨w,K,hw,_,he⟩ := choi_factorization hF
  rw [he X]
  apply Matrix.posSemidef_sum
  intro k _
  apply Matrix.PosSemidef.smul _ (hw k)
  simpa only [Matrix.conjTranspose_eq_transpose_of_trivial] using
    hX.mul_mul_conjTranspose_same (K k)

variable [DecidableEq N]

/-- `q+1` blocks of powers of `u`, each multiplying the identity. -/

noncomputable def powerStack (q : ℕ) (u : ℝ) :
    Matrix (Fin (q+1) × N) N ℝ := fun ki j => u ^ (ki.1 : ℕ) * if ki.2=j then 1 else 0

/-- A polynomial Gram square is positive at every real argument. -/
theorem gram_square_positive (q : ℕ) (G : Matrix (Fin (q+1) × N) (Fin (q+1) × N) ℝ)
    (hG : G.PosSemidef) (u : ℝ) :
    ((powerStack q u).transpose * G * powerStack q u).PosSemidef := by
  simpa only [Matrix.conjTranspose_eq_transpose_of_trivial] using
    hG.conjTranspose_mul_mul_same (powerStack q u)

/-- At `q=0` the second term is omitted, rather than creating an artificial
degree-minus-one block. -/
noncomputable def intervalGram : (q : ℕ) →
    Matrix (Fin (q+1) × N) (Fin (q+1) × N) ℝ →
    Matrix (Fin q × N) (Fin q × N) ℝ → ℝ → Matrix N N ℝ
  | 0, G₀, _, u => (powerStack 0 u).transpose * G₀ * powerStack 0 u
  | k+1, G₀, G₁, u => (powerStack (k+1) u).transpose * G₀ * powerStack (k+1) u +
      (1-u^2) • ((powerStack k u).transpose * G₁ * powerStack k u)

theorem interval_gram_positive (q : ℕ)
    (G₀ : Matrix (Fin (q+1) × N) (Fin (q+1) × N) ℝ)
    (G₁ : Matrix (Fin q × N) (Fin q × N) ℝ)
    (hG₀ : G₀.PosSemidef) (hG₁ : G₁.PosSemidef)
    (u : ℝ) (hu : u ∈ Set.Icc (-1 : ℝ) 1) : (intervalGram q G₀ G₁ u).PosSemidef := by
  cases q with
  | zero => simpa only [intervalGram] using gram_square_positive 0 G₀ hG₀ u
  | succ q =>
    apply Matrix.PosSemidef.add (gram_square_positive (q+1) G₀ hG₀ u)
    apply Matrix.PosSemidef.smul (gram_square_positive q G₁ hG₁ u)
    nlinarith [hu.1,hu.2]

theorem interval_gram_zero (G₀ : Matrix (Fin 1 × N) (Fin 1 × N) ℝ)
    (G₁ : Matrix (Fin 0 × N) (Fin 0 × N) ℝ) (u : ℝ) :
    intervalGram 0 G₀ G₁ u = fun i j => G₀ (0,i) (0,j) := by
  ext i j
  simp [intervalGram,powerStack,Matrix.mul_apply,Fintype.sum_prod_type]

section PolynomialIdentities
open Polynomial
variable {M L : Type*}

/-- Entrywise evaluation of a finite matrix polynomial. -/
noncomputable def evalMatrix (P : Matrix M N ℝ[X]) (u : ℝ) : Matrix M N ℝ :=
  fun i j => (P i j).eval u

omit [Fintype N] [DecidableEq N] in
theorem evalMatrix_add (P Q : Matrix M N ℝ[X]) (u : ℝ) :
    evalMatrix (P+Q) u = evalMatrix P u + evalMatrix Q u := by
  ext i j
  exact Polynomial.eval_add

omit [DecidableEq N] in
theorem evalMatrix_mul (P : Matrix M N ℝ[X]) (Q : Matrix N L ℝ[X]) (u : ℝ) :
    evalMatrix (P*Q) u = evalMatrix P u * evalMatrix Q u := by
  ext i j
  simp [evalMatrix,Matrix.mul_apply,Polynomial.eval_finsetSum]

omit [Fintype N] [DecidableEq N] in
/-- Formal identity of bounded-degree matrix polynomials is exactly a finite
list of coefficient equalities. It is equivalent to equality at every real point. -/
theorem polynomial_identity_finite (P Q : Matrix M N ℝ[X]) (bound : ℕ)
    (hP : ∀ i j,(P i j).natDegree ≤ bound) (hQ : ∀ i j,(Q i j).natDegree ≤ bound) :
    (∀ u, evalMatrix P u = evalMatrix Q u) ↔
      (∀ i j (k : Fin (bound+1)),(P i j).coeff k = (Q i j).coeff k) := by
  constructor
  · intro he i j k
    have hpq : P i j=Q i j := Polynomial.funext (fun u => congrFun (congrFun (he u) i) j)
    rw [hpq]
  · intro hc u
    have hpq : P=Q := by
      ext i j k
      by_cases hk : k < bound+1
      · exact hc i j ⟨k,hk⟩
      · rw [Polynomial.coeff_eq_zero_of_natDegree_lt (lt_of_le_of_lt (hP i j) (by omega)),
          Polynomial.coeff_eq_zero_of_natDegree_lt (lt_of_le_of_lt (hQ i j) (by omega))]
    rw [hpq]

omit [Fintype N] [DecidableEq N] in
/-- Equality on the entire interval already forces equality of the finite
coefficient data; no sample grid is substituted for the interval. -/
theorem polynomial_interval_identity_finite (P Q : Matrix M N ℝ[X]) (bound : ℕ)
    (hP : ∀ i j,(P i j).natDegree≤bound) (hQ : ∀ i j,(Q i j).natDegree≤bound) :
    (∀ u∈Set.Icc (-1 : ℝ) 1,evalMatrix P u=evalMatrix Q u) ↔
      (∀ i j (k : Fin (bound+1)),(P i j).coeff k=(Q i j).coeff k) := by
  constructor
  · intro h
    apply (polynomial_identity_finite P Q bound hP hQ).mp
    intro u
    have hpq : P=Q := by
      funext i j
      apply Polynomial.eq_of_infinite_eval_eq
      apply (Set.Icc_infinite (by norm_num : (-1 : ℝ)<1)).mono
      intro v hv
      exact congrFun (congrFun (h v hv) i) j
    rw [hpq]
  · intro h u _
    exact (polynomial_identity_finite P Q bound hP hQ).mpr h u

/-- Polynomial version of the stacked monomials. -/
noncomputable def powerStackPolynomial (q : ℕ) :
    Matrix (Fin (q+1) × N) N ℝ[X] := fun ki j =>
      Polynomial.X ^ (ki.1 : ℕ) * if ki.2=j then 1 else 0

noncomputable def constantMatrix (G : Matrix M N ℝ) : Matrix M N ℝ[X] :=
  fun i j => Polynomial.C (G i j)

/-- This is an actual matrix polynomial, including its explicit zero-degree case. -/
noncomputable def intervalGramPolynomial : (q : ℕ) →
    Matrix (Fin (q+1) × N) (Fin (q+1) × N) ℝ →
    Matrix (Fin q × N) (Fin q × N) ℝ → Matrix N N ℝ[X]
  | 0,G₀,_ => (powerStackPolynomial 0).transpose * constantMatrix G₀ * powerStackPolynomial 0
  | k+1,G₀,G₁ => (powerStackPolynomial (k+1)).transpose * constantMatrix G₀ * powerStackPolynomial (k+1) +
      ((1 : ℝ[X])-Polynomial.X^2) • ((powerStackPolynomial k).transpose * constantMatrix G₁ * powerStackPolynomial k)

omit [Fintype N] [DecidableEq N] in
theorem evalMatrix_transpose (P : Matrix M N ℝ[X]) (u : ℝ) :
    evalMatrix P.transpose u = (evalMatrix P u).transpose := rfl

omit [Fintype N] [DecidableEq N] in
theorem evalMatrix_scalar (p : ℝ[X]) (P : Matrix M N ℝ[X]) (u : ℝ) :
    evalMatrix (p • P) u = p.eval u • evalMatrix P u := by
  ext i j
  exact Polynomial.eval_mul

omit [Fintype N] [DecidableEq N] in
theorem evalMatrix_constant (G : Matrix M N ℝ) (u : ℝ) :
    evalMatrix (constantMatrix G) u=G := by
  ext i j
  exact Polynomial.eval_C

omit [Fintype N] in
theorem powerStackPolynomial_eval (q : ℕ) (u : ℝ) :
    evalMatrix (powerStackPolynomial (N := N) q) u=powerStack q u := by
  ext ki j
  by_cases h : ki.2=j <;> simp [evalMatrix,powerStackPolynomial,powerStack,h]

theorem intervalGramPolynomial_eval (q : ℕ)
    (G₀ : Matrix (Fin (q+1) × N) (Fin (q+1) × N) ℝ)
    (G₁ : Matrix (Fin q × N) (Fin q × N) ℝ) (u : ℝ) :
    evalMatrix (intervalGramPolynomial q G₀ G₁) u = intervalGram q G₀ G₁ u := by
  cases q <;>
    simp only [intervalGramPolynomial,intervalGram,evalMatrix_add,evalMatrix_scalar,
      evalMatrix_mul,evalMatrix_transpose,evalMatrix_constant,powerStackPolynomial_eval,
      Polynomial.eval_sub,Polynomial.eval_one,Polynomial.eval_pow,Polynomial.eval_X]

/-- Polynomial Choi contraction uses the same explicit output/input pairs. -/
noncomputable def choiPolynomial (F : Matrix (D × D) (D × D) ℝ[X])
    (X : Matrix D D ℝ) : Matrix D D ℝ[X] :=
  fun i j => ∑ p, ∑ q, F (i,p) (j,q) * Polynomial.C (X p q)

theorem choiPolynomial_eval (F : Matrix (D × D) (D × D) ℝ[X])
    (X : Matrix D D ℝ) (u : ℝ) :
    evalMatrix (choiPolynomial F X) u=choiAction (evalMatrix F u) X := by
  ext i j
  change (∑ p, ∑ q, F (i,p) (j,q) * Polynomial.C (X p q)).eval u =
    ∑ p, ∑ q, (F (i,p) (j,q)).eval u * X p q
  simp [Polynomial.eval_finsetSum]

end PolynomialIdentities

section PolynomialOperators
variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]

/-- A declared finite power expansion in continuous linear operators. -/
noncomputable def operatorPolynomial {n : ℕ} (B : Fin n → E →L[ℝ] E) (u : ℝ) : E →L[ℝ] E :=
  ∑ k : Fin n, u ^ (k : ℕ) • B k

/-- The Bochner integral is defined for the whole operator, not just its entries. -/
theorem continuous_uniform_integrable {F : Type*} [NormedAddCommGroup F] [NormedSpace ℝ F]
    {f : ℝ → F} (hf : Continuous f) : Integrable f UniformIntervalMoments.measure := by
  unfold UniformIntervalMoments.measure AveragedCongruence.uniformInterval ProbabilityTheory.cond
  exact (hf.intervalIntegrable (-1) 1).1.smul_measure (by simp)

theorem operatorPolynomial_continuous {n : ℕ} (B : Fin n → E →L[ℝ] E) :
    Continuous (operatorPolynomial B) := by
  unfold operatorPolynomial
  fun_prop

theorem operatorPolynomial_integrable {n : ℕ} (B : Fin n → E →L[ℝ] E) :
    Integrable (operatorPolynomial B) UniformIntervalMoments.measure :=
  continuous_uniform_integrable (operatorPolynomial_continuous B)

/-- Exact normalization of a polynomial uses only finitely many actual moments. -/
theorem operatorPolynomial_integral [CompleteSpace E] {n : ℕ} (B : Fin n → E →L[ℝ] E) :
    (∫ u,operatorPolynomial B u∂UniformIntervalMoments.measure) =
      ∑ k : Fin n, UniformIntervalMoments.moment k • B k := by
  unfold operatorPolynomial
  rw [integral_finsetSum _ (fun k _ => continuous_uniform_integrable (by fun_prop))]
  apply Finset.sum_congr rfl
  intro k _
  exact integral_smul_const _ _

/-- Embed the actual finite operator coefficients, on a specified input. -/
noncomputable def embeddedPolynomial {n : ℕ} (J : E →ₗ[ℝ] Matrix D D ℝ)
    (B : Fin n → E →L[ℝ] E) (z : E) : Matrix D D (Polynomial ℝ) :=
  fun i j => Polynomial.ofFn n (fun k => J (B k z) i j)

omit [Fintype D] in
theorem embeddedPolynomial_eval {n : ℕ} (J : E →ₗ[ℝ] Matrix D D ℝ)
    (B : Fin n → E →L[ℝ] E) (z : E) (u : ℝ) :
    evalMatrix (embeddedPolynomial J B z) u=J (operatorPolynomial B u z) := by
  ext i j
  simp [evalMatrix,embeddedPolynomial,UniformIntervalMoments.eval_ofFn,
    operatorPolynomial,map_sum,Matrix.sum_apply,Matrix.smul_apply,mul_comm]

/-- Once degrees are bounded, the entire intertwining identity is equivalent
to a finite coefficient test on a basis of the actual state space. -/
theorem polynomial_intertwining_finite {R : Type*} (b : Module.Basis R ℝ E) {n : ℕ}
    (J : E →ₗ[ℝ] Matrix D D ℝ) (B : Fin n → E →L[ℝ] E)
    (F : Matrix (D × D) (D × D) (Polynomial ℝ)) (bound : ℕ)
    (hL : ∀ r i j,(embeddedPolynomial J B (b r) i j).natDegree≤bound)
    (hR : ∀ r i j,(choiPolynomial F (J (b r)) i j).natDegree≤bound) :
    (∀ u z,J (operatorPolynomial B u z)=choiAction (evalMatrix F u) (J z)) ↔
      (∀ r i j (k : Fin (bound+1)),
        (embeddedPolynomial J B (b r) i j).coeff k =
          (choiPolynomial F (J (b r)) i j).coeff k) := by
  constructor
  · intro h r
    apply (polynomial_identity_finite _ _ bound (hL r) (hR r)).mp
    intro u
    rw [embeddedPolynomial_eval,choiPolynomial_eval]
    exact h u (b r)
  · intro h u z
    have he : J.comp (operatorPolynomial B u).toLinearMap =
        (choiAction (evalMatrix F u)).comp J := by
      apply b.ext
      intro r
      have hv := (polynomial_identity_finite _ _ bound (hL r) (hR r)).mpr (h r) u
      rw [embeddedPolynomial_eval,choiPolynomial_eval] at hv
      exact hv
    exact congrArg (fun L : E →ₗ[ℝ] Matrix D D ℝ => L z) he

/-- The Gram identity makes the actual state operator positive on the embedded
matrix cone at every observation point of the interval. -/
theorem gram_operator_positive [DecidableEq D] (J : E →ₗ[ℝ] Matrix D D ℝ)
    {n q : ℕ} (B : Fin n → E →L[ℝ] E)
    (G₀ : Matrix (Fin (q+1) × (D × D)) (Fin (q+1) × (D × D)) ℝ)
    (G₁ : Matrix (Fin q × (D × D)) (Fin q × (D × D)) ℝ)
    (hG₀ : G₀.PosSemidef) (hG₁ : G₁.PosSemidef)
    (he : ∀ u z,J (operatorPolynomial B u z)=choiAction (intervalGram q G₀ G₁ u) (J z))
    (u : ℝ) (hu : u∈Set.Icc (-1 : ℝ) 1) (z : E) (hz : (J z).PosSemidef) :
    (J (operatorPolynomial B u z)).PosSemidef := by
  rw [he]
  exact choi_positive (interval_gram_positive q G₀ G₁ hG₀ hG₁ u hu) hz

/-- The actual reference measure is supported on the declared interval. -/
theorem uniform_ae_interval :
    ∀ᵐ u∂UniformIntervalMoments.measure,u∈Set.Icc (-1 : ℝ) 1 := by
  unfold UniformIntervalMoments.measure AveragedCongruence.uniformInterval ProbabilityTheory.cond
  apply Measure.ae_smul_measure
  filter_upwards [ae_restrict_mem (μ := volume) measurableSet_Ioc] with u hu
  exact ⟨hu.1.le,hu.2⟩

/-- The exact integrated mass law is a finite collection of checks on a basis. -/
theorem moment_mass_finite {R : Type*} (b : Module.Basis R ℝ E) {n : ℕ}
    (l : E →ₗ[ℝ] ℝ) (B : Fin n → E →L[ℝ] E) :
    (∀ z,l ((∑ k : Fin n,UniformIntervalMoments.moment k • B k) z)=l z) ↔
      (∀ r,l ((∑ k : Fin n,UniformIntervalMoments.moment k • B k) (b r))=l (b r)) := by
  constructor
  · intro h r
    exact h (b r)
  · intro h z
    have he : l.comp (∑ k : Fin n,UniformIntervalMoments.moment k • B k).toLinearMap=l := by
      apply b.ext
      exact h
    exact congrArg (fun L : E →ₗ[ℝ] ℝ => L z) he

variable [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]

/-- Polynomial Gram data construct the literal P52 density instrument. The
input is finite Gram positivity, polynomial identities and exact finite-moment
normalization, rather than an assumed positive stochastic kernel. -/
noncomputable def polynomialDensityInstrument [DecidableEq D]
    {A R : Type*} [Fintype R] (b : Module.Basis R ℝ E)
    (C : BaseNorm.ProbabilityCone E) (J : E →ₗ[ℝ] Matrix D D ℝ)
    (hC : ∀ z,z∈C.carrier ↔ (J z).PosSemidef) {n q : ℕ}
    (B : A → Fin n → E →L[ℝ] E)
    (G₀ : A → Matrix (Fin (q+1) × (D × D)) (Fin (q+1) × (D × D)) ℝ)
    (G₁ : A → Matrix (Fin q × (D × D)) (Fin q × (D × D)) ℝ)
    (hG₀ : ∀ a,(G₀ a).PosSemidef) (hG₁ : ∀ a,(G₁ a).PosSemidef)
    (he : ∀ a u z,J (operatorPolynomial (B a) u z)=
      choiAction (intervalGram q (G₀ a) (G₁ a) u) (J z))
    (hm : ∀ a r,C.mass ((∑ k : Fin n,UniformIntervalMoments.moment k • B a k) (b r))=C.mass (b r)) :
    ContinuousInstrument.DensityInstrument (A := A) C UniformIntervalMoments.measure where
  op a := operatorPolynomial (B a)
  measurable_op a := (operatorPolynomial_continuous (B a)).measurable
  integrable_op a := operatorPolynomial_integrable (B a)
  positive a := by
    filter_upwards [uniform_ae_interval] with u hu
    intro z hz
    exact (hC _).mpr (gram_operator_positive J (B a) (G₀ a) (G₁ a) (hG₀ a) (hG₁ a)
      (he a) u hu z ((hC z).mp hz))
  mass_preserving a z := by
    rw [operatorPolynomial_integral]
    exact (moment_mass_finite b C.mass (B a)).mpr (hm a) z

/-- A finite replayable P53 certificate. All intertwining checks are literal
coefficients on a finite state basis, and normalization uses actual uniform
moments. No operator-positivity or probability-law conclusion is a field. -/
structure CoefficientCertificate [DecidableEq D] {A R : Type*} [Fintype A] [Fintype R]
    (b : Module.Basis R ℝ E) (C : BaseNorm.ProbabilityCone E)
    (J : E →ₗ[ℝ] Matrix D D ℝ) {n : ℕ} (B : A → Fin n → E →L[ℝ] E)
    (q bound : ℕ) where
  gram0 : A → Matrix (Fin (q+1) × (D × D)) (Fin (q+1) × (D × D)) ℝ
  gram1 : A → Matrix (Fin q × (D × D)) (Fin q × (D × D)) ℝ
  gram0_positive : ∀ a,(gram0 a).PosSemidef
  gram1_positive : ∀ a,(gram1 a).PosSemidef
  left_degree : ∀ a r i j,(embeddedPolynomial J (B a) (b r) i j).natDegree≤bound
  right_degree : ∀ a r i j,
    (choiPolynomial (intervalGramPolynomial q (gram0 a) (gram1 a)) (J (b r)) i j).natDegree≤bound
  coefficients : ∀ a r i j (k : Fin (bound+1)),
    (embeddedPolynomial J (B a) (b r) i j).coeff k =
      (choiPolynomial (intervalGramPolynomial q (gram0 a) (gram1 a)) (J (b r)) i j).coeff k
  mass : ∀ a r,C.mass ((∑ k : Fin n,UniformIntervalMoments.moment k • B a k) (b r))=C.mass (b r)

namespace CoefficientCertificate
variable [DecidableEq D] {A R : Type*} [Fintype A] [Fintype R]
variable {b : Module.Basis R ℝ E} {C : BaseNorm.ProbabilityCone E}
variable {J : E →ₗ[ℝ] Matrix D D ℝ} {n q bound : ℕ} {B : A → Fin n → E →L[ℝ] E}
variable (W : CoefficientCertificate b C J B q bound)

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
/-- The finite coefficient data imply the full identity on every input and
every real observation, hence on the entire interval. -/
theorem intertwines (a : A) (u : ℝ) (z : E) :
    J (operatorPolynomial (B a) u z)=choiAction (intervalGram q (W.gram0 a) (W.gram1 a) u) (J z) := by
  have he := (polynomial_intertwining_finite b J (B a)
    (intervalGramPolynomial q (W.gram0 a) (W.gram1 a)) bound
    (W.left_degree a) (W.right_degree a)).mpr (W.coefficients a) u z
  rwa [intervalGramPolynomial_eval] at he

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
include W in
/-- Whole-interval positivity is derived from the finite witness. -/
theorem positive (a : A) (u : ℝ) (hu : u∈Set.Icc (-1 : ℝ) 1)
    (z : E) (hz : (J z).PosSemidef) : (J (operatorPolynomial (B a) u z)).PosSemidef :=
  gram_operator_positive J (B a) (W.gram0 a) (W.gram1 a)
    (W.gram0_positive a) (W.gram1_positive a) (W.intertwines a) u hu z hz

/-- The checked finite data build P52's continuous probability instrument. -/
noncomputable def instrument
    (hC : ∀ z,z∈C.carrier ↔ (J z).PosSemidef) :
    ContinuousInstrument.DensityInstrument (A := A) C UniformIntervalMoments.measure :=
  polynomialDensityInstrument b C J hC B W.gram0 W.gram1
    W.gram0_positive W.gram1_positive W.intertwines W.mass

omit [MeasurableSpace E] [BorelSpace E] in
@[simp] theorem instrument_op (hC : ∀ z,z∈C.carrier ↔ (J z).PosSemidef) (a : A) (u : ℝ) :
    (W.instrument hC).op a u=operatorPolynomial (B a) u := rfl

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
include W in
/-- Every finite chronological product stays in the actual embedded PSD cone
at every interval-valued record, not merely almost everywhere or on a grid. -/
theorem word_positive (word : List (A × ℝ))
    (hword : ∀ s∈word,s.2∈Set.Icc (-1 : ℝ) 1) (z : E) (hz : (J z).PosSemidef) :
    (J (FiniteInstruments.wordAction
      (fun s : A × ℝ => (operatorPolynomial (B s.1) s.2).toLinearMap) word z)).PosSemidef := by
  induction word generalizing z with
  | nil => simpa only [FiniteInstruments.wordAction_nil,LinearMap.id_apply] using hz
  | cons s word ih =>
    rw [FiniteInstruments.wordAction_cons,LinearMap.comp_apply]
    apply ih
    · intro t ht
      exact hword t (List.mem_cons_of_mem s ht)
    · exact W.positive s.1 s.2 (hword s (List.mem_cons_self)) z hz

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
include W in
/-- The product mass is a nonnegative density at each interval-valued record;
density values are not incorrectly bounded by one. -/
theorem word_mass_nonnegative (hC : ∀ z,z∈C.carrier ↔ (J z).PosSemidef)
    (word : List (A × ℝ)) (hword : ∀ s∈word,s.2∈Set.Icc (-1 : ℝ) 1)
    (z : E) (hz : z∈C.carrier) :
    0≤C.mass (FiniteInstruments.wordAction
      (fun s : A × ℝ => (operatorPolynomial (B s.1) s.2).toLinearMap) word z) :=
  C.mass_nonneg ((hC _).mpr (W.word_positive word hword z ((hC z).mp hz)))

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
include W in
/-- The exact normalized update belongs to the same certified base at every
interval point with positive density. -/
theorem normalized_update (hC : ∀ z,z∈C.carrier ↔ (J z).PosSemidef)
    (a : A) (u : ℝ) (hu : u∈Set.Icc (-1 : ℝ) 1)
    (z : E) (hz : z∈C.base) (hp : 0<C.mass (operatorPolynomial (B a) u z)) :
    (C.mass (operatorPolynomial (B a) u z))⁻¹ • operatorPolynomial (B a) u z∈C.base := by
  refine ⟨C.smul_mem (inv_nonneg.mpr hp.le)
    ((hC _).mpr (W.positive a u hu z ((hC z).mp hz.1))),?_⟩
  rw [map_smul,smul_eq_mul]
  exact inv_mul_cancel₀ hp.ne'

end CoefficientCertificate

end PolynomialOperators

end Komorebi.LSM.PolynomialGram
