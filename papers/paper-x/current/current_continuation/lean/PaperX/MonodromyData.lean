import PaperX.CarrierPolynomials
import Mathlib.RingTheory.Nilpotent.Basic

/-! Algebraic monodromy pairs with the explicit convention F N F⁻¹ = q N.
F is an actual linear automorphism and N an actual nilpotent endomorphism.
No arithmetic Weil-group realization or inertia action is inferred. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.MonodromyData
open scoped BigOperators
open PaperX.CarrierSummands PaperX.CarrierPolynomials

variable {K : Type*} [Field K]

structure Datum (q : Kˣ) (V : Type*) [AddCommGroup V] [Module K V] where
  F : V ≃ₗ[K] V
  N : Module.End K V
  nilpotent : IsNilpotent N
  relation : ∀ x, F (N x) = (q : K) • N (F x)

variable {q : Kˣ} {V : Type*} [AddCommGroup V] [Module K V]

/-- The conjugation convention is a consequence of the pointwise relation. -/
theorem conjugation (D : Datum q V) : D.F.conj D.N = (q : K) • D.N := by
  apply LinearMap.ext
  intro x
  simpa using D.relation (D.F.symm x)

theorem kernel_stable (D : Datum q V) {x : V} (hx : D.N x = 0) : D.N (D.F x) = 0 := by
  have h := D.relation x
  rw [hx, map_zero] at h
  exact (smul_eq_zero.mp h.symm).resolve_left (Units.ne_zero q)

theorem kernel_inverse_stable (D : Datum q V) {x : V} (hx : D.N x = 0) :
    D.N (D.F.symm x) = 0 := by
  apply D.F.injective
  rw [D.relation, D.F.apply_symm_apply, hx, smul_zero, map_zero]

/-- Actual induced automorphism of the independently defined kernel. -/
def kernelF (D : Datum q V) : LinearMap.ker D.N ≃ₗ[K] LinearMap.ker D.N where
  toFun x := ⟨D.F x.val, kernel_stable D x.property⟩
  invFun x := ⟨D.F.symm x.val, kernel_inverse_stable D x.property⟩
  left_inv x := by apply Subtype.ext; exact D.F.symm_apply_apply x.val
  right_inv x := by apply Subtype.ext; exact D.F.apply_symm_apply x.val
  map_add' x y := by apply Subtype.ext; exact map_add D.F x.val y.val
  map_smul' a x := by apply Subtype.ext; exact map_smul D.F a x.val

@[simp] theorem kernelF_val (D : Datum q V) (x : LinearMap.ker D.N) :
    (kernelF D x).val = D.F x.val := rfl

def kernelCharpoly [FiniteDimensional K V] (D : Datum q V) : Polynomial K :=
  (kernelF D).toLinearMap.charpoly

variable {I : Type*} {W : I → Type*}
variable [∀ i, AddCommGroup (W i)] [∀ i, Module K (W i)]

def copiesN (N : ∀ i, Module.End K (W i)) (m : I → ℕ) :
    Module.End K (Copies W m) := piEnd (fun i => piEnd (fun _ : Fin (m i) => N i))

@[simp] theorem copiesN_apply (N : ∀ i, Module.End K (W i)) (m : I → ℕ)
    (x : Copies W m) (i : I) (k : Fin (m i)) : copiesN N m x i k = N i (x i k) := rfl

theorem copiesN_pow_apply (N : ∀ i, Module.End K (W i)) (m : I → ℕ) (n : ℕ)
    (x : Copies W m) (i : I) (k : Fin (m i)) :
    (copiesN N m ^ n) x i k = (N i ^ n) (x i k) := by
  induction n generalizing x with
  | zero => rfl
  | succ n ih =>
      simp only [pow_succ, Module.End.mul_apply, copiesN_apply, ih]

theorem copiesN_nilpotent [Fintype I] (N : ∀ i, Module.End K (W i))
    (hN : ∀ i, IsNilpotent (N i)) (m : I → ℕ) : IsNilpotent (copiesN N m) := by
  classical
  choose n hn using hN
  refine ⟨∑ i, n i, ?_⟩
  apply LinearMap.ext
  intro x
  funext i k
  rw [copiesN_pow_apply]
  have hle : n i ≤ ∑ j, n j := Finset.single_le_sum (fun j _ => Nat.zero_le (n j)) (Finset.mem_univ i)
  rw [pow_eq_zero_of_le hle (hn i)]
  rfl

def copiesF (D : ∀ i, Datum q (W i)) (m : I → ℕ) : Copies W m ≃ₗ[K] Copies W m :=
  LinearEquiv.piCongrRight (fun i => LinearEquiv.piCongrRight (fun _ : Fin (m i) => (D i).F))

@[simp] theorem copiesF_apply (D : ∀ i, Datum q (W i)) (m : I → ℕ)
    (x : Copies W m) (i : I) (k : Fin (m i)) : copiesF D m x i k = (D i).F (x i k) := rfl

/-- Every constituent is supplied; the sum's nilpotence is proved from theirs. -/
def copiesDatum [Fintype I] (D : ∀ i, Datum q (W i)) (m : I → ℕ) : Datum q (Copies W m) where
  F := copiesF D m
  N := copiesN (fun i => (D i).N) m
  nilpotent := copiesN_nilpotent _ (fun i => (D i).nilpotent) m
  relation x := by funext i k; exact (D i).relation (x i k)

theorem inclusion_intertwines_N (N : ∀ i, Module.End K (W i))
    {m c : I → ℕ} (h : ∀ i, m i ≤ c i) (x : Copies W m) :
    inclusion (R := K) h (copiesN N m x) = copiesN N c (inclusion (R := K) h x) := by
  funext i k
  dsimp [inclusion]
  split <;> simp

theorem retraction_intertwines_N (N : ∀ i, Module.End K (W i))
    {m c : I → ℕ} (h : ∀ i, m i ≤ c i) (x : Copies W c) :
    retraction (R := K) h (copiesN N c x) = copiesN N m (retraction (R := K) h x) := rfl

theorem inclusion_intertwines_F (D : ∀ i, Datum q (W i))
    {m c : I → ℕ} (h : ∀ i, m i ≤ c i) (x : Copies W m) :
    inclusion (R := K) h (copiesF D m x) = copiesF D c (inclusion (R := K) h x) := by
  funext i k
  dsimp [inclusion]
  split <;> simp

theorem retraction_intertwines_F (D : ∀ i, Datum q (W i))
    {m c : I → ℕ} (h : ∀ i, m i ≤ c i) (x : Copies W c) :
    retraction (R := K) h (copiesF D c x) = copiesF D m (retraction (R := K) h x) := rfl

end PaperX.MonodromyData
