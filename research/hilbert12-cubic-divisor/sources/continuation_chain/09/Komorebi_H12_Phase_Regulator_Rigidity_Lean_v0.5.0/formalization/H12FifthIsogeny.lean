/- Explicit polynomial core of the order-five quotient map. All geometric
identifications and analytic differentiation are separate ordinary proofs. -/
module
public import Mathlib.Tactic.Ring
public import Mathlib.Tactic.FieldSimp
@[expose] public section
namespace H12.FifthIsogeny
variable {K : Type*} [Field K]

def b2 (u : K) := u^2-6*u+1
def b4 (u : K) := u^2-u
def a4 (u : K) := -5*u*(u^2+2*u-1)
def a6 (u : K) := -u*(u^4+10*u^3-5*u^2+15*u-1)
def source (u x : K) := 4*x^3+b2 u*x^2+2*b4 u*x+u^2
def target (u x : K) := 4*x^3+b2 u*x^2+(2*b4 u+4*a4 u)*x+u^2+4*a6 u

def den (u x : K) := x^2*(x-u)^2
def num (u x : K) := x^5-2*u*x^4+(u^3+3*u^2-u)*x^3+
    (-3*u^3+3*u^2)*x^2+(u^4-3*u^3)*x+u^4
def denD (u x : K) := 2*x*(x-u)^2+2*x^2*(x-u)
def numD (u x : K) := 5*x^4-8*u*x^3+3*(u^3+3*u^2-u)*x^2+
    2*(-3*u^3+3*u^2)*x+(u^4-3*u^3)
def jacNum (u x : K) := numD u x*den u x-num u x*denD u x

def mapX (u x : K) := num u x / den u x
def mapZ (u x z : K) := jacNum u x*z/(den u x)^2

theorem numerator_at_zero (u : K) : num u 0=u^4 := by simp [num]
theorem numerator_at_kernel (u : K) : num u u=u^6 := by dsimp [num]; ring1

theorem denominator_nonzero (u x : K) (hx : x≠0) (hxu : x-u≠0) : den u x≠0 := by
  exact mul_ne_zero (pow_ne_zero 2 hx) (pow_ne_zero 2 hxu)

theorem rational_quotient_formula (u x : K) (hx : x≠0) (hxu : x-u≠0) :
    mapX u x=x+u*(u-1)/x+u^2/x^2+u^2*(u+1)/(x-u)+u^4/(x-u)^2 := by
  dsimp [mapX,num,den]
  field_simp
  ring1

theorem cleared_curve_identity (u x : K) :
    (jacNum u x)^2*source u x =
      4*(num u x)^3*den u x + b2 u*(num u x)^2*(den u x)^2 +
      (2*b4 u+4*a4 u)*num u x*(den u x)^3 +
      (u^2+4*a6 u)*(den u x)^4 := by
  dsimp [jacNum,numD,denD,num,den,source,b2,b4,a4,a6]
  ring1

theorem maps_curve (u x z : K) (hd : den u x≠0) (hz : z^2=source u x) :
    (mapZ u x z)^2=target u (mapX u x) := by
  dsimp [mapZ,mapX,target]
  field_simp
  rw [hz]
  calc
    _ = 4*(num u x)^3*den u x + b2 u*(num u x)^2*(den u x)^2 +
        (2*b4 u+4*a4 u)*num u x*(den u x)^3 +
        (u^2+4*a6 u)*(den u x)^4 := cleared_curve_identity u x
    _ = _ := by ring1

def negateZ (z : K) := -z

theorem quotient_commutes_with_negation (u x z : K) :
    mapZ u x (negateZ z)=negateZ (mapZ u x z) := by
  dsimp [mapZ,negateZ]; ring1

/-- The polynomial numerator of the logarithmic-second-derivative expression.
This lemma is algebraic; it does not assert a formal analytic derivative. -/
theorem differential_quotient_identity (u x : K) :
    num u x=(5*x-2*u)*den u x +
      (x^2+(x-u)^2)*source u x -
      (2*x-u)*x*(x-u)*(6*x^2+b2 u*x+b4 u) := by
  dsimp [num,den,source,b2,b4]; ring1

end H12.FifthIsogeny
