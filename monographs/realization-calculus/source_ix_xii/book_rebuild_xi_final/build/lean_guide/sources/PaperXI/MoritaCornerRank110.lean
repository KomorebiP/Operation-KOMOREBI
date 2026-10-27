import PaperXI.MoritaLattice110
import Mathlib.NumberTheory.LocalField.Basic
import Mathlib.LinearAlgebra.FreeModule.PID
import Mathlib.LinearAlgebra.FreeModule.Finite.Matrix
import Mathlib.RingTheory.Localization.Module

/-! Genuine finite/full submodules of the endomorphism ring acquire their
rank from the ambient field extension. No numerical index is a hypothesis. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.MoritaCornerRank110
open Module Submodule Matrix ValuativeRel
open PaperXI.MoritaLattice110

section FullSubmodule
variable {R K M : Type*} [CommRing R] [IsDomain R] [Field K]
  [Algebra R K] [IsFractionRing R K] [IsPrincipalIdealRing R]
  [AddCommGroup M] [Module R M] [Module K M] [IsScalarTower R K M]

/-- A finite full submodule over a PID has a basis whose size is derived
from the dimension of its actual ambient vector space. -/
theorem exists_basis_full_submodule (Λ : Submodule R M) (hfg : Λ.FG)
    (hfull : Submodule.span K (Λ : Set M) = ⊤) :
    ∃ n : ℕ, ∃ _b : Basis (Fin n) R Λ, n = Module.finrank K M := by
  let : Module.Finite R Λ := Module.Finite.of_fg hfg
  let : Module.IsTorsionFree R M := Module.IsTorsionFree.of_smul_eq_zero <| by
    intro r x h
    have h' : algebraMap R K r • x = 0 := by simpa only [algebraMap_smul] using h
    rcases smul_eq_zero.mp h' with hr | hx
    · exact Or.inl (IsFractionRing.injective R K (by simpa using hr))
    · exact Or.inr hx
  obtain ⟨n, b⟩ := Module.basisOfFiniteTypeTorsionFree' (R := R) (M := Λ)
  have hli : LinearIndependent R (fun i => (b i : M)) :=
    b.linearIndependent.map' Λ.subtype (by simp)
  have hliK : LinearIndependent K (fun i => (b i : M)) :=
    hli.localization K (nonZeroDivisors R)
  have hspanR : Submodule.span R (Set.range fun i => (b i : M)) = Λ := by
    calc
      _ = (Submodule.span R (Set.range b)).map Λ.subtype := by
        rw [Submodule.map_span]
        congr 1
        ext x
        constructor
        · rintro ⟨i, rfl⟩
          exact ⟨b i, ⟨i, rfl⟩, rfl⟩
        · rintro ⟨z, ⟨i, rfl⟩, rfl⟩
          exact ⟨i, rfl⟩
      _ = Λ := by rw [b.span_eq, Submodule.map_top, Submodule.range_subtype]
  have hspanK : Submodule.span K (Set.range fun i => (b i : M)) = ⊤ := by
    rw [← Submodule.span_span_of_tower R K, hspanR, hfull]
  let bK : Basis (Fin n) K M := Basis.mk hliK hspanK.ge
  exact ⟨n, b, by simpa using (Module.finrank_eq_card_basis bK).symm⟩

end FullSubmodule

section ActualEndomorphismCorner
variable (F E : Type*) [Field F] [Field E] [Algebra F E]
  [Module.Finite F E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E]
variable {m : Type*} [Fintype m] [DecidableEq m]

/-- Actual multiplication by extension-field integers as F-linear maps. -/
def coefficientMap : 𝒪[E] →+* Module.End F E :=
  (Algebra.lmul F E).toRingHom.comp (valuation E).integer.subtype

/-- The actual corner with its inherited left integer-ring module structure. -/
def cornerSubmodule (L : Submodule 𝒪[E] (Matrix m m (Module.End F E)))
    (hL : IsMatrixBimodule (coefficientMap F E) L.toAddSubgroup) (p : m) :
    Submodule 𝒪[E] (Module.End F E) where
  __ := corner L.toAddSubgroup p
  smul_mem' a x hx := by
    have he : a • x = coefficientMap F E a * x := by ext v; rfl
    rw [he]
    exact (corner_bimodule (coefficientMap F E) L.toAddSubgroup hL p a hx).1

omit [Module.Finite F E] [TopologicalSpace E] [IsNonarchimedeanLocalField E] in
/-- Entry projection identifies this corner with the image of the original
integer-ring submodule. -/
theorem cornerSubmodule_eq_map
    (L : Submodule 𝒪[E] (Matrix m m (Module.End F E)))
    (hL : IsMatrixBimodule (coefficientMap F E) L.toAddSubgroup) (p : m) :
    cornerSubmodule F E L hL p = L.map (entryLinearMap 𝒪[E] (Module.End F E) p p) := by
  ext x
  constructor
  · intro hx
    exact ⟨single p p x, hx, by simp⟩
  · rintro ⟨z, hz, rfl⟩
    exact entry_mem_corner (coefficientMap F E) L.toAddSubgroup hL p hz p p

omit [Module.Finite F E] [TopologicalSpace E] [IsNonarchimedeanLocalField E] in
/-- Finiteness is transported from the actual whole lattice to its corner. -/
theorem corner_fg (L : Submodule 𝒪[E] (Matrix m m (Module.End F E)))
    (hL : IsMatrixBimodule (coefficientMap F E) L.toAddSubgroup) (p : m)
    (hfg : L.FG) : (cornerSubmodule F E L hL p).FG := by
  rw [cornerSubmodule_eq_map]
  exact hfg.map _

omit [Module.Finite F E] [TopologicalSpace E] [IsNonarchimedeanLocalField E] in
/-- Fullness of the whole F-lattice gives fullness of the actual corner. -/
theorem corner_full (L : Submodule 𝒪[E] (Matrix m m (Module.End F E)))
    (hL : IsMatrixBimodule (coefficientMap F E) L.toAddSubgroup) (p : m)
    (hfull : Submodule.span F (L : Set (Matrix m m (Module.End F E))) = ⊤) :
    Submodule.span E (cornerSubmodule F E L hL p : Set (Module.End F E)) = ⊤ := by
  have hfullE := Submodule.span_eq_top_of_span_eq_top F E _ hfull
  have hset : (cornerSubmodule F E L hL p : Set (Module.End F E)) =
      (entryLinearMap E (Module.End F E) p p) '' (L : Set _) := by
    ext x
    constructor
    · intro hx
      exact ⟨single p p x, hx, by simp⟩
    · rintro ⟨z, hz, rfl⟩
      exact entry_mem_corner (coefficientMap F E) L.toAddSubgroup hL p hz p p
  rw [hset, ← Submodule.map_span, hfullE, Submodule.map_top]
  apply LinearMap.range_eq_top.mpr
  intro x
  exact ⟨single p p x, by simp⟩

/-- The rank coefficient is the actual extension degree, derived from full
span and finite generation rather than supplied as a numerical assumption. -/
theorem exists_corner_basis_degree
    (L : Submodule 𝒪[E] (Matrix m m (Module.End F E)))
    (hL : IsMatrixBimodule (coefficientMap F E) L.toAddSubgroup) (p : m)
    (hfg : L.FG)
    (hfull : Submodule.span F (L : Set (Matrix m m (Module.End F E))) = ⊤) :
    ∃ n : ℕ, ∃ _b : Basis (Fin n) 𝒪[E] (cornerSubmodule F E L hL p),
      n = Module.finrank F E := by
  obtain ⟨n, b, hn⟩ := exists_basis_full_submodule (cornerSubmodule F E L hL p)
    (corner_fg F E L hL p hfg) (corner_full F E L hL p hfull)
  exact ⟨n, b, hn.trans (Module.finrank_linearMap_self F E E)⟩

end ActualEndomorphismCorner
end PaperXI.MoritaCornerRank110
