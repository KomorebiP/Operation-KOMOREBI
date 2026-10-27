module
public import Euler.RestrictedAffine
public import Euler.RestrictedHigherDerivatives
public import Euler.TerminalNormalForm
public import Mathlib.Analysis.Calculus.Deriv.Add
public import Mathlib.Analysis.Calculus.Deriv.Comp
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

lemma restrictedAffine_map_red (f : Series) (a s : D) (hs : red s=0) :
    PowerSeries.map red (restrictedAffine f a s)=C (red (reval f a)) := by
  ext n
  rw [coeff_map,restrictedAffine_red f a s hs]
  simp only [coeff_C,Polynomial.coeff_C]

/-- A proper affine chart respects the genuine field derivative. -/
theorem restrictedAffine_deriv {f : Series} (hf : Restricted f) (a s x : D) (hs : ‖s‖<1) :
    deriv (qeval (restrictedAffine f a s)) (x:ℚ_[2])=
      deriv (qeval f) ((a+s*x:D):ℚ_[2])*(s:ℚ_[2]) := by
  have he : qeval (restrictedAffine f a s)=ᶠ[𝓝 (x:ℚ_[2])]
      (fun y:ℚ_[2] => qeval f ((a:ℚ_[2])+(s:ℚ_[2])*y)) := by
    apply eventuallyEq_of_eq_on_dyadic
    intro y
    have hs' : Restricted (restrictedAffine f a s) := restrictedAffine_restricted f a s hs
    rw [← coe_reval hs',restrictedAffine_reval hf,coe_reval hf]
    simp only [PadicInt.coe_add,PadicInt.coe_mul]
  have hd := (hasDerivAt_qeval hf (a+s*x)).differentiableAt.hasDerivAt
  simp only [PadicInt.coe_add,PadicInt.coe_mul] at hd
  have hi : HasDerivAt (fun y:ℚ_[2] => (a:ℚ_[2])+(s:ℚ_[2])*y) (s:ℚ_[2]) (x:ℚ_[2]) := by
    convert (hasDerivAt_const (x:ℚ_[2]) (a:ℚ_[2])).add
        ((hasDerivAt_id (x:ℚ_[2])).const_mul (s:ℚ_[2])) using 1 <;>
      first | rfl | simp only [zero_add,mul_one]
  have hc := hd.comp (x:ℚ_[2]) hi
  exact (hc.congr_of_eventuallyEq he).deriv

lemma restricted_norm_one_of_map {f : Series} (hf : Restricted f)
    (h : PowerSeries.map red f=1) (x : D) : ‖reval f x‖=1 := by
  have hv := reval_residue_polynomial hf 1 (1:Polynomial F₂) (by
    intro n
    rw [res_eq_red,← coeff_map,h]
    simp only [coeff_one,Polynomial.coeff_one]) x
  apply res_nonzero_norm_one
  have he : res (reval f x)=1 := by simpa using hv
  rw [he]
  decide

/-- An affine full binary coefficient certificate gives one global simple root. -/
theorem restricted_affine_atlas {f : Series} (hf : Restricted f) (c : F₂)
    (h : PowerSeries.map red f=X+C c) :
    ∃ α:D, reval f α=0 ∧
      ‖deriv (qeval f) (α:ℚ_[2])‖=1 ∧
      (∀ x:D, reval f x=0 ↔ x=α) ∧
      (∀ x:D, ‖reval f x‖=‖x-α‖) := by
  let p : Polynomial F₂ := Polynomial.X+Polynomial.C c
  have hp : ∀ n,res (coeff n f)=p.coeff n := by
    intro n
    rw [res_eq_red,← coeff_map,h]
    simp only [p,map_add,coeff_X,coeff_C,Polynomial.coeff_add,Polynomial.coeff_X,
      Polynomial.coeff_C,eq_comm]
  have hc : res (coeff 0 f)=c := by
    simpa [p] using hp 0
  let a : D := -coeff 0 f
  have ha : p.eval (res a)=0 := by
    simp only [p,a,Polynomial.eval_add,Polynomial.eval_X,Polynomial.eval_C,map_neg,hc,neg_add_cancel]
  have hd (x:F₂) : p.derivative.eval x=1 := by simp [p]
  obtain ⟨α,hα,hαr,_,hu⟩ := restricted_hensel_simple_residue hf p hp a ha
    (by rw [hd];decide)
  have hv (x:D) : res (reval f x)=res x+c := by
    simpa [p] using reval_residue_polynomial hf 1 p hp x
  have hroot (x:D) (hx : reval f x=0) : res x=res a := by
    have hvx := hv x
    rw [hx,map_zero] at hvx
    have he : res x = -c := eq_neg_of_add_eq_zero_left hvx.symm
    simpa only [a,map_neg,hc] using he
  refine ⟨α,hα,?_,?_,?_⟩
  · rw [deriv_qeval hf]
    change ‖rjet 1 f α‖=1
    apply res_nonzero_norm_one
    rw [res_rjet_one hf p hp,hd]
    decide
  · intro x
    constructor
    · intro hx
      exact hu x hx (hroot x hx)
    · rintro rfl
      exact hα
  · intro x
    by_cases he : res x=res α
    · exact restricted_root_distance hf p hp α x hα he (by rw [hd];decide)
    · have hval : res (reval f x)≠0 := by
        intro hz
        have h1:=hv x
        have h2:=hv α
        rw [hα,map_zero] at h2
        rw [hz] at h1
        exact he (add_right_cancel (h1.symm.trans h2))
      have hdist : res (x-α)≠0 := by simpa only [map_sub,sub_ne_zero] using he
      rw [res_nonzero_norm_one _ hval,res_nonzero_norm_one _ hdist]

end Komorebi.Euler
