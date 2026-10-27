import Mathlib.RingTheory.SimpleModule.Basic
import Mathlib.LinearAlgebra.Trace

/-! Finite families of pairwise nonisomorphic simple modules can be separated
by actual elements of their acting ring. No finiteness of that ring is assumed. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.SimpleModuleSeparation
open scoped BigOperators
variable {A : Type*} [Ring A] {I : Type*} [Fintype I] [DecidableEq I]
variable {W : I → Type*} [∀ i, AddCommGroup (W i)] [∀ i, Module A (W i)]
variable [∀ i, IsSimpleModule A (W i)]
variable (hne : ∀ i j, Nonempty (W i ≃ₗ[A] W j) → i = j)

omit [Fintype I] in
include hne in
theorem off_diagonal_zero (f : Module.End A (∀ i, W i)) (i j : I) (hij : i ≠ j) :
    (LinearMap.proj i).comp (f.comp (LinearMap.single A W j)) = 0 := by
  by_contra h
  have hb := LinearMap.bijective_of_ne_zero h
  exact hij (hne j i ⟨LinearEquiv.ofBijective _ hb⟩).symm

include hne in
theorem coordinate_of_end (f : Module.End A (∀ i, W i)) (x : ∀ i, W i) (i : I) :
    f x i = f (Pi.single i (x i)) i := by
  conv_lhs => rw [← LinearMap.sum_single_apply W x, map_sum]
  simp only [Finset.sum_apply]
  apply Finset.sum_eq_single i
  · intro j _ hji
    have h := LinearMap.congr_fun (off_diagonal_zero hne f i j hji.symm) (x j)
    exact h
  · simp

def selector (i : I) : Module.End A (∀ j, W j) :=
  (LinearMap.single A W i).comp (LinearMap.proj i)

include hne in
theorem selector_commutes (i : I) (f : Module.End A (∀ j, W j)) (x : ∀ j, W j) :
    selector (A := A) i (f x) = f (selector (A := A) i x) := by
  funext j
  by_cases h : j = i
  · subst j
    simpa [selector] using coordinate_of_end hne f x i
  · have hz := LinearMap.congr_fun (off_diagonal_zero hne f j i h) (x i)
    simpa [selector, Pi.single_apply, h] using hz.symm

/-- A coordinate projector commutes with every module endomorphism, hence is
linear for the endomorphism-ring action used by Jacobson density. -/
def doubleSelector (i : I) : Module.End (Module.End A (∀ j, W j)) (∀ j, W j) where
  toFun := selector (A := A) i
  map_add' := (selector (A := A) i).map_add
  map_smul' f x := selector_commutes hne i f x

variable {K : Type*} [Field K]
variable [∀ i, Module K (W i)] [∀ i, SMulCommClass A K (W i)]
variable [∀ i, FiniteDimensional K (W i)]

include hne in
/-- Exact simultaneous action: identity on one simple constituent, zero on all others. -/
theorem exists_selecting_element (i : I) :
    ∃ a : A, ∀ j, Module.toModuleEnd K (W j) a =
      if j = i then LinearMap.id else 0 := by
  classical
  let b := Module.finBasis K (∀ j, W j)
  obtain ⟨a, ha⟩ := jacobson_density (doubleSelector hne i) (Finset.univ.image b)
  let s : Module.End K (∀ j, W j) :=
    (LinearMap.single K W i).comp (LinearMap.proj i)
  have he : s = Module.toModuleEnd K (∀ j, W j) a := by
    apply b.ext
    intro k
    exact ha (b k) (Finset.mem_image.mpr ⟨k, Finset.mem_univ k, rfl⟩)
  refine ⟨a, ?_⟩
  intro j
  apply LinearMap.ext
  intro x
  have h := congrFun (LinearMap.congr_fun he (Pi.single j x)) j
  by_cases hj : j = i
  · subst j
    simpa [s, Module.toModuleEnd_apply] using h.symm
  · simpa [s, Module.toModuleEnd_apply, hj] using h.symm

include hne in
/-- Trace functions of pairwise nonisomorphic simple modules are independent
in characteristic zero, even when the acting ring is infinite. -/
theorem independent_module_traces [CharZero K] :
    LinearIndependent K (fun j (a : A) =>
      LinearMap.trace K (W j) (Module.toModuleEnd K (W j) a)) := by
  rw [Fintype.linearIndependent_iff]
  intro c hc i
  obtain ⟨a, ha⟩ := exists_selecting_element (K := K) hne i
  have h := congrFun hc a
  simp only [Finset.sum_apply, Pi.smul_apply, smul_eq_mul, Pi.zero_apply] at h
  have ht (j : I) : LinearMap.trace K (W j) (Module.toModuleEnd K (W j) a) =
      if j = i then (Module.finrank K (W j) : K) else 0 := by
    rw [ha]
    split <;> simp [LinearMap.trace_id]
  simp only [ht] at h
  simp only [mul_ite, mul_zero, Finset.sum_ite_eq', Finset.mem_univ, ite_true] at h
  have : Nontrivial (W i) := IsSimpleModule.nontrivial A (W i)
  have hn : (Module.finrank K (W i) : K) ≠ 0 := by
    exact_mod_cast (ne_of_gt (Module.finrank_pos (R := K) (M := W i)))
  exact (mul_eq_zero.mp h).resolve_right hn

end PaperX.SimpleModuleSeparation
