import PaperXI.PacketBasis

/-! The actual scalar character on the stabilizer of a nonzero line. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.LineCharacter
open PaperXI.CyclicAction PaperXI.PacketTransport PaperXI.FrobeniusPeriod
open PaperXI.GeneratedIrreducibility PaperXI.TameOrbitTransitivity
variable {G V : Type*} [Group G] [AddCommGroup V] [Module ℂ V]

theorem scalar_unique {v : V} (hv : v ≠ 0) {c d : ℂ} (h : c • v = d • v) : c = d := by
  apply sub_eq_zero.mp
  have hs : (c - d) • v = 0 := by rw [sub_smul, h, sub_self]
  exact (smul_eq_zero.mp hs).resolve_right hv

theorem scalar_ne_zero (π : Representation ℂ G V) {v : V} (hv : v ≠ 0)
    {g : G} {c : ℂ} (hc : π g v = c • v) : c ≠ 0 := by
  intro hz
  rw [hz, zero_smul] at hc
  exact hv ((π.apply_bijective g).injective (hc.trans (map_zero _).symm))

def lineStabilizer (π : Representation ℂ G V) (v : V) : Subgroup G where
  carrier := {g | ∃ c : ℂ, π g v = c • v}
  one_mem' := ⟨1, by simp⟩
  mul_mem' := by
    rintro g h ⟨c, hc⟩ ⟨d, hd⟩
    refine ⟨c * d, ?_⟩
    simp [map_mul, Module.End.mul_apply, hd, hc, smul_smul, mul_comm]
  inv_mem' := by
    rintro g ⟨c, hc⟩
    by_cases hv : v = 0
    · exact ⟨1, by simp [hv]⟩
    · have hc0 := scalar_ne_zero π hv hc
      refine ⟨c⁻¹, ?_⟩
      apply (π.apply_bijective g).injective
      rw [π.self_inv_apply, map_smul, hc, smul_smul, inv_mul_cancel₀ hc0, one_smul]

/-- This group is precisely the stabilizer of the line, not just a set of eigenvalues. -/
theorem mem_iff_preserves_line (π : Representation ℂ G V) (v : V) (g : G) :
    g ∈ lineStabilizer π v ↔
      (Submodule.span ℂ {v}).map (π g) = Submodule.span ℂ {v} := by
  constructor
  · intro hg
    apply le_antisymm
    · apply Submodule.map_le_iff_le_comap.mpr
      apply Submodule.span_le.mpr
      intro w hw
      have heq : w = v := Set.mem_singleton_iff.mp hw
      subst w
      obtain ⟨c, hc⟩ := hg
      change π g v ∈ Submodule.span ℂ {v}
      exact Submodule.mem_span_singleton.mpr ⟨c, hc.symm⟩
    · intro w hw
      have hg' := (lineStabilizer π v).inv_mem hg
      have hle : Submodule.span ℂ {v} ≤ (Submodule.span ℂ {v}).comap (π g⁻¹) := by
        apply Submodule.span_le.mpr
        intro x hx
        have heq : x = v := Set.mem_singleton_iff.mp hx
        subst x
        obtain ⟨c, hc⟩ := hg'
        exact Submodule.mem_span_singleton.mpr ⟨c, hc.symm⟩
      exact ⟨π g⁻¹ w, hle hw, π.self_inv_apply g w⟩
  · intro h
    have hm : π g v ∈ (Submodule.span ℂ {v}).map (π g) :=
      ⟨v, Submodule.subset_span (Set.mem_singleton v), rfl⟩
    rw [h] at hm
    obtain ⟨c, hc⟩ := Submodule.mem_span_singleton.mp hm
    exact ⟨c, hc.symm⟩

def scalar (π : Representation ℂ G V) (v : V) (g : lineStabilizer π v) : ℂ :=
  Classical.choose g.property

theorem scalar_spec (π : Representation ℂ G V) (v : V) (g : lineStabilizer π v) :
    π g v = scalar π v g • v := Classical.choose_spec g.property

/-- The scalar action on a nonzero line is a homomorphism to C units. -/
def character (π : Representation ℂ G V) (v : V) (hv : v ≠ 0) :
    lineStabilizer π v →* ℂˣ where
  toFun g := Units.mk0 (scalar π v g) (scalar_ne_zero π hv (scalar_spec π v g))
  map_one' := by
    apply Units.ext
    change scalar π v 1 = 1
    apply scalar_unique hv
    rw [← scalar_spec]
    simp
  map_mul' g h := by
    apply Units.ext
    change scalar π v (g * h) = scalar π v g * scalar π v h
    apply scalar_unique hv
    rw [← scalar_spec]
    change π ((g : G) * (h : G)) v = _
    simp [map_mul, Module.End.mul_apply, scalar_spec, smul_smul, mul_comm]

theorem character_action (π : Representation ℂ G V) (v : V) (hv : v ≠ 0)
    (g : lineStabilizer π v) : π g v = (character π v hv g : ℂ) • v := scalar_spec π v g

theorem power_action (π : Representation ℂ G V) (φ : G) (n : ℕ) (v : V) :
    (actionEquiv π φ ^ n) v = π (φ ^ n) v := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [pow_succ', pow_succ', map_mul]
    change actionEquiv π φ ((actionEquiv π φ ^ n) v) = π φ (π (φ ^ n) v)
    rw [ih]
    rfl

variable {M : ℕ} [NeZero M]

theorem inertia_mem (π : Representation ℂ G V)
    (ι : Multiplicative (ZMod M) →* G) (j : ZMod M) {v : V}
    (hv : v ∈ packet (tameRestriction π ι) j) (a : ZMod M) :
    ι (Multiplicative.ofAdd a) ∈ lineStabilizer π v :=
  ⟨ZMod.stdAddChar (j * a), hv a⟩

omit [NeZero M] in
theorem return_mem (π : Representation ℂ G V) (φ : G) (q : (ZMod M)ˣ)
    (j : ZMod M) {v : V} {c : ℂ}
    (hclose : (actionEquiv π φ ^ period q j) v = c • v) :
    φ ^ period q j ∈ lineStabilizer π v := by
  refine ⟨c, ?_⟩
  rwa [power_action] at hclose

theorem character_on_inertia (π : Representation ℂ G V)
    (ι : Multiplicative (ZMod M) →* G) (j : ZMod M) {v : V}
    (hv : v ∈ packet (tameRestriction π ι) j) (hv0 : v ≠ 0) (a : ZMod M) :
    (character π v hv0 ⟨ι (Multiplicative.ofAdd a), inertia_mem π ι j hv a⟩ : ℂ) =
      ZMod.stdAddChar (j * a) := by
  apply scalar_unique hv0
  rw [← character_action]
  exact hv a

omit [NeZero M] in
theorem character_on_return (π : Representation ℂ G V) (φ : G) (q : (ZMod M)ˣ)
    (j : ZMod M) {v : V} (hv0 : v ≠ 0) {c : ℂ}
    (hclose : (actionEquiv π φ ^ period q j) v = c • v) :
    (character π v hv0 ⟨φ ^ period q j, return_mem π φ q j hclose⟩ : ℂ) = c := by
  apply scalar_unique hv0
  rw [← character_action]
  change π (φ ^ period q j) v = c • v
  rwa [power_action] at hclose

/-- The line character is defined on the actual stabilizer of the whole packet. -/
theorem packet_stabilizer_iff (π : Representation ℂ G V) [Representation.IsIrreducible π]
    (ι : Multiplicative (ZMod M) →* G) (φ : G) (q : (ZMod M)ˣ)
    (hgen : Submonoid.closure (generators ι φ) = ⊤)
    (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
      ι (Multiplicative.ofAdd (q : ZMod M)))
    (j : ZMod M) {v : V} (hv : v ∈ packet (tameRestriction π ι) j) (hv0 : v ≠ 0)
    {c : ℂ} (hc : c ≠ 0) (hclose : (actionEquiv π φ ^ period q j) v = c • v) (g : G) :
    g ∈ lineStabilizer π v ↔
      (packet (tameRestriction π ι) j).map (π g) = packet (tameRestriction π ι) j := by
  have htop := PaperXI.PacketLines.cycleSpan_eq_top π ι φ q hgen hrel j hv hv0 hc hclose
  have hline := PaperXI.PacketLines.packet_eq_line_of_span_top (tameRestriction π ι)
    (actionEquiv π φ) q (geometric_relation π ι φ q hrel) j hv htop
  rw [hline]
  exact mem_iff_preserves_line π v g

/-- Inertia and the return power generate a subgroup of the packet stabilizer. -/
theorem expected_stabilizer_le (π : Representation ℂ G V)
    (ι : Multiplicative (ZMod M) →* G) (φ : G) (q : (ZMod M)ˣ)
    (j : ZMod M) {v : V} (hv : v ∈ packet (tameRestriction π ι) j) {c : ℂ}
    (hclose : (actionEquiv π φ ^ period q j) v = c • v) :
    Subgroup.closure (Set.range ι ∪ {φ ^ period q j}) ≤ lineStabilizer π v := by
  rw [Subgroup.closure_le]
  intro g hg
  rcases hg with ⟨a, rfl⟩ | hg
  · exact inertia_mem π ι j hv a.toAdd
  · have heq : g = φ ^ period q j := hg
    subst g
    exact return_mem π φ q j hclose

end PaperXI.LineCharacter
