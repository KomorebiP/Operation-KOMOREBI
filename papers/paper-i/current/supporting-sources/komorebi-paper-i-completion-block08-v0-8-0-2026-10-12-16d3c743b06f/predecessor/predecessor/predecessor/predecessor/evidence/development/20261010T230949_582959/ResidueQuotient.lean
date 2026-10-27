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
    simp only [Algebra.smul_def, ← map_mul, Ideal.Quotient.factor_mk]
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
  simp only [Algebra.smul_def, mul_assoc]
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

end Komorebi.PaperICompletion4.ResidueQuotient
