import PaperXI.NormalizerIntertwining60
import Mathlib.Topology.Algebra.OpenSubgroup

/-!
# The literal normalizer of a subgroup-character pair

The group is defined from the graph of the actual character. It is therefore
sensitive to both its domain and its values, rather than a separately supplied
group label. Compact parts are formed by intersection with a compact subgroup.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CharacterNormalizer61
variable {G A : Type*} [Group G] [CommGroup A]
variable (H : Subgroup G) (θ : H →* A)

/-- The literal graph of the character in the product group. -/
def graph : Subgroup (G × A) := (H.subtype.prod θ).range

/-- The exact normalizer of the domain and the character, defined through its graph. -/
def normalizer : Subgroup G :=
  (Subgroup.normalizer (graph H θ : Set (G × A))).comap (MonoidHom.inl G A)

/-- A pair normalizer carries every domain element back into the actual domain. -/
theorem conjugation_mem {g : G} (hg : g ∈ normalizer H θ) (h : H) :
    g * (h : G) * g⁻¹ ∈ H := by
  have hp : ((h : G), θ h) ∈ graph H θ := ⟨h, rfl⟩
  have hx := (Subgroup.mem_normalizer_iff.mp hg ((h : G), θ h)).mp hp
  obtain ⟨k, hk⟩ := hx
  have he : (k : G) = g * (h : G) * g⁻¹ := congrArg Prod.fst hk
  exact he ▸ k.property

/-- Character values are preserved by literal conjugation. -/
theorem character_covariance {g : G} (hg : g ∈ normalizer H θ) (h k : H)
    (hk : g * (h : G) * g⁻¹ = k) : θ k = θ h := by
  have hp : ((h : G), θ h) ∈ graph H θ := ⟨h, rfl⟩
  have hx := (Subgroup.mem_normalizer_iff.mp hg ((h : G), θ h)).mp hp
  obtain ⟨j, hj⟩ := hx
  have he : (j : G) = g * (h : G) * g⁻¹ := congrArg Prod.fst hj
  have hjk : j = k := Subtype.ext (he.trans hk)
  have hv : θ j = θ h := by simpa using congrArg Prod.snd hj
  simpa only [hjk] using hv

/-- The graph normalizer really normalizes the character domain. -/
theorem normalizes_domain : normalizer H θ ≤ Subgroup.normalizer (H : Set G) := by
  intro g hg
  apply Subgroup.mem_normalizer_iff.mpr
  intro x
  constructor
  · intro hx
    exact conjugation_mem H θ hg ⟨x, hx⟩
  · intro hx
    have hi := conjugation_mem H θ ((normalizer H θ).inv_mem hg) ⟨g * x * g⁻¹, hx⟩
    simpa [mul_assoc] using hi

/-- The domain always normalizes its own multiplicative character. -/
theorem domain_le_normalizer : H ≤ normalizer H θ := by
  have step (h : H) (p : G × A) (hp : p ∈ graph H θ) :
      ((h : G), (1 : A)) * p * ((h : G), (1 : A))⁻¹ ∈ graph H θ := by
    obtain ⟨k, rfl⟩ := hp
    refine ⟨h * k * h⁻¹, ?_⟩
    apply Prod.ext
    · rfl
    · simp [map_mul, mul_comm]
  intro g hg
  apply Subgroup.mem_normalizer_iff.mpr
  intro p
  constructor
  · exact step ⟨g, hg⟩ p
  · intro hp
    have hi := step ⟨g⁻¹, H.inv_mem hg⟩ (((g, (1 : A))) * p * (g, (1 : A))⁻¹) hp
    convert hi using 1
    ext <;> simp [mul_assoc]

/-- A normalizing element intertwines the same actual character on the actual intersection. -/
theorem character_intertwinedAt (χ : H →* ℂˣ) {g : G}
    (hg : g ∈ normalizer H χ) :
    NormalizerIntertwining60.IntertwinedAt H (MonomialInduction.scalarRepresentation χ) g := by
  apply NormalizerIntertwining60.character_intertwinedAt
  intro h
  exact (character_covariance H χ hg h
    (InductionIrreducibility.intersectionConjugation H g h) rfl).symm

/-- The compact part of a character normalizer is an actual intersection subgroup. -/
def compactPart (S : Subgroup G) : Subgroup G := normalizer H θ ⊓ S

section Topology
variable [TopologicalSpace G] [IsTopologicalGroup G]

/-- Openness follows from the actual open character domain. -/
theorem normalizer_open (hH : IsOpen (H : Set G)) : IsOpen (normalizer H θ : Set G) :=
  Subgroup.isOpen_mono (domain_le_normalizer H θ) hH

/-- Intersecting with a compact open subgroup gives the literal compact open part. -/
theorem compactPart_compact_open (S : Subgroup G) (hH : IsOpen (H : Set G))
    (hSc : IsCompact (S : Set G)) (hSo : IsOpen (S : Set G)) :
    IsCompact (compactPart H θ S : Set G) ∧ IsOpen (compactPart H θ S : Set G) := by
  have hN := normalizer_open H θ hH
  constructor
  · exact hSc.inter_left ((normalizer H θ).isClosed_of_isOpen hN)
  · exact hN.inter hSo

end Topology
end PaperXI.CharacterNormalizer61
