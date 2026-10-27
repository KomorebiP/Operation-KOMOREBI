import Std
namespace H12MixedGauge

-- The pair is a coefficient vector for 1 and omega; no analytic exponentials
-- or holomorphic cohomology are silently assumed in these integer identities.
abbrev E := Int × Int
def eadd (p q : E) : E := (p.1+q.1,p.2+q.2)
def esub (p q : E) : E := (p.1-q.1,p.2-q.2)
def emul (p q : E) : E :=
  (p.1*q.1-p.2*q.2,p.1*q.2+p.2*q.1-p.2*q.2)
def escale (n : Int) (p : E) : E := (n*p.1,n*p.2)
def om : E := (0,1)

structure V where
  x0 : Int
  x1 : Int
  x2 : Int
  y0 : Int
  y1 : Int
  y2 : Int
  deriving DecidableEq, Repr

def plus (v w : V) : V :=
  ⟨v.x0+w.x0,v.x1+w.x1,v.x2+w.x2,v.y0+w.y0,v.y1+w.y1,v.y2+w.y2⟩
def e0 : V := ⟨1,0,0,0,0,0⟩
def omegaE1 : V := ⟨0,0,0,0,1,0⟩
def realV (a b c : Int) : V := ⟨a,b,c,0,0,0⟩
def alpha (v : V) : Int := v.x0-2*v.x2-3*v.y0-v.y2
def beta (v : V) : Int := v.x1+3*v.x2-3*v.y1-2*v.y2
def modelAlt (v w : V) : Int := alpha v*beta w-beta v*alpha w

-- Logarithm of the gauge b_lambda(z)=exp(2*pi*i*t*m_1*z_0).
def gaugeLog (v : V) (z : E) : E := escale v.y1 z
def deltaLog (v w : V) (z : E) : E :=
  eadd (esub (gaugeLog w (eadd z (v.x0,v.y0))) (gaugeLog (plus v w) z))
    (gaugeLog v z)
def skewLog (v w : V) : E :=
  (v.x0*w.y1-w.x0*v.y1,v.y0*w.y1-w.y0*v.y1)

theorem zero_anchor (v : V) : gaugeLog v (0,0)=(0,0) := by simp [gaugeLog,escale]

theorem real_restriction (a b c : Int) (z : E) : gaugeLog (realV a b c) z=(0,0) := by
  simp [gaugeLog,realV,escale]

theorem gauge_boundary (v w : V) (z : E) :
    deltaLog v w z=(v.x0*w.y1,v.y0*w.y1) := by
  simp only [deltaLog,gaugeLog,eadd,esub,escale,plus]
  apply Prod.ext <;> dsimp <;> grind

theorem gauge_alternating (v w : V) (z : E) :
    esub (deltaLog v w z) (deltaLog w v z)=skewLog v w := by
  rw [gauge_boundary,gauge_boundary]
  rfl

theorem changed_mixed_entry : skewLog e0 omegaE1=(1,0) := by decide

theorem unchanged_real_entries (a b c d e f : Int) :
    skewLog (realV a b c) (realV d e f)=(0,0) := by simp [skewLog,realV]

theorem model_mixed_entry : modelAlt e0 omegaE1 = -3 := by decide

-- For a pair of spatial indices, normalized Hodge projection is
-- omega^2*A - omega*(B_ij-B_ji) + C. The gauge adds B=1,C=omega.
def hodge (A B C : E) : E :=
  eadd (esub (emul (-1,-1) A) (emul om B)) C

theorem holomorphic_gauge_hodge_zero : hodge (0,0) (1,0) om=(0,0) := by decide

theorem holomorphic_gauge_hodge_zero_scaled (k : Int) :
    hodge (0,0) (k,0) (0,k)=(0,0) := by
  simp only [hodge,eadd,esub,emul,om]; apply Prod.ext <;> dsimp <;> grind

theorem hodge_integer_formula (a b c : Int) :
    hodge (a,0) (b,0) (c,0)=(c-a,-a-b) := by
  simp only [hodge,eadd,esub,emul,om]; apply Prod.ext <;> dsimp <;> grind

-- The primitive model's FULL Hodge class survives the gauge even though
-- its one selected mixed commutator changes.
def modelH : List E := [(-5,3),(-3,-8),(8,5)]
theorem primitive_hodge_residue :
    modelH=[eadd (2,3) (escale 7 (-1,0)),
            eadd (4,6) (escale 7 (-1,-2)),
            eadd (8,12) (escale 7 (0,-1))] := by decide

theorem model_class_nonzero_mod_seven : ((-5:Int)%7=2) ∧ ((3:Int)%7=3) := by decide

-- Scalar finite-difference quotients always telescope around a square.
-- This polynomial cross-multiplication certificate uses no divisions.
theorem scalar_square_cleared (a b c d : Int) :
    (d*b)*(c*a)=(d*c)*(b*a) := by grind

end H12MixedGauge
