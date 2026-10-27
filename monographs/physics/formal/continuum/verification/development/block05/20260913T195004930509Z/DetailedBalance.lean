module

public import KomorebiPhysics.LindbladJumps
public import KomorebiPhysics.InformationTransport
public import Mathlib.Analysis.Calculus.Deriv.MeanValue

/-!
Chapter 4.8, equations (4.53)--(4.58). Detailed-balance relative-entropy
dissipation, including zero-rate edges in a nonsingular conductance form.
Strictly positive populations and reference weights are explicit. The
reference distribution is fixed during time differentiation. The result is
about packet relative entropy, not von Neumann entropy or empirical physics.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics.DetailedBalance
open scoped BigOperators
open LindbladJumps
variable {n : Type*} [Fintype n]

/-- Receiving-first detailed balance. Positivity and normalization are separate. -/
def Balanced (γ : n → n → ℝ) (π : n → ℝ) : Prop :=
  ∀ a b, γ a b * π b = γ b a * π a

/-- Density relative to a fixed positive reference. -/
def ratio (p π : n → ℝ) (a : n) : ℝ := p a / π a

/-- The edge conductance, symmetric under detailed balance. -/
def conductance (γ : n → n → ℝ) (π : n → ℝ) (a b : n) : ℝ := γ a b * π b

/-- Literal packet relative entropy, using natural logarithms. -/
def relativeEntropy (p π : n → ℝ) : ℝ := ∑ a, p a * Real.log (ratio p π a)

/-- Nonsingular entropy dissipation. Zero-rate edges contribute zero without
forming a logarithm of a zero-over-zero flux ratio. -/
def dissipation (γ : n → n → ℝ) (π p : n → ℝ) : ℝ :=
  (1/2 : ℝ) * ∑ a, ∑ b, conductance γ π a b * (ratio p π a - ratio p π b) *
    (Real.log (ratio p π a) - Real.log (ratio p π b))

omit [Fintype n] in
/-- Detailed balance makes the actual conductance symmetric. -/
theorem conductance_symm {γ : n → n → ℝ} {π : n → ℝ}
    (hbal : Balanced γ π) (a b : n) : conductance γ π a b = conductance γ π b a :=
  hbal a b

omit [Fintype n] in
/-- Reference populations have zero current on every edge. -/
theorem equilibrium_current {γ : n → n → ℝ} {π : n → ℝ}
    (hbal : Balanced γ π) (a b : n) : current γ π a b = 0 := by
  unfold current
  rw [hbal a b, sub_self]

omit [Fintype n] in
/-- Relative densities are positive under the declared domain assumptions. -/
theorem ratio_pos {p π : n → ℝ} (hp : ∀ a, 0 < p a) (hπ : ∀ a, 0 < π a) (a : n) :
    0 < ratio p π a := div_pos (hp a) (hπ a)

omit [Fintype n] in
/-- Each directed flux is conductance times the source relative density. -/
theorem flux_factor (γ : n → n → ℝ) (π p : n → ℝ)
    (hπ : ∀ a, 0 < π a) (a b : n) :
    conductance γ π a b * ratio p π b = γ a b * p b := by
  unfold conductance ratio
  field_simp [ne_of_gt (hπ b)]

omit [Fintype n] in
/-- The current is a conductance times a relative-density difference. -/
theorem current_factor {γ : n → n → ℝ} {π : n → ℝ}
    (hbal : Balanced γ π) (p : n → ℝ) (hπ : ∀ a, 0 < π a) (a b : n) :
    current γ p a b = conductance γ π a b * (ratio p π b - ratio p π a) := by
  rw [mul_sub, flux_factor γ π p hπ a b,
    conductance_symm hbal a b, flux_factor γ π p hπ b a]
  rfl

/-- Elementary logarithmic monotonicity controls the entropy-production sign. -/
theorem log_difference_product_nonneg {x y : ℝ} (hx : 0 < x) (hy : 0 < y) :
    0 ≤ (x-y) * (Real.log x - Real.log y) := by
  rcases le_total x y with hxy | hyx
  · exact mul_nonneg_of_nonpos_of_nonpos (sub_nonpos.mpr hxy)
      (sub_nonpos.mpr (Real.log_le_log hx hxy))
  · exact mul_nonneg (sub_nonneg.mpr hyx) (sub_nonneg.mpr (Real.log_le_log hy hyx))

/-- Equation (4.58), with positive arguments explicitly supplied. -/
theorem log_ratio_product_nonneg {x y : ℝ} (hx : 0 < x) (hy : 0 < y) :
    0 ≤ (x-y) * Real.log (x/y) := by
  rw [Real.log_div (ne_of_gt hx) (ne_of_gt hy)]
  exact log_difference_product_nonneg hx hy

/-- The edge factor vanishes exactly when its positive densities agree. -/
theorem log_difference_product_eq_zero_iff {x y : ℝ} (hx : 0 < x) (hy : 0 < y) :
    (x-y) * (Real.log x - Real.log y) = 0 ↔ x = y := by
  constructor
  · intro h
    rcases mul_eq_zero.mp h with hd | hl
    · exact sub_eq_zero.mp hd
    · exact Real.log_injOn_pos hx hy (sub_eq_zero.mp hl)
  · intro h
    simp [h]

omit [Fintype n] in
/-- Every conductance-form edge summand is nonnegative, including zero rates. -/
theorem edge_nonneg (γ : n → n → ℝ) (π p : n → ℝ)
    (hγ : ∀ a b, 0 ≤ γ a b) (hπ : ∀ a, 0 < π a) (hp : ∀ a, 0 < p a) (a b : n) :
    0 ≤ conductance γ π a b * (ratio p π a - ratio p π b) *
      (Real.log (ratio p π a) - Real.log (ratio p π b)) := by
  rw [mul_assoc]
  exact mul_nonneg (mul_nonneg (hγ a b) (le_of_lt (hπ b)))
    (log_difference_product_nonneg (ratio_pos hp hπ a) (ratio_pos hp hπ b))

/-- The dissipation is nonnegative. No strictly positive-rate assumption occurs. -/
theorem dissipation_nonneg (γ : n → n → ℝ) (π p : n → ℝ)
    (hγ : ∀ a b, 0 ≤ γ a b) (hπ : ∀ a, 0 < π a) (hp : ∀ a, 0 < p a) :
    0 ≤ dissipation γ π p := by
  apply mul_nonneg (by norm_num : (0:ℝ) ≤ 1/2)
  exact Finset.sum_nonneg (fun a _ => Finset.sum_nonneg (fun b _ => edge_nonneg γ π p hγ hπ hp a b))

/-- Derivative of the actual x log(x/pi) function; pi is constant in time. -/
theorem hasDerivAt_relative_term {x π : ℝ} (hx : 0 < x) (hπ : 0 < π) :
    HasDerivAt (fun y : ℝ => y * Real.log (y / π)) (1 + Real.log (x / π)) x := by
  have hd := (hasDerivAt_id x).div_const π
  have h := (hasDerivAt_id x).mul (hd.log (ne_of_gt (div_pos hx hπ)))
  change HasDerivAt (fun y : ℝ => y * Real.log (y / π))
    (1 * Real.log (x/π) + x * ((1/π)/(x/π))) x at h
  convert h using 1
  field_simp
  ring

/-- Relative entropy is differentiated before the balance equation is used. -/
theorem hasDerivAt_relativeEntropy_raw {p : ℝ → n → ℝ} {v : n → ℝ} {t : ℝ}
    (π : n → ℝ) (hπ : ∀ a, 0 < π a) (hp : ∀ a, 0 < p t a)
    (hd : ∀ a, HasDerivAt (fun s => p s a) (v a) t) :
    HasDerivAt (fun s => relativeEntropy (p s) π)
      (∑ a, (1 + Real.log (ratio (p t) π a)) * v a) t := by
  apply HasDerivAt.fun_sum
  intro a _
  simpa only [ratio, Function.comp_def] using
    (hasDerivAt_relative_term (hp a) (hπ a)).comp t (hd a)

/-- Equations (4.55)--(4.56) in conductance form, valid also at zero-rate edges.
The scalar flow equation is an input here; the matrix specialization below
separately discharges it from the original Lindblad derivative. -/
theorem hasDerivAt_relativeEntropy {p : ℝ → n → ℝ} {t : ℝ}
    (γ : n → n → ℝ) (π : n → ℝ) (hbal : Balanced γ π)
    (hπ : ∀ a, 0 < π a) (hp : ∀ a, 0 < p t a)
    (hd : ∀ a, HasDerivAt (fun s => p s a) (∑ b, current γ (p t) a b) t) :
    HasDerivAt (fun s => relativeEntropy (p s) π) (-dissipation γ π (p t)) t := by
  have h := hasDerivAt_relativeEntropy_raw π hπ hp hd
  rw [InformationTransport.weighted_current_symmetry _ _ (current_antisymm γ (p t))] at h
  have he (a b : n) :
      current γ (p t) a b * ((1 + Real.log (ratio (p t) π a)) -
        (1 + Real.log (ratio (p t) π b))) =
      -(conductance γ π a b * (ratio (p t) π a - ratio (p t) π b) *
        (Real.log (ratio (p t) π a) - Real.log (ratio (p t) π b))) := by
    rw [current_factor hbal (p t) hπ a b]
    ring
  simpa only [he, Finset.sum_neg_distrib, mul_neg, dissipation] using h

/-- The derivative sign is a proved consequence of nonnegative rates and
detailed balance, not of antisymmetry alone. -/
theorem relativeEntropy_deriv_nonpos {p : ℝ → n → ℝ} {t : ℝ}
    (γ : n → n → ℝ) (π : n → ℝ) (hbal : Balanced γ π)
    (hγ : ∀ a b, 0 ≤ γ a b) (hπ : ∀ a, 0 < π a) (hp : ∀ a, 0 < p t a)
    (hd : ∀ a, HasDerivAt (fun s => p s a) (∑ b, current γ (p t) a b) t) :
    deriv (fun s => relativeEntropy (p s) π) t ≤ 0 := by
  rw [(hasDerivAt_relativeEntropy γ π hbal hπ hp hd).deriv]
  exact neg_nonpos.mpr (dissipation_nonneg γ π (p t) hγ hπ hp)

/-- Given a positive actual solution on a convex time set, relative entropy
is nonincreasing there. Derivatives are assumed on that set, including any
endpoints; no global positive solution is manufactured by this theorem. -/
theorem relativeEntropy_antitoneOn (D : Set ℝ) (hD : Convex ℝ D)
    (γ : ℝ → n → n → ℝ) (π : n → ℝ) (p : ℝ → n → ℝ)
    (hπ : ∀ a, 0 < π a) (hγ : ∀ t ∈ D, ∀ a b, 0 ≤ γ t a b)
    (hbal : ∀ t ∈ D, Balanced (γ t) π) (hp : ∀ t ∈ D, ∀ a, 0 < p t a)
    (hd : ∀ t ∈ D, ∀ a, HasDerivAt (fun s => p s a) (∑ b, current (γ t) (p t) a b) t) :
    AntitoneOn (fun t => relativeEntropy (p t) π) D := by
  have h (t : ℝ) (ht : t ∈ D) := hasDerivAt_relativeEntropy
    (γ t) π (hbal t ht) hπ (hp t ht) (hd t ht)
  apply antitoneOn_of_deriv_nonpos hD
  · intro t ht
    exact (h t ht).continuousAt.continuousWithinAt
  · intro t ht
    exact (h t (interior_subset ht)).differentiableAt.differentiableWithinAt
  · intro t ht
    exact relativeEntropy_deriv_nonpos (γ t) π (hbal t (interior_subset ht))
      (hγ t (interior_subset ht)) hπ (hp t (interior_subset ht)) (hd t (interior_subset ht))

/-- The positive reference has zero relative entropy against itself. -/
theorem relativeEntropy_self (π : n → ℝ) (hπ : ∀ a, 0 < π a) :
    relativeEntropy π π = 0 := by
  simp [relativeEntropy, ratio, ne_of_gt (hπ _)]

/-- At equal reference and current distributions every dissipation edge vanishes. -/
theorem dissipation_self (γ : n → n → ℝ) (π : n → ℝ) (hπ : ∀ a, 0 < π a) :
    dissipation γ π π = 0 := by
  simp [dissipation, ratio, ne_of_gt (hπ _)]

/-- Flux cost on active edges only. The zero-rate branch is explicitly zero;
it is not a reliance on totalized log(0/0). -/
def activeFluxCost (γ : n → n → ℝ) (p : n → ℝ) (a b : n) : ℝ :=
  if γ a b = 0 then 0 else current γ p a b *
    Real.log ((γ a b * p b) / (γ b a * p a))

omit [Fintype n] in
/-- A zero transition has a zero reverse transition under positive detailed balance. -/
theorem zero_rate_iff {γ : n → n → ℝ} {π : n → ℝ}
    (hbal : Balanced γ π) (hπ : ∀ a, 0 < π a) (a b : n) :
    γ a b = 0 ↔ γ b a = 0 := by
  constructor
  · intro h0
    have h := hbal a b
    rw [h0, zero_mul] at h
    exact (mul_eq_zero.mp h.symm).resolve_right (ne_of_gt (hπ a))
  · intro h0
    have h := hbal a b
    rw [h0, zero_mul] at h
    exact (mul_eq_zero.mp h).resolve_right (ne_of_gt (hπ b))

omit [Fintype n] in
/-- Both fluxes inside the active logarithm are genuinely positive. -/
theorem active_fluxes_positive {γ : n → n → ℝ} {π : n → ℝ}
    (hbal : Balanced γ π) (hγ : ∀ a b, 0 ≤ γ a b) (hπ : ∀ a, 0 < π a)
    (p : n → ℝ) (hp : ∀ a, 0 < p a) (a b : n) (ha : γ a b ≠ 0) :
    0 < γ a b * p b ∧ 0 < γ b a * p a := by
  have hb : γ b a ≠ 0 := fun h => ha ((zero_rate_iff hbal hπ a b).mpr h)
  exact ⟨mul_pos (lt_of_le_of_ne (hγ a b) (Ne.symm ha)) (hp b),
    mul_pos (lt_of_le_of_ne (hγ b a) (Ne.symm hb)) (hp a)⟩

omit [Fintype n] in
/-- The literal active flux-ratio cost equals the nonsingular conductance cost. -/
theorem activeFluxCost_eq_edge {γ : n → n → ℝ} {π : n → ℝ}
    (hbal : Balanced γ π) (hγ : ∀ a b, 0 ≤ γ a b) (hπ : ∀ a, 0 < π a)
    (p : n → ℝ) (hp : ∀ a, 0 < p a) (a b : n) :
    activeFluxCost γ p a b = conductance γ π a b * (ratio p π a - ratio p π b) *
      (Real.log (ratio p π a) - Real.log (ratio p π b)) := by
  by_cases h0 : γ a b = 0
  · simp [activeFluxCost, conductance, h0]
  · have hc : conductance γ π a b ≠ 0 :=
      ne_of_gt (mul_pos (lt_of_le_of_ne (hγ a b) (Ne.symm h0)) (hπ b))
    have hf : γ a b * p b = conductance γ π a b * ratio p π b :=
      (flux_factor γ π p hπ a b).symm
    have hr : γ b a * p a = conductance γ π a b * ratio p π a := by
      rw [conductance_symm hbal a b, flux_factor γ π p hπ b a]
    have hquot : (γ a b * p b) / (γ b a * p a) = ratio p π b / ratio p π a := by
      rw [hf, hr]
      field_simp
    simp only [activeFluxCost, h0, ite_false, hquot,
      Real.log_div (ne_of_gt (ratio_pos hp hπ b)) (ne_of_gt (ratio_pos hp hπ a))]
    rw [current_factor hbal p hπ a b]
    ring

/-- Exact correspondence with equation (4.55), using the explicit active-edge convention. -/
theorem dissipation_eq_activeFlux {γ : n → n → ℝ} {π : n → ℝ}
    (hbal : Balanced γ π) (hγ : ∀ a b, 0 ≤ γ a b) (hπ : ∀ a, 0 < π a)
    (p : n → ℝ) (hp : ∀ a, 0 < p a) :
    dissipation γ π p = (1/2 : ℝ) * ∑ a, ∑ b, activeFluxCost γ p a b := by
  simp only [activeFluxCost_eq_edge hbal hγ hπ p hp, dissipation]

/-- Actual relative-entropy derivative in the source's flux-ratio form,
with zero edges omitted by definition and active logarithms proved valid. -/
theorem hasDerivAt_relativeEntropy_flux {p : ℝ → n → ℝ} {t : ℝ}
    (γ : n → n → ℝ) (π : n → ℝ) (hbal : Balanced γ π)
    (hγ : ∀ a b, 0 ≤ γ a b) (hπ : ∀ a, 0 < π a) (hp : ∀ a, 0 < p t a)
    (hd : ∀ a, HasDerivAt (fun s => p s a) (∑ b, current γ (p t) a b) t) :
    HasDerivAt (fun s => relativeEntropy (p s) π)
      (-(1/2 : ℝ) * ∑ a, ∑ b, activeFluxCost γ (p t) a b) t := by
  have h := hasDerivAt_relativeEntropy γ π hbal hπ hp hd
  simpa only [dissipation_eq_activeFlux hbal hγ hπ (p t) hp, neg_mul] using h

/-- A scalar relative-entropy term lies above its tangent mass difference. -/
theorem relative_term_lower_bound {p π : ℝ} (hp : 0 < p) (hπ : 0 < π) :
    p - π ≤ p * Real.log (p/π) := by
  have h := Real.log_le_sub_one_of_pos (div_pos hπ hp)
  have hl : Real.log (π/p) = -Real.log (p/π) := by
    rw [Real.log_div (ne_of_gt hπ) (ne_of_gt hp),
      Real.log_div (ne_of_gt hp) (ne_of_gt hπ)]
    ring
  rw [hl] at h
  have hm := mul_le_mul_of_nonneg_left h (le_of_lt hp)
  have hv : p * (π/p-1) = π-p := by field_simp; ring
  rw [hv] at hm
  nlinarith

/-- Gibbs nonnegativity for positive finite probability vectors. -/
theorem relativeEntropy_nonneg (p π : n → ℝ)
    (hp : ∀ a, 0 < p a) (hπ : ∀ a, 0 < π a)
    (hpsum : ∑ a, p a = 1) (hπsum : ∑ a, π a = 1) :
    0 ≤ relativeEntropy p π := by
  have h := Finset.sum_le_sum (s := Finset.univ)
    (fun a _ => relative_term_lower_bound (hp a) (hπ a))
  simpa only [Finset.sum_sub_distrib, hpsum, hπsum, sub_self, relativeEntropy, ratio] using h

/-- Dissipation vanishes exactly when relative densities agree on each
positive-rate edge. Reducible rate networks do not imply a unique equilibrium. -/
theorem dissipation_zero_iff (γ : n → n → ℝ) (π p : n → ℝ)
    (hγ : ∀ a b, 0 ≤ γ a b) (hπ : ∀ a, 0 < π a) (hp : ∀ a, 0 < p a) :
    dissipation γ π p = 0 ↔ ∀ a b, 0 < γ a b → ratio p π a = ratio p π b := by
  constructor
  · intro h a b hab
    have hs : (∑ a, ∑ b, conductance γ π a b * (ratio p π a - ratio p π b) *
        (Real.log (ratio p π a) - Real.log (ratio p π b))) = 0 := by
      unfold dissipation at h
      linarith
    have ha := (Finset.sum_eq_zero_iff_of_nonneg (fun a _ => Finset.sum_nonneg
      (fun b _ => edge_nonneg γ π p hγ hπ hp a b))).mp hs a (Finset.mem_univ a)
    have he := (Finset.sum_eq_zero_iff_of_nonneg
      (fun b _ => edge_nonneg γ π p hγ hπ hp a b)).mp ha b (Finset.mem_univ b)
    rw [mul_assoc] at he
    have hc : conductance γ π a b ≠ 0 := ne_of_gt (mul_pos hab (hπ b))
    exact (log_difference_product_eq_zero_iff (ratio_pos hp hπ a) (ratio_pos hp hπ b)).mp
      ((mul_eq_zero.mp he).resolve_left hc)
  · intro h
    unfold dissipation
    have hs : (∑ a, ∑ b, conductance γ π a b * (ratio p π a - ratio p π b) *
        (Real.log (ratio p π a) - Real.log (ratio p π b))) = 0 := by
      apply Finset.sum_eq_zero
      intro a _
      apply Finset.sum_eq_zero
      intro b _
      by_cases h0 : γ a b = 0
      · simp [conductance, h0]
      · rw [h a b (lt_of_le_of_ne (hγ a b) (Ne.symm h0)), sub_self, mul_zero, zero_mul]
    rw [hs, mul_zero]

/-- On a complete positive-rate network, normalized zero dissipation identifies
the reference distribution. The edge-positivity condition is not dropped. -/
theorem zero_dissipation_eq_reference [Nonempty n] (γ : n → n → ℝ) (π p : n → ℝ)
    (hγ : ∀ a b, 0 ≤ γ a b) (hpositive : ∀ a b, a ≠ b → 0 < γ a b)
    (hπ : ∀ a, 0 < π a) (hp : ∀ a, 0 < p a)
    (hpsum : ∑ a, p a = 1) (hπsum : ∑ a, π a = 1)
    (hd : dissipation γ π p = 0) : p = π := by
  classical
  have he := (dissipation_zero_iff γ π p hγ hπ hp).mp hd
  have hall (a b : n) : ratio p π a = ratio p π b := by
    by_cases h : a = b
    · rw [h]
    · exact he a b (hpositive a b h)
  let a : n := Classical.arbitrary n
  have hrep (b : n) : p b = ratio p π a * π b := by
    exact (div_eq_iff (ne_of_gt (hπ b))).mp (hall b a)
  have hr : ratio p π a = 1 := by
    calc
      _ = ratio p π a * (∑ b, π b) := by rw [hπsum, mul_one]
      _ = ∑ b, p b := by simp only [Finset.mul_sum, ← hrep]
      _ = 1 := hpsum
  funext b
  rw [hrep b, hr, one_mul]

variable [DecidableEq n]

/-- The detailed-balance theorem applied to the original density-matrix flow.
No scalar population equation is included as a separate hypothesis. -/
theorem hasDerivAt_matrix_relativeEntropy {γ : n → n → ℝ}
    {ρ : ℝ → Matrix n n ℂ} {t : ℝ} (π : n → ℝ)
    (hγ : ∀ a b, 0 ≤ γ a b) (hbal : Balanced γ π) (hπ : ∀ a, 0 < π a)
    (hp : ∀ a, 0 < population (ρ t) a)
    (hρ : HasDerivAt ρ (generator γ (ρ t)) t) :
    HasDerivAt (fun s => relativeEntropy (population (ρ s)) π)
      (-dissipation γ π (population (ρ t))) t :=
  hasDerivAt_relativeEntropy γ π hbal hπ hp (hasDerivAt_population hγ hρ)

/-- Nonpositive relative-entropy derivative from actual Lindblad evolution. -/
theorem matrix_relativeEntropy_deriv_nonpos {γ : n → n → ℝ}
    {ρ : ℝ → Matrix n n ℂ} {t : ℝ} (π : n → ℝ)
    (hγ : ∀ a b, 0 ≤ γ a b) (hbal : Balanced γ π) (hπ : ∀ a, 0 < π a)
    (hp : ∀ a, 0 < population (ρ t) a)
    (hρ : HasDerivAt ρ (generator γ (ρ t)) t) :
    deriv (fun s => relativeEntropy (population (ρ s)) π) t ≤ 0 :=
  relativeEntropy_deriv_nonpos γ π hbal hγ hπ hp (hasDerivAt_population hγ hρ)

end KomorebiPhysics.DetailedBalance
