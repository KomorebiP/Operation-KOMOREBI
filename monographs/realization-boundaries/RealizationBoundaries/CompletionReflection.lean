import RealizationBoundaries.DiagonalAutomorphisms
import RealizationBoundaries.CompletionConsequences

/-!
# The induced completion map and reflection for a supplied rank-one map

The maps below act on Mathlib's canonical completions. They are constructed from
the already checked comparison equivalences and the derived diagonal. Their
extension property and uniqueness are proved, identifying them as the induced
maps, independently of any alternate implementation of the completion functor.
-/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace RealizationBoundaries

/-- The actual continuous extension to the canonical profinite completions. -/
def completionHom (U V : Submodule ℚ TailSpace) (f : preimage U →+ preimage V) :
    CanonicalCompletion U →ₜ+ CanonicalCompletion V where
  toAddMonoidHom := (ambientToCompletion V).comp
    ((diagonal (homDiagonal U V f)).comp (completionToAmbient U))
  continuous_toFun := (ambientToCompletion_continuous V).comp
    ((diagonal_continuous _).comp (completionToAmbient_continuous U))

/-- This extension agrees with the supplied original homomorphism on every canonical point. -/
@[simp] theorem completionHom_eta (U V : Submodule ℚ TailSpace)
    (f : preimage U →+ preimage V) (x : preimage U) :
    completionHom U V f
      (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (preimage U)) x) =
      ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (preimage V)) (f x) := by
  change ambientToCompletion V
    (diagonal (homDiagonal U V f)
      (completionToAmbient U
        (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (preimage U)) x))) = _
  rw [completionToAmbient_eta, ← hom_eq_diagonal U V f x]
  exact ambientToCompletion_subtype V (f x)

/-- The coordinate formula on the entire completion, not just on its dense subgroup. -/
theorem completionHom_coordinates (U V : Submodule ℚ TailSpace)
    (f : preimage U →+ preimage V) (x : CanonicalCompletion U) :
    profiniteCompletionEquiv V (completionHom U V f x) =
      diagonal (homDiagonal U V f) (profiniteCompletionEquiv U x) :=
  completionToAmbient_ambientToCompletion V _

/-- Density makes this the unique continuous extension of the original map. -/
theorem completionHom_unique (U V : Submodule ℚ TailSpace)
    (f : preimage U →+ preimage V) (g : CanonicalCompletion U →ₜ+ CanonicalCompletion V)
    (hg : ∀ x : preimage U,
      g (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (preimage U)) x) =
        ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (preimage V)) (f x)) :
    g = completionHom U V f := by
  have he : (fun x => g x) = (fun x => completionHom U V f x) := by
    apply (ProfiniteAddGrp.ProfiniteCompletion.denseRange
      (AddGrpCat.of (preimage U))).equalizer g.continuous_toFun
        (completionHom U V f).continuous_toFun
    funext x
    exact (hg x).trans (completionHom_eta U V f x).symm
  exact ContinuousAddMonoidHom.ext (fun x => congrFun he x)

/-- The extension operation respects actual composition. -/
theorem completionHom_comp (U V W : Submodule ℚ TailSpace)
    (f : preimage U →+ preimage V) (g : preimage V →+ preimage W) :
    completionHom U W (g.comp f) = (completionHom V W g).comp (completionHom U V f) := by
  symm
  apply completionHom_unique U W (g.comp f)
  intro x
  change completionHom V W g (completionHom U V f
    (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (preimage U)) x)) = _
  rw [completionHom_eta, completionHom_eta]
  rfl

/-- Different original homomorphisms remain different after completion. -/
theorem completionHom_injective (U V : Submodule ℚ TailSpace) :
    Function.Injective (completionHom U V) := by
  intro f g h
  apply AddMonoidHom.ext
  intro x
  apply preimage_eta_injective V
  calc
    _ = completionHom U V f
        (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (preimage U)) x) :=
      (completionHom_eta U V f x).symm
    _ = completionHom U V g
        (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (preimage U)) x) := by rw [h]
    _ = _ := completionHom_eta U V g x

/-- A nonzero diagonal provides an actual topological additive equivalence of completions. -/
def completionEquivOfNonzeroDiagonal (U V : Submodule ℚ TailSpace)
    (f : preimage U →+ preimage V) (hn : ∀ p, homDiagonal U V f p ≠ 0) :
    CanonicalCompletion U ≃ₜ+ CanonicalCompletion V :=
  (profiniteCompletionEquiv U).trans
    ((diagonalAmbientEquiv (homDiagonal U V f) hn).trans (profiniteCompletionEquiv V).symm)

@[simp] theorem completionEquivOfNonzeroDiagonal_apply (U V : Submodule ℚ TailSpace)
    (f : preimage U →+ preimage V) (hn : ∀ p, homDiagonal U V f p ≠ 0)
    (x : CanonicalCompletion U) :
    completionEquivOfNonzeroDiagonal U V f hn x = completionHom U V f x := rfl

/-- Bijectivity of the induced map is exactly the nonzero-coordinate condition. -/
theorem completionHom_bijective_iff (U V : Submodule ℚ TailSpace)
    (f : preimage U →+ preimage V) :
    Function.Bijective (completionHom U V f) ↔ ∀ p, homDiagonal U V f p ≠ 0 := by
  constructor
  · intro hf
    apply (hom_injective_iff_diagonal_nonzero U V f).mp
    intro x y hxy
    apply preimage_eta_injective U
    apply hf.1
    rw [completionHom_eta, completionHom_eta, hxy]
  · intro hn
    exact (completionEquivOfNonzeroDiagonal U V f hn).bijective

/-- Isomorphism here includes continuity in both directions and equality with the induced map. -/
theorem completionHom_isomorphism_iff (U V : Submodule ℚ TailSpace)
    (f : preimage U →+ preimage V) :
    (∃ e : CanonicalCompletion U ≃ₜ+ CanonicalCompletion V,
      ∀ x, e x = completionHom U V f x) ↔ ∀ p, homDiagonal U V f p ≠ 0 := by
  constructor
  · rintro ⟨e, he⟩
    apply (completionHom_bijective_iff U V f).mp
    constructor
    · intro x y hxy
      exact e.injective ((he x).trans (hxy.trans (he y).symm))
    · intro y
      obtain ⟨x, hx⟩ := e.surjective y
      exact ⟨x, (he x).symm.trans hx⟩
  · intro hn
    exact ⟨completionEquivOfNonzeroDiagonal U V f hn, fun _ => rfl⟩

/-- Monograph Proposition 9.4: reflection for an already supplied rank-one homomorphism. -/
theorem selector_completion_reflection (S T : Set Prime) (hS : S.Infinite)
    (f : selectorGroup S →+ selectorGroup T) :
    Function.Bijective (completionHom (selectorLine S) (selectorLine T) f) ↔
      Function.Bijective f := by
  rw [completionHom_bijective_iff, selector_hom_bijective_iff S T hS]

/-- The reflection statement in terms of actual original and completed isomorphisms. -/
theorem paired_completion_reflects_isomorphisms (a b : ℕ → Bool)
    (f : pairedGroup a →+ pairedGroup b) :
    (∃ e : CanonicalCompletion (selectorLine (pairedSelector a)) ≃ₜ+
        CanonicalCompletion (selectorLine (pairedSelector b)),
      ∀ x, e x = completionHom (selectorLine (pairedSelector a))
        (selectorLine (pairedSelector b)) f x) ↔
    (∃ e : pairedGroup a ≃+ pairedGroup b, e.toAddMonoidHom = f) := by
  rw [completionHom_isomorphism_iff]
  constructor
  · intro hn
    exact ⟨selectorEquivOfNonzeroDiagonal _ _ (pairedSelector_infinite a) f hn, rfl⟩
  · rintro ⟨e, rfl⟩
    exact (hom_injective_iff_diagonal_nonzero _ _ _).mp e.injective

end RealizationBoundaries
