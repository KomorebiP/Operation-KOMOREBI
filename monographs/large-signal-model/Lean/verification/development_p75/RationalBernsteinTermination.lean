import KomorebiLSM.RationalBernsteinMargin
import KomorebiLSM.DyadicBernsteinCertificate
import KomorebiLSM.BernsteinCellPositivity

/-! Strict actual margin guarantees eventual success of complete rational dyadic certificates. -/
set_option autoImplicit false
namespace Komorebi.LSM.RationalBernsteinTermination
open TensorBernsteinCertificate RationalBernsteinMargin RationalSemicircle
open LorentzCylinder RobustOrientedMargin
noncomputable section

/-- The coefficient convergence is derived in BernsteinCellPositivity from exact rational coordinates. -/
theorem positive_polynomial_eventual (p : Polynomial₂)
    (hp : ∀ x∈square.domain,0<value p x) :
    ∃ N : ℕ,∀ M : ℕ,N≤M → Nonempty (UniformCertificate p square M) := by
  obtain ⟨delta,hdelta,hcell⟩ := BernsteinCellPositivity.exists_small_positive p hp
  exact eventually_uniform_dyadic delta hdelta hcell

/-- Finitely many polynomials share one sufficiently fine depth, and every finer depth succeeds. -/
theorem finite_family_eventual {I : Type*} [Fintype I] (p : I → Polynomial₂)
    (hp : ∀ i x,x∈square.domain → 0<value (p i) x) :
    ∃ N : ℕ,∀ M : ℕ,N≤M → ∀ i,Nonempty (UniformCertificate (p i) square M) := by
  classical
  have he (i : I) := positive_polynomial_eventual (p i) (hp i)
  choose depth hdepth using he
  refine ⟨Finset.univ.sup depth,?_⟩
  intro M hM i
  exact hdepth i M ((Finset.le_sup (Finset.mem_univ i)).trans hM)

variable {n : ℕ}

theorem strict_polynomials_positive (G : Fin n → RationalMatrix) (kappa : ℚ)
    (hmargin : ∀ u∈Set.Icc (-1 : ℝ) 1,
      (kappa : ℝ)<sigma (PolynomialGram.operatorPolynomial (fun k => matrixOperator (G k)) u))
    (left : Bool) :
    (∀ x∈square.domain,0<value (orientationPolynomial G kappa left) x) ∧
      (∀ x∈square.domain,0<value (squareGapPolynomial G kappa left) x) := by
  have h (x : Fin 2 → ℝ) (hx : x∈square.domain) :=
    strict_chart_tests (PolynomialGram.operatorPolynomial (fun k => matrixOperator (G k)) (x 0))
      kappa (hmargin (x 0) ((square_domain x).mp hx 0)) left (x 1)
  have he (x : Fin 2 → ℝ) : x=![x 0,x 1] := by
    funext i
    fin_cases i <;> rfl
  constructor
  · intro x hx
    rw [he x,value_orientationPolynomial]
    exact (h x hx).1
  · intro x hx
    rw [he x,value_squareGapPolynomial]
    exact (h x hx).2

/-- The selector is only a finite indexing of the two required tests; neither test is dropped. -/
def testPolynomial (G : Fin n → RationalMatrix) (kappa : ℚ) (which left : Bool) : Polynomial₂ :=
  if which then squareGapPolynomial G kappa left else orientationPolynomial G kappa left

/-- The same finite dyadic grid eventually certifies all actions and both tests in both charts. -/
theorem strict_family_eventual {A : Type*} [Fintype A]
    (G : A → Fin n → RationalMatrix) (kappa : ℚ)
    (hmargin : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 →
      (kappa : ℝ)<sigma (PolynomialGram.operatorPolynomial (fun k => matrixOperator (G a k)) u)) :
    ∃ N : ℕ,∀ M : ℕ,N≤M → ∀ a which left,
      Nonempty (UniformCertificate (testPolynomial (G a) kappa which left) square M) := by
  have hp (q : A × Bool × Bool) (x : Fin 2 → ℝ) (hx : x∈square.domain) :
      0<value (testPolynomial (G q.1) kappa q.2.1 q.2.2) x := by
    have h := strict_polynomials_positive (G q.1) kappa (hmargin q.1) q.2.2
    cases hwhich : q.2.1
    · simpa [testPolynomial,hwhich] using h.1 x hx
    · simpa [testPolynomial,hwhich] using h.2 x hx
  obtain ⟨N,hN⟩ := finite_family_eventual
    (fun q : A × Bool × Bool => testPolynomial (G q.1) kappa q.2.1 q.2.2) hp
  exact ⟨N,fun M hM a which left => hN M hM (a,which,left)⟩

/-- A strict actual curved margin supplies finite exact rational witnesses, with complete tree coverage. -/
theorem strict_family_certificate_exists {A : Type*} [Fintype A]
    (G : A → Fin n → RationalMatrix) (kappa : ℚ)
    (hmargin : ∀ a u,u∈Set.Icc (-1 : ℝ) 1 →
      (kappa : ℝ)<sigma (PolynomialGram.operatorPolynomial (fun k => matrixOperator (G a k)) u)) :
    Nonempty (∀ a,Certificate (G a) kappa) := by
  obtain ⟨N,hN⟩ := strict_family_eventual G kappa hmargin
  refine ⟨fun a => { orientationWitness := fun left => ?_,squareGapWitness := fun left => ?_ }⟩
  · exact (hN N le_rfl a false left).some.toSubdivision
  · exact (hN N le_rfl a true left).some.toSubdivision

end
end Komorebi.LSM.RationalBernsteinTermination
