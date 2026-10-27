import Std

/-! Exact integer relation lattice for the two independent cubic units.
The last theorem explains a conditional phase-rigidity criterion; it does
not construct an analytic comparison character. -/
namespace H12.ConjugationRelations

abbrev V := Int × Int

def add (x y : V) : V := (x.1+y.1,x.2+y.2)
def sigma (x : V) : V := (-x.2,x.1-x.2)
def kappa (x : V) : V := (-x.1,x.2-x.1)
def rotationRelation (x : V) : V := (-x.1-x.2,x.1-2*x.2)
def reflectionRelation (x : V) : V := (0,2*x.2-x.1)
def residue (x : V) : Int := (x.1+x.2)%3

theorem sigma_order_three (x : V) : sigma (sigma (sigma x)) = x := by
  rcases x with ⟨a,b⟩
  simp [sigma]
  omega

theorem kappa_involution (x : V) : kappa (kappa x) = x := by
  rcases x with ⟨a,b⟩
  simp [kappa]

theorem dihedral_relation (x : V) : kappa (sigma (kappa x)) = sigma (sigma x) := by
  rcases x with ⟨a,b⟩
  simp [sigma,kappa]
  omega

/-- Rotation coinvariants have a visible residue modulo three. -/
theorem residue_rotation (x : V) : residue (sigma x) = residue x := by
  simp only [residue,sigma]
  omega

theorem rotation_kernel_exact (x : V) :
    residue x = 0 ↔ ∃ y : V, rotationRelation y = x := by
  rcases x with ⟨a,b⟩
  constructor
  · intro h
    refine ⟨(-a-(-(a+b)/3),-(a+b)/3), ?_⟩
    simp only [residue] at h
    simp only [rotationRelation,Prod.mk.injEq]
    omega
  · rintro ⟨⟨m,n⟩,h⟩
    simp only [rotationRelation,Prod.mk.injEq] at h
    simp only [residue]
    omega

theorem residue_surjective (n : Int) : ∃ x : V, residue x = n%3 := by
  exact ⟨(n,0),by simp [residue]⟩

/-- The twisted reflection relations destroy all of the remaining Z/3. -/
theorem full_relation_lattice (x : V) :
    add (rotationRelation (-x.1,0))
        (reflectionRelation (-(x.1+x.2),0)) = x := by
  rcases x with ⟨a,b⟩
  simp [add,rotationRelation,reflectionRelation]
  omega

/-- Explicit primitive relation: an exponent basis vector is already a sum
of one rotation relation and one semilinear reflection relation. -/
theorem primitive_relation :
    add (rotationRelation (-1,0)) (reflectionRelation (-1,0)) = (1,0) := by decide

end H12.ConjugationRelations
