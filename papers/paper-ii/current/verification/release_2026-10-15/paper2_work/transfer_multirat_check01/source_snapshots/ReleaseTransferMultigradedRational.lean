import ReleaseTransferMultigraded

/-! Determinant-adjugate identity for the independently defined multigraded
semantic walk series, including arbitrary scalar edge and endpoint weights. -/
set_option autoImplicit false
open scoped BigOperators

namespace Komorebi.PaperII.ReleaseTransferMultigraded
universe u v w z
variable {V : Type u} {E : Type v} {σ : Type w} {R : Type z}
variable [Fintype E] [Fintype V] [DecidableEq V] [DecidableEq σ] [CommRing R]
variable (G : Graph V E σ) (m : E → R)

noncomputable def series (s t : V) : MvPowerSeries σ R := coefficient G m s t

@[simp] theorem coeff_series (s t : V) (n : σ →₀ ℕ) :
    MvPowerSeries.coeff n (series G m s t) = coefficient G m s t n := rfl

noncomputable def adjacency : Matrix V V (MvPolynomial σ R) :=
  fun i j ↦ ∑ e : E, if G.source e = i ∧ G.target e = j then
    MvPolynomial.monomial (G.weight e) (m e) else 0

theorem adjacency_constantCoeff_zero (i j : V) :
    MvPolynomial.constantCoeff (adjacency G m i j) = 0 := by
  classical
  rw [adjacency, map_sum]
  apply Finset.sum_eq_zero
  intro e _
  by_cases h : G.source e = i ∧ G.target e = j <;>
    simp [h, MvPolynomial.constantCoeff_monomial, G.weight_ne_zero e]

noncomputable def adjacencySeries : Matrix V V (MvPowerSeries σ R) :=
  MvPolynomial.coeToMvPowerSeries.ringHom.mapMatrix (adjacency G m)

noncomputable def seriesMatrix : Matrix V V (MvPowerSeries σ R) := fun s t ↦ series G m s t

theorem adjacencySeries_mul_seriesMatrix_apply (s t : V) :
    (adjacencySeries G m * seriesMatrix G m) s t =
      ∑ e : E, if G.source e = s then
        MvPowerSeries.monomial (G.weight e) (m e) * series G m (G.target e) t else 0 := by
  classical
  have hadj (i j : V) : adjacencySeries G m i j =
      ∑ e : E, if G.source e = i ∧ G.target e = j then
        MvPowerSeries.monomial (G.weight e) (m e) else 0 := by
    rw [adjacencySeries, RingHom.mapMatrix_apply, Matrix.map_apply, adjacency, map_sum]
    apply Finset.sum_congr rfl
    intro e _
    by_cases h : G.source e = i ∧ G.target e = j <;> simp [h]
  rw [Matrix.mul_apply]
  simp_rw [hadj, Finset.sum_mul]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro e _
  by_cases hs : G.source e = s
  · simp [hs, seriesMatrix]
  · simp [hs]

theorem coeff_adjacency_mul_series (s t : V) (n : σ →₀ ℕ) :
    MvPowerSeries.coeff n ((adjacencySeries G m * seriesMatrix G m) s t) =
      ∑ e : E, if G.source e = s ∧ G.weight e ≤ n then
        m e * coefficient G m (G.target e) t (n - G.weight e) else 0 := by
  classical
  rw [adjacencySeries_mul_seriesMatrix_apply, map_sum]
  apply Finset.sum_congr rfl
  intro e _
  by_cases hs : G.source e = s
  · simp [hs, MvPowerSeries.coeff_monomial_mul]
  · simp [hs]

theorem seriesMatrix_eq_one_add_adjacency_mul :
    seriesMatrix G m = 1 + adjacencySeries G m * seriesMatrix G m := by
  ext s t n
  change MvPowerSeries.coeff n (series G m s t) =
    MvPowerSeries.coeff n ((1 : Matrix V V (MvPowerSeries σ R)) s t +
      (adjacencySeries G m * seriesMatrix G m) s t)
  rw [coeff_series, map_add, coeff_adjacency_mul_series]
  have hrec := coefficient_firstEdge G m s t n
  by_cases hst : s = t
  · subst t
    by_cases hn : n = 0 <;> simpa [Matrix.one_apply, MvPowerSeries.coeff_one, hn] using hrec
  · simpa [Matrix.one_apply, MvPowerSeries.coeff_one, hst] using hrec

noncomputable def transfer : Matrix V V (MvPolynomial σ R) := 1 - adjacency G m
noncomputable def denominator : MvPolynomial σ R := Matrix.det (transfer G m)
noncomputable def denominatorInverse : MvPowerSeries σ R :=
  MvPowerSeries.invOfUnit (denominator G m : MvPowerSeries σ R) (1 : Rˣ)

theorem denominator_constantCoeff : MvPolynomial.constantCoeff (denominator G m) = 1 := by
  rw [denominator, RingHom.map_det]
  have h : MvPolynomial.constantCoeff.mapMatrix (transfer G m) = (1 : Matrix V V R) := by
    ext i j
    by_cases hij : i = j <;>
      simp [transfer, RingHom.mapMatrix_apply, Matrix.map_apply,
        adjacency_constantCoeff_zero, Matrix.one_apply, hij]
  rw [h, Matrix.det_one]

theorem denominator_series_constantCoeff :
    MvPowerSeries.constantCoeff (denominator G m : MvPowerSeries σ R) = 1 := by
  rw [← MvPowerSeries.coeff_zero_eq_constantCoeff_apply, MvPolynomial.coeff_coe,
    ← MvPolynomial.constantCoeff_eq, denominator_constantCoeff]

theorem denominator_mul_inverse :
    (denominator G m : MvPowerSeries σ R) * denominatorInverse G m = 1 := by
  exact MvPowerSeries.mul_invOfUnit _ _ (denominator_series_constantCoeff G m)

theorem denominator_inverse_mul :
    denominatorInverse G m * (denominator G m : MvPowerSeries σ R) = 1 := by
  exact MvPowerSeries.invOfUnit_mul _ _ (denominator_series_constantCoeff G m)

theorem transfer_mul_seriesMatrix :
    MvPolynomial.coeToMvPowerSeries.ringHom.mapMatrix (transfer G m) * seriesMatrix G m = 1 := by
  have ht : MvPolynomial.coeToMvPowerSeries.ringHom.mapMatrix (transfer G m) =
      1 - adjacencySeries G m := by
    rw [transfer, adjacencySeries, map_sub, map_one]
  rw [ht, sub_mul, one_mul]
  exact sub_eq_iff_eq_add.mpr (seriesMatrix_eq_one_add_adjacency_mul G m)

theorem seriesMatrix_eq_rationalMatrix : seriesMatrix G m =
    ReleaseTransferMatrix.rationalMatrix MvPolynomial.coeToMvPowerSeries.ringHom
      (transfer G m) (denominatorInverse G m) := by
  let Z := ReleaseTransferMatrix.rationalMatrix MvPolynomial.coeToMvPowerSeries.ringHom
    (transfer G m) (denominatorInverse G m)
  have hleft : Z * MvPolynomial.coeToMvPowerSeries.ringHom.mapMatrix (transfer G m) = 1 :=
    ReleaseTransferMatrix.rationalMatrix_mul _ _ _ (denominator_inverse_mul G m)
  calc
    seriesMatrix G m = 1 * seriesMatrix G m := (one_mul _).symm
    _ = (Z * MvPolynomial.coeToMvPowerSeries.ringHom.mapMatrix (transfer G m)) *
      seriesMatrix G m := by rw [hleft]
    _ = Z * (MvPolynomial.coeToMvPowerSeries.ringHom.mapMatrix (transfer G m) *
      seriesMatrix G m) := mul_assoc _ _ _
    _ = Z := by rw [transfer_mul_seriesMatrix, mul_one]

theorem denominator_mul_series (s t : V) :
    (denominator G m : MvPowerSeries σ R) * series G m s t =
      (Matrix.adjugate (transfer G m) s t : MvPolynomial σ R) := by
  have h := ReleaseTransferMatrix.denominator_smul_rationalMatrix
    MvPolynomial.coeToMvPowerSeries.ringHom (transfer G m) (denominatorInverse G m)
    (denominator_mul_inverse G m)
  rw [← seriesMatrix_eq_rationalMatrix] at h
  exact congrFun (congrFun h s) t

noncomputable def endpointSeries (u v : V → R) : MvPowerSeries σ R :=
  ReleaseTransferMatrix.contract (MvPowerSeries.C ∘ u) (seriesMatrix G m) (MvPowerSeries.C ∘ v)

noncomputable def endpointNumerator (u v : V → R) : MvPolynomial σ R :=
  ReleaseTransferMatrix.contract (MvPolynomial.C ∘ u) (Matrix.adjugate (transfer G m))
    (MvPolynomial.C ∘ v)

theorem endpoint_rationality (u v : V → R) :
    (denominator G m : MvPowerSeries σ R) * endpointSeries G m u v =
      (endpointNumerator G m u v : MvPowerSeries σ R) := by
  rw [endpointSeries, seriesMatrix_eq_rationalMatrix]
  simpa [endpointNumerator, denominator, Function.comp_def] using
    ReleaseTransferMatrix.rational_endpoint_identity MvPolynomial.coeToMvPowerSeries.ringHom
      (transfer G m) (denominatorInverse G m) (denominator_mul_inverse G m)
      (MvPolynomial.C ∘ u) (MvPolynomial.C ∘ v)

theorem endpoint_coeff (u v : V → R) (n : σ →₀ ℕ) :
    MvPowerSeries.coeff n (endpointSeries G m u v) =
      ∑ i, ∑ j, u i * coefficient G m i j n * v j := by
  simp [endpointSeries, ReleaseTransferMatrix.contract, seriesMatrix,
    map_sum, MvPowerSeries.coeff_C_mul, MvPowerSeries.coeff_mul_C]

end Komorebi.PaperII.ReleaseTransferMultigraded
