import PaperICompletion7.Nakayama
import KomorebiVerification.SeedRankBasics

/-!
Generator lifting and equality of the existing canonical seed ranks. The
quotient is the literal M / IM and the scalar ring is the literal R / I.
No semisimplicity of the quotient ring is assumed.
-/
set_option autoImplicit false

namespace Komorebi.PaperICompletion7.ModuleTop

open Komorebi.SeedRankBasics
open Komorebi.PaperICompletion7.Nakayama

universe u v w
variable {R : Type u} {M : Type v} [Ring R] [AddCommGroup M] [Module R M]

/-- A set generates exactly when its image generates modulo a radical ideal. -/
theorem image_generates_iff [Module.Finite R M]
    (I : Ideal R) [I.IsTwoSided] (hI : I ≤ Ring.jacobson R) (s : Set M) :
    Generates (R ⧸ I) (IdealTop I M) (idealTopMap I '' s) ↔ Generates R M s := by
  simpa only [Generates, Submodule.map_span] using
    map_eq_top_iff I hI (Submodule.span R s)

/-- The generating-family statement keeps exactly the original index set. -/
theorem family_generates_iff [Module.Finite R M]
    (I : Ideal R) [I.IsTwoSided] (hI : I ≤ Ring.jacobson R)
    {ι : Type w} (x : ι → M) :
    FamilyGenerates (R ⧸ I) (IdealTop I M) (idealTopMap I ∘ x) ↔
      FamilyGenerates R M x := by
  simpa only [FamilyGenerates, Set.range_comp] using
    image_generates_iff I hI (Set.range x)

/-- Any choice of lifts of a generating quotient family generates upstairs. -/
theorem lifts_generate [Module.Finite R M]
    (I : Ideal R) [I.IsTwoSided] (hI : I ≤ Ring.jacobson R)
    {ι : Type w} (x : ι → IdealTop I M) (y : ι → M)
    (hxy : ∀ i, idealTopMap I (y i) = x i)
    (hx : FamilyGenerates (R ⧸ I) (IdealTop I M) x) :
    FamilyGenerates R M y := by
  apply (family_generates_iff I hI y).mp
  have heq : idealTopMap I ∘ y = x := funext hxy
  rwa [heq]

/-- Both inequalities for the canonical cardinal minimum are proved. -/
theorem seedRank_eq_idealTop [Module.Finite R M]
    (I : Ideal R) [I.IsTwoSided] (hI : I ≤ Ring.jacobson R) :
    seedRank R M = seedRank (R ⧸ I) (IdealTop I M) := by
  classical
  let f := idealTopMap (M := M) I
  apply le_antisymm
  · obtain ⟨s, hs, hcard⟩ := exists_generating_set_card_eq_seedRank
      (R ⧸ I) (IdealTop I M)
    let g : IdealTop I M → M := fun y ↦ Classical.choose (idealTopMap_surjective I y)
    have hg (y : IdealTop I M) : f (g y) = y :=
      Classical.choose_spec (idealTopMap_surjective I y)
    have himage : f '' (g '' s) = s := by
      ext y
      constructor
      · rintro ⟨x, ⟨z, hz, rfl⟩, rfl⟩
        rwa [hg]
      · intro hy
        exact ⟨g y, ⟨y, hy, rfl⟩, hg y⟩
    have hlift : Generates R M (g '' s) :=
      (image_generates_iff I hI _).mp (by
        change Generates (R ⧸ I) (IdealTop I M) (f '' (g '' s))
        rw [himage]
        exact hs)
    calc
      seedRank R M ≤ Cardinal.mk (g '' s) := seedRank_le_mk_of_generates R M hlift
      _ ≤ Cardinal.mk s := Cardinal.mk_image_le
      _ = seedRank (R ⧸ I) (IdealTop I M) := hcard
  · obtain ⟨s, hs, hcard⟩ := exists_generating_set_card_eq_seedRank R M
    have himage := (image_generates_iff I hI s).mpr hs
    calc
      seedRank (R ⧸ I) (IdealTop I M) ≤ Cardinal.mk (f '' s) :=
        seedRank_le_mk_of_generates (R ⧸ I) (IdealTop I M) himage
      _ ≤ Cardinal.mk s := Cardinal.mk_image_le
      _ = seedRank R M := hcard

/-- The natural-valued minimum agrees too, for the existing definitions. -/
theorem seedFinrank_eq_idealTop [Module.Finite R M]
    (I : Ideal R) [I.IsTwoSided] (hI : I ≤ Ring.jacobson R) :
    seedFinrank R M = seedFinrank (R ⧸ I) (IdealTop I M) :=
  congrArg Cardinal.toNat (seedRank_eq_idealTop I hI)

/-- The quotient module over the quotient ring is genuinely finitely generated. -/
theorem idealTop_finite [Module.Finite R M]
    (I : Ideal R) [I.IsTwoSided] (hI : I ≤ Ring.jacobson R) :
    Module.Finite (R ⧸ I) (IdealTop I M) := by
  apply (seedRank_lt_aleph0_iff (R ⧸ I) (IdealTop I M)).mp
  rw [← seedRank_eq_idealTop I hI]
  exact (seedRank_lt_aleph0_iff R M).mpr inferInstance

/-- The module top, without a semisimplicity assumption. -/
abbrev RadicalTop (R : Type u) (M : Type v) [Ring R] [AddCommGroup M] [Module R M] :=
  IdealTop (Ring.jacobson R) M

/-- Manuscript-facing generator lifting modulo the Jacobson radical. -/
theorem generates_iff_radicalTop [Module.Finite R M] (s : Set M) :
    Generates R M s ↔
      Generates (R ⧸ Ring.jacobson R) (RadicalTop R M)
        (idealTopMap (Ring.jacobson R) '' s) :=
  (image_generates_iff (Ring.jacobson R) le_rfl s).symm

/-- The printed cardinal seed-rank equality over an arbitrary unital ring. -/
theorem seedRank_eq_radicalTop [Module.Finite R M] :
    seedRank R M = seedRank (R ⧸ Ring.jacobson R) (RadicalTop R M) :=
  seedRank_eq_idealTop (Ring.jacobson R) le_rfl

/-- Natural minimum version of the module-top equality. -/
theorem seedFinrank_eq_radicalTop [Module.Finite R M] :
    seedFinrank R M = seedFinrank (R ⧸ Ring.jacobson R) (RadicalTop R M) :=
  seedFinrank_eq_idealTop (Ring.jacobson R) le_rfl

/-- Any lifts of a quotient basis generate over the original ring. -/
theorem quotient_basis_lifts_generate [Module.Finite R M]
    (I : Ideal R) [I.IsTwoSided] (hI : I ≤ Ring.jacobson R) {ι : Type w}
    (b : Module.Basis ι (R ⧸ I) (IdealTop I M)) (x : ι → M)
    (hx : ∀ i, idealTopMap I (x i) = b i) : FamilyGenerates R M x :=
  lifts_generate I hI b x hx b.span_eq

end Komorebi.PaperICompletion7.ModuleTop
