/-
Exact integer-lattice algebra for the theta/kernel translation classes.
The analytic identification with elliptic divisors is proved in PROOF.md,
not assumed as an axiom in this file.
-/
module
public import Mathlib.Tactic.Ring.Basic
public section
namespace H12.NormProjector
abbrev Pair := ℤ × ℤ

def evenNorm (v : Pair) : Pair := (v.1 - 6*v.2, 0)
def thetaAxis (a : ℤ) : Pair := (a,0)
def primitiveAxis (b : ℤ) : Pair := (6*b,b)
def coordinates (v : Pair) : Pair := (v.1-6*v.2,v.2)
def fromCoordinates (v : Pair) : Pair := (v.1+6*v.2,v.2)

theorem projector_idempotent (v : Pair) : evenNorm (evenNorm v)=evenNorm v := by
  cases v with | mk a b => simp [evenNorm]

theorem theta_axis_fixed (a : ℤ) : evenNorm (thetaAxis a)=thetaAxis a := by
  simp [evenNorm,thetaAxis]

theorem primitive_axis_killed (b : ℤ) : evenNorm (primitiveAxis b)=(0,0) := by
  simp [evenNorm,primitiveAxis]

theorem kernel_exact (v : Pair) : evenNorm v=(0,0) ↔ v=primitiveAxis v.2 := by
  rcases v with ⟨a,b⟩
  simp only [evenNorm,primitiveAxis,Prod.mk.injEq,and_true]
  omega

theorem fixed_exact (v : Pair) : evenNorm v=v ↔ v.2=0 := by
  rcases v with ⟨a,b⟩
  simp only [evenNorm,Prod.mk.injEq]
  omega

theorem coordinates_inverse (v : Pair) : fromCoordinates (coordinates v)=v := by
  rcases v with ⟨a,b⟩
  simp [coordinates,fromCoordinates]

theorem inverse_coordinates (v : Pair) : coordinates (fromCoordinates v)=v := by
  rcases v with ⟨a,b⟩
  simp [coordinates,fromCoordinates]

theorem diagonal_in_split_basis (v : Pair) :
    coordinates (evenNorm v)=((coordinates v).1,0) := by
  rcases v with ⟨a,b⟩
  simp [coordinates,evenNorm]

theorem two_charge_injective (a b : ℤ) (h0 : 4*a+4*b=0) (hhalf : -4*b=0) :
    a=0 ∧ b=0 := by omega

theorem primitive_nonzero (b : ℤ) : primitiveAxis b=(0,0) ↔ b=0 := by
  simp [primitiveAxis]

end H12.NormProjector
