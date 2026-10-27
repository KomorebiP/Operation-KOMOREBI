import Mathlib.Data.ZMod.Basic
import Mathlib.LinearAlgebra.Isomorphisms
import Mathlib.LinearAlgebra.FreeModule.Int

noncomputable section

namespace KomorebiCrossRadix

/-- Integral coordinate families on an arbitrary index type. -/
abbrev IntFamily (ι : Type*) := ι → ℤ

/-- Coordinatewise reduction modulo `D`. -/
def reduceModFamily (D : ℕ) (κ : Type*) : IntFamily κ →ₗ[ℤ] (κ → ZMod D) where
  toFun x := fun i => (x i : ZMod D)
  map_add' x y := by ext i; simp
  map_smul' c x := by ext i; simp

/-- Reduce the output of an integral numerator map modulo its declared denominator. -/
def denominatorDefectMapOn {ι κ : Type*} (D : ℕ)
    (A : IntFamily ι →ₗ[ℤ] IntFamily κ) :
    IntFamily ι →ₗ[ℤ] (κ → ZMod D) :=
  (reduceModFamily D κ).comp A

/-- The maximal integral lattice on which division by `D` after applying `A`
produces integral coordinates. -/
def ProjectorGoodLatticeOn {ι κ : Type*} (D : ℕ)
    (A : IntFamily ι →ₗ[ℤ] IntFamily κ) :
    Submodule ℤ (IntFamily ι) :=
  LinearMap.ker (denominatorDefectMapOn D A)

/-- Membership in the good lattice is exactly coordinatewise divisibility of the
numerator output by `D`. -/
theorem mem_ProjectorGoodLatticeOn_iff {ι κ : Type*} {D : ℕ}
    (A : IntFamily ι →ₗ[ℤ] IntFamily κ) (x : IntFamily ι) :
    x ∈ ProjectorGoodLatticeOn D A ↔ ∀ i, (D : ℤ) ∣ A x i := by
  change (fun i => ((A x i : ℤ) : ZMod D)) = 0 ↔ _
  constructor
  · intro h i
    have hi := congrFun h i
    exact (CharP.intCast_eq_zero_iff (ZMod D) D (A x i)).mp hi
  · intro h
    funext i
    exact (CharP.intCast_eq_zero_iff (ZMod D) D (A x i)).mpr (h i)

/-- The residual denominator defect is the actual image of the numerator map
modulo `D`. -/
def ProjectorDefectModuleOn {ι κ : Type*} (D : ℕ)
    (A : IntFamily ι →ₗ[ℤ] IntFamily κ) :
    Submodule ℤ (κ → ZMod D) :=
  LinearMap.range (denominatorDefectMapOn D A)

/-- Exact first-isomorphism theorem for an arbitrary integral numerator/denominator
presentation. -/
noncomputable def projectorDefectEquivOn {ι κ : Type*} (D : ℕ)
    (A : IntFamily ι →ₗ[ℤ] IntFamily κ) :
    (IntFamily ι ⧸ ProjectorGoodLatticeOn D A) ≃ₗ[ℤ] ProjectorDefectModuleOn D A :=
  LinearMap.quotKerEquivRange (denominatorDefectMapOn D A)

/-- Every defect class is annihilated by the denominator. -/
theorem projectorDefectOn_annihilated {ι κ : Type*} {D : ℕ}
    (A : IntFamily ι →ₗ[ℤ] IntFamily κ) (y : ProjectorDefectModuleOn D A) :
    (D : ℤ) • y = 0 := by
  apply Subtype.ext
  funext i
  simp

/-- Prime-power specialization: the residual defect is a `p^k`-torsion module. -/
theorem primePowerProjectorDefectOn_annihilated {ι κ : Type*} {p k : ℕ}
    (A : IntFamily ι →ₗ[ℤ] IntFamily κ) (y : ProjectorDefectModuleOn (p^k) A) :
    ((p^k : ℕ) : ℤ) • y = 0 := by
  simpa using projectorDefectOn_annihilated (D := p^k) A y

/-- On a finite domain coordinate type, the good lattice has a Smith normal form.
This provides canonical PID invariant-factor data for the denominator defect. -/
noncomputable def projectorGoodLatticeOnSmithNormalForm
    {ι κ : Type*} [Fintype ι] (D : ℕ)
    (A : IntFamily ι →ₗ[ℤ] IntFamily κ) :
    Σ r : ℕ, Module.Basis.SmithNormalForm (ProjectorGoodLatticeOn D A) ι r :=
  (ProjectorGoodLatticeOn D A).smithNormalForm (Pi.basisFun ℤ ι)

/-- Finite-coordinate aliases retained for compatibility with the v0.10 prototype. -/
abbrev IntVec (n : ℕ) := IntFamily (Fin n)
def reduceModVec (D m : ℕ) := reduceModFamily D (Fin m)
def denominatorDefectMap {n m : ℕ} (D : ℕ) (A : IntVec n →ₗ[ℤ] IntVec m) :=
  denominatorDefectMapOn D A
def ProjectorGoodLattice {n m : ℕ} (D : ℕ) (A : IntVec n →ₗ[ℤ] IntVec m) :=
  ProjectorGoodLatticeOn D A
def ProjectorDefectModule {n m : ℕ} (D : ℕ) (A : IntVec n →ₗ[ℤ] IntVec m) :=
  ProjectorDefectModuleOn D A

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.mem_ProjectorGoodLatticeOn_iff
#print axioms KomorebiCrossRadix.projectorDefectEquivOn
#print axioms KomorebiCrossRadix.projectorDefectOn_annihilated
#print axioms KomorebiCrossRadix.projectorGoodLatticeOnSmithNormalForm
