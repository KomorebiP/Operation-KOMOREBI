import Std

namespace H12PrincipalModel
abbrev P := Int × Int × Int × Int × Int × Int

def alpha (v : P) := v.1-2*v.2.2.1-3*v.2.2.2.1-v.2.2.2.2.2

def beta (v : P) := v.2.1+3*v.2.2.1-3*v.2.2.2.2.1-2*v.2.2.2.2.2

def principal (v : P) : P :=
 (2*v.1-v.2.1,4*v.1-15*v.2.2.1,v.1-2*v.2.2.1,
  2*v.2.2.2.1-v.2.2.2.2.1,4*v.2.2.2.1-15*v.2.2.2.2.2,v.2.2.2.1-2*v.2.2.2.2.2)

theorem alpha_carry (v : P) :
  alpha (principal v) = -beta v + 7*(v.2.2.1-v.2.2.2.1) := by
  rcases v with ⟨a,b,c,d,e,f⟩
  simp [alpha, beta, principal]
  omega

theorem beta_carry (v : P) :
  beta (principal v) = 7*(v.1-3*v.2.2.1-2*v.2.2.2.1+7*v.2.2.2.2.2) := by
  rcases v with ⟨a,b,c,d,e,f⟩
  simp [beta, principal]
  omega

def wedge (a b c d : Int) := a*d-b*c

theorem principal_wedge_zero (a b : Int) : wedge (-a) 0 (-b) 0=0 := by
  simp [wedge]

theorem principal_label_square (a b : Int) :
   let transform := fun v : Int × Int => (-v.2,0)
   transform (transform (a,b)) = (0,0) := by rfl

end H12PrincipalModel
