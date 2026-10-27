/- Rational changes of the marked order-five Tate curve; no elliptic
uniformization or arithmetic special-value claim is imported here. -/
module
public import Mathlib.Tactic.Ring
public import Mathlib.Tactic.FieldSimp
@[expose] public section
namespace H12.TateMarking
variable {K : Type*} [Field K]

def curve (u x y : K) := y^2+(1-u)*x*y-u*y-x^3+u*x^2
def negY (u x y : K) := -y-(1-u)*x+u
def newU (u : K) := -1/u
def newX (u x : K) := (x-u)/u^2
def newY (u x y : K) := (y-u*x)/u^3
def theta (u x : K) := u^2/(x*(x-u))

theorem negation_involution (u x y : K) : negY u x (negY u x y)=y := by
  dsimp [negY]; ring1

theorem negation_preserves_curve (u x y : K) : curve u x (negY u x y)=curve u x y := by
  dsimp [curve,negY]; ring1

theorem changed_parameter_nonzero (u : K) (hu : u≠0) : newU u≠0 := by
  dsimp [newU]; exact div_ne_zero (neg_ne_zero.mpr one_ne_zero) hu

theorem parameter_twice (u : K) (hu : u≠0) : newU (newU u)=u := by
  dsimp [newU]; field_simp

theorem marking_curve_identity (u x y : K) (hu : u≠0) :
    u^6*curve (newU u) (newX u x) (newY u x y)=curve u x y := by
  dsimp [curve,newU,newX,newY]; field_simp; ring1

theorem marking_preserves_curve (u x y : K) (hu : u≠0) (hc : curve u x y=0) :
    curve (newU u) (newX u x) (newY u x y)=0 := by
  have h := marking_curve_identity u x y hu
  rw [hc] at h
  exact (mul_eq_zero.mp h).resolve_left (pow_ne_zero 6 hu)

theorem marking_x_twice (u x : K) (hu : u≠0) : newX (newU u) (newX u x)=x := by
  dsimp [newX,newU]; field_simp; ring1

theorem marking_y_twice (u x y : K) (hu : u≠0) :
    newY (newU u) (newX u x) (newY u x y)=negY u x y := by
  dsimp [newY,newX,newU,negY]; field_simp; ring1

theorem marking_theta_invariant (u x : K) (hu : u≠0) (hx : x≠0) (hxu : x-u≠0) :
    theta (newU u) (newX u x)=theta u x := by
  have h1 : newX u x≠0 := div_ne_zero hxu (pow_ne_zero 2 hu)
  have h2 : newX u x-newU u=x/u^2 := by dsimp [newX,newU]; field_simp; ring1
  dsimp [theta]
  rw [h2]
  dsimp [newX,newU]
  field_simp

end H12.TateMarking
