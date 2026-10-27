import KomorebiPhysics.Relativistic3DTorusFourierEvolution
import Mathlib.Analysis.InnerProductSpace.LinearPMap

/-!
# Unbounded continuum Dirac multiplier on Fourier coefficients

This module defines the free continuum Dirac Hamiltonian as a densely defined
partial linear map on the complete coefficient Hilbert space `ℓ²(ℤ³; ℂ⁴)`.
Its maximal domain consists exactly of coefficient fields for which the modewise
Dirac action is square summable.  The operator is proved symmetric,
self-adjoint, and closed.  Finite Fourier truncations preserve the domain,
commute with the multiplier, and approximate every domain vector together with
its image, giving the finite Fourier graph-core approximation property.
-/

noncomputable section
set_option autoImplicit false
set_option maxHeartbeats 1000000

open Filter
open scoped ENNReal BigOperators Topology lp LinearPMap

namespace KomorebiPhysics
namespace Relativistic3DUnboundedDirac

open Relativistic3DFourierHilbertStability
open Relativistic3DFullFourierEvolution

abbrev Mode := Relativistic3DFullFourierEvolution.Mode
abbrev HilbertSpinor := Relativistic3DFourierHilbertStability.HilbertSpinor
abbrev CoeffL2 := Relativistic3DFullFourierEvolution.CoeffL2

/-- The pointwise continuum Dirac multiplier on coefficient fields. -/
def diracCoeff (m : ℝ) (f : CoeffL2) (n : Mode) : HilbertSpinor :=
  continuumHilbertModeOperator m n (f n)

@[simp] theorem diracCoeff_zero (m : ℝ) (n : Mode) :
    diracCoeff m (0 : CoeffL2) n = 0 := by
  simp [diracCoeff]

@[simp] theorem diracCoeff_add (m : ℝ) (f g : CoeffL2) (n : Mode) :
    diracCoeff m (f + g) n = diracCoeff m f n + diracCoeff m g n := by
  simp [diracCoeff]

@[simp] theorem diracCoeff_smul (m : ℝ) (c : ℂ) (f : CoeffL2) (n : Mode) :
    diracCoeff m (c • f) n = c • diracCoeff m f n := by
  simp [diracCoeff]

/-- Natural maximal Fourier domain of the free continuum Dirac multiplier. -/
def continuumDiracDomain (m : ℝ) : Submodule ℂ CoeffL2 where
  carrier := {f | Memℓp (diracCoeff m f) 2}
  zero_mem' := by
    change Memℓp (diracCoeff m (0 : CoeffL2)) 2
    convert (zero_memℓp : Memℓp (fun _ : Mode => (0 : HilbertSpinor)) 2) using 1
    funext n
    exact diracCoeff_zero m n
  add_mem' := by
    intro f g hf hg
    change Memℓp (diracCoeff m (f + g)) 2
    convert hf.add hg using 1
    funext n
    exact diracCoeff_add m f g n
  smul_mem' := by
    intro c f hf
    change Memℓp (diracCoeff m (c • f)) 2
    convert hf.const_smul c using 1
    funext n
    exact diracCoeff_smul m c f n

@[simp] theorem mem_continuumDiracDomain_iff (m : ℝ) (f : CoeffL2) :
    f ∈ continuumDiracDomain m ↔ Memℓp (diracCoeff m f) 2 := Iff.rfl

/-- The square-summable modewise Dirac output of a domain vector. -/
def continuumDiracOutput (m : ℝ) (f : continuumDiracDomain m) : CoeffL2 :=
  ⟨diracCoeff m f.1, f.2⟩

@[simp] theorem continuumDiracOutput_apply (m : ℝ)
    (f : continuumDiracDomain m) (n : Mode) :
    continuumDiracOutput m f n = continuumHilbertModeOperator m n (f.1 n) := rfl

/-- The free continuum Dirac Hamiltonian as a partially defined linear map. -/
def continuumDiracPMap (m : ℝ) : CoeffL2 →ₗ.[ℂ] CoeffL2 where
  domain := continuumDiracDomain m
  toFun :=
    { toFun := continuumDiracOutput m
      map_add' := by
        intro f g
        apply lp.ext
        funext n
        simp [continuumDiracOutput_apply]
      map_smul' := by
        intro c f
        apply lp.ext
        funext n
        simp [continuumDiracOutput_apply] }

@[simp] theorem continuumDiracPMap_apply (m : ℝ)
    (f : (continuumDiracPMap m).domain) (n : Mode) :
    continuumDiracPMap m f n = continuumHilbertModeOperator m n (f.1 n) := rfl

/-- A single Fourier mode lies in the maximal Dirac domain. -/
theorem single_mem_continuumDiracDomain (m : ℝ) (n : Mode) (ψ : HilbertSpinor) :
    lp.single 2 n ψ ∈ continuumDiracDomain m := by
  change Memℓp (diracCoeff m (lp.single 2 n ψ)) 2
  have h : diracCoeff m (lp.single 2 n ψ) =
      (lp.single 2 n (continuumHilbertModeOperator m n ψ) : Mode → HilbertSpinor) := by
    funext k
    by_cases hk : k = n
    · subst hk
      simp [diracCoeff]
    · simp [diracCoeff, hk]
  let s : CoeffL2 := lp.single 2 n (continuumHilbertModeOperator m n ψ)
  have hs : Memℓp (fun k => s k) 2 := s.prop
  convert hs using 1

/-- The Dirac operator acts diagonally on a single Fourier mode. -/
theorem continuumDiracPMap_single_apply (m : ℝ) (n : Mode) (ψ : HilbertSpinor) :
    continuumDiracPMap m
      ⟨lp.single 2 n ψ, single_mem_continuumDiracDomain m n ψ⟩ =
      lp.single 2 n (continuumHilbertModeOperator m n ψ) := by
  apply lp.ext
  funext k
  by_cases hk : k = n
  · subst hk
    simp [continuumDiracPMap_apply]
  · simp [continuumDiracPMap_apply, hk]

/-- Every finite Fourier truncation belongs to the continuum Dirac domain. -/
theorem coeffTruncation_mem_continuumDiracDomain (m : ℝ)
    (S : Finset Mode) (f : CoeffL2) :
    coeffTruncation S f ∈ continuumDiracDomain m := by
  classical
  unfold coeffTruncation
  apply Submodule.sum_mem
  intro n hn
  exact single_mem_continuumDiracDomain m n (f n)

/-- The maximal Fourier Dirac domain is dense in coefficient `ℓ²`. -/
theorem continuumDiracDomain_dense (m : ℝ) :
    Dense ((continuumDiracDomain m : Set CoeffL2)) := by
  rw [Metric.dense_iff]
  intro f r hr
  obtain ⟨S, hS⟩ := exists_coeffTruncation_approx f hr
  refine ⟨coeffTruncation S f, ?_, ?_⟩
  · simpa [Metric.mem_ball, dist_eq_norm, norm_sub_rev] using hS
  · exact coeffTruncation_mem_continuumDiracDomain m S f

/-- The diagonal continuum Dirac partial map is symmetric on its maximal domain. -/
theorem continuumDiracPMap_isFormalAdjoint (m : ℝ) :
    (continuumDiracPMap m).IsFormalAdjoint (continuumDiracPMap m) := by
  intro f g
  rw [lp.inner_eq_tsum, lp.inner_eq_tsum]
  apply tsum_congr
  intro n
  exact continuumHilbertModeOperator_symmetric m n (f.1 n) (g.1 n)


/-- The symmetric Dirac multiplier is contained in its Hilbert adjoint. -/
theorem continuumDiracPMap_le_adjoint (m : ℝ) :
    continuumDiracPMap m ≤ (continuumDiracPMap m)† := by
  exact (continuumDiracPMap_isFormalAdjoint m).le_adjoint
    (continuumDiracDomain_dense m)

/-- Coordinate formula for the adjoint of the diagonal Dirac multiplier. -/
theorem continuumDiracAdjoint_apply_coord (m : ℝ)
    (f : ((continuumDiracPMap m)†).domain) (n : Mode) :
    ((continuumDiracPMap m)† f) n =
      continuumHilbertModeOperator m n (f.1 n) := by
  apply ext_inner_right ℂ
  intro ψ
  rw [← lp.inner_single_right n ψ ((continuumDiracPMap m)† f)]
  have hfa := LinearPMap.adjoint_isFormalAdjoint
    (T := continuumDiracPMap m) (continuumDiracDomain_dense m)
  rw [hfa f
    ⟨lp.single 2 n ψ, single_mem_continuumDiracDomain m n ψ⟩]
  rw [continuumDiracPMap_single_apply, lp.inner_single_right]
  exact (continuumHilbertModeOperator_symmetric m n (f.1 n) ψ).symm

/-- Every vector in the adjoint domain already lies in the maximal Dirac domain. -/
theorem continuumDiracAdjoint_domain_le (m : ℝ) :
    ((continuumDiracPMap m)†).domain ≤ (continuumDiracPMap m).domain := by
  intro f hf
  let f' : ((continuumDiracPMap m)†).domain := ⟨f, hf⟩
  let g : CoeffL2 := (continuumDiracPMap m)† f'
  have heq : diracCoeff m f = fun n => g n := by
    funext n
    exact (continuumDiracAdjoint_apply_coord m f' n).symm
  change Memℓp (diracCoeff m f) 2
  rw [heq]
  exact g.prop

/-- The Hilbert adjoint is contained in the maximal diagonal Dirac multiplier. -/
theorem continuumDiracAdjoint_le (m : ℝ) :
    (continuumDiracPMap m)† ≤ continuumDiracPMap m := by
  refine ⟨continuumDiracAdjoint_domain_le m, ?_⟩
  intro f g hfg
  apply lp.ext
  funext n
  rw [continuumDiracAdjoint_apply_coord, continuumDiracPMap_apply]
  have hn : f.1 n = g.1 n := congrArg (fun x : CoeffL2 => x n) hfg
  rw [hn]

/-- The maximal Fourier-multiplier realization of the free Dirac Hamiltonian is self-adjoint. -/
theorem continuumDiracPMap_selfAdjoint (m : ℝ) :
    IsSelfAdjoint (continuumDiracPMap m) := by
  rw [LinearPMap.isSelfAdjoint_def]
  exact le_antisymm (continuumDiracAdjoint_le m)
    (continuumDiracPMap_le_adjoint m)

/-- The self-adjoint continuum Dirac multiplier is a closed unbounded operator. -/
theorem continuumDiracPMap_isClosed (m : ℝ) :
    (continuumDiracPMap m).IsClosed :=
  (continuumDiracPMap_selfAdjoint m).isClosed


/-- The Dirac multiplier commutes exactly with finite Fourier truncation. -/
theorem continuumDiracPMap_coeffTruncation (m : ℝ)
    (S : Finset Mode) (f : (continuumDiracPMap m).domain) :
    continuumDiracPMap m
      ⟨coeffTruncation S f.1,
        coeffTruncation_mem_continuumDiracDomain m S f.1⟩ =
      coeffTruncation S (continuumDiracPMap m f) := by
  classical
  apply lp.ext
  funext n
  by_cases hn : n ∈ S
  · simp [continuumDiracPMap_apply, coeffTruncation_apply, hn]
  · simp [continuumDiracPMap_apply, coeffTruncation_apply, hn]

/-- Every domain vector admits one finite Fourier truncation which approximates
both the vector and its Dirac image.  This is the graph-core approximation
property used by the finite Fourier subspace. -/
theorem exists_finite_graph_approx (m : ℝ)
    (f : (continuumDiracPMap m).domain) {ε : ℝ} (hε : 0 < ε) :
    ∃ S : Finset Mode,
      ‖f.1 - coeffTruncation S f.1‖ < ε ∧
      ‖continuumDiracPMap m f -
          continuumDiracPMap m
            ⟨coeffTruncation S f.1,
              coeffTruncation_mem_continuumDiracDomain m S f.1⟩‖ < ε := by
  have hf := hasSum_single_coeff f.1
  rw [HasSum, Metric.tendsto_nhds] at hf
  obtain ⟨Sf, hSf⟩ := eventually_atTop.1 (hf ε hε)
  let g : CoeffL2 := continuumDiracPMap m f
  have hg := hasSum_single_coeff g
  rw [HasSum, Metric.tendsto_nhds] at hg
  obtain ⟨Sg, hSg⟩ := eventually_atTop.1 (hg ε hε)
  let S : Finset Mode := Sf ∪ Sg
  refine ⟨S, ?_, ?_⟩
  · have h := hSf S (by
      intro n hn
      exact Finset.mem_union_left Sg hn)
    simpa [S, coeffTruncation, dist_eq_norm, norm_sub_rev] using h
  · have h := hSg S (by
      intro n hn
      exact Finset.mem_union_right Sf hn)
    have hout : ‖g - coeffTruncation S g‖ < ε := by
      simpa [S, coeffTruncation, dist_eq_norm, norm_sub_rev] using h
    rw [continuumDiracPMap_coeffTruncation]
    exact hout

end Relativistic3DUnboundedDirac
end KomorebiPhysics
