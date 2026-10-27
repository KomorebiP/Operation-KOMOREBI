import PaperXI.CocycleCommutator

/-! The explicit quotient of normalized cocycles by normalized scalar coboundaries.
This is a concrete cohomological-class model; no identification with a separate
Mathlib group-cohomology construction is assumed. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CocycleClass

open CocycleCommutator
variable {A B C : Type*} [CommGroup A] [CommGroup B] [CommGroup C]

/-- Equality of actual cocycle coefficients determines the cocycle. -/
theorem cocycle_ext {c d : Cocycle A C} (h : ∀ a b, c.coeff a b = d.coeff a b) : c = d := by
  cases c
  cases d
  congr
  funext a b
  exact h a b

@[simp] theorem rescale_one (c : Cocycle A C) : rescale c (fun _ => 1) = c := by
  apply cocycle_ext
  intro a b
  simp [rescale]

/-- Successive scalar changes multiply their actual cochains. -/
theorem rescale_trans (c : Cocycle A C) (s t : A → C) :
    rescale (rescale c s) t = rescale c (fun a => s a * t a) := by
  apply cocycle_ext
  intro a b
  simp [rescale, div_eq_mul_inv, mul_assoc, mul_comm, mul_left_comm]

/-- Normalized cocycles, retaining the actual multiplication coefficients. -/
abbrev NormalizedCocycle (A C : Type*) [CommGroup A] [CommGroup C] :=
  {c : Cocycle A C // Normalized c}

/-- An explicit normalized cochain relates the second cocycle to the first. -/
def Related (c d : NormalizedCocycle A C) : Prop :=
  ∃ s : A → C, s 1 = 1 ∧ d.val = rescale c.val s

theorem related_refl (c : NormalizedCocycle A C) : Related c c :=
  ⟨fun _ => 1, rfl, (rescale_one c.val).symm⟩

theorem related_symm {c d : NormalizedCocycle A C} (h : Related c d) : Related d c := by
  obtain ⟨s, hs, hd⟩ := h
  refine ⟨fun a => (s a)⁻¹, by simp [hs], ?_⟩
  rw [hd, rescale_trans]
  simp

theorem related_trans {c d e : NormalizedCocycle A C}
    (hcd : Related c d) (hde : Related d e) : Related c e := by
  obtain ⟨s, hs, hd⟩ := hcd
  obtain ⟨t, ht, he⟩ := hde
  refine ⟨fun a => s a * t a, by simp [hs, ht], ?_⟩
  rw [he, hd, rescale_trans]

/-- The equivalence relation is proved directly from scalar changes. -/
def coboundarySetoid (A C : Type*) [CommGroup A] [CommGroup C] :
    Setoid (NormalizedCocycle A C) where
  r := Related
  iseqv := ⟨related_refl, related_symm, related_trans⟩

/-- The concrete normalized-cocycle class space. -/
def Class (A C : Type*) [CommGroup A] [CommGroup C] := Quotient (coboundarySetoid A C)

/-- The class of the actual normalized cocycle. -/
def of (c : Cocycle A C) (hc : Normalized c) : Class A C :=
  Quotient.mk (coboundarySetoid A C) ⟨c, hc⟩

/-- Class equality is exactly the existence of an explicit normalized coboundary. -/
theorem of_eq_iff (c d : Cocycle A C) (hc : Normalized c) (hd : Normalized d) :
    of c hc = of d hd ↔ ∃ s : A → C, s 1 = 1 ∧ d = rescale c s :=
  Quotient.eq

/-- A proved rescaling identity gives equality of the actual cocycle classes. -/
theorem of_eq_of_rescale (c d : Cocycle A C) (hc : Normalized c) (hd : Normalized d)
    (s : A → C) (hs : s 1 = 1) (h : d = rescale c s) : of c hc = of d hd :=
  (of_eq_iff c d hc hd).mpr ⟨s, hs, h⟩

@[simp] theorem of_rescale (c : Cocycle A C) (hc : Normalized c)
    (s : A → C) (hs : s 1 = 1) :
    of (rescale c s) (normalized_rescale c hc s hs) = of c hc :=
  (of_eq_of_rescale c (rescale c s) hc (normalized_rescale c hc s hs) s hs rfl).symm

/-- The alternating commutator descends to actual cocycle classes. -/
def commutator : Class A C → A → A → C :=
  Quotient.lift (fun c : NormalizedCocycle A C => CocycleCommutator.commutator c.val)
    (by
      intro c d h
      obtain ⟨s, _, hd⟩ := h
      rw [hd]
      funext a b
      exact (commutator_rescale c.val s a b).symm)

@[simp] theorem commutator_of (c : Cocycle A C) (hc : Normalized c) (a b : A) :
    commutator (of c hc) a b = CocycleCommutator.commutator c a b := rfl

/-- The radical subgroup is independent of the chosen representative. -/
def radical : Class A C → Subgroup A :=
  Quotient.lift (fun c : NormalizedCocycle A C => CocycleCommutator.radical c.val)
    (by
      intro c d h
      obtain ⟨s, _, hd⟩ := h
      rw [hd]
      exact (radical_rescale c.val s).symm)

@[simp] theorem radical_of (c : Cocycle A C) (hc : Normalized c) :
    radical (of c hc) = CocycleCommutator.radical c := rfl

/-- Pull back the actual coefficient function along an index-group homomorphism. -/
def pullbackCocycle (f : B →* A) (c : Cocycle A C) : Cocycle B C where
  coeff a b := c.coeff (f a) (f b)
  assoc a b d := by simpa using c.assoc (f a) (f b) (f d)

theorem normalized_pullback (f : B →* A) (c : Cocycle A C) (hc : Normalized c) :
    Normalized (pullbackCocycle f c) := by
  constructor <;> intro a <;> simp [pullbackCocycle, hc.1, hc.2]

theorem pullback_rescale (f : B →* A) (c : Cocycle A C) (s : A → C) :
    pullbackCocycle f (rescale c s) = rescale (pullbackCocycle f c) (s ∘ f) := by
  apply cocycle_ext
  intro a b
  simp [pullbackCocycle, rescale]

/-- The induced contravariant map on actual normalized-cocycle classes. -/
def pullback (f : B →* A) : Class A C → Class B C :=
  Quotient.map (fun c : NormalizedCocycle A C =>
    ⟨pullbackCocycle f c.val, normalized_pullback f c.val c.property⟩)
    (by
      intro c d h
      obtain ⟨s, hs, hd⟩ := h
      refine ⟨s ∘ f, by simpa using hs, ?_⟩
      change pullbackCocycle f d.val = _
      rw [hd, pullback_rescale])

@[simp] theorem pullback_of (f : B →* A) (c : Cocycle A C) (hc : Normalized c) :
    pullback f (of c hc) = of (pullbackCocycle f c) (normalized_pullback f c hc) := rfl

/-- Relabeling the index group by a genuine isomorphism induces a class equivalence. -/
def congrEquiv (e : A ≃* B) : Class A C ≃ Class B C where
  toFun := pullback e.symm.toMonoidHom
  invFun := pullback e.toMonoidHom
  left_inv q := by
    refine Quotient.inductionOn q ?_
    intro c
    change of (pullbackCocycle e.toMonoidHom (pullbackCocycle e.symm.toMonoidHom c.val)) _ = of c.val c.property
    have h : pullbackCocycle e.toMonoidHom (pullbackCocycle e.symm.toMonoidHom c.val) = c.val := by
      apply cocycle_ext
      intro a b
      simp [pullbackCocycle]
    apply Quotient.sound
    exact ⟨fun _ => 1, rfl, by simpa using h.symm⟩
  right_inv q := by
    refine Quotient.inductionOn q ?_
    intro c
    change of (pullbackCocycle e.symm.toMonoidHom (pullbackCocycle e.toMonoidHom c.val)) _ = of c.val c.property
    have h : pullbackCocycle e.symm.toMonoidHom (pullbackCocycle e.toMonoidHom c.val) = c.val := by
      apply cocycle_ext
      intro a b
      simp [pullbackCocycle]
    apply Quotient.sound
    exact ⟨fun _ => 1, rfl, by simpa using h.symm⟩

@[simp] theorem congrEquiv_of (e : A ≃* B) (c : Cocycle A C) (hc : Normalized c) :
    congrEquiv e (of c hc) =
      of (pullbackCocycle e.symm.toMonoidHom c) (normalized_pullback e.symm.toMonoidHom c hc) := rfl

end PaperXI.CocycleClass
