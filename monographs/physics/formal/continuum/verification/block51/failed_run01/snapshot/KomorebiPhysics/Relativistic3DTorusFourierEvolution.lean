import KomorebiPhysics.Relativistic3DFullFourierEvolution
import Mathlib.Analysis.Fourier.AddCircleMulti
import Mathlib.Analysis.InnerProductSpace.PiL2

/-!
# Physical torus Fourier evolution

This module constructs the unitary Fourier-series equivalence between the physical
four-spinor Hilbert space on the flat three-torus and the complete square-summable
mode-coefficient space.  The full continuum and central-difference propagators from
`Relativistic3DFullFourierEvolution` are conjugated through this equivalence.

The resulting physical torus propagators are exact linear isometric equivalences,
satisfy the time-group law, and converge strongly and uniformly on every compact
time interval for every torus `L²` spinor field.

The unbounded continuum Dirac generator and its weighted Fourier domain are kept
separate from this block.
-/

noncomputable section
set_option autoImplicit false
set_option maxHeartbeats 1000000

open Filter
open scoped ENNReal BigOperators Topology lp
open MeasureTheory WithLp

namespace KomorebiPhysics
namespace Relativistic3DTorusFourierEvolution

open Relativistic3DFourierL2Generator
open Relativistic3DFullFourierEvolution

local instance : MeasureSpace UnitAddCircle := ⟨AddCircle.haarAddCircle⟩
local instance : Measure.IsAddHaarMeasure (volume : Measure UnitAddCircle) :=
  inferInstanceAs (Measure.IsAddHaarMeasure AddCircle.haarAddCircle)
local instance : IsProbabilityMeasure (volume : Measure UnitAddCircle) :=
  inferInstanceAs (IsProbabilityMeasure AddCircle.haarAddCircle)

abbrev Mode := Relativistic3DFullFourierEvolution.Mode
abbrev HilbertSpinor := Relativistic3DFourierHilbertStability.HilbertSpinor
abbrev ScalarTorusL2 := Lp ℂ 2 (volume : Measure (UnitAddTorus (Fin 3)))
abbrev TorusSpinorL2 := PiLp 2 (fun _ : Fin 4 => ScalarTorusL2)
abbrev CoeffL2 := Relativistic3DFullFourierEvolution.CoeffL2

/-- The four-spinor Fourier coefficient at one spatial mode. -/
def torusCoeff (f : TorusSpinorL2) (n : Mode) : HilbertSpinor :=
  toLp 2 (fun j => UnitAddTorus.mFourierBasis.repr (f j) n)

@[simp] theorem torusCoeff_apply (f : TorusSpinorL2) (n : Mode) (j : Fin 4) :
    torusCoeff f n j = UnitAddTorus.mFourierBasis.repr (f j) n := rfl

/-- Parseval at one mode, summed over the four spinor coordinates. -/
theorem norm_torusCoeff_sq (f : TorusSpinorL2) (n : Mode) :
    ‖torusCoeff f n‖ ^ 2 =
      ∑ j : Fin 4, ‖UnitAddTorus.mFourierBasis.repr (f j) n‖ ^ 2 := by
  simpa [torusCoeff] using
    (PiLp.norm_sq_eq_of_L2 (fun _ : Fin 4 => ℂ) (torusCoeff f n))

/-- The complete square-summable Fourier coefficient field of a torus spinor. -/
def torusCoeffL2 (f : TorusSpinorL2) : CoeffL2 :=
  ⟨fun n => torusCoeff f n, by
    change Memℓp (fun n => torusCoeff f n) 2
    rw [memℓp_gen_iff (by norm_num : 0 < (2 : ℝ≥0∞).toReal)]
    norm_num
    simp_rw [norm_torusCoeff_sq]
    exact summable_sum (s := Finset.univ) fun j _ =>
      (by simpa using
        (UnitAddTorus.mFourierBasis.repr (f j)).prop.summable (by norm_num))⟩

@[simp] theorem torusCoeffL2_apply (f : TorusSpinorL2) (n : Mode) :
    torusCoeffL2 f n = torusCoeff f n := rfl

/-- Fourier synthesis of the coordinatewise scalar coefficients reconstructs the field. -/
theorem modeEmbed_torusCoeffL2 (f : TorusSpinorL2) :
    modeEmbed_orthogonalFamily.linearIsometry (torusCoeffL2 f) = f := by
  apply PiLp.ext
  intro j
  have hs := modeEmbed_orthogonalFamily.hasSum_linearIsometry (torusCoeffL2 f)
  have hsj := (PiLp.proj (𝕜 := ℂ) 2 (fun _ : Fin 4 => ScalarTorusL2) j).hasSum hs
  have hfour := UnitAddTorus.mFourierBasis.hasSum_repr (f j)
  have hsj' : HasSum
      (fun i => UnitAddTorus.mFourierBasis.repr (f j) i •
        UnitAddTorus.mFourierBasis i)
      ((modeEmbed_orthogonalFamily.linearIsometry (torusCoeffL2 f)) j) := by
    simpa [torusCoeffL2, torusCoeff, modeEmbedIsometry_apply,
      modeEmbed_apply, UnitAddTorus.coe_mFourierBasis] using hsj
  exact hsj'.unique hfour

/-- The Fourier-mode Hilbert-sum synthesis map is onto physical torus `L²`. -/
theorem modeEmbed_linearIsometry_surjective :
    Function.Surjective
      (modeEmbed_orthogonalFamily.linearIsometry : CoeffL2 → TorusSpinorL2) := by
  intro f
  exact ⟨torusCoeffL2 f, modeEmbed_torusCoeffL2 f⟩

/-- The mode embeddings exhibit torus spinor `L²` as the Hilbert sum of mode spinors. -/
theorem modeEmbed_isHilbertSum :
    IsHilbertSum ℂ (fun _ : Mode => HilbertSpinor) modeEmbedIsometry :=
  IsHilbertSum.ofSurjective modeEmbed_orthogonalFamily modeEmbed_linearIsometry_surjective

/-- Unitary Fourier-series equivalence from physical torus spinors to mode coefficients. -/
def torusFourierEquiv : TorusSpinorL2 ≃ₗᵢ[ℂ] CoeffL2 :=
  modeEmbed_isHilbertSum.linearIsometryEquiv

@[simp] theorem torusFourierEquiv_symm_apply (a : CoeffL2) :
    torusFourierEquiv.symm a = modeEmbed_orthogonalFamily.linearIsometry a := rfl

/-- The Fourier equivalence returns the coordinatewise scalar Fourier coefficients. -/
theorem torusFourierEquiv_apply_eq (f : TorusSpinorL2) :
    torusFourierEquiv f = torusCoeffL2 f := by
  apply torusFourierEquiv.symm.injective
  rw [LinearIsometryEquiv.symm_apply_apply]
  rw [torusFourierEquiv_symm_apply]
  exact (modeEmbed_torusCoeffL2 f).symm

@[simp] theorem torusFourierEquiv_apply_coeff
    (f : TorusSpinorL2) (n : Mode) (j : Fin 4) :
    torusFourierEquiv f n j = UnitAddTorus.mFourierBasis.repr (f j) n := by
  rw [torusFourierEquiv_apply_eq]
  rfl

/-- Fourier synthesis converges in torus `L²` for every square-summable coefficient field. -/
theorem hasSum_torusFourierSeries (a : CoeffL2) :
    HasSum (fun n => modeEmbedIsometry n (a n)) (torusFourierEquiv.symm a) := by
  exact modeEmbed_isHilbertSum.hasSum_linearIsometryEquiv_symm a

@[simp] theorem torusFourierEquiv_symm_single (n : Mode) (ψ : HilbertSpinor) :
    torusFourierEquiv.symm (lp.single 2 n ψ) = modeEmbedIsometry n ψ := by
  exact modeEmbed_isHilbertSum.linearIsometryEquiv_symm_apply_single ψ

@[simp] theorem torusFourierEquiv_modeEmbed (n : Mode) (ψ : HilbertSpinor) :
    torusFourierEquiv (modeEmbedIsometry n ψ) = lp.single 2 n ψ := by
  apply torusFourierEquiv.symm.injective
  simp

/-- Continuum Dirac evolution transported to physical torus spinor `L²`. -/
def continuumTorusUnitary (m t : ℝ) : TorusSpinorL2 ≃ₗᵢ[ℂ] TorusSpinorL2 :=
  torusFourierEquiv.trans ((continuumCoeffUnitary m t).trans torusFourierEquiv.symm)

/-- Central-difference evolution transported to physical torus spinor `L²`. -/
def centralTorusUnitary (m h t : ℝ) : TorusSpinorL2 ≃ₗᵢ[ℂ] TorusSpinorL2 :=
  torusFourierEquiv.trans ((centralCoeffUnitary m h t).trans torusFourierEquiv.symm)

@[simp] theorem torusFourierEquiv_continuumTorusUnitary_apply
    (m t : ℝ) (f : TorusSpinorL2) :
    torusFourierEquiv (continuumTorusUnitary m t f) =
      continuumCoeffUnitary m t (torusFourierEquiv f) := by
  change torusFourierEquiv
      (torusFourierEquiv.symm (continuumCoeffUnitary m t (torusFourierEquiv f))) = _
  exact torusFourierEquiv.apply_symm_apply _

@[simp] theorem torusFourierEquiv_centralTorusUnitary_apply
    (m h t : ℝ) (f : TorusSpinorL2) :
    torusFourierEquiv (centralTorusUnitary m h t f) =
      centralCoeffUnitary m h t (torusFourierEquiv f) := by
  change torusFourierEquiv
      (torusFourierEquiv.symm (centralCoeffUnitary m h t (torusFourierEquiv f))) = _
  exact torusFourierEquiv.apply_symm_apply _

/-- Exact continuum norm preservation on physical torus `L²`. -/
theorem norm_continuumTorusUnitary (m t : ℝ) (f : TorusSpinorL2) :
    ‖continuumTorusUnitary m t f‖ = ‖f‖ :=
  (continuumTorusUnitary m t).norm_map f

/-- Exact lattice norm preservation on physical torus `L²`. -/
theorem norm_centralTorusUnitary (m h t : ℝ) (f : TorusSpinorL2) :
    ‖centralTorusUnitary m h t f‖ = ‖f‖ :=
  (centralTorusUnitary m h t).norm_map f

/-- Exact continuum inner-product preservation on physical torus `L²`. -/
theorem inner_continuumTorusUnitary (m t : ℝ) (f g : TorusSpinorL2) :
    inner ℂ (continuumTorusUnitary m t f) (continuumTorusUnitary m t g) =
      inner ℂ f g :=
  (continuumTorusUnitary m t).inner_map_map f g

/-- Exact lattice inner-product preservation on physical torus `L²`. -/
theorem inner_centralTorusUnitary (m h t : ℝ) (f g : TorusSpinorL2) :
    inner ℂ (centralTorusUnitary m h t f) (centralTorusUnitary m h t g) =
      inner ℂ f g :=
  (centralTorusUnitary m h t).inner_map_map f g

/-- Continuum torus evolution satisfies the time-group law. -/
theorem continuumTorusUnitary_add_time (m s t : ℝ) (f : TorusSpinorL2) :
    continuumTorusUnitary m (s + t) f =
      continuumTorusUnitary m s (continuumTorusUnitary m t f) := by
  apply torusFourierEquiv.injective
  simp [continuumCoeffUnitary_apply, continuumCoeffPropagator_add_time]

/-- Lattice torus evolution satisfies the time-group law. -/
theorem centralTorusUnitary_add_time (m h s t : ℝ) (f : TorusSpinorL2) :
    centralTorusUnitary m h (s + t) f =
      centralTorusUnitary m h s (centralTorusUnitary m h t f) := by
  apply torusFourierEquiv.injective
  simp [centralCoeffUnitary_apply, centralCoeffPropagator_add_time]

/-- Physical-torus propagator residual. -/
def fullTorusResidual (m h t : ℝ) (f : TorusSpinorL2) : TorusSpinorL2 :=
  centralTorusUnitary m h t f - continuumTorusUnitary m t f

/-- Fourier transport preserves the exact propagator residual norm. -/
theorem norm_fullTorusResidual_eq_coeff (m h t : ℝ) (f : TorusSpinorL2) :
    ‖fullTorusResidual m h t f‖ =
      ‖fullCoeffResidual m h t (torusFourierEquiv f)‖ := by
  calc
    ‖fullTorusResidual m h t f‖ =
        ‖torusFourierEquiv (fullTorusResidual m h t f)‖ :=
      (torusFourierEquiv.norm_map _).symm
    _ = ‖fullCoeffResidual m h t (torusFourierEquiv f)‖ := by
      simp [fullTorusResidual, fullCoeffResidual]

/-- Compact-time strong convergence on physical torus spinor `L²`. -/
theorem fullTorusPropagator_compactTime_converges (m T : ℝ) (hT : 0 ≤ T)
    (f : TorusSpinorL2) :
    ∀ ε > 0, ∀ᶠ h in 𝓝[>] (0 : ℝ), ∀ t : ℝ, |t| ≤ T →
      ‖centralTorusUnitary m h t f - continuumTorusUnitary m t f‖ < ε := by
  intro ε hε
  have hc := fullCoeffPropagator_compactTime_converges
    m T hT (torusFourierEquiv f) ε hε
  filter_upwards [hc] with h hh
  intro t ht
  rw [show centralTorusUnitary m h t f - continuumTorusUnitary m t f =
      fullTorusResidual m h t f by rfl]
  rw [norm_fullTorusResidual_eq_coeff]
  exact hh t ht

/-- Pointwise strong convergence on physical torus spinor `L²`. -/
theorem tendsto_centralTorusUnitary (m t : ℝ) (f : TorusSpinorL2) :
    Tendsto (fun h : ℝ => centralTorusUnitary m h t f)
      (𝓝[>] (0 : ℝ)) (𝓝 (continuumTorusUnitary m t f)) := by
  rw [Metric.tendsto_nhds]
  intro ε hε
  filter_upwards [fullTorusPropagator_compactTime_converges
      m |t| (abs_nonneg t) f ε hε] with h hh
  have hres := hh t le_rfl
  simpa [dist_eq_norm, norm_sub_rev] using hres

end Relativistic3DTorusFourierEvolution
end KomorebiPhysics
