import PaperX.CertificateBoundary
import PaperX.ComparisonCertificates
import PaperX.CertificateIsomorphisms

/-! A fixed nonunit comparison over the actual ring of 3-adic integers.
The representations become isomorphic over Q_3, although their integral
representations are not conjugate. -/
set_option autoImplicit false
namespace PaperX.CertificateExamples
open scoped Matrix
open PaperX.CompletionBoundary PaperX.CertificateBoundary
open PaperX.RepresentationLimits PaperX.RepresentationClasses
open PaperX.RepresentationForests PaperX.RepresentationTopology

noncomputable abbrev threeIdeal : Ideal ℤ_[3] := IsLocalRing.maximalIdeal ℤ_[3]

noncomputable def rho : MatrixRep ℤ_[3] (Multiplicative ℤ) (Fin 2) := unipotent 3
noncomputable def tau : MatrixRep ℤ_[3] (Multiplicative ℤ) (Fin 2) := unipotent 1
noncomputable def positiveComparison : Matrix (Fin 2) (Fin 2) ℤ_[3] := comparison 3

theorem positive_intertwining (g : Multiplicative ℤ) :
    rho g * positiveComparison = positiveComparison * tau g :=
  comparison_intertwines_representation 3 g

theorem positive_det : positiveComparison.det = 3 := comparison_det 3

/-- The comparison is detected at precision two: 3 is nonzero modulo 9. -/
theorem positive_det_mod_nine :
    PadicInt.toZModPow 2 positiveComparison.det ≠ 0 := by
  rw [positive_det]
  rw [map_ofNat]
  decide +kernel

theorem positive_det_detected :
    Ideal.Quotient.mk (threeIdeal^2) positiveComparison.det ≠ 0 := by
  intro hz
  have hm := Ideal.Quotient.eq_zero_iff_mem.mp hz
  rw [show threeIdeal = Ideal.span {(3 : ℤ_[3])} from
    PadicInt.maximalIdeal_eq_span_p, Ideal.span_singleton_pow] at hm
  apply positive_det_mod_nine
  change positiveComparison.det ∈ RingHom.ker (PadicInt.toZModPow 2)
  rw [PadicInt.ker_toZModPow]
  exact hm

/-- The determinant certificate does not require an integral unit matrix. -/
theorem positive_comparison_not_unit : ¬ IsUnit positiveComparison := by
  intro hu
  have hd := (Matrix.isUnit_iff_isUnit_det positiveComparison).mp hu
  rw [positive_det] at hd
  have hf := hd.map (PadicInt.toZMod : ℤ_[3] →+* ZMod 3)
  simp only [map_ofNat] at hf
  rw [show (3 : ZMod 3) = 0 by decide +kernel] at hf
  exact not_isUnit_zero hf

theorem positive_field_conjugacy :
    Conjugate (changeCoefficients (algebraMap ℤ_[3] ℚ_[3]) tau)
      (changeCoefficients (algebraMap ℤ_[3] ℚ_[3]) rho) := by
  simp only [rho, tau, changeCoefficients_unipotent, map_one, map_ofNat]
  exact field_conjugate 3 (by norm_num)

/-- No alternative integral invertible comparison exists either. -/
theorem positive_not_integrally_conjugate : ¬ Conjugate tau rho := by
  rintro ⟨u, hu⟩
  have hi : ∀ g, unipotent (3 : ℤ_[3]) g * (u : Matrix (Fin 2) (Fin 2) ℤ_[3]) =
      (u : Matrix (Fin 2) (Fin 2) ℤ_[3]) * unipotent 1 g := by
    intro g
    have H := congrArg (fun σ : MatrixRep ℤ_[3] (Multiplicative ℤ) (Fin 2) => σ g) hu
    change (u : Matrix (Fin 2) (Fin 2) ℤ_[3]) * unipotent 1 g *
      (↑(u⁻¹) : Matrix (Fin 2) (Fin 2) ℤ_[3]) = unipotent 3 g at H
    rw [← H, mul_assoc]
    simp
  have hd := representation_intertwiner_det 3 (u : Matrix (Fin 2) (Fin 2) ℤ_[3]) hi
  have hf := (Matrix.isUnits_det_units u).map (PadicInt.toZMod : ℤ_[3] →+* ZMod 3)
  rw [hd] at hf
  simp only [map_mul, map_pow, map_ofNat] at hf
  rw [show (3 : ZMod 3) = 0 by decide +kernel, zero_mul] at hf
  exact not_isUnit_zero hf

/-- There is no fixed determinant-detection depth for all the degenerating
3-adic representations, even when any integral comparison may be chosen. -/
theorem actual_three_adic_no_uniform_depth :
    ¬ ∃ b : ℕ, ∀ n : ℕ, ∃ P : Matrix (Fin 2) (Fin 2) ℤ_[3],
      (∀ g, unipotent (3^n) g * P = P * unipotent 1 g) ∧
      Ideal.Quotient.mk (threeIdeal^(b+1)) P.det ≠ 0 := by
  apply no_uniform_detecting_depth threeIdeal 3
  change (3 : ℤ_[3]) ∈ IsLocalRing.maximalIdeal ℤ_[3]
  rw [PadicInt.maximalIdeal_eq_span_p]
  exact Ideal.subset_span (by simp)

theorem actual_three_adic_every_power_field_conjugate (n : ℕ) :
    Conjugate (unipotent (1 : ℚ_[3])) (unipotent ((3 : ℚ_[3])^n)) :=
  every_nonzero_power_field_conjugate 3 (by norm_num) n

/-- The same integral representation family converges pointwise to the trivial
representation in the maximal-ideal-adic topology. -/
theorem actual_three_adic_degenerates (g : Multiplicative ℤ) :
    letI : TopologicalSpace ℤ_[3] := threeIdeal.adicTopology
    Filter.Tendsto (fun n : ℕ => unipotent ((3 : ℤ_[3])^n) g) Filter.atTop
      (nhds (1 : Matrix (Fin 2) (Fin 2) ℤ_[3])) := by
  apply unipotent_tendsto threeIdeal 3 _ g
  change (3 : ℤ_[3]) ∈ IsLocalRing.maximalIdeal ℤ_[3]
  rw [PadicInt.maximalIdeal_eq_span_p]
  exact Ideal.subset_span (by simp)

/-- A concrete finite condition set for the completion theorem. The infinite
source group does not make this allowed singleton infinite. -/
noncomputable def fixedRhoConditions :
    Conditions (G := Multiplicative ℤ) (ι := Fin 2) threeIdeal where
  allowed k σ := σ = reduce threeIdeal rho k
  downward := by
    intro j k hjk σ hσ
    rw [hσ]
    exact transition_reduce threeIdeal rho hjk

theorem fixedRhoConditions_finite (k : ℕ) :
    Finite {σ : MatrixRep (ℤ_[3] ⧸ threeIdeal^k) (Multiplicative ℤ) (Fin 2) //
      fixedRhoConditions.allowed k σ} := by
  let : Subsingleton {σ : MatrixRep (ℤ_[3] ⧸ threeIdeal^k) (Multiplicative ℤ) (Fin 2) //
      fixedRhoConditions.allowed k σ} :=
    ⟨fun x y => Subtype.ext (x.property.trans y.property.symm)⟩
  infer_instance

/-- Every augmented level is populated by reducing the actual nonunit comparison. -/
theorem positive_certificate_levels (k : ℕ) :
    Nonempty (PaperX.ComparisonCertificates.Node threeIdeal fixedRhoConditions
      (fun _ : Unit => MonoidHom.id (Multiplicative ℤ)) (fun _ => tau) (fun _ => 2) k) := by
  exact ⟨PaperX.ComparisonCertificates.node_of_integral threeIdeal fixedRhoConditions
    (fun _ : Unit => MonoidHom.id (Multiplicative ℤ)) (fun _ => tau) (fun _ => 2)
    rho (fun _ => positiveComparison) (fun _ => rfl)
    (fun _ g => positive_intertwining g) (fun _ => positive_det_detected) k⟩

/-- This actually invokes simultaneous certificate completion over Z_3 and then
turns the reconstructed comparison into a field isomorphism. Occupancy in this
model is supplied by the explicit representation and nonunit comparison above. -/
theorem actual_three_adic_certificate_completion :
    ∃ (σ : MatrixRep ℤ_[3] (Multiplicative ℤ) (Fin 2))
      (P : Matrix (Fin 2) (Fin 2) ℤ_[3]),
      Realizes threeIdeal fixedRhoConditions σ ∧ AdicRepContinuous threeIdeal σ ∧
      (∀ g, σ g * P = P * tau g) ∧
      Ideal.Quotient.mk (threeIdeal^2) P.det ≠ 0 ∧
      Conjugate (changeCoefficients (algebraMap ℤ_[3] ℚ_[3]) tau)
        (changeCoefficients (algebraMap ℤ_[3] ℚ_[3]) σ) := by
  obtain ⟨σ, P, hσ, hc, hP, hd⟩ :=
    PaperX.ComparisonCertificates.exists_continuous_comparison_realization
      threeIdeal fixedRhoConditions
      (fun _ : Unit => MonoidHom.id (Multiplicative ℤ)) (fun _ => tau) (fun _ => 2)
      (fun k => Ideal.finite_quotient_pow (IsNoetherian.noetherian threeIdeal) k)
      fixedRhoConditions_finite positive_certificate_levels
      (fun _ _ _ _ _ _ => by simp [nhds_discrete])
  refine ⟨σ, P (), hσ, hc, hP (), hd (), ?_⟩
  apply PaperX.CertificateIsomorphisms.conjugate_of_finite_certificate threeIdeal
    (algebraMap ℤ_[3] ℚ_[3]) (IsFractionRing.injective ℤ_[3] ℚ_[3]) σ tau (P ()) 2
  · change ((Ideal.Quotient.mk (threeIdeal^2)).mapMatrix (P ())).det ≠ 0
    rw [← RingHom.map_det]
    exact hd ()
  · exact hP ()

/-- All reductions fix the actual integral representation by separatedness. -/
theorem fixed_realizer_eq_rho (σ : MatrixRep ℤ_[3] (Multiplicative ℤ) (Fin 2))
    (hσ : Realizes threeIdeal fixedRhoConditions σ) : σ = rho := by
  apply MonoidHom.ext
  intro g
  apply Matrix.ext
  intro i j
  apply scalar_ext threeIdeal
  intro k
  exact congrArg (fun ρ => ρ g i j) (hσ k)

/-- Applying the completion theorem really produces a comparison which is
noninvertible integrally, yet is an isomorphism after passage to Q_3. -/
theorem completed_comparison_is_nonunit :
    ∃ P : Matrix (Fin 2) (Fin 2) ℤ_[3],
      (∀ g, rho g * P = P * tau g) ∧
      Ideal.Quotient.mk (threeIdeal^2) P.det ≠ 0 ∧ ¬ IsUnit P ∧
      IsUnit (P.map (algebraMap ℤ_[3] ℚ_[3])) := by
  obtain ⟨σ, P, hσ, _, hi, hd, _⟩ := actual_three_adic_certificate_completion
  have he := fixed_realizer_eq_rho σ hσ
  subst σ
  refine ⟨P, hi, hd, ?_, ?_⟩
  · intro hu
    have hf := ((Matrix.isUnit_iff_isUnit_det P).mp hu).map
      (PadicInt.toZMod : ℤ_[3] →+* ZMod 3)
    rw [representation_intertwiner_det 3 P hi] at hf
    simp only [map_mul, map_pow, map_ofNat] at hf
    rw [show (3 : ZMod 3) = 0 by decide +kernel, zero_mul] at hf
    exact not_isUnit_zero hf
  · apply PaperX.CertificateIsomorphisms.mapped_matrix_isUnit
      (algebraMap ℤ_[3] ℚ_[3]) (IsFractionRing.injective ℤ_[3] ℚ_[3]) P
    intro hzero
    apply hd
    rw [hzero, map_zero]

end PaperX.CertificateExamples
