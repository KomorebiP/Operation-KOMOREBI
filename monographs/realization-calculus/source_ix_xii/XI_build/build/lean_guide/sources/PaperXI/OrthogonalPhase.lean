import PaperXI.OddPhaseSum
import PaperXI.OrthogonalSummands
import Mathlib.Algebra.DirectSum.Module

/-! Source 12.4 for an actual finite internal orthogonal decomposition. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.OrthogonalPhase
open scoped BigOperators Classical

variable {K X ι : Type*} [Field K] [AddCommGroup X] [Module K X] [Fintype ι]

/-- The actual internal direct-sum map becomes a finite-product equivalence. -/
def decomposition (S : ι → Submodule K X) (hS : DirectSum.IsInternal S) :
    (∀ i, S i) ≃ₗ[K] X :=
  (DirectSum.linearEquivFunOnFintype K ι (fun i => S i)).symm.trans
    (LinearEquiv.ofBijective (DirectSum.coeLinearMap S) hS)

theorem decomposition_sum (S : ι → Submodule K X) (hS : DirectSum.IsInternal S)
    (x : ∀ i, S i) : decomposition S hS x = ∑ i, (x i : X) := by
  classical
  have he : (decomposition S hS).toLinearMap =
      ∑ i, (S i).subtype.comp (LinearMap.proj i) := by
    apply LinearMap.pi_ext
    intro i y
    simp only [LinearMap.sum_apply, LinearMap.comp_apply, LinearMap.proj_apply,
      Submodule.subtype_apply]
    change (DirectSum.coeLinearMap S)
      ((DirectSum.linearEquivFunOnFintype K ι (fun i => S i)).symm (Pi.single i y)) = _
    rw [DirectSum.linearEquivFunOnFintype_symm_single, DirectSum.coeLinearMap_lof]
    symm
    have hs : ∑ j, ((Pi.single i y : ∀ j, S j) j : X) =
        ((Pi.single i y : ∀ j, S j) i : X) := by
      apply Finset.sum_eq_single i
      · intro j _ hji
        rw [Pi.single_eq_of_ne hji]
        rfl
      · intro hi
        exact (hi (Finset.mem_univ i)).elim
    simpa using hs
  simpa only [LinearMap.sum_apply, LinearMap.comp_apply, LinearMap.proj_apply,
    Submodule.subtype_apply, LinearEquiv.coe_coe] using
    congrArg (fun f : (∀ i, S i) →ₗ[K] X => f x) he

variable [FiniteDimensional K X]

def restricted (G : X ≃ₗ[K] X) (S : ι → Submodule K X)
    (hstable : ∀ i, ∀ x ∈ S i, G x ∈ S i) (i : ι) : S i ≃ₗ[K] S i :=
  OrthogonalSummands.restrictionEquiv G (S i) (hstable i)

omit [Fintype ι] in
@[simp] theorem restricted_coe (G : X ≃ₗ[K] X) (S : ι → Submodule K X)
    (hstable : ∀ i, ∀ x ∈ S i, G x ∈ S i) (i : ι) (x : S i) :
    (restricted G S hstable i x : X) = G x := rfl

theorem intertwines (G : X ≃ₗ[K] X) (S : ι → Submodule K X)
    (hS : DirectSum.IsInternal S) (hstable : ∀ i, ∀ x ∈ S i, G x ∈ S i)
    (x : ∀ i, S i) :
    decomposition S hS (LinearEquiv.piCongrRight (restricted G S hstable) x) =
      G (decomposition S hS x) := by
  simp only [decomposition_sum, map_sum, LinearEquiv.piCongrRight_apply, restricted_coe]

section PrimeField
variable {p : ℕ} [Fact p.Prime]
variable {V : Type*} [AddCommGroup V] [Module (ZMod p) V]
variable [FiniteDimensional (ZMod p) V]

theorem phase_product (hp : p ≠ 2) (b : LinearMap.BilinForm (ZMod p) V)
    (ha : b.IsAlt) (hn : b.Nondegenerate) (G : V ≃ₗ[ZMod p] V)
    (S : ι → Submodule (ZMod p) V) (hS : DirectSum.IsInternal S)
    (horth : ∀ i j, i ≠ j → ∀ x ∈ S i, ∀ y ∈ S j, b x y = 0)
    (hstable : ∀ i, ∀ x ∈ S i, G x ∈ S i) :
    OddPhase.phase G = ∏ i, OddPhase.phase (restricted G S hstable i) := by
  apply OddPhaseSum.of_decomposition hp (fun i => b.restrict (S i))
    (fun i => OrthogonalSummands.restricted_isAlt b ha (S i))
    (fun i => OrthogonalSummands.restricted_form_nondegenerate b hn S
      hS.submodule_iSup_eq_top horth i)
    (restricted G S hstable) G (decomposition S hS)
  exact intertwines G S hS hstable

theorem fixedPointFree (G : V ≃ₗ[ZMod p] V)
    (S : ι → Submodule (ZMod p) V) (hS : DirectSum.IsInternal S)
    (hstable : ∀ i, ∀ x ∈ S i, G x ∈ S i)
    (hfix : ∀ i, OddPhase.FixedPointFree (restricted G S hstable i)) :
    OddPhase.FixedPointFree G :=
  OddPhaseSum.fixedPointFree_of_decomposition (restricted G S hstable) hfix G
    (decomposition S hS) (intertwines G S hS hstable)

/-- Full finite orthogonal multiplicativity: the restricted forms and actions
are constructed from the ambient data, and all fixed-point-free conditions hold. -/
theorem source (hp : p ≠ 2) (b : LinearMap.BilinForm (ZMod p) V)
    (ha : b.IsAlt) (hn : b.Nondegenerate) (G : V ≃ₗ[ZMod p] V)
    (hform : ∀ x y, b (G x) (G y) = b x y)
    (S : ι → Submodule (ZMod p) V) (hS : DirectSum.IsInternal S)
    (horth : ∀ i j, i ≠ j → ∀ x ∈ S i, ∀ y ∈ S j, b x y = 0)
    (hstable : ∀ i, ∀ x ∈ S i, G x ∈ S i)
    (hfix : ∀ i, OddPhase.FixedPointFree (restricted G S hstable i)) :
    (∀ i, (b.restrict (S i)).IsAlt ∧ (b.restrict (S i)).Nondegenerate) ∧
      (∀ i (x y : S i), b.restrict (S i) (restricted G S hstable i x)
        (restricted G S hstable i y) = b.restrict (S i) x y) ∧
      OddPhase.FixedPointFree G ∧
      OddPhase.phase G = ∏ i, OddPhase.phase (restricted G S hstable i) := by
  refine ⟨fun i => ⟨OrthogonalSummands.restricted_isAlt b ha (S i),
    OrthogonalSummands.restricted_form_nondegenerate b hn S
      hS.submodule_iSup_eq_top horth i⟩, ?_, fixedPointFree G S hS hstable hfix,
    phase_product hp b ha hn G S hS horth hstable⟩
  intro i x y
  exact OrthogonalSummands.restrictionEquiv_form b G hform (S i) (hstable i) x y

end PrimeField
end PaperXI.OrthogonalPhase
