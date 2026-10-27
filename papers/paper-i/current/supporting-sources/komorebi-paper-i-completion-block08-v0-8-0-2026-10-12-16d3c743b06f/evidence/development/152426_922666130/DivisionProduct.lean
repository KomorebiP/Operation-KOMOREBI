import PaperICompletion8.DivisionBlock

/-! Finite products of matrix rings over a dependent family of division rings.
All scalar actions are actual left multiplication. No Algebra over a
noncommutative division ring is requested. -/
set_option autoImplicit false
set_option linter.unnecessarySimpa false

namespace Komorebi.PaperICompletion8.DivisionProduct

open scoped BigOperators
open Komorebi.SeedRankBasics Komorebi.SeedRankOperations
open Komorebi.PaperICompletion8.DivisionRows
open Komorebi.PaperICompletion8.DivisionBlock
open Komorebi.SemisimpleCompletion (seedFinrank_eq_of_exists_fin_family_iff)

universe u v w
variable {I : Type v} [Fintype I] [DecidableEq I]
variable {D : I → Type u} [∀ i, DivisionRing (D i)]
variable (d m : I → ℕ)

local instance (priority := 100) blockModuleAction (i : I) :
    Module (BlockAlgebra (k := D i) (d i)) (BlockModule (k := D i) (d i) (m i)) :=
  Matrix.Module.matrixModule

/-- The literal finite product ring in the nonsplit Wedderburn hypothesis. -/
abbrev DivisionProductAlgebra :=
  ∀ i : I, BlockAlgebra (k := D i) (d i)

/-- The literal product of the corresponding isotypic matrix modules. -/
abbrev DivisionProductModule :=
  ∀ i : I, BlockModule (k := D i) (d i) (m i)

/-- The maximum of the blockwise ceiling requirements.  `Finset.sup` gives
value zero for an empty product; Paper I assumes a nonempty block set. -/
def maxCeilDiv : ℕ :=
  Finset.univ.sup (fun i : I ↦ m i ⌈/⌉ d i)

/-- A family generates the literal product module exactly when its projection
to every isotypic block generates that block.  The proof assembles the
blockwise coefficient matrices into elements of the product algebra. -/
omit [Fintype I] in
theorem divisionProduct_familyGenerates_iff {r : ℕ}
    (v : Fin r → DivisionProductModule (D := D) d m) :
    FamilyGenerates (DivisionProductAlgebra (D := D) d)
        (DivisionProductModule (D := D) d m) v ↔
      ∀ i : I, LeftGenerates (fun j ↦ v j i) := by
  classical
  rw [FamilyGenerates, Generates, eq_top_iff,
    Submodule.top_le_span_range_iff_forall_exists_fun]
  constructor
  · intro h i X
    obtain ⟨c, hc⟩ := h (Pi.single i X)
    refine ⟨fun j ↦ c j i, ?_⟩
    calc
      X = (Pi.single i X : DivisionProductModule (D := D) d m) i := by simp
      _ = (∑ j, c j • v j) i := by rw [hc]
      _ = ∑ j, (c j i) * (v j i) := by
        simp only [Finset.sum_apply, Pi.smul_apply', block_smul_eq_mul]
  · intro h X
    choose c hc using fun i ↦ h i (X i)
    let a : Fin r → DivisionProductAlgebra (D := D) d :=
      fun j i ↦ c i j
    refine ⟨a, ?_⟩
    funext i
    simpa only [Finset.sum_apply, Pi.smul_apply', block_smul_eq_mul, a]
      using (hc i).symm

/-- Existence of `r` product generators is equivalent to the simultaneous
row-dimension inequalities on all simple blocks. -/
theorem exists_divisionProduct_generators_iff_coordinate_bounds
    {r : ℕ} (hd : ∀ i, 0 < d i) :
    (∃ v : Fin r → DivisionProductModule (D := D) d m,
      FamilyGenerates (DivisionProductAlgebra (D := D) d)
        (DivisionProductModule (D := D) d m) v) ↔
      ∀ i : I, m i ≤ r * d i := by
  constructor
  · rintro ⟨v, hv⟩ i
    exact multiplicity_le_of_leftGenerates (k := D i) (hd i)
      ((divisionProduct_familyGenerates_iff d m v).mp hv i)
  · intro h
    choose w hw using fun i ↦
      exists_leftGenerators_of_le (k := D i) (hd i) (h i)
    let v : Fin r → DivisionProductModule (D := D) d m :=
      fun j i ↦ w i j
    refine ⟨v, (divisionProduct_familyGenerates_iff d m v).mpr ?_⟩
    intro i
    simpa only [v] using hw i

/-- The finite-product assembly criterion: `r` seeds exist exactly when `r`
is at least the maximum blockwise ceiling. -/
theorem exists_divisionProduct_generators_iff_maxCeilDiv_le
    {r : ℕ} (hd : ∀ i, 0 < d i) :
    (∃ v : Fin r → DivisionProductModule (D := D) d m,
      FamilyGenerates (DivisionProductAlgebra (D := D) d)
        (DivisionProductModule (D := D) d m) v) ↔
      maxCeilDiv d m ≤ r := by
  rw [exists_divisionProduct_generators_iff_coordinate_bounds d m hd]
  constructor
  · intro h
    apply Finset.sup_le
    intro i hi
    apply (ceilDiv_le_iff_le_mul (hd i)).mpr
    simpa [Nat.mul_comm] using h i
  · intro h i
    have hblock : m i ⌈/⌉ d i ≤ maxCeilDiv d m :=
      Finset.le_sup (f := fun j : I ↦ m j ⌈/⌉ d j) (Finset.mem_univ i)
    have hceil : m i ⌈/⌉ d i ≤ r := hblock.trans h
    have hm : m i ≤ d i * r := (ceilDiv_le_iff_le_mul (hd i)).mp hceil
    simpa [Nat.mul_comm] using hm

/-- The displayed maximum is the least possible size of a finite generating
family for the split product module. -/
theorem maxCeilDiv_isLeast_product_generatorCount
    (hd : ∀ i, 0 < d i) :
    IsLeast
      {r : ℕ |
        ∃ v : Fin r → DivisionProductModule (D := D) d m,
          FamilyGenerates (DivisionProductAlgebra (D := D) d)
            (DivisionProductModule (D := D) d m) v}
      (maxCeilDiv d m) := by
  constructor
  · exact (exists_divisionProduct_generators_iff_maxCeilDiv_le
      (D := D) d m hd).mpr le_rfl
  · intro r hr
    exact (exists_divisionProduct_generators_iff_maxCeilDiv_le
      (D := D) d m hd).mp hr

/-- Paper I's finite semisimple multiplicity formula for the literal
decomposition displayed above. -/
theorem divisionProduct_seedFinrank_eq_maxCeilDiv
    (hd : ∀ i, 0 < d i) :
    seedFinrank (DivisionProductAlgebra (D := D) d)
        (DivisionProductModule (D := D) d m) =
      maxCeilDiv d m := by
  apply seedFinrank_eq_of_exists_fin_family_iff
  intro r
  exact exists_divisionProduct_generators_iff_maxCeilDiv_le (D := D) d m hd

/-- Cardinal-valued form of the finite semisimple multiplicity
formula. -/
theorem divisionProduct_seedRank_eq_maxCeilDiv
    (hd : ∀ i, 0 < d i) :
    seedRank (DivisionProductAlgebra (D := D) d)
        (DivisionProductModule (D := D) d m) =
      ((maxCeilDiv d m : ℕ) : Cardinal) := by
  classical
  obtain ⟨v, hv⟩ :=
    (exists_divisionProduct_generators_iff_maxCeilDiv_le (D := D) d m hd).mpr le_rfl
  let : Module.Finite (DivisionProductAlgebra (D := D) d)
      (DivisionProductModule (D := D) d m) :=
    Module.Finite.of_surjective
      (multiSeedMap (DivisionProductAlgebra (D := D) d)
        (DivisionProductModule (D := D) d m) v)
      ((familyGenerates_iff_surjective _ _ v).mp hv)
  rw [seedRank_eq_seedFinrank,
    divisionProduct_seedFinrank_eq_maxCeilDiv d m hd]

/-- Transport of the formula to any module supplied with an explicit linear
decomposition over the literal product algebra.  This is the exact hypothesis
needed after transporting an abstract semisimple algebra along a chosen
Wedderburn isomorphism. -/
theorem seedRank_eq_maxCeilDiv_of_divisionProduct_decomposition
    {X : Type (max u v)} [AddCommMonoid X]
    [Module (DivisionProductAlgebra (D := D) d) X]
    (e : X ≃ₗ[DivisionProductAlgebra (D := D) d]
      DivisionProductModule (D := D) d m)
    (hd : ∀ i, 0 < d i) :
    seedRank (DivisionProductAlgebra (D := D) d) X =
      ((maxCeilDiv d m : ℕ) : Cardinal) := by
  rw [seedRank_linearEquiv e,
    divisionProduct_seedRank_eq_maxCeilDiv d m hd]

end Komorebi.PaperICompletion8.DivisionProduct
