import KomorebiVerification.PaperII.ReleaseCoordinatesResidue

/-!
The literal operator F(X) ↦ F(ωX), its iterates, and its finite weighted
average on actual formal power series. These connect the independently
proved coefficient-kernel certificate to the printed operator equality.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.Residue
universe u
variable {R : Type u}

/-- The actual formal substitution F(X) ↦ F(ωX), as an R-linear map. -/
def seriesPhase [CommSemiring R] (omega : R) : Module.End R (PowerSeries R) where
  toFun := PowerSeries.rescale omega
  map_add' := (PowerSeries.rescale omega).map_add
  map_smul' c f := by
    ext n
    simp only [PowerSeries.coeff_rescale, PowerSeries.coeff_smul, smul_eq_mul,
      RingHom.id_apply]
    ring

@[simp] theorem seriesPhase_coeff [CommSemiring R]
    (omega : R) (f : PowerSeries R) (n : Nat) :
    PowerSeries.coeff n (seriesPhase omega f) = omega ^ n * PowerSeries.coeff n f :=
  PowerSeries.coeff_rescale f omega n

/-- The kth power is the kth iterate of the actual phase operator. -/
theorem seriesPhase_pow_coeff [CommSemiring R]
    (omega : R) (k : Nat) (f : PowerSeries R) (n : Nat) :
    PowerSeries.coeff n ((seriesPhase omega ^ k) f) =
      omega ^ (n * k) * PowerSeries.coeff n f := by
  induction k with
  | zero => simp
  | succ k ih =>
      rw [pow_succ', Module.End.mul_apply, seriesPhase_coeff, ih]
      rw [Nat.mul_succ, pow_add]
      ring

/-- The Nth operator power is the identity when the phase has order dividing N. -/
theorem seriesPhase_pow_order [CommSemiring R]
    (N : Nat) (omega : R) (h : omega ^ N = 1) :
    seriesPhase omega ^ N = 1 := by
  ext f n
  rw [seriesPhase_pow_coeff, Nat.mul_comm n N, pow_mul, h]
  simp

/-- The finite operator sum appearing in the general-ring theorem. -/
def seriesFourierAverage [CommSemiring R]
    (N : Nat) (omega omegaDual eta : R) (j : Fin N) : Module.End R (PowerSeries R) :=
  eta • ∑ k : Fin N, (omegaDual ^ (j.val * k.val)) • (seriesPhase omega ^ k.val)

/-- Direct evaluation of the finite operator sum gives the independently defined kernel. -/
theorem seriesFourierAverage_coeff [CommSemiring R]
    (N : Nat) (omega omegaDual eta : R) (j : Fin N) (f : PowerSeries R) (n : Nat) :
    PowerSeries.coeff n (seriesFourierAverage N omega omegaDual eta j f) =
      (eta * ringFourierKernel N omega omegaDual j n) * PowerSeries.coeff n f := by
  simp only [seriesFourierAverage, LinearMap.smul_apply, LinearMap.sum_apply,
    map_smul, map_sum, seriesPhase_pow_coeff, smul_eq_mul,
    ringFourierKernel]
  rw [mul_assoc, Finset.sum_mul]
  congr 1
  apply Finset.sum_congr rfl
  intro k _
  rw [mul_assoc]

/-- A finite certificate proves the literal formal-series operator equality. -/
theorem seriesFourierAverage_eq_residueProj [CommSemiring R]
    (N : Nat) (hN : 0 < N) (omega omegaDual eta : R)
    (h : FiniteRingFourierOrthogonalityCertificate R N omega omegaDual eta) (j : Fin N) :
    seriesFourierAverage N omega omegaDual eta j = seriesResidueProj N hN j := by
  ext f n
  rw [seriesFourierAverage_coeff,
    (h.toRingCertificate N hN omega omegaDual eta).weighted_sum_eq,
    seriesResidueProj_coeff]
  have heq : residueAddress N hN n = j ↔ n % N = j.val := Fin.ext_iff
  by_cases hn : n % N = j.val
  · simp [hn, heq.mpr hn]
  · have hn' : residueAddress N hN n ≠ j := fun h => hn (heq.mp h)
    simp [hn, hn']

/-- Under root periodicity, the field ratio kernel and inverse-power kernel agree. -/
theorem ringFourierKernel_inv_eq_fourierKernel [Field R]
    (N : Nat) (omega : R) (homega : omega ^ N = 1) (j : Fin N) (n : Nat) :
    ringFourierKernel N omega omega⁻¹ j n = fourierKernel N omega j n := by
  unfold ringFourierKernel fourierKernel
  apply Finset.sum_congr rfl
  intro k _
  simp only [pow_mul, inv_pow, div_eq_mul_inv, mul_pow]
  rw [pow_eq_pow_mod n homega]
  ring

/-- A primitive root over a field supplies the manuscript finite ring certificate itself. -/
theorem primitiveRoot_finiteRingFourierCertificate [Field R]
    (N : Nat) (hN : 0 < N) (omega : R) (homega : IsPrimitiveRoot omega N) :
    FiniteRingFourierOrthogonalityCertificate R N omega omega⁻¹ (N : R)⁻¹ := by
  refine ⟨homega.pow_eq_one, ?_⟩
  intro j r
  have hc := primitiveRoot_fourierOrthogonalityCertificate N hN omega homega
  have hker : ringFourierResidueKernel N omega omega⁻¹ j r =
      fourierKernel N omega j r.val :=
    ringFourierKernel_inv_eq_fourierKernel N omega homega.pow_eq_one j r.val
  rw [hker, hc.sum_eq, Nat.mod_eq_of_lt r.isLt]
  by_cases hr : r = j
  · subst r
    simp [hc.order_ne_zero]
  · have hv : r.val ≠ j.val := fun h => hr (Fin.ext h)
    simp [hr, hv]

/-- Character realization as a finite sum of powers of actual series substitution. -/
theorem seriesFourierAverage_eq_residueProj_of_primitiveRoot [Field R]
    (N : Nat) (hN : 0 < N) (omega : R) (homega : IsPrimitiveRoot omega N) (j : Fin N) :
    (N : R)⁻¹ • (∑ k : Fin N, (omega⁻¹ ^ (j.val * k.val)) •
      (seriesPhase omega ^ k.val)) = seriesResidueProj N hN j :=
  seriesFourierAverage_eq_residueProj N hN omega omega⁻¹ (N : R)⁻¹
    (primitiveRoot_finiteRingFourierCertificate N hN omega homega) j

end Komorebi.Residue
#print axioms Komorebi.Residue.seriesFourierAverage_eq_residueProj
#print axioms Komorebi.Residue.primitiveRoot_finiteRingFourierCertificate
#print axioms Komorebi.Residue.seriesFourierAverage_eq_residueProj_of_primitiveRoot
