import KomorebiVerification.PaperII.TransferZeta
import KomorebiVerification.PaperII.ReleaseTransferMatrix
/-!
Scalar-weighted semantic walks. The finite walk type is the original unrestricted
list model with its proved finite enumeration. Products below retain every edge
occurrence, including parallel edges and repeated visits.
-/
set_option autoImplicit false
open scoped BigOperators

namespace Komorebi.PaperII.ReleaseTransferScalar
open TransferZeta TransferZeta.PositiveWeightedMultigraph
universe u v w
variable {V : Type u} {E : Type v} {R : Type w}
variable [Fintype E] [DecidableEq V] [CommRing R]
variable (G : PositiveWeightedMultigraph V E) (m : E → R)

def walkMultiplicity (es : List E) : R := (es.map m).prod

omit [Fintype E] in
@[simp] theorem walkMultiplicity_nil : walkMultiplicity m [] = 1 := rfl
omit [Fintype E] in
@[simp] theorem walkMultiplicity_cons (e : E) (es : List E) :
    walkMultiplicity m (e :: es) = m e * walkMultiplicity m es := rfl

noncomputable def coefficient (s t : V) (n : ℕ) : R :=
  ∑ x : G.ExactWalk s t n, walkMultiplicity m x.val

theorem coefficient_firstEdge (s t : V) (n : ℕ) :
    coefficient G m s t n = (if s = t ∧ n = 0 then 1 else 0) +
      ∑ e : E, if G.source e = s ∧ G.weight e ≤ n then
        m e * coefficient G m (G.target e) t (n - G.weight e) else 0 := by
  classical
  let f : EmptyExactWalk s t n ⊕ G.FirstEdgeExactWalk s t n → R :=
    Sum.elim (fun _ ↦ 1) (fun x ↦ m x.val.1 * walkMultiplicity m x.val.2)
  have hfirst : coefficient G m s t n = ∑ x, f x := by
    apply Fintype.sum_equiv (G.exactWalkFirstEdgeEquiv s t n)
    intro x
    rcases x with ⟨es, hx⟩
    cases es <;> rfl
  rw [hfirst, Fintype.sum_sum_type]
  have hempty : (∑ _x : EmptyExactWalk s t n, (1 : R)) =
      if s = t ∧ n = 0 then 1 else 0 := by
    by_cases h : s = t ∧ n = 0 <;> simp [EmptyExactWalk, h]
  change (∑ _x : EmptyExactWalk s t n, (1 : R)) +
    (∑ x : G.FirstEdgeExactWalk s t n, m x.val.1 * walkMultiplicity m x.val.2) = _
  rw [hempty]
  congr 1
  calc
    _ = ∑ x : G.FirstEdgeTail s t n,
          m x.1 * walkMultiplicity m x.2.val.val := by
      apply Fintype.sum_equiv (G.firstEdgeTailEquiv s t n)
      intro x
      rcases x with ⟨⟨e, es⟩, hs, hw, hn⟩
      rfl
    _ = _ := by
      rw [Fintype.sum_sigma]
      apply Finset.sum_congr rfl
      intro e _
      by_cases h : G.source e = s ∧ G.weight e ≤ n
      · rw [ite_eq_left h, coefficient, Finset.mul_sum]
        apply Fintype.sum_equiv (Equiv.subtypeUnivEquiv fun _ ↦ h)
        intro x
        rfl
      · rw [ite_eq_right h]
        apply Finset.sum_eq_zero
        intro x _
        exact False.elim (h x.property)

noncomputable def series (s t : V) : PowerSeries R :=
  PowerSeries.mk (coefficient G m s t)

@[simp] theorem coeff_series (s t : V) (n : ℕ) :
    PowerSeries.coeff n (series G m s t) = coefficient G m s t n := by
  simp [series]

noncomputable def adjacency : Matrix V V (Polynomial R) :=
  fun i j ↦ ∑ e : E, if G.source e = i ∧ G.target e = j then
    Polynomial.monomial (G.weight e) (m e) else 0

theorem adjacency_coeff_zero (i j : V) : (adjacency G m i j).coeff 0 = 0 := by
  classical
  rw [adjacency, ← Polynomial.lcoeff_apply, map_sum]
  simp only [Polynomial.lcoeff_apply]
  apply Finset.sum_eq_zero
  intro e _
  by_cases h : G.source e = i ∧ G.target e = j
  · simp [h, Polynomial.coeff_monomial, Nat.ne_of_gt (G.weight_pos e)]
  · simp [h]



variable [Fintype V]

noncomputable def adjacencySeries : Matrix V V (PowerSeries R) :=
  Polynomial.coeToPowerSeries.ringHom.mapMatrix (adjacency G m)

noncomputable def seriesMatrix : Matrix V V (PowerSeries R) := fun s t ↦ series G m s t

theorem adjacencySeries_mul_seriesMatrix_apply (s t : V) :
    (adjacencySeries G m * seriesMatrix G m) s t =
      ∑ e : E, if G.source e = s then
        (PowerSeries.C (m e) * PowerSeries.X ^ G.weight e) *
          series G m (G.target e) t else 0 := by
  classical
  have hmon (e : E) :
      ((Polynomial.monomial (G.weight e) (m e) : Polynomial R) : PowerSeries R) =
        PowerSeries.C (m e) * PowerSeries.X ^ G.weight e := by
    ext n
    simp [PowerSeries.coeff_monomial]
  have hadj (i j : V) : adjacencySeries G m i j =
      ∑ e : E, if G.source e = i ∧ G.target e = j then
        (PowerSeries.C (m e) * PowerSeries.X ^ G.weight e) else 0 := by
    rw [adjacencySeries, RingHom.mapMatrix_apply, Matrix.map_apply, adjacency, map_sum]
    apply Finset.sum_congr rfl
    intro e _
    by_cases h : G.source e = i ∧ G.target e = j <;> simp [h, hmon]
  rw [Matrix.mul_apply]
  simp_rw [hadj, Finset.sum_mul]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro e _
  by_cases hs : G.source e = s
  · simp [hs, seriesMatrix]
  · simp [hs]

theorem coeff_adjacency_mul_series (s t : V) (n : ℕ) :
    PowerSeries.coeff n ((adjacencySeries G m * seriesMatrix G m) s t) =
      ∑ e : E, if G.source e = s ∧ G.weight e ≤ n then
        m e * coefficient G m (G.target e) t (n - G.weight e) else 0 := by
  classical
  rw [adjacencySeries_mul_seriesMatrix_apply, map_sum]
  apply Finset.sum_congr rfl
  intro e _
  by_cases hs : G.source e = s
  · by_cases hw : G.weight e ≤ n <;>
      simp [hs, hw, mul_assoc, PowerSeries.coeff_C_mul, PowerSeries.coeff_X_pow_mul']
  · simp [hs]

theorem seriesMatrix_eq_one_add_adjacency_mul :
    seriesMatrix G m = 1 + adjacencySeries G m * seriesMatrix G m := by
  ext s t n
  change PowerSeries.coeff n (series G m s t) =
    PowerSeries.coeff n ((1 : Matrix V V (PowerSeries R)) s t +
      (adjacencySeries G m * seriesMatrix G m) s t)
  rw [coeff_series, map_add, coeff_adjacency_mul_series]
  have hrec := coefficient_firstEdge G m s t n
  by_cases hst : s = t
  · subst t
    by_cases hn : n = 0 <;> simpa [Matrix.one_apply, PowerSeries.coeff_one, hn] using hrec
  · simpa [Matrix.one_apply, PowerSeries.coeff_one, hst] using hrec

noncomputable def transfer : Matrix V V (Polynomial R) := 1 - adjacency G m
noncomputable def denominator : Polynomial R := Matrix.det (transfer G m)
noncomputable def denominatorInverse : PowerSeries R :=
  PowerSeries.invOfUnit (denominator G m : PowerSeries R) (1 : Rˣ)

theorem denominator_coeff_zero : (denominator G m).coeff 0 = 1 := by
  change Polynomial.constantCoeff (denominator G m) = 1
  rw [denominator, RingHom.map_det]
  have h : Polynomial.constantCoeff.mapMatrix (transfer G m) = (1 : Matrix V V R) := by
    ext i j
    by_cases hij : i = j <;>
      simp [transfer, RingHom.mapMatrix_apply, Matrix.map_apply,
        Polynomial.constantCoeff_apply, adjacency_coeff_zero, Matrix.one_apply, hij]
  rw [h, Matrix.det_one]

theorem denominator_mul_inverse :
    (denominator G m : PowerSeries R) * denominatorInverse G m = 1 := by
  apply PowerSeries.mul_invOfUnit
  simpa [Polynomial.constantCoeff_coe] using denominator_coeff_zero G m

theorem denominator_inverse_mul :
    denominatorInverse G m * (denominator G m : PowerSeries R) = 1 := by
  apply PowerSeries.invOfUnit_mul
  simpa [Polynomial.constantCoeff_coe] using denominator_coeff_zero G m

theorem transfer_mul_seriesMatrix :
    Polynomial.coeToPowerSeries.ringHom.mapMatrix (transfer G m) * seriesMatrix G m = 1 := by
  have ht : Polynomial.coeToPowerSeries.ringHom.mapMatrix (transfer G m) =
      1 - adjacencySeries G m := by
    rw [transfer, adjacencySeries, map_sub, map_one]
  rw [ht, sub_mul, one_mul]
  exact sub_eq_iff_eq_add.mpr (seriesMatrix_eq_one_add_adjacency_mul G m)

theorem seriesMatrix_eq_rationalMatrix : seriesMatrix G m =
    ReleaseTransferMatrix.rationalMatrix Polynomial.coeToPowerSeries.ringHom
      (transfer G m) (denominatorInverse G m) := by
  let Z := ReleaseTransferMatrix.rationalMatrix Polynomial.coeToPowerSeries.ringHom
    (transfer G m) (denominatorInverse G m)
  have hleft : Z * Polynomial.coeToPowerSeries.ringHom.mapMatrix (transfer G m) = 1 :=
    ReleaseTransferMatrix.rationalMatrix_mul _ _ _ (denominator_inverse_mul G m)
  calc
    seriesMatrix G m = 1 * seriesMatrix G m := (one_mul _).symm
    _ = (Z * Polynomial.coeToPowerSeries.ringHom.mapMatrix (transfer G m)) *
      seriesMatrix G m := by rw [hleft]
    _ = Z * (Polynomial.coeToPowerSeries.ringHom.mapMatrix (transfer G m) *
      seriesMatrix G m) := mul_assoc _ _ _
    _ = Z := by rw [transfer_mul_seriesMatrix, mul_one]

theorem denominator_mul_series (s t : V) :
    (denominator G m : PowerSeries R) * series G m s t =
      (Matrix.adjugate (transfer G m) s t : Polynomial R) := by
  have h := ReleaseTransferMatrix.denominator_smul_rationalMatrix
    Polynomial.coeToPowerSeries.ringHom (transfer G m) (denominatorInverse G m)
    (denominator_mul_inverse G m)
  rw [← seriesMatrix_eq_rationalMatrix] at h
  exact congrFun (congrFun h s) t

noncomputable def endpointSeries (u v : V → R) : PowerSeries R :=
  ReleaseTransferMatrix.contract (PowerSeries.C ∘ u) (seriesMatrix G m) (PowerSeries.C ∘ v)

noncomputable def endpointNumerator (u v : V → R) : Polynomial R :=
  ReleaseTransferMatrix.contract (Polynomial.C ∘ u) (Matrix.adjugate (transfer G m))
    (Polynomial.C ∘ v)

theorem endpoint_rationality (u v : V → R) :
    (denominator G m : PowerSeries R) * endpointSeries G m u v =
      (endpointNumerator G m u v : PowerSeries R) := by
  rw [endpointSeries, seriesMatrix_eq_rationalMatrix]
  simpa [endpointNumerator, denominator, Function.comp_def] using
    ReleaseTransferMatrix.rational_endpoint_identity Polynomial.coeToPowerSeries.ringHom
      (transfer G m) (denominatorInverse G m) (denominator_mul_inverse G m)
      (Polynomial.C ∘ u) (Polynomial.C ∘ v)

theorem endpoint_coeff (u v : V → R) (n : ℕ) :
    PowerSeries.coeff n (endpointSeries G m u v) =
      ∑ i, ∑ j, u i * coefficient G m i j n * v j := by
  simp [endpointSeries, ReleaseTransferMatrix.contract, seriesMatrix,
    map_sum, PowerSeries.coeff_C_mul, PowerSeries.coeff_mul_C]

theorem endpoint_recurrence_at_zero_coefficient (u v : V → R) (n : ℕ)
    (h : (endpointNumerator G m u v).coeff n = 0) :
    ∑ p ∈ Finset.HasAntidiagonal.antidiagonal n,
      (denominator G m).coeff p.1 * PowerSeries.coeff p.2 (endpointSeries G m u v) = 0 := by
  have hc := congrArg (PowerSeries.coeff n) (endpoint_rationality G m u v)
  rw [PowerSeries.coeff_mul] at hc
  simpa [h] using hc

theorem endpoint_recurrence (u v : V → R) (n : ℕ)
    (h : (endpointNumerator G m u v).degree < (n : WithBot ℕ)) :
    ∑ p ∈ Finset.HasAntidiagonal.antidiagonal n,
      (denominator G m).coeff p.1 * PowerSeries.coeff p.2 (endpointSeries G m u v) = 0 := by
  exact endpoint_recurrence_at_zero_coefficient G m u v n
    (Polynomial.coeff_eq_zero_of_degree_lt h)

end Komorebi.PaperII.ReleaseTransferScalar
