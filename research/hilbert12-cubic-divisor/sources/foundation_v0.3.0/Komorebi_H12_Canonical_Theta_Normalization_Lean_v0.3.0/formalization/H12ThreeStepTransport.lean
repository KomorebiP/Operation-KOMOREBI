/- Exact three-step unit carries, and affine preservation at every iterate.
All inputs here are scalars/vectors; theta analytic identities are not assumed. -/
module
public import H12SignedGeometry
public import Mathlib.Data.Rat.Defs
@[expose] public section
namespace H12.ThreeStepTransport
open H12.SignedGeometry
abbrev Vec (A : Type*) := A × A × A

def backward {A : Type*} [CommRing A] (v : Vec A) : Vec A :=
  (8*v.1-4*v.2.1+15*v.2.2,v.1,2*v.1-v.2.1+4*v.2.2)
def cubeMap {A : Type*} [CommRing A] (v : Vec A) : Vec A :=
  (1033*v.1-540*v.2.1+2070*v.2.2,
    90*v.1-47*v.2.1+180*v.2.2,
    264*v.1-138*v.2.1+529*v.2.2)

theorem actual_unit_cube {A : Type*} [CommRing A] (v : Vec A) :
    backward (backward (backward v))=cubeMap v := by
  rcases v with ⟨x,y,z⟩
  apply Prod.ext
  · dsimp [backward,cubeMap]; ring1
  · apply Prod.ext
    · dsimp [backward,cubeMap]; ring1
    · dsimp [backward,cubeMap]; ring1

def oneCarry {A : Type*} [CommRing A] (b c a : A) : Vec A :=
  (690+516*b-270*c+1035*a,
    60+45*b-24*c+90*a,
    176+132*b-69*c+264*a)

theorem actual_three_step_carry (b c a : ℚ) :
    cubeMap (b/2,c/2,1/3+a/2)=
      (b/2+(oneCarry b c a).1,
       c/2+(oneCarry b c a).2.1,
       1/3+a/2+(oneCarry b c a).2.2) := by
  apply Prod.ext
  · dsimp [cubeMap,oneCarry]; ring1
  · apply Prod.ext
    · dsimp [cubeMap,oneCarry]; ring1
    · dsimp [cubeMap,oneCarry]; ring1

def plus (u v : Vec ℤ) : Vec ℤ := (u.1+v.1,u.2.1+v.2.1,u.2.2+v.2.2)
def accum : ℕ → ℤ → ℤ → ℤ → Vec ℤ
  | 0,_,_,_ => (0,0,0)
  | n+1,b,c,a => plus (cubeMap (accum n b c a)) (oneCarry b c a)

def mix (b c a : ℤ) (u v w z : Vec ℤ) : Vec ℤ :=
  (u.1+b*(v.1-u.1)+c*(w.1-u.1)+a*(z.1-u.1),
   u.2.1+b*(v.2.1-u.2.1)+c*(w.2.1-u.2.1)+a*(z.2.1-u.2.1),
   u.2.2+b*(v.2.2-u.2.2)+c*(w.2.2-u.2.2)+a*(z.2.2-u.2.2))

theorem all_iterates_affine (n : ℕ) (b c a : ℤ) :
    accum n b c a=mix b c a (accum n 0 0 0) (accum n 1 0 0)
      (accum n 0 1 0) (accum n 0 0 1) := by
  induction n with
  | zero => simp [accum,mix]
  | succ n ih =>
    simp only [accum]
    rw [ih]
    apply Prod.ext
    · dsimp [plus,cubeMap,oneCarry,mix]; ring1
    · apply Prod.ext
      · dsimp [plus,cubeMap,oneCarry,mix]; ring1
      · dsimp [plus,cubeMap,oneCarry,mix]; ring1

def eta (n : ℕ) (b c a : ℤ) : ℤ :=
  (accum n b c a).1-(accum n b c a).2.1

theorem all_iterates_eta_affine (n : ℕ) (b c a : ℤ) :
    eta n b c a=eta n 0 0 0+b*(eta n 1 0 0-eta n 0 0 0)+
      c*(eta n 0 1 0-eta n 0 0 0)+a*(eta n 0 0 1-eta n 0 0 0) := by
  unfold eta
  rw [all_iterates_affine n b c a]
  dsimp [mix]; ring1

end H12.ThreeStepTransport
