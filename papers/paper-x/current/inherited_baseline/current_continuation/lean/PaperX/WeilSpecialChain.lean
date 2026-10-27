import PaperX.WeilEuler
import PaperX.SpecialMonodromy

/-! The special monodromy chain is extended to an actual action of the whole
group using two characters. Ramified scalar inertia kills every fixed vector. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.WeilSpecialChain
open Polynomial PaperX.WeilData PaperX.WeilEuler PaperX.SpecialMonodromy
variable {K G : Type*} [Field K] [Group G]

def chainRep (ν α : G →* Kˣ) (n : ℕ) : Representation K G (Fin n → K) where
  toFun g := (diagonalF (ν g) (α g) n).toLinearMap
  map_one' := by apply LinearMap.ext; intro x; funext j; simp [diagonalF]
  map_mul' g h := by
    apply LinearMap.ext
    intro x
    funext j
    simp [diagonalF, mul_pow, mul_comm, mul_left_comm, mul_assoc]

def chainDatum (ν α : G →* Kˣ) (n : ℕ) : Datum ν (Fin n → K) where
  r := chainRep ν α n
  N := shift n
  nilpotent := ⟨n, shift_nilpotent n⟩
  relation g := chain_relation (ν g) (α g) n

theorem inertia_scalar (ν α : G →* Kˣ) (n : ℕ) (H : Subgroup G)
    (hν : ∀ h : H, ν h = 1) (h : H) (x : Fin n → K) :
    (chainDatum ν α n).r h x = (α h : K) • x := by
  funext j
  simp [chainDatum, chainRep, diagonalF, hν h]

theorem unramified_fixed (ν α : G →* Kˣ) (n : ℕ) (H : Subgroup G)
    (hν : ∀ h : H, ν h = 1) (hα : ∀ h : H, α h = 1) :
    fixedKernel (chainDatum ν α n) H = LinearMap.ker (shift (K := K) n) := by
  apply fixedKernel_eq_kernel
  intro h
  apply LinearMap.ext
  intro x
  rw [inertia_scalar ν α n H hν h x, hα h]
  simp

/-- The unramified local space is the earlier kernel, with the same actual F-action. -/
def unramifiedKernelEquiv (ν α : G →* Kˣ) (n : ℕ) (H : Subgroup G)
    (hν : ∀ h : H, ν h = 1) (hα : ∀ h : H, α h = 1) :
    fixedKernel (chainDatum ν α n) H ≃ₗ[K] LinearMap.ker (shift (K := K) n) :=
  LinearEquiv.ofEq _ _ (unramified_fixed ν α n H hν hα)

theorem unramified_charpoly (ν α : G →* Kˣ) (n : ℕ) (hn : 0 < n)
    (H : Subgroup G) [H.Normal] (hν : ∀ h : H, ν h = 1)
    (hα : ∀ h : H, α h = 1) (φ : G) :
    localCharpoly (chainDatum ν α n) H φ = X - C (α φ : K) := by
  let e := unramifiedKernelEquiv ν α n H hν hα
  have he : e.conj (fixedRep (chainDatum ν α n) H φ) =
      (PaperX.MonodromyData.kernelF (specialDatum (ν φ) (α φ) n)).toLinearMap := by
    apply LinearMap.ext
    intro x
    apply Subtype.ext
    rfl
  unfold localCharpoly
  rw [← LinearEquiv.charpoly_conj e, he]
  exact special_kernel_charpoly (ν φ) (α φ) n hn

theorem ramified_fixed (ν α : G →* Kˣ) (n : ℕ) (H : Subgroup G)
    (hν : ∀ h : H, ν h = 1) (hα : ∃ h : H, α h ≠ 1) :
    fixedKernel (chainDatum ν α n) H = ⊥ := by
  obtain ⟨h, hh⟩ := hα
  apply eq_bot_iff.mpr
  intro x hx
  change x = 0
  have hf : (α h : K) • x = x :=
    (inertia_scalar ν α n H hν h x).symm.trans (hx.2 h)
  have hz : ((α h : K) - 1) • x = 0 := by rw [sub_smul, one_smul, hf, sub_self]
  have ha : (α h : K) - 1 ≠ 0 := sub_ne_zero.mpr (by
    intro he
    apply hh
    apply Units.ext
    exact he)
  exact (smul_eq_zero.mp hz).resolve_left ha

theorem unramified_dimension (ν α : G →* Kˣ) (n : ℕ) (hn : 0 < n)
    (H : Subgroup G) (hν : ∀ h : H, ν h = 1) (hα : ∀ h : H, α h = 1) :
    Module.finrank K (fixedKernel (chainDatum ν α n) H) = 1 := by
  rw [unramified_fixed ν α n H hν hα, (kernelLine (K := K) n hn).finrank_eq]
  simp

theorem ramified_dimension (ν α : G →* Kˣ) (n : ℕ) (H : Subgroup G)
    (hν : ∀ h : H, ν h = 1) (hα : ∃ h : H, α h ≠ 1) :
    Module.finrank K (fixedKernel (chainDatum ν α n) H) = 0 := by
  rw [ramified_fixed ν α n H hν hα]
  simp

theorem ramified_charpoly (ν α : G →* Kˣ) (n : ℕ) (H : Subgroup G) [H.Normal]
    (hν : ∀ h : H, ν h = 1) (hα : ∃ h : H, α h ≠ 1) (φ : G) :
    localCharpoly (chainDatum ν α n) H φ = 1 := by
  have hd : (localCharpoly (chainDatum ν α n) H φ).natDegree = 0 := by
    rw [localCharpoly, LinearMap.charpoly_natDegree, ramified_dimension ν α n H hν hα]
  have hc : (localCharpoly (chainDatum ν α n) H φ).coeff 0 = 1 := by
    rw [← hd]
    exact (LinearMap.charpoly_monic _).leadingCoeff
  rw [Polynomial.eq_C_of_natDegree_eq_zero hd, hc, Polynomial.C_1]


theorem reverse_linear (a : K) : (X - C a).reverse = 1 - C a * X := by
  have h1 : (1 : Polynomial K).reverse = 1 := by
    simpa using Polynomial.reverse_C (1 : K)
  have hx : (X : Polynomial K).reverse = 1 := by
    simpa [h1] using Polynomial.reverse_mul_X (1 : Polynomial K)
  rw [sub_eq_add_neg, ← map_neg, Polynomial.reverse_add_C]
  simp [hx, sub_eq_add_neg]

theorem unramified_euler (ν α : G →* Kˣ) (n : ℕ) (hn : 0 < n)
    (H : Subgroup G) [H.Normal] (hν : ∀ h : H, ν h = 1)
    (hα : ∀ h : H, α h = 1) (φ : G) :
    eulerPolynomial (chainDatum ν α n) H φ = 1 - C (α φ : K) * X := by
  rw [eulerPolynomial, unramified_charpoly ν α n hn H hν hα φ, reverse_linear]

theorem ramified_euler (ν α : G →* Kˣ) (n : ℕ) (H : Subgroup G) [H.Normal]
    (hν : ∀ h : H, ν h = 1) (hα : ∃ h : H, α h ≠ 1) (φ : G) :
    eulerPolynomial (chainDatum ν α n) H φ = 1 := by
  rw [eulerPolynomial, ramified_charpoly ν α n H hν hα φ]
  simpa using Polynomial.reverse_C (1 : K)

end PaperX.WeilSpecialChain
