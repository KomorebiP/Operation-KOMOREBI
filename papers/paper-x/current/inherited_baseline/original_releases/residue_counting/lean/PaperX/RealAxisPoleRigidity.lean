import Mathlib.Analysis.Asymptotics.Lemmas
import Mathlib.Analysis.Asymptotics.Ring
import Mathlib.Analysis.SpecialFunctions.Complex.Analytic
import Mathlib.Tactic

/-! A pole product argument using only limits and first-order endpoint bounds.
No meromorphic or analytic regularity is assumed. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.RealAxisPoleRigidity
open Filter Asymptotics
open scoped Topology

/-- A first-order error against a vanishing scale supplies the endpoint limit. -/
theorem tendsto_of_error_isBigO {α : Type*} {l : Filter α}
    {x a : α → ℂ} {A : ℂ} (hx : Tendsto x l (𝓝 0))
    (ha : (fun t => a t - A) =O[l] x) : Tendsto a l (𝓝 A) := by
  have h := (ha.trans_tendsto hx).add_const A
  simpa using h

/-- A bounded function cannot have a nonzero simple-pole residue. -/
theorem residue_eq_zero_of_bounded {α : Type*} {l : Filter α} [NeBot l]
    {x Z : α → ℂ} {Q : ℂ} (hx : Tendsto x l (𝓝 0))
    (hZ : Z =O[l] fun _ => (1 : ℂ))
    (hQ : Tendsto (fun t => x t * Z t) l (𝓝 Q)) : Q = 0 := by
  have hb : (fun t => x t * Z t) =O[l] x := by
    simpa using (isBigO_refl x l).mul hZ
  exact tendsto_nhds_unique hQ (hb.trans_tendsto hx)

/-- Once every endpoint factor is nonzero, a product identity between two
simple poles forces the natural exponent to be one. -/
theorem exponent_one_of_nonzero_limits {α ι : Type*} [Fintype ι]
    {l : Filter α} [NeBot l] (x p Z : α → ℂ) (a : ι → α → ℂ)
    (A : ι → ℂ) (P Q : ℂ) (d : ℕ)
    (hx : Tendsto x l (𝓝 0))
    (hp : Tendsto (fun t => x t * p t) l (𝓝 P)) (hP : P ≠ 0)
    (hZ : Tendsto (fun t => x t * Z t) l (𝓝 Q)) (hQ : Q ≠ 0)
    (ha : ∀ i, Tendsto (a i) l (𝓝 (A i))) (hA : ∀ i, A i ≠ 0)
    (hid : Z =ᶠ[l] fun t => (p t * ∏ i, a i t) ^ d) : d = 1 := by
  classical
  have hprod : Tendsto (fun t => ∏ i, a i t) l (𝓝 (∏ i, A i)) :=
    tendsto_finsetProd _ (fun i _ => ha i)
  have hB : Tendsto (fun t => x t * (p t * ∏ i, a i t)) l
      (𝓝 (P * ∏ i, A i)) := by
    simpa only [mul_assoc] using hp.mul hprod
  have hB0 : P * ∏ i, A i ≠ 0 := mul_ne_zero hP
    (Finset.prod_ne_zero_iff.mpr (fun i _ => hA i))
  have hd0 : d ≠ 0 := by
    intro hd
    have he : Z =ᶠ[l] fun _ => (1 : ℂ) := by simpa [hd] using hid
    exact hQ (residue_eq_zero_of_bounded hx
      ((isBigO_refl (fun _ : α => (1 : ℂ)) l).congr' he.symm Filter.EventuallyEq.rfl) hZ)
  by_contra hd
  have hd1 : 0 < d - 1 := by omega
  have hleft : Tendsto (fun t => x t ^ (d - 1) * (x t * Z t)) l (𝓝 0) := by
    simpa [zero_pow (Nat.ne_of_gt hd1)] using (hx.pow (d - 1)).mul hZ
  have hright : Tendsto (fun t => (x t * (p t * ∏ i, a i t)) ^ d) l
      (𝓝 ((P * ∏ i, A i) ^ d)) := hB.pow d
  have he : (fun t => x t ^ (d - 1) * (x t * Z t)) =ᶠ[l]
      fun t => (x t * (p t * ∏ i, a i t)) ^ d := by
    filter_upwards [hid] with t ht
    rw [ht, mul_pow]
    rw [← mul_assoc, ← pow_succ, Nat.sub_add_cancel (Nat.one_le_iff_ne_zero.mpr hd0)]
    simp only [mul_pow]
  have hz := tendsto_nhds_unique (hleft.congr' he) hright
  exact (pow_ne_zero d hB0) hz.symm

/-- A finite family with first-order endpoint errors cannot cancel a supplied
simple pole inside a natural power which again has a nonzero simple-pole residue.
The exponent and nonvanishing conclusions are derived together. -/
theorem index_one_and_factors_nonzero {α ι : Type*} [Fintype ι]
    {l : Filter α} [NeBot l] (x p Z : α → ℂ) (a : ι → α → ℂ)
    (A : ι → ℂ) (P Q : ℂ) (d : ℕ)
    (hx : Tendsto x l (𝓝 0))
    (hp : Tendsto (fun t => x t * p t) l (𝓝 P)) (hP : P ≠ 0)
    (hZ : Tendsto (fun t => x t * Z t) l (𝓝 Q)) (hQ : Q ≠ 0)
    (ha : ∀ i, (fun t => a i t - A i) =O[l] x)
    (hid : Z =ᶠ[l] fun t => (p t * ∏ i, a i t) ^ d) :
    d = 1 ∧ ∀ i, A i ≠ 0 := by
  classical
  have hal : ∀ i, Tendsto (a i) l (𝓝 (A i)) :=
    fun i => tendsto_of_error_isBigO hx (ha i)
  have hA : ∀ i, A i ≠ 0 := by
    intro i hi
    have hai : a i =O[l] x := by simpa [hi] using ha i
    have hpa : (fun t => p t * a i t) =O[l] fun _ => (1 : ℂ) := by
      have hh : (fun t => p t * a i t) =O[l] fun t => x t * p t := by
        simpa only [mul_comm] using hai.mul (isBigO_refl p l)
      exact hh.trans (hp.isBigO_one ℂ)
    have hrest : Tendsto (fun t => ∏ j ∈ Finset.univ.erase i, a j t) l
        (𝓝 (∏ j ∈ Finset.univ.erase i, A j)) :=
      tendsto_finsetProd _ (fun j _ => hal j)
    have hb : (fun t => p t * ∏ j, a j t) =O[l] fun _ => (1 : ℂ) := by
      have hh := hpa.mul (hrest.isBigO_one ℂ)
      have he : (fun t => p t * a i t * ∏ j ∈ Finset.univ.erase i, a j t) =
          fun t => p t * ∏ j, a j t := by
        funext t
        rw [mul_assoc, Finset.mul_prod_erase Finset.univ (fun j => a j t)
          (Finset.mem_univ i)]
      simpa only [he, one_mul] using hh
    have hbZ : Z =O[l] fun _ => (1 : ℂ) := by
      have hh : (fun t => (p t * ∏ j, a j t) ^ d) =O[l] fun _ => (1 : ℂ) := by
        simpa using hb.pow d
      exact hh.congr' hid.symm Filter.EventuallyEq.rfl
    exact hQ (residue_eq_zero_of_bounded hx hbZ hZ)
  exact ⟨exponent_one_of_nonzero_limits x p Z a A P Q d hx hp hP hZ hQ hal hA hid, hA⟩

/-- Specialization to the right-hand real endpoint, with scale `h`. -/
theorem right_endpoint_index_one_and_factors_nonzero {ι : Type*} [Fintype ι]
    (p Z : ℝ → ℂ) (a : ι → ℝ → ℂ) (P Q : ℂ) (d : ℕ)
    (hp : Tendsto (fun h : ℝ => (h : ℂ) * p h) (𝓝[>] 0) (𝓝 P)) (hP : P ≠ 0)
    (hZ : Tendsto (fun h : ℝ => (h : ℂ) * Z h) (𝓝[>] 0) (𝓝 Q)) (hQ : Q ≠ 0)
    (ha : ∀ i, (fun h => a i h - a i 0) =O[𝓝[>] 0] fun h => (h : ℂ))
    (hid : Z =ᶠ[𝓝[>] 0] fun h => (p h * ∏ i, a i h) ^ d) :
    d = 1 ∧ ∀ i, a i 0 ≠ 0 := by
  apply index_one_and_factors_nonzero (fun h : ℝ => (h : ℂ)) p Z a (fun i => a i 0)
    P Q d _ hp hP hZ hQ ha hid
  exact Complex.continuous_ofReal.continuousAt.tendsto.mono_left nhdsWithin_le_nhds

end PaperX.RealAxisPoleRigidity
