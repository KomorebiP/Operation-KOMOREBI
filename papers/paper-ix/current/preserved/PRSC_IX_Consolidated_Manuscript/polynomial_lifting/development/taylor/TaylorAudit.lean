module
public import PolynomialTaylor
@[expose] public section

#print axioms Komorebi.PolynomialTaylor.directional
#print axioms Komorebi.PolynomialTaylor.directional_C
#print axioms Komorebi.PolynomialTaylor.directional_add
#print axioms Komorebi.PolynomialTaylor.directional_mul
#print axioms Komorebi.PolynomialTaylor.directional_X
#print axioms Komorebi.PolynomialTaylor.taylor_dvd
#print axioms Komorebi.PolynomialTaylor.taylor_step_dvd
#print axioms Komorebi.PolynomialTaylor.eval_dvd_of_dvd
#print axioms Komorebi.PolynomialTaylor.pderiv_eval_dvd_of_dvd

open MvPolynomial Komorebi.PolynomialTaylor in
example (d : ℕ) (P : MvPolynomial (Fin d) ℤ) (x t : Fin d → ℤ)
    (q L : ℕ) (hL : 1 ≤ L) :
    (q : ℤ) ^ (L + 1) ∣
      eval (fun i => x i + (q : ℤ) ^ L * t i) P - eval x P -
        (q : ℤ) ^ L * (∑ i, eval x (pderiv i P) * t i) :=
  taylor_step_dvd P x t q L hL
