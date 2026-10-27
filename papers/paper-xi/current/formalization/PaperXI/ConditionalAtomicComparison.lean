import PaperXI.FiniteBreakAssembly
import PaperXI.GluedPacketSections
import PaperXI.LocalFactorIdentification

/-! The last comparison pipeline. Actual finite tensor intertwiners and global
parallel-section equivalences are constructed. Atom realization and normalized
pair-factor characterization remain explicit external interfaces. They are not
consequences of finite phases or of zero holonomy. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ConditionalAtomicComparison
open Quiver GraphTransport GraphGauge GluedPacketSections LocalFactorIdentification

variable {X K G V W : Type*} [Quiver X] [Field K] [Monoid G]
variable [AddCommGroup V] [Module K V] [AddCommGroup W] [Module K W]

/-- A finite representation diagram retains all fibers and all transports.
Its space of parallel sections may be zero and is not identified with an atom. -/
structure Diagram (X K G V : Type*) [Quiver X] [Field K] [Monoid G]
    [AddCommGroup V] [Module K V] where
  action : X → Representation K G V
  edge : ∀ {u v : X}, (u ⟶ v) → (V ≃ₗ[K] V)
  covariance : RepresentationGraph.EdgeEquivariant edge action

/-- Local actions and honest transport data. There is no root comparison map,
global gauge, global section equivalence, or atomic identification in this record. -/
structure Atlas (leftRoot : Representation K G V) (rightRoot : Representation K G W) where
  root : X
  connected : GraphTree.Connected (α := X)
  left : X → Representation K G V
  right : X → Representation K G W
  left_root : left root = leftRoot
  right_root : right root = rightRoot
  sourceEdge : ∀ {u v : X}, (u ⟶ v) → (V ≃ₗ[K] V)
  targetEdge : ∀ {u v : X}, (u ⟶ v) → (W ≃ₗ[K] W)
  sourceCovariance : RepresentationGraph.EdgeEquivariant sourceEdge left
  targetCovariance : RepresentationGraph.EdgeEquivariant targetEdge right

variable {leftRoot : Representation K G V} {rightRoot : Representation K G W}
variable (a : Atlas (X := X) leftRoot rightRoot)

def targetDiagram : Diagram X K G W :=
  ⟨a.right, a.targetEdge, a.targetCovariance⟩

def sourceDiagram : Diagram X K G V :=
  ⟨a.left, a.sourceEdge, a.sourceCovariance⟩

/-- Root action equality only transports the already constructed finite map. -/
def atRoot (U : Representation.Equiv leftRoot rightRoot) :
    Representation.Equiv (a.left a.root) (a.right a.root) := by
  refine Representation.Equiv.mk U.toLinearEquiv ?_
  intro g
  rw [a.left_root, a.right_root]
  exact U.toIntertwiningMap.isIntertwining' g

@[simp] theorem atRoot_linear (U : Representation.Equiv leftRoot rightRoot) :
    (atRoot a U).toLinearEquiv = U.toLinearEquiv := rfl

/-- The matrix obstruction is tested on actual fundamental cycles of a derived tree. -/
def Holonomy (U : V ≃ₗ[K] W) : Prop :=
  ∀ e : GraphTree.Chord (GraphTree.ofConnected a.root a.connected),
    CycleCompatible a.sourceEdge a.targetEdge U
      (GraphTree.rootPath (GraphTree.ofConnected a.root a.connected)) e.val

def leftSections := sectionRepresentation a.sourceEdge a.left a.sourceCovariance

def rightSections := sectionRepresentation a.targetEdge a.right a.targetCovariance

/-- A real equivalence of global section representations, not an assumed record field. -/
def glue (U : Representation.Equiv leftRoot rightRoot) (h : Holonomy a U.toLinearEquiv) :
    Representation.Equiv (leftSections a) (rightSections a) :=
  fromChords a.sourceEdge a.targetEdge a.left a.right a.connected
    a.sourceCovariance a.targetCovariance (atRoot a U) h

theorem glue_apply (U : Representation.Equiv leftRoot rightRoot) (h : Holonomy a U.toLinearEquiv)
    (s : sections a.sourceEdge) (v : X) :
    (glue a U h s).val v =
      path a.targetEdge (GraphTree.rootPath (GraphTree.ofConnected a.root a.connected) v)
        (U ((path a.sourceEdge (GraphTree.rootPath (GraphTree.ofConnected a.root a.connected) v)).symm
          (s.val v))) := rfl

/-- Matrix holonomy is necessary as well as sufficient for the based gauge.
A scalar determinant, trace, or projective cycle test is not substituted. -/
theorem holonomy_iff_gauge (U : Representation.Equiv leftRoot rightRoot) :
    Holonomy a U.toLinearEquiv ↔
      ∃ F : X → V ≃ₗ[K] W,
        F a.root = U.toLinearEquiv ∧ EdgeCompatible a.sourceEdge a.targetEdge F ∧
          RepresentationGraph.Intertwines a.left a.right F := by
  exact (RepresentationGraph.connected_iff_chords a.sourceEdge a.targetEdge
    a.left a.right a.sourceCovariance a.targetCovariance (atRoot a U).toLinearEquiv
    (fun g x => DFunLike.congr_fun ((atRoot a U).toIntertwiningMap.isIntertwining' g) x) a.connected).symm

section Source
variable {I Z C : Type*} [Fintype I] [CommGroup Z] [Group C]
variable {H A H' A' Vb Wb : I → Type*}
variable [∀ i, Group (H i)] [∀ i, CommGroup (A i)] [∀ i, Fintype (A i)]
variable [∀ i, Group (H' i)] [∀ i, CommGroup (A' i)]
variable [∀ i, AddCommGroup (Vb i)] [∀ i, Module ℂ (Vb i)]
variable [∀ i, AddCommGroup (Wb i)] [∀ i, Module ℂ (Wb i)]

variable (d : FiniteBreakAssembly.Data (I := I) (Z := Z) (H := H) (A := A)
  (H' := H') (A' := A') (V := Vb) (W := Wb))
variable (α : C →* MulAut (CentralProduct.Group d.source))
variable (R : Representation ℂ C (PiTensorProduct ℂ Vb))
variable (T : Representation ℂ C (PiTensorProduct ℂ Wb))
variable (hR : ∀ g h x, R g (FiniteBreakAssembly.sourceAction d h x) =
  FiniteBreakAssembly.sourceAction d (α g h) (R g x))
variable (hT : ∀ g h x, T g (FiniteBreakAssembly.targetAction d h x) =
  FiniteBreakAssembly.targetAction d (α g h) (T g x))
variable (S : Set C) (hgen : Subgroup.closure S = ⊤)
variable (hp : ∀ g ∈ S, FiniteBreakAssembly.discrepancy d α R T hR hT g = 1)
variable (a0 : Atlas (X := X)
  (CyclicBridge.semidirectRepresentation α (FiniteBreakAssembly.sourceAction d) R hR)
  (CyclicBridge.semidirectRepresentation α (FiniteBreakAssembly.targetAction d) T hT))
variable (hhol : Holonomy a0 (FiniteBreakAssembly.tensorBridge d))

/-- Source finite endpoint: the root tensor map and the global section bridge
are both constructed from the phase, lift and graph data. -/
def finiteComparison : Representation.Equiv (leftSections a0) (rightSections a0) :=
  glue a0 (FiniteBreakAssembly.equivOfPhase d α R T hR hT S hgen hp) hhol

include hgen hp hhol in
/-- Theorem 16.2 at explicit arithmetic interfaces. The permitted finite data
are represented by a subtype; no realization of arbitrary finite data is asserted.
The output includes the concrete finite equivalence AND equality of realized
atom classes. There is no assumed finite bridge or final atom equality. -/
theorem source {Atom Test Value : Type*} {atomIso : Setoid Atom}
    (sys : FactorSystem atomIso Test Value)
    (allowed : Set (Diagram X ℂ (CentralProduct.Group d.source ⋊[α] C)
      (PiTensorProduct ℂ Wb)))
    (ha : targetDiagram a0 ∈ allowed)
    (realization : Realization sys allowed)
    (reference : Atom) (href : sys.admissible reference)
    (expected : Test → Value)
    (hfactors : ∀ b, realization.realizes ⟨targetDiagram a0, ha⟩ b →
      sys.profile b = expected)
    (hreference : sys.profile reference = expected) :
    (∃ F : X → PiTensorProduct ℂ Vb ≃ₗ[ℂ] PiTensorProduct ℂ Wb,
      F a0.root = FiniteBreakAssembly.tensorBridge d ∧
      EdgeCompatible a0.sourceEdge a0.targetEdge F ∧
      RepresentationGraph.Intertwines a0.left a0.right F) ∧
    Nonempty (Representation.Equiv (leftSections a0) (rightSections a0)) ∧
      candidate sys realization ⟨targetDiagram a0, ha⟩ = Quotient.mk atomIso reference := by
  refine ⟨?_, ⟨finiteComparison d α R T hR hT S hgen hp a0 hhol⟩,
    candidate_eq_reference sys realization ⟨targetDiagram a0, ha⟩ reference
      href expected hfactors hreference⟩
  exact (holonomy_iff_gauge a0
    (FiniteBreakAssembly.equivOfPhase d α R T hR hT S hgen hp)).mp hhol

end Source
end PaperXI.ConditionalAtomicComparison
