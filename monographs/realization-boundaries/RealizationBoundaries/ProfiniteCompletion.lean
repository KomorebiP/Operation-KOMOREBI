import RealizationBoundaries.FiniteTargets
import Mathlib.Topology.Algebra.Category.ProfiniteGrp.Completion

/-!
# The actual profinite-completion identification

The completion here is Mathlib's limit over ALL finite-index normal additive
subgroups. It is not a newly named copy of the desired product. Both comparison
maps are constructed and their inverse laws are proved using dense ranges.
-/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
open CategoryTheory
namespace RealizationBoundaries

abbrev CanonicalCompletion (W : Submodule ℚ TailSpace) :=
  ProfiniteAddGrp.ProfiniteCompletion.completion (AddGrpCat.of (preimage W))

abbrev CompletionIndex (W : Submodule ℚ TailSpace) :=
  FiniteIndexNormalAddSubgroup (preimage W)

def quotientProjection (W : Submodule ℚ TailSpace) (K : CompletionIndex W) :
    preimage W →+ (preimage W ⧸ K.toAddSubgroup) := QuotientAddGroup.mk' K.toAddSubgroup

def quotientTransition (W : Submodule ℚ TailSpace) {K L : CompletionIndex W} (h : K ≤ L) :
    (preimage W ⧸ K.toAddSubgroup) →+ (preimage W ⧸ L.toAddSubgroup) :=
  QuotientAddGroup.map _ _ (AddMonoidHom.id _) h

@[simp] theorem quotientTransition_projection (W : Submodule ℚ TailSpace)
    {K L : CompletionIndex W} (h : K ≤ L) :
    (quotientTransition W h).comp (quotientProjection W K) = quotientProjection W L := by
  ext x
  rfl

/-- Assemble the extended quotient maps into a point of the genuine inverse limit. -/
def ambientToCompletion (W : Submodule ℚ TailSpace) : Ambient →+ CanonicalCompletion W where
  toFun x := ⟨fun K => finiteTargetExtension W _ (quotientProjection W K) x, by
    intro K L f
    change quotientTransition W f.le
      (finiteTargetExtension W _ (quotientProjection W K) x) =
        finiteTargetExtension W _ (quotientProjection W L) x
    have h := finiteTargetExtension_natural W _ _
      (quotientProjection W K) (quotientTransition W f.le)
    rw [quotientTransition_projection] at h
    exact (DFunLike.congr_fun h x).symm⟩
  map_zero' := by
    apply Subtype.ext
    funext K
    exact map_zero (finiteTargetExtension W _ (quotientProjection W K))
  map_add' x y := by
    apply Subtype.ext
    funext K
    exact map_add (finiteTargetExtension W _ (quotientProjection W K)) x y

theorem ambientToCompletion_continuous (W : Submodule ℚ TailSpace) :
    Continuous (ambientToCompletion W) := by
  apply continuous_induced_rng.mpr
  apply continuous_pi
  intro K
  let : TopologicalSpace (preimage W ⧸ K.toAddSubgroup) := ⊥
  exact finiteTargetExtension_continuous W _ (quotientProjection W K)

@[simp] theorem ambientToCompletion_subtype (W : Submodule ℚ TailSpace) (x : preimage W) :
    ambientToCompletion W x.val =
      ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (preimage W)) x := by
  apply Subtype.ext
  funext K
  exact finiteTargetExtension_subtype W _ (quotientProjection W K) x

/-- The individual prime coordinate, as a homomorphism on the actual dense subgroup. -/
def primeCoordinate (W : Submodule ℚ TailSpace) (p : Prime) : preimage W →+ Coordinate p where
  toFun x := x.val p
  map_zero' := rfl
  map_add' _ _ := rfl

/-- Its kernel is an actual finite-index normal subgroup in the completion diagram. -/
def primeCoordinateIndex (W : Submodule ℚ TailSpace) (p : Prime) : CompletionIndex W :=
  FiniteIndexNormalAddSubgroup.ofAddSubgroup (primeCoordinate W p).ker

/-- Read one prime coordinate from Mathlib's actual profinite completion. -/
def completionCoordinate (W : Submodule ℚ TailSpace) (p : Prime) :
    CanonicalCompletion W →+ Coordinate p where
  toFun x := QuotientAddGroup.lift (primeCoordinate W p).ker (primeCoordinate W p) le_rfl
    (x.val (primeCoordinateIndex W p))
  map_zero' := map_zero _
  map_add' x y := map_add _ (x.val (primeCoordinateIndex W p))
    (y.val (primeCoordinateIndex W p))

theorem completionCoordinate_continuous (W : Submodule ℚ TailSpace) (p : Prime) :
    Continuous (completionCoordinate W p) := by
  let : TopologicalSpace (preimage W ⧸ (primeCoordinate W p).ker) := ⊥
  let : DiscreteTopology (preimage W ⧸ (primeCoordinate W p).ker) := ⟨rfl⟩
  exact (continuous_of_discreteTopology : Continuous
    (QuotientAddGroup.lift (primeCoordinate W p).ker (primeCoordinate W p) le_rfl)).comp
      ((continuous_apply (primeCoordinateIndex W p)).comp continuous_subtype_val)

@[simp] theorem completionCoordinate_eta (W : Submodule ℚ TailSpace) (p : Prime)
    (x : preimage W) : completionCoordinate W p
      (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (preimage W)) x) = x.val p := rfl

/-- The comparison map from the actual profinite completion to the fixed product. -/
def completionToAmbient (W : Submodule ℚ TailSpace) : CanonicalCompletion W →+ Ambient where
  toFun x p := completionCoordinate W p x
  map_zero' := by funext p; exact map_zero (completionCoordinate W p)
  map_add' x y := by funext p; exact map_add (completionCoordinate W p) x y

theorem completionToAmbient_continuous (W : Submodule ℚ TailSpace) :
    Continuous (completionToAmbient W) :=
  continuous_pi fun p => completionCoordinate_continuous W p

@[simp] theorem completionToAmbient_eta (W : Submodule ℚ TailSpace) (x : preimage W) :
    completionToAmbient W
      (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (preimage W)) x) = x.val := rfl

/-- The comparison is an inverse on the entire ambient product, not just on H_W. -/
theorem completionToAmbient_ambientToCompletion (W : Submodule ℚ TailSpace) (x : Ambient) :
    completionToAmbient W (ambientToCompletion W x) = x := by
  have heq : (fun y => completionToAmbient W (ambientToCompletion W y)) = id := by
    apply (preimage_denseRange W).equalizer
      ((completionToAmbient_continuous W).comp (ambientToCompletion_continuous W)) continuous_id
    funext y
    simp
  exact congrFun heq x

/-- The reverse inverse law uses the dense canonical map into Mathlib's completion. -/
theorem ambientToCompletion_completionToAmbient (W : Submodule ℚ TailSpace)
    (x : CanonicalCompletion W) : ambientToCompletion W (completionToAmbient W x) = x := by
  have heq : (fun y => ambientToCompletion W (completionToAmbient W y)) = id := by
    apply (ProfiniteAddGrp.ProfiniteCompletion.denseRange (AddGrpCat.of (preimage W))).equalizer
      ((ambientToCompletion_continuous W).comp (completionToAmbient_continuous W)) continuous_id
    funext y
    simp
  exact congrFun heq x

/-- Monograph completion theorem: the canonical profinite completion is topologically
and additively isomorphic to P, with the canonical embedding respected. -/
def profiniteCompletionEquiv (W : Submodule ℚ TailSpace) : CanonicalCompletion W ≃ₜ+ Ambient where
  toFun := completionToAmbient W
  invFun := ambientToCompletion W
  left_inv := ambientToCompletion_completionToAmbient W
  right_inv := completionToAmbient_ambientToCompletion W
  map_add' := map_add (completionToAmbient W)
  continuous_toFun := completionToAmbient_continuous W
  continuous_invFun := ambientToCompletion_continuous W

@[simp] theorem profiniteCompletionEquiv_eta (W : Submodule ℚ TailSpace) (x : preimage W) :
    profiniteCompletionEquiv W
      (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (preimage W)) x) = x.val := rfl

/-- The canonical map is a topological embedding for the induced product topology. -/
theorem completion_eta_isEmbedding (W : Submodule ℚ TailSpace) :
    Topology.IsEmbedding (ProfiniteAddGrp.ProfiniteCompletion.etaFn
      (AddGrpCat.of (preimage W))) := by
  have heq : ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (preimage W)) =
      (profiniteCompletionEquiv W).symm ∘ (fun x : preimage W => x.val) := by
    funext x
    exact (ambientToCompletion_subtype W x).symm
  rw [heq]
  exact (profiniteCompletionEquiv W).symm.toHomeomorph.isEmbedding.comp
    Topology.IsEmbedding.subtypeVal

/-- The full profinite topology is the initial topology of the canonical map into
the limit of all finite quotient groups. -/
@[instance_reducible] def fullProfiniteTopology (W : Submodule ℚ TailSpace) : TopologicalSpace (preimage W) :=
  TopologicalSpace.induced (ProfiniteAddGrp.ProfiniteCompletion.etaFn
    (AddGrpCat.of (preimage W))) inferInstance

/-- No topology from the finite quotients is missing from the induced product topology. -/
theorem fullProfiniteTopology_eq (W : Submodule ℚ TailSpace) :
    fullProfiniteTopology W = (inferInstance : TopologicalSpace (preimage W)) :=
  (completion_eta_isEmbedding W).isInducing.eq_induced.symm

end RealizationBoundaries
