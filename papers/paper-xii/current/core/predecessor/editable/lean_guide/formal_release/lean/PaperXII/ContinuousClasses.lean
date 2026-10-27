import PaperXII.AdicSpines
import PaperX.ClassInvariants
import Mathlib.Basic.Finite.Sigma

/-! Bridge actual continuous GL representations to the checked change-of-basis
classes. Finite coefficient rings make each individual fiber finite, even for
an infinite source group. No choice of compatible frames is assumed. -/
set_option autoImplicit false
namespace PaperXII.ContinuousClasses

open ContinuousMonoidHom Matrix
open PaperX.RepresentationLimits PaperX.RepresentationClasses
open PaperX.RepresentationTopology PaperX.ClassInvariants

variable {Γ ι S : Type} [Group Γ] [TopologicalSpace Γ]
    [Fintype ι] [DecidableEq ι] [CommRing S] [TopologicalSpace S]

/-- Forget the topology and retain the actual matrix representation. -/
def matrixRep (ρ : Γ →ₜ* GL ι S) : MatrixRep S Γ ι where
  toFun g := (ρ g).val
  map_one' := congrArg Units.val ρ.map_one
  map_mul' g h := congrArg Units.val (ρ.map_mul g h)

/-- The underlying matrix representation determines the continuous GL map. -/
theorem matrixRep_injective : Function.Injective (matrixRep (Γ := Γ) (ι := ι) (S := S)) := by
  intro ρ σ h
  apply ContinuousMonoidHom.ext
  intro g
  apply Units.ext
  exact DFunLike.congr_fun h g

/-- The actual change-of-basis class of a continuous representation. -/
def classOfRep (ρ : Γ →ₜ* GL ι S) : ClassRep S Γ ι := classOf (matrixRep ρ)

/-- Locally constant matrix entries produce an actual continuous GL representation. -/
noncomputable def fromMatrix (ρ : MatrixRep S Γ ι) (hρ : FiniteRepContinuous ρ) :
    Γ →ₜ* GL ι S where
  __ := ρ.toHomUnits
  continuous_toFun := by
    apply IsLocallyConstant.continuous
    apply (IsLocallyConstant.iff_eventually_eq _).mpr
    intro g
    filter_upwards [finiteRepContinuous_matrix ρ hρ g] with h hh
    exact Units.ext hh

/-- Passing to GL and forgetting back to matrices is exact. -/
theorem matrixRep_fromMatrix (ρ : MatrixRep S Γ ι) (hρ : FiniteRepContinuous ρ) :
    matrixRep (fromMatrix ρ hρ) = ρ := rfl

/-- A continuous representation into discrete coefficients has locally constant entries. -/
theorem matrixRep_finiteContinuous [DiscreteTopology S] (ρ : Γ →ₜ* GL ι S) :
    FiniteRepContinuous (matrixRep ρ) := by
  intro i j
  apply (IsLocallyConstant.iff_eventually_eq _).mp
  apply (IsLocallyConstant.iff_continuous _).mpr
  have hm : Continuous (fun g : Γ ↦ (ρ g).val) := Units.continuous_val.comp ρ.continuous
  exact (continuous_apply j).comp ((continuous_apply i).comp hm)

/-- Every class arising from a continuous finite representation is a continuous class. -/
theorem classOfRep_continuous [DiscreteTopology S] (ρ : Γ →ₜ* GL ι S) :
    ClassContinuous (classOfRep ρ) := matrixRep_finiteContinuous ρ

/-- A continuous class has an actual continuous representative. -/
theorem exists_continuous_representative (c : ClassRep S Γ ι) (hc : ClassContinuous c) :
    ∃ ρ : Γ →ₜ* GL ι S, classOfRep ρ = c := by
  obtain ⟨σ, rfl⟩ := classOf_surjective c
  exact ⟨fromMatrix σ hc, rfl⟩

/-- The class-level continuity condition is precisely existence of a continuous frame. -/
theorem continuous_class_iff [DiscreteTopology S] (c : ClassRep S Γ ι) :
    ClassContinuous c ↔ ∃ ρ : Γ →ₜ* GL ι S, classOfRep ρ = c := by
  refine ⟨exists_continuous_representative c, ?_⟩
  rintro ⟨ρ, rfl⟩
  exact classOfRep_continuous ρ

/-- Individual continuous class fibers are finite over finite coefficients. -/
theorem finite_continuous_fiber [Finite S] (c : ClassRep S Γ ι) :
    Finite {ρ : Γ →ₜ* GL ι S // classOfRep ρ = c} := by
  let _ : Finite {ρ : MatrixRep S Γ ι // classOf ρ = c} := finite_class_fiber c
  let f : {ρ : Γ →ₜ* GL ι S // classOfRep ρ = c} →
      {ρ : MatrixRep S Γ ι // classOf ρ = c} := fun ρ ↦ ⟨matrixRep ρ.val, ρ.property⟩
  apply Finite.of_injective f
  intro ρ σ h
  apply Subtype.ext
  exact matrixRep_injective (congrArg Subtype.val h)

/-- Finitely many admissible classes give finitely many actual continuous frames. -/
theorem finite_allowed_frames [Finite S] (C : ClassRep S Γ ι → Prop)
    [Finite {c // C c}] : Finite {ρ : Γ →ₜ* GL ι S // C (classOfRep ρ)} := by
  let _ : ∀ c : {c // C c}, Finite {ρ : Γ →ₜ* GL ι S // classOfRep ρ = c.val} :=
    fun c ↦ finite_continuous_fiber c.val
  let f : {ρ : Γ →ₜ* GL ι S // C (classOfRep ρ)} →
      Σ c : {c // C c}, {ρ : Γ →ₜ* GL ι S // classOfRep ρ = c.val} :=
    fun ρ ↦ ⟨⟨classOfRep ρ.val, ρ.property⟩, ⟨ρ.val, rfl⟩⟩
  apply Finite.of_injective f
  intro ρ σ h
  exact Subtype.ext (congrArg (fun x ↦ x.2.val) h)

/-- Class invariants refer to the full characteristic polynomial of the actual map. -/
theorem classCharpoly_classOfRep (ρ : Γ →ₜ* GL ι S) (g : Γ) :
    classCharpoly (classOfRep ρ) g = (ρ g).val.charpoly := rfl

/-- Class triviality is exactly triviality of the actual continuous representation. -/
theorem classTrivial_classOfRep (H : Subgroup Γ) (ρ : Γ →ₜ* GL ι S) :
    ClassTrivial H (classOfRep ρ) ↔ ∀ g, g ∈ H → ρ g = 1 := by
  constructor
  · intro h g hg
    exact Units.ext (h g hg)
  · intro h g hg
    exact congrArg Units.val (h g hg)

end PaperXII.ContinuousClasses
