import RealizationBoundaries

set_option autoImplicit false
noncomputable section
namespace RealizationBoundariesTests
open RealizationBoundaries

def allFalse : ℕ → Bool := fun _ => false

theorem no_half : ¬ ∃ y : pairedGroup allFalse,
    (2 : ℕ) • y = markedElement (pairedSelector allFalse) := by
  have hp : (primeAt (chosenIndex allFalse 0)).val = 2 := by simp [primeAt, chosenIndex, allFalse]
  simpa only [hp] using chosen_prime_obstructs allFalse 0

theorem third_root : ∃ y : pairedGroup allFalse,
    (3 : ℕ) • y = markedElement (pairedSelector allFalse) := by
  have hp : (primeAt (omittedIndex allFalse 0)).val = 3 := by simp [primeAt, omittedIndex, allFalse]
  simpa only [hp] using omitted_prime_has_root allFalse 0

theorem empty_selector_not_injective : ¬ Function.Injective (normalEvaluate ∅) := by
  intro h
  have hz : normalEvaluate ∅ (0,0) = normalEvaluate ∅ (1,0) := by
    apply Subtype.ext
    funext p
    change rationalSection ∅ 0 p + 0 = rationalSection ∅ 1 p + 0
    simp [rationalSection]
  have hc : (0 : ℚ) = 1 := congrArg Prod.fst (h hz)
  exact zero_ne_one hc

theorem cocycle_not_erasable : ¬ ∃ b : ℚ → finiteSupport,
    ∀ r t : ℚ, cocycle (pairedSelector allFalse) r t + b r + b t - b (r+t) = 0 :=
  cocycle_not_removable (pairedSelector_infinite allFalse)

theorem tail_nontrivial : ∃ v : TailSpace, v ≠ 0 :=
  ⟨quotientMap (indicator (pairedSelector allFalse)),
    indicator_tail_ne_zero (pairedSelector_infinite allFalse)⟩

theorem zero_multiplier_not_injective : ¬ Function.Injective (fun v : TailSpace => (0 : ℕ) • v) := by
  obtain ⟨v, hv⟩ := tail_nontrivial
  intro h
  exact hv (h (by simp))

theorem four_and_two_multiples (W : Submodule ℚ TailSpace) : multiples W 4 = multiples W 2 := by
  apply multiples_eq_of_same_prime_divisors W (by decide) (by decide)
  intro p
  change p.val ∣ 2*2 ↔ p.val ∣ 2
  rw [p.property.dvd_mul]
  simp

example (a : ℕ → Bool) : NormalForm (pairedSelector a) ≃+ pairedGroup a :=
  NormalForm.realizationEquiv (pairedSelector_infinite a)

example (a : ℕ → Bool) :
    (pairedGroup a ⧸ multiples (selectorLine (pairedSelector a)) 12) ≃+ DivisorCoordinates 12 :=
  integerQuotientEquiv (selectorLine (pairedSelector a)) (by decide)

example : ¬ Nat.Prime 4 := by decide
example : (2 : ZMod 2) = 0 := by decide

end RealizationBoundariesTests

namespace RealizationBoundariesContinuationTests
open RealizationBoundaries

example (H : AddSubgroup Ambient) (hD : finiteSupport ≤ H) (hH : IsPure H) :
    preimage (rationalImage H hD hH) = H := preimage_rationalImage H hD hH

example (W : Submodule ℚ TailSpace) :
    rationalImage (preimage W) (finiteSupport_le_preimage W) (preimage_isPure W) = W :=
  rationalImage_preimage W

example (V W : Submodule ℚ TailSpace) : preimage V ≤ preimage W ↔ V ≤ W := preimage_le_iff V W

theorem bottom_isPure : IsPure (⊥ : AddSubgroup Ambient) := by
  intro _ _ x _
  refine ⟨0, ?_⟩
  have hx : x = 0 := Subsingleton.elim x 0
  simp [hx]

theorem bottom_not_preimage : ¬ ∃ W : Submodule ℚ TailSpace,
    preimage W = (⊥ : AddSubgroup Ambient) := by
  rintro ⟨W, h⟩
  have hm := finiteSupport_le_preimage W (primeSeed (primeAt 0)).property
  rw [h] at hm
  have hz := AddSubgroup.mem_bot.mp hm
  have he := congrFun hz (primeAt 0)
  simp [primeSeed, cut] at he

example : Countable finiteSupport := inferInstance
example : Infinite finiteSupport := inferInstance
example (a : ℕ → Bool) : Countable (pairedGroup a) ∧ Infinite (pairedGroup a) :=
  paired_countably_infinite a
example (W : Submodule ℚ TailSpace) : Countable (preimage W) ↔ Countable W :=
  preimage_countable_iff W
example : Dense (finiteSupport : Set Ambient) := finiteSupport_dense
example : finiteSupport ≠ ⊤ := finiteSupport_ne_top
example (W : Submodule ℚ TailSpace) : DenseRange (fun x : preimage W => x.val) :=
  preimage_denseRange W
example : CompactSpace Ambient := inferInstance

example (W : Submodule ℚ TailSpace) (x : Ambient) :
    completionToAmbient W (ambientToCompletion W x) = x :=
  completionToAmbient_ambientToCompletion W x
example (W : Submodule ℚ TailSpace) (x : CanonicalCompletion W) :
    ambientToCompletion W (completionToAmbient W x) = x :=
  ambientToCompletion_completionToAmbient W x
example (W : Submodule ℚ TailSpace) (x : preimage W) :
    profiniteCompletionEquiv W
      (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (preimage W)) x) = x.val :=
  profiniteCompletionEquiv_eta W x
example (W : Submodule ℚ TailSpace) :
    fullProfiniteTopology W = (inferInstance : TopologicalSpace (preimage W)) :=
  fullProfiniteTopology_eq W
example (W : Submodule ℚ TailSpace) : AddGroup.ResiduallyFinite (preimage W) :=
  preimage_residuallyFinite W

example (a : ℕ → Bool) :
    ProfiniteAddGrp.ProfiniteCompletion.completion (AddGrpCat.of (pairedGroup a)) ≃ₜ+ Ambient :=
  pairedCompletionEquiv a
example : ProfiniteAddGrp.ProfiniteCompletion.completion (AddGrpCat.of finiteSupport) ≃ₜ+ Ambient :=
  finiteSupportCompletionEquiv
example (a : ℕ → Bool) :
    ¬ Function.Surjective (fun d : finiteSupport =>
      (⟨d.val, finiteSupport_le_preimage (selectorLine (pairedSelector a)) d.property⟩ : pairedGroup a)) :=
  finiteSupport_inclusion_not_surjective a

example (W : Submodule ℚ TailSpace) (F : Type*) [AddGroup F] [Finite F]
    (f : preimage W →+ F) (x : preimage W) : finiteTargetExtension W F f x.val = f x :=
  finiteTargetExtension_subtype W F f x
example (W : Submodule ℚ TailSpace) (F : Type*) [AddGroup F] [Finite F]
    (f : preimage W →+ F) (d : finiteSupport) : finiteSupportRestrictionEquiv W F f d =
      f ⟨d.val, finiteSupport_le_preimage W d.property⟩ :=
  finiteSupportRestrictionEquiv_apply W F f d
example (W : Submodule ℚ TailSpace) (F E : Type*) [AddGroup F] [Finite F]
    [AddGroup E] [Finite E] (f : preimage W →+ F) (g : F →+ E) :
    finiteSupportRestrictionEquiv W E (g.comp f) = g.comp (finiteSupportRestrictionEquiv W F f) :=
  finiteSupportRestrictionEquiv_natural W F E f g
example (a : ℕ → Bool) (d : finiteSupport) :
    finiteSupportToPairedCompletion a
      (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of finiteSupport) d) =
      ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (pairedGroup a))
        ⟨d.val, finiteSupport_le_preimage (selectorLine (pairedSelector a)) d.property⟩ :=
  finiteSupportToPairedCompletion_eta a d

end RealizationBoundariesContinuationTests

namespace RealizationBoundariesClassificationTests
open RealizationBoundaries
set_option backward.isDefEq.respectTransparency false

def zeroBits : ℕ → Bool := fun _ => false
def oneBits : ℕ → Bool := fun _ => true

example {r : ℚ} (hr : r ≠ 0) (d : finiteSupport) : (tailExceptions r d).Finite :=
  tailExceptions_finite hr d

/-- Zero rational coordinate must not be silently included in the finite-exception theorem. -/
theorem zero_exception_set_infinite : (tailExceptions 0 (0 : finiteSupport)).Infinite := by
  have he : tailExceptions 0 (0 : finiteSupport) = Set.univ := by
    ext p
    simp [tailExceptions, exceptional]
  rw [he]
  exact Set.infinite_univ

/-- A numerator prime can have a root even when it is selected. -/
theorem numerator_exception_has_root :
    HasPrimeRoot (normalEvaluate (pairedSelector zeroBits) (2,0)) (primeAt 0) := by
  rw [preimage_prime_root_iff (selectorLine (pairedSelector zeroBits))]
  change rationalSection (pairedSelector zeroBits) 2 (primeAt 0) + 0 = 0
  have hc : (2 : Coordinate (primeAt 0)) = 0 :=
    (coordinate_cast_eq_zero 2 (primeAt 0)).mpr (by simp [primeAt])
  simp [rationalSection, hc]

/-- A denominator prime is genuinely a zero coordinate in the actual section. -/
example : rationalSection (pairedSelector zeroBits) (1/2) (primeAt 0) = 0 := by
  apply rationalSection_denominator_zero
  have hp : (primeAt 0).val = 2 := by simp [primeAt]
  rw [hp]
  simp [one_div, Rat.den_inv]

/-- A finite correction may change the root test at a selected prime. -/
theorem support_exception_has_root (S : Set Prime) (p : Prime) (hp : p ∈ S) :
    HasPrimeRoot (normalEvaluate S (1, -(primeSeed p))) p := by
  rw [preimage_prime_root_iff (selectorLine S)]
  change rationalSection S 1 p + (-(primeSeed p).val) p = 0
  simp [rationalSection_one, indicator_apply_mem hp, primeSeed, cut]

example (S : Set Prime) (x : selectorGroup S) (hx : x.val ∉ finiteSupport) :
    ∃ E : Set Prime, E.Finite ∧ ∀ p ∉ E, (HasPrimeRoot x p ↔ p ∉ S) :=
  selector_tail_signature S x hx

example (a b : ℕ → Bool) (f : pairedGroup a →+ pairedGroup b) (x : pairedGroup a)
    (hx : (f x).val ∉ finiteSupport) : {n | a n ≠ b n}.Finite :=
  finite_disagreement_of_nontorsion_image a b f x hx

example (a b : ℕ → Bool) :
    Nonempty (pairedGroup a ≃+ pairedGroup b) ↔ {n | a n ≠ b n}.Finite :=
  pairedGroup_isomorphic_iff a b

example (a b : ℕ → Bool) (h : {n | a n ≠ b n}.Finite) : pairedGroup a = pairedGroup b :=
  pairedGroup_eq_of_finite_disagreement a b h

example (a b : ℕ → Bool) :
    (∃ e : pairedGroup a ≃+ pairedGroup b,
      e (markedElement (pairedSelector a)) = markedElement (pairedSelector b)) ↔ a = b :=
  pairedGroup_marked_isomorphic_iff a b

example (a : ℕ → Bool) (k : ℕ) : pairedGroup a = pairedGroup (toggleBit a k) :=
  toggleBit_group_eq a k

example (a : ℕ → Bool) (k : ℕ) : a ≠ toggleBit a k := toggleBit_ne a k

example (a : ℕ → Bool) (k : ℕ) :
    ¬ ∃ e : pairedGroup a ≃+ pairedGroup (toggleBit a k),
      e (markedElement (pairedSelector a)) = markedElement (pairedSelector (toggleBit a k)) :=
  toggleBit_not_marked_isomorphic a k

example : ¬ Nonempty (pairedGroup zeroBits ≃+ pairedGroup oneBits) :=
  constant_groups_not_isomorphic

example (f : pairedGroup zeroBits →+ pairedGroup oneBits) (x : pairedGroup zeroBits) :
    (f x).val ∈ finiteSupport :=
  hom_image_finiteSupport _ _ constant_selectors_infinite_disagreement f x

example (f : pairedGroup zeroBits →+ pairedGroup oneBits) : ¬ Function.Injective f :=
  no_injective_hom_of_infinite_disagreement _ _ constant_selectors_infinite_disagreement f

example (f : pairedGroup zeroBits →+ pairedGroup oneBits) : ¬ Function.Surjective f :=
  no_surjective_hom_of_infinite_disagreement _ _ constant_selectors_infinite_disagreement f

example (a b : ℕ → Bool) :
    (∃ f : pairedGroup a →+ pairedGroup b, Function.Injective f) ↔ {n | a n ≠ b n}.Finite :=
  pairedGroup_embeds_iff a b

example (a b : ℕ → Bool) :
    (∃ f : pairedGroup a →+ pairedGroup b, Function.Surjective f) ↔ {n | a n ≠ b n}.Finite :=
  pairedGroup_surjects_iff a b

example (a b : ℕ → Bool) (h : {n | a n ≠ b n}.Infinite) (f : pairedGroup a →+ pairedGroup b) :
    finiteSupport.subtype.comp (torsionFactor a b h f) = (pairedGroup b).subtype.comp f :=
  torsionFactor_commutes a b h f

example (a b : ℕ → Bool) (h : {n | a n ≠ b n}.Finite) (x : NormalForm (pairedSelector a)) :
    (normalFormTransport a b h x).rational = x.rational := rfl

example (a b : ℕ → Bool) (h : {n | a n ≠ b n}.Finite) (x : NormalForm (pairedSelector a)) :
    (NormalForm.realizationEquiv (pairedSelector_infinite b) (normalFormTransport a b h x)).val =
      (NormalForm.realizationEquiv (pairedSelector_infinite a) x).val :=
  normalFormTransport_realization a b h x

example (a b : ℕ → Bool) (h : {n | a n ≠ b n}.Finite) (x y : NormalForm (pairedSelector a)) :
    normalFormTransport a b h (x+y) = normalFormTransport a b h x + normalFormTransport a b h y :=
  normalFormTransport_add a b h x y

example (a b : ℕ → Bool) (h : {n | a n ≠ b n}.Finite) (x : NormalForm (pairedSelector a)) :
    (normalFormTransportEquiv a b h).symm (normalFormTransportEquiv a b h x) = x :=
  (normalFormTransportEquiv a b h).symm_apply_apply x

example : ∃ a b : ℕ → Bool,
    Nonempty (CanonicalCompletion (selectorLine (pairedSelector a)) ≃ₜ+
      CanonicalCompletion (selectorLine (pairedSelector b))) ∧
    ¬ Nonempty (pairedGroup a ≃+ pairedGroup b) := completion_object_counterexample

example (R : (ℕ → Bool) → Type*) [∀ a, AddGroup (R a)]
    (hi : ∀ a b,
      Nonempty (CanonicalCompletion (selectorLine (pairedSelector a)) ≃ₜ+
        CanonicalCompletion (selectorLine (pairedSelector b))) → Nonempty (R a ≃+ R b))
    (hr : ∀ a, Nonempty (R a ≃+ pairedGroup a)) : False :=
  no_completion_invariant_reconstruction R hi hr

example (a b : ℕ → Bool) (h : {n | a n ≠ b n}.Infinite) :
    ¬ ∃ f : pairedGroup a →+ pairedGroup b, ∀ x : pairedGroup a,
      pairedCommonCompletionEquiv a b
        (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (pairedGroup a)) x) =
      ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (pairedGroup b)) (f x) :=
  no_lift_of_commonCompletionEquiv a b h

/-- The stronger all-prime assertion fails on an explicit infinite-order normal form. -/
theorem numerator_not_exact_signature :
    ¬ (HasPrimeRoot (normalEvaluate (pairedSelector zeroBits) (2,0)) (primeAt 0) ↔
      primeAt 0 ∉ pairedSelector zeroBits) := by
  intro h
  have hp : primeAt 0 ∈ pairedSelector zeroBits := by
    simpa [chosenIndex, zeroBits] using chosen_mem zeroBits 0
  exact ((h.mp numerator_exception_has_root)) hp

/-- A nonzero homomorphism exists even between infinitely different selectors. -/
def oneCoordinateMap (a b : ℕ → Bool) (p : Prime) : pairedGroup a →+ pairedGroup b where
  toFun x := ⟨cut {p} x.val,
    finiteSupport_le_preimage (selectorLine (pairedSelector b)) (cut_mem_finiteSupport {p} x.val)⟩
  map_zero' := by
    apply Subtype.ext
    funext q
    simp [cut]
  map_add' x y := by
    apply Subtype.ext
    funext q
    by_cases hq : q ∈ ({p} : Finset Prime) <;> simp [cut, hq]

theorem oneCoordinateMap_ne_zero (a b : ℕ → Bool) (p : Prime) :
    oneCoordinateMap a b p ≠ 0 := by
  intro h
  let x : pairedGroup a := ⟨(primeSeed p).val,
    finiteSupport_le_preimage (selectorLine (pairedSelector a)) (primeSeed p).property⟩
  have he := congrArg (fun y : pairedGroup b => y.val p) (DFunLike.congr_fun h x)
  simp [oneCoordinateMap, x, primeSeed, cut] at he

example : ∃ f : pairedGroup zeroBits →+ pairedGroup oneBits, f ≠ 0 :=
  ⟨oneCoordinateMap zeroBits oneBits (primeAt 0), oneCoordinateMap_ne_zero _ _ _⟩

end RealizationBoundariesClassificationTests

namespace RealizationBoundariesDiagonalTests
open RealizationBoundaries
set_option backward.isDefEq.respectTransparency false

example (U V : Submodule ℚ TailSpace) (f : preimage U →+ preimage V)
    (x : preimage U) (p : Prime) :
    (f x).val p = homDiagonal U V f p * x.val p := hom_coordinate_formula U V f x p

example (U V : Submodule ℚ TailSpace) (f : preimage U →+ preimage V)
    (x : preimage U) (p : Prime) (hx : x.val p = 0) : (f x).val p = 0 :=
  hom_preserves_zero_coordinate U V f x p hx

example (U V : Submodule ℚ TailSpace) (f : preimage U →+ preimage V) : Continuous f :=
  preimage_hom_continuous U V f

example (U V : Submodule ℚ TailSpace) (f : preimage U →+ preimage V) :
    (diagonalHomEquiv U V).symm (diagonalHomEquiv U V f) = f :=
  (diagonalHomEquiv U V).symm_apply_apply f

example (U V : Submodule ℚ TailSpace) (c : Ambient) (hc : DiagonalAdmissible U V c) :
    homDiagonal U V (diagonalRestriction U V c hc) = c :=
  homDiagonal_restriction U V c hc

example (c : Ambient) (r : ℚ) (v : TailSpace) :
    diagonalTail c (r • v) = r • diagonalTail c v := map_smul (diagonalTail c) r v

example (S T : Set Prime) (c : Ambient) :
    DiagonalAdmissible (selectorLine S) (selectorLine T) c ↔
      ∃ r : ℚ, diagonal c (indicator S) - rationalSection T r ∈ finiteSupport :=
  diagonalAdmissible_iff_finite_defect S T c

example (S : Set Prime) (c : Ambient) :
    c ∈ diagonalEndRing (selectorLine S) ↔
      ∃ r : ℚ, {p | p ∈ S ∧ c p ≠ (r : Coordinate p)}.Finite :=
  diagonalEndRing_mem_iff S c

example (W : Submodule ℚ TailSpace) :
    AddMonoid.End (preimage W) ≃+* diagonalEndRing W := endomorphismRingEquiv W

example (W : Submodule ℚ TailSpace) (f g : AddMonoid.End (preimage W)) : f*g = g*f :=
  preimage_endomorphisms_commute W f g

example (S : Set Prime) (hS : S.Infinite) (r : ℚ) :
    quotientScalar S hS (rationalDiagonal S r) = r :=
  quotientScalar_rationalDiagonal S hS r

example (S : Set Prime) (hS : S.Infinite) : Function.Surjective (quotientScalar S hS) :=
  quotientScalar_surjective S hS

example (S : Set Prime) (hS : S.Infinite) (c d : diagonalEndRing (selectorLine S)) :
    quotientScalar S hS (c*d) = quotientScalar S hS c * quotientScalar S hS d :=
  map_mul (quotientScalar S hS) c d

example (S : Set Prime) (hS : S.Infinite) (c : diagonalEndRing (selectorLine S)) :
    quotientScalar S hS c = 0 ↔ {p | p ∈ S ∧ c.val p ≠ 0}.Finite :=
  quotientScalar_eq_zero_iff S hS c

example (S : Set Prime) (hS : S.Infinite) :
    Function.Surjective (endomorphismQuotientScalar S hS) :=
  endomorphismQuotientScalar_surjective S hS

example (S T : Set Prime) (hS : S.Infinite) (c : Ambient)
    (hc : DiagonalAdmissible (selectorLine S) (selectorLine T) c)
    (hn : ∀ p, c p ≠ 0) : diagonalSlope S T c hc ≠ 0 :=
  diagonalSlope_ne_zero S T hS c hc hn

example (S T : Set Prime) (hS : S.Infinite) (c : Ambient)
    (hc : DiagonalAdmissible (selectorLine S) (selectorLine T) c)
    (hn : ∀ p, c p ≠ 0) :
    DiagonalAdmissible (selectorLine T) (selectorLine S) (inverseDiagonal c) :=
  inverseDiagonal_admissible S T hS c hc hn

example (S T : Set Prime) (hS : S.Infinite) (f : selectorGroup S →+ selectorGroup T) :
    Function.Injective f ↔ Function.Bijective f :=
  selector_hom_injective_iff_bijective S T hS f

example (S T : Set Prime) (hS : S.Infinite) (f : selectorGroup S →+ selectorGroup T) :
    Function.Surjective f ↔ Function.Bijective f :=
  selector_hom_surjective_iff_bijective S T hS f

example (S T : Set Prime) (hS : S.Infinite) (f : selectorGroup S →+ selectorGroup T)
    (hn : ∀ p, homDiagonal (selectorLine S) (selectorLine T) f p ≠ 0)
    (y : selectorGroup T) (p : Prime) :
    ((selectorEquivOfNonzeroDiagonal S T hS f hn).symm y).val p =
      (homDiagonal (selectorLine S) (selectorLine T) f p)⁻¹ * y.val p :=
  selectorEquiv_inverse_coordinate S T hS f hn y p

example (U V : Submodule ℚ TailSpace) (f : preimage U →+ preimage V) (x : preimage U) :
    completionHom U V f
      (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (preimage U)) x) =
      ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (preimage V)) (f x) :=
  completionHom_eta U V f x

example (U V : Submodule ℚ TailSpace) (f : preimage U →+ preimage V)
    (x : CanonicalCompletion U) :
    profiniteCompletionEquiv V (completionHom U V f x) =
      diagonal (homDiagonal U V f) (profiniteCompletionEquiv U x) :=
  completionHom_coordinates U V f x

example (U V W : Submodule ℚ TailSpace) (f : preimage U →+ preimage V)
    (g : preimage V →+ preimage W) :
    completionHom U W (g.comp f) = (completionHom V W g).comp (completionHom U V f) :=
  completionHom_comp U V W f g

example (U V : Submodule ℚ TailSpace) : Function.Injective (completionHom U V) :=
  completionHom_injective U V

example (S T : Set Prime) (hS : S.Infinite) (f : selectorGroup S →+ selectorGroup T) :
    Function.Bijective (completionHom (selectorLine S) (selectorLine T) f) ↔
      Function.Bijective f := selector_completion_reflection S T hS f

example : AddMonoid.End finiteSupport ≃+* Ambient := finiteSupportEndomorphismRingEquiv

example (f : AddMonoid.End finiteSupport) (x : finiteSupport) (p : Prime) (hx : x.val p = 0) :
    (f x).val p = 0 := finiteSupport_endomorphism_preserves_zero f x p hx

/-- Positive control: no abstract homomorphism transfers a prime seed to another prime. -/
theorem no_off_diagonal_seed (U V : Submodule ℚ TailSpace)
    (f : preimage U →+ preimage V) (p q : Prime) (hpq : p ≠ q) :
    (f (preimageSeed U p)).val q = 0 := by
  apply hom_preserves_zero_coordinate U V f _ q
  classical
  simp [preimageSeed, primeSeed, cut, Ne.symm hpq]

/-- A coordinate projection has quotient scalar one but kills every omitted-prime seed. -/
def selectedProjection (a : ℕ → Bool) : AddMonoid.End (pairedGroup a) :=
  diagonalRestriction _ _ (rationalDiagonal (pairedSelector a) 1).val
    (rationalDiagonal (pairedSelector a) 1).property

theorem selectedProjection_scalar (a : ℕ → Bool) :
    endomorphismQuotientScalar (pairedSelector a) (pairedSelector_infinite a)
      (selectedProjection a) = 1 := by
  change quotientScalar (pairedSelector a) (pairedSelector_infinite a)
    (homDiagonalRing (selectorLine (pairedSelector a)) (selectedProjection a)) = 1
  have he : homDiagonalRing (selectorLine (pairedSelector a)) (selectedProjection a) =
      rationalDiagonal (pairedSelector a) 1 :=
    Subtype.ext (homDiagonal_restriction (selectorLine (pairedSelector a))
      (selectorLine (pairedSelector a)) (rationalDiagonal (pairedSelector a) 1).val
      (rationalDiagonal (pairedSelector a) 1).property)
  rw [he, quotientScalar_rationalDiagonal]

theorem selectedProjection_not_injective (a : ℕ → Bool) :
    ¬ Function.Injective (selectedProjection a) := by
  intro hi
  have hn := (hom_injective_iff_diagonal_nonzero _ _ (selectedProjection a)).mp hi
  have hd : homDiagonal (selectorLine (pairedSelector a)) (selectorLine (pairedSelector a))
      (selectedProjection a) = (rationalDiagonal (pairedSelector a) 1).val :=
    homDiagonal_restriction (selectorLine (pairedSelector a))
      (selectorLine (pairedSelector a)) (rationalDiagonal (pairedSelector a) 1).val
      (rationalDiagonal (pairedSelector a) 1).property
  have h := hn (primeAt (omittedIndex a 0))
  rw [hd] at h
  change rationalSection (pairedSelector a) 1 (primeAt (omittedIndex a 0)) ≠ 0 at h
  rw [rationalSection_one] at h
  exact h (indicator_apply_not_mem (omitted_not_mem a 0))

theorem identity_not_admissible_across_constant_selectors :
    ¬ DiagonalAdmissible (selectorLine (pairedSelector (fun _ => false)))
      (selectorLine (pairedSelector (fun _ => true))) 1 := by
  intro h
  let f := diagonalRestriction _ _ 1 h
  have hi : Function.Injective f := by
    apply (hom_injective_iff_diagonal_nonzero _ _ f).mpr
    intro p
    have hc := homDiagonal_restriction _ _ 1 h
    rw [hc]
    exact one_ne_zero
  exact no_injective_hom_of_infinite_disagreement _ _
    constant_selectors_infinite_disagreement f hi

theorem inverse_zero_is_not_inverse :
    diagonal (inverseDiagonal 0) (diagonal 0 (primeSeed (primeAt 0)).val) ≠
      (primeSeed (primeAt 0)).val := by
  intro h
  have hp := congrFun h (primeAt 0)
  simp [inverseDiagonal, primeSeed, cut] at hp

/-- The proper inclusion from the zero quotient remains a counterexample outside rank one. -/
def bottomInclusion (a : ℕ → Bool) : preimage (⊥ : Submodule ℚ TailSpace) →+ pairedGroup a where
  toFun x := ⟨x.val, finiteSupport_le_preimage _
    (preimage_bot_eq_finiteSupport ▸ x.property)⟩
  map_zero' := rfl
  map_add' _ _ := rfl

theorem bottomInclusion_not_surjective (a : ℕ → Bool) :
    ¬ Function.Surjective (bottomInclusion a) := by
  intro hs
  obtain ⟨x, hx⟩ := hs (markedElement (pairedSelector a))
  have hd : x.val ∈ finiteSupport := preimage_bot_eq_finiteSupport ▸ x.property
  have he := congrArg (fun z : pairedGroup a => z.val) hx
  exact markedElement_not_finiteSupport (pairedSelector_infinite a) (he ▸ hd)

theorem bottomInclusion_completion_bijective (a : ℕ → Bool) :
    Function.Bijective (completionHom ⊥ (selectorLine (pairedSelector a)) (bottomInclusion a)) := by
  apply (completionHom_bijective_iff _ _ _).mpr
  intro p
  change (preimageSeed ⊥ p).val p ≠ 0
  rw [preimageSeed_apply]
  exact one_ne_zero

/-- Clearing a denominator does not make the chosen section a ring section. -/
theorem rationalDiagonal_not_additive :
    rationalDiagonal (pairedSelector (fun _ => false)) ((1/2 : ℚ) + 1/2) ≠
      rationalDiagonal (pairedSelector (fun _ => false)) (1/2) +
      rationalDiagonal (pairedSelector (fun _ => false)) (1/2) := by
  intro h
  have hp : primeAt 0 ∈ pairedSelector (fun _ => false) := by
    simpa [chosenIndex] using chosen_mem (fun _ => false) 0
  have hhalf : rationalSection (pairedSelector (fun _ => false)) (1/2) (primeAt 0) = 0 := by
    apply rationalSection_denominator_zero
    simp [primeAt]
  have hr : ((1/2 : ℚ) + 1/2) = 1 := by norm_num
  have he := congrArg (fun c : diagonalEndRing (selectorLine (pairedSelector (fun _ => false))) =>
    c.val (primeAt 0)) h
  change rationalSection (pairedSelector (fun _ => false)) ((1/2 : ℚ)+1/2) (primeAt 0) =
    rationalSection (pairedSelector (fun _ => false)) (1/2) (primeAt 0) +
    rationalSection (pairedSelector (fun _ => false)) (1/2) (primeAt 0) at he
  rw [hr, rationalSection_one, indicator_apply_mem hp, hhalf, zero_add] at he
  exact one_ne_zero he

end RealizationBoundariesDiagonalTests

namespace RealizationBoundariesSeedTests
open RealizationBoundaries

example {G : Type*} [AddGroup G] (S : Set G) {x : G} (hx : x ∈ S) :
    x ∈ endomorphismHull S := seed_mem_endomorphismHull hx

example {G : Type*} [AddGroup G] (S : Set G) (f : AddMonoid.End G)
    {x : G} (hx : x ∈ endomorphismHull S) : f x ∈ endomorphismHull S :=
  endomorphismHull_invariant S f hx

example (S : Set finiteSupport) (hs : S.Finite) :
    endomorphismHull S ≠ ⊤ := finiteSupport_no_finite_endomorphism_seeds S hs

example (S : Set finiteSupport) (hs : S.Finite) :
    topologicalEndomorphismHull S ≠ ⊤ := finiteSupport_no_finite_topological_seeds S hs

example (a : ℕ → Bool) (S : Set (pairedGroup a)) (hs : S.Finite) :
    endomorphismHull S ≠ ⊤ := paired_no_finite_endomorphism_seeds a S hs

example (a : ℕ → Bool) (S : Set (pairedGroup a)) (hs : S.Finite) :
    topologicalEndomorphismHull S ≠ ⊤ := paired_no_finite_topological_seeds a S hs

example (a : ℕ → Bool) (x : pairedGroup a) :
    (support x.val \ pairedSelector a).Finite := selector_outside_support_finite _ x

example (a : ℕ → Bool) (x : pairedGroup a) :
    topologicalEndomorphismHull {x} ≠ ⊤ :=
  paired_no_finite_topological_seeds a {x} (Set.finite_singleton x)

example : endomorphismSeedRank finiteSupport = Cardinal.aleph0 :=
  finiteSupport_endomorphismSeedRank

example : topologicalEndomorphismSeedRank finiteSupport = Cardinal.aleph0 :=
  finiteSupport_topologicalEndomorphismSeedRank

example : ordinaryTopologicalRank finiteSupport = Cardinal.aleph0 :=
  finiteSupport_ordinaryTopologicalRank

example (a : ℕ → Bool) : endomorphismSeedRank (pairedGroup a) = Cardinal.aleph0 :=
  paired_endomorphismSeedRank a

example (a : ℕ → Bool) : topologicalEndomorphismSeedRank (pairedGroup a) = Cardinal.aleph0 :=
  paired_topologicalEndomorphismSeedRank a

example (a : ℕ → Bool) : ordinaryTopologicalRank (pairedGroup a) = Cardinal.aleph0 :=
  paired_ordinaryTopologicalRank a

example (a : ℕ → Bool) :
    IsLeast (generationCardinals (endomorphismHull (G := pairedGroup a))) Cardinal.aleph0 :=
  generationCardinals_isLeast_aleph0 _ endomorphismHull_univ
    (paired_no_finite_endomorphism_seeds a)

example (J : Finset Prime) (x : Ambient) :
    ∃ n : ℕ, ∀ p ∈ J, (n : Coordinate p) = x p := finite_coordinate_interpolation J x

example : Dense (AddSubgroup.closure {(1 : Ambient)} : Set Ambient) := ambient_cyclic_dense

example : ordinaryTopologicalHull {(1 : Ambient)} = ⊤ := ambient_topological_generator

example : ordinaryTopologicalRank Ambient = 1 := ambient_ordinaryTopologicalRank

example (W : Submodule ℚ TailSpace) :
    ordinaryTopologicalHull {completionGenerator W} = ⊤ := completionGenerator_generates W

example (W : Submodule ℚ TailSpace) :
    ordinaryTopologicalRank (CanonicalCompletion W) = 1 := canonicalCompletion_ordinaryTopologicalRank W

example : (1 : Ambient) ∉ finiteSupport := all_one_not_finiteSupport

example (a : ℕ → Bool) : (1 : Ambient) ∉ pairedGroup a := all_one_not_pairedGroup a

example (m : ℕ) (hm : 0 < m) : m • (1 : Ambient) ≠ 0 := all_one_infinite_order m hm

example (a : ℕ → Bool) :
    completionGenerator (selectorLine (pairedSelector a)) ∉
      Set.range (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (pairedGroup a))) :=
  paired_completionGenerator_not_in_eta_range a

example (p : Prime) : (primeSeed p).val ∉ AddSubgroup.closure {(1 : Ambient)} :=
  primeSeed_not_in_all_one_cyclic p

example : AddSubgroup.closure {(1 : Ambient)} ≠ ⊤ := all_one_cyclic_ne_top

example : endomorphismHull {(1 : Ambient)} = ⊤ := ambient_single_endomorphism_generator

example : endomorphismSeedRank Ambient = 1 := ambient_endomorphismSeedRank

/-- Marked elements themselves have infinite support: only their unselected support is finite. -/
theorem marked_not_finite_support (a : ℕ → Bool) :
    ¬ (support (markedElement (pairedSelector a)).val).Finite :=
  markedElement_not_finiteSupport (pairedSelector_infinite a)

/-- Empty seeds do not generate a nontrivial Hausdorff group even topologically. -/
theorem empty_ambient_not_generating : ordinaryTopologicalHull (∅ : Set Ambient) ≠ ⊤ := by
  rw [ordinaryTopologicalHull_empty]
  exact bot_ne_top

/-- Exact infinite rank is incompatible with a singleton operator-generation claim. -/
theorem paired_seed_rank_ne_one (a : ℕ → Bool) :
    endomorphismSeedRank (pairedGroup a) ≠ 1 := by
  rw [paired_endomorphismSeedRank]
  exact ne_of_gt Cardinal.one_lt_aleph0

/-- A zero coordinate is a simultaneous obstruction for every map, not a chosen finite list. -/
example (a : ℕ → Bool) (S : Set (pairedGroup a)) (hs : S.Finite) :
    ∃ p : Prime, p ∉ pairedSelector a ∧
      endomorphismHull S ≤ coordinateKernel (pairedGroup a) p ∧
      topologicalEndomorphismHull S ≤ coordinateKernel (pairedGroup a) p ∧
      coordinateKernel (pairedGroup a) p ≠ ⊤ := paired_seed_certificate a S hs

end RealizationBoundariesSeedTests


namespace RealizationBoundariesRootTests
open RealizationBoundaries
open scoped BigOperators

theorem radical_four : primeRadical 4 = 2 :=
  primeRadical_prime_pow Nat.prime_two (by decide : (2 : ℕ) ≠ 0)

theorem radical_eight : primeRadical 8 = 2 :=
  primeRadical_prime_pow Nat.prime_two (by decide : (3 : ℕ) ≠ 0)

theorem radical_twelve : primeRadical 12 = 6 := by
  change (∏ p ∈ ((2 ^ 2) * 3).primeFactors, p) = 6
  rw [Nat.primeFactors_mul (by decide) (by decide),
    Nat.primeFactors_prime_pow (by decide : (2 : ℕ) ≠ 0) Nat.prime_two,
    (by decide : Nat.Prime 3).primeFactors]
  norm_num

theorem radical_eighteen : primeRadical 18 = 6 := by
  change (∏ p ∈ (2 * (3 ^ 2)).primeFactors, p) = 6
  rw [Nat.primeFactors_mul (by decide) (by decide), Nat.prime_two.primeFactors,
    Nat.primeFactors_prime_pow (by decide : (2 : ℕ) ≠ 0) (by decide : Nat.Prime 3)]
  norm_num

theorem radical_thirty : primeRadical 30 = 30 := by
  change (∏ p ∈ ((2 * 3) * 5).primeFactors, p) = 30
  rw [Nat.primeFactors_mul (by decide) (by decide),
    Nat.primeFactors_mul (by decide) (by decide), Nat.prime_two.primeFactors,
    (by decide : Nat.Prime 3).primeFactors, (by decide : Nat.Prime 5).primeFactors]
  norm_num

theorem radical_sixty : primeRadical 60 = 30 := by
  change (∏ p ∈ (((2 ^ 2) * 3) * 5).primeFactors, p) = 30
  rw [Nat.primeFactors_mul (by decide) (by decide),
    Nat.primeFactors_mul (by decide) (by decide),
    Nat.primeFactors_prime_pow (by decide : (2 : ℕ) ≠ 0) Nat.prime_two,
    (by decide : Nat.Prime 3).primeFactors, (by decide : Nat.Prime 5).primeFactors]
  norm_num

example (W : Submodule ℚ TailSpace) (m : ℕ) (hm : 0 < m) :
    rootKernel W m ≃+ DivisorCoordinates m := rootKernelEquiv W hm

example (W : Submodule ℚ TailSpace) (m : ℕ) (hm : 0 < m)
    (x : preimage W) (y : RootFiber W m x) :
    RootFiber W m x ≃ DivisorCoordinates m := rootFiberEquiv W hm x y

example (W : Submodule ℚ TailSpace) (m : ℕ) (hm : 0 < m)
    (x : preimage W) (y : RootFiber W m x) (z : DivisorCoordinates m) :
    ((rootFiberEquiv W hm x y).symm z).val.val = y.val.val + coordinateExtension m z :=
  rootFiberEquiv_symm_apply W hm x y z

example (W : Submodule ℚ TailSpace) (m : ℕ) (hm : 0 < m) (x : preimage W) :
    Finite (RootFiber W m x) := rootFiber_finite W hm x

example (W : Submodule ℚ TailSpace) (m : ℕ) (hm : 0 < m)
    (x : preimage W) (y : RootFiber W m x) :
    Nat.card (RootFiber W m x) = primeRadical m := rootFiber_card_of_root W hm x y

example (W : Submodule ℚ TailSpace) (x : preimage W) :
    Nat.card (RootFiber W 1 x) = 1 := by
  simpa using rootFiber_card_of_solvable W (by decide : 0 < 1) x ⟨x, one_nsmul x⟩

theorem fourth_zero_has_two_roots (W : Submodule ℚ TailSpace) :
    Nat.card (RootFiber W 4 0) = 2 := by
  simpa only [radical_four] using
    rootFiber_card_of_solvable W (by decide : 0 < 4) 0 ⟨0, nsmul_zero 4⟩

theorem fourth_zero_not_four_roots (W : Submodule ℚ TailSpace) :
    Nat.card (RootFiber W 4 0) ≠ 4 := by
  rw [fourth_zero_has_two_roots]
  decide

example (W : Submodule ℚ TailSpace) : Nat.card (rootKernel W 8) = 2 := by
  simpa only [radical_eight] using rootKernel_card W (by decide : 0 < 8)

example (W : Submodule ℚ TailSpace) : Nat.card (RootFiber W 12 0) = 6 := by
  simpa only [radical_twelve] using
    rootFiber_card_of_solvable W (by decide : 0 < 12) 0 ⟨0, nsmul_zero 12⟩

example (W : Submodule ℚ TailSpace) : Nat.card (RootFiber W 18 0) = 6 := by
  simpa only [radical_eighteen] using
    rootFiber_card_of_solvable W (by decide : 0 < 18) 0 ⟨0, nsmul_zero 18⟩

example (W : Submodule ℚ TailSpace) : Nat.card (RootFiber W 60 0) = 30 := by
  simpa only [radical_sixty] using
    rootFiber_card_of_solvable W (by decide : 0 < 60) 0 ⟨0, nsmul_zero 60⟩

example (W : Submodule ℚ TailSpace) : multiples W 12 = multiples W 6 := by
  simpa only [radical_twelve] using multiples_eq_radical W (by decide : 0 < 12)

example (W : Submodule ℚ TailSpace) : multiples W 60 = multiples W 30 := by
  simpa only [radical_sixty] using multiples_eq_radical W (by decide : 0 < 60)

example (W : Submodule ℚ TailSpace) : (preimage W ⧸ multiples W 12) ≃+ ZMod 6 := by
  exact (cyclicIntegerQuotientEquiv W (by decide : 0 < 12)).trans
    (ZMod.ringEquivCongr radical_twelve).toAddEquiv

example (W : Submodule ℚ TailSpace) : (preimage W ⧸ multiples W 4) ≃+ ZMod 2 := by
  exact (cyclicIntegerQuotientEquiv W (by decide : 0 < 4)).trans
    (ZMod.ringEquivCongr radical_four).toAddEquiv

example (W : Submodule ℚ TailSpace) (m : ℕ) (hm : 0 < m)
    (x : preimage W) (y : RootFiber W m x) :
    RootFiber W m x ≃ ZMod (primeRadical m) := cyclicRootFiberEquiv W hm x y

example (W : Submodule ℚ TailSpace) (m n : ℕ) (hm : 0 < m) (hn : 0 < n)
    (hmn : m ∣ n) (x : preimage W ⧸ multiples W n) :
    cyclicIntegerQuotientEquiv W hm (quotientRestriction W hmn x) =
      ZMod.castHom (primeRadical_dvd_of_dvd hn hmn) (ZMod (primeRadical m))
        (cyclicIntegerQuotientEquiv W hn x) :=
  cyclicIntegerQuotientEquiv_restriction W hm hn hmn x

example (W : Submodule ℚ TailSpace) (m n : ℕ) (hmn : m ∣ n) (x : preimage W) :
    quotientRestriction W hmn (QuotientAddGroup.mk x) = QuotientAddGroup.mk x := rfl

theorem marked_half_empty :
    IsEmpty (RootFiber (selectorLine (pairedSelector (fun _ => false))) 2
      (markedElement (pairedSelector (fun _ => false)))) :=
  rootFiber_isEmpty _ _ _ RealizationBoundariesTests.no_half

theorem marked_half_count_zero :
    Nat.card (RootFiber (selectorLine (pairedSelector (fun _ => false))) 2
      (markedElement (pairedSelector (fun _ => false)))) = 0 := by
  let := marked_half_empty
  exact Nat.card_of_isEmpty

theorem marked_third_count_three :
    Nat.card (RootFiber (selectorLine (pairedSelector (fun _ => false))) 3
      (markedElement (pairedSelector (fun _ => false)))) = 3 := by
  exact (rootFiber_card_of_solvable _ (by decide : 0 < 3) _
    RealizationBoundariesTests.third_root).trans (primeRadical_prime (by decide : Nat.Prime 3))

example (W : Submodule ℚ TailSpace) (m : ℕ) (hm : 0 < m) (x : preimage W)
    (h : ∀ p : Prime, p.val ∣ m → x.val p = 0) :
    m • (normalizedRoot W hm x h).val = x := (normalizedRoot W hm x h).property

example (W : Submodule ℚ TailSpace) (m : ℕ) (hm : 0 < m) (x : preimage W)
    (h : ∀ p : Prime, p.val ∣ m → x.val p = 0)
    (y : RootFiber W m x) (hy : ∀ p : Prime, p.val ∣ m → y.val.val p = 0) :
    y = normalizedRoot W hm x h := normalizedRoot_unique W hm x h y hy

theorem fourth_root_not_unique (W : Submodule ℚ TailSpace) :
    ¬ ∃! y : preimage W, (4 : ℕ) • y = 0 := by
  rw [unique_root_iff_one W (by decide : 0 < 4) 0 ⟨0, nsmul_zero 4⟩]
  decide

example (W : Submodule ℚ TailSpace) : Infinite (RootFiber W 0 0) := zeroRootFiber_infinite W

example (W : Submodule ℚ TailSpace) :
    Nat.card (RootFiber W 0 0) = 0 ∧ Nonempty (RootFiber W 0 0) :=
  ⟨zeroRootFiber_card W, zeroRootFiber_nonempty W⟩

example (W : Submodule ℚ TailSpace) (x : preimage W) (hx : x ≠ 0) :
    IsEmpty (RootFiber W 0 x) := zeroRootFiber_isEmpty_of_ne_zero W x hx

example (W : Submodule ℚ TailSpace) (F : Type*) [AddGroup F] [Finite F]
    (f : preimage W →+ F) (hf : Function.Surjective f) :
    f.ker = multiples W (Nat.card F) := finite_surjection_ker W F f hf

example (W : Submodule ℚ TailSpace) (F : Type*) [AddGroup F] [Finite F] :
    (∃ f : preimage W →+ F, Function.Surjective f) ↔
      IsAddCyclic F ∧ Squarefree (Nat.card F) := finite_quotient_exists_iff W F

theorem cyclic_four_not_a_quotient (W : Submodule ℚ TailSpace) :
    ¬ ∃ f : preimage W →+ ZMod 4, Function.Surjective f := by
  intro h
  have hs := ((finite_quotient_exists_iff W (ZMod 4)).mp h).2
  have hcard : Nat.card (ZMod 4) = 4 := by simp [Nat.card_eq_fintype_card, ZMod.card]
  rw [hcard] at hs
  have hu : IsUnit (2 : ℕ) := hs 2 (by decide)
  norm_num at hu

example (W : Submodule ℚ TailSpace) :
    ∃ f : preimage W →+ ZMod 6, Function.Surjective f := by
  apply (finite_quotient_exists_iff W (ZMod 6)).mpr
  constructor
  · infer_instance
  · have he : Nat.card (ZMod 6) = 6 := by simp
    rw [he]
    exact (Nat.squarefree_mul (by decide : Nat.Coprime 2 3)).mpr
      ⟨Nat.prime_two.prime.squarefree, (by decide : Nat.Prime 3).prime.squarefree⟩

example (W : Submodule ℚ TailSpace) :
    ∃ f : preimage W →+ ZMod 1, Function.Surjective f := by
  apply (finite_quotient_exists_iff W (ZMod 1)).mpr
  constructor
  · infer_instance
  · norm_num [Nat.card_eq_fintype_card, ZMod.card]

end RealizationBoundariesRootTests
