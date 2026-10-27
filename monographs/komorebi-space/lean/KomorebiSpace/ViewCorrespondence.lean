import KomorebiSpace.SectionGluing

set_option autoImplicit false

/-!
# Common ambient realizations as section-valued bridge fibers

At the strict set-valued level, taking coherent sections commutes with the
specified fiber of a correspondence span. Existence is not assumed. Matching
local bridge sections give a global bridge under transition-covered gluing.
-/
universe u v w z t i
namespace KomorebiSpace
open CategoryTheory
namespace ViewSystem
variable {V : Type u} [Category.{v} V]
variable {M : ViewSystem.{u,v,w} V} {F : ViewSystem.{u,v,z} V}
variable {G : ViewSystem.{u,v,t} V}

/-- A strict fiber of a specified span at two ambient sections. -/
def GlobalBridge (p : Morphism M F) (q : Morphism M G)
    (a : F.Ambient) (b : G.Ambient) :=
  {s : M.Ambient // p.onAmbient s = a ∧ q.onAmbient s = b}

/-- Each view contains realizations of the prescribed pair in the span. -/
def bridgeSystem (p : Morphism M F) (q : Morphism M G)
    (a : F.Ambient) (b : G.Ambient) : ViewSystem V where
  Obj v := {x : M.Obj v // p.app v x = a.val v ∧ q.app v x = b.val v}
  pull := fun {v w} f x => ⟨M.pull f x.val, by
    constructor
    · calc
        p.app v (M.pull f x.val) = F.pull f (p.app w x.val) := (p.natural f x.val).symm
        _ = F.pull f (a.val w) := congrArg (F.pull f) x.property.1
        _ = a.val v := a.property v w f
    · calc
        q.app v (M.pull f x.val) = G.pull f (q.app w x.val) := (q.natural f x.val).symm
        _ = G.pull f (b.val w) := congrArg (G.pull f) x.property.2
        _ = b.val v := b.property v w f⟩
  pull_id := by intro v x; apply Subtype.ext; exact M.pull_id v x.val
  pull_comp := by intro v w z f g x; apply Subtype.ext; exact M.pull_comp f g x.val

/-- This is the set-level fiber/section equivalence, not a homotopy-fiber theorem. -/
def bridgeEquiv (p : Morphism M F) (q : Morphism M G)
    (a : F.Ambient) (b : G.Ambient) :
    (bridgeSystem p q a b).Ambient ≃ GlobalBridge p q a b where
  toFun := fun x =>
    ⟨⟨fun v => (x.val v).val, by
        intro v w f
        exact congrArg Subtype.val (x.property v w f)⟩, by
      constructor
      · apply Ambient.ext; intro v; exact (x.val v).property.1
      · apply Ambient.ext; intro v; exact (x.val v).property.2⟩
  invFun := fun s =>
    ⟨fun v => ⟨s.val.val v, by
        constructor
        · exact congrArg (fun x : F.Ambient => x.val v) s.property.1
        · exact congrArg (fun x : G.Ambient => x.val v) s.property.2⟩, by
      intro v w f
      apply Subtype.ext
      exact s.val.property v w f⟩
  left_inv := by intro x; apply Ambient.ext; intro v; rfl
  right_inv := by intro s; apply Subtype.ext; apply Ambient.ext; intro v; rfl

@[simp] theorem bridgeEquiv_coordinate (p : Morphism M F) (q : Morphism M G)
    (a : F.Ambient) (b : G.Ambient) (x : (bridgeSystem p q a b).Ambient) (v : V) :
    (bridgeEquiv p q a b x).val.val v = (x.val v).val := rfl

theorem bridge_nonempty_iff (p : Morphism M F) (q : Morphism M G)
    (a : F.Ambient) (b : G.Ambient) :
    Nonempty (GlobalBridge p q a b) ↔ Nonempty (bridgeSystem p q a b).Ambient := by
  constructor
  · rintro ⟨x⟩; exact ⟨(bridgeEquiv p q a b).symm x⟩
  · rintro ⟨x⟩; exact ⟨bridgeEquiv p q a b x⟩

/-- Glue the correspondence objects themselves, with both projected objects fixed. -/
noncomputable def glueBridge (p : Morphism M F) (q : Morphism M G)
    (a : F.Ambient) (b : G.Ambient) {I : Type i} {U : I → Set V}
    (h : TransitionCover U) (m : Matching (bridgeSystem p q a b) U) :
    GlobalBridge p q a b := bridgeEquiv p q a b (m.glue h)

@[simp] theorem glueBridge_left (p : Morphism M F) (q : Morphism M G)
    (a : F.Ambient) (b : G.Ambient) {I : Type i} {U : I → Set V}
    (h : TransitionCover U) (m : Matching (bridgeSystem p q a b) U) :
    p.onAmbient (glueBridge p q a b h m).val = a :=
  (glueBridge p q a b h m).property.1

@[simp] theorem glueBridge_right (p : Morphism M F) (q : Morphism M G)
    (a : F.Ambient) (b : G.Ambient) {I : Type i} {U : I → Set V}
    (h : TransitionCover U) (m : Matching (bridgeSystem p q a b) U) :
    q.onAmbient (glueBridge p q a b h m).val = b :=
  (glueBridge p q a b h m).property.2

/-- Local bridges must form a matching family, not merely exist individually. -/
theorem bridge_exists_iff_matching (p : Morphism M F) (q : Morphism M G)
    (a : F.Ambient) (b : G.Ambient) {I : Type i} (U : I → Set V)
    (h : TransitionCover U) :
    Nonempty (GlobalBridge p q a b) ↔ Nonempty (Matching (bridgeSystem p q a b) U) := by
  constructor
  · rintro ⟨x⟩
    exact ⟨(bridgeSystem p q a b).toMatching U ((bridgeEquiv p q a b).symm x)⟩
  · rintro ⟨m⟩
    exact ⟨glueBridge p q a b h m⟩

/-- A fixed matching family determines its global bridge uniquely. -/
theorem bridge_glue_unique (p : Morphism M F) (q : Morphism M G)
    (a : F.Ambient) (b : G.Ambient) {I : Type i} {U : I → Set V}
    (h : TransitionCover U) (m : Matching (bridgeSystem p q a b) U)
    (z : GlobalBridge p q a b)
    (hz : ∀ j, (bridgeSystem p q a b).restrict (U j)
      ((bridgeEquiv p q a b).symm z) = m.localSection j) :
    z = glueBridge p q a b h m := by
  have he := m.glue_unique h ((bridgeEquiv p q a b).symm z) hz
  have he' := congrArg (bridgeEquiv p q a b) he
  simpa only [Equiv.apply_symm_apply, glueBridge] using he'

end ViewSystem
end KomorebiSpace
