/- Canonical theta coordinate algebra. Analytic identity q(z)=c/Q5(wp(z))
and the fifth-torsion hypotheses are established outside this algebraic core. -/
module
public import H12CoprimeNormalization
public import H12SignedAlgebra
public import Mathlib.Tactic.FieldSimp
@[expose] public section
namespace H12.CanonicalTheta
variable {K : Type*} [Field K]

def coordinate (a b x : K) : K := (x-a)/(a-b)
def canonical (a b x : K) : K := (a-b)^2/((x-a)*(x-b))

theorem coordinate_factorization (a b x : K) (hd : a-b≠0) :
    (x-a)*(x-b)=(a-b)^2*coordinate a b x*(coordinate a b x+1) := by
  dsimp [coordinate]; field_simp; ring1

theorem canonical_coordinate_form (a b x : K)
    (hd : a-b≠0) (ha : x-a≠0) (hb : x-b≠0) :
    canonical a b x=1/(coordinate a b x*(coordinate a b x+1)) := by
  have hsum : coordinate a b x+1=(x-b)/(a-b) := by
    dsimp [coordinate]; field_simp; ring1
  rw [hsum]
  dsimp [canonical,coordinate]
  field_simp

theorem normalized_scalar_replacement (a b x c : K) (hc : c=(a-b)^2) :
    c/((x-a)*(x-b))=canonical a b x := by rw [hc]; rfl

theorem nonzero_difference (a b : K) (h : a≠b) : a-b≠0 := sub_ne_zero.mpr h

theorem canonical_swap (a b x : K) : canonical b a x=canonical a b x := by
  dsimp [canonical]
  have hn : (b-a)^2=(a-b)^2 := by ring1
  rw [hn,mul_comm (x-b) (x-a)]

theorem coordinate_swap (a b x : K) (hd : a-b≠0) :
    coordinate b a x= -1-coordinate a b x := by
  have hd' : b-a≠0 := sub_ne_zero.mpr (Ne.symm (sub_ne_zero.mp hd))
  dsimp [coordinate]; field_simp; ring1

theorem rational_shape_reflection (u : K) :
    (-1-u)*((-1-u)+1)=u*(u+1) := by ring1

theorem scale_invariance (a b x scale : K) (hs : scale≠0) :
    canonical (scale*a) (scale*b) (scale*x)=canonical a b x := by
  dsimp [canonical]
  have h1 : scale*a-scale*b=scale*(a-b) := by ring1
  have h2 : scale*x-scale*a=scale*(x-a) := by ring1
  have h3 : scale*x-scale*b=scale*(x-b) := by ring1
  rw [h1,h2,h3]
  simp only [mul_pow]
  have h4 : (scale*(x-a))*(scale*(x-b))=scale^2*((x-a)*(x-b)) := by ring1
  rw [h4]
  exact mul_div_mul_left _ _ (pow_ne_zero 2 hs)

theorem field_normalizer (c d : K) (hc : c≠0)
    (h3 : c^3=d^6) (h8 : c^8=d^16) : c=d^2 := by
  apply mul_right_cancel₀ (pow_ne_zero 8 hc)
  calc
    c*c^8=(c^3)^3 := by ring1
    _=(d^6)^3 := by rw [h3]
    _=d^2*d^16 := by ring1
    _=d^2*c^8 := by rw [h8]

theorem symmetric_kernel_formula (a b x : K) :
    canonical a b x=((a+b)^2-4*a*b)/(x^2-(a+b)*x+a*b) := by
  have hn : (a-b)^2=(a+b)^2-4*a*b := by ring1
  have hd : (x-a)*(x-b)=x^2-(a+b)*x+a*b := by ring1
  dsimp [canonical]; rw [hn,hd]

end H12.CanonicalTheta
