import PaperICompletion3
import Mathlib.Algebra.Module.Torsion.Basic
import Mathlib.RingTheory.Artinian.Module

/-! # Exact residue quotients of primary products
The kernel is identified with the actual scalar image, and the resulting
quotient equivalences are linear over the residue ring, not only the base ring.
-/
set_option autoImplicit false
noncomputable section
open scoped Pointwise
namespace Komorebi.PaperICompletion4.ResidueQuotient
open Komorebi.PaperICompletion3.PrimarySeedFormula
universe u v w
variable {R : Type u} [CommRing R]

/-- A quotient factor vanishes precisely on multiples of its generator. -/
theorem factor_eq_zero_iff_smul (I : Ideal R) (p : R)
    (hI : I ≤ Ideal.span {p}) (x : R ⧸ I) :
    Ideal.Quotient.factor hI x = 0 ↔ ∃ y : R ⧸ I, p • y = x := by
  obtain ⟨r, rfl⟩ := Ideal.Quotient.mk_surjective x
  constructor
  · intro h
    have hd : p ∣ r := Ideal.mem_span_singleton.mp
      (Ideal.Quotient.eq_zero_iff_mem.mp h)
    obtain ⟨s, rfl⟩ := hd
    exact ⟨Ideal.Quotient.mk I s, by simp [Algebra.smul_def]⟩
  · rintro ⟨y, hy⟩
    obtain ⟨s, rfl⟩ := Ideal.Quotient.mk_surjective y
    rw [← hy]
    simp only [Algebra.smul_def]
    exact Ideal.Quotient.eq_zero_iff_mem.mpr
      (Ideal.mem_span_singleton.mpr (dvd_mul_right p s))

/-- Multiplication by a coprime element is onto the quotient. -/
theorem smul_surjective_of_coprime (p q : R) (h : IsCoprime p q) :
    Function.Surjective (fun x : R ⧸ Ideal.span {q} ↦ p • x) := by
  obtain ⟨a, b, hab⟩ := h
  intro x
  refine ⟨a • x, ?_⟩
  have hq : (Ideal.Quotient.mk (Ideal.span {q})) q = 0 :=
    Ideal.Quotient.eq_zero_iff_mem.mpr (Ideal.subset_span (Set.mem_singleton q))
  have hid := congrArg (Ideal.Quotient.mk (Ideal.span {q})) hab
  simp only [map_add, map_mul, map_one, hq, mul_zero, add_zero] at hid
  simp only [Algebra.smul_def]
  rw [← mul_assoc, mul_comm ((algebraMap R (R ⧸ Ideal.span {q})) p)]
  change ((Ideal.Quotient.mk (Ideal.span {q})) a *
    (Ideal.Quotient.mk (Ideal.span {q})) p) * x = x
  rw [hid, one_mul]

/-- The scalar-image quotient carries its canonical residue-ring action. -/
abbrev ScalarQuotient (M : Type v) [AddCommGroup M] [Module R M] (p : R) :=
  M ⧸ (p • (⊤ : Submodule R M))

/-- Literal membership in the scalar image, including zero modules. -/
theorem mem_scalarImage_iff {M : Type v} [AddCommGroup M] [Module R M]
    (p : R) (x : M) : x ∈ p • (⊤ : Submodule R M) ↔ ∃ y, p • y = x := by
  simp only [Submodule.mem_smul_pointwise_iff_exists, Submodule.mem_top, true_and]


section QuotientEquivalence
variable {M : Type v} [AddCommGroup M] [Module R M]
variable {N : Type w} [AddCommGroup N] [Module R N]
variable (p : R) [Module (R ⧸ Ideal.span {p}) N]
  [IsScalarTower R (R ⧸ Ideal.span {p}) N]

/-- Exact kernel and surjectivity induce an equivalence over the residue ring.
The action on the source is the canonical action on the literal quotient by pM. -/
def scalarQuotientEquiv (f : M →ₗ[R] N) (hf : Function.Surjective f)
    (hker : f.ker = p • (⊤ : Submodule R M)) :
    ScalarQuotient M p ≃ₗ[R ⧸ Ideal.span {p}] N := by
  let e : ScalarQuotient M p ≃ₗ[R] N :=
    (Submodule.quotEquivOfEq _ _ hker.symm).trans (f.quotKerEquivOfSurjective hf)
  exact
    { e.toAddEquiv with
      map_smul' := by
        intro a x
        obtain ⟨r, rfl⟩ := Ideal.Quotient.mk_surjective a
        change e (r • x) = (Ideal.Quotient.mk (Ideal.span {p}) r) • e x
        rw [e.map_smul]
        exact (IsScalarTower.algebraMap_smul (R ⧸ Ideal.span {p}) r (e x)).symm }

/-- The induced map takes a quotient class to the original residue map. -/
theorem scalarQuotientEquiv_mk (f : M →ₗ[R] N) (hf : Function.Surjective f)
    (hker : f.ker = p • (⊤ : Submodule R M)) (x : M) :
    scalarQuotientEquiv p f hf hker (Submodule.Quotient.mk x) = f x := by
  simp [scalarQuotientEquiv]
end QuotientEquivalence

section PrimaryProduct
variable [IsDomain R] [IsPrincipalIdealRing R]
variable {ι : Type v} [Fintype ι]
variable (q : ι → R) (hq : ∀ i, Irreducible (q i))
  (e : ι → ℕ) (he : ∀ i, 0 < e i)

/-- The canonical map from each prime-power quotient to its residue field. -/
def primaryResidueMap (p : R) :
    ((i : ι) → R ⧸ Ideal.span {q i ^ e i}) →ₗ[R]
      ({i : ι // Ideal.span {q i} = Ideal.span {p}} → R ⧸ Ideal.span {p}) :=
  residueFiberMap (fun i ↦ Ideal.span {q i ^ e i}) (fun i ↦ Ideal.span {q i})
    (fun i ↦ Ideal.span_singleton_le_span_singleton.mpr
      (dvd_pow_self _ (Nat.ne_of_gt (he i)))) (Ideal.span {p})

omit [Fintype ι] in
include hq in
/-- The full residue map, including all off-primary coordinates, has kernel pM. -/
theorem primaryResidueMap_ker (p : R) (hp : Irreducible p) :
    (primaryResidueMap q e he p).ker =
      p • (⊤ : Submodule R ((i : ι) → R ⧸ Ideal.span {q i ^ e i})) := by
  classical
  ext x
  rw [LinearMap.mem_ker, mem_scalarImage_iff]
  constructor
  · intro hx
    have hcoord : ∀ i, ∃ y : R ⧸ Ideal.span {q i ^ e i}, p • y = x i := by
      intro i
      by_cases hi : Ideal.span {q i} = Ideal.span {p}
      · have hz := congrFun hx ⟨i, hi⟩
        exact (factor_eq_zero_iff_smul _ p
          ((Ideal.span_singleton_le_span_singleton.mpr
            (dvd_pow_self _ (Nat.ne_of_gt (he i)))).trans_eq hi) (x i)).mp hz
      · have hc : IsCoprime p (q i ^ e i) := by
          have h := coprime_primePower_ideals p (q i) hp (hq i)
            (Ne.symm hi) 1 (e i)
          simpa only [pow_one] using (Ideal.isCoprime_span_singleton_iff _ _).mp h
        exact smul_surjective_of_coprime p (q i ^ e i) hc (x i)
    choose y hy using hcoord
    exact ⟨y, funext hy⟩
  · rintro ⟨y, rfl⟩
    ext i
    exact (factor_eq_zero_iff_smul _ p
      ((Ideal.span_singleton_le_span_singleton.mpr
        (dvd_pow_self _ (Nat.ne_of_gt (he i)))).trans_eq i.property) (p • y i)).mpr
      ⟨y i, rfl⟩

omit [IsDomain R] [IsPrincipalIdealRing R] [Fintype ι] in
/-- The full primary residue map is onto even for an absent label. -/
theorem primaryResidueMap_surjective (p : R) :
    Function.Surjective (primaryResidueMap q e he p) :=
  residueFiberMap_surjective _ _ _ _

/-- The literal quotient by p is the selected residue-field fibre. -/
def primaryProductQuotientEquiv (p : R) (hp : Irreducible p) :
    ScalarQuotient ((i : ι) → R ⧸ Ideal.span {q i ^ e i}) p ≃ₗ[R ⧸ Ideal.span {p}]
      ({i : ι // Ideal.span {q i} = Ideal.span {p}} → R ⧸ Ideal.span {p}) :=
  scalarQuotientEquiv p (primaryResidueMap q e he p)
    (primaryResidueMap_surjective q e he p) (primaryResidueMap_ker q hq e he p hp)

end PrimaryProduct
end Komorebi.PaperICompletion4.ResidueQuotient
