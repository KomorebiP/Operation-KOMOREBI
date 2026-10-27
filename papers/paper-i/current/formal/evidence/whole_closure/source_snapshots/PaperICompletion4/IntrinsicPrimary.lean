import PaperICompletion4.ResidueQuotient
import Mathlib.Algebra.Module.Torsion.PrimaryComponent

/-! # The intrinsic primary component and its literal quotient
The primary component consists exactly of vectors killed by some power of p.
Its inclusion induces an isomorphism with M/pM for Artinian modules.
-/
set_option autoImplicit false
noncomputable section
open scoped Pointwise
namespace Komorebi.PaperICompletion4.IntrinsicPrimary
open Komorebi.PaperICompletion4.ResidueQuotient
universe u v w
variable {R : Type u} [CommRing R]
variable (M : Type v) [AddCommGroup M] [Module R M]

/-- A higher power also kills a vector killed by a lower power. -/
theorem power_kills_of_le (p : R) {m n : ℕ} (h : m ≤ n) (x : M)
    (hx : p ^ m • x = 0) : p ^ n • x = 0 := by
  obtain ⟨r, rfl⟩ := Nat.exists_eq_add_of_le h
  rw [pow_add, mul_comm, mul_smul, hx, smul_zero]

/-- The intrinsic p-primary submodule, without any presentation choices. -/
def primarySubmodule (p : R) : Submodule R M where
  carrier := {x | ∃ n : ℕ, p ^ n • x = 0}
  zero_mem' := ⟨0, smul_zero _⟩
  add_mem' := by
    rintro x y ⟨m, hm⟩ ⟨n, hn⟩
    refine ⟨max m n, ?_⟩
    rw [smul_add, power_kills_of_le M p (le_max_left m n) x hm,
      power_kills_of_le M p (le_max_right m n) y hn, add_zero]
  smul_mem' := by
    rintro a x ⟨n, hn⟩
    exact ⟨n, by rw [smul_comm, hn, smul_zero]⟩

/-- Membership is the actual annihilation-by-a-power condition. -/
theorem mem_primarySubmodule (p : R) (x : M) :
    x ∈ primarySubmodule M p ↔ ∃ n : ℕ, p ^ n • x = 0 := Iff.rfl

/-- This is also Mathlib's ideal-primary component for the principal ideal (p). -/
theorem primarySubmodule_eq_idealPrimary (p : R) :
    primarySubmodule M p = (Ideal.span {p}).primaryComponent M := by
  ext x
  simp only [mem_primarySubmodule, Ideal.primaryComponent_mem,
    Ideal.span_singleton_pow, Submodule.torsionBySet_ideal_span_singleton_eq,
    Submodule.mem_torsionBy_iff]

/-- The literal inclusion followed by quotienting the whole module by pM. -/
def primaryToGlobal (p : R) :
    primarySubmodule M p →ₗ[R] ScalarQuotient M p :=
  (p • (⊤ : Submodule R M)).mkQ.comp (primarySubmodule M p).subtype

/-- Its kernel is exactly p times the primary submodule, not a supplied certificate. -/
theorem primaryToGlobal_ker (p : R) :
    (primaryToGlobal M p).ker =
      p • (⊤ : Submodule R (primarySubmodule M p)) := by
  ext x
  change Submodule.Quotient.mk (x : M) = (0 : ScalarQuotient M p) ↔ _
  rw [Submodule.Quotient.mk_eq_zero, mem_scalarImage_iff, mem_scalarImage_iff]
  constructor
  · rintro ⟨y, hy⟩
    obtain ⟨n, hn⟩ := x.property
    have hyprim : y ∈ primarySubmodule M p := by
      refine ⟨n + 1, ?_⟩
      rw [pow_succ, mul_smul, hy]
      exact hn
    exact ⟨⟨y, hyprim⟩, Subtype.ext hy⟩
  · rintro ⟨y, hy⟩
    exact ⟨y, congrArg Subtype.val hy⟩

/-- In an Artinian module, every class modulo pM has a primary representative. -/
theorem primaryToGlobal_surjective [IsArtinian R M] (p : R) :
    Function.Surjective (primaryToGlobal M p) := by
  let f : Module.End R M := DistribSMul.toLinearMap R M p
  obtain ⟨n, hn : ∀ m, n ≤ m → LinearMap.range (f ^ n) = LinearMap.range (f ^ m)⟩ :=
    IsArtinian.monotone_stabilizes f.iterateRange
  have hpow : ∀ n : ℕ, ∀ x : M, (f ^ n) x = p ^ n • x := by
    intro n
    induction n with
    | zero => intro x; simp
    | succ n ih =>
      intro x
      rw [pow_succ, Module.End.mul_apply, ih, pow_succ, mul_smul]
      rfl
  intro z
  obtain ⟨x, rfl⟩ := (p • (⊤ : Submodule R M)).mkQ_surjective z
  have hx : (f ^ n) x ∈ LinearMap.range (f ^ (n + 1)) := by
    rw [← hn (n + 1) (Nat.le_succ n)]
    exact LinearMap.mem_range_self _ x
  obtain ⟨y, hy⟩ := hx
  have hy' : p ^ n • (p • y) = p ^ n • x := by
    rw [hpow, hpow, pow_succ, mul_smul] at hy
    exact hy
  have hprimary : x - p • y ∈ primarySubmodule M p := by
    exact ⟨n, by rw [smul_sub, hy', sub_self]⟩
  refine ⟨⟨x - p • y, hprimary⟩, ?_⟩
  change Submodule.Quotient.mk (x - p • y) =
    (Submodule.Quotient.mk x : ScalarQuotient M p)
  have hz : Submodule.Quotient.mk (p • y) = (0 : ScalarQuotient M p) := by
    exact (Submodule.Quotient.mk_eq_zero _).mpr
      ((mem_scalarImage_iff p _).mpr ⟨y, rfl⟩)
  rw [Submodule.Quotient.mk_sub, hz, sub_zero]

/-- The primary quotient equals the global quotient over the residue ring itself. -/
def primaryQuotientEquivGlobal [IsArtinian R M] (p : R) :
    ScalarQuotient (primarySubmodule M p) p ≃ₗ[R ⧸ Ideal.span {p}]
      ScalarQuotient M p :=
  scalarQuotientEquiv p (primaryToGlobal M p)
    (primaryToGlobal_surjective M p) (primaryToGlobal_ker M p)

/-- The equivalence is induced by inclusion, with no arbitrary reassignment of classes. -/
theorem primaryQuotientEquivGlobal_mk [IsArtinian R M] (p : R)
    (x : primarySubmodule M p) :
    primaryQuotientEquivGlobal M p (Submodule.Quotient.mk x) =
      Submodule.Quotient.mk (x : M) :=
  scalarQuotientEquiv_mk p _ _ _ x

end Komorebi.PaperICompletion4.IntrinsicPrimary
