import KomorebiLSM.BernsteinRationalBasis
import KomorebiLSM.TensorBernsteinCertificate
import Mathlib.Topology.MetricSpace.Thickening
import Mathlib.Algebra.MvPolynomial.Degrees

set_option autoImplicit false
namespace Komorebi.LSM.BernsteinCellPositivity
open scoped BigOperators
open MvPolynomial
open TensorBernsteinCertificate BernsteinRationalBasis
noncomputable section

theorem affine_axis_reconstruct (n d : ℕ) (hd : d≤n) (a w : ℚ) (axis : Fin 2) :
    ∑ i : Fin (n+1), C (affineCoordinates n d a w i)*basisPolynomial n i axis =
      (C a+C w*X axis)^d := by
  have h := congrArg (Polynomial.eval₂RingHom (C : ℚ →+* Polynomial₂) (X axis))
    (affine_reconstruct n d hd a w)
  simpa [basisPolynomial, bernsteinPolynomial, Polynomial.eval₂_pow, Polynomial.eval₂_sub] using h

/-- The submitted coefficients are rational, with one fixed degree for all cells. -/
def coefficients (p : Polynomial₂) (a w : Fin 2 → ℚ) :
    Fin (p.totalDegree+1) → Fin (p.totalDegree+1) → ℚ := fun i j =>
  ∑ d ∈ p.support, p.coeff d *
    affineCoordinates p.totalDegree (d 0) (a 0) (w 0) i *
    affineCoordinates p.totalDegree (d 1) (a 1) (w 1) j

/-- The real extension of the same finite rational formula. -/
def realCoefficients (p : Polynomial₂) (a w : Fin 2 → ℝ) :
    Fin (p.totalDegree+1) → Fin (p.totalDegree+1) → ℝ := fun i j =>
  ∑ d ∈ p.support, (p.coeff d : ℝ) *
    affineReal p.totalDegree (d 0) (a 0) (w 0) i *
    affineReal p.totalDegree (d 1) (a 1) (w 1) j

@[simp] theorem cast_coefficients (p : Polynomial₂) (a w : Fin 2 → ℚ)
    (i j : Fin (p.totalDegree+1)) :
    (coefficients p a w i j : ℝ) =
      realCoefficients p (fun k => (a k : ℝ)) (fun k => (w k : ℝ)) i j := by
  simp [coefficients, realCoefficients]

theorem support_degree (p : Polynomial₂) (d : Fin 2 →₀ ℕ) (hd : d∈p.support) (i : Fin 2) :
    d i≤p.totalDegree :=
  (MvPolynomial.monomial_le_degreeOf i hd).trans (MvPolynomial.degreeOf_le_totalDegree p i)

theorem rational_reconstruction (p : Polynomial₂) (a w : Fin 2 → ℚ) :
    MvPolynomial.bind₁ (fun axis => C (a axis)+C (w axis)*X axis) p =
      tensorPolynomial (coefficients p a w) := by
  have hexpand : MvPolynomial.bind₁ (fun axis => C (a axis)+C (w axis)*X axis) p =
      ∑ d ∈ p.support, C (p.coeff d) *
        (C (a 0)+C (w 0)*X 0)^(d 0) * (C (a 1)+C (w 1)*X 1)^(d 1) := by
    change MvPolynomial.eval₂ C (fun axis => C (a axis)+C (w axis)*X axis) p = _
    rw [MvPolynomial.eval₂_eq']
    simp [Fin.prod_univ_two, mul_assoc]
  rw [hexpand]
  have hterm (d : Fin 2 →₀ ℕ) (hd : d∈p.support) :
      C (p.coeff d) * (C (a 0)+C (w 0)*X 0)^(d 0) *
        (C (a 1)+C (w 1)*X 1)^(d 1) =
      ∑ i : Fin (p.totalDegree+1), ∑ j : Fin (p.totalDegree+1),
        C (p.coeff d * affineCoordinates p.totalDegree (d 0) (a 0) (w 0) i *
          affineCoordinates p.totalDegree (d 1) (a 1) (w 1) j) *
          basisPolynomial p.totalDegree i 0 * basisPolynomial p.totalDegree j 1 := by
    rw [← affine_axis_reconstruct p.totalDegree (d 0) (support_degree p d hd 0),
      ← affine_axis_reconstruct p.totalDegree (d 1) (support_degree p d hd 1)]
    simp only [Finset.mul_sum, Finset.sum_mul, map_mul]
    rw [Finset.sum_comm]
    apply Finset.sum_congr rfl
    intro i _
    apply Finset.sum_congr rfl
    intro j _
    ring
  have hsum := Finset.sum_congr rfl hterm
  rw [hsum]
  unfold tensorPolynomial coefficients
  simp only [map_sum, map_mul, Finset.sum_mul]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro i _
  rw [Finset.sum_comm]

theorem continuous_realCoefficients (p : Polynomial₂) (i j : Fin (p.totalDegree+1)) :
    Continuous (fun aw : (Fin 2 → ℝ) × (Fin 2 → ℝ) => realCoefficients p aw.1 aw.2 i j) := by
  unfold realCoefficients affineReal
  fun_prop

@[simp] theorem realCoefficients_zero_width (p : Polynomial₂) (a : Fin 2 → ℝ)
    (i j : Fin (p.totalDegree+1)) : realCoefficients p a 0 i j = value p a := by
  simp only [realCoefficients, Pi.zero_apply, affineReal_zero_width]
  rw [value, MvPolynomial.eval₂_eq']
  simp [Fin.prod_univ_two, mul_assoc]

theorem square_compact : IsCompact square.domain := by
  convert (isCompact_Icc : IsCompact (Set.Icc (fun _ : Fin 2 => (-1 : ℝ)) (fun _ => (1 : ℝ)))) using 1
  ext a
  simp [Rectangle.domain, square, Set.mem_Icc, Pi.le_def, forall_and]

/-- Uniformity follows from a genuine compact zero-width set and continuity of the actual coefficients. -/
theorem positive_coefficients_near_zero (p : Polynomial₂)
    (hp : ∀ a∈square.domain, 0<value p a) :
    ∃ δ>0, ∀ a∈square.domain, ∀ w : Fin 2 → ℝ,
      (∀ axis, |w axis|<δ) → ∀ i j, 0<realCoefficients p a w i j := by
  let K : Set ((Fin 2 → ℝ) × (Fin 2 → ℝ)) := square.domain ×ˢ {0}
  let U : Set ((Fin 2 → ℝ) × (Fin 2 → ℝ)) :=
    {aw | ∀ i j, 0<realCoefficients p aw.1 aw.2 i j}
  have hK : IsCompact K := square_compact.prod isCompact_singleton
  have hU : IsOpen U := by
    simp only [U, Set.ofPred_forall]
    exact isOpen_iInter_of_finite (fun i => isOpen_iInter_of_finite (fun j =>
      isOpen_lt continuous_const (continuous_realCoefficients p i j)))
  have hKU : K⊆U := by
    rintro ⟨a,w⟩ ⟨ha,hw⟩
    have hw0 : w=0 := Set.mem_singleton_iff.mp hw
    subst w
    intro i j
    rw [realCoefficients_zero_width]
    exact hp a ha
  obtain ⟨δ,hδ,hsub⟩ := hK.exists_thickening_subset_open hU hKU
  refine ⟨δ,hδ,?_⟩
  intro a ha w hw
  have hwn : ‖w‖<δ := (pi_norm_lt_iff hδ).mpr (fun axis => by
    simpa only [Real.norm_eq_abs] using hw axis)
  change (a,w)∈U
  apply hsub
  apply Metric.mem_thickening_iff.mpr
  refine ⟨(a,0),⟨ha,by simp⟩,?_⟩
  simpa only [Prod.dist_eq, dist_self, dist_zero_right, max_eq_right (norm_nonneg w)] using hwn

/-- Strict positivity on the square produces actual rational tensor witnesses on every sufficiently small cell. -/
theorem exists_small_positive (p : Polynomial₂) (hp : ∀ x∈square.domain, 0<value p x) :
    ∃ δ>0, ∀ R : Rectangle, R.domain⊆square.domain →
      (∀ axis, (R.width axis : ℝ)<δ) → Nonempty (LocalCertificate p R) := by
  obtain ⟨δ,hδ,hcoeff⟩ := positive_coefficients_near_zero p hp
  refine ⟨δ,hδ,?_⟩
  intro R hR hw
  have ha : (fun axis => (R.lo axis : ℝ))∈square.domain := by
    apply hR
    intro axis
    refine ⟨le_rfl,?_⟩
    change (R.lo axis : ℝ) ≤ (R.hi axis : ℝ)
    exact_mod_cast (R.proper axis).le
  have hc := hcoeff (fun axis => (R.lo axis : ℝ)) ha (fun axis => (R.width axis : ℝ))
    (fun axis => by rw [abs_of_pos (R.width_pos axis)]; exact hw axis)
  refine ⟨{
    degreeX := p.totalDegree
    degreeY := p.totalDegree
    coefficient := coefficients p R.lo R.width
    nonneg := ?_
    identity := ?_ }⟩
  · intro i j
    have hreal : 0<(coefficients p R.lo R.width i j : ℝ) := by
      rw [cast_coefficients]
      exact hc i j
    exact le_of_lt (by exact_mod_cast hreal)
  · exact rational_reconstruction p R.lo R.width

end
end Komorebi.LSM.BernsteinCellPositivity
