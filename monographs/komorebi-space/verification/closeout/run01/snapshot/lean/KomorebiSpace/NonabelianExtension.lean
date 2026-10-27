import KomorebiSpace.CocycleGaugeGroupoid

set_option autoImplicit false

/-!
# A nonabelian relative obstruction to extending a twisted section

A raw extension normalizes a fixed cocycle. Its orbit under gauge changes
which equal identity on the prescribed domain is independent of the raw
extension. Being in the neutral orbit is equivalent to actual extension.
No abelian quotient-group structure or decision procedure is asserted.
-/
universe u v w
namespace KomorebiSpace
open CategoryTheory
namespace GroupViewSystem
variable {V : Type u} [Category.{v} V]
variable {G : V → Type w} [∀ a, Group (G a)]
variable (F : GroupViewSystem V G)

/-- Normalize the transition labels by a raw family of local trivializations. -/
def normalize (c : F.Cocycle) (q : ∀ v, G v) : F.Cocycle := F.gauge q⁻¹ c

@[simp] theorem normalize_edge (c : F.Cocycle) (q : ∀ v, G v)
    {v w : V} (f : v ⟶ w) :
    (F.normalize c q).edge f = (q v)⁻¹ * c.edge f * F.pull f (q w) := by
  simp [normalize]

theorem normalize_trivial_iff (c : F.Cocycle) (q : ∀ v, G v) :
    F.normalize c q = F.trivial ↔
      ∀ v w (f : v ⟶ w), c.edge f * F.pull f (q w) = q v := by
  simpa [normalize] using F.flatten_iff_section q⁻¹ c

/-- Raw normalization changes by an allowed gauge when observations agree. -/
theorem normalization_independent (c : F.Cocycle) (U : Set V)
    (q t : ∀ v, G v) (h : ∀ v : U, q v.val = t v.val) :
    F.orbitClass U (F.normalize c q) = F.orbitClass U (F.normalize c t) := by
  rw [F.orbitClass_eq_iff]
  let a : F.basedGauge U := ⟨t⁻¹ * q, by
    intro v
    change (t v.val)⁻¹ * q v.val = 1
    rw [h v]; group⟩
  refine ⟨a, ?_⟩
  change F.gauge (t⁻¹ * q) (F.gauge q⁻¹ c) = F.gauge t⁻¹ c
  rw [F.gauge_mul]
  have he : (t⁻¹ * q) * q⁻¹ = t⁻¹ := by group
  rw [he]

/-- The orbit condition is equivalent to solving the original equations with fixed data. -/
theorem normalized_class_neutral_iff (c : F.Cocycle) (U : Set V) (q : ∀ v, G v) :
    F.orbitClass U (F.normalize c q) = F.neutralClass U ↔
      ∃ x : (F.twistedViews c).Ambient, ∀ v : U, x.val v.val = q v.val := by
  change F.orbitClass U (F.normalize c q) = F.orbitClass U F.trivial ↔ _
  rw [F.orbitClass_eq_iff]
  constructor
  · rintro ⟨a, ha⟩
    have he : F.gauge (a.val * q⁻¹) c = F.trivial := by
      rw [← F.gauge_mul]
      exact ha
    have hx := (F.flatten_iff_section (a.val * q⁻¹) c).mp he
    refine ⟨⟨fun v => ((a.val * q⁻¹) v)⁻¹, hx⟩, ?_⟩
    intro v
    change (a.val v.val * (q v.val)⁻¹)⁻¹ = q v.val
    rw [a.property v]
    simp
  · rintro ⟨x, hx⟩
    let a : F.basedGauge U := ⟨x.val⁻¹ * q, by
      intro v
      change (x.val v.val)⁻¹ * q v.val = 1
      rw [hx v]; group⟩
    refine ⟨a, ?_⟩
    change F.gauge (x.val⁻¹ * q) (F.gauge q⁻¹ c) = F.trivial
    rw [F.gauge_mul]
    have he : (x.val⁻¹ * q) * q⁻¹ = x.val⁻¹ := by group
    rw [he]
    apply (F.normalize_trivial_iff c x.val).mpr
    exact x.property

/-- Identity outside the prescribed domain is one raw extension, usually noncoherent. -/
noncomputable def rawSection (c : F.Cocycle) (U : Set V)
    (s : (F.twistedViews c).Partial U) : ∀ v, G v := by
  classical
  exact fun v => if h : v ∈ U then s.val ⟨v, h⟩ else 1

@[simp] theorem rawSection_prescribed (c : F.Cocycle) (U : Set V)
    (s : (F.twistedViews c).Partial U) (v : U) :
    F.rawSection c U s v.val = s.val v := by
  classical
  simp [rawSection, v.property]

noncomputable def extensionOrbit (c : F.Cocycle) (U : Set V)
    (s : (F.twistedViews c).Partial U) : F.Orbit U :=
  F.orbitClass U (F.normalize c (F.rawSection c U s))

/-- Actual extension is equivalent to neutrality of the independently defined orbit. -/
theorem extensionOrbit_neutral_iff (c : F.Cocycle) (U : Set V)
    (s : (F.twistedViews c).Partial U) :
    F.extensionOrbit c U s = F.neutralClass U ↔
      Nonempty ((F.twistedViews c).Extensions U s) := by
  change F.orbitClass U (F.normalize c (F.rawSection c U s)) = F.neutralClass U ↔ _
  rw [F.normalized_class_neutral_iff]
  constructor
  · rintro ⟨x, hx⟩
    refine ⟨⟨x, ?_⟩⟩
    apply ViewSystem.Partial.ext
    intro v
    exact (hx v).trans (F.rawSection_prescribed c U s v)
  · rintro ⟨⟨x, hx⟩⟩
    refine ⟨x, ?_⟩
    intro v
    have he := congrArg (fun t : (F.twistedViews c).Partial U => t.val v) hx
    exact he.trans (F.rawSection_prescribed c U s v).symm

theorem extensionOrbit_independent (c : F.Cocycle) (U : Set V)
    (s : (F.twistedViews c).Partial U) (q : ∀ v, G v)
    (hq : ∀ v : U, q v.val = s.val v) :
    F.orbitClass U (F.normalize c q) = F.extensionOrbit c U s := by
  apply F.normalization_independent
  intro v
  exact (hq v).trans (F.rawSection_prescribed c U s v).symm

/-- Coherence of the prescribed partial section trivializes internal transition labels. -/
theorem normalized_internal_edge (c : F.Cocycle) (U : Set V)
    (s : (F.twistedViews c).Partial U) (v w : U) (f : v.val ⟶ w.val) :
    (F.normalize c (F.rawSection c U s)).edge f = 1 := by
  rw [F.normalize_edge, F.rawSection_prescribed, F.rawSection_prescribed]
  have hs := s.property v w f
  change c.edge f * F.pull f (s.val w) = s.val v at hs
  calc
    _ = (s.val v)⁻¹ * (c.edge f * F.pull f (s.val w)) := by group
    _ = 1 := by rw [hs]; group

end GroupViewSystem
end KomorebiSpace
