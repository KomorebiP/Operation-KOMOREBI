import KomorebiPaperV.FIRTransfer
import Mathlib.Analysis.SpecialFunctions.Pow.Complex
import Mathlib.LinearAlgebra.Matrix.ToLin

/-!
Author: Komorebi P. Bilateral channel transforms with explicit summability.
The time-domain FIR theorem applies to every sequence. A transform equality is
asserted only where the input weighted series converges; no totalized divergent
series is silently treated as a transform.
-/
namespace KomorebiPaperV.ZTransform
open KomorebiPaperV.FIRTransfer KomorebiPaperV.IntegerPolyphase

noncomputable def transform (x : ℤ → ℂ) (z : ℂ) : ℂ := ∑' n, x n * z ^ (-n)

def HasTransform (x : ℤ → ℂ) (z X : ℂ) : Prop := HasSum (fun n => x n * z ^ (-n)) X

theorem transform_unique (x : ℤ → ℂ) (z X : ℂ) (h : HasTransform x z X) :
    transform x z = X := h.tsum_eq

theorem delay_transform (x : ℤ → ℂ) (z X : ℂ) (hz : z ≠ 0)
    (h : HasTransform x z X) (d : ℤ) :
    HasTransform (fun n => x (n-d)) z (z ^ (-d) * X) := by
  have hh := h.mul_left (z ^ (-d))
  have he : (fun n : ℤ => z ^ (-d) * (x n * z ^ (-n))) =
      (fun n : ℤ => x (n-d) * z ^ (-n)) ∘ Equiv.addRight d := by
    funext n
    change z ^ (-d) * (x n * z ^ (-n)) = x (n+d-d) * z ^ (-(n+d))
    rw [add_sub_cancel_right, neg_add, zpow_add₀ hz]
    ring
  rw [he] at hh
  exact (Equiv.addRight d).hasSum_iff.mp hh

theorem finite_transfer_transform {I : Type*} (s : Finset I) (x : I → ℤ → ℂ)
    (w : I → ℂ) (d : I → ℤ) (z : ℂ) (hz : z ≠ 0) (X : I → ℂ)
    (hx : ∀ i ∈ s, HasTransform (x i) z (X i)) :
    HasTransform (fun n => ∑ i ∈ s, w i * x i (n-d i)) z
      (∑ i ∈ s, w i * z ^ (-d i) * X i) := by
  have hh : ∀ i ∈ s, HasSum (fun n => w i * (x i (n-d i) * z ^ (-n)))
      (w i * (z ^ (-d i) * X i)) :=
    fun i hi => (delay_transform (x i) z (X i) hz (hx i hi) (d i)).mul_left (w i)
  have ht := hasSum_sum hh
  simpa [HasTransform, Finset.sum_mul, mul_assoc] using ht

noncomputable def transferMatrix (N : ℕ) (hN : 0 < N) (h : ℤ →₀ ℂ) (z : ℂ) :
    Matrix (Fin N) (Fin N) ℂ := fun k s =>
  ∑ m ∈ delays N hN h k s, kernel N h k s m * z ^ (-m)

theorem fir_channel_transform (N : ℕ) (hN : 0 < N) (h : ℤ →₀ ℂ) (x : ℤ → ℂ)
    (z : ℂ) (hz : z ≠ 0) (X : Fin N → ℂ)
    (hx : ∀ s, HasTransform (analysis N x s) z (X s)) (k : Fin N) :
    HasTransform (analysis N (fir h x) k) z ((transferMatrix N hN h z).mulVec X k) := by
  have hh : ∀ s : Fin N, HasSum
      (fun n => (∑ m ∈ delays N hN h k s, kernel N h k s m * analysis N x s (n-m)) * z ^ (-n))
      (transferMatrix N hN h z k s * X s) := by
    intro s
    have ht := finite_transfer_transform (delays N hN h k s) (fun _ => analysis N x s)
      (fun m => kernel N h k s m) (fun m => m) z hz (fun _ => X s) (fun _ _ => hx s)
    simpa [HasTransform, transferMatrix, Finset.sum_mul] using ht
  have ht := hasSum_sum (s := Finset.univ) (fun s _ => hh s)
  simpa only [HasTransform, fir_polyphase_transfer N hN h x, Finset.sum_mul,
    Matrix.mulVec, dotProduct] using ht

theorem fir_matrix_transform (N : ℕ) (hN : 0 < N) (h : ℤ →₀ ℂ) (x : ℤ → ℂ)
    (z : ℂ) (hz : z ≠ 0)
    (hx : ∀ s, Summable (fun n => analysis N x s n * z ^ (-n))) :
    (fun k => transform (analysis N (fir h x) k) z) =
      (transferMatrix N hN h z).mulVec (fun s => transform (analysis N x s) z) := by
  funext k
  exact (fir_channel_transform N hN h x z hz _ (fun s => (hx s).hasSum) k).tsum_eq

end KomorebiPaperV.ZTransform
