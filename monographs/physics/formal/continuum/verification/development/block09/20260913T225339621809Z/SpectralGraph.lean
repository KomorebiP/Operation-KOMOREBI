module
public import KomorebiPhysics.DiagonalDomain

/-! Exact weighted spectral-domain and graph-tail formulas. The multiplier
model is not identified with a differential oscillator without a separate
unitary-equivalence theorem. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace SpectralGraph
open Filter
open scoped Topology BigOperators lp
variable {I : Type*} [DecidableEq I]
variable (eig : I → ℝ)

omit [DecidableEq I] in
theorem norm_sq_tsum (x : ℓ²(I, ℂ)) : ‖x‖ ^ 2 = ∑' i, ‖x i‖ ^ 2 := by
  simpa using lp.norm_rpow_eq_tsum (by norm_num : 0 < (2 : ENNReal).toReal) x

omit [DecidableEq I] in
theorem norm_sq_summable (x : ℓ²(I, ℂ)) : Summable (fun i => ‖x i‖ ^ 2) := by
  simpa using (memℓp_gen_iff (by norm_num : 0 < (2 : ENNReal).toReal)).mp (lp.memℓp x)

omit [DecidableEq I] in
theorem weighted_norm_sq (r : ℝ) (z : ℂ) : ‖(r : ℂ) * z‖ ^ 2 = r ^ 2 * ‖z‖ ^ 2 := by
  rw [norm_mul, mul_pow, Complex.norm_real, Real.norm_eq_abs, sq_abs]

omit [DecidableEq I] in
/-- The maximal operator domain is exactly the source weighted-l2 condition. -/
theorem domain_iff (x : ℓ²(I, ℂ)) : x ∈ DiagonalDomain.domain eig ↔
    Summable (fun i => eig i ^ 2 * ‖x i‖ ^ 2) := by
  change Memℓp (fun i => (eig i : ℂ) * x i) 2 ↔ _
  rw [memℓp_gen_iff (by norm_num)]
  simp only [ENNReal.toReal_ofNat, Real.rpow_two, weighted_norm_sq]

omit [DecidableEq I] in
theorem action_norm_sq (x : (DiagonalDomain.operator eig).domain) :
    ‖DiagonalDomain.operator eig x‖ ^ 2 = ∑' i, eig i ^ 2 * ‖(x : ℓ²(I, ℂ)) i‖ ^ 2 := by
  rw [norm_sq_tsum]
  simp only [DiagonalDomain.operator_apply, weighted_norm_sq]

omit [DecidableEq I] in
theorem graph_weight_summable (x : (DiagonalDomain.operator eig).domain) :
    Summable (fun i => (1 + eig i ^ 2) * ‖(x : ℓ²(I, ℂ)) i‖ ^ 2) := by
  have h := (norm_sq_summable (x : ℓ²(I, ℂ))).add ((domain_iff eig x).mp x.property)
  simpa only [add_mul, one_mul] using h

omit [DecidableEq I] in
theorem graph_norm_sq (x : (DiagonalDomain.operator eig).domain) :
    GraphDomain.graphNorm (DiagonalDomain.operator eig) x ^ 2 =
      ∑' i, (1 + eig i ^ 2) * ‖(x : ℓ²(I, ℂ)) i‖ ^ 2 := by
  rw [GraphDomain.graphNorm_sq, norm_sq_tsum, action_norm_sq]
  simp only [add_mul, one_mul]
  exact ((norm_sq_summable (x : ℓ²(I, ℂ))).tsum_add ((domain_iff eig x).mp x.property)).symm

theorem coordinate_tail_sq (x : ℓ²(I, ℂ)) (s : Finset I) :
    ‖x - DiagonalDomain.coordinateAtlas.partialSum s x‖ ^ 2 =
      ‖x‖ ^ 2 - ∑ i ∈ s, ‖x i‖ ^ 2 := by
  simpa only [ENNReal.toReal_ofNat, Real.rpow_two, StrongAtlas.partialSum,
    DiagonalDomain.coordinateAtlas, DiagonalDomain.coordinate_apply] using
    lp.norm_compl_sum_single (by norm_num : 0 < (2 : ENNReal).toReal) x s

/-- Exact finite-cutoff graph error, keeping both state and generator tails. -/
theorem graph_tail_sq (x : (DiagonalDomain.operator eig).domain) (s : Finset I) :
    GraphDomain.graphNorm (DiagonalDomain.operator eig)
      (x - (DiagonalDomain.atlas eig).partialSum s x) ^ 2 =
      GraphDomain.graphNorm (DiagonalDomain.operator eig) x ^ 2 -
        ∑ i ∈ s, (1 + eig i ^ 2) * ‖(x : ℓ²(I, ℂ)) i‖ ^ 2 := by
  rw [GraphDomain.graphNorm_sq, GraphDomain.graphNorm_sq]
  rw [Submodule.coe_sub, LinearPMap.map_sub, DomainAtlas.partial_coe, DomainAtlas.action_partial]
  simp only [DiagonalDomain.action_project]
  change ‖(x : ℓ²(I, ℂ)) - DiagonalDomain.coordinateAtlas.partialSum s x‖ ^ 2 +
    ‖DiagonalDomain.operator eig x - DiagonalDomain.coordinateAtlas.partialSum s
      (DiagonalDomain.operator eig x)‖ ^ 2 = _
  rw [coordinate_tail_sq, coordinate_tail_sq]
  simp only [DiagonalDomain.operator_apply, weighted_norm_sq, add_mul, one_mul,
    Finset.sum_add_distrib]
  ring

/-- The full graph error genuinely tends to zero on the directed finite-set net. -/
theorem graph_tail_tendsto (x : (DiagonalDomain.operator eig).domain) :
    Tendsto (fun s => GraphDomain.graphNorm (DiagonalDomain.operator eig)
      (x - (DiagonalDomain.atlas eig).partialSum s x) ^ 2) atTop (𝓝 0) := by
  have h := (DiagonalDomain.graph_compatible eig x).pow 2
  have heq : ∀ s, GraphDomain.graphNorm (DiagonalDomain.operator eig)
      (x - (DiagonalDomain.atlas eig).partialSum s x) =
      GraphDomain.graphNorm (DiagonalDomain.operator eig)
      ((DiagonalDomain.atlas eig).partialSum s x - x) := by
    intro s
    rw [← neg_sub ((DiagonalDomain.atlas eig).partialSum s x) x,
      GraphDomain.graphNorm_neg]
  simpa only [heq, zero_pow (by decide : 2 ≠ 0)] using h

/-- In the spectral atlas the individual currents vanish; this is not assumed
in the general countable continuity theorem. -/
theorem spectral_current_zero (x : (DiagonalDomain.operator eig).domain) (i j : I) :
    (DiagonalDomain.atlas eig).current x i j = 0 := by
  by_cases hij : i = j
  · subst j
    exact (DiagonalDomain.atlas eig).current_self (DiagonalDomain.symmetric eig) x i
  · unfold DomainAtlas.current DomainAtlas.amplitude
    rw [DiagonalDomain.action_project]
    have h := DiagonalDomain.coordinateAtlas.packets_orthogonal
      (x : ℓ²(I, ℂ)) (DiagonalDomain.operator eig x) i j hij
    change inner ℂ (DiagonalDomain.coordinate i x)
      (DiagonalDomain.coordinate j (DiagonalDomain.operator eig x)) = 0 at h
    simpa only [DiagonalDomain.atlas, DiagonalDomain.coordinateAtlas, h,
      Complex.zero_im, mul_zero]

end SpectralGraph
end KomorebiPhysics
