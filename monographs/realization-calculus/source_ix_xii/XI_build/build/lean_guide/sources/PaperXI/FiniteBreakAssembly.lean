import PaperXI.BreakBridgeAlong
import PaperXI.CentralExtensionComparison
import PaperXI.TraceDiscrepancy

/-! Construct the initial tensor bridge and close its honest stabilizer action.
The central extensions (including dyadic square data), their actual lifts,
central characters and actions are inputs. No initial intertwiner, discrepancy
character, finite-dimensional certificate, or final comparison is an input. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FiniteBreakAssembly

variable {I Z C : Type*} [Fintype I] [CommGroup Z] [Group C]
variable {H A H' A' V W : I → Type*}
variable [∀ i, Group (H i)] [∀ i, CommGroup (A i)] [∀ i, Fintype (A i)]
variable [∀ i, Group (H' i)] [∀ i, CommGroup (A' i)]
variable [∀ i, AddCommGroup (V i)] [∀ i, Module ℂ (V i)]
variable [∀ i, AddCommGroup (W i)] [∀ i, Module ℂ (W i)]

/-- Concrete break data. A group lift is required, not merely an alternating
form isometry in residue characteristic two. -/
structure Data where
  source : ∀ i, CentralExtension.Datum Z (H i) (A i)
  target : ∀ i, CentralExtension.Datum Z (H' i) (A' i)
  lift : ∀ i, H i ≃* H' i
  lift_center : ∀ i z, lift i ((source i).i z) = (target i).i z
  centralCharacter : Z →* ℂˣ
  nondegenerate : ∀ i, CocycleCommutator.radical
    (CentralExtension.scalarCocycle (source i) centralCharacter) = ⊥
  leftAction : ∀ i, Representation ℂ (H i) (V i)
  rightAction : ∀ i, Representation ℂ (H' i) (W i)
  leftIrreducible : ∀ i, Representation.IsIrreducible (leftAction i)
  rightIrreducible : ∀ i, Representation.IsIrreducible (rightAction i)
  leftCentral : ∀ i z, leftAction i ((source i).i z) =
    (centralCharacter z : ℂ) • LinearMap.id
  rightCentral : ∀ i z, rightAction i ((target i).i z) =
    (centralCharacter z : ℂ) • LinearMap.id

variable (d : Data (I := I) (Z := Z) (H := H) (A := A) (H' := H') (A' := A')
  (V := V) (W := W))

/-- Every factor intertwiner is obtained from actual central-extension uniqueness. -/
def factor (i : I) : V i ≃ₗ[ℂ] W i := by
  letI := d.leftIrreducible i
  letI := d.rightIrreducible i
  exact (CentralExtensionComparison.equivAlong (d.source i) d.centralCharacter
    (d.nondegenerate i) (d.lift i) (d.leftAction i) (d.rightAction i)
    (d.leftCentral i) (by intro z; rw [d.lift_center]; exact d.rightCentral i z)).toLinearEquiv

omit [Fintype I] in
@[simp] theorem factor_intertwines (i : I) (h : H i) (x : V i) :
    factor d i (d.leftAction i h x) = d.rightAction i (d.lift i h) (factor d i x) := by
  let := d.leftIrreducible i
  let := d.rightIrreducible i
  exact CentralExtensionComparison.equivAlong_intertwines (d.source i) d.centralCharacter
    (d.nondegenerate i) (d.lift i) (d.leftAction i) (d.rightAction i)
    (d.leftCentral i) (by intro z; rw [d.lift_center]; exact d.rightCentral i z) h x

/-- The full break intertwiner is the literal tensor product of the constructed maps. -/
def tensorBridge : PiTensorProduct ℂ V ≃ₗ[ℂ] PiTensorProduct ℂ W :=
  BreakTensorMap.tensor (factor d)

def sourceAction : Representation ℂ (CentralProduct.Group d.source) (PiTensorProduct ℂ V) :=
  HeisenbergTensor.descend d.source d.centralCharacter d.leftAction d.leftCentral

/-- The actual target central product is pulled back by the constructed quotient isomorphism. -/
def targetAction : Representation ℂ (CentralProduct.Group d.source) (PiTensorProduct ℂ W) :=
  (HeisenbergTensor.descend d.target d.centralCharacter d.rightAction d.rightCentral).comp
    (CentralProduct.congr d.source d.target d.lift d.lift_center).toMonoidHom

theorem tensor_intertwines (h : CentralProduct.Group d.source) (x : PiTensorProduct ℂ V) :
    tensorBridge d (sourceAction d h x) = targetAction d h (tensorBridge d x) := by
  exact BreakBridgeAlong.quotient_intertwines d.source d.target d.lift d.lift_center
    d.centralCharacter d.leftAction d.rightAction d.leftCentral d.rightCentral
    (factor d) (factor_intertwines d) h x

include d in
/-- Finite dimensionality and irreducibility are derived before Schur is used. -/
theorem source_finiteDimensional : FiniteDimensional ℂ (PiTensorProduct ℂ V) := by
  let := d.leftIrreducible
  exact HeisenbergTensor.finiteDimensional d.source d.centralCharacter d.nondegenerate
    d.leftAction d.leftCentral

theorem source_irreducible : Representation.IsIrreducible (sourceAction d) := by
  let := d.leftIrreducible
  exact HeisenbergTensor.irreducible d.source d.centralCharacter d.nondegenerate
    d.leftAction d.leftCentral

variable (α : C →* MulAut (CentralProduct.Group d.source))
variable (R : Representation ℂ C (PiTensorProduct ℂ V))
variable (T : Representation ℂ C (PiTensorProduct ℂ W))
variable (hR : ∀ g h x, R g (sourceAction d h x) = sourceAction d (α g h) (R g x))
variable (hT : ∀ g h x, T g (targetAction d h x) = targetAction d (α g h) (T g x))

/-- The actual total discrepancy character, chosen only from the proved Schur law. -/
def discrepancy : C →* ℂˣ := by
  letI := source_finiteDimensional d
  letI := source_irreducible d
  exact Classical.choose (DiscrepancyCharacter.exists_character (sourceAction d)
    (targetAction d) (tensorBridge d) (tensor_intertwines d) α R T hR hT)

theorem discrepancy_law (g : C) (x : PiTensorProduct ℂ V) :
    tensorBridge d (R g x) = (discrepancy d α R T hR hT g : ℂ) • T g (tensorBridge d x) := by
  let := source_finiteDimensional d
  let := source_irreducible d
  exact Classical.choose_spec (DiscrepancyCharacter.exists_character (sourceAction d)
    (targetAction d) (tensorBridge d) (tensor_intertwines d) α R T hR hT) g x

/-- Arbitrary generating-set phase closure. No nonzero-trace restriction is needed
when the actual discrepancy values themselves are supplied and checked. -/
def equivOfPhase (S : Set C) (hgen : Subgroup.closure S = ⊤)
    (hp : ∀ g ∈ S, discrepancy d α R T hR hT g = 1) :
    Representation.Equiv
      (CyclicBridge.semidirectRepresentation α (sourceAction d) R hR)
      (CyclicBridge.semidirectRepresentation α (targetAction d) T hT) := by
  refine Representation.Equiv.mk (tensorBridge d) ?_
  have hc : ∀ g x, tensorBridge d (R g x) = T g (tensorBridge d x) := by
    intro g x
    simpa only [CharacterGenerators.trivial _ S hgen hp g, Units.val_one, one_smul]
      using discrepancy_law d α R T hR hT g x
  intro a
  apply LinearMap.ext
  intro x
  exact CyclicBridge.semidirect_intertwining α
    (CyclicBridge.semidirectRepresentation α (sourceAction d) R hR)
    (CyclicBridge.semidirectRepresentation α (targetAction d) T hT) (tensorBridge d)
    (by simpa only [CyclicBridge.semidirectRepresentation_inl] using tensor_intertwines d)
    (by simpa only [CyclicBridge.semidirectRepresentation_inr] using hc) a x

/-- The discrepancy is derived from honest lift covariance on the irreducible
central product. Its triviality is a test, not an assumed initial bridge. -/
theorem discrepancy_and_closure (S : Set C) (hgen : Subgroup.closure S = ⊤) :
    ∃ δ : C →* ℂˣ,
      (∀ g x, tensorBridge d (R g x) = (δ g : ℂ) • T g (tensorBridge d x)) ∧
      ((∀ g ∈ S, δ g = 1) →
        Nonempty (Representation.Equiv
          (CyclicBridge.semidirectRepresentation α (sourceAction d) R hR)
          (CyclicBridge.semidirectRepresentation α (targetAction d) T hT))) := by
  let := source_finiteDimensional d
  let := source_irreducible d
  obtain ⟨δ, hd, hc⟩ := CharacterGenerators.bridge_from_actions
    (sourceAction d) (targetAction d) (tensorBridge d) (tensor_intertwines d) α R T hR hT S hgen
  refine ⟨δ, hd, fun hp => ⟨Representation.Equiv.mk (tensorBridge d) ?_⟩⟩
  intro g
  apply LinearMap.ext
  intro x
  exact hc hp g x

/-- A useful directly observable phase contract: matched nonzero total traces
on generators close the bridge. Zero traces are deliberately not cancellable. -/
def equivOfTraces (S : Set C) (hgen : Subgroup.closure S = ⊤)
    (ht : ∀ g ∈ S, LinearMap.trace ℂ (PiTensorProduct ℂ V) (R g) =
      LinearMap.trace ℂ (PiTensorProduct ℂ W) (T g))
    (hn : ∀ g ∈ S, LinearMap.trace ℂ (PiTensorProduct ℂ W) (T g) ≠ 0) :
    Representation.Equiv
      (CyclicBridge.semidirectRepresentation α (sourceAction d) R hR)
      (CyclicBridge.semidirectRepresentation α (targetAction d) T hT) := by
  letI := source_finiteDimensional d
  letI := source_irreducible d
  refine Representation.Equiv.mk (tensorBridge d) ?_
  intro g
  apply LinearMap.ext
  intro x
  exact TraceDiscrepancy.bridge_from_traces
    (sourceAction d) (targetAction d) (tensorBridge d) (tensor_intertwines d)
    α R T hR hT S hgen ht hn g x

/-- The observable phase route does not change the underlying tensor map. -/
theorem equivOfTraces_map (S : Set C) (hgen : Subgroup.closure S = ⊤)
    (ht : ∀ g ∈ S, LinearMap.trace ℂ (PiTensorProduct ℂ V) (R g) =
      LinearMap.trace ℂ (PiTensorProduct ℂ W) (T g))
    (hn : ∀ g ∈ S, LinearMap.trace ℂ (PiTensorProduct ℂ W) (T g) ≠ 0) :
    (equivOfTraces d α R T hR hT S hgen ht hn).toLinearEquiv = tensorBridge d := rfl

end PaperXI.FiniteBreakAssembly
