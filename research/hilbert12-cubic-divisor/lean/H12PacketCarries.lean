/- Exact rational unit matrices and their half-grid carries. -/
module
public import Mathlib.Tactic.Ring.Basic
public import Mathlib.Data.Rat.Defs
public section
namespace H12.PacketCarries
abbrev Triple := ℚ × ℚ × ℚ

def forward (p : Triple) : Triple :=
  (p.2.1, -4*p.1+2*p.2.1+15*p.2.2, -p.1+4*p.2.2)
def backward (p : Triple) : Triple :=
  (8*p.1-4*p.2.1+15*p.2.2, p.1, 2*p.1-p.2.1+4*p.2.2)
def point (b c a : ℚ) : Triple := (b/2,c/2,1/3+a/2)
def rotate {A : Type*} (p : A × A × A) : A × A × A := (p.2.2,p.1,p.2.1)

theorem forward_backward (p : Triple) : forward (backward p)=p := by
  rcases p with ⟨x,y,z⟩
  apply Prod.ext
  · rfl
  · apply Prod.ext
    · dsimp [forward,backward]; ring1
    · dsimp [forward,backward]; ring1

theorem backward_forward (p : Triple) : backward (forward p)=p := by
  rcases p with ⟨x,y,z⟩
  apply Prod.ext
  · dsimp [forward,backward]; ring1
  · apply Prod.ext
    · rfl
    · dsimp [forward,backward]; ring1

theorem rotate_cube {A : Type*} (p : A × A × A) : rotate (rotate (rotate p))=p := by
  rcases p with ⟨x,y,z⟩; rfl

theorem inverse_carry (b c a : ℚ) :
    backward (point b c a)=
      (a/2+(5+4*b-2*c+7*a), b/2, 1/3+c/2+(1+b-c+2*a)) := by
  apply Prod.ext
  · dsimp [backward,point]; ring1
  · apply Prod.ext
    · rfl
    · dsimp [backward,point]; ring1

theorem forward_carry (b c a : ℚ) :
    forward (point b c a)=
      (c/2, a/2+(5-2*b+c+7*a), 1/3+b/2+(1-b+2*a)) := by
  apply Prod.ext
  · rfl
  · apply Prod.ext
    · dsimp [forward,point]; ring1
    · dsimp [forward,point]; ring1

end H12.PacketCarries
