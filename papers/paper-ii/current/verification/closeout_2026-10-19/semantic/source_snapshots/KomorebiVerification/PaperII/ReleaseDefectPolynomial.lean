import KomorebiVerification.PaperII.TypedLinearDefects

set_option autoImplicit false
namespace Komorebi.PaperII.ReleaseDefectPolynomial
open scoped BigOperators
open TypedLinearDefects
universe u v w

/-- The full polynomial defect, with every coefficient retained. The zero-degree
summand vanishes by the all-natural-powers telescope. -/
theorem polynomial_defect
    {R : Type u} [CommSemiring R]
    {Xf : Type v} {Xc : Type w}
    [AddCommGroup Xf] [AddCommGroup Xc] [Module R Xf] [Module R Xc]
    (C : Xf →ₗ[R] Xc) (Tf : Module.End R Xf) (Tc : Module.End R Xc)
    (p : Polynomial R) :
    C.comp (polynomialAction p Tf) - (polynomialAction p Tc).comp C =
      p.sum (fun n a => a • (∑ k ∈ Finset.range n,
        (Tc ^ (n - 1 - k)).comp ((defect C Tf Tc).comp (Tf ^ k)))) := by
  classical
  calc
    _ = p.sum (fun n a => a • (C.comp (Tf ^ n) - (Tc ^ n).comp C)) := by
      ext x
      simp [polynomialAction, Polynomial.sum_def, Finset.sum_sub_distrib, smul_sub]
    _ = _ := by
      simp only [Polynomial.sum_def]
      apply Finset.sum_congr rfl
      intro n hn
      rw [power_defect_identity_all]

/-- The same full identity in the space of bounded linear maps, without a
zero-defect assumption or any completeness assumption. -/
theorem continuous_polynomial_defect
    {𝕜 : Type u} [NontriviallyNormedField 𝕜]
    {Ef : Type v} {Ec : Type w}
    [NormedAddCommGroup Ef] [NormedAddCommGroup Ec]
    [NormedSpace 𝕜 Ef] [NormedSpace 𝕜 Ec]
    (C : Ef →L[𝕜] Ec) (Tf : Ef →L[𝕜] Ef) (Tc : Ec →L[𝕜] Ec)
    (p : Polynomial 𝕜) :
    C.comp (continuousPolynomialAction p Tf) -
        (continuousPolynomialAction p Tc).comp C =
      p.sum (fun n a => a • (∑ k ∈ Finset.range n,
        (Tc ^ (n - 1 - k)).comp ((continuousDefect C Tf Tc).comp (Tf ^ k)))) := by
  classical
  calc
    _ = p.sum (fun n a => a • (C.comp (Tf ^ n) - (Tc ^ n).comp C)) := by
      ext x
      simp [continuousPolynomialAction, Polynomial.sum_def,
        Finset.sum_sub_distrib, smul_sub]
    _ = _ := by
      simp only [Polynomial.sum_def]
      apply Finset.sum_congr rfl
      intro n hn
      rw [continuous_power_defect_identity_all]

end Komorebi.PaperII.ReleaseDefectPolynomial
