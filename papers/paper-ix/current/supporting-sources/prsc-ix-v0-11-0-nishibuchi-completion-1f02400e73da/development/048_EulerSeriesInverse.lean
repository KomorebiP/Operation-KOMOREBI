module
public import RatioSeriesSupport
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.EulerSeriesInverse
open PowerSeries DworkAlgebra DworkClosure HurwitzDworkClosure
variable (p : ℕ) [Fact p.Prime]

/-- Actual coefficient support, including the constant coefficient. -/
def Supported (N : ℕ) (f : PowerSeries ℚ_[p]) : Prop :=
  ∀ d, ¬N∣d → coeff d f=0

theorem supported_zero (N : ℕ) : Supported N (0 : PowerSeries ℚ_[p]) := by
  intro d _; simp

theorem supported_constant (N : ℕ) (a : ℚ_[p]) : Supported N (C a) := by
  intro d hd
  have hn : d≠0 := by intro h; subst d; exact hd (dvd_zero _)
  simp [coeff_C, hn]

theorem supported_add {N : ℕ} {f g : PowerSeries ℚ_[p]}
    (hf : Supported N f) (hg : Supported N g) : Supported N (f+g) := by
  intro d hd; simp [hf d hd, hg d hd]

theorem supported_sub {N : ℕ} {f g : PowerSeries ℚ_[p]}
    (hf : Supported N f) (hg : Supported N g) : Supported N (f-g) := by
  intro d hd; simp [hf d hd, hg d hd]

theorem supported_mul {N : ℕ} {f g : PowerSeries ℚ_[p]}
    (hf : Supported N f) (hg : Supported N g) : Supported N (f*g) := by
  intro d hd
  rw [coeff_mul]
  apply Finset.sum_eq_zero
  intro ij hij
  have he := Finset.mem_antidiagonal.mp hij
  by_cases hi : N∣ij.1
  · have hj : ¬N∣ij.2 := by intro h; exact hd (he ▸ dvd_add hi h)
    rw [hg ij.2 hj, mul_zero]
  · rw [hf ij.1 hi, zero_mul]

/-- Full normalized differential flatness in the original power-series variable. -/
def Flat (f : PowerSeries ℚ_[p]) : Prop :=
  DworkClosure.flat (derivative ℚ_[p]) p (integralSeries p) f

theorem flat_zero : Flat p 0 := by
  intro s; rw [map_zero]; exact zero_mem _

theorem flat_constant (a : ℚ_[p]) (ha : a∈PadicInt.subring p) : Flat p (C a) := by
  apply WeightedDworkTransfer.flat_of_log_weighted
  rw [subst_C]
  exact WeightedAmice.weighted_constant p ha

theorem flat_add {f g : PowerSeries ℚ_[p]} (hf : Flat p f) (hg : Flat p g) : Flat p (f+g) := by
  intro s; rw [map_add]; exact add_mem (hf s) (hg s)

theorem flat_sub {f g : PowerSeries ℚ_[p]} (hf : Flat p f) (hg : Flat p g) : Flat p (f-g) := by
  intro s; rw [map_sub]; exact sub_mem (hf s) (hg s)

theorem flat_mul {f g : PowerSeries ℚ_[p]} (hf : Flat p f) (hg : Flat p g) : Flat p (f*g) :=
  HurwitzDworkClosure.flat_product p hf hg

/-- Coefficientwise solution of (t D + c)y=f. No invertibility premise is hidden. -/
def solve (c : ℕ) (f : PowerSeries ℚ_[p]) : PowerSeries ℚ_[p] :=
  mk (fun d => coeff d f / ((d+c:ℕ):ℚ_[p]))

@[simp] theorem solve_coeff (c d : ℕ) (f : PowerSeries ℚ_[p]) :
    coeff d (solve p c f)=coeff d f/((d+c:ℕ):ℚ_[p]) := coeff_mk _ _

def euler (c : ℕ) (f : PowerSeries ℚ_[p]) : PowerSeries ℚ_[p] :=
  X*derivative ℚ_[p] f+C (c:ℚ_[p])*f

theorem euler_coeff (c d : ℕ) (f : PowerSeries ℚ_[p]) :
    coeff d (euler p c f)=((d+c:ℕ):ℚ_[p])*coeff d f := by
  rw [euler, map_add, coeff_C_mul]
  cases d with
  | zero => simp
  | succ d => rw [coeff_succ_X_mul, coeff_derivative]; push_cast; ring

theorem euler_solve (c : ℕ) (hc : 0<c) (f : PowerSeries ℚ_[p]) :
    euler p c (solve p c f)=f := by
  ext d
  rw [euler_coeff, solve_coeff]
  have hn : ((d+c:ℕ):ℚ_[p])≠0 := Nat.cast_ne_zero.mpr (by omega)
  exact mul_div_cancel₀ _ hn

theorem solve_euler (c : ℕ) (hc : 0<c) (f : PowerSeries ℚ_[p]) :
    solve p c (euler p c f)=f := by
  ext d
  rw [solve_coeff, euler_coeff]
  have hn : ((d+c:ℕ):ℚ_[p])≠0 := Nat.cast_ne_zero.mpr (by omega)
  exact mul_div_cancel_left₀ _ hn

theorem solve_supported {N c : ℕ} {f : PowerSeries ℚ_[p]}
    (hf : Supported N f) : Supported N (solve p c f) := by
  intro d hd; rw [solve_coeff, hf d hd, zero_div]

theorem solve_constant_zero {c : ℕ} {f : PowerSeries ℚ_[p]} (hf : constantCoeff f=0) :
    constantCoeff (solve p c f)=0 := by
  rw [←coeff_zero_eq_constantCoeff, solve_coeff, coeff_zero_eq_constantCoeff, hf, zero_div]

/-- The actual solution is Hurwitz-integral because its supported pivots are genuine p-adic units. -/
theorem solve_integral (c : ℕ) (hc : ¬p∣c) (f : PowerSeries ℚ_[p])
    (hf : f∈integralSeries p) (hs : Supported p f) : solve p c f∈integralSeries p := by
  intro d
  by_cases hd : p∣d
  · obtain ⟨u,hu⟩ := EulerDefect.euler_pivot_unit p c d hc hd
    have hi : (((d+c:ℕ):ℚ_[p]))⁻¹ = ((u⁻¹ : ℤ_[p]ˣ):ℤ_[p]) := by
      have hh := congrArg (fun x:ℤ_[p] => (x:ℚ_[p])) hu
      change ((u:ℤ_[p]):ℚ_[p])=((d+c:ℕ):ℚ_[p]) at hh
      rw [←hh]
      simp
    have hq : EGF.decode (solve p c f) d = EGF.decode f d * ((d+c:ℕ):ℚ_[p])⁻¹ := by
      simp only [EGF.decode, solve_coeff, div_eq_mul_inv]; ring
    rw [hq, hi]
    exact mul_mem (hf d) (show (((u⁻¹:ℤ_[p]ˣ):ℤ_[p]):ℚ_[p])∈PadicInt.subring p from
      ((u⁻¹:ℤ_[p]ˣ):ℤ_[p]).property)
  · simp [EGF.decode, solve_coeff, hs d hd]

/-- Genuine integral lifts of every Hurwitz coefficient of a series. -/
def lift (f : PowerSeries ℚ_[p]) (hf : f∈integralSeries p) (d : ℕ) : ℤ_[p] :=
  ⟨EGF.decode f d, hf d⟩

theorem encode_lift (f : PowerSeries ℚ_[p]) (hf : f∈integralSeries p) :
    encodeIntegral p (lift p f hf)=f := EGF.encode_decode f

theorem euler_lift_encoding (c : ℕ) (f : PowerSeries ℚ_[p]) (hf : f∈integralSeries p) :
    encodeIntegral p (EulerDefect.eulerOperator c (lift p f hf)) = euler p c f := by
  ext d
  simp only [encodeIntegral, EGF.encode, coeff_mk, EulerDefect.eulerOperator, euler_coeff,
    lift, EGF.decode, Nat.cast_add, PadicInt.coe_mul, PadicInt.coe_natCast]
  have hn : (d.factorial:ℚ_[p])≠0 := Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero d)
  field_simp

/-- Full flatness is reflected through the actual nonsingular Euler inverse. -/
theorem solve_flat (c : ℕ) (hc : ¬p∣c) (f : PowerSeries ℚ_[p])
    (hf : Flat p f) (hs : Supported p f) : Flat p (solve p c f) := by
  have hcpos : 0<c := by by_contra h; have : c=0 := by omega; subst c; exact hc (dvd_zero _)
  have hi := solve_integral p c hc f (hf 0) hs
  rw [←encode_lift p (solve p c f) hi]
  apply (flat_encode_iff p _).mpr
  apply EulerDefect.flat_of_euler_flat p c hc
  · intro d hd
    apply Subtype.ext
    change EGF.decode (solve p c f) d = 0
    simp [EGF.decode, solve_supported p hs d hd]
  · apply (flat_encode_iff p _).mp
    rw [euler_lift_encoding, euler_solve p c hcpos]
    exact hf

end KomorebiPaperIX.EulerSeriesInverse
