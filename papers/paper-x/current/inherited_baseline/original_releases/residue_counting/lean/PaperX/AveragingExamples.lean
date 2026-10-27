import PaperX.AveragingCompletion
import PaperX.ArithmeticCertificateExample

/-! A nontrivial integral comparison obtained by averaging for C2 over Z_3,
and its pullback to the actual absolute Galois group of Q. -/
set_option autoImplicit false
namespace PaperX.AveragingExamples
open scoped Matrix
open PaperX.CompletionExamples PaperX.RepresentationLimits
open PaperX.RepresentationTopology PaperX.RepresentationClasses
open PaperX.FiniteGroupAveraging PaperX.RepresentationForests

def integerRho : MatrixRep ℤ C2 (Fin 2) where
  toFun g := if g.toAdd = 0 then 1 else !![1, 1; 0, -1]
  map_one' := by decide +kernel
  map_mul' := by decide +kernel

def integerLift : Matrix (Fin 2) (Fin 2) ℤ := !![1, 1; 0, 1]

noncomputable def rho : MatrixRep ℤ_[3] C2 (Fin 2) :=
  changeCoefficients (Int.castRingHom ℤ_[3]) integerRho

noncomputable def tau : MatrixRep ℤ_[3] C2 (Fin 2) :=
  changeCoefficients (Int.castRingHom ℤ_[3]) signRep

noncomputable def initialLift : Matrix (Fin 2) (Fin 2) ℤ_[3] :=
  integerLift.map (Int.castRingHom ℤ_[3])

noncomputable abbrev residueMap : ℤ_[3] →+* ZMod 3 := PadicInt.toZMod

theorem residue_surjective : Function.Surjective residueMap :=
  ZMod.ringHom_surjective residueMap

instance residueLocal : IsLocalHom residueMap :=
  IsLocalHom.of_surjective residueMap residue_surjective

theorem group_order_unit : IsUnit (Fintype.card C2 : ℤ_[3]) := by
  apply isUnit_of_map_unit residueMap
  rw [map_natCast, show Fintype.card C2 = 2 from rfl]
  exact isUnit_iff_ne_zero.mpr (by decide +kernel)

/-- The original lift is not an integral intertwiner. -/
theorem initial_lift_not_intertwiner :
    rho generator * initialLift ≠ initialLift * tau generator := by
  intro h
  have h01 := congrArg (fun M : Matrix (Fin 2) (Fin 2) ℤ_[3] => M 0 1) h
  norm_num [rho, tau, initialLift, integerLift, integerRho, signRep, signValue,
    generator, changeCoefficients, Matrix.mul_apply, Fin.sum_univ_succ] at h01

/-- Nevertheless its reduction is an exact residual intertwiner. -/
theorem residual_intertwining (g : C2) :
    (rho g).map residueMap * initialLift.map residueMap =
      initialLift.map residueMap * (tau g).map residueMap := by
  have hi : ∀ g : C2,
      (integerRho g).map (Int.castRingHom (ZMod 3)) *
        integerLift.map (Int.castRingHom (ZMod 3)) =
      integerLift.map (Int.castRingHom (ZMod 3)) *
        (signRep g).map (Int.castRingHom (ZMod 3)) := by decide +kernel
  simpa [rho, tau, initialLift, changeCoefficients, Matrix.map_map,
    Function.comp_def] using hi g

theorem initial_lift_unit : IsUnit initialLift := by
  apply (Matrix.isUnit_iff_isUnit_det _).mpr
  have hd : initialLift.det = 1 := by
    norm_num [initialLift, integerLift, Matrix.det_fin_two]
  rw [hd]
  exact isUnit_one

/-- The displayed average is an actual integral operator. -/
noncomputable def averagedComparison : Matrix (Fin 2) (Fin 2) ℤ_[3] :=
  average rho tau group_order_unit initialLift

theorem averaged_intertwining (g : C2) :
    rho g * averagedComparison = averagedComparison * tau g :=
  average_intertwines rho tau group_order_unit initialLift g

theorem averaged_reduction : averagedComparison.map residueMap = initialLift.map residueMap :=
  map_average_of_intertwines residueMap rho tau group_order_unit initialLift residual_intertwining

theorem averaged_isUnit : IsUnit averagedComparison := by
  apply matrix_isUnit_of_map residueMap
  rw [averaged_reduction]
  exact initial_lift_unit.map residueMap.mapMatrix

theorem average_changes_the_lift : averagedComparison ≠ initialLift := by
  intro h
  exact initial_lift_not_intertwiner (h ▸ averaged_intertwining generator)

/-- The explicit finite sum is evaluated over the integers first. -/
theorem integer_averaging_sum :
    (∑ g : C2, integerRho g * integerLift * signRep g⁻¹) = !![2, -1; 0, 2] := by
  decide +kernel

/-- The constructed average is the integral matrix with upper-right entry
minus the inverse of two. This inverse exists inside Z_3. -/
theorem averaged_formula : averagedComparison =
    !![1, -(↑(group_order_unit.unit⁻¹) : ℤ_[3]); 0, 1] := by
  have hs : (∑ g : C2, rho g * initialLift * tau g⁻¹) =
      !![(2 : ℤ_[3]), -1; 0, 2] := by
    have hh := congrArg (fun M => (Int.castRingHom ℤ_[3]).mapMatrix M) integer_averaging_sum
    rw [map_sum] at hh
    simp only [map_mul, RingHom.mapMatrix_apply] at hh
    convert hh using 1 <;> ext i j <;> fin_cases i <;> fin_cases j <;>
      norm_num [rho, tau, initialLift, changeCoefficients]
  have hi : (↑(group_order_unit.unit⁻¹) : ℤ_[3]) * 2 = 1 := by
    calc
      _ = (↑(group_order_unit.unit⁻¹) : ℤ_[3]) * (↑group_order_unit.unit : ℤ_[3]) :=
        congrArg (fun x : ℤ_[3] => (↑(group_order_unit.unit⁻¹) : ℤ_[3]) * x)
          group_order_unit.unit_spec.symm
      _ = 1 := group_order_unit.unit.inv_mul
  unfold averagedComparison average
  rw [hs]
  ext i j
  fin_cases i <;> fin_cases j <;> simp_all

theorem averaged_det_one : averagedComparison.det = 1 := by
  rw [averaged_formula, Matrix.det_fin_two]
  simp

/-- This invokes the new existence theorem on the prescribed residual matrix.
It proves both integral invertibility and exact preservation of that matrix. -/
theorem actual_three_adic_isomorphism_lift :
    ∃ P : (Matrix (Fin 2) (Fin 2) ℤ_[3])ˣ,
      (P : Matrix (Fin 2) (Fin 2) ℤ_[3]).map residueMap = initialLift.map residueMap ∧
      ∀ g, rho g * (P : Matrix (Fin 2) (Fin 2) ℤ_[3]) =
        (P : Matrix (Fin 2) (Fin 2) ℤ_[3]) * tau g := by
  let B := (initial_lift_unit.map residueMap.mapMatrix).unit
  obtain ⟨P, hP, hi⟩ := exists_isomorphism_lift residueMap residue_surjective
    rho tau group_order_unit B (by simpa only [B, IsUnit.unit_spec, RingHom.mapMatrix_apply] using residual_intertwining)
  exact ⟨P, by simpa only [B, IsUnit.unit_spec, RingHom.mapMatrix_apply] using hP, hi⟩

noncomputable abbrev threeIdeal : Ideal ℤ_[3] := IsLocalRing.maximalIdeal ℤ_[3]

/-- A unit comparison gives the fixed detecting depth one. -/
theorem averaged_depth_one : Ideal.Quotient.mk (threeIdeal^1) averagedComparison.det ≠ 0 := by
  have hdet := (Matrix.isUnit_iff_isUnit_det _).mp averaged_isUnit
  rw [pow_one]
  exact (hdet.map (Ideal.Quotient.mk threeIdeal)).ne_zero

/-- Concrete finite conditions, populated by the displayed framed representation. -/
noncomputable def fixedConditions : Conditions (G := C2) (ι := Fin 2) threeIdeal where
  allowed k σ := σ = reduce threeIdeal rho k
  downward := by
    intro j k hjk σ hσ
    rw [hσ]
    exact transition_reduce threeIdeal rho hjk

theorem fixed_residual_type :
    AveragingCompletion.ResidualType threeIdeal fixedConditions tau := by
  intro σ hσ
  change σ = reduce threeIdeal rho 1 at hσ
  subst σ
  let P := averaged_isUnit.unit
  let f := Ideal.Quotient.mk (threeIdeal^1)
  refine ⟨Units.map f.mapMatrix.toMonoidHom P, ?_⟩
  intro g
  have hi := congrArg (fun M => f.mapMatrix M) (averaged_intertwining g)
  change (rho g).map f * (P : Matrix (Fin 2) (Fin 2) ℤ_[3]).map f =
    (P : Matrix (Fin 2) (Fin 2) ℤ_[3]).map f * (tau g).map f
  rw [show (P : Matrix (Fin 2) (Fin 2) ℤ_[3]) = averagedComparison from averaged_isUnit.unit_spec]
  exact hi

/-- The new completion theorem is genuinely invoked. In this explicit example
the displayed rho supplies occupancy; no new global occupancy claim is made. -/
theorem actual_three_adic_averaging_completion :
    ∃ (σ : MatrixRep ℤ_[3] C2 (Fin 2)) (P : (Matrix (Fin 2) (Fin 2) ℤ_[3])ˣ),
      Realizes threeIdeal fixedConditions σ ∧ AdicRepContinuous threeIdeal σ ∧
      (∀ g, σ g * (P : Matrix (Fin 2) (Fin 2) ℤ_[3]) =
        (P : Matrix (Fin 2) (Fin 2) ℤ_[3]) * tau g) ∧
      Ideal.Quotient.mk (threeIdeal^1) (P : Matrix (Fin 2) (Fin 2) ℤ_[3]).det ≠ 0 := by
  apply AveragingCompletion.continuous_finite_group_completion threeIdeal fixedConditions
    (IsLocalRing.maximalIdeal.isMaximal ℤ_[3]).ne_top tau group_order_unit fixed_residual_type
  · intro k
    exact Ideal.finite_quotient_pow (IsNoetherian.noetherian threeIdeal) k
  · intro k
    exact ⟨reduce threeIdeal rho k, rfl⟩

noncomputable def galoisRho : MatrixRep ℤ_[3] ArithmeticCertificateExample.GQ (Fin 2) :=
  rho.comp ArithmeticCertificateExample.quadraticCharacter

noncomputable def galoisTau : MatrixRep ℤ_[3] ArithmeticCertificateExample.GQ (Fin 2) :=
  tau.comp ArithmeticCertificateExample.quadraticCharacter

theorem galois_rho_continuous : AdicRepContinuous threeIdeal galoisRho := by
  let : TopologicalSpace ℤ_[3] := threeIdeal.adicTopology
  exact (continuous_of_discreteTopology (f := rho)).comp
    ArithmeticCertificateExample.quadraticCharacter_continuous

theorem galois_tau_continuous : AdicRepContinuous threeIdeal galoisTau := by
  let : TopologicalSpace ℤ_[3] := threeIdeal.adicTopology
  exact (continuous_of_discreteTopology (f := tau)).comp
    ArithmeticCertificateExample.quadraticCharacter_continuous

/-- Averaging on the finite quotient gives an actual integral isomorphism of
continuous representations of the absolute Galois group of Q. -/
theorem actual_galois_integral_isomorphism :
    ∃ P : (Matrix (Fin 2) (Fin 2) ℤ_[3])ˣ,
      (P : Matrix (Fin 2) (Fin 2) ℤ_[3]).map residueMap = initialLift.map residueMap ∧
      ∀ g, galoisRho g * (P : Matrix (Fin 2) (Fin 2) ℤ_[3]) =
        (P : Matrix (Fin 2) (Fin 2) ℤ_[3]) * galoisTau g := by
  obtain ⟨P, hp, hi⟩ := actual_three_adic_isomorphism_lift
  exact ⟨P, hp, fun g => hi (ArithmeticCertificateExample.quadraticCharacter g)⟩

/-- The arithmetic source does act nontrivially; this is not a trivial-group
specialization disguised by its name. -/
theorem actual_galois_generator_values :
    ∃ g : ArithmeticCertificateExample.GQ,
      galoisRho g = !![1, 1; 0, -1] ∧ galoisTau g = !![1, 0; 0, -1] := by
  obtain ⟨g, hg⟩ := ArithmeticCertificateExample.quadraticCharacter_hits_generator
  refine ⟨g, ?_, ?_⟩ <;> ext i j <;> fin_cases i <;> fin_cases j <;>
    norm_num [galoisRho, galoisTau, MonoidHom.comp_apply, hg, rho, tau,
      changeCoefficients, integerRho, signRep, signValue, generator, Matrix.map]

end PaperX.AveragingExamples
