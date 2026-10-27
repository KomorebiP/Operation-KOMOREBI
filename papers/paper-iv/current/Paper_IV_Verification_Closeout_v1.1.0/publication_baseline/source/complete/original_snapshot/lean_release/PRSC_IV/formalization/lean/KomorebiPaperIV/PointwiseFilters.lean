/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.EntireBridge
import KomorebiPaperIV.ZeroMomentLogarithm

namespace Komorebi.PaperIV
open scoped Topology PowerSeries
open Set
noncomputable section

/-- The manuscript's finite root average, acting on actual functions. -/
def pointwiseRootAverage (N j : ℕ) (omega : ℂ) (f : ℂ → ℂ) (z : ℂ) : ℂ :=
  (N : ℂ)⁻¹ * ∑ l ∈ Finset.range N, ((omega ^ j)⁻¹) ^ l * f (omega ^ l * z)

theorem root_weight_sum {N : ℕ} (hN : 0 < N) {omega : ℂ}
    (ho : IsPrimitiveRoot omega N) (j n : ℕ) :
    ∑ l ∈ Finset.range N, ((omega ^ j)⁻¹) ^ l * (omega ^ l) ^ n =
      if n % N = j % N then (N : ℂ) else 0 := by
  let b := (omega ^ j)⁻¹ * omega ^ n
  have ho0 := ho.ne_zero hN.ne'
  have ht (l : ℕ) : ((omega ^ j)⁻¹) ^ l * (omega ^ l) ^ n = b ^ l := by
    simp only [b, ← pow_mul, mul_pow]
    rw [Nat.mul_comm l n]
  simp_rw [ht]
  have hb : b = 1 ↔ n % N = j % N := by
    rw [show b = (omega ^ j)⁻¹ * omega ^ n from rfl,
      inv_mul_eq_one₀ (pow_ne_zero j ho0), eq_comm]
    simpa only [ho.eq_orderOf, Nat.ModEq] using
      (ho.isOfFinOrder hN.ne').pow_eq_pow_iff_modEq (n := n) (m := j)
  have hp : b ^ N = 1 := by
    simp only [b, mul_pow, inv_pow, ← pow_mul]
    rw [mul_comm j N, mul_comm n N, pow_mul, pow_mul, ho.pow_eq_one]
    simp
  split_ifs with h
  · simp [hb.mpr h]
  · have hn : b ≠ 1 := fun he => h (hb.mp he)
    have he : (b - 1) * ∑ l ∈ Finset.range N, b ^ l = 0 := by
      rw [mul_geom_sum, hp, sub_self]
    exact (mul_eq_zero.mp he).resolve_left (sub_ne_zero.mpr hn)

theorem mapsTo_root_pow {omega : ℂ} {s : Set ℂ}
    (hs : MapsTo (fun z => omega * z) s s) (l : ℕ) :
    MapsTo (fun z => omega ^ l * z) s s := by
  induction l with
  | zero => intro z hz; simpa using hz
  | succ l ih =>
    intro z hz
    simpa [pow_succ', mul_assoc] using hs (ih hz)

theorem pointwiseRootAverage_covariant {N : ℕ} (hN : 0 < N) {omega : ℂ}
    (ho : IsPrimitiveRoot omega N) (j : ℕ) (f : ℂ → ℂ) (z : ℂ) :
    pointwiseRootAverage N j omega f (omega * z) =
      omega ^ j * pointwiseRootAverage N j omega f z := by
  let a := (omega ^ j)⁻¹
  let g := fun l : ℕ => a ^ l * f (omega ^ l * z)
  have haN : a ^ N = 1 := by
    simp only [a, inv_pow, ← pow_mul]
    rw [Nat.mul_comm j N, pow_mul, ho.pow_eq_one]
    simp
  have hg : g N = g 0 := by simp [g, haN, ho.pow_eq_one]
  have hshift : (∑ l ∈ Finset.range N, g (l + 1)) = ∑ l ∈ Finset.range N, g l := by
    have h := Finset.sum_range_succ' g N
    rw [Finset.sum_range_succ, hg] at h
    exact (add_right_cancel h).symm
  have ht (l : ℕ) : a ^ l * f (omega ^ l * (omega * z)) = omega ^ j * g (l + 1) := by
    rw [show omega ^ l * (omega * z) = omega ^ (l + 1) * z by rw [pow_succ]; ring]
    dsimp [g]
    rw [pow_succ]
    have hc : omega ^ j * a = 1 := mul_inv_cancel₀ (pow_ne_zero j (ho.ne_zero hN.ne'))
    calc
      _ = (omega ^ j * a) * (a ^ l * f (omega ^ (l + 1) * z)) := by rw [hc]; ring
      _ = _ := by ring
  unfold pointwiseRootAverage
  change (N : ℂ)⁻¹ * (∑ l ∈ Finset.range N, a ^ l * f (omega ^ l * (omega * z))) = _
  simp_rw [ht]
  rw [← Finset.mul_sum, hshift]
  dsimp [g, a]
  ring

theorem pointwiseRootAverage_of_covariant {N : ℕ} (hN : 0 < N) {omega : ℂ}
    (ho : IsPrimitiveRoot omega N) {s : Set ℂ}
    (hs : MapsTo (fun z => omega * z) s s) (j k : ℕ) (f : ℂ → ℂ)
    (hf : ∀ z ∈ s, f (omega * z) = omega ^ k * f z) {z : ℂ} (hz : z ∈ s) :
    pointwiseRootAverage N j omega f z =
      if k % N = j % N then f z else 0 := by
  have hp (l : ℕ) : f (omega ^ l * z) = (omega ^ l) ^ k * f z := by
    induction l with
    | zero => simp
    | succ l ih =>
      rw [pow_succ', mul_assoc, hf _ (mapsTo_root_pow hs l hz), ih, mul_pow]
      ring
  unfold pointwiseRootAverage
  simp_rw [hp, ← mul_assoc]
  rw [← Finset.sum_mul, root_weight_sum hN ho]
  split_ifs <;> simp [Nat.cast_ne_zero.mpr hN.ne']

theorem pointwiseRootAverage_projector {N : ℕ} (hN : 0 < N) {omega : ℂ}
    (ho : IsPrimitiveRoot omega N) (i j : ℕ) (f : ℂ → ℂ) (z : ℂ) :
    pointwiseRootAverage N i omega (pointwiseRootAverage N j omega f) z =
      if j % N = i % N then pointwiseRootAverage N j omega f z else 0 := by
  exact pointwiseRootAverage_of_covariant hN ho (mapsTo_univ _ _) i j _
    (fun w _ => pointwiseRootAverage_covariant hN ho j f w) (mem_univ z)

theorem pointwiseRootAverage_resolution {N : ℕ} (hN : 0 < N) {omega : ℂ}
    (ho : IsPrimitiveRoot omega N) (f : ℂ → ℂ) (z : ℂ) :
    (∑ j ∈ Finset.range N, pointwiseRootAverage N j omega f z) = f z := by
  have hw (l : ℕ) : (∑ j ∈ Finset.range N, ((omega ^ j)⁻¹) ^ l) =
      if l % N = 0 then (N : ℂ) else 0 := by
    have h := root_weight_sum hN ho l 0
    simp only [pow_zero, mul_one, Nat.zero_mod] at h
    convert h using 1
    · apply Finset.sum_congr rfl
      intro j _
      simp only [← inv_pow, ← pow_mul]
      rw [Nat.mul_comm]
    · simp [eq_comm]
  unfold pointwiseRootAverage
  rw [← Finset.mul_sum, Finset.sum_comm]
  simp_rw [← Finset.sum_mul, hw]
  rw [Finset.sum_eq_single 0]
  · simp [Nat.cast_ne_zero.mpr hN.ne']
  · intro l hl hl0
    simp [Nat.mod_eq_of_lt (Finset.mem_range.mp hl), hl0]
  · simp [hN]

theorem differentiableOn_pointwiseRootAverage {N : ℕ} (j : ℕ) (omega : ℂ)
    {s : Set ℂ} (hs : MapsTo (fun z => omega * z) s s)
    {f : ℂ → ℂ} (hf : DifferentiableOn ℂ f s) :
    DifferentiableOn ℂ (pointwiseRootAverage N j omega f) s := by
  apply DifferentiableOn.const_mul
  apply DifferentiableOn.fun_sum
  intro l _
  apply DifferentiableOn.const_mul
  exact hf.comp (by fun_prop) (mapsTo_root_pow hs l)

theorem pointwiseRootAverage_range_iff {N : ℕ} (hN : 0 < N) {omega : ℂ}
    (ho : IsPrimitiveRoot omega N) {s : Set ℂ}
    (hs : MapsTo (fun z => omega * z) s s) (j : ℕ) {f : ℂ → ℂ}
    (hf : DifferentiableOn ℂ f s) :
    (∃ g : ℂ → ℂ, DifferentiableOn ℂ g s ∧ EqOn (pointwiseRootAverage N j omega g) f s) ↔
      ∀ z ∈ s, f (omega * z) = omega ^ j * f z := by
  constructor
  · rintro ⟨g, _, hg⟩ z hz
    rw [← hg (hs hz), ← hg hz]
    exact pointwiseRootAverage_covariant hN ho j g z
  · intro hc
    refine ⟨f, hf, fun z hz => ?_⟩
    simpa using pointwiseRootAverage_of_covariant hN ho hs j j f hc hz

theorem pointwiseRootAverage_sum {I : Type*} (s : Finset I)
    (N j : ℕ) (omega : ℂ) (f : I → ℂ → ℂ) (z : ℂ) :
    pointwiseRootAverage N j omega (fun w => ∑ i ∈ s, f i w) z =
      ∑ i ∈ s, pointwiseRootAverage N j omega (f i) z := by
  unfold pointwiseRootAverage
  simp_rw [Finset.mul_sum]
  rw [Finset.sum_comm]

theorem pointwiseRootAverage_product {N : ℕ} (hN : 0 < N) {omega : ℂ}
    (ho : IsPrimitiveRoot omega N) (k : ℕ) (f g : ℂ → ℂ) (z : ℂ) :
    pointwiseRootAverage N k omega (fun w => f w * g w) z =
      ∑ i ∈ Finset.range N, ∑ j ∈ Finset.range N,
        if (i + j) % N = k % N then
          pointwiseRootAverage N i omega f z * pointwiseRootAverage N j omega g z
        else 0 := by
  have he : (fun w => f w * g w) =
      (fun w => ∑ i ∈ Finset.range N, ∑ j ∈ Finset.range N,
        pointwiseRootAverage N i omega f w * pointwiseRootAverage N j omega g w) := by
    funext w
    rw [← Finset.sum_mul_sum, pointwiseRootAverage_resolution hN ho,
      pointwiseRootAverage_resolution hN ho]
  rw [he, pointwiseRootAverage_sum]
  apply Finset.sum_congr rfl
  intro i _
  rw [pointwiseRootAverage_sum]
  apply Finset.sum_congr rfl
  intro j _
  apply pointwiseRootAverage_of_covariant hN ho (mapsTo_univ _ _)
  · intro w _
    rw [pointwiseRootAverage_covariant hN ho, pointwiseRootAverage_covariant hN ho, pow_add]
    ring
  · exact mem_univ z

theorem pointwiseRootAverage_hasSum {N : ℕ} (hN : 0 < N) {omega : ℂ}
    (ho : IsPrimitiveRoot omega N) (j : ℕ) (a : ℕ → ℂ) (f : ℂ → ℂ) (z : ℂ)
    (hf : ∀ l ∈ Finset.range N, HasSum (fun n => a n * (omega ^ l * z) ^ n)
      (f (omega ^ l * z))) :
    HasSum (fun n => (if n % N = j % N then a n else 0) * z ^ n)
      (pointwiseRootAverage N j omega f z) := by
  have h := (hasSum_sum (fun l hl => (hf l hl).mul_left (((omega ^ j)⁻¹) ^ l))).mul_left ((N : ℂ)⁻¹)
  apply h.congr_fun
  intro n
  simp only [mul_pow]
  have ht (l : ℕ) : ((omega ^ j)⁻¹) ^ l * (a n * ((omega ^ l) ^ n * z ^ n)) =
      (((omega ^ j)⁻¹) ^ l * (omega ^ l) ^ n) * (a n * z ^ n) := by ring
  simp_rw [ht]
  rw [← Finset.sum_mul, root_weight_sum hN ho]
  split_ifs <;> simp [Nat.cast_ne_zero.mpr hN.ne']

end
end Komorebi.PaperIV
