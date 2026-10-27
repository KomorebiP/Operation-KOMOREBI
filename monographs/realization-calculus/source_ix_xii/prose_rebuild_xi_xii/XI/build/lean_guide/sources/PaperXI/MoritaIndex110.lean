import PaperXI.MoritaCornerRank110
import PaperXI.MoritaQuotient110
import PaperXI.FreeLatticeCard110
import PaperXI.MoritaUniformizer110
import Mathlib.Algebra.Module.Submodule.Pointwise
import Mathlib.GroupTheory.Index

/-! Actual corner power quotients and the diagonal matrix-lattice index. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.MoritaIndex110
open scoped Pointwise
open PaperXI.MoritaLattice110 PaperXI.MoritaCornerRank110

section PowerQuotient
variable {R D : Type*} [CommRing R] [Ring D] [Module R D]

/-- An ambient left-power subgroup restricted to its actual corner module is
exactly the internally defined principal-ideal-power submodule. -/
theorem leftPower_addSubgroupOf_eq (φ : R →+* D)
    (hsmul : ∀ (r : R) (x : D), r • x = φ r * x)
    (Λ : Submodule R D) (π : R) (u : Dˣ) (hπ : (u : D) = φ π) (n : ℕ) :
    (leftPower Λ.toAddSubgroup u (n : ℤ)).addSubgroupOf Λ.toAddSubgroup =
      (((Ideal.span {π}) ^ n) • (⊤ : Submodule R Λ)).toAddSubgroup := by
  ext x
  change (x : D) ∈ leftPower Λ.toAddSubgroup u (n : ℤ) ↔
    x ∈ ((Ideal.span {π}) ^ n) • (⊤ : Submodule R Λ)
  rw [Submodule.mem_smul_top_iff, Ideal.span_singleton_pow,
    Submodule.ideal_span_singleton_smul, Submodule.mem_smul_pointwise_iff_exists]
  simp only [leftPower, AddSubgroup.mem_map]
  have hp : ((u ^ (n : ℤ) : Dˣ) : D) = φ (π ^ n) := by
    simp [hπ]
  constructor
  · rintro ⟨z, hz, hx⟩
    change ((u ^ (n : ℤ) : Dˣ) : D) * z = (x : D) at hx
    exact ⟨z, hz, by simpa only [hsmul, hp] using hx⟩
  · rintro ⟨z, hz, hx⟩
    refine ⟨z, hz, ?_⟩
    change ((u ^ (n : ℤ) : Dˣ) : D) * z = (x : D)
    simpa only [hsmul, hp] using hx

/-- The literal ambient-power quotient obtains its cardinality from an actual
basis and an actual nonzero prime principal ideal. -/
theorem card_leftPower_quotient {ι : Type*} [Fintype ι] [DecidableEq ι]
    [IsDedekindDomain R] (φ : R →+* D)
    (hsmul : ∀ (r : R) (x : D), r • x = φ r * x)
    (Λ : Submodule R D) (b : Module.Basis ι R Λ)
    (π : R) [(Ideal.span {π} : Ideal R).IsPrime]
    (hI : (Ideal.span {π} : Ideal R) ≠ ⊥)
    (u : Dˣ) (hπ : (u : D) = φ π) (n : ℕ) :
    Nat.card (Λ.toAddSubgroup ⧸
      (leftPower Λ.toAddSubgroup u (n : ℤ)).addSubgroupOf Λ.toAddSubgroup) =
      Nat.card (R ⧸ (Ideal.span {π} : Ideal R)) ^ (n * Fintype.card ι) := by
  rw [leftPower_addSubgroupOf_eq φ hsmul Λ π u hπ n]
  exact PaperXI.FreeLatticeCard110.card_quotient_prime_pow b
    (Ideal.span {π}) hI n

end PowerQuotient

section ActualDiagonalIndex
open Module Matrix ValuativeRel
variable (F E : Type*) [Field F] [Field E] [Algebra F E]
  [Module.Finite F E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E]
variable {m : Type*} [Fintype m] [DecidableEq m]

/-- Multiplication by an actual nonzero integer-ring element, as an invertible
F-linear endomorphism of E. -/
def coefficientUnit (π : 𝒪[E]) (hπ : (π : E) ≠ 0) : (Module.End F E)ˣ :=
  Units.map (Algebra.lmul F E).toRingHom (Units.mk0 (π : E) hπ)

omit [Module.Finite F E] [TopologicalSpace E] [IsNonarchimedeanLocalField E] in
@[simp] theorem coefficientUnit_coe (π : 𝒪[E]) (hπ : (π : E) ≠ 0) :
    (coefficientUnit F E π hπ : Module.End F E) = coefficientMap F E π := rfl

/-- The cardinality of the actual diagonal intersection is derived from matrix
units, radical normalization, a finite full corner, and its residue quotients. -/
theorem card_diagonal_intersection
    (L : Submodule 𝒪[E] (Matrix m m (Module.End F E)))
    (hL : IsMatrixBimodule (coefficientMap F E) L.toAddSubgroup) (p : m)
    (hfg : L.FG)
    (hfull : Submodule.span F (L : Set (Matrix m m (Module.End F E))) = ⊤)
    (π : 𝒪[E]) (hπirr : Irreducible π) (u : (Module.End F E)ˣ)
    (hπ : (u : Module.End F E) = coefficientMap F E π)
    (hu : u ∈ normalizingUnits (corner L.toAddSubgroup p)) (a : m → ℤ) :
    Nat.card (L.toAddSubgroup ⧸
      (L.toAddSubgroup ⊓ L.toAddSubgroup.map
        (unitConjugation (diagonalUnit (fun i => u ^ a i))).toAddMonoidHom).addSubgroupOf
          L.toAddSubgroup) =
      Nat.card 𝓀[E] ^ (Module.finrank F E * ∑ i, ∑ j, (a i - a j).toNat) := by
  let Λ := cornerSubmodule F E L hL p
  obtain ⟨n, b, hn⟩ := exists_corner_basis_degree F E L hL p hfg hfull
  let I : Ideal 𝒪[E] := Ideal.span {π}
  have hI : I ≠ ⊥ := PaperXI.MoritaUniformizer110.uniformizerIdeal_ne_bot π hπirr
  let : I.IsPrime := PaperXI.MoritaUniformizer110.uniformizerIdeal_isPrime π hπirr
  have hsmul : ∀ (r : 𝒪[E]) (x : Module.End F E),
      r • x = coefficientMap F E r * x := by intro r x; ext v; rfl
  have hcoordinate (k : ℕ) :
      Nat.card (Λ.toAddSubgroup ⧸
        (leftPower Λ.toAddSubgroup u (k : ℤ)).addSubgroupOf Λ.toAddSubgroup) =
          Nat.card 𝓀[E] ^ (k * Module.finrank F E) := by
    rw [card_leftPower_quotient (coefficientMap F E) hsmul Λ b π hI u hπ k]
    have hq : Nat.card (𝒪[E] ⧸ (Ideal.span {π} : Ideal 𝒪[E])) = Nat.card 𝓀[E] :=
      PaperXI.MoritaUniformizer110.card_uniformizer_quotient π hπirr
    rw [hq]
    simp [hn]
  have hbase : L.toAddSubgroup = entrywise (fun _ _ => Λ.toAddSubgroup) := by
    exact eq_matrix_corner (coefficientMap F E) L.toAddSubgroup hL p
  rw [intersection_eq_nonnegative_entrywise (coefficientMap F E) L.toAddSubgroup
    hL p π u hπ hu a]
  change Nat.card (L.toAddSubgroup ⧸
    (entrywise (fun i j => leftPower Λ.toAddSubgroup u ((a i - a j).toNat : ℤ))).addSubgroupOf
      L.toAddSubgroup) = _
  rw [hbase, PaperXI.MoritaQuotient110.card_matrix_quotient]
  simp_rw [hcoordinate, Finset.prod_pow_eq_pow_sum]
  congr 1
  simp_rw [← Finset.sum_mul]
  exact Nat.mul_comm _ _

/-- The original scalar radical-commutation equality supplies the corner
normalization used above; it is not an additional index premise. -/
theorem diagonal_relIndex_of_radical_commutation
    (L : Submodule 𝒪[E] (Matrix m m (Module.End F E)))
    (hL : IsMatrixBimodule (coefficientMap F E) L.toAddSubgroup) (p : m)
    (hfg : L.FG)
    (hfull : Submodule.span F (L : Set (Matrix m m (Module.End F E))) = ⊤)
    (π : 𝒪[E]) (hπirr : Irreducible π) (u : (Module.End F E)ˣ)
    (hπ : (u : Module.End F E) = coefficientMap F E π)
    (hcomm : L.toAddSubgroup.map
        (AddMonoidHom.mulLeft ((diagonalUnit (fun _ : m => u) :
          (Matrix m m (Module.End F E))ˣ) : Matrix m m (Module.End F E))) =
      L.toAddSubgroup.map
        (AddMonoidHom.mulRight ((diagonalUnit (fun _ : m => u) :
          (Matrix m m (Module.End F E))ˣ) : Matrix m m (Module.End F E))))
    (a : m → ℤ) :
    (L.toAddSubgroup ⊓ L.toAddSubgroup.map
      (unitConjugation (diagonalUnit (fun i => u ^ a i))).toAddMonoidHom).relIndex
        L.toAddSubgroup =
      Nat.card 𝓀[E] ^ (Module.finrank F E * ∑ i, ∑ j, (a i - a j).toNat) := by
  exact card_diagonal_intersection F E L hL p hfg hfull π hπirr u hπ
    (corner_normalizes_of_scalar_commutation L.toAddSubgroup u p hcomm) a

end ActualDiagonalIndex
end PaperXI.MoritaIndex110
