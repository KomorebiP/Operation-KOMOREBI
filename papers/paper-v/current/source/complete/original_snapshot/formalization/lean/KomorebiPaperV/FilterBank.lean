import KomorebiPaperV.ZTransform
import Mathlib.Algebra.MonoidAlgebra.Basic
import Mathlib.LinearAlgebra.Matrix.ToLin

/-!
Author: Komorebi P. FIR banks as matrices of finite Laurent polynomials.
A monomial at d is z^(-d), acting by x[n] ↦ x[n-d]. The matrix criterion is
proved on all bilateral sequences, without a convergence assumption.
-/
namespace KomorebiPaperV.FilterBank
abbrev Signal := ℤ → ℂ
abbrev Laurent := AddMonoidAlgebra ℂ ℤ

noncomputable def delayMap (d : ℤ) : Module.End ℂ Signal where
  toFun x := fun n => x (n-d)
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

noncomputable def shiftHom : Multiplicative ℤ →* Module.End ℂ Signal where
  toFun d := delayMap d.toAdd
  map_one' := by ext x n; change x (n-0) = x n; simp
  map_mul' a b := by
    ext x n
    change x (n-(a.toAdd+b.toAdd)) = x (n-a.toAdd-b.toAdd)
    congr 1
    ring

noncomputable def act : Laurent →ₐ[ℂ] Module.End ℂ Signal :=
  AddMonoidAlgebra.lift ℂ (Module.End ℂ Signal) ℤ shiftHom

theorem act_apply (h : Laurent) (x : Signal) (n : ℤ) :
    act h x n = ∑ t ∈ h.coeff.support, h.coeff t * x (n-t) := by
  rw [act, AddMonoidAlgebra.lift_apply]
  simp [Finsupp.sum, shiftHom, delayMap]

theorem act_is_fir (h : Laurent) (x : Signal) :
    act h x = KomorebiPaperV.FIRTransfer.fir h.coeff x := by
  funext n
  exact act_apply h x n

noncomputable def impulse : Signal := fun n => if n = 0 then 1 else 0

theorem act_impulse (h : Laurent) (n : ℤ) : act h impulse n = h.coeff n := by
  classical
  rw [act_apply]
  simp [impulse, sub_eq_zero, Finsupp.mem_support_iff]
  intro hzero
  exact hzero.symm

theorem act_single (d : ℤ) (c : ℂ) (x : Signal) (n : ℤ) :
    act (AddMonoidAlgebra.single d c) x n = c * x (n-d) := by
  rw [act, AddMonoidAlgebra.lift_single]
  rfl

noncomputable def scalarShift (z : ℂ) (hz : z ≠ 0) : Multiplicative ℤ →* ℂ where
  toFun d := z ^ (-d.toAdd)
  map_one' := by simp
  map_mul' a b := by
    change z ^ (-(a.toAdd+b.toAdd)) = z ^ (-a.toAdd) * z ^ (-b.toAdd)
    rw [neg_add, zpow_add₀ hz]

noncomputable def evalZ (z : ℂ) (hz : z ≠ 0) : Laurent →ₐ[ℂ] ℂ :=
  AddMonoidAlgebra.lift ℂ ℂ ℤ (scalarShift z hz)

theorem evalZ_apply (z : ℂ) (hz : z ≠ 0) (h : Laurent) :
    evalZ z hz h = ∑ d ∈ h.coeff.support, h.coeff d * z ^ (-d) := by
  rw [evalZ, AddMonoidAlgebra.lift_apply]
  rfl

theorem filter_transform (h : Laurent) (x : Signal) (z X : ℂ) (hz : z ≠ 0)
    (hx : KomorebiPaperV.ZTransform.HasTransform x z X) :
    KomorebiPaperV.ZTransform.HasTransform (act h x) z (evalZ z hz h * X) := by
  have ht := KomorebiPaperV.ZTransform.finite_transfer_transform h.coeff.support
    (fun _ => x) (fun d => h.coeff d) (fun d => d) z hz (fun _ => X) (fun _ _ => hx)
  simpa only [KomorebiPaperV.ZTransform.HasTransform, act_apply, evalZ_apply,
    Finset.sum_mul] using ht

variable {I : Type*} [Fintype I] [DecidableEq I]

noncomputable def bank (B : Matrix I I Laurent) (x : I → Signal) : I → Signal :=
  fun k => ∑ s, act (B k s) (x s)

omit [DecidableEq I] in
theorem bank_mul (A B : Matrix I I Laurent) (x : I → Signal) :
    bank (A*B) x = bank A (bank B x) := by
  funext k
  simp only [bank, Matrix.mul_apply, map_sum, map_mul, LinearMap.sum_apply,
    Module.End.mul_apply]
  rw [Finset.sum_comm]

noncomputable def channelImpulse (s : I) : I → Signal := Pi.single s impulse

theorem bank_impulse (B : Matrix I I Laurent) (k s : I) (n : ℤ) :
    bank B (channelImpulse s) k n = (B k s).coeff n := by
  classical
  simp only [bank, channelImpulse, Pi.single_apply, Finset.sum_apply]
  rw [Finset.sum_eq_single s]
  · simpa only [↓reduceIte] using act_impulse (B k s) n
  · intro j _ hj
    simp only [ite_eq_right hj, map_zero, Pi.zero_apply]
  · intro hs
    exact False.elim (hs (Finset.mem_univ s))

theorem bank_faithful (A B : Matrix I I Laurent) :
    (∀ x, bank A x = bank B x) ↔ A = B := by
  constructor
  · intro h
    funext k s
    apply AddMonoidAlgebra.ext
    apply Finsupp.ext
    intro n
    have he := congrArg (fun y : I → Signal => y k n) (h (channelImpulse s))
    simpa only [bank_impulse] using he
  · rintro rfl
    intro x
    rfl

noncomputable def gainDelay (c : ℂ) (d : ℤ) : Matrix I I Laurent :=
  Matrix.diagonal (fun _ => AddMonoidAlgebra.single d c)

theorem gain_delay_action (c : ℂ) (d : ℤ) (x : I → Signal) (k : I) (n : ℤ) :
    bank (gainDelay c d) x k n = c*x k (n-d) := by
  classical
  simp only [bank, gainDelay, Matrix.diagonal_apply, Finset.sum_apply]
  rw [Finset.sum_eq_single k]
  · simpa only [↓reduceIte] using act_single d c (x k) n
  · intro j _ hj
    simp only [ite_eq_right hj.symm, map_zero, LinearMap.zero_apply, Pi.zero_apply]
  · intro hk
    exact False.elim (hk (Finset.mem_univ k))

/-- Exact reconstruction of every channel sequence iff the Laurent matrix is gain times delay. -/
theorem perfect_reconstruction_iff (E R : Matrix I I Laurent) (c : ℂ) (d : ℤ) :
    (∀ x : I → Signal, ∀ k n, bank R (bank E x) k n = c*x k (n-d)) ↔
      R*E = gainDelay c d := by
  rw [← bank_faithful]
  constructor
  · intro h x
    funext k n
    rw [bank_mul, gain_delay_action]
    exact h x k n
  · intro h x k n
    have he := congrArg (fun y : I → Signal => y k n) (h x)
    simpa only [bank_mul, gain_delay_action] using he

omit [DecidableEq I] in
theorem bank_transform (B : Matrix I I Laurent) (x : I → Signal) (z : ℂ) (hz : z ≠ 0)
    (X : I → ℂ) (hx : ∀ i, KomorebiPaperV.ZTransform.HasTransform (x i) z (X i)) (k : I) :
    KomorebiPaperV.ZTransform.HasTransform (bank B x k) z
      (Matrix.mulVec (fun k s => evalZ z hz (B k s)) X k) := by
  have ht := hasSum_sum (s := Finset.univ) (fun s _ => filter_transform (B k s) (x s) z (X s) hz (hx s))
  simpa only [KomorebiPaperV.ZTransform.HasTransform, bank, Finset.sum_apply,
    Finset.sum_mul, Matrix.mulVec, dotProduct] using ht

theorem original_sample_delay (N : ℕ) (hN : 0 < N)
    (E R : Matrix (Fin N) (Fin N) Laurent) (c : ℂ) (d : ℤ)
    (h : R*E = gainDelay c d) (x : Signal) (n : ℤ) :
    KomorebiPaperV.IntegerPolyphase.synthesis N hN
      (bank R (bank E (KomorebiPaperV.IntegerPolyphase.analysis N x))) n = c*x (n-(N:ℤ)*d) := by
  have hr := (perfect_reconstruction_iff E R c d).mpr h
  unfold KomorebiPaperV.IntegerPolyphase.synthesis
  rw [hr]
  congr 1
  unfold KomorebiPaperV.IntegerPolyphase.analysis
  congr 1
  have ha := KomorebiPaperV.IntegerPolyphase.address_phase_quotient N hN n
  dsimp [KomorebiPaperV.IntegerPolyphase.address] at ha ⊢
  linarith

end KomorebiPaperV.FilterBank
