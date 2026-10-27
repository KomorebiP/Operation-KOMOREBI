module
public import Euler.RestrictedHensel
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

/-- The first derivative of the kth Hasse coefficient series has the correct factorial factor. -/
lemma hasseSeries_one_coeff (f : PowerSeries D) (k n : ℕ) :
    coeff n (hasseSeries 1 (hasseSeries k f)) =
      (k+1:D)*coeff n (hasseSeries (k+1) f) := by
  simp only [coeff_hasseSeries, Nat.choose_one_right]
  have hb : (n+1)*Nat.choose (n+(k+1)) k =
      (k+1)*Nat.choose (n+(k+1)) (k+1) := by
    have h := Nat.choose_succ_right_eq (n+(k+1)) k
    have he : n+(k+1)-k=n+1 := by omega
    rw [he] at h
    simpa only [Nat.mul_comm] using h.symm
  have hd : (n+1:D)*(Nat.choose (n+(k+1)) k:D) =
      (k+1:D)*(Nat.choose (n+(k+1)) (k+1):D) := by exact_mod_cast hb
  rw [show n+1+k=n+(k+1) by omega]
  simpa only [mul_assoc, Nat.cast_add, Nat.cast_one] using
    congrArg (fun z : D => z*coeff (n+(k+1)) f) hd

lemma rjet_one_hasseSeries {f : PowerSeries D} (hf : Restricted f) (k : ℕ) (x : D) :
    rjet 1 (hasseSeries k f) x=(k+1:D)*rjet (k+1) f x := by
  simp only [rjet, reval, hasseSeries_one_coeff]
  simp only [mul_assoc]
  exact Summable.tsum_mul_left (k+1:D) (summable_reval (restricted_hasseSeries hf (k+1)) x)

/-- The evaluated coefficient derivative and the analytic derivative agree on a neighborhood
of every integral point of Q_2, not just at integer representatives. -/
lemma deriv_qeval_eventually {f : PowerSeries D} (hf : Restricted f) (x : D) :
    deriv (qeval f) =ᶠ[𝓝 (x:ℚ_[2])] qeval (hasseSeries 1 f) := by
  filter_upwards [Metric.ball_mem_nhds (x:ℚ_[2]) (by norm_num : (0:ℝ)<1)] with y hy
  have hd : ‖y-(x:ℚ_[2])‖<1 := by simpa only [Metric.mem_ball, dist_eq_norm] using hy
  have hint : ‖y‖≤1 := by
    calc
      ‖y‖=‖(y-(x:ℚ_[2]))+(x:ℚ_[2])‖ := by rw [sub_add_cancel]
      _ ≤ max ‖y-(x:ℚ_[2])‖ ‖(x:ℚ_[2])‖ := IsUltrametricDist.norm_add_le_max _ _
      _ ≤ 1 := max_le hd.le x.2
  let yy : D := ⟨y,hint⟩
  have h := deriv_qeval hf yy
  rw [← coe_reval (restricted_hasseSeries hf 1) yy]
  exact h

/-- The second analytic derivative, with no division by 2 in the dyadic integer ring. -/
theorem hasDerivAt_deriv_qeval {f : PowerSeries D} (hf : Restricted f) (x : D) :
    HasDerivAt (deriv (qeval f)) (2*((rjet 2 f x:D):ℚ_[2])) (x:ℚ_[2]) := by
  have h := (hasDerivAt_qeval (restricted_hasseSeries hf 1) x).congr_of_eventuallyEq
    (deriv_qeval_eventually hf x)
  rw [rjet_one_hasseSeries hf] at h
  convert h using 1 <;> first | rfl | norm_num
  exact Or.inl (PadicInt.coe_natCast (p:=2) 2).symm

lemma second_deriv_qeval {f : PowerSeries D} (hf : Restricted f) (x : D) :
    deriv (deriv (qeval f)) (x:ℚ_[2])=2*((rjet 2 f x:D):ℚ_[2]) :=
  (hasDerivAt_deriv_qeval hf x).deriv

/-- A triple-zero analytic jet would force the first three integral Hasse jets to vanish. -/
theorem analytic_triple_zero_implies_hasse {f : PowerSeries D}
    (hf : Restricted f) (x : D)
    (h0 : qeval f (x:ℚ_[2])=0)
    (h1 : deriv (qeval f) (x:ℚ_[2])=0)
    (h2 : deriv (deriv (qeval f)) (x:ℚ_[2])=0) :
    ∀ d : Fin 3, rjet d.val f x=0 := by
  have hz0 : rjet 0 f x=0 := by
    rw [rjet_zero]
    apply PadicInt.coe_eq_zero.mp
    rwa [coe_reval hf]
  have hz1 : rjet 1 f x=0 := by
    apply PadicInt.coe_eq_zero.mp
    rwa [deriv_qeval hf] at h1
  have hz2 : rjet 2 f x=0 := by
    rw [second_deriv_qeval hf] at h2
    have ht : (2:ℚ_[2])≠0 := by norm_num
    apply PadicInt.coe_eq_zero.mp
    exact (mul_eq_zero.mp h2).resolve_left ht
  intro d
  fin_cases d
  · exact hz0
  · exact hz1
  · exact hz2

/-- Modulus-2^k polynomial certificates rule out genuine analytic third-order vanishing. -/
theorem restricted_no_analytic_triple_of_residue {f : PowerSeries D}
    (hf : Restricted f) (k : ℕ) (p : Polynomial (ZMod (2^k)))
    (hc : ∀ n, redPow k (coeff n f)=p.coeff n)
    (hp : ∀ y, ¬ ∀ d : Fin 3, (Polynomial.hasseDeriv d.val p).eval y=0) :
    ∀ x : D, ¬ (qeval f (x:ℚ_[2])=0 ∧ deriv (qeval f) (x:ℚ_[2])=0 ∧
      deriv (deriv (qeval f)) (x:ℚ_[2])=0) := by
  intro x hx
  exact restricted_no_jet_zero_of_residue hf k 3 p hc hp x
    (analytic_triple_zero_implies_hasse hf x hx.1 hx.2.1 hx.2.2)

end Komorebi.Euler
