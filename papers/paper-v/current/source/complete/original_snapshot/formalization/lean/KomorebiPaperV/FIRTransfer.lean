import KomorebiPaperV.IntegerPolyphase

/-!
Author: Komorebi P.
Checked source; see the bundled build and axiom audit.
Exact finite-support FIR time-domain transfer, including negative tap addresses.
All sums below are finite. No bilateral z-transform convergence is assumed.
-/

open scoped BigOperators
namespace KomorebiPaperV.FIRTransfer
open KomorebiPaperV.IntegerPolyphase

variable {K : Type*} [Semiring K]

def reflectEquiv (k : ℤ) : ℤ ≃ ℤ where
  toFun t := k - t
  invFun t := k - t
  left_inv t := by dsimp; omega
  right_inv t := by dsimp; omega

def negateQuotient (N : ℕ) : (Fin N × ℤ) ≃ (Fin N × ℤ) where
  toFun p := (p.1, -p.2)
  invFun p := (p.1, -p.2)
  left_inv p := by cases p; simp
  right_inv p := by cases p; simp

def tapEquiv (N : ℕ) (hN : 0 < N) (k : Fin N) : ℤ ≃ Fin N × ℤ :=
  ((reflectEquiv (k.val : ℤ)).trans (addressEquiv N hN)).trans (negateQuotient N)

def tapIndex (N : ℕ) (k s : Fin N) (m : ℤ) : ℤ :=
  (N : ℤ) * m + (k.val : ℤ) - (s.val : ℤ)

theorem tapEquiv_symm (N : ℕ) (hN : 0 < N) (k s : Fin N) (m : ℤ) :
    (tapEquiv N hN k).symm (s, m) = tapIndex N k s m := by
  simp only [tapEquiv, Equiv.symm_trans_apply, reflectEquiv,
    addressEquiv, negateQuotient, Equiv.coe_fn_symm_mk,
    address, tapIndex]
  ring

theorem tapIndex_equiv (N : ℕ) (hN : 0 < N) (k : Fin N) (t : ℤ) :
    tapIndex N k ((tapEquiv N hN k) t).1 ((tapEquiv N hN k) t).2 = t := by
  calc
    _ = (tapEquiv N hN k).symm ((tapEquiv N hN k) t) :=
      (tapEquiv_symm N hN k _ _).symm
    _ = t := (tapEquiv N hN k).symm_apply_apply t

theorem transfer_address (N : ℕ) (k s : Fin N) (n m : ℤ) :
    address N k n - tapIndex N k s m = address N s (n - m) := by
  dsimp [address, tapIndex]
  ring

def fir (h : ℤ →₀ K) (x : ℤ → K) (n : ℤ) : K :=
  ∑ t ∈ h.support, h t * x (n - t)

def kernel (N : ℕ) (h : ℤ →₀ K) (k s : Fin N) (m : ℤ) : K :=
  h (tapIndex N k s m)

def transferSupport (N : ℕ) (hN : 0 < N) (h : ℤ →₀ K) (k : Fin N) :
    Finset (Fin N × ℤ) := h.support.map (tapEquiv N hN k).toEmbedding

def delays (N : ℕ) (hN : 0 < N) (h : ℤ →₀ K) (k s : Fin N) : Finset ℤ :=
  ((transferSupport N hN h k).filter (fun p => p.1 = s)).image Prod.snd

theorem fir_reindex (N : ℕ) (hN : 0 < N) (h : ℤ →₀ K) (x : ℤ → K)
    (k : Fin N) (n : ℤ) :
    fir h x (address N k n) =
      ∑ p ∈ transferSupport N hN h k,
        kernel N h k p.1 p.2 * analysis N x p.1 (n - p.2) := by
  simp only [fir, transferSupport, Finset.sum_map]
  apply Finset.sum_congr rfl
  intro t _
  dsimp only [Function.Embedding.coeFn_mk, Equiv.toEmbedding, kernel, analysis]
  have ht := tapIndex_equiv N hN k t
  rw [ht]
  congr 1
  apply congrArg x
  exact (congrArg (fun t' => address N k n - t') ht.symm).trans
    (transfer_address N k _ n _)

/-- Reindex a fiber of a finite set of pairs by its second coordinate. -/
theorem sum_pair_fiber {R Q E : Type*} [DecidableEq R] [DecidableEq Q]
    [AddCommMonoid E] (u : Finset (R × Q)) (r : R) (F : R → Q → E) :
    (∑ p ∈ u.filter (fun p => p.1 = r), F p.1 p.2) =
      ∑ q ∈ (u.filter (fun p => p.1 = r)).image Prod.snd, F r q := by
  rw [Finset.sum_image (by
    intro p hp q hq hpq
    apply Prod.ext
    · exact (Finset.mem_filter.mp hp).2.trans (Finset.mem_filter.mp hq).2.symm
    · exact hpq)]
  apply Finset.sum_congr rfl
  intro p hp
  rw [(Finset.mem_filter.mp hp).2]

/-- Literal h[k,s](m)=h[N*m+k-s] transfer, on the exact finite channel supports. -/
theorem fir_polyphase_transfer (N : ℕ) (hN : 0 < N) (h : ℤ →₀ K)
    (x : ℤ → K) (k : Fin N) (n : ℤ) :
    analysis N (fir h x) k n =
      ∑ s : Fin N, ∑ m ∈ delays N hN h k s,
        kernel N h k s m * analysis N x s (n - m) := by
  change fir h x (address N k n) = _
  rw [fir_reindex N hN h x k n]
  calc
    _ = ∑ s : Fin N, ∑ p ∈ (transferSupport N hN h k).filter (fun p => p.1 = s),
        kernel N h k p.1 p.2 * analysis N x p.1 (n - p.2) :=
      (Finset.sum_fiberwise (transferSupport N hN h k) Prod.fst
        (fun p => kernel N h k p.1 p.2 * analysis N x p.1 (n - p.2))).symm
    _ = _ := by
      apply Finset.sum_congr rfl
      intro s _
      exact sum_pair_fiber (transferSupport N hN h k) s
        (fun r m => kernel N h k r m * analysis N x r (n - m))

end KomorebiPaperV.FIRTransfer
