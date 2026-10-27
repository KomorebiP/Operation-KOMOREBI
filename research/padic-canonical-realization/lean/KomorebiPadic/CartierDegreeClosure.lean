import KomorebiPadic.CartierMaskTransition
import KomorebiPadic.FiniteCartierMachine

/-! # Explicit sufficient layer and numerator-degree closure
These bounds retain all r formal correction orders. They are sufficient bounds,
not an assertion of minimal orbit size or of no cancellation after sectioning.
-/
namespace KomorebiPadic
open Polynomial

/-- Ceiling division with explicit positive-divisor hypotheses on its bound. -/
def cartierCeilDiv (n a : ℕ) : ℕ := (n+a-1)/a

theorem le_mul_cartierCeilDiv (n : ℕ) {a : ℕ} (ha : 0 < a) :
    n ≤ a * cartierCeilDiv n a := by
  have he := Nat.div_add_mod (n+a-1) a
  have hm := Nat.mod_lt (n+a-1) ha
  unfold cartierCeilDiv
  omega

/-- Original contiguous all-branch denominator bound. -/
def cartierLayerBound (p r : ℕ) : ℕ := r-1+cartierCeilDiv r (p-1)

theorem cartierLayerBound_pos {p r : ℕ} (hp : 1 < p) (hr : 0 < r) :
    0 < cartierLayerBound p r := by
  have hs := le_mul_cartierCeilDiv r (by omega : 0 < p-1)
  have hn : 0 < cartierCeilDiv r (p-1) := by
    by_contra hz
    have he : cartierCeilDiv r (p-1) = 0 := by omega
    rw [he, Nat.mul_zero] at hs
    omega
  unfold cartierLayerBound
  omega

/-- Every formal correction target stays within the finite denominator array. -/
theorem cartierLayerBound_closed {p r ell k : ℕ} (hp : 1 < p)
    (hell : ell ≤ cartierLayerBound p r) (hk : k < r) :
    quotientOfLayer p ell + k ≤ cartierLayerBound p r := by
  let s := cartierCeilDiv r (p-1)
  have hs : r ≤ (p-1)*s := le_mul_cartierCeilDiv r (by omega)
  have hps : (p-1)*s+s = s*p := by
    have he : p-1+1 = p := by omega
    calc
      (p-1)*s+s = (p-1+1)*s := by ring
      _ = s*p := by rw [he]; ring
  have hl : ell < s*p := by
    change ell ≤ r-1+s at hell
    omega
  have hq := (Nat.div_lt_iff_lt_mul (by omega : 0 < p)).mpr hl
  change ell/p+1+k ≤ r-1+s
  omega

/-- Uniform upper bound on the non-numerator part of each branch. -/
noncomputable def cartierKernelDegreeCap (p r : ℕ) (A B : ℤ[X]) : ℕ :=
  A.natDegree + (p-1)*B.natDegree + (r-1)*(frobeniusDefect p B).natDegree

noncomputable def cartierNumeratorBound (p r : ℕ) (A B : ℤ[X]) : ℕ :=
  max B.natDegree (cartierCeilDiv (cartierKernelDegreeCap p r A B) (p-1))

theorem cartierNumeratorBound_initial (p r : ℕ) (A B : ℤ[X]) :
    B.natDegree ≤ cartierNumeratorBound p r A B := Nat.le_max_left _ _

theorem cartierNumeratorBound_kernel {p r : ℕ} (hp : 1 < p) (A B : ℤ[X]) :
    cartierKernelDegreeCap p r A B ≤ (p-1)*cartierNumeratorBound p r A B := by
  exact (le_mul_cartierCeilDiv _ (by omega : 0 < p-1)).trans
    (Nat.mul_le_mul_left (p-1) (Nat.le_max_right _ _))

theorem cartierBranchWeight_degree (p q k : ℕ) (E : ℤ[X]) :
    (cartierBranchWeight p q k E).natDegree ≤ k*E.natDegree := by
  unfold cartierBranchWeight
  rw [← map_mul, ← map_mul]
  exact (Polynomial.natDegree_C_mul_le _ _).trans Polynomial.natDegree_pow_le

/-- Kernel over the actual finite coefficient ring, without lifting its state numerator. -/
noncomputable def finiteMaskKernel (p r ell k : ℕ) (A B : ℤ[X]) : (ZMod (p^r))[X] :=
  (A * B^maskPadding p ell *
    cartierBranchWeight p (quotientOfLayer p ell) k (frobeniusDefect p B)).map
      (Int.castRingHom (ZMod (p^r)))

theorem finiteMaskKernel_degree {p r ell k : ℕ} (hp : 1 < p) (hk : k < r)
    (A B : ℤ[X]) :
    (finiteMaskKernel p r ell k A B).natDegree ≤ (p-1)*cartierNumeratorBound p r A B := by
  have ht : maskPadding p ell ≤ p-1 := by have h := (maskPadding_spec (ell := ell) (by omega : 0 < p)).2; omega
  have hb := Polynomial.natDegree_pow_le (p := B) (n := maskPadding p ell)
  have hw := cartierBranchWeight_degree p (quotientOfLayer p ell) k (frobeniusDefect p B)
  have hprod := Polynomial.natDegree_mul_le
    (p := A*B^maskPadding p ell)
    (q := cartierBranchWeight p (quotientOfLayer p ell) k (frobeniusDefect p B))
  have hab := Polynomial.natDegree_mul_le (p := A) (q := B^maskPadding p ell)
  have ht' := Nat.mul_le_mul_right B.natDegree ht
  have hk' := Nat.mul_le_mul_right (frobeniusDefect p B).natDegree (show k ≤ r-1 by omega)
  have hcap : (A*B^maskPadding p ell*
      cartierBranchWeight p (quotientOfLayer p ell) k (frobeniusDefect p B)).natDegree ≤
      cartierKernelDegreeCap p r A B := by
    unfold cartierKernelDegreeCap
    omega
  exact Polynomial.natDegree_map_le.trans (hcap.trans (cartierNumeratorBound_kernel hp A B))

/-- Every residue-polynomial state numerator stays in the explicit degree bound. -/
theorem finiteMaskBranch_degree {p r ell k : ℕ} (hp : 1 < p) (hk : k < r)
    (d : ℕ) (A B : ℤ[X]) (P : (ZMod (p^r))[X])
    (hP : P.natDegree ≤ cartierNumeratorBound p r A B) :
    (polynomialCartier p d (P*finiteMaskKernel p r ell k A B)).natDegree ≤
      cartierNumeratorBound p r A B :=
  polynomialCartier_mul_degree_le (by omega) d P _ hP (finiteMaskKernel_degree hp hk A B)

end KomorebiPadic
