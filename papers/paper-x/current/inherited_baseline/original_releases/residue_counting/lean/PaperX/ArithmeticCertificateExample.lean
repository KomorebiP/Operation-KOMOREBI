import PaperX.CompletionExamples
import Mathlib.FieldTheory.AbsoluteGaloisGroup
import Mathlib.FieldTheory.Galois.Infinite
import PaperX.CertificateIsomorphisms

/-! A concrete quadratic character of the actual absolute Galois group of Q,
defined by its action on a square root of minus one in the algebraic closure. -/
set_option autoImplicit false
namespace PaperX.ArithmeticCertificateExample
open PaperX.CompletionExamples PaperX.RepresentationLimits
open PaperX.RepresentationTopology PaperX.RepresentationClasses
open scoped Matrix
open scoped Topology

abbrev Qbar := AlgebraicClosure ℚ
/-- This is definitionally `Field.absoluteGaloisGroup ℚ`, with its Krull topology. -/
abbrev GQ := Qbar ≃ₐ[ℚ] Qbar

noncomputable def imaginary : Qbar :=
  Classical.choose (IsAlgClosed.exists_pow_nat_eq (-1 : Qbar) (by decide : 0 < 2))

theorem imaginary_sq : imaginary ^ 2 = -1 :=
  Classical.choose_spec (IsAlgClosed.exists_pow_nat_eq (-1 : Qbar) (by decide : 0 < 2))

theorem imaginary_ne_zero : imaginary ≠ 0 := by
  intro h
  have := imaginary_sq
  rw [h] at this
  norm_num at this

theorem imaginary_ne_neg : imaginary ≠ -imaginary := by
  intro h
  have : (2 : Qbar) * imaginary = 0 := by linear_combination h
  exact imaginary_ne_zero ((mul_eq_zero.mp this).resolve_left (by norm_num))

theorem imaginary_not_rational : imaginary ∉ Set.range (algebraMap ℚ Qbar) := by
  rintro ⟨q, hq⟩
  have h : (algebraMap ℚ Qbar) (q ^ 2) = (algebraMap ℚ Qbar) (-1) := by
    simpa [map_pow, hq] using imaginary_sq
  have hq2 : q ^ 2 = -1 := (algebraMap ℚ Qbar).injective h
  nlinarith [sq_nonneg q]

theorem action_imaginary (σ : GQ) : σ imaginary = imaginary ∨ σ imaginary = -imaginary := by
  have hs : (σ imaginary) ^ 2 = imaginary ^ 2 := by
    rw [← map_pow, imaginary_sq, map_neg, map_one]
  exact sq_eq_sq_iff_eq_or_eq_neg.mp hs

noncomputable def quadraticValue (σ : GQ) : C2 := by
  classical
  exact if σ imaginary = imaginary then 1 else generator

theorem quadraticValue_mul (σ τ : GQ) :
    quadraticValue (σ * τ) = quadraticValue σ * quadraticValue τ := by
  have hgen : generator * generator = 1 := by decide +kernel
  by_cases hs : σ imaginary = imaginary
  · by_cases ht : τ imaginary = imaginary
    · have hst : (σ * τ) imaginary = imaginary := by
        change σ (τ imaginary) = imaginary
        rw [ht, hs]
      simp only [quadraticValue, ite_eq_left hst, ite_eq_left hs, ite_eq_left ht, mul_one]
    · have ht' : τ imaginary = -imaginary := (action_imaginary τ).resolve_left ht
      have hst : (σ * τ) imaginary ≠ imaginary := by
        change σ (τ imaginary) ≠ imaginary
        rw [ht', map_neg, hs]
        exact imaginary_ne_neg.symm
      simp only [quadraticValue, ite_eq_right hst, ite_eq_left hs, ite_eq_right ht, one_mul]
  · have hs' : σ imaginary = -imaginary := (action_imaginary σ).resolve_left hs
    by_cases ht : τ imaginary = imaginary
    · have hst : (σ * τ) imaginary ≠ imaginary := by
        change σ (τ imaginary) ≠ imaginary
        rw [ht]
        exact hs
      simp only [quadraticValue, ite_eq_right hst, ite_eq_right hs, ite_eq_left ht, mul_one]
    · have ht' : τ imaginary = -imaginary := (action_imaginary τ).resolve_left ht
      have hst : (σ * τ) imaginary = imaginary := by
        change σ (τ imaginary) = imaginary
        rw [ht', map_neg, hs', neg_neg]
      simp only [quadraticValue, ite_eq_left hst, ite_eq_right hs, ite_eq_right ht, hgen]

noncomputable def quadraticCharacter : GQ →* C2 where
  toFun := quadraticValue
  map_one' := by simp [quadraticValue]
  map_mul' := quadraticValue_mul

theorem quadraticCharacter_hits_generator : ∃ σ : GQ, quadraticCharacter σ = generator := by
  have h : ¬ ∀ σ : GQ, σ imaginary = imaginary := by
    intro h
    exact imaginary_not_rational
      ((InfiniteGalois.mem_range_algebraMap_iff_fixed imaginary).mpr h)
  obtain ⟨σ, hσ⟩ := Classical.not_forall.mp h
  exact ⟨σ, by simp [quadraticCharacter, quadraticValue, hσ]⟩

theorem quadraticCharacter_continuous : Continuous quadraticCharacter := by
  apply continuous_of_continuousAt_one quadraticCharacter
  rw [ContinuousAt, nhds_discrete C2, Filter.tendsto_pure]
  have hopen : IsOpen {σ : GQ | σ imaginary = imaginary} := by
    exact stabilizer_isOpen_of_isIntegral imaginary
  filter_upwards [hopen.mem_nhds (show (1 : GQ) imaginary = imaginary from rfl)] with σ hσ
  simp [quadraticCharacter, quadraticValue, hσ]

/-- The character also has the explicitly named absolute Galois group as domain. -/
noncomputable def absoluteQuadraticCharacter : Field.absoluteGaloisGroup ℚ →* C2 :=
  quadraticCharacter

theorem absoluteQuadraticCharacter_continuous : Continuous absoluteQuadraticCharacter :=
  quadraticCharacter_continuous

/-- An integral lattice representation with the same rational constituents as
the diagonal sign representation, but a different reduction modulo two. -/
def nonsplitRep : MatrixRep ℤ C2 (Fin 2) where
  toFun g := if g.toAdd = 0 then 1 else !![1, -1; 0, -1]
  map_one' := by decide +kernel
  map_mul' := by decide +kernel

def integralComparison : Matrix (Fin 2) (Fin 2) ℤ := !![1, 1; 0, 2]

theorem integral_comparison_det : integralComparison.det = 2 := by decide +kernel

theorem integral_intertwining : ∀ g : C2,
    nonsplitRep g * integralComparison = integralComparison * signRep g := by
  decide +kernel

instance twoPrime : Fact (Nat.Prime 2) := ⟨by decide⟩

noncomputable abbrev twoIdeal : Ideal ℤ_[2] := IsLocalRing.maximalIdeal ℤ_[2]

noncomputable def tau : MatrixRep ℤ_[2] GQ (Fin 2) :=
  (changeCoefficients (Int.castRingHom ℤ_[2]) signRep).comp quadraticCharacter

noncomputable def rho : MatrixRep ℤ_[2] GQ (Fin 2) :=
  (changeCoefficients (Int.castRingHom ℤ_[2]) nonsplitRep).comp quadraticCharacter

noncomputable def comparison : Matrix (Fin 2) (Fin 2) ℤ_[2] :=
  integralComparison.map (Int.castRingHom ℤ_[2])

theorem comparison_det : comparison.det = 2 := by
  change ((Int.castRingHom ℤ_[2]).mapMatrix integralComparison).det = 2
  rw [← RingHom.map_det, integral_comparison_det, map_ofNat]

theorem comparison_intertwining (g : GQ) : rho g * comparison = comparison * tau g := by
  have h := congrArg (fun M => M.map (Int.castRingHom ℤ_[2]))
    (integral_intertwining (quadraticCharacter g))
  rw [Matrix.map_mul, Matrix.map_mul] at h
  simpa [rho, tau, comparison, changeCoefficients] using h

theorem tau_continuous : AdicRepContinuous twoIdeal tau := by
  let : TopologicalSpace ℤ_[2] := twoIdeal.adicTopology
  exact (continuous_of_discreteTopology (f :=
    (changeCoefficients (Int.castRingHom ℤ_[2]) signRep))).comp
    quadraticCharacter_continuous

theorem rho_continuous : AdicRepContinuous twoIdeal rho := by
  let : TopologicalSpace ℤ_[2] := twoIdeal.adicTopology
  exact (continuous_of_discreteTopology (f :=
    (changeCoefficients (Int.castRingHom ℤ_[2]) nonsplitRep))).comp
    quadraticCharacter_continuous

/-- The determinant is not zero modulo four even though it is not an integral unit. -/
theorem comparison_det_mod_four : PadicInt.toZModPow 2 comparison.det ≠ 0 := by
  rw [comparison_det, map_ofNat]
  decide +kernel

theorem comparison_det_detected : Ideal.Quotient.mk (twoIdeal ^ 2) comparison.det ≠ 0 := by
  intro hz
  have hm := Ideal.Quotient.eq_zero_iff_mem.mp hz
  rw [show twoIdeal = Ideal.span {(2 : ℤ_[2])} from
    PadicInt.maximalIdeal_eq_span_p, Ideal.span_singleton_pow] at hm
  apply comparison_det_mod_four
  change comparison.det ∈ RingHom.ker (PadicInt.toZModPow 2)
  rw [PadicInt.ker_toZModPow]
  exact hm

theorem comparison_not_unit : ¬ IsUnit comparison := by
  intro hu
  have hd := (Matrix.isUnit_iff_isUnit_det comparison).mp hu
  rw [comparison_det] at hd
  have hf := hd.map (PadicInt.toZMod : ℤ_[2] →+* ZMod 2)
  simp only [map_ofNat] at hf
  rw [show (2 : ZMod 2) = 0 by decide +kernel] at hf
  exact not_isUnit_zero hf

/-- A genuine isomorphism over Q_2 follows from the fixed finite determinant
certificate, for representations of the actual absolute Galois group. -/
theorem field_conjugacy :
    Conjugate (changeCoefficients (algebraMap ℤ_[2] ℚ_[2]) tau)
      (changeCoefficients (algebraMap ℤ_[2] ℚ_[2]) rho) := by
  apply PaperX.CertificateIsomorphisms.conjugate_of_finite_certificate twoIdeal
    (algebraMap ℤ_[2] ℚ_[2]) (fun _ _ h => Subtype.ext h) rho tau comparison 2
  · change ((Ideal.Quotient.mk (twoIdeal ^ 2)).mapMatrix comparison).det ≠ 0
    rw [← RingHom.map_det]
    exact comparison_det_detected
  · exact comparison_intertwining

theorem tau_residue (g : GQ) :
    changeCoefficients (PadicInt.toZMod : ℤ_[2] →+* ZMod 2) tau g = 1 := by
  have h : ∀ c : C2, (signRep c).map (Int.castRingHom (ZMod 2)) = 1 := by
    decide +kernel
  ext i j
  have H := congrArg (fun M => M i j) (h (quadraticCharacter g))
  simpa [tau, changeCoefficients] using H

theorem rho_residue_generator (g : GQ) (hg : quadraticCharacter g = generator) :
    changeCoefficients (PadicInt.toZMod : ℤ_[2] →+* ZMod 2) rho g 0 1 = 1 := by
  norm_num [rho, changeCoefficients, hg, nonsplitRep, generator]

/-- No integral change of basis works: a genuine Galois element has trivial
tau reduction but a nonidentity rho reduction modulo two. -/
theorem not_integrally_conjugate : ¬ Conjugate tau rho := by
  intro hc
  obtain ⟨g, hg⟩ := quadraticCharacter_hits_generator
  obtain ⟨u, hu⟩ := changeCoefficients_conjugacy
    (PadicInt.toZMod : ℤ_[2] →+* ZMod 2) hc
  have H := congrArg (fun σ : MatrixRep (ZMod 2) GQ (Fin 2) => σ g) hu
  rw [conjugate_apply, tau_residue] at H
  have H01 := congrArg (fun M : Matrix (Fin 2) (Fin 2) (ZMod 2) => M 0 1) H
  simp at H01
  have H1 := rho_residue_generator g hg
  exact zero_ne_one (H01.trans H1)

end PaperX.ArithmeticCertificateExample
