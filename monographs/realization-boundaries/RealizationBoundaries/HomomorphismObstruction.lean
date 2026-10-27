import RealizationBoundaries.SelectorClassification

/-!
# The torsion-image obstruction for arbitrary group homomorphisms

This block obtains the structural obstruction directly from root preservation.
It does not presuppose the still-separate full diagonal homomorphism formula.
-/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace RealizationBoundaries

/-- Monograph Corollary 7.6: selectors with infinitely many disagreements force
all images of any additive homomorphism to belong to the actual subgroup D. -/
theorem hom_image_finiteSupport (a b : ℕ → Bool)
    (h : {n : ℕ | a n ≠ b n}.Infinite) (f : pairedGroup a →+ pairedGroup b)
    (x : pairedGroup a) : (f x).val ∈ finiteSupport := by
  by_contra hx
  exact h (finite_disagreement_of_nontorsion_image a b f x hx)

/-- The obstruction is expressed intrinsically as an actual positive annihilator
for every image element, not merely as a coordinate-support assertion. -/
theorem hom_image_torsion (a b : ℕ → Bool)
    (h : {n : ℕ | a n ≠ b n}.Infinite) (f : pairedGroup a →+ pairedGroup b)
    (x : pairedGroup a) : ∃ m : ℕ, 0 < m ∧ m • f x = 0 :=
  (preimage_torsion_iff (selectorLine (pairedSelector b)) (f x)).mpr
    (hom_image_finiteSupport a b h f x)

/-- Canonical factorization of every such homomorphism through D. -/
def torsionFactor (a b : ℕ → Bool) (h : {n : ℕ | a n ≠ b n}.Infinite)
    (f : pairedGroup a →+ pairedGroup b) : pairedGroup a →+ finiteSupport where
  toFun x := ⟨(f x).val, hom_image_finiteSupport a b h f x⟩
  map_zero' := by
    apply Subtype.ext
    exact congrArg (fun y : pairedGroup b => y.val) (map_zero f)
  map_add' x y := by
    apply Subtype.ext
    exact congrArg (fun z : pairedGroup b => z.val) (map_add f x y)

@[simp] theorem torsionFactor_val (a b : ℕ → Bool)
    (h : {n : ℕ | a n ≠ b n}.Infinite) (f : pairedGroup a →+ pairedGroup b)
    (x : pairedGroup a) : (torsionFactor a b h f x).val = (f x).val := rfl

/-- The factorization commutes with the original embeddings in the prime product. -/
theorem torsionFactor_commutes (a b : ℕ → Bool)
    (h : {n : ℕ | a n ≠ b n}.Infinite) (f : pairedGroup a →+ pairedGroup b) :
    finiteSupport.subtype.comp (torsionFactor a b h f) = (pairedGroup b).subtype.comp f := rfl

/-- There is no freedom in the D-valued factor once the original map is fixed. -/
theorem torsionFactor_unique (a b : ℕ → Bool)
    (h : {n : ℕ | a n ≠ b n}.Infinite) (f : pairedGroup a →+ pairedGroup b)
    (g : pairedGroup a →+ finiteSupport)
    (hg : finiteSupport.subtype.comp g = (pairedGroup b).subtype.comp f) :
    g = torsionFactor a b h f := by
  apply AddMonoidHom.ext
  intro x
  apply Subtype.ext
  exact DFunLike.congr_fun hg x

/-- Infinite selector disagreement forbids embeddings of the original groups. -/
theorem no_injective_hom_of_infinite_disagreement (a b : ℕ → Bool)
    (h : {n : ℕ | a n ≠ b n}.Infinite) (f : pairedGroup a →+ pairedGroup b) :
    ¬ Function.Injective f := by
  intro hi
  let x : pairedGroup a := markedElement (pairedSelector a)
  have hx : x.val ∉ finiteSupport := markedElement_not_finiteSupport (pairedSelector_infinite a)
  obtain ⟨m, hm, hmx⟩ := hom_image_torsion a b h f x
  have he : m • x = 0 := hi (by simpa only [map_nsmul, map_zero] using hmx)
  exact hx ((preimage_torsion_iff (selectorLine (pairedSelector a)) x).mp ⟨m, hm, he⟩)

/-- Infinite selector disagreement also forbids surjections. -/
theorem no_surjective_hom_of_infinite_disagreement (a b : ℕ → Bool)
    (h : {n : ℕ | a n ≠ b n}.Infinite) (f : pairedGroup a →+ pairedGroup b) :
    ¬ Function.Surjective f := by
  intro hs
  let y : pairedGroup b := markedElement (pairedSelector b)
  have hy : y.val ∉ finiteSupport := markedElement_not_finiteSupport (pairedSelector_infinite b)
  obtain ⟨x, hx⟩ := hs y
  apply hy
  rw [← hx]
  exact hom_image_finiteSupport a b h f x

/-- For this family embeddings, surjections and isomorphisms have the same existence criterion. -/
theorem pairedGroup_embeds_iff (a b : ℕ → Bool) :
    (∃ f : pairedGroup a →+ pairedGroup b, Function.Injective f) ↔
      {n : ℕ | a n ≠ b n}.Finite := by
  constructor
  · rintro ⟨f, hf⟩
    by_contra h
    exact no_injective_hom_of_infinite_disagreement a b h f hf
  · intro h
    exact ⟨(pairedEquivOfFiniteDisagreement a b h).toAddMonoidHom,
      (pairedEquivOfFiniteDisagreement a b h).injective⟩

theorem pairedGroup_surjects_iff (a b : ℕ → Bool) :
    (∃ f : pairedGroup a →+ pairedGroup b, Function.Surjective f) ↔
      {n : ℕ | a n ≠ b n}.Finite := by
  constructor
  · rintro ⟨f, hf⟩
    by_contra h
    exact no_surjective_hom_of_infinite_disagreement a b h f hf
  · intro h
    exact ⟨(pairedEquivOfFiniteDisagreement a b h).toAddMonoidHom,
      (pairedEquivOfFiniteDisagreement a b h).surjective⟩

end RealizationBoundaries
