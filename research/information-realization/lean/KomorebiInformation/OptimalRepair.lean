module
public import KomorebiInformation.LinearAccess
public import Mathlib.FieldTheory.Finiteness
@[expose] public section

namespace KomorebiInformation.Linear
variable {K V O Y E : Type*}
variable [DivisionRing K]
variable [AddCommGroup V] [Module K V]
variable [AddCommGroup O] [Module K O]
variable [AddCommGroup Y] [Module K Y]
variable [AddCommGroup E] [Module K E]

/-- A feasible helper can encode directly into the missing-task subspace.
The construction is linear, although the lower bound below covers nonlinear codes. -/
theorem optimal_obstruction_space_repair
    (R : V →ₗ[K] O) (F : V →ₗ[K] Y) (U : V →ₗ[K] E)
    (hfeas : R.ker ⊓ U.ker ≤ F.ker) :
    ∃ H : E →ₗ[K] ObstructionSpace R F,
      ∃ G : O × ObstructionSpace R F →ₗ[K] Y,
        G.comp (R.prod (H.comp U)) = F := by
  let D := ObstructionSpace R F
  let FK := F.domRestrict R.ker
  let Fr : R.ker →ₗ[K] D := FK.rangeRestrict
  let UK := U.domRestrict R.ker
  have hk : UK.ker ≤ Fr.ker := by
    intro v hv
    apply Subtype.ext
    change F v = 0
    exact hfeas ⟨v.property, hv⟩
  obtain ⟨H, hH⟩ := (exists_linear_decoder_iff_kernel UK Fr).mpr hk
  let L : V →ₗ[K] Y := F - D.subtype.comp (H.comp U)
  have hl : R.ker ≤ L.ker := by
    intro x hx
    have hval := congrArg Subtype.val (LinearMap.congr_fun hH ⟨x,hx⟩)
    change ((H (U x)) : Y) = F x at hval
    change F x - ((H (U x)) : Y) = 0
    rw [hval, sub_self]
  obtain ⟨G0, hG0⟩ := (exists_linear_decoder_iff_kernel R L).mpr hl
  refine ⟨H, G0.coprod D.subtype, ?_⟩
  ext x
  change G0 (R x) + ((H (U x)) : Y) = F x
  have heq := LinearMap.congr_fun hG0 x
  change G0 (R x) = F x - ((H (U x)) : Y) at heq
  rw [heq, sub_add_cancel]

/-- In one observation fiber every obstruction-space element is a different
answer, so it injects into the alphabet of every correct code. -/
theorem obstruction_card_le_any_repair
    (R : V →ₗ[K] O) (F : V →ₗ[K] Y) (U : V →ₗ[K] E)
    {Message : Type*} [Fintype Message] [Fintype (ObstructionSpace R F)]
    {h : E → Message} {g : O × Message → Y}
    (hrep : Repair R F U h g) :
    Fintype.card (ObstructionSpace R F) ≤ Fintype.card Message := by
  classical
  let s : ObstructionSpace R F → V := fun y =>
    (Classical.choose y.property : R.ker)
  have hr : ∀ y, R (s y) = 0 := fun y => (Classical.choose y.property).property
  have hs : ∀ y, F (s y) = (y : Y) := fun y => Classical.choose_spec y.property
  have hf : Function.Injective (F ∘ s) := by
    intro a b hab
    apply Subtype.ext
    change F (s a) = F (s b) at hab
    simpa only [hs] using hab
  exact repair_alphabet_lower_bound hrep s 0 hr hf

/-- The familiar q^d alphabet is an exact cardinality of the obstruction space. -/
theorem obstruction_space_card
    [Fintype K] (R : V →ₗ[K] O) (F : V →ₗ[K] Y)
    [Fintype (ObstructionSpace R F)] :
    Fintype.card (ObstructionSpace R F) =
      Fintype.card K ^ Module.finrank K (ObstructionSpace R F) :=
  Module.card_eq_pow_finrank

/-- q^d is a lower bound for arbitrary nonlinear helper codes. -/
theorem power_finrank_le_any_repair
    [Fintype K] (R : V →ₗ[K] O) (F : V →ₗ[K] Y) (U : V →ₗ[K] E)
    {Message : Type*} [Fintype Message] [Fintype (ObstructionSpace R F)]
    {h : E → Message} {g : O × Message → Y}
    (hrep : Repair R F U h g) :
    Fintype.card K ^ Module.finrank K (ObstructionSpace R F) ≤
      Fintype.card Message := by
  rw [← obstruction_space_card R F]
  exact obstruction_card_le_any_repair R F U hrep
end KomorebiInformation.Linear
