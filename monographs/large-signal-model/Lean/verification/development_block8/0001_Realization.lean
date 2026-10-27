import Std

/-! Set-level realization and coherent coordinate transport.
The coefficients are explicitly restricted to the realizable subtype.
This module proves the algebraic part of P1 and the total-map statement of P2.
-/
set_option autoImplicit false

namespace Komorebi.LSM

universe u v w t

/-- An observation archive with a specified left inverse. -/
structure Realization (X : Type u) (C : Type v) where
  analysis : X → C
  synthesis : C → X
  reconstruct : ∀ x, synthesis (analysis x) = x

namespace Realization

variable {X : Type u} {C : Type v} {D : Type w} {E : Type t}

/-- Coefficients fixed by analysis after synthesis are the consistent coefficients. -/
def projector (r : Realization X C) (c : C) : C := r.analysis (r.synthesis c)

def Consistent (r : Realization X C) (c : C) : Prop := ∃ x, r.analysis x = c

def Coeff (r : Realization X C) := {c : C // r.Consistent c}

theorem analysis_injective (r : Realization X C) {x y : X}
    (h : r.analysis x = r.analysis y) : x = y := by
  have hs := congrArg r.synthesis h
  simpa only [r.reconstruct] using hs

theorem projector_idempotent (r : Realization X C) (c : C) :
    r.projector (r.projector c) = r.projector c := by
  simp only [projector, r.reconstruct]

theorem projector_consistent (r : Realization X C) (c : C) :
    r.Consistent (r.projector c) := ⟨r.synthesis c, rfl⟩

theorem projector_fixed_iff (r : Realization X C) (c : C) :
    r.projector c = c ↔ r.Consistent c := by
  constructor
  · intro h
    exact ⟨r.synthesis c, h⟩
  · rintro ⟨x, rfl⟩
    exact congrArg r.analysis (r.reconstruct x)

theorem projector_range (r : Realization X C) (c : C) :
    (∃ d, r.projector d = c) ↔ r.Consistent c := by
  constructor
  · rintro ⟨d, rfl⟩
    exact r.projector_consistent d
  · intro h
    exact ⟨c, (r.projector_fixed_iff c).mpr h⟩

def encode (r : Realization X C) (x : X) : r.Coeff :=
  ⟨r.analysis x, x, rfl⟩

def decode (r : Realization X C) (c : r.Coeff) : X := r.synthesis c.val

@[simp] theorem decode_encode (r : Realization X C) (x : X) :
    r.decode (r.encode x) = x := r.reconstruct x

@[simp] theorem encode_decode (r : Realization X C) (c : r.Coeff) :
    r.encode (r.decode c) = c := by
  apply Subtype.ext
  exact (r.projector_fixed_iff c.val).mpr c.property

/-- `transport a b` is T_ba: from the realizable coefficients of a to b. -/
def transport (a : Realization X C) (b : Realization X D)
    (c : a.Coeff) : b.Coeff := b.encode (a.decode c)

@[simp] theorem transport_self (a : Realization X C) (c : a.Coeff) :
    transport a a c = c := a.encode_decode c

theorem transport_comp (a : Realization X C) (b : Realization X D)
    (d : Realization X E) (c : a.Coeff) :
    transport b d (transport a b c) = transport a d c := by
  simp only [transport, decode_encode]

def realize (a : Realization X C) (F : X → X) (c : a.Coeff) : a.Coeff :=
  a.encode (F (a.decode c))

theorem realize_natural (a : Realization X C) (b : Realization X D)
    (F : X → X) (c : a.Coeff) :
    realize b F (transport a b c) = transport a b (realize a F c) := by
  simp only [realize, transport, decode_encode]

theorem realize_identity (a : Realization X C) (c : a.Coeff) :
    realize a (fun x => x) c = c := a.encode_decode c

theorem realize_composition (a : Realization X C) (F G : X → X) (c : a.Coeff) :
    realize a (fun x => G (F x)) c = realize a G (realize a F c) := by
  simp only [realize, decode_encode]

theorem realize_faithful (a : Realization X C) (F G : X → X)
    (h : ∀ c, realize a F c = realize a G c) : F = G := by
  funext x
  have hx := congrArg a.decode (h (a.encode x))
  simpa only [realize, decode_encode] using hx

end Realization

/-- Every pairwise compatible family on a nonempty collection of charts comes
from exactly one operation on observations. A reference chart is supplied. -/
theorem coherent_family_unique_realization
    {X : Type u} {I : Type v} {C : I → Type w}
    (atlas : (i : I) → Realization X (C i)) (ref : I)
    (G : (i : I) → (atlas i).Coeff → (atlas i).Coeff)
    (coherent : ∀ i j c,
      G j (Realization.transport (atlas i) (atlas j) c) =
      Realization.transport (atlas i) (atlas j) (G i c)) :
    ∃ F : X → X,
      (∀ i c, G i c = Realization.realize (atlas i) F c) ∧
      (∀ H : X → X,
        (∀ i c, G i c = Realization.realize (atlas i) H c) → H = F) := by
  let F : X → X := fun x => (atlas ref).decode (G ref ((atlas ref).encode x))
  have hf : ∀ i c, G i c = Realization.realize (atlas i) F c := by
    intro i c
    have h := coherent ref i ((atlas ref).encode ((atlas i).decode c))
    simpa only [Realization.transport, Realization.decode_encode,
      Realization.encode_decode, Realization.realize, F] using h
  refine ⟨F, hf, ?_⟩
  intro H hh
  apply Realization.realize_faithful (atlas ref)
  intro c
  exact (hh ref c).symm.trans (hf ref c)

end Komorebi.LSM
