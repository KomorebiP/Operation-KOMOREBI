module
public import EulerSeriesInverse
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.RiccatiFlatPropagation
open PowerSeries DworkAlgebra HurwitzDworkClosure EulerSeriesInverse
variable (p : ℕ) [Fact p.Prime]

/-- Nonlinear right hand side of the actual centered ratio equation. -/
def forcing (c : ℕ) (q y : PowerSeries ℚ_[p]) : PowerSeries ℚ_[p] :=
  C (c:ℚ_[p])*q+y*q-y*y

/-- Explicit Picard iterations in formal coefficients, starting from zero. -/
def picard (c : ℕ) (q : PowerSeries ℚ_[p]) : ℕ → PowerSeries ℚ_[p]
  | 0 => 0
  | r+1 => solve p c (forcing p c q (picard c q r))

theorem forcing_difference (c : ℕ) (q y z : PowerSeries ℚ_[p]) :
    forcing p c q y-forcing p c q z=(y-z)*(q-y-z) := by
  unfold forcing
  ring

theorem picard_constant (c : ℕ) (q : PowerSeries ℚ_[p])
    (hq : constantCoeff q=0) (r : ℕ) : constantCoeff (picard p c q r)=0 := by
  induction r with
  | zero => simp [picard]
  | succ r ih =>
    rw [picard]
    apply solve_constant_zero
    simp [forcing, hq, ih]

theorem picard_supported (c : ℕ) (q : PowerSeries ℚ_[p]) (hq : Supported p p q) (r : ℕ) :
    Supported p p (picard p c q r) := by
  induction r with
  | zero => exact supported_zero p p
  | succ r ih =>
    rw [picard]
    apply solve_supported
    exact supported_sub p
      (supported_add p (supported_mul p (supported_constant p p _) hq) (supported_mul p ih hq))
      (supported_mul p ih ih)

theorem picard_flat (c : ℕ) (hc : ¬p∣c) (q : PowerSeries ℚ_[p])
    (hq : Flat p q) (hs : Supported p p q) (r : ℕ) : Flat p (picard p c q r) := by
  induction r with
  | zero => exact flat_zero p
  | succ r ih =>
    rw [picard]
    apply solve_flat p c hc
    · exact flat_sub p
        (flat_add p (flat_mul p (flat_constant p _ (natCast_mem _ _)) hq) (flat_mul p ih hq))
        (flat_mul p ih ih)
    · have hz := picard_supported p c q hs r
      exact supported_sub p
        (supported_add p (supported_mul p (supported_constant p p _) hs) (supported_mul p hz hs))
        (supported_mul p hz hz)

/-- Multiplying a zero constant series raises a proved finite vanishing prefix by one. -/
theorem product_vanishing_prefix (r n : ℕ) (f g : PowerSeries ℚ_[p])
    (hf : ∀ d≤r, coeff d f=0) (hg : constantCoeff g=0) (hn : n≤r+1) :
    coeff n (f*g)=0 := by
  rw [coeff_mul]
  apply Finset.sum_eq_zero
  intro ij hij
  have he := Finset.mem_antidiagonal.mp hij
  by_cases hi : ij.1≤r
  · rw [hf ij.1 hi, zero_mul]
  · have hj : ij.2=0 := by omega
    rw [hj, coeff_zero_eq_constantCoeff, hg, mul_zero]

/-- The iterates agree with the actual solution through degree r after r iterations. -/
theorem picard_matches (c : ℕ) (hc : 0<c) (q y : PowerSeries ℚ_[p])
    (hq : constantCoeff q=0) (hy : constantCoeff y=0)
    (he : euler p c y=forcing p c q y) (r d : ℕ) (hd : d≤r) :
    coeff d (picard p c q r)=coeff d y := by
  induction r generalizing d with
  | zero =>
    have hdz : d=0 := by omega
    rw [hdz, coeff_zero_eq_constantCoeff, hy]
    simp [picard]
  | succ r ih =>
    have hsolve : solve p c (forcing p c q y)=y := by rw [←he, solve_euler p c hc]
    rw [picard, ←hsolve, solve_coeff, solve_coeff]
    congr 1
    have hmul : coeff d (forcing p c q (picard p c q r)-forcing p c q y)=0 := by
      rw [forcing_difference]
      apply product_vanishing_prefix p r d
      · intro i hi
        rw [map_sub, ih i hi, sub_self]
      · simp only [map_sub, hq, hy, picard_constant p c q hq, sub_self]
      · exact hd
    exact sub_eq_zero.mp (by simpa only [map_sub] using hmul)

/-- Every normalized defect depends on a finite, explicitly bounded coefficient prefix. -/
theorem B_iterate_prefix (s n : ℕ) (f g : PowerSeries ℚ_[p])
    (h : ∀ d≤n+p^2*s, coeff d f=coeff d g) :
    EGF.decode ((B (derivative ℚ_[p]) p ^ s) f) n =
      EGF.decode ((B (derivative ℚ_[p]) p ^ s) g) n := by
  rw [decode_B_iterate, decode_B_iterate,
    DworkCriterion.defect_is_shifted_difference, DworkCriterion.defect_is_shifted_difference]
  congr 1
  apply Mahler.difference_eq_of_stencil
  intro r hr
  have hp := (Fact.out : p.Prime).pos
  have hp1 : 1≤p := by omega
  have he : p+p*(p-1)=p^2 := by
    have hh := Nat.sub_add_cancel hp1
    nlinarith
  have hm : r*(p*(p-1))≤s*(p*(p-1)) := Nat.mul_le_mul_right _ hr
  have hb : n+p*s+r*(p*(p-1))≤n+p^2*s := by nlinarith
  simp only [EGF.decode, h _ hb]

/-- Nonsingular Riccati propagation for a supplied actual solution. Its flatness is a conclusion. -/
theorem riccati_solution_flat (c : ℕ) (hc : ¬p∣c) (q y : PowerSeries ℚ_[p])
    (hq : Flat p q) (hs : Supported p p q)
    (hq0 : constantCoeff q=0) (hy0 : constantCoeff y=0)
    (he : euler p c y=forcing p c q y) : Flat p y := by
  have hcpos : 0<c := Nat.pos_of_ne_zero (by
    intro hz; apply hc; rw [hz]; exact dvd_zero _)
  intro s n
  have hm := B_iterate_prefix p s n (picard p c q (n+p^2*s)) y
    (picard_matches p c hcpos q y hq0 hy0 he (n+p^2*s))
  rw [←hm]
  exact picard_flat p c hc q hq hs (n+p^2*s) s n

end KomorebiPaperIX.RiccatiFlatPropagation
