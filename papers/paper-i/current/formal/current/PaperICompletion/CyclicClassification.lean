import KomorebiVerification.SingleOperatorGraph
import Mathlib.Algebra.Module.PID
import Mathlib.LinearAlgebra.AnnihilatingPolynomial
import Mathlib.RingTheory.AdjoinRoot

/-!
# The cyclic-vector / minimal-characteristic polynomial bridge

Unlike the historical certificate-assembly theorem, these declarations do
not accept the desired polynomial equivalence as a hypothesis.  The reverse
implication uses Mathlib's proven PID-module annihilator-attainment theorem.
All maps are the actual polynomial action of the given endomorphism.
-/

set_option autoImplicit false
noncomputable section

namespace Komorebi.PaperICompletion.CyclicClassification
open Komorebi.SingleOperatorGraph
open Polynomial

universe u v
variable {k : Type u} [Field k]
variable {V : Type v} [AddCommGroup V] [Module k V]

/-- The polynomial-module presentation of the orbit of a specified vector. -/
def orbitMap (T : Module.End k V) (x : V) : k[X] →ₗ[k[X]] Module.AEval' T :=
  LinearMap.toSpanSingleton k[X] (Module.AEval' T) (Module.AEval'.of T x)

@[simp]
theorem orbitMap_apply (T : Module.End k V) (x : V) (p : k[X]) :
    orbitMap T x p = Module.AEval'.of T (aeval T p x) := rfl

/-- The span definition of one seed is equivalent to surjectivity of its actual orbit map. -/
theorem singleton_generates_iff_orbitMap_surjective (T : Module.End k V) (x : V) :
    FamilyGenerates T (fun _ : Fin 1 ↦ x) ↔ Function.Surjective (orbitMap T x) := by
  have hrange : Set.range (orbitFamily T (fun _ : Fin 1 ↦ x)) =
      ((evalVector T x).range : Set V) := by
    ext y
    constructor
    · rintro ⟨⟨_i, p⟩, rfl⟩
      exact ⟨p, rfl⟩
    · rintro ⟨p, rfl⟩
      exact ⟨(0, p), rfl⟩
  change Submodule.span k (Set.range (orbitFamily T (fun _ : Fin 1 ↦ x))) = ⊤ ↔ _
  rw [hrange, Submodule.span_eq, LinearMap.range_eq_top]
  rfl

/-- Eliminate the arbitrary indexing function from the one-seed predicate. -/
theorem hasCyclicVector_iff_exists_surjective (T : Module.End k V) :
    HasCyclicVector T ↔ ∃ x : V, Function.Surjective (orbitMap T x) := by
  constructor
  · rintro ⟨s, hs⟩
    have heq : s = fun _ : Fin 1 ↦ s 0 := by
      funext i
      exact congrArg s (Subsingleton.elim i 0)
    rw [heq] at hs
    exact ⟨s 0, (singleton_generates_iff_orbitMap_surjective T (s 0)).mp hs⟩
  · rintro ⟨x, hx⟩
    exact ⟨fun _ : Fin 1 ↦ x, (singleton_generates_iff_orbitMap_surjective T x).mpr hx⟩

/-- A cyclic vector has exactly the annihilator of the whole polynomial module. -/
theorem orbitMap_ker_eq_annihilator_of_surjective
    (T : Module.End k V) (x : V) (hx : Function.Surjective (orbitMap T x)) :
    (orbitMap T x).ker = Module.annihilator k[X] (Module.AEval' T) := by
  ext p
  change p • Module.AEval'.of T x = 0 ↔
    p ∈ Module.annihilator k[X] (Module.AEval' T)
  rw [Module.mem_annihilator]
  constructor
  · intro hp y
    obtain ⟨q, rfl⟩ := hx y
    change p • (q • Module.AEval'.of T x) = 0
    rw [smul_smul, mul_comm p q, ← smul_smul, hp, smul_zero]
  · intro hp
    exact hp (Module.AEval'.of T x)

/-- Identify the orbit's quotient with the minimal-polynomial quotient, from kernel equality. -/
def minpolyQuotientEquivOrbit (T : Module.End k V) (x : V)
    (hx : (orbitMap T x).ker = Module.annihilator k[X] (Module.AEval' T)) :
    (k[X] ⧸ Ideal.span {minpoly k T}) ≃ₗ[k[X]] (orbitMap T x).range :=
  (Submodule.quotEquivOfEq _ _
    ((Polynomial.span_minpoly_eq_annihilator k T).trans hx.symm)).trans
    (orbitMap T x).quotKerEquivRange

/-- The cyclic orbit has dimension equal to the degree of the minimal polynomial. -/
theorem orbit_finrank_eq_minpoly_degree (T : Module.End k V) (x : V)
    (hx : (orbitMap T x).ker = Module.annihilator k[X] (Module.AEval' T)) :
    Module.finrank k (orbitMap T x).range = (minpoly k T).natDegree := by
  rw [← ((minpolyQuotientEquivOrbit T x hx).restrictScalars k).finrank_eq]
  exact finrank_quotient_span_eq_natDegree

/-- Cyclicity gives the minimal polynomial its full possible degree. -/
theorem minpoly_degree_eq_finrank_of_cyclic [FiniteDimensional k V]
    (T : Module.End k V) (hT : HasCyclicVector T) :
    (minpoly k T).natDegree = Module.finrank k V := by
  obtain ⟨x, hx⟩ := (hasCyclicVector_iff_exists_surjective T).mp hT
  have hker := orbitMap_ker_eq_annihilator_of_surjective T x hx
  have hd := orbit_finrank_eq_minpoly_degree T x hker
  have he : (orbitMap T x).range ≃ₗ[k[X]] Module.AEval' T :=
    LinearEquiv.ofTop (orbitMap T x).range (LinearMap.range_eq_top.mpr hx)
  exact hd.symm.trans (((he.restrictScalars k).finrank_eq).trans
    (Module.AEval'.of T).finrank_eq.symm)

/-- The forward minpoly/charpoly bridge, without any canonical-form certificate. -/
theorem minpoly_eq_charpoly_of_cyclic [FiniteDimensional k V]
    (T : Module.End k V) (hT : HasCyclicVector T) :
    minpoly k T = T.charpoly := by
  apply (Polynomial.eq_of_monic_of_dvd_of_natDegree_le
    (minpoly.monic (LinearMap.isIntegral T)) (LinearMap.charpoly_monic T)
    (LinearMap.minpoly_dvd_charpoly T) ?_).symm
  rw [LinearMap.charpoly_natDegree, minpoly_degree_eq_finrank_of_cyclic T hT]

/-- The PID theorem supplies a vector with the full operator annihilator. -/
theorem exists_full_annihilator_vector [FiniteDimensional k V] (T : Module.End k V) :
    ∃ x : V, (orbitMap T x).ker = Module.annihilator k[X] (Module.AEval' T) := by
  obtain ⟨x, hx⟩ := Module.exists_ker_toSpanSingleton_eq_annihilator
    k[X] (Module.AEval' T)
  exact ⟨(Module.AEval'.of T).symm x, hx⟩

/-- Full minimal-polynomial degree forces the attained annihilator orbit to fill the space. -/
theorem cyclic_of_minpoly_degree_eq_finrank [FiniteDimensional k V]
    (T : Module.End k V) (hdegree : (minpoly k T).natDegree = Module.finrank k V) :
    HasCyclicVector T := by
  obtain ⟨x, hx⟩ := exists_full_annihilator_vector T
  have hrank : Module.finrank k (orbitMap T x).range =
      Module.finrank k (Module.AEval' T) := by
    rw [orbit_finrank_eq_minpoly_degree T x hx, hdegree, ← (Module.AEval'.of T).finrank_eq]
  have htop : ((orbitMap T x).range.restrictScalars k) = ⊤ :=
    Submodule.eq_top_of_finrank_eq hrank
  have hsurj : Function.Surjective (orbitMap T x) := by
    intro y
    have hy : y ∈ (orbitMap T x).range.restrictScalars k := by rw [htop]; trivial
    exact hy
  exact (hasCyclicVector_iff_exists_surjective T).mpr ⟨x, hsurj⟩

/-- The complete cyclic-vector criterion over an arbitrary field. -/
theorem hasCyclicVector_iff_minpoly_eq_charpoly [FiniteDimensional k V]
    (T : Module.End k V) : HasCyclicVector T ↔ minpoly k T = T.charpoly := by
  constructor
  · exact minpoly_eq_charpoly_of_cyclic T
  · intro hp
    apply cyclic_of_minpoly_degree_eq_finrank T
    rw [hp, LinearMap.charpoly_natDegree]

/-- The one-seed polynomial predicate agrees with cyclicity for the actual operator algebra. -/
theorem hasCyclicVector_iff_operatorAlgebra_cyclic (T : Module.End k V) :
    HasCyclicVector T ↔ Komorebi.SeedRankBasics.Cyclic (operatorAlgebra T) V := by
  constructor
  · rintro ⟨s, hs⟩
    have heq : s = fun _ : Fin 1 ↦ s 0 := by
      funext i
      exact congrArg s (Subsingleton.elim i 0)
    rw [heq] at hs
    have h := (familyGenerates_iff_operatorAlgebra_familyGenerates T
      (fun _ : Fin 1 ↦ s 0)).mp hs
    exact ⟨s 0, by simpa [Komorebi.SeedRankBasics.FamilyGenerates] using h⟩
  · rintro ⟨x, hx⟩
    refine ⟨fun _ : Fin 1 ↦ x, ?_⟩
    apply (familyGenerates_iff_operatorAlgebra_familyGenerates T _).mpr
    simpa [Komorebi.SeedRankBasics.FamilyGenerates] using hx

/-- Rank-one form of the genuine polynomial criterion; nonzero space is necessary. -/
theorem operatorAlgebra_seedRank_eq_one_iff_minpoly_eq_charpoly
    [FiniteDimensional k V] [Nontrivial V] (T : Module.End k V) :
    Komorebi.SeedRankBasics.seedRank (operatorAlgebra T) V = 1 ↔
      minpoly k T = T.charpoly := by
  let : Module.Finite (operatorAlgebra T) V :=
    Module.Finite.of_restrictScalars_finite k (operatorAlgebra T) V
  rw [Komorebi.SeedRankBasics.seedRank_eq_one_iff_cyclic,
    ← hasCyclicVector_iff_operatorAlgebra_cyclic,
    hasCyclicVector_iff_minpoly_eq_charpoly]

/-- The old four-way assembly no longer needs a polynomial classification input.
The seed-number and geometric/block-identification certificates remain explicit. -/
theorem cyclic_four_way_without_polynomial_certificate
    [FiniteDimensional k V] {Λ : Type*}
    (T : Module.End k V) (R : ℕ)
    (geometricMultiplicity blockMultiplicity : Λ → ℕ)
    (hpositive : ∀ eigen, 0 < geometricMultiplicity eigen)
    (hbound : ∀ eigen, geometricMultiplicity eigen ≤ R)
    (maxEigen : Λ) (hmax : geometricMultiplicity maxEigen = R)
    (hLeast : IsLeast {r : ℕ | SeedNumberLE T r} R)
    (hgeometric_eq_blocks : ∀ eigen,
      geometricMultiplicity eigen = blockMultiplicity eigen) :
    (HasCyclicVector T ↔ AllGeometricMultiplicitiesOne geometricMultiplicity) ∧
      (AllGeometricMultiplicitiesOne geometricMultiplicity ↔
        OneJordanBlockPerEigenvalue blockMultiplicity) ∧
      (OneJordanBlockPerEigenvalue blockMultiplicity ↔ minpoly k T = T.charpoly) := by
  have hfirst : HasCyclicVector T ↔
      AllGeometricMultiplicitiesOne geometricMultiplicity :=
    hasCyclicVector_iff_one_block_per_eigenvalue
      T R geometricMultiplicity hpositive hbound maxEigen hmax hLeast
  have hmiddle : AllGeometricMultiplicitiesOne geometricMultiplicity ↔
      OneJordanBlockPerEigenvalue blockMultiplicity := by
    constructor
    · intro h eigen
      rw [← hgeometric_eq_blocks eigen]
      exact h eigen
    · intro h eigen
      rw [hgeometric_eq_blocks eigen]
      exact h eigen
  exact ⟨hfirst, hmiddle,
    hmiddle.symm.trans (hfirst.symm.trans (hasCyclicVector_iff_minpoly_eq_charpoly T))⟩

end Komorebi.PaperICompletion.CyclicClassification
