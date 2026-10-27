import AVOC.Verification

namespace Komorebi.AVOC

universe u v w

/-- Exact recovery of an intended target by a downstream computation that sees
only the formalized representation. -/
def RecoversThrough
    {I : Type u} {F : Type v} {Y : Type w}
    (formalize : I → F) (target : I → Y) (downstream : F → Y) : Prop :=
  ∀ i, downstream (formalize i) = target i

/-- Exact semantic recovery through a formalization is exactly AVOC task
sufficiency for that formalization. -/
theorem taskSufficient_iff_exists_downstream_recovery
    {I : Type u} {F : Type v} {Y : Type w}
    (formalize : I → F) (target : I → Y) :
    TaskSufficient formalize target ↔
      ∃ downstream : F → Y, RecoversThrough formalize target downstream := by
  rfl

/-- Structural semantic bottleneck: if formalization identifies two intended
states that the intended task distinguishes, then no downstream verifier,
checker, decoder, or decision rule that sees only the formal object can recover
the intended target on every state. -/
theorem specification_collision_obstructs_every_downstream
    {I : Type u} {F : Type v} {Y : Type w}
    {formalize : I → F} {target : I → Y} {x y : I}
    (hformal : formalize x = formalize y)
    (htarget : target x ≠ target y) :
    ∀ downstream : F → Y, ¬ RecoversThrough formalize target downstream := by
  intro downstream hrecover
  apply htarget
  calc
    target x = downstream (formalize x) := (hrecover x).symm
    _ = downstream (formalize y) := congrArg downstream hformal
    _ = target y := hrecover y

/-- A task-insufficient formalization cannot be repaired by any downstream
computation that receives only its output. -/
theorem insufficient_specification_has_no_exact_downstream
    {I : Type u} {F : Type v} {Y : Type w}
    {formalize : I → F} {target : I → Y}
    (hinsufficient : ¬ TaskSufficient formalize target) :
    ¬ ∃ downstream : F → Y, RecoversThrough formalize target downstream := by
  intro h
  exact hinsufficient ((taskSufficient_iff_exists_downstream_recovery formalize target).2 h)

/-- Semantic fidelity for proposition-valued intended claims.  This is a
property of the formalization-plus-formal-semantics layer, not of the verifier
that later checks formal objects. -/
def SemanticFidelity
    {I : Type u} {F : Type v}
    (formalize : I → F) (formalTruth : F → Prop) (intendedTruth : I → Prop) : Prop :=
  ∀ i, formalTruth (formalize i) ↔ intendedTruth i

/-- A sound verifier plus a semantically faithful formalization implies intended
truth for every accepted formalized item. -/
theorem sound_gate_plus_semantic_fidelity
    {I : Type u} {F : Type v}
    {formalize : I → F} {formalTruth : F → Prop} {intendedTruth : I → Prop}
    {gate : F → Prop}
    (hsound : SoundGate gate formalTruth)
    (hfidelity : SemanticFidelity formalize formalTruth intendedTruth)
    {i : I} (hadmit : gate (formalize i)) :
    intendedTruth i := by
  exact (hfidelity i).1 (hsound (formalize i) hadmit)

/-- If a formalization merges one intended-true and one intended-false state,
then no proposition on the formal objects can be semantically faithful. -/
theorem semantic_collision_obstructs_fidelity
    {I : Type u} {F : Type v}
    {formalize : I → F} {intendedTruth : I → Prop} {x y : I}
    (hformal : formalize x = formalize y)
    (hx : intendedTruth x) (hy : ¬ intendedTruth y) :
    ∀ formalTruth : F → Prop,
      ¬ SemanticFidelity formalize formalTruth intendedTruth := by
  intro formalTruth hfidelity
  have hfx : formalTruth (formalize x) := (hfidelity x).2 hx
  have hfy : formalTruth (formalize y) := by
    simpa [hformal] using hfx
  exact hy ((hfidelity y).1 hfy)

/-- Perfect formal verification cannot by itself certify intended semantics when
semantic fidelity is unavailable: the missing ingredient is a specification
property, not a stronger downstream checker. -/
theorem no_sound_gate_can_supply_missing_semantic_fidelity
    {I : Type u} {F : Type v}
    {formalize : I → F} {intendedTruth : I → Prop} {x y : I}
    (hformal : formalize x = formalize y)
    (hx : intendedTruth x) (hy : ¬ intendedTruth y) :
    ¬ ∃ formalTruth : F → Prop,
        SemanticFidelity formalize formalTruth intendedTruth := by
  rintro ⟨formalTruth, hfidelity⟩
  exact semantic_collision_obstructs_fidelity hformal hx hy formalTruth hfidelity

end Komorebi.AVOC

namespace Komorebi.AVOC

universe u v w z

/-- An ensemble of downstream verifiers followed by an arbitrary aggregation
rule is still only a function of the formalized object.  Therefore a semantic
collision cannot be repaired by adding more downstream verifiers. -/
theorem specification_collision_obstructs_verifier_ensemble
    {I : Type u} {F : Type v} {V : Type w} {Y : Type z}
    {formalize : I → F} {target : I → Y} {x y : I}
    (hformal : formalize x = formalize y)
    (htarget : target x ≠ target y)
    (verifier : V → F → Y)
    (aggregate : (V → Y) → Y) :
    ¬ ∀ i, aggregate (fun v => verifier v (formalize i)) = target i := by
  let downstream : F → Y := fun f => aggregate (fun v => verifier v f)
  exact specification_collision_obstructs_every_downstream
    hformal htarget downstream

/-- Exact intended semantics downstream of a formalization implies that the
formalization itself is task-sufficient.  Checker multiplicity cannot evade
this necessary condition. -/
theorem exact_ensemble_recovery_implies_specification_sufficient
    {I : Type u} {F : Type v} {V : Type w} {Y : Type z}
    {formalize : I → F} {target : I → Y}
    (verifier : V → F → Y)
    (aggregate : (V → Y) → Y)
    (hrecover : ∀ i, aggregate (fun v => verifier v (formalize i)) = target i) :
    TaskSufficient formalize target := by
  refine ⟨fun f => aggregate (fun v => verifier v f), ?_⟩
  exact hrecover

end Komorebi.AVOC
