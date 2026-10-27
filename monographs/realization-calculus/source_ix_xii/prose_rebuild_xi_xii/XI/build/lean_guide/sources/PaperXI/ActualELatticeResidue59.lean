import PaperXI.ActualIntegralGeneralLinear
import PaperXI.ActualLocalUnitDecomposition
import Mathlib.LinearAlgebra.Matrix.GeneralLinearGroup.Defs

/-!
# Literal residue action on an extension-field lattice

The group and the congruence kernel below are the actual integral matrices on
`E^n`, viewed as `K`-linear operators. The next lattice is multiplication of the
integral lattice by the chosen actual uniformizer.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualELatticeResidue59
open Matrix ValuativeRel

variable (K E : Type*) [Field K] [Field E] [Algebra K E]
variable (n : Type*) [Fintype n] [DecidableEq n]

def restrictScalarMatrix : GeneralLinearGroup n E →* ((n → E) ≃ₗ[K] (n → E)) where
  toFun g := (GeneralLinearGroup.toLin g).toLinearEquiv.restrictScalars K
  map_one' := by ext v i; simp
  map_mul' g h := by ext v i; simp

@[simp] theorem restrictScalarMatrix_apply (g : GeneralLinearGroup n E) (v : n → E) :
    restrictScalarMatrix K E n g v = (g : Matrix n n E) *ᵥ v := rfl

theorem restrictScalarMatrix_injective : Function.Injective (restrictScalarMatrix K E n) := by
  intro g h he
  apply GeneralLinearGroup.ext
  intro i j
  have hv := congrArg (fun f : ((n → E) ≃ₗ[K] (n → E)) => f (Pi.single j 1) i) he
  simpa [Matrix.mulVec, dotProduct, Pi.single_apply] using hv

variable [ValuativeRel E]

def integralMatrix : GeneralLinearGroup n 𝒪[E] →* ((n → E) ≃ₗ[K] (n → E)) :=
  (restrictScalarMatrix K E n).comp (ActualIntegralGeneralLinear.embedding E n)

theorem integralMatrix_injective : Function.Injective (integralMatrix K E n) :=
  (restrictScalarMatrix_injective K E n).comp
    (ActualIntegralGeneralLinear.embedding_injective E n)

def integralLattice : AddSubgroup (n → E) where
  carrier := {v | ∀ i, v i ∈ (valuation E).integer}
  zero_mem' := by intro i; exact (valuation E).integer.zero_mem
  add_mem' := by intro v w hv hw i; exact (valuation E).integer.add_mem (hv i) (hw i)
  neg_mem' := by intro v hv i; exact (valuation E).integer.neg_mem (hv i)

omit [Fintype n] [DecidableEq n] in
@[simp] theorem mem_integralLattice (v : n → E) :
    v ∈ integralLattice E n ↔ ∀ i, v i ∈ (valuation E).integer := Iff.rfl

omit [Algebra K E] [Fintype n] [DecidableEq n] in
theorem integralLattice_coe (v : n → 𝒪[E]) :
    (fun i => (v i : E)) ∈ integralLattice E n := fun i => (v i).property

@[simp] theorem integralMatrix_coe (g : GeneralLinearGroup n 𝒪[E]) (v : n → 𝒪[E]) :
    integralMatrix K E n g (fun i => (v i : E)) =
      fun i => (((g : Matrix n n 𝒪[E]) *ᵥ v) i : E) := by
  ext i
  simp [integralMatrix, Matrix.mulVec, dotProduct]

theorem integralMatrix_preserves (g : GeneralLinearGroup n 𝒪[E]) (v : n → E)
    (hv : v ∈ integralLattice E n) : integralMatrix K E n g v ∈ integralLattice E n := by
  let w : n → 𝒪[E] := fun i => ⟨v i, hv i⟩
  change integralMatrix K E n g (fun i => (w i : E)) ∈ integralLattice E n
  rw [integralMatrix_coe]
  exact integralLattice_coe E n _

variable [TopologicalSpace E] [IsNonarchimedeanLocalField E]

/-- The actual next lattice is multiplication by the chosen `E`-uniformizer. -/
def nextLattice : AddSubgroup (n → E) :=
  (integralLattice E n).map
    ((ActualLocalUnitDecomposition.uniformizer E : E) • (LinearMap.id : (n → E) →ₗ[E] (n → E))).toAddMonoidHom

omit [Fintype n] [DecidableEq n] in
@[simp] theorem mem_nextLattice (v : n → E) :
    v ∈ nextLattice E n ↔ ∃ w ∈ integralLattice E n,
      (ActualLocalUnitDecomposition.uniformizer E : E) • w = v := Iff.rfl

omit [Algebra K E] [Fintype n] [DecidableEq n] in
theorem coe_mem_nextLattice_iff (v : n → 𝒪[E]) :
    (fun i => (v i : E)) ∈ nextLattice E n ↔
      ∀ i, v i ∈ IsLocalRing.maximalIdeal 𝒪[E] := by
  classical
  rw [mem_nextLattice]
  have hπ := (IsDiscreteValuationRing.irreducible_iff_uniformizer
    (ActualLocalUnitDecomposition.uniformizer E)).mp
      (ActualLocalUnitDecomposition.uniformizer_irreducible E)
  constructor
  · rintro ⟨w, hw, he⟩ i
    rw [hπ, Ideal.mem_span_singleton]
    refine ⟨⟨w i, hw i⟩, ?_⟩
    apply Subtype.ext
    exact (congrFun he i).symm
  · intro hv
    have hd : ∀ i, ∃ w : 𝒪[E], v i = ActualLocalUnitDecomposition.uniformizer E * w := by
      intro i
      have hi := hv i
      rw [hπ, Ideal.mem_span_singleton] at hi
      obtain ⟨w, hw⟩ := hi
      exact ⟨w, hw⟩
    choose w hw using hd
    refine ⟨fun i => (w i : E), integralLattice_coe E n w, ?_⟩
    ext i
    exact congrArg (fun x : 𝒪[E] => (x : E)) (hw i).symm

/-- Congruence on the actual lattice is exactly entrywise residue reduction. -/
theorem reduction_kernel_iff (g : GeneralLinearGroup n 𝒪[E]) :
    g ∈ (ActualResidueGeneralLinear.reduction E n).ker ↔
      ∀ v ∈ integralLattice E n,
        integralMatrix K E n g v - v ∈ nextLattice E n := by
  classical
  rw [ActualIntegralGeneralLinear.mem_reduction_kernel]
  constructor
  · intro hg v hv
    let w : n → 𝒪[E] := fun i => ⟨v i, hv i⟩
    change integralMatrix K E n g (fun i => (w i : E)) - (fun i => (w i : E)) ∈ _
    rw [integralMatrix_coe]
    change (fun i => ((((g : Matrix n n 𝒪[E]) *ᵥ w - w) i) : E)) ∈ _
    rw [coe_mem_nextLattice_iff]
    intro i
    have he : ((g : Matrix n n 𝒪[E]) *ᵥ w - w) i =
        ∑ j, (g i j - (1 : Matrix n n 𝒪[E]) i j) * w j := by
      simp [Matrix.mulVec, dotProduct, sub_mul, Finset.sum_sub_distrib, Matrix.one_apply]
    rw [he]
    exact Ideal.sum_mem _ fun j _ => Ideal.mul_mem_right _ _ (hg i j)
  · intro hg i j
    let w : n → 𝒪[E] := Pi.single j 1
    have hv := hg (fun i => (w i : E)) (integralLattice_coe E n w)
    rw [integralMatrix_coe] at hv
    change (fun i => ((((g : Matrix n n 𝒪[E]) *ᵥ w - w) i) : E)) ∈ _ at hv
    rw [coe_mem_nextLattice_iff] at hv
    simpa [w, Matrix.mulVec, dotProduct, Matrix.one_apply, Pi.single_apply, eq_comm] using hv i

/-- The concrete integral matrix image among `K`-linear automorphisms. -/
def integralImage : Subgroup ((n → E) ≃ₗ[K] (n → E)) := (integralMatrix K E n).range

def integralImageEquiv : GeneralLinearGroup n 𝒪[E] ≃* integralImage K E n :=
  MonoidHom.ofInjective (integralMatrix_injective K E n)

def residueAction : integralImage K E n →* GeneralLinearGroup n 𝓀[E] :=
  (ActualResidueGeneralLinear.reduction E n).comp (integralImageEquiv K E n).symm.toMonoidHom

theorem residueAction_surjective : Function.Surjective (residueAction K E n) :=
  (ActualResidueGeneralLinear.reduction_surjective E n).comp
    (integralImageEquiv K E n).symm.surjective

/-- The literal finite residue group of this actual extension-field lattice. -/
def residueQuotientEquiv :
    integralImage K E n ⧸ (residueAction K E n).ker ≃* GeneralLinearGroup n 𝓀[E] :=
  QuotientGroup.quotientKerEquivOfSurjective (residueAction K E n)
    (residueAction_surjective K E n)

end PaperXI.ActualELatticeResidue59
