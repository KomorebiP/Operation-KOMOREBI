/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.AnalyticTaylorDifferential
import KomorebiPaperIV.PrincipalPartCoefficients
import Mathlib.Analysis.Meromorphic.NormalForm

namespace Komorebi.PaperIV
noncomputable section
open Set Filter Metric
open scoped Topology Classical

def poleTerm (ρ : ℂ) (ℓ : ℕ) (z : ℂ) : ℂ := ((1 - z / ρ) ^ ℓ)⁻¹

def polePrincipalPart (a : ℂ → ℕ → ℂ) (r : ℕ) (ρ z : ℂ) : ℂ :=
  ∑ k ∈ Finset.range r, a ρ (k + 1) * poleTerm ρ (k + 1) z

def rawPoleRemainder (f : ℂ → ℂ) (S : Finset ℂ) (a : ℂ → ℕ → ℂ) (r : ℕ) (z : ℂ) : ℂ :=
  (f z ^ r)⁻¹ - ∑ ρ ∈ S, polePrincipalPart a r ρ z

theorem poleTerm_analyticAt {ρ z : ℂ} (hρ : ρ ≠ 0) (hz : z ≠ ρ) (ℓ : ℕ) :
    AnalyticAt ℂ (poleTerm ρ ℓ) z := by
  have h : 1 - z / ρ ≠ 0 := by
    intro he
    apply hz
    exact (div_eq_one_iff_eq hρ).mp (sub_eq_zero.mp he).symm
  unfold poleTerm
  exact ((analyticAt_const.sub (analyticAt_id.div_const)).pow ℓ).inv (pow_ne_zero ℓ h)

theorem poleTerm_meromorphicAt (ρ z : ℂ) (ℓ : ℕ) : MeromorphicAt (poleTerm ρ ℓ) z := by
  unfold poleTerm
  exact (((analyticAt_const.sub (analyticAt_id.div_const)).pow ℓ).meromorphicAt).inv

theorem polePrincipalPart_analyticAt {ρ z : ℂ} (hρ : ρ ≠ 0) (hz : z ≠ ρ)
    (a : ℂ → ℕ → ℂ) (r : ℕ) : AnalyticAt ℂ (polePrincipalPart a r ρ) z := by
  exact Finset.analyticAt_fun_sum _ (fun k _ => analyticAt_const.mul (poleTerm_analyticAt hρ hz (k+1)))

theorem rawPoleRemainder_meromorphic {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (S : Finset ℂ) (a : ℂ → ℕ → ℂ) (r : ℕ) :
    MeromorphicOn (rawPoleRemainder f S a r) univ := by
  intro z _
  apply (((hf.analyticAt z).pow r).meromorphicAt.inv).sub
  exact MeromorphicAt.fun_sum (fun ρ _ => MeromorphicAt.fun_sum
    (fun k _ => (MeromorphicAt.const _ _).mul (poleTerm_meromorphicAt ρ z (k+1))))

theorem rawPoleRemainder_analyticAt {f : ℂ → ℂ} {z : ℂ} (hf : AnalyticAt ℂ f z)
    (hfz : f z ≠ 0) {S : Finset ℂ} (hS : ∀ ρ ∈ S, ρ ≠ 0) (hz : z ∉ S)
    (a : ℂ → ℕ → ℂ) (r : ℕ) : AnalyticAt ℂ (rawPoleRemainder f S a r) z := by
  apply ((hf.pow r).inv (pow_ne_zero r hfz)).sub
  exact Finset.analyticAt_fun_sum _ (fun ρ hρ => polePrincipalPart_analyticAt (hS ρ hρ)
    (fun (he : z = ρ) => hz (he.symm ▸ hρ)) a r)

/-- A locally bounded meromorphic germ has no negative order. This proves
removability without assuming a holomorphic remainder. -/
theorem meromorphicOrderAt_nonneg_of_bounded {f : ℂ → ℂ} {z : ℂ}
    (hb : ∃ C : ℝ, ∀ᶠ w in 𝓝[≠] z, ‖f w‖ ≤ C) : 0 ≤ meromorphicOrderAt f z := by
  by_contra hn
  have ht := tendsto_norm_atTop_iff_cobounded.mpr (tendsto_cobounded_of_meromorphicOrderAt_neg (lt_of_not_ge hn))
  obtain ⟨C, hC⟩ := hb
  obtain ⟨w, hw, hw'⟩ := (hC.and (ht.eventually_gt_atTop C)).exists
  exact (not_lt_of_ge hw) hw'

/-- The manuscript's local O(1) principal-part condition implies boundedness
of the remainder after all finitely many principal parts are subtracted. -/
theorem rawPoleRemainder_bounded_at_pole {f : ℂ → ℂ} {S : Finset ℂ}
    (hS : ∀ ρ ∈ S, ρ ≠ 0) (a : ℂ → ℕ → ℂ) (r : ℕ) {ρ : ℂ} (hρ : ρ ∈ S)
    (hb : ∃ C : ℝ, ∀ᶠ z in 𝓝[≠] ρ, ‖(f z ^ r)⁻¹ - polePrincipalPart a r ρ z‖ ≤ C) :
    ∃ C : ℝ, ∀ᶠ z in 𝓝[≠] ρ, ‖rawPoleRemainder f S a r z‖ ≤ C := by
  let Q : ℂ → ℂ := fun z => ∑ τ ∈ S.erase ρ, polePrincipalPart a r τ z
  have hQ : AnalyticAt ℂ Q ρ := Finset.analyticAt_fun_sum _ (fun τ hτ =>
    polePrincipalPart_analyticAt (hS τ (Finset.mem_erase.mp hτ).2)
      (Ne.symm (Finset.mem_erase.mp hτ).1) a r)
  have he : ∀ᶠ z in 𝓝[≠] ρ, ‖Q z‖ ≤ ‖Q ρ‖ + 1 :=
    (hQ.continuousAt.norm.eventually (eventually_le_nhds (by linarith : ‖Q ρ‖ < ‖Q ρ‖ + 1))).filter_mono nhdsWithin_le_nhds
  obtain ⟨C, hC⟩ := hb
  refine ⟨C + (‖Q ρ‖ + 1), ?_⟩
  filter_upwards [hC, he] with z hz hq
  have hsum := Finset.sum_erase_add S (fun τ => polePrincipalPart a r τ z) hρ
  have heq : rawPoleRemainder f S a r z = ((f z ^ r)⁻¹ - polePrincipalPart a r ρ z) - Q z := by
    unfold rawPoleRemainder Q
    rw [← hsum]
    ring
  rw [heq]
  exact (norm_sub_le _ _).trans (add_le_add hz hq)

def removedPoleRemainder (f : ℂ → ℂ) (S : Finset ℂ) (a : ℂ → ℕ → ℂ) (r : ℕ) : ℂ → ℂ :=
  toMeromorphicNFOn (rawPoleRemainder f S a r) univ

theorem removedPoleRemainder_analyticOnNhd {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    {S : Finset ℂ} (hS : ∀ ρ ∈ S, ρ ≠ 0) (a : ℂ → ℕ → ℂ) (r : ℕ) {U : Set ℂ}
    (hzeros : ∀ z ∈ U, f z = 0 → z ∈ S)
    (hlocal : ∀ ρ ∈ S, ∃ C : ℝ, ∀ᶠ z in 𝓝[≠] ρ,
      ‖(f z ^ r)⁻¹ - polePrincipalPart a r ρ z‖ ≤ C) :
    AnalyticOnNhd ℂ (removedPoleRemainder f S a r) U := by
  intro z hz
  have hn := meromorphicNFOn_toMeromorphicNFOn (rawPoleRemainder f S a r) univ (mem_univ z)
  apply hn.meromorphicOrderAt_nonneg_iff_analyticAt.mp
  rw [meromorphicOrderAt_toMeromorphicNFOn (rawPoleRemainder_meromorphic hf S a r) (mem_univ z)]
  by_cases hsz : z ∈ S
  · exact meromorphicOrderAt_nonneg_of_bounded (rawPoleRemainder_bounded_at_pole hS a r hsz (hlocal z hsz))
  · have ha := rawPoleRemainder_analyticAt (hf.analyticAt z) (fun he => hsz (hzeros z hz he)) hS hsz a r
    exact ha.meromorphicNFAt.meromorphicOrderAt_nonneg_iff_analyticAt.mpr ha

theorem removedPoleRemainder_eq_raw {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    {S : Finset ℂ} (hS : ∀ ρ ∈ S, ρ ≠ 0) (a : ℂ → ℕ → ℂ) (r : ℕ) {z : ℂ}
    (hfz : f z ≠ 0) (hz : z ∉ S) :
    removedPoleRemainder f S a r z = rawPoleRemainder f S a r z := by
  unfold removedPoleRemainder
  rw [toMeromorphicNFOn_eq_toMeromorphicNFAt (rawPoleRemainder_meromorphic hf S a r) (mem_univ z),
    toMeromorphicNFAt_eq_self.mpr (rawPoleRemainder_analyticAt (hf.analyticAt z) hfz hS hz a r).meromorphicNFAt]

end
end Komorebi.PaperIV
