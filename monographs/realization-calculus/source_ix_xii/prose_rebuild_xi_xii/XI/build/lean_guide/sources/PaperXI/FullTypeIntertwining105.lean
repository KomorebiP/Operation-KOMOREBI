import PaperXI.CuspidalCartan105
import PaperXI.FullIntertwiningLocus69
import PaperXI.CompactModCenterInduction68

/-!
From the actual finite cuspidal factor to full extended-type Mackey vanishing.
The BK tensor-to-residue reduction and arithmetic Cartan decomposition remain
explicit inputs. The full-H intertwining bound and induced irreducibility do not.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FullTypeIntertwining105
open Matrix Representation
open PaperXI.IntertwiningAlong105 PaperXI.InductionIrreducibility

section ExactHom
variable {C G V : Type*} [Field C] [Group G] [AddCommGroup V] [Module C V]

/-- The elementary equation is equivalent to the actual intersection Hom space. -/
def mapOfAlong (H : Subgroup G) (ρ : Representation C H V) (g : G)
    (T : V →ₗ[C] V) (hT : Along H.subtype ρ g T) :
    IntertwiningMap (ρ.comp (intersectionSubgroup H g).subtype)
      (ρ.comp (intersectionConjugation H g)) where
  toLinearMap := T
  isIntertwining' x := by
    ext v
    exact hT (x : H) (intersectionConjugation H g x) rfl v

/-- No equivalence or inverse for the intertwiner is assumed. -/
theorem alongOfMap (H : Subgroup G) (ρ : Representation C H V) (g : G)
    (T : IntertwiningMap (ρ.comp (intersectionSubgroup H g).subtype)
      (ρ.comp (intersectionConjugation H g))) :
    Along H.subtype ρ g T.toLinearMap := by
  intro x y hy v
  change (y : G) = g * (x : G) * g⁻¹ at hy
  let z : intersectionSubgroup H g := ⟨x, by
    change g * (x : G) * g⁻¹ ∈ H
    rw [← hy]
    exact y.property⟩
  have he : intersectionConjugation H g z = y := Subtype.ext hy.symm
  have ht := LinearMap.congr_fun (T.isIntertwining' z) v
  change T (ρ x v) = ρ (intersectionConjugation H g z) (T v) at ht
  change T (ρ x v) = ρ y (T v)
  rw [he] at ht
  exact ht

theorem existsAt_iff_locus (H : Subgroup G) (ρ : Representation C H V) (g : G) :
    ExistsAt H.subtype ρ g ↔ g ∈ FullIntertwiningLocus69.locus H ρ := by
  constructor
  · rintro ⟨T, hn, ht⟩
    refine ⟨mapOfAlong H ρ g T ht, ?_⟩
    intro he
    apply hn
    exact congrArg IntertwiningMap.toLinearMap he
  · rintro ⟨T, hn⟩
    refine ⟨T.toLinearMap, ?_, alongOfMap H ρ g T⟩
    intro he
    apply hn
    ext v
    exact LinearMap.congr_fun he v

/-- Restriction to J <= H keeps the same nonzero operator and carrier. -/
theorem restrict_existsAt (J H : Subgroup G) (hJH : J ≤ H)
    (Λ : Representation C H V) (g : G) (hg : ExistsAt H.subtype Λ g) :
    ExistsAt J.subtype (Λ.comp (Subgroup.inclusion hJH)) g := by
  obtain ⟨T, hn, ht⟩ := hg
  refine ⟨T, hn, ?_⟩
  intro x y he v
  exact ht (Subgroup.inclusion hJH x) (Subgroup.inclusion hJH y) he v

/-- An irreducible compact restriction proves irreducibility of its extension. -/
theorem extension_irreducible (J H : Subgroup G) (hJH : J ≤ H)
    (Λ : Representation C H V)
    [IsIrreducible (Λ.comp (Subgroup.inclusion hJH))] : IsIrreducible Λ := by
  let : Nontrivial V := GeneratedIrreducibility.nontrivial_space
    (Λ.comp (Subgroup.inclusion hJH))
  apply RepresentationStability.irreducible_of_stable
  intro S hS
  exact RepresentationStability.eq_bot_or_top (Λ.comp (Subgroup.inclusion hJH)) S
    (fun j v hv => hS (Subgroup.inclusion hJH j) v hv)
end ExactHom

section FullLocus
variable {ι R F k C Ω V W : Type*} [Fintype ι] [DecidableEq ι]
  [CommRing R] [Field F] [Field k] [Fintype k] [Field C] [CharZero C]
  [Group Ω] [AddCommGroup V] [Module C V] [Nontrivial V]
  [AddCommGroup W] [Module C W]

/-- The full locus of the completed type is an output, not a premise.
`hBK532` is precisely the source tensor-to-residue reduction, without any
cuspidal or maximal-support conclusion built into it. -/
theorem full_locus
    (f : R →+* F) (red : R →+* k) (hred : Function.Surjective red)
    (π : R) (hπ : f π ≠ 0) (hπred : red π = 0)
    (hCartan : CuspidalCartan105.HasCartan (ι := ι) f π hπ)
    (σ : Representation C (GL ι k) W) (hσ : CuspidalCartan105.Cuspidal σ)
    (b : GL ι F →* Ω) (J H : Subgroup Ω) (hJH : J ≤ H)
    (hintegral : ∀ u : GL ι R, b (GeneralLinearGroup.map f u) ∈ J)
    (hscalar : ∀ c : Fˣ, b (GeneralLinearGroup.scalar ι c) ∈ H)
    (Λ : Representation C H V)
    (hBK532 : ∀ g : Ω,
      ExistsAt J.subtype (Λ.comp (Subgroup.inclusion hJH)) g →
      ∃ j₁ j₂ : J, ∃ y : GL ι F,
        g = (j₁ : Ω) * b y * (j₂ : Ω) ∧
        ExistsAt (GeneralLinearGroup.map f) (σ.comp (GeneralLinearGroup.map red)) y) :
    FullIntertwiningLocus69.locus H Λ = (H : Set Ω) := by
  apply Set.Subset.antisymm
  · intro g hg
    have hg' := restrict_existsAt J H hJH Λ g ((existsAt_iff_locus H Λ g).mpr hg)
    obtain ⟨j₁, j₂, y, he, hy⟩ := hBK532 g hg'
    obtain ⟨c, u, hu⟩ := CuspidalCartan105.intertwining_support
      f red hred π hπ hπred hCartan σ hσ y hy
    rw [he, hu, map_mul]
    exact H.mul_mem (H.mul_mem (hJH j₁.property)
      (H.mul_mem (hscalar c) (hJH (hintegral u)))) (hJH j₂.property)
  · exact FullIntertwiningLocus69.subgroup_subset H Λ

/-- This theorem genuinely calls the existing compact-mod-center induction
construction after deriving its formerly missing full-H hypothesis. -/
theorem induction_package
    [TopologicalSpace Ω] [IsTopologicalGroup Ω] [FiniteDimensional C V]
    (f : R →+* F) (red : R →+* k) (hred : Function.Surjective red)
    (π : R) (hπ : f π ≠ 0) (hπred : red π = 0)
    (hCartan : CuspidalCartan105.HasCartan (ι := ι) f π hπ)
    (σ : Representation C (GL ι k) W) (hσ : CuspidalCartan105.Cuspidal σ)
    (b : GL ι F →* Ω) (J H : Subgroup Ω) (hJH : J ≤ H)
    (hintegral : ∀ u : GL ι R, b (GeneralLinearGroup.map f u) ∈ J)
    (hscalar : ∀ c : Fˣ, b (GeneralLinearGroup.scalar ι c) ∈ H)
    (Λ : Representation C H V)
    [IsIrreducible (Λ.comp (Subgroup.inclusion hJH))]
    (hBK532 : ∀ g : Ω,
      ExistsAt J.subtype (Λ.comp (Subgroup.inclusion hJH)) g →
      ∃ j₁ j₂ : J, ∃ y : GL ι F,
        g = (j₁ : Ω) * b y * (j₂ : Ω) ∧
        ExistsAt (GeneralLinearGroup.map f) (σ.comp (GeneralLinearGroup.map red)) y)
    (Z : Subgroup H) [Z.Normal] [CompactSpace (H ⧸ Z)]
    (χ : Z →* Cˣ)
    (hcentral : ∀ z : Z, ∀ g : Ω, Commute (((z : H) : Ω)) g)
    (hscalarZ : ∀ z : Z, ∀ v, Λ (z : H) v = (χ z : C) • v)
    (hHopen : IsOpen (H : Set Ω)) (hΛ : SmoothDegreeQuotient.IsSmooth Λ) :
    FullIntertwiningLocus69.locus H Λ = (H : Set Ω) ∧
      Nontrivial (IndV H.subtype Λ) ∧
      SmoothDegreeQuotient.IsSmooth (ind H.subtype Λ) ∧
      IsIrreducible (ind H.subtype Λ) := by
  let : IsIrreducible Λ := extension_irreducible J H hJH Λ
  have hI := full_locus f red hred π hπ hπred hCartan σ hσ b J H hJH
    hintegral hscalar Λ hBK532
  exact ⟨hI, CompactModCenterInduction68.induction_package H Λ Z χ hcentral
    hscalarZ hHopen hΛ ((FullIntertwiningLocus69.locus_eq_iff H Λ).mp hI)⟩
end FullLocus
end PaperXI.FullTypeIntertwining105
