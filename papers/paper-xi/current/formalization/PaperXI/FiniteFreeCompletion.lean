import PaperXI.ResidueExtensionRealization
import Mathlib.RingTheory.AdicCompletion.Basic
import Mathlib.RingTheory.AdicCompletion.Noetherian

/-! Completeness is derived in finite free coordinates, not assumed of the
constructed root ring. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FiniteFreeCompletion
open IsLocalRing Module
variable {R : Type*} [CommRing R] (I : Ideal R)
variable {M N : Type*} [AddCommGroup M] [Module R M] [AddCommGroup N] [Module R N]

theorem linear_congruence (f : M →ₗ[R] N) {x y : M} {n : ℕ}
    (h : x ≡ y [SMOD (I ^ n • ⊤ : Submodule R M)]) :
    f x ≡ f y [SMOD (I ^ n • ⊤ : Submodule R N)] := by
  apply (h.map f).mono
  rw [Submodule.map_smul'']
  gcongr
  exact le_top

variable {ι : Type*} [Fintype ι] (b : Basis ι R M)
include b

theorem precomplete [IsPrecomplete I R] : IsPrecomplete I M := by
  classical
  constructor
  intro a ha
  have hc : ∀ i, ∃ L : R, ∀ n,
      b.coord i (a n) ≡ L [SMOD (I ^ n • ⊤ : Submodule R R)] := by
    intro i
    exact IsPrecomplete.prec' (fun n => b.coord i (a n))
      (fun h => linear_congruence I (b.coord i) (ha h))
  choose L hL using hc
  refine ⟨∑ i, L i • b i, ?_⟩
  intro n
  rw [← b.sum_repr (a n)]
  apply SModEq.sum
  intro i _
  exact linear_congruence I (LinearMap.toSpanSingleton R M (b i)) (hL i n)

theorem hausdorff [IsHausdorff I R] : IsHausdorff I M := by
  constructor
  intro x hx
  have hc : ∀ i, b.coord i x = 0 := by
    intro i
    apply IsHausdorff.haus' (I := I)
    intro n
    simpa using linear_congruence I (b.coord i) (hx n)
  rw [← b.sum_repr x]
  simp only [← Basis.coord_apply, hc, zero_smul, Finset.sum_const_zero]

theorem complete [IsAdicComplete I R] : IsAdicComplete I M :=
  { precomplete I b, hausdorff I b with }

end PaperXI.FiniteFreeCompletion

namespace PaperXI.CompleteResidueRealization
open IsLocalRing Polynomial
variable (R : Type*) [CommRing R] [IsDomain R] [IsDiscreteValuationRing R]
variable (s : Type*) [Field s] [Algebra (ResidueField R) s]
variable [FiniteDimensional (ResidueField R) s] [Algebra.IsSeparable (ResidueField R) s]
variable [IsAdicComplete (maximalIdeal R) R]

theorem complete :
    IsAdicComplete (maximalIdeal (ResidueExtensionRealization.ring R s))
      (ResidueExtensionRealization.ring R s) := by
  let b := AdjoinRoot.powerBasis'
    (ResidueExtensionRealization.monic R s).out
  have hc := FiniteFreeCompletion.complete (maximalIdeal R) b.basis
  rw [MonicResidueAlgebra.maximalIdeal_eq, MonicResidueAlgebra.specialIdeal]
  exact { IsPrecomplete.map_algebraMap_iff.mpr hc.toIsPrecomplete,
          IsHausdorff.map_algebraMap_iff.mpr hc.toIsHausdorff with }

end PaperXI.CompleteResidueRealization
