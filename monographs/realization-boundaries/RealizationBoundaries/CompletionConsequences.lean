import RealizationBoundaries.ProfiniteCompletion
import RealizationBoundaries.Countability
import RealizationBoundaries.PureCorrespondence

/-! # Canonical consequences of the checked completion theorem -/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace RealizationBoundaries

@[simp] theorem preimage_bot_eq_finiteSupport :
    preimage (⊥ : Submodule ℚ TailSpace) = finiteSupport := by
  ext x
  change quotientMap x ∈ (⊥ : Submodule ℚ TailSpace) ↔ x ∈ finiteSupport
  rw [Submodule.mem_bot, quotientMap_eq_zero_iff]

/-- Transport is along literal subgroup equality, retaining its group structure. -/
def completionEquivOfEq (W : Submodule ℚ TailSpace) (H : AddSubgroup Ambient)
    (h : preimage W = H) :
    ProfiniteAddGrp.ProfiniteCompletion.completion (AddGrpCat.of H) ≃ₜ+ Ambient :=
  h ▸ profiniteCompletionEquiv W

@[simp] theorem completionEquivOfEq_eta (W : Submodule ℚ TailSpace)
    (H : AddSubgroup Ambient) (h : preimage W = H) (x : H) :
    completionEquivOfEq W H h
      (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of H) x) = x.val := by
  subst H
  exact profiniteCompletionEquiv_eta W x

/-- Monograph Proposition 2.5, for the original finite-support subgroup. -/
def finiteSupportCompletionEquiv :
    ProfiniteAddGrp.ProfiniteCompletion.completion (AddGrpCat.of finiteSupport) ≃ₜ+ Ambient :=
  completionEquivOfEq ⊥ finiteSupport preimage_bot_eq_finiteSupport

@[simp] theorem finiteSupportCompletionEquiv_eta (x : finiteSupport) :
    finiteSupportCompletionEquiv
      (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of finiteSupport) x) = x.val :=
  completionEquivOfEq_eta _ _ _ x

/-- All the completions are isomorphic by the canonical coordinate comparisons. -/
def commonCompletionEquiv (V W : Submodule ℚ TailSpace) :
    CanonicalCompletion V ≃ₜ+ CanonicalCompletion W :=
  (profiniteCompletionEquiv V).trans (profiniteCompletionEquiv W).symm

/-- When the rational subspaces are nested, the comparison is exactly the extension
of the original subgroup inclusion, as witnessed on every canonical point. -/
theorem commonCompletionEquiv_inclusion (V W : Submodule ℚ TailSpace) (h : V ≤ W)
    (x : preimage V) : commonCompletionEquiv V W
      (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (preimage V)) x) =
      ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (preimage W))
        ⟨x.val, h x.property⟩ := by
  exact ambientToCompletion_subtype W ⟨x.val, h x.property⟩

/-- The abstract group embeds faithfully in its actual profinite completion. -/
theorem preimage_eta_injective (W : Submodule ℚ TailSpace) :
    Function.Injective (ProfiniteAddGrp.ProfiniteCompletion.etaFn
      (AddGrpCat.of (preimage W))) := by
  intro x y h
  apply Subtype.ext
  exact congrArg (profiniteCompletionEquiv W) h

/-- The official residual-finiteness predicate, rather than a replacement definition. -/
theorem preimage_residuallyFinite (W : Submodule ℚ TailSpace) :
    AddGroup.ResiduallyFinite (preimage W) :=
  (ProfiniteAddGrp.ProfiniteCompletion.etaFn_injective_iff_residuallyFinite
    (AddGrpCat.of (preimage W))).mp (preimage_eta_injective W)

def pairedCompletionEquiv (a : ℕ → Bool) :
    ProfiniteAddGrp.ProfiniteCompletion.completion (AddGrpCat.of (pairedGroup a)) ≃ₜ+ Ambient :=
  profiniteCompletionEquiv (selectorLine (pairedSelector a))

/-- D is proper inside every paired-prime group, not just dense in it. -/
theorem paired_has_nonfiniteSupport (a : ℕ → Bool) :
    ∃ x : pairedGroup a, x.val ∉ finiteSupport := by
  refine ⟨markedElement (pairedSelector a), ?_⟩
  intro h
  exact indicator_tail_ne_zero (pairedSelector_infinite a)
    ((quotientMap_eq_zero_iff _).mpr h)

theorem finiteSupport_ne_top : finiteSupport ≠ ⊤ := by
  intro h
  obtain ⟨x, hx⟩ := paired_has_nonfiniteSupport (fun _ => false)
  apply hx
  rw [h]
  trivial

/-- The inclusion D → G_a is not surjective even though its extension to the
canonical completions is the isomorphism `commonCompletionEquiv`. -/
theorem finiteSupport_inclusion_not_surjective (a : ℕ → Bool) :
    ¬ Function.Surjective (fun d : finiteSupport =>
      (⟨d.val, finiteSupport_le_preimage (selectorLine (pairedSelector a)) d.property⟩ : pairedGroup a)) := by
  obtain ⟨x, hx⟩ := paired_has_nonfiniteSupport a
  intro hs
  obtain ⟨d, hd⟩ := hs x
  apply hx
  exact (congrArg Subtype.val hd) ▸ d.property

/-- Transport the zero-subspace group to the original named D. -/
def bottomFiniteSupportEquiv : preimage (⊥ : Submodule ℚ TailSpace) ≃+ finiteSupport where
  toFun x := ⟨x.val, preimage_bot_eq_finiteSupport ▸ x.property⟩
  invFun d := ⟨d.val, finiteSupport_le_preimage ⊥ d.property⟩
  left_inv _ := rfl
  right_inv _ := rfl
  map_add' _ _ := rfl

def bottomFiniteHomEquiv (F : Type*) [AddGroup F] :
    (preimage (⊥ : Submodule ℚ TailSpace) →+ F) ≃ (finiteSupport →+ F) where
  toFun f := f.comp bottomFiniteSupportEquiv.symm.toAddMonoidHom
  invFun g := g.comp bottomFiniteSupportEquiv.toAddMonoidHom
  left_inv f := by ext x; rfl
  right_inv g := by ext x; rfl

/-- Monograph Proposition 4.5: natural finite-target equivalence with the original D. -/
def finiteSupportRestrictionEquiv (W : Submodule ℚ TailSpace) (F : Type*)
    [AddGroup F] [Finite F] : (preimage W →+ F) ≃ (finiteSupport →+ F) := by
  letI : TopologicalSpace F := ⊥
  letI : DiscreteTopology F := ⟨rfl⟩
  exact (finiteTargetHomEquiv W F).symm.trans
    ((finiteTargetHomEquiv ⊥ F).trans (bottomFiniteHomEquiv F))

/-- The forward equivalence is literal restriction along D's inclusion. -/
@[simp] theorem finiteSupportRestrictionEquiv_apply (W : Submodule ℚ TailSpace) (F : Type*)
    [AddGroup F] [Finite F] (f : preimage W →+ F) (d : finiteSupport) :
    finiteSupportRestrictionEquiv W F f d =
      f ⟨d.val, finiteSupport_le_preimage W d.property⟩ :=
  finiteTargetExtension_subtype W F f ⟨d.val, finiteSupport_le_preimage W d.property⟩

/-- Naturality in all finite target groups is an equality of homomorphisms. -/
theorem finiteSupportRestrictionEquiv_natural (W : Submodule ℚ TailSpace)
    (F E : Type*) [AddGroup F] [Finite F] [AddGroup E] [Finite E]
    (f : preimage W →+ F) (g : F →+ E) :
    finiteSupportRestrictionEquiv W E (g.comp f) =
      g.comp (finiteSupportRestrictionEquiv W F f) := by
  ext d
  simp

/-- The extension of D → G_a is an actual isomorphism of their canonical completions. -/
def finiteSupportToPairedCompletion (a : ℕ → Bool) :
    ProfiniteAddGrp.ProfiniteCompletion.completion (AddGrpCat.of finiteSupport) ≃ₜ+
      ProfiniteAddGrp.ProfiniteCompletion.completion (AddGrpCat.of (pairedGroup a)) :=
  finiteSupportCompletionEquiv.trans (pairedCompletionEquiv a).symm

theorem finiteSupportToPairedCompletion_eta (a : ℕ → Bool) (d : finiteSupport) :
    finiteSupportToPairedCompletion a
      (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of finiteSupport) d) =
      ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (pairedGroup a))
        ⟨d.val, finiteSupport_le_preimage (selectorLine (pairedSelector a)) d.property⟩ := by
  change (pairedCompletionEquiv a).symm
    (finiteSupportCompletionEquiv
      (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of finiteSupport) d)) = _
  rw [finiteSupportCompletionEquiv_eta]
  exact ambientToCompletion_subtype (selectorLine (pairedSelector a))
    ⟨d.val, finiteSupport_le_preimage (selectorLine (pairedSelector a)) d.property⟩

end RealizationBoundaries
