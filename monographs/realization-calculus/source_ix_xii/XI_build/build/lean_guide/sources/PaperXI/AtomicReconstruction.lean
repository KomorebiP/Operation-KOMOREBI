import PaperXI.AtomicMultiset

/-! Paper XI, Theorem 2.5: choice-independent conditional reconstruction.
External interfaces here are exactly (1) existence and intrinsic uniqueness of
indecomposable source displays and (2) existence and uniqueness of irreducible
Langlands quotients of ordered target factors. They do not contain the final
candidate map. Sorting, atomic replacement, descent, and that map are constructed.
The theorem is conditional on these classical interfaces; it does not formalize
the construction/classification of local Weil groups or p-adic representations. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.AtomicReconstruction
open PaperXI.AtomicMultiset

/-- The imported block decomposition, expressed on raw source representatives.
`parameterIso` is the declared isomorphism relation, not equality of displays. -/
structure Decomposition {P : Type*} (parameterIso : Setoid P) (A : Type*) where
  displays : P → List (Block A) → Prop
  exists_display : ∀ p, ∃ xs, displays p xs
  intrinsic : ∀ p q xs ys, parameterIso.r p q →
    displays p xs → displays q ys → xs.Perm ys

variable {P A B T : Type*} {sP : Setoid P}

def rawBlocks (D : Decomposition sP A) (p : P) : Multiset (Block A) :=
  (Classical.choose (D.exists_display p) : List (Block A))

theorem rawBlocks_eq (D : Decomposition sP A) (p : P)
    (xs : List (Block A)) (hxs : D.displays p xs) : rawBlocks D p = xs := by
  apply Multiset.coe_eq_coe.mpr
  exact D.intrinsic p p _ xs (sP.refl p) (Classical.choose_spec (D.exists_display p)) hxs

theorem rawBlocks_iso (D : Decomposition sP A) {p q : P} (h : sP.r p q) :
    rawBlocks D p = rawBlocks D q := by
  apply Multiset.coe_eq_coe.mpr
  exact D.intrinsic p q _ _ h (Classical.choose_spec (D.exists_display p))
    (Classical.choose_spec (D.exists_display q))

/-- The intrinsic multiset is derived from the display theorem and descends to
actual source isomorphism classes. No decomposition map is supplied as a field. -/
def blocks (D : Decomposition sP A) : Quotient sP → Multiset (Block A) :=
  Quotient.lift (rawBlocks D) (fun _ _ h => rawBlocks_iso D h)

theorem blocks_of_display (D : Decomposition sP A) (p : P)
    (xs : List (Block A)) (hxs : D.displays p xs) :
    blocks D (Quotient.mk sP p) = xs := rawBlocks_eq D p xs hxs

/-- The target classical input. T denotes isomorphism classes of irreducible
outputs. `quotient xs t` means t is the irreducible quotient of normalized
induction of the generalized Steinberg factors recorded by xs.
Only Langlands-ordered displays are used. Ties need not be ordered uniquely. -/
structure OrderedQuotient (B T : Type*) where
  precedes : Block B → Block B → Prop
  total : ∀ a b, precedes a b ∨ precedes b a
  transitive : ∀ a b c, precedes a b → precedes b c → precedes a c
  quotient : List (Block B) → T → Prop
  exists_quotient : ∀ xs, xs.Pairwise precedes → ∃ t, quotient xs t
  unique_quotient : ∀ xs ys t u, xs.Pairwise precedes → ys.Pairwise precedes →
    xs.Perm ys → quotient xs t → quotient ys u → t = u

/-- Sort a representative by the declared total preorder. Tied factors are not
forced into a fictitious canonical linear order. `realize_eq` removes this choice. -/
def ordered (L : OrderedQuotient B T) (s : Multiset (Block B)) : List (Block B) := by
  classical
  exact s.toList.mergeSort (fun a b => decide (L.precedes a b))

theorem ordered_pairwise (L : OrderedQuotient B T) (s : Multiset (Block B)) :
    (ordered L s).Pairwise L.precedes := by
  classical
  let : Std.Total L.precedes := ⟨L.total⟩
  let : IsTrans (Block B) L.precedes := ⟨L.transitive⟩
  exact List.pairwise_mergeSort' L.precedes s.toList

theorem ordered_multiset (L : OrderedQuotient B T) (s : Multiset (Block B)) :
    (ordered L s : Multiset (Block B)) = s := by
  classical
  change ((s.toList.mergeSort (fun a b => decide (L.precedes a b))) : Multiset (Block B)) = s
  calc
    _ = (s.toList : Multiset (Block B)) :=
      Multiset.coe_eq_coe.mpr (List.mergeSort_perm _ _)
    _ = s := Multiset.coe_toList s

def realize (L : OrderedQuotient B T) (s : Multiset (Block B)) : T :=
  Classical.choose (L.exists_quotient (ordered L s) (ordered_pairwise L s))

theorem realize_eq (L : OrderedQuotient B T) (s : Multiset (Block B))
    (ys : List (Block B)) (hs : ys.Pairwise L.precedes)
    (hy : (ys : Multiset (Block B)) = s) (t : T) (ht : L.quotient ys t) :
    realize L s = t := by
  exact L.unique_quotient (ordered L s) ys _ t (ordered_pairwise L s) hs
    (Multiset.coe_eq_coe.mp ((ordered_multiset L s).trans hy.symm))
    (Classical.choose_spec (L.exists_quotient (ordered L s) (ordered_pairwise L s))) ht

/-- Any valid ordering, including arbitrary choices inside ties, gives the same output. -/
theorem realize_spec (L : OrderedQuotient B T) (s : Multiset (Block B))
    (ys : List (Block B)) (hs : ys.Pairwise L.precedes)
    (hy : (ys : Multiset (Block B)) = s) : L.quotient ys (realize L s) := by
  obtain ⟨t, ht⟩ := L.exists_quotient ys hs
  rw [realize_eq L s ys hs hy t ht]
  exact ht

/-- The candidate is constructed, rather than included among the external inputs. -/
def candidate (f : A → B) (D : Decomposition sP A) (L : OrderedQuotient B T) :
    Quotient sP → T := fun p => realize L (extend f (blocks D p))

/-- Operational specification of Theorem 2.5, for all source displays and all
valid target orderings of the mapped blocks. -/
def Reconstructs (f : A → B) (D : Decomposition sP A) (L : OrderedQuotient B T)
    (F : Quotient sP → T) : Prop :=
  ∀ (p : P) (xs : List (Block A)) (ys : List (Block B)), D.displays p xs → ys.Pairwise L.precedes →
    (ys : Multiset (Block B)) = extend f (xs : Multiset (Block A)) →
      L.quotient ys (F (Quotient.mk sP p))

theorem candidate_spec (f : A → B) (D : Decomposition sP A)
    (L : OrderedQuotient B T) : Reconstructs f D L (candidate f D L) := by
  intro p xs ys hd hs hy
  apply realize_spec L _ ys hs
  simpa only [blocks_of_display D p xs hd] using hy

/-- Evaluation against a supplied decomposition and quotient witness. -/
theorem candidate_eq (f : A → B) (D : Decomposition sP A) (L : OrderedQuotient B T)
    (p : P) (xs : List (Block A)) (ys : List (Block B))
    (hd : D.displays p xs) (hs : ys.Pairwise L.precedes)
    (hy : (ys : Multiset (Block B)) = extend f (xs : Multiset (Block A)))
    (t : T) (ht : L.quotient ys t) : candidate f D L (Quotient.mk sP p) = t := by
  apply realize_eq L _ ys hs _ t ht
  simpa only [blocks_of_display D p xs hd] using hy

/-- Uniqueness is derived from the pointwise classical quotient theorem. -/
theorem candidate_unique (f : A → B) (D : Decomposition sP A) (L : OrderedQuotient B T)
    (F : Quotient sP → T) (hF : Reconstructs f D L F) : F = candidate f D L := by
  funext p
  refine Quotient.inductionOn p ?_
  intro p
  obtain ⟨xs, hd⟩ := D.exists_display p
  let s := extend f (xs : Multiset (Block A))
  exact (candidate_eq f D L p xs (ordered L s) hd (ordered_pairwise L s)
    (ordered_multiset L s) _ (hF p xs _ hd (ordered_pairwise L s)
      (ordered_multiset L s))).symm

/-- Source-facing formal atomic reconstruction. It constructs a unique candidate,
not a bijection, and does not prove local-factor identities. -/
theorem formal_atomic_reconstruction (f : A → B) (D : Decomposition sP A)
    (L : OrderedQuotient B T) : ∃! F : Quotient sP → T, Reconstructs f D L F := by
  exact ⟨candidate f D L, candidate_spec f D L, fun F hF => candidate_unique f D L F hF⟩

/-- Changing the raw parameter representative cannot change the output class. -/
theorem candidate_isomorphism (f : A → B) (D : Decomposition sP A)
    (L : OrderedQuotient B T) {p q : P} (h : sP.r p q) :
    candidate f D L (Quotient.mk sP p) = candidate f D L (Quotient.mk sP q) := by
  exact congrArg (candidate f D L) (Quotient.sound h)

end PaperXI.AtomicReconstruction
