import Mathlib.Data.Set.Lattice.Indexed

/-!
The proof field induces a contravariant system of local Horn models.
Support coverage is coverage of whole justifications, not pairwise edges.
-/
namespace ProofPath

structure Field (ι J : Type*) where
  leaf : Set ι
  premises : J → Set ι
  conclusion : J → ι
  certified : J → Prop

namespace Field
variable {ι J I : Type*} (F : Field ι J)

def support (j : J) : Set ι := insert (F.conclusion j) (F.premises j)

inductive Derives : ι → Prop where
  | leaf {v} : v ∈ F.leaf → Derives v
  | step (j) : F.certified j → (∀ v, v ∈ F.premises j → Derives v) →
      Derives (F.conclusion j)

def Model (x : ι → Prop) : Prop :=
  (∀ v, v ∈ F.leaf → x v) ∧
  (∀ j, F.certified j → (∀ v, v ∈ F.premises j → x v) → x (F.conclusion j))

theorem derives_sound {x : ι → Prop} (hx : F.Model x) {v : ι}
    (h : F.Derives v) : x v := by
  induction h with
  | leaf h => exact hx.1 _ h
  | step j hc _ ih => exact hx.2 j hc ih

theorem derives_model : F.Model F.Derives :=
  ⟨fun _ h => Derives.leaf h, fun j hc hp => Derives.step j hc hp⟩

theorem derives_iff_all_models (v : ι) :
    F.Derives v ↔ ∀ x, F.Model x → x v := by
  exact ⟨fun h _ hx => F.derives_sound hx h, fun h => h F.Derives F.derives_model⟩

theorem nonderivable_countermodel {v : ι} (h : ¬ F.Derives v) :
    ∃ x, F.Model x ∧ ¬ x v :=
  ⟨F.Derives, F.derives_model, h⟩

/-- New exploratory rules cannot destroy an old certified derivation. -/
theorem derives_mono (G : Field ι J)
    (hleaf : F.leaf ⊆ G.leaf)
    (hpre : ∀ j, G.premises j = F.premises j)
    (hcon : ∀ j, G.conclusion j = F.conclusion j)
    (hcert : ∀ j, F.certified j → G.certified j)
    {v : ι} (hv : F.Derives v) : G.Derives v := by
  induction hv with
  | leaf h => exact Derives.leaf (hleaf h)
  | step j hc _ ih =>
    rw [← hcon j]
    exact Derives.step j (hcert j hc) (by simpa [hpre j] using ih)

/-- Outside values are normalized to false, so there are no hidden coordinates. -/
structure Local (U : Set ι) where
  val : ι → Prop
  outside : ∀ v, v ∉ U → ¬ val v
  leaves : ∀ v, v ∈ F.leaf → v ∈ U → val v
  rules : ∀ j, F.certified j → F.support j ⊆ U →
    (∀ v, v ∈ F.premises j → val v) → val (F.conclusion j)

@[ext] theorem Local.ext {U : Set ι} {a b : F.Local U}
    (h : ∀ v, a.val v ↔ b.val v) : a = b := by
  cases a with
  | mk a ao al ar =>
    cases b with
    | mk b bo bl br =>
      have hab : a = b := funext fun v => propext (h v)
      cases hab
      rfl

def restrict {U V : Set ι} (hUV : U ⊆ V) (x : F.Local V) : F.Local U where
  val v := v ∈ U ∧ x.val v
  outside _ hv h := hv h.1
  leaves v hv hu := ⟨hu, x.leaves v hv (hUV hu)⟩
  rules j hc hs hp :=
    ⟨hs (Set.mem_insert _ _),
      x.rules j hc (fun _ h => hUV (hs h)) (fun v hv => (hp v hv).2)⟩

theorem restrict_identity {U : Set ι} (x : F.Local U) :
    F.restrict (fun _ h => h) x = x := by
  apply Local.ext
  intro v
  constructor
  · exact fun h => h.2
  · intro h
    exact ⟨by by_contra hn; exact x.outside v hn h, h⟩

theorem restrict_composition {U V W : Set ι} (hUV : U ⊆ V) (hVW : V ⊆ W)
    (x : F.Local W) :
    F.restrict hUV (F.restrict hVW x) = F.restrict (fun _ h => hVW (hUV h)) x := by
  apply Local.ext
  intro v
  exact ⟨fun h => ⟨h.1, h.2.2⟩, fun h => ⟨h.1, hUV h.1, h.2⟩⟩

def localize (x : ι → Prop) (hx : F.Model x) (U : Set ι) : F.Local U where
  val v := v ∈ U ∧ x v
  outside _ hv h := hv h.1
  leaves _ hl hu := ⟨hu, hx.1 _ hl⟩
  rules j hc hs hp :=
    ⟨hs (Set.mem_insert _ _), hx.2 j hc (fun v hv => (hp v hv).2)⟩

def Matching (U : I → Set ι) (s : ∀ i, F.Local (U i)) : Prop :=
  ∀ i j v, v ∈ U i → v ∈ U j → ((s i).val v ↔ (s j).val v)

def gluedValue (U : I → Set ι) (s : ∀ i, F.Local (U i)) (v : ι) : Prop :=
  ∃ i, v ∈ U i ∧ (s i).val v

theorem glued_agrees (U : I → Set ι) (s : ∀ i, F.Local (U i))
    (hm : F.Matching U s) (i : I) {v : ι} (hv : v ∈ U i) :
    F.gluedValue U s v ↔ (s i).val v := by
  constructor
  · rintro ⟨j, hj, hs⟩
    exact (hm j i v hj hv).mp hs
  · exact fun h => ⟨i, hv, h⟩

theorem support_cover_gluing (U : I → Set ι) (s : ∀ i, F.Local (U i))
    (hcov : ∀ v, ∃ i, v ∈ U i)
    (hsup : ∀ j, F.certified j → ∃ i, F.support j ⊆ U i)
    (hm : F.Matching U s) :
    ∃! x : ι → Prop, F.Model x ∧
      ∀ i v, v ∈ U i → (x v ↔ (s i).val v) := by
  have agree := F.glued_agrees U s hm
  refine ⟨F.gluedValue U s, ⟨?_, ?_⟩, ?_⟩
  · constructor
    · intro v hl
      obtain ⟨i, hi⟩ := hcov v
      exact ⟨i, hi, (s i).leaves v hl hi⟩
    · intro j hc hp
      obtain ⟨i, hi⟩ := hsup j hc
      have hcon : F.conclusion j ∈ U i := hi (Set.mem_insert _ _)
      apply (agree i hcon).mpr
      apply (s i).rules j hc hi
      intro v hv
      exact (agree i (hi (Set.mem_insert_of_mem _ hv))).mp (hp v hv)
  · intro i v hv
    exact agree i hv
  · intro x hx
    apply funext
    intro v
    obtain ⟨i, hi⟩ := hcov v
    exact propext ((hx.2 i v hi).trans (agree i hi).symm)

/-- The intended truth interpretation remains an explicit, checkable contract. -/
theorem semantic_soundness (meaning : ι → Prop)
    (leaves_true : ∀ v, v ∈ F.leaf → meaning v)
    (rules_sound : ∀ j, F.certified j →
      (∀ v, v ∈ F.premises j → meaning v) → meaning (F.conclusion j))
    {v : ι} (hv : F.Derives v) : meaning v :=
  F.derives_sound ⟨leaves_true, rules_sound⟩ hv

end Field
end ProofPath
