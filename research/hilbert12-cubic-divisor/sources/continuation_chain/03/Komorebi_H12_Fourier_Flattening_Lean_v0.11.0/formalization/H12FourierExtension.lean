import H12DualFourier
namespace H12FourierExtension
open H12DualFourier

/-- Numerator of u=-m*(M-I)^(-1), with denominator six. -/
def liftNumerator (m : V) : V :=
  ⟨3*m.x-3*m.y+m.z,-3*m.x-3*m.y-m.z,15*m.x+15*m.y+3*m.z⟩

def rowDelta (u : V) : V :=
  ⟨-u.x-4*u.y-u.z,u.x+u.y,15*u.y+3*u.z⟩

theorem explicit_flat_extension (m : V) : rowDelta (liftNumerator m) =
    ⟨-6*m.x,-6*m.y,-6*m.z⟩ := by
  cases m; simp only [rowDelta,liftNumerator]; congr 1 <;> omega

theorem lift_pairing (m n : V) :
    dot (liftNumerator m) (original n) - dot (liftNumerator m) n = -6*dot m n := by
  cases m; cases n; simp only [dot,liftNumerator,original]; grind

theorem invariant_character_residue (m n : V) :
    (dot (liftNumerator m) (original n))%6=(dot (liftNumerator m) n)%6 := by
  have h := lift_pairing m n
  omega

theorem cubic_based_exponent (m : V) : (3*m.z)%3=0 := by omega

theorem finite_grid_phase_vanishes (q n : Int) :
    (q*n)%q = 0 := by simp

end H12FourierExtension
