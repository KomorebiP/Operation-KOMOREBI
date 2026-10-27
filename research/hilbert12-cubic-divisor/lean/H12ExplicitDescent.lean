import Std
namespace H12ExplicitDescent

structure V where
  x0 : Int
  x1 : Int
  x2 : Int
  y0 : Int
  y1 : Int
  y2 : Int
  deriving DecidableEq, Repr

def add (v w : V) : V :=
  ⟨v.x0+w.x0,v.x1+w.x1,v.x2+w.x2,v.y0+w.y0,v.y1+w.y1,v.y2+w.y2⟩
def zero : V := ⟨0,0,0,0,0,0⟩
def original (v : V) : V :=
  ⟨v.x1,-4*v.x0+2*v.x1+15*v.x2,-v.x0+4*v.x2,
   v.y1,-4*v.y0+2*v.y1+15*v.y2,-v.y0+4*v.y2⟩
def rotate (v : V) : V := ⟨-v.y0,-v.y1,-v.y2,v.x0-v.y0,v.x1-v.y1,v.x2-v.y2⟩
def twisted (v : V) : V := rotate (original v)
def alpha (v : V) : Int := v.x0-2*v.x2-3*v.y0-v.y2
def beta (v : V) : Int := v.x1+3*v.x2-3*v.y1-2*v.y2
def aCarry (v : V) : Int := -v.x1-2*v.x2+2*v.y1+3*v.y2
def bCarry (v : V) : Int := 2*v.x0-v.x1-8*v.x2-v.y0+v.y1+4*v.y2

theorem alpha_add (v w : V) : alpha (add v w)=alpha v+alpha w := by
  cases v; cases w; simp only [alpha,add]; omega

theorem beta_add (v w : V) : beta (add v w)=beta v+beta w := by
  cases v; cases w; simp only [beta,add]; omega

theorem alpha_twisted (v : V) :
    alpha (twisted v)=alpha v+4*beta v+7*aCarry v := by
  cases v; simp only [alpha,beta,twisted,original,rotate,aCarry]; omega

theorem beta_twisted (v : V) :
    beta (twisted v)=beta v+7*bCarry v := by
  cases v; simp only [beta,twisted,original,rotate,bCarry]; omega

theorem alpha_original (v : V) :
    alpha (original v)=2*alpha v+beta v+7*(-v.x2+v.y0) := by
  cases v; simp only [alpha,beta,original]; omega

theorem beta_original (v : V) :
    beta (original v)=2*beta v+7*(-v.x0+3*v.x2+2*v.y0-7*v.y2) := by
  cases v; simp only [beta,original]; omega

theorem alpha_rotation (v : V) :
    alpha (rotate v)=4*alpha v+7*(-v.x0+v.x2+2*v.y0+v.y2) := by
  cases v; simp only [alpha,rotate]; omega

theorem beta_rotation (v : V) :
    beta (rotate v)=4*beta v+7*(-v.x1-2*v.x2+2*v.y1+v.y2) := by
  cases v; simp only [beta,rotate]; omega

def liftPair (a b : Int) : V := ⟨a,b,0,0,0,0⟩
theorem quotient_section (a b : Int) :
    alpha (liftPair a b)=a ∧ beta (liftPair a b)=b := by
  simp [alpha,beta,liftPair]

def alt (a b c d : Int) : Int := a*d-b*c

theorem cocycle_identity (a b c d e f : Int) :
    4*alt a b c d + 4*alt (a+c) (b+d) e f =
    4*alt c d e f + 4*alt a b (c+e) (d+f) := by
  simp only [alt]; grind

theorem alternating_swap (a b c d : Int) : alt a b c d = -alt c d a b := by
  simp only [alt]; grind

theorem normalized_zero (a b : Int) : alt a b 0 0=0 ∧ alt 0 0 a b=0 := by
  simp [alt]

theorem commutator_exponent (a b c d : Int) :
    4*alt a b c d - 4*alt c d a b = alt a b c d + 7*alt a b c d := by
  simp only [alt]; grind

theorem symplectic_shear (a b c d : Int) :
    alt (a+4*b) b (c+4*d) d = alt a b c d := by
  simp only [alt]; grind

theorem original_multiplier (a b c d : Int) :
    alt (2*a+b) (2*b) (2*c+d) (2*d) = 4*alt a b c d := by
  simp only [alt]; grind

theorem carry_defect (a b c d k l m n : Int) :
    alt (a+4*b+7*k) (b+7*l) (c+4*d+7*m) (d+7*n) - alt a b c d =
    7*(a*n+4*b*n+k*d-b*m-l*c-4*l*d+7*(k*n-l*m)) := by
  simp only [alt]; grind

-- These polynomial identities certify the cochain numerators. The passage
-- to holomorphic functions exp(2*pi*i*.../7) is proved in PROOF.md, not axiomatized.
theorem real_cover_coboundary (az bz an bn am bm : Int) :
    4*alt (az+an) (bz+bn) am bm
      - 4*alt az bz (an+am) (bn+bm)
      + 4*alt az bz an bn = 4*alt an bn am bm := by
  simp only [alt]; grind

theorem full_cover_residual (al bl az bz am bm : Int) :
    4*alt al bl am bm - 4*alt az bz am bm =
    4*alt (al-az) (bl-bz) am bm := by
  simp only [alt]; grind

abbrev E := Int × Int
def emul (x y : E) : E :=
  (x.1*y.1-x.2*y.2,x.1*y.2+x.2*y.1-x.2*y.2)
def esub (x y : E) : E := (x.1-y.1,x.2-y.2)
def hodgeA : List E := [(3,1),(0,0),(1,-2)]
def hodgeB : List E := [(0,0),(3,1),(2,3)]
def hodgeCross : List E :=
 [esub (emul (hodgeA[1]!) (hodgeB[2]!)) (emul (hodgeA[2]!) (hodgeB[1]!)),
  esub (emul (hodgeA[2]!) (hodgeB[0]!)) (emul (hodgeA[0]!) (hodgeB[2]!)),
  esub (emul (hodgeA[0]!) (hodgeB[1]!)) (emul (hodgeA[1]!) (hodgeB[0]!))]

theorem hodge_coordinates : hodgeCross=[(-5,3),(-3,-8),(8,5)] := by decide

theorem hodge_class_residues :
  ((-5-2)%7=0 ∧ (3-3)%7=0) ∧
  ((-3-4)%7=0 ∧ (-8-6)%7=0) ∧
  ((8-8)%7=0 ∧ (5-12)%7=0) := by decide

end H12ExplicitDescent
