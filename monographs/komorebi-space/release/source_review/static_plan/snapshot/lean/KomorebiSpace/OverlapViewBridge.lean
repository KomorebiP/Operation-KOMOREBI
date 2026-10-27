import KomorebiSpace.OverlapPathRepair
import KomorebiSpace.SectionObstruction
import KomorebiSpace.RepairProjection

set_option autoImplicit false

/-!
# Quantitative overlap repair is an actual ambient realization

The complete comparison category has one arrow between each ordered pair of
views. A connected measured graph supplies a generating set of comparisons.
The coefficient system is explicitly trivialized by the supplied isometries.
This is a model-specific quantitative theorem, not a norm on arbitrary stacks.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace OverlapTransport
open CategoryTheory
variable {V : Type u} {H : Type v}
variable [NormedAddCommGroup H] [NormedSpace ℝ H]

structure PairView (V : Type u) where
  point : V

instance pairViewCategory : Category (PairView V) where
  Hom _ _ := PUnit
  id _ := PUnit.unit
  comp _ _ := PUnit.unit
  id_comp := by intros; apply Subsingleton.elim
  comp_id := by intros; apply Subsingleton.elim
  assoc := by intros; rfl

variable (e : Frames (V := V) (H := H))

def viewSystem : AdditiveViewSystem (PairView V) (fun _ => H) where
  pull := fun {i j} _ => (transport e i.point j.point).toLinearEquiv.toLinearMap.toAddHom
  pull_id := by intro i x; exact transport_self e i.point x
  pull_comp := by intro i j k f g x; exact (transport_comp e i.point j.point k.point x).symm

def rawViews (x : V → H) : PairView V → H := fun i => x i.point

def patch (U : Set V) : Set (PairView V) := {i | i.point ∈ U}

/-- Agreement with the old additive view differential, including its sign. -/
@[simp] theorem view_differential (x : V → H) (i j : V) :
    (viewSystem e).differential (rawViews x) ⟨i⟩ ⟨j⟩ PUnit.unit = defect e x i j := rfl

def ambientFromSeed (z : H) : (viewSystem e).views.Ambient :=
  ⟨fun i => e i.point z, by
    intro i j f
    change transport e i.point j.point (e j.point z) = e i.point z
    simp [transport_apply]⟩

@[simp] theorem ambientFromSeed_coordinate (z : H) (i : V) :
    (ambientFromSeed e z).val ⟨i⟩ = e i z := rfl

/-- The intended global object is an ordinary vector in the supplied reference space. -/
def ambientEquiv (o : V) : (viewSystem e).views.Ambient ≃ H where
  toFun x := (e o).symm (x.val ⟨o⟩)
  invFun := ambientFromSeed e
  left_inv := by
    intro x
    apply ViewSystem.Ambient.ext
    intro i
    exact x.property i ⟨o⟩ PUnit.unit
  right_inv := by intro z; simp

def repairedAmbient (o : V) (x : V → H) : (viewSystem e).views.Ambient :=
  ambientFromSeed e (normalized e x o)

@[simp] theorem repairedAmbient_coordinate (o : V) (x : V → H) (i : V) :
    (repairedAmbient e o x).val ⟨i⟩ = repair e o x i := rfl

/-- Raw prescribed values must agree when expressed in the common frame. -/
def boundaryCompatible (U : Set V) (o : V) (x : V → H) : Prop :=
  ∀ i ∈ U, normalized e x i = normalized e x o

theorem repair_preserves_boundary (U : Set V) (o : V) (x : V → H)
    (hc : boundaryCompatible e U o x) : ∀ i ∈ U, repair e o x i = x i := by
  intro i hi
  apply (e i).symm.injective
  change normalized e (repair e o x) i = normalized e x i
  rw [normalized_repair]
  exact (hc i hi).symm

/-- The existing quotient detects precisely incompatible prescribed overlap values. -/
theorem obstruction_zero_iff_boundary (U : Set V) (o : V) (ho : o ∈ U) (x : V → H) :
    ((viewSystem e).problem (patch U)).obstruction (rawViews x) = 0 ↔
      boundaryCompatible e U o x := by
  rw [(viewSystem e).obstruction_zero_iff_section]
  constructor
  · rintro ⟨s,hs⟩ i hi
    have h0 := hs ⟨⟨o⟩,ho⟩
    have h1 := hs ⟨⟨i⟩,hi⟩
    have he := s.property ⟨i⟩ ⟨o⟩ PUnit.unit
    change transport e i o (s.val ⟨o⟩) = s.val ⟨i⟩ at he
    change s.val ⟨o⟩ = x o at h0
    change s.val ⟨i⟩ = x i at h1
    rw [h0,h1] at he
    have hn := congrArg (e i).symm he
    simpa [transport_apply, normalized] using hn.symm
  · intro hc
    refine ⟨repairedAmbient e o x, ?_⟩
    intro i
    exact repair_preserves_boundary e U o x hc i.val.point i.property

variable [Fintype V]
variable {graph : SimpleGraph V} {o : V} (routing : Routing graph o)

include routing in
/-- Measured edge exactness is exactly ambient coherence on the complete comparison category. -/
theorem edge_exact_iff_view_exact (x : V → H) :
    edgeDifferential e graph x = 0 ↔
      (viewSystem e).differential (rawViews x) = 0 := by
  rw [(viewSystem e).differential_zero_iff]
  constructor
  · intro hx i j f
    have he := (routing.exact_iff_repair e x).mp hx
    have hz := repair_defect e o x i.point j.point
    rw [he] at hz
    exact sub_eq_zero.mp hz
  · intro hx
    funext a
    exact sub_eq_zero.mpr (hx ⟨a.val.1⟩ ⟨a.val.2⟩ PUnit.unit)

/-- A concrete global section, protected values, and a derived analytic bound together. -/
theorem quantitative_realization (U : Set V) (ho : o ∈ U) (x : V → H)
    (hz : ((viewSystem e).problem (patch U)).obstruction (rawViews x) = 0) :
    ∃ s : (viewSystem e).views.Ambient,
      (∀ i ∈ U, s.val ⟨i⟩ = x i) ∧
      ‖x - (fun i => (show H from s.val ⟨i⟩))‖ ≤ (routing.radius : ℝ) * ‖edgeDifferential e graph x‖ := by
  have hc := (obstruction_zero_iff_boundary e U o ho x).mp hz
  refine ⟨repairedAmbient e o x, ?_, ?_⟩
  · exact repair_preserves_boundary e U o x hc
  · exact routing.repair_error e x

/-- Anchor evaluation as an actual continuous linear protected observable. -/
def anchorObservation (o : V) : (V → H) →L[ℝ] H :=
  (LinearMap.proj o).mkContinuous 1 (by intro x; simpa using norm_le_pi_norm x o)

@[simp] theorem anchorObservation_apply (o : V) (x : V → H) :
    anchorObservation o x = x o := rfl

/-- Instantiate the existing correction scheme, with all its obligations derived. -/
def Routing.scheme : RepairDynamics.Scheme (edgeDifferential e graph) (anchorObservation o) where
  correction := routing.correction e
  rate := 0
  rate_nonneg := le_rfl
  rate_lt_one := zero_lt_one
  preserve := routing.correction_anchor e
  contract := by
    intro x
    rw [routing.differential_correction_differential e x, sub_self, norm_zero, zero_mul]

@[simp] theorem scheme_step (x : V → H) :
    RepairDynamics.step (edgeDifferential e graph) (routing.scheme e).correction x =
      repair e o x := by
  change x - routing.correction e (edgeDifferential e graph x) = _
  rw [routing.correction_differential e]
  abel

variable [CompleteSpace H]

/-- The old iterative projector and the explicit overlap repair are the same operator. -/
theorem scheme_projection (x : V → H) :
    (routing.scheme e).projection x = repair e o x := by
  have hx := (routing.scheme e).limit_exact x
  have hp := (routing.scheme e).limit_semantics x
  change (routing.scheme e).limit x = _
  have he := (routing.exact_iff_repair e _).mp hx
  calc
    (routing.scheme e).limit x = repair e o ((routing.scheme e).limit x) := he.symm
    _ = repair e o x := by
      funext i
      change transport e i o ((routing.scheme e).limit x o) = transport e i o (x o)
      exact congrArg (transport e i o) hp

end OverlapTransport
end KomorebiSpace
end
