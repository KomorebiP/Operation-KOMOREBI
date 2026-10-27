module
public import Euler.RestrictedHigherDerivatives
public import Euler.LocalAnalyticTools
public import Mathlib.Analysis.Calculus.IteratedDeriv.Lemmas
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

/-- The top surviving residue coefficient becomes a constant unit Hasse series.
This needs no Weierstrass preparation theorem. -/
lemma lastOdd_top_hasse_red {f:Series} {d:ℕ} (hd:LastOdd f d) :
    PowerSeries.map red (hasseSeries d f)=1 := by
  ext n
  rw [coeff_map,coeff_hasseSeries,map_mul,map_natCast]
  cases n with
  | zero => simpa only [Nat.zero_add,Nat.choose_self,Nat.cast_one,one_mul,coeff_one,ite_true] using hd.1
  | succ n =>
    rw [hd.2 _ (by omega),mul_zero]
    simp

lemma lastOdd_top_jet_norm {f:Series} (hf:Restricted f) {d:ℕ}
    (hd:LastOdd f d) (x:D) : ‖rjet d f x‖=1 := by
  exact restricted_norm_one_of_map (restricted_hasseSeries hf d) (lastOdd_top_hasse_red hd) x

/-- Exact ordinary top-derivative norm, with the factorial retained. -/
theorem lastOdd_top_iteratedDeriv_norm {f:Series} (hf:Restricted f) {d:ℕ}
    (hd:LastOdd f d) (x:D) :
    ‖iteratedDeriv d (qeval f) (x:ℚ_[2])‖=‖(d.factorial:ℚ_[2])‖ := by
  rw [iteratedDeriv_qeval hf,norm_mul]
  have h : ‖(rjet d f x:ℚ_[2])‖=1 := lastOdd_top_jet_norm hf hd x
  rw [h,mul_one]

theorem lastOdd_top_iteratedDeriv_ne_zero {f:Series} (hf:Restricted f) {d:ℕ}
    (hd:LastOdd f d) (x:D) : iteratedDeriv d (qeval f) (x:ℚ_[2])≠0 := by
  intro hz
  have hn:=lastOdd_top_iteratedDeriv_norm hf hd x
  rw [hz,norm_zero] at hn
  exact (norm_ne_zero_iff.mpr (by exact_mod_cast Nat.factorial_ne_zero d)) hn.symm

/-- All-order chain rule on the integral disc, with no global differentiability
claim outside that disc and no real/complex-only theorem. -/
theorem iteratedDeriv_dyadic_affine {f:Series} (hf:Restricted f)
    (a s:D) (n:ℕ) (x:D) :
    iteratedDeriv n (fun y:ℚ_[2]=>qeval f ((a:ℚ_[2])+(s:ℚ_[2])*y)) (x:ℚ_[2])=
      (s:ℚ_[2])^n*iteratedDeriv n (qeval f) ((a+s*x:D):ℚ_[2]) := by
  induction n generalizing x with
  | zero => simp
  | succ n ih =>
    have he : iteratedDeriv n (fun y:ℚ_[2]=>qeval f ((a:ℚ_[2])+(s:ℚ_[2])*y))
        =ᶠ[𝓝 (x:ℚ_[2])] (fun y:ℚ_[2]=>
          (s:ℚ_[2])^n*iteratedDeriv n (qeval f) ((a:ℚ_[2])+(s:ℚ_[2])*y)) := by
      apply eventuallyEq_of_eq_on_dyadic
      intro z
      simpa only [PadicInt.coe_add,PadicInt.coe_mul] using ih z
    have ha : HasDerivAt (fun y:ℚ_[2] => (a:ℚ_[2])+(s:ℚ_[2])*y) (s:ℚ_[2]) (x:ℚ_[2]) := by
      simpa using (((hasDerivAt_id (x:ℚ_[2])).const_mul (s:ℚ_[2])).const_add (a:ℚ_[2]))
    have ht:=hasDerivAt_iteratedDeriv_qeval hf n (a+s*x)
    have hcomp:=ht.comp (x:ℚ_[2]) ha
    have hscaled:=(hcomp.const_mul ((s:ℚ_[2])^n)).congr_of_eventuallyEq he
    rw [iteratedDeriv_succ,hscaled.deriv,iteratedDeriv_qeval hf]
    rw [pow_succ]
    ring

/-- An exact scaled analytic chart transports every derivative order, preserving
both the coordinate radius and removed coefficient content. -/
theorem restricted_scaled_iteratedDeriv {g f:Series}
    (hg:Restricted g) (hf:Restricted f) (a s c:D)
    (he:∀y:D,reval g (a+s*y)=c*reval f y) (n:ℕ) (x:D) :
    (s:ℚ_[2])^n*iteratedDeriv n (qeval g) ((a+s*x:D):ℚ_[2])=
      (c:ℚ_[2])*iteratedDeriv n (qeval f) (x:ℚ_[2]) := by
  have hfun : (fun y:ℚ_[2]=>qeval g ((a:ℚ_[2])+(s:ℚ_[2])*y))
      =ᶠ[𝓝 (x:ℚ_[2])] (fun y:ℚ_[2]=>(c:ℚ_[2])*qeval f y) := by
    apply eventuallyEq_of_eq_on_dyadic
    intro y
    have hh:=congrArg (fun z:D=>(z:ℚ_[2])) (he y)
    simpa only [PadicInt.coe_mul,PadicInt.coe_add,coe_reval hg,coe_reval hf] using hh
  have hh:=hfun.iteratedDeriv_eq n
  rw [iteratedDeriv_dyadic_affine hg,iteratedDeriv_scaled_qeval hf] at hh
  rw [iteratedDeriv_qeval hf]
  simpa only [mul_assoc] using hh

end Komorebi.Euler
