import PaperICompletion7.ModuleTop
import Mathlib.RingTheory.LocalRing.Basic
import Mathlib.RingTheory.Ideal.Quotient.Basic
import Mathlib.LinearAlgebra.Basis.VectorSpace

/-!
The noncommutative local-ring specialization. The division-ring structure on
R / Jac(R) is derived from IsLocalRing R. It is not assumed, and no CommRing
or commutative residue-field convenience API is used.
-/
set_option autoImplicit false

namespace Komorebi.PaperICompletion7.LocalResidue

open Komorebi.SeedRankBasics
open Komorebi.PaperICompletion7.Nakayama
open Komorebi.PaperICompletion7.ModuleTop

universe u v w
variable {R : Type u} [Ring R] [IsLocalRing R]

/-- Two proper left ideals of a local ring cannot sum to the whole ring. -/
theorem proper_sup_ne_top (I J : Ideal R) (hI : I ≠ ⊤) (hJ : J ≠ ⊤) :
    I ⊔ J ≠ ⊤ := by
  intro h
  have hone : (1 : R) ∈ I ⊔ J := by rw [h]; trivial
  obtain ⟨a, ha, b, hb, hab⟩ := Submodule.mem_sup.mp hone
  rcases IsLocalRing.isUnit_or_isUnit_of_add_one hab with hu | hu
  · exact hI (I.eq_top_of_isUnit_mem ha hu)
  · exact hJ (J.eq_top_of_isUnit_mem hb hu)

/-- Uniqueness of the maximal left ideal, without commutativity. -/
theorem maximal_left_ideal_unique (I J : Ideal R)
    (hI : I.IsMaximal) (hJ : J.IsMaximal) : I = J := by
  by_contra h
  exact proper_sup_ne_top I J hI.ne_top hJ.ne_top (hI.coprime_of_ne hJ h)

/-- The actual ring Jacobson radical is maximal as a left ideal. -/
theorem jacobson_isMaximal : (Ring.jacobson R).IsMaximal := by
  obtain ⟨m, hm⟩ := Ideal.exists_maximal R
  have heq : Ring.jacobson R = m := by
    rw [Ring.jacobson_eq_sInf_isMaximal]
    apply le_antisymm (sInf_le hm)
    exact le_sInf fun I hI ↦ (maximal_left_ideal_unique m I hm hI).le
  exact heq.symm ▸ hm

/-- The division-ring structure is constructed on the actual radical quotient. -/
noncomputable abbrev residueDivisionRing (R : Type u) [Ring R] [IsLocalRing R] :
    DivisionRing (R ⧸ Ring.jacobson R) :=
  letI := jacobson_isMaximal (R := R)
  Ideal.Quotient.divisionRing (Ring.jacobson R)

variable {M : Type v} [AddCommGroup M] [Module R M]

/-- The printed local formula, with left dimension over the residue division ring. -/
theorem seedRank_eq_residue_dimension [Module.Finite R M] :
    letI := residueDivisionRing R
    seedRank R M = Module.rank (R ⧸ Ring.jacobson R) (RadicalTop R M) := by
  letI := residueDivisionRing R
  exact seedRank_eq_radicalTop.trans Submodule.rank_eq_spanRank_of_free.symm

/-- The natural-valued version uses the same constructed division-ring action. -/
theorem seedFinrank_eq_residue_finrank [Module.Finite R M] :
    letI := residueDivisionRing R
    seedFinrank R M = Module.finrank (R ⧸ Ring.jacobson R) (RadicalTop R M) := by
  letI := residueDivisionRing R
  exact seedFinrank_eq_radicalTop.trans Module.finrank_eq_spanFinrank_of_free.symm

/-- Finite generation descends to the residue division-ring vector space. -/
theorem residueTop_finite [Module.Finite R M] :
    letI := residueDivisionRing R
    Module.Finite (R ⧸ Ring.jacobson R) (RadicalTop R M) := by
  letI := residueDivisionRing R
  exact idealTop_finite (Ring.jacobson R) le_rfl

/-- Any lifts of a residue basis form a generating family over the original ring. -/
theorem residue_basis_lifts_generate [Module.Finite R M] {ι : Type w} :
    letI := residueDivisionRing R
    ∀ (b : Module.Basis ι (R ⧸ Ring.jacobson R) (RadicalTop R M))
      (x : ι → M),
      (∀ i, idealTopMap (Ring.jacobson R) (x i) = b i) →
      FamilyGenerates R M x := by
  letI := residueDivisionRing R
  intro b x hx
  exact lifts_generate (Ring.jacobson R) le_rfl b x hx b.span_eq

end Komorebi.PaperICompletion7.LocalResidue
