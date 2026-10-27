import KomorebiVerification.ProjectorCore

/-!
# Concrete fibre projectors and exact refinement

This file upgrades the pointwise masks from `ProjectorCore` to genuine linear
projectors.  It also proves the refinement law from independently defined
coarse and fine masks: a coarse fibre is the sum of the fine fibres mapping to
it.  In particular, the conclusion is not stored as a structure field.
-/

set_option autoImplicit false

namespace Komorebi.Packet

universe u v w x

variable {R : Type u} {M : Type v} {α : Type w} {β : Type x}

/-- The pointwise fibre mask, regarded as an `R`-linear endomorphism. -/
def fibreLinearProj
    [Semiring R] [AddCommMonoid M] [Module R M] [DecidableEq β]
    (address : α → β) (b : β) : Module.End R (α → M) where
  toFun := fibreProj address b
  map_add' x y := by
    funext a
    by_cases h : address a = b <;> simp [fibreProj, h]
  map_smul' r x := by
    funext a
    by_cases h : address a = b <;> simp [fibreProj, h]

@[simp] theorem fibreLinearProj_apply
    [Semiring R] [AddCommMonoid M] [Module R M] [DecidableEq β]
    (address : α → β) (b : β) (x : α → M) :
    fibreLinearProj (R := R) address b x = fibreProj address b x :=
  rfl

/-- Every finite address map induces a complete orthogonal projector family. -/
def fibreLinearProjectorFamily
    [Semiring R] [AddCommMonoid M] [Module R M]
    [DecidableEq β] [Fintype β]
    (address : α → β) :
    Komorebi.Foundation.LinearProjectorFamily R (α → M) β where
  proj := fibreLinearProj (R := R) address
  idempotent b x := fibreProj_idempotent address b x
  orthogonal hbc x := fibreProj_orthogonal address hbc x
  complete x := fibreProj_reconstruction address x

/--
Exact nested refinement for fibre masks.  The coarse mask on `merge ∘ fine`
equals the sum of all independently defined fine masks in the selected fibre.
-/
theorem fibreProj_refinement
    {γ : Type*}
    [DecidableEq β] [DecidableEq γ] [Fintype γ] [AddCommMonoid M]
    (fine : α → γ) (merge : γ → β) (b : β) (x : α → M) :
    fibreProj (fun a => merge (fine a)) b x =
      ∑ c, if merge c = b then fibreProj fine c x else 0 := by
  funext a
  classical
  simp only [fibreProj]
  rw [Finset.sum_apply]
  simp only [ite_apply, Pi.zero_apply]
  simp only [fibreProj]
  symm
  have hzero : ∀ c : γ, c ≠ fine a →
      (if merge c = b then if fine a = c then x a else 0 else 0) = 0 := by
    intro c hca
    simp [Ne.symm hca]
  simpa using
    (Fintype.sum_eq_single
      (f := fun c : γ =>
        if merge c = b then if fine a = c then x a else 0 else 0)
      (fine a) hzero)

/-- The same refinement law, expressed for the corresponding linear maps. -/
theorem fibreLinearProj_refinement
    {γ : Type*}
    [Semiring R] [AddCommMonoid M] [Module R M]
    [DecidableEq β] [DecidableEq γ] [Fintype γ]
    (fine : α → γ) (merge : γ → β) (b : β) :
    fibreLinearProj (R := R) (M := M) (fun a => merge (fine a)) b =
      ∑ c, if merge c = b then fibreLinearProj (R := R) (M := M) fine c else 0 := by
  apply LinearMap.ext
  intro (x : α → M)
  apply funext
  intro a
  change fibreProj (fun a => merge (fine a)) b x a =
    ((∑ c ∈ Finset.univ,
      if merge c = b then fibreLinearProj (R := R) (M := M) fine c else 0) x) a
  rw [LinearMap.sum_apply, Finset.sum_apply]
  calc
    fibreProj (fun a => merge (fine a)) b x a =
        ∑ c, if merge c = b then fibreProj fine c x a else 0 := by
      simpa only [Fintype.sum_apply, ite_apply, Pi.zero_apply] using
        congrFun (fibreProj_refinement fine merge b x) a
    _ = ∑ c, (if merge c = b then
          fibreLinearProj (R := R) (M := M) fine c else 0) x a := by
      apply Fintype.sum_congr
      intro c
      by_cases hc : merge c = b <;> simp [hc, fibreLinearProj_apply]

end Komorebi.Packet
