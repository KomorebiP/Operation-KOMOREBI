import PaperXI.InductionIrreducibility

/-! Exact convention adapter for the full extended-type intertwining locus. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FullIntertwiningLocus69
open Representation PaperXI.InductionIrreducibility

variable {k G V : Type*} [Field k] [Group G] [AddCommGroup V] [Module k V]
  (H : Subgroup G) (σ : Representation k H V)

/-- Actual full intertwining locus, with the intersection and conjugation of the
coefficient-model Mackey theorem, not a compact-subgroup substitute. -/
def locus : Set G :=
  {g | ∃ A : IntertwiningMap (σ.comp (intersectionSubgroup H g).subtype)
    (σ.comp (intersectionConjugation H g)), A ≠ 0}

/-- An element of H intertwines by its own representation operator. -/
def internalIntertwiner (g : H) :
    IntertwiningMap (σ.comp (intersectionSubgroup H (g : G)).subtype)
      (σ.comp (intersectionConjugation H (g : G))) where
  toLinearMap := σ g
  isIntertwining' h := by
    change σ g * σ (h : H) = σ (intersectionConjugation H (g : G) h) * σ g
    rw [← map_mul, ← map_mul]
    congr 1
    apply Subtype.ext
    simp [intersectionConjugation, mul_assoc]

theorem internalIntertwiner_ne_zero [Nontrivial V] (g : H) :
    internalIntertwiner H σ g ≠ 0 := by
  intro he
  obtain ⟨v, hv⟩ := exists_ne (0 : V)
  have hz := congrArg (fun A => σ g⁻¹ (A v)) he
  have hz' : σ g⁻¹ (σ g v) = 0 := by simpa [internalIntertwiner] using hz
  have hi : σ g⁻¹ (σ g v) = v := by
    rw [← Module.End.mul_apply, ← map_mul, inv_mul_cancel, map_one]
    rfl
  exact hv (hi.symm.trans hz')

theorem subgroup_subset [Nontrivial V] :
    (H : Set G) ⊆ locus H σ := by
  intro g hg
  exact ⟨internalIntertwiner H σ ⟨g,hg⟩, internalIntertwiner_ne_zero H σ ⟨g,hg⟩⟩

/-- A genuine full-locus equality is exactly the hypothesis used by the
compact-mod-center induction theorem. -/
theorem locus_eq_iff [Nontrivial V] :
    locus H σ = (H : Set G) ↔
      ∀ g : G, g ∉ H →
        ∀ A : IntertwiningMap (σ.comp (intersectionSubgroup H g).subtype)
          (σ.comp (intersectionConjugation H g)), A = 0 := by
  constructor
  · intro he g hg A
    by_contra hA
    have hm : g ∈ locus H σ := ⟨A,hA⟩
    rw [he] at hm
    exact hg hm
  · intro h
    apply Set.Subset.antisymm
    · intro g hg
      by_contra hgn
      obtain ⟨A,hA⟩ := hg
      exact hA (h g hgn A)
    · exact subgroup_subset H σ


/-- The opposite common conjugation convention: its subgroup is
H intersect g H g-inverse and its conjugate operator is sigma(g-inverse h g).
This is the present literal coefficient convention at g-inverse. -/
def standardLocus : Set G := {g | g⁻¹ ∈ locus H σ}

/-- Full subgroup equality is independent of the two inverse conventions.
This does not identify individual Hom spaces by assuming invertible maps. -/
theorem standardLocus_eq_iff :
    standardLocus H σ = (H : Set G) ↔ locus H σ = (H : Set G) := by
  constructor
  · intro he
    ext g
    have ht := Set.ext_iff.mp he g⁻¹
    simpa [standardLocus] using ht
  · intro he
    ext g
    simp [standardLocus, he]

/-- A source using the conventional inverse-conjugation definition supplies
exactly the full off-H premise of the existing Mackey construction. -/
theorem off_subgroup_of_standard_locus [Nontrivial V]
    (hI : standardLocus H σ = (H : Set G)) :
    ∀ g : G, g ∉ H →
      ∀ A : IntertwiningMap (σ.comp (intersectionSubgroup H g).subtype)
        (σ.comp (intersectionConjugation H g)), A = 0 :=
  (locus_eq_iff H σ).mp ((standardLocus_eq_iff H σ).mp hI)

end PaperXI.FullIntertwiningLocus69
