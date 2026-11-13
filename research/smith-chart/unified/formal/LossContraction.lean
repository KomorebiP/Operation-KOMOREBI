import GraphCore
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

/-! Finite port mismatch from local branch laws and power. Author: Komorebi P.
Existence of physical grounded solutions is a separate positive-loss argument.
-/
namespace SmithLossContraction
open scoped BigOperators
variable {E : Type*} [Fintype E]

theorem port_power {V : Type*} [Fintype V] [DecidableEq V]
    (src dst : E → V) (i z : E → ℂ) (u : V → ℂ) (a b : V)
    (hi : ∀ n, SmithGraphCore.divergence src dst i n =
      SmithGraphCore.portInjection a b (1-(u a-u b)) n)
    (hu : ∀ e, u (src e)-u (dst e)=z e*i e) :
    4*(∑ e, (z e).re*Complex.normSq (i e)) =
      1-Complex.normSq (2*(u a-u b)-1) := by
  have hc : ∀ n, SmithGraphCore.divergence src dst (fun e => star (i e)) n =
      SmithGraphCore.portInjection a b (star (1-(u a-u b))) n := by
    intro n
    have hc : SmithGraphCore.divergence src dst (fun e => star (i e)) n =
        star (SmithGraphCore.divergence src dst i n) := by
      simp only [SmithGraphCore.divergence,star_sum,star_sub]
      apply Finset.sum_congr rfl
      intro e he
      split_ifs <;> simp
    rw [hc,hi]
    simp only [SmithGraphCore.portInjection,star_sub]
    split_ifs <;> simp
  have h := SmithGraphCore.port_green src dst (fun e => star (i e)) u a b
    (star (1-(u a-u b))) hc
  simp_rw [hu] at h
  have hr := congrArg Complex.re h
  have hr' : (∑ e, (z e).re*Complex.normSq (i e)) =
      ((u a-u b)*star (1-(u a-u b))).re := by
    calc
      _ = (∑ e, z e*i e*star (i e)).re := by
        rw [Complex.re_sum]
        apply Finset.sum_congr rfl
        intro e he
        simp only [Complex.mul_re,Complex.mul_im,Complex.star_def,
          Complex.conj_re,Complex.conj_im,Complex.normSq_apply]
        ring
      _ = _ := hr
  rw [hr']
  exact SmithPortPower.power_identity (u a-u b)

theorem finite_mismatch (d i j : E → ℂ) (a b : E → ℝ) (B : ℝ)
    (hB : 0 ≤ B) (ha : ∀ e, 0 ≤ a e) (hb : ∀ e, 0 ≤ b e)
    (hlocal : ∀ e, Complex.normSq (d e) ≤ 4*B*a e*b e) :
    Complex.normSq (∑ e, d e*i e*j e) ≤
      4*B*(∑ e, a e*Complex.normSq (i e))*(∑ e, b e*Complex.normSq (j e)) := by
  have hpoint (e : E) : ‖d e*i e*j e‖^2 ≤
      (4*B*a e*Complex.normSq (i e))*(b e*Complex.normSq (j e)) := by
    calc
      _ = Complex.normSq (d e)*Complex.normSq (i e)*Complex.normSq (j e) := by
        simp [Complex.normSq_eq_norm_sq,mul_pow]
      _ ≤ (4*B*a e*b e)*(Complex.normSq (i e)*Complex.normSq (j e)) := by
        nlinarith only [mul_le_mul_of_nonneg_right (hlocal e)
          (mul_nonneg (Complex.normSq_nonneg (i e)) (Complex.normSq_nonneg (j e)))]
      _ = _ := by ring
  have hcs := Finset.sum_sq_le_sum_mul_sum_of_sq_le_mul (Finset.univ : Finset E)
    (fun e _ => mul_nonneg (mul_nonneg (mul_nonneg (by norm_num) hB) (ha e))
      (Complex.normSq_nonneg (i e)))
    (fun e _ => mul_nonneg (hb e) (Complex.normSq_nonneg (j e)))
    (fun e _ => hpoint e)
  have hn : ‖∑ e, d e*i e*j e‖ ≤ ∑ e, ‖d e*i e*j e‖ := norm_sum_le _ _
  have hs := pow_le_pow_left₀ (norm_nonneg (∑ e, d e*i e*j e)) hn 2
  have hsum : (∑ e, 4*B*a e*Complex.normSq (i e)) =
      4*B*(∑ e, a e*Complex.normSq (i e)) := by simp [Finset.mul_sum,mul_assoc]
  rw [hsum] at hcs
  rw [Complex.normSq_eq_norm_sq]
  exact hs.trans (by simpa [mul_assoc] using hcs)

theorem power_to_port (d i j : E → ℂ) (a b : E → ℝ) (B : ℝ) (g gp : ℂ)
    (hB : 0 ≤ B) (ha : ∀ e, 0 ≤ a e) (hb : ∀ e, 0 ≤ b e)
    (hlocal : ∀ e, Complex.normSq (d e) ≤ 4*B*a e*b e)
    (hchange : gp-g=2*(∑ e, d e*i e*j e))
    (hpower : 4*(∑ e, a e*Complex.normSq (i e))=1-Complex.normSq g)
    (hpower' : 4*(∑ e, b e*Complex.normSq (j e))=1-Complex.normSq gp) :
    Complex.normSq (gp-g) ≤ B*(1-Complex.normSq g)*(1-Complex.normSq gp) := by
  have h := finite_mismatch d i j a b B hB ha hb hlocal
  rw [hchange]
  simp only [Complex.normSq_mul]
  norm_num
  calc
    4*Complex.normSq (∑ e, d e*i e*j e) ≤
        4*((4*B*(∑ e, a e*Complex.normSq (i e)))*(∑ e, b e*Complex.normSq (j e))) :=
      mul_le_mul_of_nonneg_left h (by norm_num)
    _ = B*(4*(∑ e, a e*Complex.normSq (i e)))*(4*(∑ e, b e*Complex.normSq (j e))) := by ring
    _ = _ := by rw [hpower,hpower']

theorem polynomial_disk_identity (g gp : ℂ) (B : ℝ) :
    let r := Complex.normSq g
    let A := 1+B*(1-r)
    Complex.normSq ((A:ℂ)*gp-g)-B*(1+B)*(1-r)^2 =
      A*(Complex.normSq (gp-g)-B*(1-r)*(1-Complex.normSq gp)) := by
  dsimp
  simp [Complex.normSq,Complex.mul_re,Complex.mul_im]
  ring

theorem graph_to_port {V : Type*} [Fintype V] [DecidableEq V]
    (src dst : E → V) (i j z w : E → ℂ) (u v : V → ℂ) (a b : V) (B : ℝ)
    (hB : 0 ≤ B) (hz : ∀ e, 0 ≤ (z e).re) (hw : ∀ e, 0 ≤ (w e).re)
    (hlocal : ∀ e, Complex.normSq (w e-z e) ≤ 4*B*(z e).re*(w e).re)
    (hi : ∀ n, SmithGraphCore.divergence src dst i n =
      SmithGraphCore.portInjection a b (1-(u a-u b)) n)
    (hj : ∀ n, SmithGraphCore.divergence src dst j n =
      SmithGraphCore.portInjection a b (1-(v a-v b)) n)
    (hu : ∀ e, u (src e)-u (dst e)=z e*i e)
    (hv : ∀ e, v (src e)-v (dst e)=w e*j e) :
    Complex.normSq ((2*(v a-v b)-1)-(2*(u a-u b)-1)) ≤
      B*(1-Complex.normSq (2*(u a-u b)-1))*(1-Complex.normSq (2*(v a-v b)-1)) := by
  have hc := SmithGraphCore.impedance_change src dst i j z w u v a b
    (1-(u a-u b)) (1-(v a-v b)) hi hj hu hv
  have hchange : (2*(v a-v b)-1)-(2*(u a-u b)-1) =
      2*(∑ e, (w e-z e)*i e*j e) := by rw [hc]; ring
  exact power_to_port (fun e => w e-z e) i j (fun e => (z e).re)
    (fun e => (w e).re) B _ _ hB hz hw hlocal hchange
    (port_power src dst i z u a b hi hu) (port_power src dst j w v a b hj hv)

theorem polynomial_disk (g gp : ℂ) (B : ℝ) (hB : 0 ≤ B)
    (hg : Complex.normSq g ≤ 1)
    (hport : Complex.normSq (gp-g) ≤ B*(1-Complex.normSq g)*(1-Complex.normSq gp)) :
    Complex.normSq (((1+B*(1-Complex.normSq g):ℝ):ℂ)*gp-g) ≤
      B*(1+B)*(1-Complex.normSq g)^2 := by
  have hA : 0 ≤ 1+B*(1-Complex.normSq g) := by positivity
  have h := mul_nonpos_of_nonneg_of_nonpos hA (sub_nonpos.mpr hport)
  rw [← polynomial_disk_identity] at h
  linarith

theorem one_percent_low_quality :
    ((1/100:ℝ)^2*((1-1/100)^2+1^2)/(4*(1-1/100)^3)) = 19801/388119600 := by norm_num

theorem one_percent_distance_majorant :
    (19801/388119600:ℝ) < (1/140)^2 := by norm_num

end SmithLossContraction
