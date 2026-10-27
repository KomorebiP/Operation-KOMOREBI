import PaperXI.QuotientRepresentation
import PaperXI.GeneratedIrreducibility
import Mathlib.Analysis.Complex.Basic
import Mathlib.GroupTheory.Index
import Mathlib.GroupTheory.Subgroup.Center

/-! The actual type-side scalar restriction and quotient action. The source
input that an irreducible representation contains the invariant character
is used through its nonzero character eigenspace; scalar restriction on
the whole representation is a conclusion, not an additional assumption. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TypeSideDescent

variable {G V : Type*} [Group G] [AddCommGroup V] [Module ℂ V]

/-- Conjugation in a normal subgroup, retaining the actual subgroup element. -/
def conjugate (H : Subgroup G) [H.Normal] (g : G) (h : H) : H :=
  ⟨g * h * g⁻¹, Subgroup.Normal.conj_mem (inferInstance : H.Normal) (h : G) h.property g⟩

/-- The invariance of the actual character under the ambient group. -/
def Invariant (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ) : Prop :=
  ∀ (g : G) (h : H), θ (conjugate H g h) = θ h

/-- The simultaneous character eigenspace in the supplied representation. -/
def characterSpace (H : Subgroup G) (θ : H →* ℂˣ) (η : Representation ℂ G V) :
    Submodule ℂ V where
  carrier := {v | ∀ h : H, η h v = (θ h : ℂ) • v}
  zero_mem' := by simp
  add_mem' := by
    intro v w hv hw h
    simp only [map_add, hv h, hw h, smul_add]
  smul_mem' := by
    intro c v hv h
    simp only [map_smul, hv h, smul_comm c (θ h : ℂ)]

/-- Containment of a one-dimensional character, expressed by a nonzero
vector in the actual simultaneous eigenspace. -/
def Contains (H : Subgroup G) (θ : H →* ℂˣ) (η : Representation ℂ G V) : Prop :=
  ∃ v : V, v ≠ 0 ∧ v ∈ characterSpace H θ η

/-- The actual one-dimensional representation associated to the character. -/
def characterRepresentation (H : Subgroup G) (θ : H →* ℂˣ) : Representation ℂ H ℂ where
  toFun h := (θ h : ℂ) • LinearMap.id
  map_one' := by simp [Module.End.one_eq_id]
  map_mul' a b := by
    apply LinearMap.ext
    intro z
    simp [mul_smul, mul_left_comm]

/-- The eigenspace formulation of containment is equivalent to an actual
nonzero intertwiner from the one-dimensional character representation. -/
theorem contains_iff_nonzero_intertwiner (H : Subgroup G) (θ : H →* ℂˣ)
    (η : Representation ℂ G V) :
    Contains H θ η ↔ ∃ F : Representation.IntertwiningMap (characterRepresentation H θ)
      (η.comp H.subtype), F ≠ 0 := by
  constructor
  · rintro ⟨v, hv, hmem⟩
    let F : Representation.IntertwiningMap (characterRepresentation H θ)
        (η.comp H.subtype) :=
      ⟨LinearMap.toSpanSingleton ℂ V v, fun h => by
        apply LinearMap.ext
        intro z
        change ((θ h : ℂ) • z) • v = η (h : G) (z • v)
        rw [map_smul, hmem h]
        simp [smul_smul, mul_comm]⟩
    refine ⟨F, ?_⟩
    intro hF
    have heq := congrArg (fun f : Representation.IntertwiningMap
      (characterRepresentation H θ) (η.comp H.subtype) => f 1) hF
    exact hv (by simpa [F] using heq)
  · rintro ⟨F, hF⟩
    refine ⟨F 1, ?_, ?_⟩
    · intro hzero
      apply hF
      apply Representation.IntertwiningMap.ext
      apply LinearMap.ext
      intro z
      have hz := F.map_smul z (1 : ℂ)
      simpa [hzero] using hz
    · intro h
      have heq := (Representation.IntertwiningMap.isIntertwining
        (characterRepresentation H θ) (η.comp H.subtype) F h 1).symm
      exact heq.trans (F.map_smul (θ h : ℂ) 1)

theorem characterSpace_stable (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) (η : Representation ℂ G V) (g : G)
    {v : V} (hv : v ∈ characterSpace H θ η) : η g v ∈ characterSpace H θ η := by
  intro h
  have hmul : η (h : G) * η g = η g * η (conjugate H g⁻¹ h : G) := by
    rw [← map_mul, ← map_mul]
    congr 1
    simp [conjugate, mul_assoc]
  change (η (h : G) * η g) v = (θ h : ℂ) • η g v
  rw [hmul, Module.End.mul_apply, hv (conjugate H g⁻¹ h), hθ]
  exact (η g).map_smul _ _

/-- The character eigenspace is an actual subrepresentation by invariance. -/
def characterSubrepresentation (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) (η : Representation ℂ G V) : Subrepresentation η :=
  ⟨characterSpace H θ η, fun g _ hv => characterSpace_stable H θ hθ η g hv⟩

/-- Irreducibility promotes containment of the invariant character to its
scalar action on every vector. -/
theorem scalar_restriction (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) (η : Representation ℂ G V) [Representation.IsIrreducible η]
    (hcontains : Contains H θ η) (h : H) : η (h : G) = (θ h : ℂ) • LinearMap.id := by
  let S := characterSubrepresentation H θ hθ η
  have hS : S ≠ ⊥ := by
    intro hs
    obtain ⟨v, hv, hmem⟩ := hcontains
    have hz : v ∈ (⊥ : Subrepresentation η) := hs ▸ hmem
    exact hv hz
  have htop : S = ⊤ := (eq_bot_or_eq_top S).resolve_left hS
  ext v
  have hv : v ∈ S := htop ▸ (show v ∈ (⊤ : Subrepresentation η) from trivial)
  exact hv h

/-- The kernel of the character viewed as an actual subgroup of the ambient
group. Invariance is recorded so that its normality is available canonically. -/
def characterKernel (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (_hθ : Invariant H θ) : Subgroup G := θ.ker.map H.subtype

theorem characterKernel_le (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) : characterKernel H θ hθ ≤ H := by
  rintro g ⟨h, _, rfl⟩
  exact h.property

@[simp] theorem mem_characterKernel (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) (h : H) :
    (h : G) ∈ characterKernel H θ hθ ↔ θ h = 1 := by
  constructor
  · rintro ⟨h', hh', heq⟩
    have : h' = h := Subtype.ext heq
    simpa [this] using hh'
  · intro hh
    exact ⟨h, hh, rfl⟩

instance characterKernel_normal (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) : (characterKernel H θ hθ).Normal where
  conj_mem := by
    rintro g ⟨h, hh, rfl⟩ a
    refine ⟨conjugate H a h, ?_, rfl⟩
    exact (hθ a h).trans hh

/-- The character kernel acts trivially, as a consequence of containment. -/
theorem characterKernel_le_ker (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) (η : Representation ℂ G V) [Representation.IsIrreducible η]
    (hcontains : Contains H θ η) : characterKernel H θ hθ ≤ η.ker := by
  rintro g ⟨h, hh, rfl⟩
  change η (h : G) = 1
  rw [scalar_restriction H θ hθ η hcontains h]
  have hh' : θ h = 1 := hh
  simp [hh', Module.End.one_eq_id]

/-- The actual action descended to `J¹ / ker θ`. -/
def representation (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) (η : Representation ℂ G V) [Representation.IsIrreducible η]
    (hcontains : Contains H θ η) : Representation ℂ (G ⧸ characterKernel H θ hθ) V :=
  QuotientRepresentation.descend (characterKernel H θ hθ) η
    (characterKernel_le_ker H θ hθ η hcontains)

@[simp] theorem representation_apply (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) (η : Representation ℂ G V) [Representation.IsIrreducible η]
    (hcontains : Contains H θ η) (g : G) :
    representation H θ hθ η hcontains (QuotientGroup.mk' (characterKernel H θ hθ) g) =
      η g := rfl

theorem representation_irreducible (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) (η : Representation ℂ G V) [Representation.IsIrreducible η]
    (hcontains : Contains H θ η) :
    Representation.IsIrreducible (representation H θ hθ η hcontains) :=
  QuotientRepresentation.descend_irreducible _ _ _

/-- Finiteness of the central quotient follows from the actual finite
quotient and finite character image, without assuming the ambient group finite. -/
theorem finite_quotient (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) [Finite (G ⧸ H)] [Finite θ.range] :
    Finite (G ⧸ characterKernel H θ hθ) := by
  let : H.FiniteIndex := Subgroup.finiteIndex_of_finite_quotient
  have hindex : (characterKernel H θ hθ).FiniteIndex := by
    constructor
    rw [characterKernel, Subgroup.index_map_subtype]
    exact mul_ne_zero Subgroup.FiniteIndex.index_ne_zero Subgroup.FiniteIndex.index_ne_zero
  exact @Subgroup.finite_quotient_of_finiteIndex G _ (characterKernel H θ hθ) hindex

/-- The actual quotient map onto the type-side symplectic quotient. -/
def quotientProjection (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) : (G ⧸ characterKernel H θ hθ) →* (G ⧸ H) :=
  QuotientGroup.lift (characterKernel H θ hθ) (QuotientGroup.mk' H) (by
    simpa using characterKernel_le H θ hθ)

@[simp] theorem quotientProjection_apply (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) (g : G) :
    quotientProjection H θ hθ (QuotientGroup.mk' (characterKernel H θ hθ) g) =
      QuotientGroup.mk' H g := rfl

theorem quotientProjection_surjective (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) : Function.Surjective (quotientProjection H θ hθ) :=
  QuotientGroup.lift_surjective_of_surjective _ _ QuotientGroup.mk_surjective _

/-- Exactness identifies the kernel with the image of `H¹ / ker θ`. -/
theorem quotientProjection_ker (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) :
    (quotientProjection H θ hθ).ker = H.map (QuotientGroup.mk' (characterKernel H θ hθ)) := by
  rw [quotientProjection, QuotientGroup.ker_lift, QuotientGroup.ker_mk']

/-- Character invariance makes the distinguished subgroup central in the
actual quotient group. -/
theorem central_image (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) :
    H.map (QuotientGroup.mk' (characterKernel H θ hθ)) ≤
      Subgroup.center (G ⧸ characterKernel H θ hθ) := by
  rintro z ⟨h, hh, rfl⟩
  rw [Subgroup.mem_center_iff]
  intro a
  obtain ⟨g, rfl⟩ := QuotientGroup.mk_surjective a
  let hH : H := ⟨h, hh⟩
  let q := QuotientGroup.mk' (characterKernel H θ hθ)
  have heq : q (conjugate H g hH : G) = q h := by
    apply QuotientGroup.eq.mpr
    refine ⟨(conjugate H g hH)⁻¹ * hH, ?_, rfl⟩
    change θ ((conjugate H g hH)⁻¹ * hH) = 1
    simp [hθ g hH]
  have heq' := congrArg (fun b => b * q g) heq
  simpa [conjugate, hH, map_mul, mul_assoc, q] using heq'

/-- The actual central quotient character. -/
def centralCharacter (H : Subgroup G) (θ : H →* ℂˣ) : (H ⧸ θ.ker) →* ℂˣ :=
  QuotientGroup.lift θ.ker θ le_rfl

@[simp] theorem centralCharacter_apply (H : Subgroup G) (θ : H →* ℂˣ) (h : H) :
    centralCharacter H θ (QuotientGroup.mk' θ.ker h) = θ h := rfl

theorem centralCharacter_injective (H : Subgroup G) (θ : H →* ℂˣ) :
    Function.Injective (centralCharacter H θ) :=
  (QuotientGroup.injective_lift_iff _ _ _).mpr rfl

/-- Include `H¹ / ker θ` into the actual finite central quotient. -/
def centerInclusion (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) : (H ⧸ θ.ker) →* (G ⧸ characterKernel H θ hθ) :=
  QuotientGroup.lift θ.ker
    ((QuotientGroup.mk' (characterKernel H θ hθ)).comp H.subtype) (by
      intro h hh
      change (h : G ⧸ characterKernel H θ hθ) = 1
      exact (QuotientGroup.eq_one_iff (h : G)).mpr ⟨h, hh, rfl⟩)

@[simp] theorem centerInclusion_apply (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) (h : H) :
    centerInclusion H θ hθ (QuotientGroup.mk' θ.ker h) =
      QuotientGroup.mk' (characterKernel H θ hθ) (h : G) := rfl

theorem centerInclusion_injective (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) : Function.Injective (centerInclusion H θ hθ) := by
  apply (QuotientGroup.injective_lift_iff _ _ _).mpr
  ext h
  change θ h = 1 ↔ (h : G ⧸ characterKernel H θ hθ) = 1
  rw [QuotientGroup.eq_one_iff, mem_characterKernel]

theorem centerInclusion_range (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) :
    (centerInclusion H θ hθ).range = H.map (QuotientGroup.mk' (characterKernel H θ hθ)) := by
  ext a
  constructor
  · rintro ⟨z, rfl⟩
    obtain ⟨h, rfl⟩ := QuotientGroup.mk_surjective z
    exact ⟨h, h.property, rfl⟩
  · rintro ⟨h, hh, rfl⟩
    exact ⟨QuotientGroup.mk' θ.ker ⟨h, hh⟩, rfl⟩

/-- The constructed center inclusion and quotient map form an exact sequence. -/
theorem exact_center_quotient (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) :
    (centerInclusion H θ hθ).range = (quotientProjection H θ hθ).ker := by
  rw [centerInclusion_range, quotientProjection_ker]

theorem centerInclusion_central (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) :
    (centerInclusion H θ hθ).range ≤ Subgroup.center (G ⧸ characterKernel H θ hθ) := by
  rw [centerInclusion_range]
  exact central_image H θ hθ

/-- The descended action has precisely the character induced by `θ` on its
actual central subgroup, after proving scalar restriction from containment. -/
theorem central_action (H : Subgroup G) [H.Normal] (θ : H →* ℂˣ)
    (hθ : Invariant H θ) (η : Representation ℂ G V) [Representation.IsIrreducible η]
    (hcontains : Contains H θ η) (z : H ⧸ θ.ker) :
    representation H θ hθ η hcontains (centerInclusion H θ hθ z) =
      (centralCharacter H θ z : ℂ) • LinearMap.id := by
  obtain ⟨h, rfl⟩ := QuotientGroup.mk_surjective z
  exact scalar_restriction H θ hθ η hcontains h

end PaperXI.TypeSideDescent
