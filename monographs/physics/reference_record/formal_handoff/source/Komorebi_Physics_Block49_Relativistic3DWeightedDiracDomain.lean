import KomorebiPhysics.Relativistic3DUnboundedDirac

/-!
# Weighted Fourier domain and physical torus Dirac Hamiltonian

This module identifies the maximal coefficient-space domain of the free Dirac
multiplier with the inhomogeneous first-order Fourier condition, proves the
exact modal and global energy identities, and transports the unbounded
Hamiltonian through the checked torus Fourier equivalence.  The transported
physical-space partial operator is densely defined, self-adjoint, and closed.

The module does not identify the unitary evolution with an unbounded functional
calculus exponential and does not assert strong-resolvent convergence.
-/

noncomputable section
set_option autoImplicit false
set_option maxHeartbeats 1000000

open scoped ENNReal BigOperators Topology lp LinearPMap

namespace KomorebiPhysics
namespace Relativistic3DWeightedDomain

open Relativistic3DFourierGenerator
open Relativistic3DFourierHilbertStability
open Relativistic3DFourierL2Generator
open Relativistic3DUnboundedDirac

abbrev HilbertSpinor := Relativistic3DFourierHilbertStability.HilbertSpinor

/-- Squared continuum energy of one torus Fourier mode. -/
def modeEnergySq (m : ℝ) (n : Relativistic3DUnboundedDirac.Mode) : ℝ :=
  symbolEnergySq m (modeMomentum n 0) (modeMomentum n 1) (modeMomentum n 2)

lemma continuumHilbertModeOperator_apply_as_spinor
    (m : ℝ) (n : Relativistic3DUnboundedDirac.Mode) (ψ : HilbertSpinor) :
    continuumHilbertModeOperator m n ψ =
      spinorToHilbert (continuumModeAction m n (hilbertToSpinor ψ)) := by
  rfl

lemma continuumHilbertModeOperator_sq
    (m : ℝ) (n : Relativistic3DUnboundedDirac.Mode) (ψ : HilbertSpinor) :
    continuumHilbertModeOperator m n
        (continuumHilbertModeOperator m n ψ) =
      (modeEnergySq m n : ℂ) • ψ := by
  rw [continuumHilbertModeOperator_apply_as_spinor]
  rw [continuumHilbertModeOperator_apply_as_spinor]
  change spinorToHilbert
      (continuumModeAction m n
        (continuumModeAction m n (hilbertToSpinor ψ))) = _
  rw [show continuumModeAction m n
      (continuumModeAction m n (hilbertToSpinor ψ)) =
      (modeEnergySq m n : ℂ) • hilbertToSpinor ψ by
        exact continuumDiracSymbol_sq m (modeMomentum n 0)
          (modeMomentum n 1) (modeMomentum n 2) (hilbertToSpinor ψ)]
  rfl

end Relativistic3DWeightedDomain
end KomorebiPhysics

namespace KomorebiPhysics
namespace Relativistic3DWeightedDomain

open Relativistic3DFourierGenerator
open Relativistic3DFourierHilbertStability
open Relativistic3DFourierL2Generator
open Relativistic3DUnboundedDirac

lemma modeEnergySq_nonneg (m : ℝ) (n : Relativistic3DUnboundedDirac.Mode) : 0 ≤ modeEnergySq m n := by
  unfold modeEnergySq symbolEnergySq
  positivity

lemma inner_continuumHilbertModeOperator_self
    (m : ℝ) (n : Relativistic3DUnboundedDirac.Mode) (ψ : HilbertSpinor) :
    inner ℂ (continuumHilbertModeOperator m n ψ)
        (continuumHilbertModeOperator m n ψ) =
      (modeEnergySq m n : ℂ) * inner ℂ ψ ψ := by
  calc
    inner ℂ (continuumHilbertModeOperator m n ψ)
        (continuumHilbertModeOperator m n ψ) =
      inner ℂ ψ (continuumHilbertModeOperator m n
        (continuumHilbertModeOperator m n ψ)) := by
          simpa using (continuumHilbertModeOperator_symmetric m n ψ
            (continuumHilbertModeOperator m n ψ))
    _ = inner ℂ ψ ((modeEnergySq m n : ℂ) • ψ) := by
      rw [continuumHilbertModeOperator_sq]
    _ = (modeEnergySq m n : ℂ) * inner ℂ ψ ψ := by
      rw [inner_smul_right]

lemma norm_continuumHilbertModeOperator_sq
    (m : ℝ) (n : Relativistic3DUnboundedDirac.Mode) (ψ : HilbertSpinor) :
    ‖continuumHilbertModeOperator m n ψ‖ ^ 2 =
      modeEnergySq m n * ‖ψ‖ ^ 2 := by
  calc
    ‖continuumHilbertModeOperator m n ψ‖ ^ 2 =
        Complex.re (inner ℂ (continuumHilbertModeOperator m n ψ)
          (continuumHilbertModeOperator m n ψ)) := by
            simpa using (norm_sq_eq_re_inner (𝕜 := ℂ)
              (continuumHilbertModeOperator m n ψ))
    _ = Complex.re ((modeEnergySq m n : ℂ) * inner ℂ ψ ψ) := by
      rw [inner_continuumHilbertModeOperator_self]
    _ = modeEnergySq m n * ‖ψ‖ ^ 2 := by
      rw [inner_self_eq_norm_sq_to_K]
      simp [Complex.mul_re, pow_two]

end Relativistic3DWeightedDomain
end KomorebiPhysics

namespace KomorebiPhysics
namespace Relativistic3DWeightedDomain

open Relativistic3DFourierGenerator
open Relativistic3DFourierHilbertStability
open Relativistic3DFourierL2Generator
open Relativistic3DUnboundedDirac

/-- Pointwise first-order Fourier energy carried by a coefficient field. -/
def weightedModeTerm (m : ℝ) (f : CoeffL2) (n : Relativistic3DUnboundedDirac.Mode) : ℝ :=
  modeEnergySq m n * ‖f n‖ ^ 2

lemma diracCoeff_norm_sq (m : ℝ) (f : CoeffL2) (n : Relativistic3DUnboundedDirac.Mode) :
    ‖diracCoeff m f n‖ ^ 2 = weightedModeTerm m f n := by
  exact norm_continuumHilbertModeOperator_sq m n (f n)

/-- Exact weighted Fourier characterization of the maximal continuum Dirac domain. -/
theorem mem_continuumDiracDomain_iff_summable_weighted
    (m : ℝ) (f : CoeffL2) :
    f ∈ continuumDiracDomain m ↔
      Summable (fun n => weightedModeTerm m f n) := by
  constructor
  · intro hf
    have hs := (mem_continuumDiracDomain_iff m f).mp hf
    have hsum := hs.summable (p := (2 : ℝ≥0∞)) (by norm_num)
    simpa [weightedModeTerm, diracCoeff_norm_sq] using hsum
  · intro hsum
    rw [mem_continuumDiracDomain_iff]
    apply memℓp_gen
    simpa [weightedModeTerm, diracCoeff_norm_sq] using hsum

end Relativistic3DWeightedDomain
end KomorebiPhysics

namespace KomorebiPhysics
namespace Relativistic3DWeightedDomain

open Relativistic3DFourierGenerator
open Relativistic3DFourierHilbertStability
open Relativistic3DFourierL2Generator
open Relativistic3DUnboundedDirac

/-- Squared spatial momentum of a torus Fourier mode. -/
def momentumNormSq (n : Relativistic3DUnboundedDirac.Mode) : ℝ :=
  (modeMomentum n 0) ^ 2 + (modeMomentum n 1) ^ 2 + (modeMomentum n 2) ^ 2

@[simp] lemma modeEnergySq_eq_mass_add_momentum
    (m : ℝ) (n : Relativistic3DUnboundedDirac.Mode) :
    modeEnergySq m n = m ^ 2 + momentumNormSq n := by
  simp [modeEnergySq, symbolEnergySq, momentumNormSq]
  ring

/-- Pure spatial first-order Fourier energy. -/
def momentumModeTerm (f : CoeffL2)
    (n : Relativistic3DUnboundedDirac.Mode) : ℝ :=
  momentumNormSq n * ‖f n‖ ^ 2

/-- Standard inhomogeneous first-order Fourier weight. -/
def h1ModeTerm (f : CoeffL2)
    (n : Relativistic3DUnboundedDirac.Mode) : ℝ :=
  (1 + momentumNormSq n) * ‖f n‖ ^ 2

lemma summable_coeff_norm_sq (f : CoeffL2) :
    Summable (fun n => ‖f n‖ ^ 2) := by
  have h := (lp.memℓp f).summable (p := (2 : ℝ≥0∞)) (by norm_num)
  simpa using h

lemma weightedModeTerm_eq_mass_add_momentum
    (m : ℝ) (f : CoeffL2) (n : Relativistic3DUnboundedDirac.Mode) :
    weightedModeTerm m f n =
      m ^ 2 * ‖f n‖ ^ 2 + momentumModeTerm f n := by
  simp [weightedModeTerm, momentumModeTerm, modeEnergySq_eq_mass_add_momentum]
  ring

lemma h1ModeTerm_eq_norm_add_momentum
    (f : CoeffL2) (n : Relativistic3DUnboundedDirac.Mode) :
    h1ModeTerm f n = ‖f n‖ ^ 2 + momentumModeTerm f n := by
  simp [h1ModeTerm, momentumModeTerm]
  ring

lemma summable_weighted_iff_momentum (m : ℝ) (f : CoeffL2) :
    Summable (fun n => weightedModeTerm m f n) ↔
      Summable (fun n => momentumModeTerm f n) := by
  constructor
  · intro h
    exact h.of_nonneg_of_le (fun n => by
      unfold momentumModeTerm momentumNormSq
      positivity) (fun n => by
        rw [weightedModeTerm_eq_mass_add_momentum]
        have hm : 0 ≤ m ^ 2 * ‖f n‖ ^ 2 := mul_nonneg (sq_nonneg m) (sq_nonneg _)
        linarith)
  · intro h
    have hm : Summable (fun n => m ^ 2 * ‖f n‖ ^ 2) :=
      (summable_coeff_norm_sq f).mul_left (m ^ 2)
    exact (hm.add h).congr (fun n => (weightedModeTerm_eq_mass_add_momentum m f n).symm)

lemma summable_h1_iff_momentum (f : CoeffL2) :
    Summable (fun n => h1ModeTerm f n) ↔
      Summable (fun n => momentumModeTerm f n) := by
  constructor
  · intro h
    exact h.of_nonneg_of_le (fun n => by
      unfold momentumModeTerm momentumNormSq
      positivity) (fun n => by
        rw [h1ModeTerm_eq_norm_add_momentum]
        linarith [sq_nonneg ‖f n‖])
  · intro h
    exact ((summable_coeff_norm_sq f).add h).congr
      (fun n => (h1ModeTerm_eq_norm_add_momentum f n).symm)

/-- The maximal free Dirac domain is exactly the inhomogeneous first-order
Fourier-Sobolev condition. -/
theorem mem_continuumDiracDomain_iff_summable_h1
    (m : ℝ) (f : CoeffL2) :
    f ∈ continuumDiracDomain m ↔
      Summable (fun n => h1ModeTerm f n) := by
  rw [mem_continuumDiracDomain_iff_summable_weighted]
  exact (summable_weighted_iff_momentum m f).trans
    (summable_h1_iff_momentum f).symm

/-- The maximal free Dirac domain is independent of the mass parameter. -/
theorem mem_continuumDiracDomain_iff_mass
    (m₁ m₂ : ℝ) (f : CoeffL2) :
    f ∈ continuumDiracDomain m₁ ↔ f ∈ continuumDiracDomain m₂ := by
  rw [mem_continuumDiracDomain_iff_summable_h1,
    mem_continuumDiracDomain_iff_summable_h1]

end Relativistic3DWeightedDomain
end KomorebiPhysics

namespace KomorebiPhysics
namespace Relativistic3DWeightedDomain

open Relativistic3DUnboundedDirac
open Relativistic3DTorusFourierEvolution
open Relativistic3DFourierHilbertStability

abbrev TorusSpinorL2 := Relativistic3DTorusFourierEvolution.TorusSpinorL2

/-- Physical torus domain obtained by Fourier transport of the maximal coefficient domain. -/
def physicalDiracDomain (m : ℝ) : Submodule ℂ TorusSpinorL2 :=
  (continuumDiracDomain m).comap torusFourierEquiv.toLinearMap

@[simp] lemma mem_physicalDiracDomain_iff (m : ℝ) (f : TorusSpinorL2) :
    f ∈ physicalDiracDomain m ↔ torusFourierEquiv f ∈ continuumDiracDomain m := Iff.rfl

/-- Fourier transport from the physical operator domain to the coefficient domain. -/
def physicalToCoeffDomain (m : ℝ) :
    physicalDiracDomain m →ₗ[ℂ] continuumDiracDomain m where
  toFun f := ⟨torusFourierEquiv f.1, f.2⟩
  map_add' := by
    intro f g
    ext n j
    simp
  map_smul' := by
    intro c f
    ext n j
    simp

/-- Physical torus realization of the continuum Dirac Hamiltonian. -/
def physicalDiracPMap (m : ℝ) : TorusSpinorL2 →ₗ.[ℂ] TorusSpinorL2 where
  domain := physicalDiracDomain m
  toFun := torusFourierEquiv.symm.toLinearMap.comp
    ((continuumDiracPMap m).toFun.comp (physicalToCoeffDomain m))

@[simp] theorem torusFourierEquiv_physicalDiracPMap_apply (m : ℝ)
    (f : (physicalDiracPMap m).domain) :
    torusFourierEquiv (physicalDiracPMap m f) =
      continuumDiracPMap m (physicalToCoeffDomain m f) := by
  change torusFourierEquiv
    (torusFourierEquiv.symm
      (continuumDiracPMap m (physicalToCoeffDomain m f))) = _
  exact torusFourierEquiv.apply_symm_apply _

@[simp] theorem physicalDiracPMap_apply_coeff (m : ℝ)
    (f : (physicalDiracPMap m).domain)
    (n : Relativistic3DUnboundedDirac.Mode) :
    torusFourierEquiv (physicalDiracPMap m f) n =
      continuumHilbertModeOperator m n (torusFourierEquiv f.1 n) := by
  rw [torusFourierEquiv_physicalDiracPMap_apply]
  rfl

/-- Physical domain in explicit first-order Fourier form. -/
theorem mem_physicalDiracDomain_iff_summable_h1 (m : ℝ) (f : TorusSpinorL2) :
    f ∈ physicalDiracDomain m ↔
      Summable (fun n => h1ModeTerm (torusFourierEquiv f) n) := by
  rw [mem_physicalDiracDomain_iff,
    mem_continuumDiracDomain_iff_summable_h1]

end Relativistic3DWeightedDomain
end KomorebiPhysics

namespace KomorebiPhysics
namespace Relativistic3DWeightedDomain

open Relativistic3DUnboundedDirac
open Relativistic3DTorusFourierEvolution

/-- The physical Fourier-transported Dirac domain is dense in torus `L²`. -/
theorem physicalDiracDomain_dense (m : ℝ) :
    Dense ((physicalDiracDomain m : Set TorusSpinorL2)) := by
  change Dense (torusFourierEquiv ⁻¹' (continuumDiracDomain m : Set Relativistic3DUnboundedDirac.CoeffL2))
  exact (continuumDiracDomain_dense m).preimage
    torusFourierEquiv.toHomeomorph.isOpenMap

/-- The physical torus Dirac partial map is symmetric. -/
theorem physicalDiracPMap_isFormalAdjoint (m : ℝ) :
    (physicalDiracPMap m).IsFormalAdjoint (physicalDiracPMap m) := by
  intro f g
  calc
    inner ℂ (physicalDiracPMap m f) g.1 =
        inner ℂ (torusFourierEquiv (physicalDiracPMap m f))
          (torusFourierEquiv g.1) :=
      (torusFourierEquiv.inner_map_map _ _).symm
    _ = inner ℂ (continuumDiracPMap m (physicalToCoeffDomain m f))
          (physicalToCoeffDomain m g).1 := by
      rw [torusFourierEquiv_physicalDiracPMap_apply]
      rfl
    _ = inner ℂ (physicalToCoeffDomain m f).1
          (continuumDiracPMap m (physicalToCoeffDomain m g)) :=
      continuumDiracPMap_isFormalAdjoint m
        (physicalToCoeffDomain m f) (physicalToCoeffDomain m g)
    _ = inner ℂ (torusFourierEquiv f.1)
          (torusFourierEquiv (physicalDiracPMap m g)) := by
      rw [torusFourierEquiv_physicalDiracPMap_apply]
      rfl
    _ = inner ℂ f.1 (physicalDiracPMap m g) :=
      torusFourierEquiv.inner_map_map _ _

/-- The symmetric physical torus Hamiltonian is contained in its adjoint. -/
theorem physicalDiracPMap_le_adjoint (m : ℝ) :
    physicalDiracPMap m ≤ (physicalDiracPMap m)† := by
  exact (physicalDiracPMap_isFormalAdjoint m).le_adjoint
    (physicalDiracDomain_dense m)

end Relativistic3DWeightedDomain
end KomorebiPhysics

namespace KomorebiPhysics
namespace Relativistic3DWeightedDomain

open Relativistic3DUnboundedDirac
open Relativistic3DTorusFourierEvolution

/-- Every vector in the adjoint domain of the physical realization already lies
in the Fourier-transported maximal Dirac domain. -/
theorem physicalDiracAdjoint_domain_le (m : ℝ) :
    ((physicalDiracPMap m)†).domain ≤ (physicalDiracPMap m).domain := by
  intro f hf
  apply continuumDiracAdjoint_domain_le m
  apply LinearPMap.mem_adjoint_domain_of_exists
  let f' : ((physicalDiracPMap m)†).domain := ⟨f, hf⟩
  use torusFourierEquiv ((physicalDiracPMap m)† f')
  intro x
  let yval : TorusSpinorL2 := torusFourierEquiv.symm x.1
  have hy : yval ∈ physicalDiracDomain m := by
    rw [mem_physicalDiracDomain_iff]
    change torusFourierEquiv (torusFourierEquiv.symm x.1) ∈ continuumDiracDomain m
    rw [torusFourierEquiv.apply_symm_apply]
    exact x.2
  let y : (physicalDiracPMap m).domain := ⟨yval, hy⟩
  have hadj := LinearPMap.adjoint_isFormalAdjoint
    (T := physicalDiracPMap m) (physicalDiracDomain_dense m)
  have hUy : torusFourierEquiv y.1 = x.1 := by
    change torusFourierEquiv (torusFourierEquiv.symm x.1) = x.1
    exact torusFourierEquiv.apply_symm_apply x.1
  have hcoeff : physicalToCoeffDomain m y = x := by
    apply Subtype.ext
    exact hUy
  calc
    inner ℂ (torusFourierEquiv ((physicalDiracPMap m)† f')) x.1
        = inner ℂ ((physicalDiracPMap m)† f') y.1 := by
          rw [← hUy]
          exact torusFourierEquiv.inner_map_map _ _
    _ = inner ℂ f'.1 (physicalDiracPMap m y) := hadj f' y
    _ = inner ℂ (torusFourierEquiv f'.1)
          (torusFourierEquiv (physicalDiracPMap m y)) :=
      (torusFourierEquiv.inner_map_map _ _).symm
    _ = inner ℂ (torusFourierEquiv f'.1)
          (continuumDiracPMap m (physicalToCoeffDomain m y)) := by
      rw [torusFourierEquiv_physicalDiracPMap_apply]
    _ = inner ℂ (torusFourierEquiv f'.1)
          (continuumDiracPMap m x) := by rw [hcoeff]

/-- The physical Hilbert adjoint is contained in the Fourier-transported
maximal Dirac multiplier. -/
theorem physicalDiracAdjoint_le (m : ℝ) :
    (physicalDiracPMap m)† ≤ physicalDiracPMap m := by
  refine ⟨physicalDiracAdjoint_domain_le m, ?_⟩
  intro f g hfg
  let y : (physicalDiracPMap m).domain :=
    ⟨f.1, (physicalDiracAdjoint_domain_le m) f.2⟩
  have hy : y = g := by
    apply Subtype.ext
    exact hfg
  have heq : (physicalDiracPMap m)† f = physicalDiracPMap m y := by
    apply LinearPMap.adjoint_apply_eq (physicalDiracDomain_dense m)
    intro x
    simpa [y] using physicalDiracPMap_isFormalAdjoint m y x
  simpa [hy] using heq

/-- The physical torus realization of the free Dirac Hamiltonian is self-adjoint. -/
theorem physicalDiracPMap_selfAdjoint (m : ℝ) :
    IsSelfAdjoint (physicalDiracPMap m) := by
  rw [LinearPMap.isSelfAdjoint_def]
  exact le_antisymm (physicalDiracAdjoint_le m)
    (physicalDiracPMap_le_adjoint m)

/-- The physical torus Dirac Hamiltonian is closed. -/
theorem physicalDiracPMap_isClosed (m : ℝ) :
    (physicalDiracPMap m).IsClosed :=
  (physicalDiracPMap_selfAdjoint m).isClosed

end Relativistic3DWeightedDomain
end KomorebiPhysics

namespace KomorebiPhysics
namespace Relativistic3DWeightedDomain

open Relativistic3DUnboundedDirac
open Relativistic3DTorusFourierEvolution

/-- Exact coefficient-space energy identity for the unbounded Dirac multiplier. -/
theorem norm_continuumDiracPMap_sq_eq_tsum_weighted
    (m : ℝ) (f : (continuumDiracPMap m).domain) :
    ‖continuumDiracPMap m f‖ ^ 2 =
      ∑' n, weightedModeTerm m f.1 n := by
  calc
    ‖continuumDiracPMap m f‖ ^ 2 =
        ∑' n, ‖(continuumDiracPMap m f) n‖ ^ 2 := by
      simpa using lp.norm_rpow_eq_tsum
        (by norm_num : 0 < (2 : ℝ≥0∞).toReal) (continuumDiracPMap m f)
    _ = ∑' n, weightedModeTerm m f.1 n := by
      apply tsum_congr
      intro n
      rw [continuumDiracPMap_apply]
      exact diracCoeff_norm_sq m f.1 n

/-- The physical maximal Dirac domain is independent of the mass. -/
theorem mem_physicalDiracDomain_iff_mass
    (m₁ m₂ : ℝ) (f : TorusSpinorL2) :
    f ∈ physicalDiracDomain m₁ ↔ f ∈ physicalDiracDomain m₂ := by
  rw [mem_physicalDiracDomain_iff_summable_h1,
    mem_physicalDiracDomain_iff_summable_h1]

/-- The physical domains for any two masses are equal as submodules. -/
theorem physicalDiracDomain_eq_mass (m₁ m₂ : ℝ) :
    physicalDiracDomain m₁ = physicalDiracDomain m₂ := by
  ext f
  exact mem_physicalDiracDomain_iff_mass m₁ m₂ f

/-- Exact physical-space energy identity after Fourier transport. -/
theorem norm_physicalDiracPMap_sq_eq_tsum_weighted
    (m : ℝ) (f : (physicalDiracPMap m).domain) :
    ‖physicalDiracPMap m f‖ ^ 2 =
      ∑' n, weightedModeTerm m (torusFourierEquiv f.1) n := by
  calc
    ‖physicalDiracPMap m f‖ ^ 2 =
        ‖torusFourierEquiv (physicalDiracPMap m f)‖ ^ 2 := by
      rw [torusFourierEquiv.norm_map]
    _ = ‖continuumDiracPMap m (physicalToCoeffDomain m f)‖ ^ 2 := by
      rw [torusFourierEquiv_physicalDiracPMap_apply]
    _ = ∑' n, weightedModeTerm m
          (physicalToCoeffDomain m f).1 n :=
      norm_continuumDiracPMap_sq_eq_tsum_weighted m
        (physicalToCoeffDomain m f)
    _ = ∑' n, weightedModeTerm m (torusFourierEquiv f.1) n := rfl

end Relativistic3DWeightedDomain
end KomorebiPhysics
