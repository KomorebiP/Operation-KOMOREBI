import Std
namespace H12AnchorObstruction

-- Coefficient proofs for the analytic example g(q)=(q-q^-1)/(omega-omega^2).
-- On the sixth roots, q^-1=q^5. In Z[omega], omega^2=(-1,-1).
abbrev E := Int × Int
def sub (p q : E) : E := (p.1-q.1,p.2-q.2)
def scale (n : Int) (p : E) : E := (n*p.1,n*p.2)
def D : E := (1,2)
def sixthRoot : Fin 6 → E
 | 0 => (1,0)
 | 1 => (0,-1)
 | 2 => (-1,-1)
 | 3 => (-1,0)
 | 4 => (0,1)
 | 5 => (1,1)
def phaseValue : Fin 6 → Int
 | 0 => 0
 | 1 => -1
 | 2 => -1
 | 3 => 0
 | 4 => 1
 | 5 => 1

theorem sixth_root_phase_table : ∀ j : Fin 6,
    sub (sixthRoot j) (sixthRoot ⟨(6-j.val)%6,by omega⟩)=scale (phaseValue j) D := by decide

theorem target_and_anchor : phaseValue 4=1 ∧ phaseValue 0=0 := by decide

theorem inverse_point_phase : phaseValue 2 = -phaseValue 4 := by decide

-- Exact fixed-point enumeration: p_j=j*(-1/2,1/2,-1/6).
-- Multiplying coordinates by six gives (-3j,3j,-j).
theorem fixed_point_carry (j : Int) :
    (-(-3*j)+3*j, -4*(-3*j)+3*j+15*(-j), -(-3*j)+3*(-j))
      = (6*j,0,0) := by
  apply Prod.ext
  · dsimp; omega
  · apply Prod.ext <;> dsimp <;> omega

theorem conductor_label : ((-3*4:Int)%6, (3*4:Int)%6, (-4:Int)%6)=(0,0,2) := by decide

-- A unit-cocycle's free scalar exponent is independent of the lattice
-- character. Relative fixed-point holonomy cancels this exponent.
theorem based_exponent_cancellation (unitPhase charPhase : Int) :
    (unitPhase+2*charPhase)-unitPhase=2*charPhase := by omega

theorem based_cube_exponent (unitPhase charPhase : Int) :
    3*((unitPhase+2*charPhase)-unitPhase)=6*charPhase := by omega

-- Gauge change b(Mx)/b(x) cannot alter the multiplier at a fixed point.
-- The analytic statement is multiplicative; the additive core is exact.
theorem fixed_point_gauge_value (old atMx atX : Int) (h : atMx=atX) :
    old+atMx-atX=old := by omega

-- For additive cocycles, iteration preserves the sum law. This is not an
-- axiom requiring any desired special-value identity.
def orbitSum (f : Nat → Int) : Nat → Int
 | 0 => 0
 | n+1 => orbitSum f n+f n

theorem constant_orbit_sum (a : Int) (n : Nat) :
    orbitSum (fun _ => a) n=(n:Int)*a := by
  induction n with
  | zero => simp [orbitSum]
  | succ n ih => simp only [orbitSum,ih,Int.natCast_add,Int.natCast_one]; grind

end H12AnchorObstruction
