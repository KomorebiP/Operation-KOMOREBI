import RealizationBoundaries.ClassificationConsequences
import RealizationBoundaries.CompletionReflection
import Mathlib.Topology.Algebra.Category.ProfiniteGrp.Completion
import Mathlib.CategoryTheory.ObjectProperty.FullSubcategory
import Mathlib.CategoryTheory.Filtered.Final
import Mathlib.CategoryTheory.Functor.ReflectsIso.Basic

/-!
# Finite observation systems and the completion functor

The global faithfulness statements below use Mathlib's actual profinite-completion
functor on arbitrary groups, rather than a family-specific coordinate extension.
-/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
open CategoryTheory
namespace RealizationBoundaries

/-- Naturality on actual canonical points for the official completion functor. -/
theorem official_completion_map_eta {G H : GrpCat} (f : G ⟶ H) (x : G) :
    ProfiniteGrp.profiniteCompletion.map f
      (ProfiniteGrp.ProfiniteCompletion.etaFn G x) =
      ProfiniteGrp.ProfiniteCompletion.etaFn H (f x) := by
  exact ConcreteCategory.congr_hom
    (ProfiniteGrp.ProfiniteCompletion.lift_eta
      (f ≫ ProfiniteGrp.ProfiniteCompletion.eta H)) x

/-- Completion distinguishes maps whenever their target is residually finite.
No commutativity, countability, continuity or source residual-finiteness is needed. -/
theorem official_completion_map_injective {G H : GrpCat}
    (hH : Group.ResiduallyFinite H) :
    Function.Injective (ProfiniteGrp.profiniteCompletion.map (X := G) (Y := H)) := by
  intro f g h
  ext x
  apply (ProfiniteGrp.ProfiniteCompletion.etaFn_injective_iff_residuallyFinite H).mpr hH
  rw [← official_completion_map_eta f x, ← official_completion_map_eta g x, h]

/-- The full category of all residually finite groups and all group homomorphisms. -/
def residuallyFiniteObjects : ObjectProperty GrpCat := fun G => Group.ResiduallyFinite G

abbrev ResiduallyFiniteGrp := residuallyFiniteObjects.FullSubcategory

/-- The restriction of the official profinite-completion functor. -/
def residuallyFiniteCompletion : ResiduallyFiniteGrp ⥤ ProfiniteGrp :=
  residuallyFiniteObjects.ι ⋙ ProfiniteGrp.profiniteCompletion

/-- Monograph 9.3, the unrestricted categorical faithfulness assertion. -/
instance residuallyFiniteCompletion_faithful : residuallyFiniteCompletion.Faithful where
  map_injective := by
    intro X Y f g h
    apply ObjectProperty.hom_ext
    exact official_completion_map_injective Y.property h

/-- A presentation of the full source category whose objects are the paired groups.
Every abstract additive group homomorphism is a morphism. -/
abbrev PairedGroupCategory := InducedCategory AddGrpCat
  (fun a : ℕ → Bool => AddGrpCat.of (pairedGroup a))

/-- The family completion functor on actual canonical profinite completions. -/
def pairedCompletionFunctor : PairedGroupCategory ⥤ ProfiniteAddGrp where
  obj a := CanonicalCompletion (selectorLine (pairedSelector a))
  map f := ProfiniteAddGrp.ofHom (completionHom _ _ f.hom.hom)
  map_id a := by
    apply ConcreteCategory.hom_ext
    intro x
    have he := completionHom_unique (selectorLine (pairedSelector a))
      (selectorLine (pairedSelector a)) (AddMonoidHom.id _)
      (ContinuousAddMonoidHom.id _) (fun _ => rfl)
    exact congrArg (fun h => h x) he.symm
  map_comp f g := by
    apply ConcreteCategory.hom_ext
    intro x
    exact congrArg (fun h => h x) (completionHom_comp _ _ _ f.hom.hom g.hom.hom)

instance pairedCompletionFunctor_faithful : pairedCompletionFunctor.Faithful where
  map_injective := by
    intro a b f g h
    apply InducedCategory.hom_ext
    apply AddGrpCat.hom_ext
    apply completionHom_injective (selectorLine (pairedSelector a))
      (selectorLine (pairedSelector b))
    exact congrArg (fun m => m.hom) h

/-- The completion morphism given by the common coordinates has no source lift. -/
theorem pairedCompletionFunctor_not_full : ¬ pairedCompletionFunctor.Full := by
  intro hf
  let : pairedCompletionFunctor.Full := hf
  let a : PairedGroupCategory := fun _ => false
  let b : PairedGroupCategory := fun _ => true
  let g : pairedCompletionFunctor.obj a ⟶ pairedCompletionFunctor.obj b :=
    ProfiniteAddGrp.ofHom {
      toAddMonoidHom := (pairedCommonCompletionEquiv a b).toAddMonoidHom
      continuous_toFun := (pairedCommonCompletionEquiv a b).continuous_toFun
    }
  obtain ⟨f, hfg⟩ := pairedCompletionFunctor.map_surjective g
  apply no_lift_of_commonCompletionEquiv a b constant_selectors_infinite_disagreement
  refine ⟨f.hom.hom, ?_⟩
  intro x
  have h := ConcreteCategory.congr_hom hfg
    (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (pairedGroup a)) x)
  exact h.symm.trans (completionHom_eta _ _ f.hom.hom x)

/-- Finite sets of primes, ordered in the direction of quotient restriction. -/
abbrev CoordinateIndex := OrderDual (Finset Prime)

/-- The source-free finite coordinate groups. -/
abbrev FiniteCoordinates (s : CoordinateIndex) := (p : {p : Prime // p ∈ s.ofDual}) → Coordinate p.val

def finiteCoordinateProjection (W : Submodule ℚ TailSpace) (s : CoordinateIndex) :
    preimage W →+ FiniteCoordinates s where
  toFun x p := x.val p.val
  map_zero' := rfl
  map_add' _ _ := rfl

def finiteCoordinateRestriction {s t : CoordinateIndex} (h : s ≤ t) :
    FiniteCoordinates s →+ FiniteCoordinates t where
  toFun x p := x ⟨p.val, h p.property⟩
  map_zero' := rfl
  map_add' _ _ := rfl

/-- This diagram contains no dense source group or evaluations of named elements. -/
def coordinateObservation : CoordinateIndex ⥤ FiniteAddGrp where
  obj s := FiniteAddGrp.of (FiniteCoordinates s)
  map f := FiniteAddGrp.ofHom (finiteCoordinateRestriction f.le)
  map_id _ := by ext; rfl
  map_comp _ _ := by ext; rfl

/-- The actual kernel indexing the corresponding quotient of the original group. -/
def finiteCoordinateIndex (W : Submodule ℚ TailSpace) (s : CoordinateIndex) : CompletionIndex W :=
  FiniteIndexNormalAddSubgroup.ofAddSubgroup (finiteCoordinateProjection W s).ker

theorem finiteCoordinateIndex_mono (W : Submodule ℚ TailSpace) :
    Monotone (finiteCoordinateIndex W) := by
  intro s t h x hx
  change finiteCoordinateProjection W t x = 0
  funext p
  exact congrFun hx ⟨p.val, h p.property⟩

/-- The inclusion of the finite-coordinate quotient subsystem in all finite quotients. -/
def coordinateIndexFunctor (W : Submodule ℚ TailSpace) : CoordinateIndex ⥤ CompletionIndex W :=
  (show CoordinateIndex →o CompletionIndex W from
    ⟨finiteCoordinateIndex W, finiteCoordinateIndex_mono W⟩).monotone.functor

/-- Every finite quotient is dominated by an actual finite-coordinate quotient. -/
theorem finiteCoordinateIndex_cofinal (W : Submodule ℚ TailSpace) (K : CompletionIndex W) :
    ∃ s : CoordinateIndex, finiteCoordinateIndex W s ≤ K := by
  let F := preimage W ⧸ K.toAddSubgroup
  let : Fintype F := Fintype.ofFinite F
  let m := Fintype.card F
  have hm : 0 < m := Fintype.card_pos
  let s : CoordinateIndex := OrderDual.toDual ((exceptional_finite hm).toFinset)
  refine ⟨s, ?_⟩
  intro x hx
  have hcoord : coordinateMap W m x = 0 := by
    funext p
    exact congrFun hx ⟨p.val, by
      change p.val ∈ (exceptional_finite hm).toFinset
      exact (exceptional_finite hm).mem_toFinset.mpr p.property⟩
  have hk := finite_target_coordinate_kernel W F (quotientProjection W K) hcoord
  exact (QuotientAddGroup.eq_zero_iff x).mp hk

/-- Categorical initiality records genuine cofinal reindexing of this inverse system. -/
instance coordinateIndexFunctor_initial (W : Submodule ℚ TailSpace) :
    (coordinateIndexFunctor W).Initial := by
  apply (Functor.initial_iff_of_isCofiltered _).mpr
  constructor
  · intro K
    obtain ⟨s, hs⟩ := finiteCoordinateIndex_cofinal W K
    exact ⟨s, ⟨hs.hom⟩⟩
  · intro K s f g
    exact ⟨s, 𝟙 s, Subsingleton.elim _ _⟩

/-- Extension by zero proves that these are quotient groups, not just finite targets. -/
theorem finiteCoordinateProjection_surjective (W : Submodule ℚ TailSpace) (s : CoordinateIndex) :
    Function.Surjective (finiteCoordinateProjection W s) := by
  intro z
  let x : Ambient := fun p => if hp : p ∈ s.ofDual then z ⟨p, hp⟩ else 0
  have hx : x ∈ finiteSupport := by
    apply s.ofDual.finite_toSet.subset
    intro p hp
    by_contra hn
    have hn' : p ∉ s.ofDual := hn
    exact hp (by simp [x, hn'])
  refine ⟨⟨x, finiteSupport_le_preimage W hx⟩, ?_⟩
  funext p
  change x p.val = z p
  simp [x, p.property]

/-- The canonical quotient-coordinate comparison. -/
def finiteCoordinateQuotientEquiv (W : Submodule ℚ TailSpace) (s : CoordinateIndex) :
    (preimage W ⧸ (finiteCoordinateIndex W s).toAddSubgroup) ≃+ FiniteCoordinates s :=
  QuotientAddGroup.quotientKerEquivOfSurjective (finiteCoordinateProjection W s)
    (finiteCoordinateProjection_surjective W s)

/-- The genuine all-finite-quotient diagram becomes the common coordinate diagram
under the categorically initial finite-coordinate reindexing. -/
def coordinateObservationIso (W : Submodule ℚ TailSpace) :
    coordinateIndexFunctor W ⋙ ProfiniteAddGrp.ProfiniteCompletion.finiteAddGrpDiagram
      (AddGrpCat.of (preimage W)) ≅ coordinateObservation :=
  NatIso.ofComponents (fun s => {
    hom := FiniteAddGrp.ofHom (finiteCoordinateQuotientEquiv W s).toAddMonoidHom
    inv := FiniteAddGrp.ofHom (finiteCoordinateQuotientEquiv W s).symm.toAddMonoidHom
    hom_inv_id := by ext x; exact (finiteCoordinateQuotientEquiv W s).symm_apply_apply x
    inv_hom_id := by ext x; exact (finiteCoordinateQuotientEquiv W s).apply_symm_apply x
  }) (by
    intro s t f
    ext x
    refine QuotientAddGroup.induction_on x ?_
    intro y
    rfl)

/-- Finite quotient kernels form a nonempty cofiltered index category. -/
instance completionIndex_cofiltered (W : Submodule ℚ TailSpace) :
    IsCofiltered (CompletionIndex W) := by
  let : Nonempty (CompletionIndex W) := ⟨finiteCoordinateIndex W (OrderDual.toDual ∅)⟩
  infer_instance

/-- An unmarked observation contains only a finite-group diagram. In particular
there is no source group and no distinguished image of any source element. -/
structure FiniteObservation where
  Index : Type
  [category : SmallCategory Index]
  [cofiltered : IsCofiltered Index]
  diagram : Index ⥤ FiniteAddGrp

attribute [instance] FiniteObservation.category FiniteObservation.cofiltered

/-- The actual system over all finite-index normal subgroups. -/
def allFiniteObservation (W : Submodule ℚ TailSpace) : FiniteObservation where
  Index := CompletionIndex W
  diagram := ProfiniteAddGrp.ProfiniteCompletion.finiteAddGrpDiagram (AddGrpCat.of (preimage W))

/-- Isomorphism after a common initial (inverse-system cofinal) reindexing.
Every pro-object invariant must respect this explicitly certified comparison. -/
def CommonCofinalObservation (A B : FiniteObservation) : Prop :=
  ∃ (I : Type) (_ : SmallCategory I) (F : I ⥤ A.Index) (G : I ⥤ B.Index),
    IsCofiltered I ∧ F.Initial ∧ G.Initial ∧ Nonempty (F ⋙ A.diagram ≅ G ⋙ B.diagram)

/-- All rational preimages have the same unmarked finite-quotient observation
under a source-free, compatible and genuinely cofinal comparison. -/
theorem allFiniteObservation_common (U V : Submodule ℚ TailSpace) :
    CommonCofinalObservation (allFiniteObservation U) (allFiniteObservation V) := by
  refine ⟨CoordinateIndex, inferInstance, coordinateIndexFunctor U,
    coordinateIndexFunctor V, inferInstance, coordinateIndexFunctor_initial U,
    coordinateIndexFunctor_initial V, ?_⟩
  exact ⟨(coordinateObservationIso U).trans (coordinateObservationIso V).symm⟩

/-- An arbitrary decoder invariant under certified pro-object comparisons.
No computability or definability restriction is imposed. -/
structure ObservationDecoder where
  decode : FiniteObservation → AddGrpCat
  invariant : ∀ A B, CommonCofinalObservation A B → Nonempty (decode A ≅ decode B)

/-- Monograph 9.1: no isomorphism-invariant decoder of the actual unmarked
finite-quotient systems recovers every paired source group. -/
theorem no_unmarked_observation_decoder (R : ObservationDecoder)
    (recovers : ∀ a : ℕ → Bool, Nonempty
      (R.decode (allFiniteObservation (selectorLine (pairedSelector a))) ≅
        AddGrpCat.of (pairedGroup a))) : False := by
  obtain ⟨ea⟩ := recovers (fun _ => false)
  obtain ⟨eb⟩ := recovers (fun _ => true)
  obtain ⟨er⟩ := R.invariant _ _ (allFiniteObservation_common _ _)
  exact constant_groups_not_isomorphic
    ⟨((ea.symm.trans er).trans eb).addGroupIsoToAddEquiv⟩

/-- The source category with D (the zero-subspace preimage) and all paired groups. -/
def boundarySubspace : Option (ℕ → Bool) → Submodule ℚ TailSpace
  | none => ⊥
  | some a => selectorLine (pairedSelector a)

abbrev BoundaryGroupCategory := InducedCategory AddGrpCat
  (fun i : Option (ℕ → Bool) => AddGrpCat.of (preimage (boundarySubspace i)))

/-- Completion on the enlarged full source category. -/
def boundaryCompletionFunctor : BoundaryGroupCategory ⥤ ProfiniteAddGrp where
  obj i := CanonicalCompletion (boundarySubspace i)
  map f := ProfiniteAddGrp.ofHom (completionHom _ _ f.hom.hom)
  map_id i := by
    apply ConcreteCategory.hom_ext
    intro x
    have he := completionHom_unique (boundarySubspace i) (boundarySubspace i)
      (AddMonoidHom.id _) (ContinuousAddMonoidHom.id _) (fun _ => rfl)
    exact congrArg (fun h => h x) he.symm
  map_comp f g := by
    apply ConcreteCategory.hom_ext
    intro x
    exact congrArg (fun h => h x) (completionHom_comp _ _ _ f.hom.hom g.hom.hom)

/-- The literal inclusion of the zero-subspace preimage, which equals D. -/
def bottomToPaired (a : ℕ → Bool) :
    preimage (⊥ : Submodule ℚ TailSpace) →+ pairedGroup a :=
  AddSubgroup.inclusion ((preimage_le_iff ⊥ (selectorLine (pairedSelector a))).mpr bot_le)

/-- The enlarged full source category contains a proper inclusion. -/
theorem bottomToPaired_not_surjective (a : ℕ → Bool) :
    ¬ Function.Surjective (bottomToPaired a) := by
  obtain ⟨x, hx⟩ := paired_has_nonfiniteSupport a
  intro hs
  obtain ⟨d, hd⟩ := hs x
  apply hx
  have hdmem : d.val ∈ finiteSupport := preimage_bot_eq_finiteSupport ▸ d.property
  exact congrArg Subtype.val hd ▸ hdmem

/-- This inclusion's induced map is exactly the common-coordinate equivalence. -/
theorem bottomToPaired_completion (a : ℕ → Bool) :
    completionHom ⊥ (selectorLine (pairedSelector a)) (bottomToPaired a) =
      { toAddMonoidHom := (commonCompletionEquiv ⊥ (selectorLine (pairedSelector a))).toAddMonoidHom
        continuous_toFun := (commonCompletionEquiv ⊥ (selectorLine (pairedSelector a))).continuous_toFun } := by
  symm
  apply completionHom_unique
  intro x
  exact commonCompletionEquiv_inclusion ⊥ (selectorLine (pairedSelector a)) bot_le x

/-- The failure to reflect isomorphisms is categorical, on the precise enlarged
full source category, and witnessed by the actual inclusion D → G_a. -/
theorem boundaryCompletionFunctor_not_reflects_isomorphisms :
    ¬ boundaryCompletionFunctor.ReflectsIsomorphisms := by
  intro hreflect
  let : boundaryCompletionFunctor.ReflectsIsomorphisms := hreflect
  let a : ℕ → Bool := fun _ => false
  let i : BoundaryGroupCategory := none
  let j : BoundaryGroupCategory := some a
  let f : i ⟶ j := InducedCategory.homMk (AddGrpCat.ofHom (bottomToPaired a))
  let e := commonCompletionEquiv ⊥ (selectorLine (pairedSelector a))
  let iso : boundaryCompletionFunctor.obj i ≅ boundaryCompletionFunctor.obj j := {
    hom := ProfiniteAddGrp.ofHom {
      toAddMonoidHom := e.toAddMonoidHom
      continuous_toFun := e.continuous_toFun }
    inv := ProfiniteAddGrp.ofHom {
      toAddMonoidHom := e.symm.toAddMonoidHom
      continuous_toFun := e.symm.continuous_toFun }
    hom_inv_id := by ext x; exact e.symm_apply_apply x
    inv_hom_id := by ext x; exact e.apply_symm_apply x
  }
  have hmap : boundaryCompletionFunctor.map f = iso.hom := by
    apply ConcreteCategory.hom_ext
    intro x
    exact congrArg (fun h => h x) (bottomToPaired_completion a)
  have : IsIso (boundaryCompletionFunctor.map f) := hmap.symm ▸ iso.isIso_hom
  have : IsIso f := isIso_of_reflects_iso f boundaryCompletionFunctor
  have : IsIso f.hom := (inducedFunctor
    (fun k : Option (ℕ → Bool) => AddGrpCat.of (preimage (boundarySubspace k)))).map_isIso f
  exact bottomToPaired_not_surjective a ((AddGrpCat.epi_iff_surjective f.hom).mp inferInstance)

end RealizationBoundaries
