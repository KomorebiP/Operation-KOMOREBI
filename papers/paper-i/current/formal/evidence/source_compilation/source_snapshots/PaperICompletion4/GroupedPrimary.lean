import PaperICompletion4.IntrinsicPrimary

/-! # Grouped elementary divisors are the actual intrinsic primary component -/
set_option autoImplicit false
noncomputable section
open scoped Pointwise
namespace Komorebi.PaperICompletion4.GroupedPrimary
open Komorebi.PaperICompletion3.PrimarySeedFormula
open Komorebi.PaperICompletion4.ResidueQuotient
open Komorebi.PaperICompletion4.IntrinsicPrimary
universe u v w
variable {R : Type u} [CommRing R]

/-- Coprimality makes scalar multiplication injective as well as surjective. -/
theorem eq_zero_of_coprime_smul (p q : R) (hc : IsCoprime p q)
    (x : R ⧸ Ideal.span {q}) (hx : p • x = 0) : x = 0 := by
  obtain ⟨a, b, hab⟩ := hc
  have hq : q • x = 0 := by
    rw [Algebra.smul_def]
    change Ideal.Quotient.mk (Ideal.span {q}) q * x = 0
    rw [Ideal.Quotient.eq_zero_iff_mem.mpr (Ideal.subset_span (Set.mem_singleton q)),
      zero_mul]
  calc
    x = (1 : R) • x := (one_smul R x).symm
    _ = (a * p + b * q) • x := by rw [hab]
    _ = 0 := by rw [add_smul, mul_smul, mul_smul, hx, hq, smul_zero, smul_zero, add_zero]

section Equivalence
variable {M : Type v} [AddCommGroup M] [Module R M]
variable {N : Type w} [AddCommGroup N] [Module R N]

/-- An actual module equivalence preserves the intrinsic primary condition. -/
theorem primary_equiv_mem_iff (p : R) (f : M ≃ₗ[R] N) (x : M) :
    f x ∈ primarySubmodule N p ↔ x ∈ primarySubmodule M p := by
  change (∃ n : ℕ, p ^ n • f x = 0) ↔ ∃ n : ℕ, p ^ n • x = 0
  simp only [← f.map_smul, map_eq_zero_iff f f.injective]

/-- Restriction to intrinsic primary components, not an unrelated presentation witness. -/
def primaryCongr (p : R) (f : M ≃ₗ[R] N) :
    primarySubmodule M p ≃ₗ[R] primarySubmodule N p where
  toFun x := ⟨f x, (primary_equiv_mem_iff p f x).mpr x.property⟩
  invFun y := ⟨f.symm y, (primary_equiv_mem_iff p f.symm y).mpr y.property⟩
  left_inv x := Subtype.ext (f.symm_apply_apply x)
  right_inv y := Subtype.ext (f.apply_symm_apply y)
  map_add' x y := Subtype.ext (f.map_add x y)
  map_smul' a x := Subtype.ext (f.map_smul a x)
end Equivalence

section Product
variable [IsDomain R] [IsPrincipalIdealRing R]
variable {ι : Type v} [Fintype ι]
variable (q : ι → R) (hq : ∀ i, Irreducible (q i)) (e : ι → ℕ)

include hq in
/-- The intrinsic primary component consists exactly of the matching coordinates. -/
theorem primaryProduct_mem_iff (p : R) (hp : Irreducible p)
    (x : (i : ι) → R ⧸ Ideal.span {q i ^ e i}) :
    x ∈ primarySubmodule ((i : ι) → R ⧸ Ideal.span {q i ^ e i}) p ↔
      ∀ i, Ideal.span {q i} ≠ Ideal.span {p} → x i = 0 := by
  classical
  constructor
  · rintro ⟨n, hn⟩ i hi
    have hc := coprime_primePower_ideals p (q i) hp (hq i) (Ne.symm hi) n (e i)
    exact eq_zero_of_coprime_smul (p ^ n) (q i ^ e i)
      ((Ideal.isCoprime_span_singleton_iff _ _).mp hc) (x i) (congrFun hn i)
  · intro hx
    refine ⟨Finset.univ.sup e, ?_⟩
    ext i
    by_cases hi : Ideal.span {q i} = Ideal.span {p}
    · have hid : Ideal.span {q i ^ e i} = Ideal.span {p ^ e i} := by
        simpa only [Ideal.span_singleton_pow] using
          congrArg (fun I : Ideal R ↦ I ^ e i) hi
      have hz : p ^ e i • x i = 0 := by
        rw [Algebra.smul_def]
        change Ideal.Quotient.mk (Ideal.span {q i ^ e i}) (p ^ e i) * x i = 0
        have hpq : p ^ e i ∈ Ideal.span {q i ^ e i} := by
          rw [hid]
          exact Ideal.subset_span (Set.mem_singleton _)
        rw [Ideal.Quotient.eq_zero_iff_mem.mpr hpq, zero_mul]
      exact power_kills_of_le _ p (Finset.le_sup (f := e) (Finset.mem_univ i)) (x i) hz
    · simp only [Pi.smul_apply, Pi.zero_apply, hx i hi, smul_zero]

/-- The grouped product is equivalent to the literal intrinsic primary submodule. -/
def groupedPrimaryEquiv (p : R) (hp : Irreducible p) :
    primarySubmodule ((i : ι) → R ⧸ Ideal.span {q i ^ e i}) p ≃ₗ[R]
      ((i : {i : ι // Ideal.span {q i} = Ideal.span {p}}) →
        R ⧸ Ideal.span {q i ^ e i}) := by
  classical
  let f : primarySubmodule ((i : ι) → R ⧸ Ideal.span {q i ^ e i}) p →ₗ[R]
      ((i : {i : ι // Ideal.span {q i} = Ideal.span {p}}) →
        R ⧸ Ideal.span {q i ^ e i}) :=
    (LinearMap.pi fun i ↦ LinearMap.proj i.val).comp (primarySubmodule _ p).subtype
  apply LinearEquiv.ofBijective f
  constructor
  · intro x y hxy
    apply Subtype.ext
    funext i
    by_cases hi : Ideal.span {q i} = Ideal.span {p}
    · exact congrFun hxy ⟨i, hi⟩
    · rw [(primaryProduct_mem_iff q hq e p hp x).mp x.property i hi,
        (primaryProduct_mem_iff q hq e p hp y).mp y.property i hi]
  · intro y
    let x : (i : ι) → R ⧸ Ideal.span {q i ^ e i} :=
      fun i ↦ if hi : Ideal.span {q i} = Ideal.span {p} then y ⟨i, hi⟩ else 0
    have hx : x ∈ primarySubmodule _ p := by
      apply (primaryProduct_mem_iff q hq e p hp x).mpr
      intro i hi
      simp [x, hi]
    refine ⟨⟨x, hx⟩, ?_⟩
    ext i
    change x i.val = y i
    simp [x, i.property]
end Product
end Komorebi.PaperICompletion4.GroupedPrimary
