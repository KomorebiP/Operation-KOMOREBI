import KomorebiVerification.SeedRankBasics
import KomorebiVerification.SeedRankOperations
import KomorebiVerification.SemisimpleSeedRank
import KomorebiVerification.FullMatrixCyclicity

/-!
# Completion bridges for the semisimple claims in Paper I

This file connects the row-space generator count proved in
`SemisimpleSeedRank` to the general `SeedRankBasics` invariant.  It then
assembles finitely many split simple blocks in the literal product algebra

`∀ i, Matrix (Fin (d i)) (Fin (d i)) k`

acting coordinatewise on the literal product module

`∀ i, Matrix (Fin (d i)) (Fin (m i)) k`.

Thus the assembly theorem assumes the displayed Wedderburn decomposition as
data: it does not formalize or invoke a classification theorem.  The final
corollaries are literal bridges to the full-matrix cyclicity and multiplicity
obstruction statements in Paper I.
-/

set_option autoImplicit false

-- Keep theorem bodies stable in this audit release while making the build warning-fatal.
set_option linter.unnecessarySimpa false
set_option linter.style.haveILetI false
set_option linter.unusedSectionVars false

namespace Komorebi.SemisimpleCompletion

open scoped BigOperators

open Komorebi.SeedRankBasics
open Komorebi.SeedRankOperations
open Komorebi.SemisimpleSeedRank

universe u v

variable {k : Type u} [Field k]

abbrev BlockAlgebra (d : ℕ) := Matrix (Fin d) (Fin d) k

abbrev BlockModule (d m : ℕ) := Matrix (Fin d) (Fin m) k

section BlockModules

local instance (priority := 100) blockModuleAction (d m : ℕ) :
    Module (BlockAlgebra (k := k) d) (BlockModule (k := k) d m) :=
  Matrix.Module.matrixModule

/-- The scoped matrix-module action is ordinary multiplication on a
rectangular matrix. -/
theorem block_smul_eq_mul {d m : ℕ}
    (A : BlockAlgebra (k := k) d) (V : BlockModule (k := k) d m) :
    A • V = A * V := by
  ext i j
  change (∑ b, A i b • V b) j = ∑ b, A i b * V b j
  simp

/-- The bespoke row-space notion is exactly `FamilyGenerates` for the
canonical full-matrix module. -/
theorem leftGenerates_iff_familyGenerates {r d m : ℕ}
    (v : Fin r → BlockModule (k := k) d m) :
    LeftGenerates v ↔
      FamilyGenerates (BlockAlgebra (k := k) d) (BlockModule (k := k) d m) v := by
  classical
  rw [FamilyGenerates, Generates, eq_top_iff,
    Submodule.top_le_span_range_iff_forall_exists_fun]
  constructor
  · intro h X
    obtain ⟨A, hA⟩ := h X
    refine ⟨A, ?_⟩
    simpa only [block_smul_eq_mul] using hA.symm
  · intro h X
    obtain ⟨A, hA⟩ := h X
    refine ⟨A, ?_⟩
    simpa only [block_smul_eq_mul] using hA.symm

/-- A reusable minimum principle: if `c ≤ r` exactly characterizes the
existence of a generating `Fin r`-family, then the general natural-valued
seed rank is `c`.  The existence direction supplies finite generation, so no
separate finiteness hypothesis is hidden here. -/
theorem seedFinrank_eq_of_exists_fin_family_iff
    {A : Type u} {M : Type v}
    [Semiring A] [AddCommMonoid M] [Module A M]
    (c : ℕ)
    (hcount : ∀ r : ℕ,
      (∃ v : Fin r → M, FamilyGenerates A M v) ↔ c ≤ r) :
    seedFinrank A M = c := by
  classical
  obtain ⟨v, hv⟩ := (hcount c).mpr le_rfl
  letI : Module.Finite A M :=
    Module.Finite.of_surjective (multiSeedMap A M v)
      ((familyGenerates_iff_surjective A M v).mp hv)
  apply le_antisymm
  · rw [seedFinrank, ← hv]
    refine (Submodule.spanFinrank_span_le_ncard_of_finite
      (Set.finite_range v)).trans ?_
    rw [← Set.image_univ]
    simpa using Set.ncard_image_le (f := v) (s := Set.univ)
  · obtain ⟨s, hsCard, hsSpan⟩ :=
      Module.Finite.fg_top.exists_span_finset_card_eq_spanFinrank
        (R := A) (M := M)
    let e : Fin s.card ≃ {x : M // x ∈ s} := by
      simpa using (Fintype.equivFin {x : M // x ∈ s}).symm
    let w : Fin s.card → M := fun j ↦ (e j : M)
    have hwRange : Set.range w = (s : Set M) := by
      ext x
      constructor
      · rintro ⟨j, rfl⟩
        exact (e j).property
      · intro hx
        let y : {x : M // x ∈ s} := ⟨x, hx⟩
        refine ⟨e.symm y, ?_⟩
        simp [w, y]
    have hw : FamilyGenerates A M w := by
      rw [FamilyGenerates, Generates, hwRange, hsSpan]
    have hc : c ≤ s.card := (hcount s.card).mp ⟨w, hw⟩
    simpa [seedFinrank, hsCard] using hc

/-- The one-block ceiling count is the general `SeedRankBasics.seedFinrank`,
not merely a bespoke minimum. -/
theorem oneBlock_seedFinrank_eq_ceilDiv {d m : ℕ} (hd : 0 < d) :
    seedFinrank (BlockAlgebra (k := k) d) (BlockModule (k := k) d m) =
      m ⌈/⌉ d := by
  apply seedFinrank_eq_of_exists_fin_family_iff (c := m ⌈/⌉ d)
  intro r
  constructor
  · rintro ⟨v, hv⟩
    have hm : m ≤ r * d := (exists_leftGenerators_iff (k := k) hd).mp
      ⟨v, (leftGenerates_iff_familyGenerates v).mpr hv⟩
    apply (ceilDiv_le_iff_le_mul hd).mpr
    simpa [Nat.mul_comm] using hm
  · intro hr
    have hm : m ≤ r * d := by
      simpa [Nat.mul_comm] using (ceilDiv_le_iff_le_mul hd).mp hr
    obtain ⟨v, hv⟩ := (exists_leftGenerators_iff (k := k) hd).mpr hm
    exact ⟨v, (leftGenerates_iff_familyGenerates v).mp hv⟩

/-- Cardinal-valued form of the same one-block formula. -/
theorem oneBlock_seedRank_eq_ceilDiv {d m : ℕ} (hd : 0 < d) :
    seedRank (BlockAlgebra (k := k) d) (BlockModule (k := k) d m) =
      ((m ⌈/⌉ d : ℕ) : Cardinal) := by
  classical
  have hfin : Module.Finite (BlockAlgebra (k := k) d)
      (BlockModule (k := k) d m) := by
    obtain ⟨v, hv⟩ := exists_leftGenerators_of_le (k := k)
      (r := m ⌈/⌉ d) hd (by
        have hm : m ≤ d * (m ⌈/⌉ d) := (ceilDiv_le_iff_le_mul hd).mp le_rfl
        simpa [Nat.mul_comm] using hm)
    exact Module.Finite.of_surjective
      (multiSeedMap (BlockAlgebra (k := k) d) (BlockModule (k := k) d m) v)
      ((familyGenerates_iff_surjective _ _ v).mp
        ((leftGenerates_iff_familyGenerates v).mp hv))
  letI := hfin
  rw [seedRank_eq_seedFinrank,
    oneBlock_seedFinrank_eq_ceilDiv (k := k) hd]

section FiniteProduct

variable {I : Type v} [Fintype I] [DecidableEq I]
variable (d m : I → ℕ)

/-- The literal finite product algebra in the split Wedderburn hypothesis. -/
abbrev SplitProductAlgebra :=
  ∀ i : I, BlockAlgebra (k := k) (d i)

/-- The literal product of the corresponding isotypic matrix modules. -/
abbrev SplitProductModule :=
  ∀ i : I, BlockModule (k := k) (d i) (m i)

/-- The maximum of the blockwise ceiling requirements.  `Finset.sup` gives
value zero for an empty product; Paper I assumes a nonempty block set. -/
def maxCeilDiv : ℕ :=
  Finset.univ.sup (fun i : I ↦ m i ⌈/⌉ d i)

/-- A family generates the literal product module exactly when its projection
to every isotypic block generates that block.  The proof assembles the
blockwise coefficient matrices into elements of the product algebra. -/
theorem splitProduct_familyGenerates_iff {r : ℕ}
    (v : Fin r → SplitProductModule (k := k) d m) :
    FamilyGenerates (SplitProductAlgebra (k := k) d)
        (SplitProductModule (k := k) d m) v ↔
      ∀ i : I, LeftGenerates (fun j ↦ v j i) := by
  classical
  rw [FamilyGenerates, Generates, eq_top_iff,
    Submodule.top_le_span_range_iff_forall_exists_fun]
  constructor
  · intro h i X
    obtain ⟨c, hc⟩ := h (Pi.single i X)
    refine ⟨fun j ↦ c j i, ?_⟩
    calc
      X = (Pi.single i X : SplitProductModule (k := k) d m) i := by simp
      _ = (∑ j, c j • v j) i := by rw [hc]
      _ = ∑ j, (c j i) * (v j i) := by
        simp only [Finset.sum_apply, Pi.smul_apply', block_smul_eq_mul]
  · intro h X
    choose c hc using fun i ↦ h i (X i)
    let a : Fin r → SplitProductAlgebra (k := k) d :=
      fun j i ↦ c i j
    refine ⟨a, ?_⟩
    funext i
    simpa only [Finset.sum_apply, Pi.smul_apply', block_smul_eq_mul, a]
      using (hc i).symm

/-- Existence of `r` product generators is equivalent to the simultaneous
row-dimension inequalities on all simple blocks. -/
theorem exists_splitProduct_generators_iff_coordinate_bounds
    {r : ℕ} (hd : ∀ i, 0 < d i) :
    (∃ v : Fin r → SplitProductModule (k := k) d m,
      FamilyGenerates (SplitProductAlgebra (k := k) d)
        (SplitProductModule (k := k) d m) v) ↔
      ∀ i : I, m i ≤ r * d i := by
  constructor
  · rintro ⟨v, hv⟩ i
    exact multiplicity_le_of_leftGenerates (k := k) (hd i)
      ((splitProduct_familyGenerates_iff d m v).mp hv i)
  · intro h
    choose w hw using fun i ↦
      exists_leftGenerators_of_le (k := k) (hd i) (h i)
    let v : Fin r → SplitProductModule (k := k) d m :=
      fun j i ↦ w i j
    refine ⟨v, (splitProduct_familyGenerates_iff d m v).mpr ?_⟩
    intro i
    simpa only [v] using hw i

/-- The finite-product assembly criterion: `r` seeds exist exactly when `r`
is at least the maximum blockwise ceiling. -/
theorem exists_splitProduct_generators_iff_maxCeilDiv_le
    {r : ℕ} (hd : ∀ i, 0 < d i) :
    (∃ v : Fin r → SplitProductModule (k := k) d m,
      FamilyGenerates (SplitProductAlgebra (k := k) d)
        (SplitProductModule (k := k) d m) v) ↔
      maxCeilDiv d m ≤ r := by
  rw [exists_splitProduct_generators_iff_coordinate_bounds d m hd]
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
        ∃ v : Fin r → SplitProductModule (k := k) d m,
          FamilyGenerates (SplitProductAlgebra (k := k) d)
            (SplitProductModule (k := k) d m) v}
      (maxCeilDiv d m) := by
  constructor
  · exact (exists_splitProduct_generators_iff_maxCeilDiv_le
      (k := k) d m hd).mpr le_rfl
  · intro r hr
    exact (exists_splitProduct_generators_iff_maxCeilDiv_le
      (k := k) d m hd).mp hr

/-- Paper I's finite split-semisimple multiplicity formula for the literal
decomposition displayed above. -/
theorem splitProduct_seedFinrank_eq_maxCeilDiv
    (hd : ∀ i, 0 < d i) :
    seedFinrank (SplitProductAlgebra (k := k) d)
        (SplitProductModule (k := k) d m) =
      maxCeilDiv d m := by
  apply seedFinrank_eq_of_exists_fin_family_iff
  intro r
  exact exists_splitProduct_generators_iff_maxCeilDiv_le (k := k) d m hd

/-- Cardinal-valued form of the finite split-semisimple multiplicity
formula. -/
theorem splitProduct_seedRank_eq_maxCeilDiv
    (hd : ∀ i, 0 < d i) :
    seedRank (SplitProductAlgebra (k := k) d)
        (SplitProductModule (k := k) d m) =
      ((maxCeilDiv d m : ℕ) : Cardinal) := by
  classical
  obtain ⟨v, hv⟩ :=
    (exists_splitProduct_generators_iff_maxCeilDiv_le (k := k) d m hd).mpr le_rfl
  letI : Module.Finite (SplitProductAlgebra (k := k) d)
      (SplitProductModule (k := k) d m) :=
    Module.Finite.of_surjective
      (multiSeedMap (SplitProductAlgebra (k := k) d)
        (SplitProductModule (k := k) d m) v)
      ((familyGenerates_iff_surjective _ _ v).mp hv)
  rw [seedRank_eq_seedFinrank,
    splitProduct_seedFinrank_eq_maxCeilDiv d m hd]

/-- Transport of the formula to any module supplied with an explicit linear
decomposition over the literal product algebra.  This is the exact hypothesis
needed after transporting an abstract split semisimple algebra along a chosen
Wedderburn isomorphism. -/
theorem seedRank_eq_maxCeilDiv_of_splitProduct_decomposition
    {X : Type (max u v)} [AddCommMonoid X]
    [Module (SplitProductAlgebra (k := k) d) X]
    (e : X ≃ₗ[SplitProductAlgebra (k := k) d]
      SplitProductModule (k := k) d m)
    (hd : ∀ i, 0 < d i) :
    seedRank (SplitProductAlgebra (k := k) d) X =
      ((maxCeilDiv d m : ℕ) : Cardinal) := by
  rw [seedRank_linearEquiv e,
    splitProduct_seedRank_eq_maxCeilDiv d m hd]

end FiniteProduct

end BlockModules

section AbstractSplitDecomposition

variable {I : Type u} [Fintype I] [DecidableEq I]
variable (d m : I → ℕ)

attribute [local instance] RingHomInvPair.of_ringEquiv

local instance abstractSplitBlockModuleAction (i : I) :
    Module (BlockAlgebra (k := k) (d i))
      (BlockModule (k := k) (d i) (m i)) :=
  Matrix.Module.matrixModule

/--
Exact transport form of Paper I's split-semisimple hypothesis.

The hypotheses supply, rather than derive:

* a chosen `k`-algebra isomorphism from the abstract acting algebra `A` to
  the finite product of full matrix algebras; and
* a chosen semilinear equivalence from `X` to the corresponding product of
  isotypic matrix modules, whose scalar law is precisely that algebra
  isomorphism.

No existence or classification part of Wedderburn--Artin is asserted here.
-/
theorem semisimple_seedRank_eq_maxCeilDiv_of_equivalences
    {A X : Type u} [Semiring A] [Algebra k A]
    [AddCommMonoid X] [Module A X]
    (algebraEquiv : A ≃ₐ[k] SplitProductAlgebra (k := k) d)
    (moduleEquiv : X ≃ₛₗ[RingHomClass.toRingHom algebraEquiv.toRingEquiv]
      SplitProductModule (k := k) d m)
    (hd : ∀ i, 0 < d i) :
    seedRank A X = ((maxCeilDiv d m : ℕ) : Cardinal) := by
  letI : RingHomSurjective
      (RingHomClass.toRingHom algebraEquiv.toRingEquiv) :=
    ⟨algebraEquiv.surjective⟩
  calc
    seedRank A X =
        seedRank (SplitProductAlgebra (k := k) d)
          (SplitProductModule (k := k) d m) :=
      seedRank_eq_of_bijective_semilinear moduleEquiv.toLinearMap
        moduleEquiv.bijective
    _ = ((maxCeilDiv d m : ℕ) : Cardinal) :=
      splitProduct_seedRank_eq_maxCeilDiv (k := k) d m hd

end AbstractSplitDecomposition

section FullMatrixCorollaries

variable {n : ℕ}

/-- `FullMatrixCyclicity.IsCyclic` is exactly singleton generation in the
general seed-rank module for the natural full-matrix action. -/
theorem fullMatrix_isCyclic_iff_generates (x : Fin n → k) :
    Komorebi.FullMatrixCyclicity.IsCyclic x ↔
      Generates (Matrix (Fin n) (Fin n) k) (Fin n → k) {x} := by
  rw [generates_singleton_iff_surjective]
  constructor
  · intro hx y
    obtain ⟨A, hA⟩ := hx y
    refine ⟨A, ?_⟩
    simpa [oneSeedMap_apply, Matrix.smul_eq_mulVec] using hA
  · intro hx y
    obtain ⟨A, hA⟩ := hx y
    refine ⟨A, ?_⟩
    simpa [oneSeedMap_apply, Matrix.smul_eq_mulVec] using hA

/-- Literal Paper I statement: every nonzero coordinate vector generates the
natural module over the full matrix algebra. -/
theorem fullMatrix_every_nonzero_vector_generates
    {x : Fin n → k} (hx : x ≠ 0) :
    Generates (Matrix (Fin n) (Fin n) k) (Fin n → k) {x} :=
  (fullMatrix_isCyclic_iff_generates x).mp
    (Komorebi.FullMatrixCyclicity.isCyclic_of_ne_zero hx)

/-- The nonzero natural full-matrix module is cyclic in the general
`SeedRankBasics` sense. -/
theorem fullMatrix_module_cyclic (hn : 0 < n) :
    Cyclic (Matrix (Fin n) (Fin n) k) (Fin n → k) := by
  let i₀ : Fin n := ⟨0, hn⟩
  let x : Fin n → k := Pi.single i₀ 1
  have hx : x ≠ 0 := by
    intro hzero
    have hentry := congrFun hzero i₀
    simpa [x] using hentry
  exact ⟨x, fullMatrix_every_nonzero_vector_generates hx⟩

/-- Literal seed-rank corollary for the natural full-matrix module. -/
theorem fullMatrix_seedRank_eq_one (hn : 0 < n) :
    seedRank (Matrix (Fin n) (Fin n) k) (Fin n → k) = 1 := by
  classical
  have hcyc := fullMatrix_module_cyclic (k := k) hn
  obtain ⟨x, hx⟩ := hcyc
  have hsurj : Function.Surjective
      (oneSeedMap (Matrix (Fin n) (Fin n) k) (Fin n → k) x) :=
    (generates_singleton_iff_surjective _ _ x).mp hx
  letI : Module.Finite (Matrix (Fin n) (Fin n) k) (Fin n → k) :=
    Module.Finite.of_surjective
      (oneSeedMap (Matrix (Fin n) (Fin n) k) (Fin n → k) x) hsurj
  letI : Nonempty (Fin n) := ⟨⟨0, hn⟩⟩
  exact (seedRank_eq_one_iff_cyclic
    (Matrix (Fin n) (Fin n) k) (Fin n → k)).mpr ⟨x, hx⟩

end FullMatrixCorollaries

section MultiplicityCorollaries

variable {r d m : ℕ}

local instance multiplicityBlockModuleAction (d m : ℕ) :
    Module (BlockAlgebra (k := k) d) (BlockModule (k := k) d m) :=
  Matrix.Module.matrixModule

/-- Literal multiplicity obstruction in the general generation language:
any `r` seeds for `m` copies of the natural `d`-dimensional module force
`ceil(m/d) ≤ r`. -/
theorem multiplicity_obstruction
    (hd : 0 < d) {v : Fin r → BlockModule (k := k) d m}
    (hv : FamilyGenerates (BlockAlgebra (k := k) d)
      (BlockModule (k := k) d m) v) :
    m ⌈/⌉ d ≤ r := by
  apply (ceilDiv_le_iff_le_mul hd).mpr
  have hm : m ≤ r * d := multiplicity_le_of_leftGenerates (k := k) hd
    ((leftGenerates_iff_familyGenerates v).mpr hv)
  simpa [Nat.mul_comm] using hm

/-- Literal Paper I formula for the diagonal action on `m` copies of the
natural `d`-dimensional module. -/
theorem multiplicity_seedRank_formula (hd : 0 < d) :
    seedRank (BlockAlgebra (k := k) d) (BlockModule (k := k) d m) =
      ((m ⌈/⌉ d : ℕ) : Cardinal) :=
  oneBlock_seedRank_eq_ceilDiv (k := k) hd

end MultiplicityCorollaries

end Komorebi.SemisimpleCompletion

#print axioms Komorebi.SemisimpleCompletion.oneBlock_seedRank_eq_ceilDiv
#print axioms Komorebi.SemisimpleCompletion.splitProduct_seedRank_eq_maxCeilDiv
#print axioms Komorebi.SemisimpleCompletion.semisimple_seedRank_eq_maxCeilDiv_of_equivalences
#print axioms Komorebi.SemisimpleCompletion.fullMatrix_seedRank_eq_one
#print axioms Komorebi.SemisimpleCompletion.multiplicity_obstruction
