import KomorebiVerification.PaperII.ReleaseRectifiableCycle

/-! Classical tagged Riemann–Stieltjes integration and its actual velocity representation. -/
set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperII.ReleaseRectifiableRSError

open MeasureTheory Set
open scoped Topology BigOperators
open Komorebi.PaperII.ReleaseRectifiable

variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
  [NormedSpace ℝ E] [CompleteSpace E]

/-- Exact tagged-sum error on a single interval, using the actual path velocity. -/
theorem tagged_increment_sub_integral {f : ℝ → ℂ} {a b τ : ℝ} {H : ℂ → E}
    (hf : AbsolutelyContinuousOnInterval f a b)
    (hH : ContinuousOn H (f '' uIcc a b)) :
    (f b - f a) • H (f τ) -
        (∫ s : ℝ in a..b, coordinateVelocity f s • H (f s)) =
      ∫ s : ℝ in a..b, coordinateVelocity f s • (H (f τ) - H (f s)) := by
  have hv := integrable_coordinateVelocity hf
  have hcomp : ContinuousOn (fun s ↦ H (f s)) (uIcc a b) :=
    hH.comp hf.continuousOn (fun s hs ↦ mem_image_of_mem _ hs)
  have hi := hv.smul_continuousOn hcomp
  have hc := hv.smul_continuousOn (continuousOn_const (c := H (f τ)))
  rw [← integral_coordinateVelocity hf, ← intervalIntegral.integral_smul_const,
    ← intervalIntegral.integral_sub hc hi]
  apply intervalIntegral.integral_congr
  intro s hs
  exact (smul_sub _ _ _).symm

/-- Oscillation times integrated speed bounds the genuine tagged-sum error. -/
theorem norm_tagged_increment_sub_integral_le {f : ℝ → ℂ} {a b τ ε : ℝ} {H : ℂ → E}
    (hab : a ≤ b) (hf : AbsolutelyContinuousOnInterval f a b)
    (hH : ContinuousOn H (f '' uIcc a b))
    (hosc : ∀ s ∈ Icc a b, ‖H (f τ) - H (f s)‖ ≤ ε) :
    ‖(f b - f a) • H (f τ) -
        (∫ s : ℝ in a..b, coordinateVelocity f s • H (f s))‖ ≤
      (∫ s : ℝ in a..b, ‖coordinateVelocity f s‖) * ε := by
  rw [tagged_increment_sub_integral hf hH]
  calc
    _ ≤ ∫ s : ℝ in a..b, ‖coordinateVelocity f s‖ * ε := by
      apply intervalIntegral.norm_integral_le_of_norm_le hab
      · exact Filter.Eventually.of_forall fun s hs ↦ by
          rw [norm_smul]
          exact mul_le_mul_of_nonneg_left (hosc s (Ioc_subset_Icc_self hs)) (norm_nonneg _)
      · exact (integrable_coordinateVelocity hf).norm.mul_const ε
    _ = _ := intervalIntegral.integral_mul_const _ _

/-- Genuine tagged Riemann–Stieltjes contour sum. -/
def taggedSum (f : ℝ → ℂ) (H : ℂ → E) (p q : ℕ → ℝ) (n : ℕ) : E :=
  ∑ j ∈ Finset.range n, (f (p (j+1)) - f (p j)) • H (f (q j))

/-- All endpoints of an ordered partition lie in its endpoint interval. -/
theorem partition_mem {a b : ℝ} {n : ℕ} {p : ℕ → ℝ}
    (hp : MonotoneOn p (Iic n)) (hp0 : p 0 = a) (hpn : p n = b)
    {j : ℕ} (hj : j ≤ n) : p j ∈ uIcc a b := by
  have ha : a ≤ p j := by rw [← hp0]; exact hp (by simp) hj (Nat.zero_le j)
  have hb : p j ≤ b := by rw [← hpn]; exact hp hj (by simp) hj
  exact Icc_subset_uIcc ⟨ha,hb⟩

/-- Every finite ordered partition has total tagged-sum error bounded by one
common oscillation bound times the actual integral of speed. -/
theorem norm_taggedSum_sub_integral_le {f : ℝ → ℂ} {a b ε : ℝ} {H : ℂ → E}
    (hf : AbsolutelyContinuousOnInterval f a b)
    (hH : ContinuousOn H (f '' uIcc a b))
    {n : ℕ} {p q : ℕ → ℝ}
    (hp : MonotoneOn p (Iic n)) (hp0 : p 0 = a) (hpn : p n = b)
    (hosc : ∀ j < n, ∀ s ∈ Icc (p j) (p (j+1)), ‖H (f (q j)) - H (f s)‖ ≤ ε) :
    ‖taggedSum f H p q n - (∫ s : ℝ in a..b, coordinateVelocity f s • H (f s))‖ ≤
      (∫ s : ℝ in a..b, ‖coordinateVelocity f s‖) * ε := by
  have hsub (j : ℕ) (hj : j < n) : uIcc (p j) (p (j+1)) ⊆ uIcc a b :=
    uIcc_subset_uIcc (partition_mem hp hp0 hpn (Nat.le_of_lt hj))
      (partition_mem hp hp0 hpn (Nat.succ_le_of_lt hj))
  have hac (j : ℕ) (hj : j < n) := hf.mono (hsub j hj)
  have hcont (j : ℕ) (hj : j < n) :
      ContinuousOn H (f '' uIcc (p j) (p (j+1))) :=
    hH.mono (image_mono (hsub j hj))
  have hint (j : ℕ) (hj : j < n) :
      IntervalIntegrable (fun s ↦ coordinateVelocity f s • H (f s)) volume (p j) (p (j+1)) :=
    (integrable_coordinateVelocity (hac j hj)).smul_continuousOn
      ((hcont j hj).comp (hac j hj).continuousOn (fun s hs ↦ mem_image_of_mem _ hs))
  have hsum : (∑ j ∈ Finset.range n,
      ∫ s : ℝ in p j..p (j+1), coordinateVelocity f s • H (f s)) =
        ∫ s : ℝ in a..b, coordinateVelocity f s • H (f s) := by
    simpa only [hp0,hpn] using intervalIntegral.sum_integral_adjacent_intervals hint
  have hnormsum : (∑ j ∈ Finset.range n,
      ∫ s : ℝ in p j..p (j+1), ‖coordinateVelocity f s‖) =
        ∫ s : ℝ in a..b, ‖coordinateVelocity f s‖ := by
    simpa only [hp0,hpn] using intervalIntegral.sum_integral_adjacent_intervals
      (fun j hj ↦ (integrable_coordinateVelocity (hac j hj)).norm)
  calc
    _ = ‖∑ j ∈ Finset.range n, ((f (p (j+1)) - f (p j)) • H (f (q j)) -
        ∫ s : ℝ in p j..p (j+1), coordinateVelocity f s • H (f s))‖ := by
      rw [Finset.sum_sub_distrib, hsum]
      rfl
    _ ≤ ∑ j ∈ Finset.range n, ‖(f (p (j+1)) - f (p j)) • H (f (q j)) -
        ∫ s : ℝ in p j..p (j+1), coordinateVelocity f s • H (f s)‖ := norm_sum_le _ _
    _ ≤ ∑ j ∈ Finset.range n, (∫ s : ℝ in p j..p (j+1), ‖coordinateVelocity f s‖) * ε := by
      apply Finset.sum_le_sum
      intro j hj
      have hjn := Finset.mem_range.mp hj
      exact norm_tagged_increment_sub_integral_le
        (hp (Nat.le_of_lt hjn) (Nat.succ_le_of_lt hjn) (Nat.le_succ j))
        (hac j hjn) (hcont j hjn) (hosc j hjn)
    _ = _ := by rw [← Finset.sum_mul, hnormsum]

/-- Classical all-tagged-partitions epsilon-delta contour integral predicate.
Repeated partition points are allowed and contribute zero. -/
def HasTaggedContourIntegral (f : ℝ → ℂ) (H : ℂ → E) (a b : ℝ) (I : E) : Prop :=
  a ≤ b ∧ ∀ ε : ℝ, 0 < ε → ∃ δ : ℝ, 0 < δ ∧
    ∀ (n : ℕ) (p q : ℕ → ℝ), MonotoneOn p (Iic n) → p 0 = a → p n = b →
      (∀ j < n, q j ∈ Icc (p j) (p (j+1))) →
      (∀ j < n, p (j+1) - p j < δ) → ‖taggedSum f H p q n - I‖ < ε

/-- For every absolutely continuous path, every tagged Riemann–Stieltjes sum
converges to the genuine Bochner velocity integral.  This is an all-partitions
statement, with no Riemann–Stieltjes/velocity equality assumed in its hypotheses. -/
theorem hasTaggedContourIntegral_of_absolutelyContinuous {f : ℝ → ℂ} {a b : ℝ} {H : ℂ → E}
    (hab : a ≤ b) (hf : AbsolutelyContinuousOnInterval f a b)
    (hH : ContinuousOn H (f '' uIcc a b)) :
    HasTaggedContourIntegral f H a b
      (∫ s : ℝ in a..b, coordinateVelocity f s • H (f s)) := by
  refine ⟨hab, ?_⟩
  intro ε hε
  let V : ℝ := ∫ s : ℝ in a..b, ‖coordinateVelocity f s‖
  have hV : 0 ≤ V := intervalIntegral.integral_nonneg_of_forall hab (fun s ↦ norm_nonneg _)
  let η : ℝ := ε / (V+1)
  have hden : 0 < V+1 := by linarith
  have hη : 0 < η := div_pos hε hden
  have hsmall : V * η < ε := by
    have heq : η * (V+1) = ε := div_mul_cancel₀ ε (ne_of_gt hden)
    nlinarith
  have hcomp : ContinuousOn (fun s ↦ H (f s)) (uIcc a b) :=
    hH.comp hf.continuousOn (fun s hs ↦ mem_image_of_mem _ hs)
  have huc := isCompact_uIcc.uniformContinuousOn_of_continuous hcomp
  obtain ⟨δ,hδ,hctl⟩ := Metric.uniformContinuousOn_iff.mp huc η hη
  refine ⟨δ,hδ,?_⟩
  intro n p q hp hp0 hpn htag hmesh
  have hosc : ∀ j < n, ∀ s ∈ Icc (p j) (p (j+1)), ‖H (f (q j)) - H (f s)‖ ≤ η := by
    intro j hj s hs
    have ht := htag j hj
    have hsub : uIcc (p j) (p (j+1)) ⊆ uIcc a b :=
      uIcc_subset_uIcc (partition_mem hp hp0 hpn (Nat.le_of_lt hj))
        (partition_mem hp hp0 hpn (Nat.succ_le_of_lt hj))
    have hdist : dist (q j) s < δ := by
      have hle : dist (q j) s ≤ p (j+1) - p j := by
        rw [Real.dist_eq, abs_le]
        constructor <;> linarith [ht.1, ht.2, hs.1, hs.2]
      exact hle.trans_lt (hmesh j hj)
    have hlt := hctl (q j) (hsub (Icc_subset_uIcc ht)) s (hsub (Icc_subset_uIcc hs)) hdist
    have hlt' : ‖H (f (q j)) - H (f s)‖ < η := by
      simpa only [dist_eq_norm] using hlt
    exact hlt'.le
  exact (norm_taggedSum_sub_integral_le hf hH hp hp0 hpn hosc).trans_lt hsmall

omit [NormedSpace ℝ E] [CompleteSpace E] in
/-- Orientation-preserving continuous monotone reparameterization preserves
the classical tagged contour integral, including flat parameter segments. -/
theorem HasTaggedContourIntegral.comp_monotone {f g : ℝ → ℂ} {H : ℂ → E}
    {a b c d : ℝ} {I : E} {φ : ℝ → ℝ}
    (hI : HasTaggedContourIntegral g H c d I) (hab : a ≤ b)
    (hφc : ContinuousOn φ (uIcc a b)) (hφm : MonotoneOn φ (uIcc a b))
    (hφa : φ a = c) (hφb : φ b = d) (hfg : EqOn f (g ∘ φ) (uIcc a b)) :
    HasTaggedContourIntegral f H a b I := by
  refine ⟨hab, ?_⟩
  intro ε hε
  obtain ⟨δ,hδ,hctl⟩ := hI.2 ε hε
  have huc := isCompact_uIcc.uniformContinuousOn_of_continuous hφc
  obtain ⟨η,hη,hφctl⟩ := Metric.uniformContinuousOn_iff.mp huc δ hδ
  refine ⟨η,hη,?_⟩
  intro n p q hp hp0 hpn htag hmesh
  have hpmem (j : ℕ) (hj : j ≤ n) : p j ∈ uIcc a b := partition_mem hp hp0 hpn hj
  have hqmem (j : ℕ) (hj : j < n) : q j ∈ uIcc a b :=
    (uIcc_subset_uIcc (hpmem j (Nat.le_of_lt hj)) (hpmem (j+1) (Nat.succ_le_of_lt hj)))
      (Icc_subset_uIcc (htag j hj))
  have hp' : MonotoneOn (φ ∘ p) (Iic n) := by
    intro j hj k hk hjk
    exact hφm (hpmem j hj) (hpmem k hk) (hp hj hk hjk)
  have hp0' : (φ ∘ p) 0 = c := by simp only [Function.comp_apply,hp0,hφa]
  have hpn' : (φ ∘ p) n = d := by simp only [Function.comp_apply,hpn,hφb]
  have htag' : ∀ j < n, (φ ∘ q) j ∈ Icc ((φ ∘ p) j) ((φ ∘ p) (j+1)) := by
    intro j hj
    exact ⟨hφm (hpmem j (Nat.le_of_lt hj)) (hqmem j hj) (htag j hj).1,
      hφm (hqmem j hj) (hpmem (j+1) (Nat.succ_le_of_lt hj)) (htag j hj).2⟩
  have hmesh' : ∀ j < n, (φ ∘ p) (j+1) - (φ ∘ p) j < δ := by
    intro j hj
    have hpj : p j ≤ p (j+1) := hp (Nat.le_of_lt hj) (Nat.succ_le_of_lt hj) (Nat.le_succ j)
    have hd : dist (p (j+1)) (p j) < η := by
      rw [Real.dist_eq, abs_of_nonneg (sub_nonneg.mpr hpj)]
      exact hmesh j hj
    have h := hφctl (p (j+1)) (hpmem (j+1) (Nat.succ_le_of_lt hj))
      (p j) (hpmem j (Nat.le_of_lt hj)) hd
    have h' : |φ (p (j+1)) - φ (p j)| < δ := by simpa only [Real.dist_eq] using h
    exact (le_abs_self (φ (p (j+1)) - φ (p j))).trans_lt h' 
  have hsum : taggedSum f H p q n = taggedSum g H (φ ∘ p) (φ ∘ q) n := by
    apply Finset.sum_congr rfl
    intro j hj
    have hjn := Finset.mem_range.mp hj
    rw [hfg (hpmem (j+1) (Nat.succ_le_of_lt hjn)), hfg (hpmem j (Nat.le_of_lt hjn)),
      hfg (hqmem j hjn)]
    rfl
  rw [hsum]
  exact hctl n (φ ∘ p) (φ ∘ q) hp' hp0' hpn' htag' hmesh'

open Komorebi.PaperII.ReleaseArcLength

/-- Every continuous bounded-variation path has its original classical tagged
contour integral identified with the arclength-reconstructed Bochner velocity
integral, including the zero-length case. -/
theorem hasTaggedContourIntegral_of_rectifiable {f : ℝ → ℂ} {H : ℂ → E}
    (hv : BoundedVariationOn f (Icc (0:ℝ) 1))
    (hc : ContinuousOn f (Icc (0:ℝ) 1))
    (hH : ContinuousOn H (f '' Icc (0:ℝ) 1)) :
    HasTaggedContourIntegral f H 0 1
      (∫ s : ℝ in (0:ℝ)..1, coordinateVelocity (unitIntervalPath f) s •
        H (unitIntervalPath f s)) := by
  have h01 : (0:ℝ) ≤ 1 := by norm_num
  have hGU : LipschitzOnWith ⟨geometricLength f, ENNReal.toReal_nonneg⟩
      (unitIntervalPath f) (uIcc (0:ℝ) 1) := by
    simpa only [uIcc_of_le h01] using unitIntervalPath_lipschitz hv hc
  have hHG : ContinuousOn H (unitIntervalPath f '' uIcc (0:ℝ) 1) := by
    rw [uIcc_of_le h01, unitIntervalPath_image hv hc]
    exact hH
  have hG := hasTaggedContourIntegral_of_absolutelyContinuous h01
    hGU.absolutelyContinuousOnInterval hHG
  by_cases hL : geometricLength f = 0
  · have hfg : EqOn f (unitIntervalPath f ∘ id) (uIcc (0:ℝ) 1) := by
      intro t ht
      have ht' : t ∈ Icc (0:ℝ) 1 := by simpa only [uIcc_of_le h01] using ht
      have hmem : arcMap f t ∈ Icc 0 (geometricLength f) := by
        rw [← arcMap_image hv hc]
        exact mem_image_of_mem _ ht'
      have ha : arcMap f t = 0 := by rw [hL] at hmem; exact le_antisymm hmem.2 hmem.1
      change f t = arcPath f (geometricLength f * t)
      rw [hL, zero_mul, ← ha]
      exact (arcPath_recovers hv t ht').symm
    exact hG.comp_monotone h01 continuous_id.continuousOn (monotone_id.monotoneOn _) rfl rfl hfg
  · have hLpos : 0 < geometricLength f := lt_of_le_of_ne ENNReal.toReal_nonneg (Ne.symm hL)
    have hφc : ContinuousOn (fun t ↦ arcMap f t / geometricLength f) (uIcc (0:ℝ) 1) := by
      simpa only [uIcc_of_le h01] using (arcMap_continuous hv hc).div_const (geometricLength f)
    have hφm : MonotoneOn (fun t ↦ arcMap f t / geometricLength f) (uIcc (0:ℝ) 1) := by
      rw [uIcc_of_le h01]
      intro x hx y hy hxy
      exact div_le_div_of_nonneg_right (arcMap_monotone hv hx hy hxy) hLpos.le
    have hφa : arcMap f 0 / geometricLength f = 0 := by simp
    have hφb : arcMap f 1 / geometricLength f = 1 := by simp [hL]
    have hfg : EqOn f (unitIntervalPath f ∘ (fun t ↦ arcMap f t / geometricLength f))
        (uIcc (0:ℝ) 1) := by
      intro t ht
      have ht' : t ∈ Icc (0:ℝ) 1 := by simpa only [uIcc_of_le h01] using ht
      have hscale : geometricLength f * (arcMap f t / geometricLength f) = arcMap f t := by
        field_simp
      change f t = arcPath f (geometricLength f * (arcMap f t / geometricLength f))
      rw [hscale]
      exact (arcPath_recovers hv t ht').symm
    exact hG.comp_monotone h01 hφc hφm hφa hφb hfg

omit [NormedSpace ℝ E] [CompleteSpace E] in
/-- Every positive mesh tolerance admits an honest finite tagged partition.
This rules out a vacuous all-partitions integral predicate. -/
theorem exists_tagged_partition {a b δ : ℝ} (hab : a ≤ b) (hδ : 0 < δ) :
    ∃ (n : ℕ) (p q : ℕ → ℝ), MonotoneOn p (Iic n) ∧ p 0 = a ∧ p n = b ∧
      (∀ j < n, q j ∈ Icc (p j) (p (j+1))) ∧ (∀ j < n, p (j+1) - p j < δ) := by
  obtain ⟨n,hn⟩ := exists_nat_gt ((b-a)/δ)
  have hnp : (0:ℝ) < (n:ℝ) := (div_nonneg (sub_nonneg.mpr hab) hδ.le).trans_lt hn
  have hnz : (n:ℝ) ≠ 0 := ne_of_gt hnp
  let p : ℕ → ℝ := fun j ↦ a + (b-a) * (j:ℝ) / (n:ℝ)
  have hp : MonotoneOn p (Iic n) := by
    intro j hj k hk hjk
    dsimp [p]
    gcongr
  have hp0 : p 0 = a := by simp [p]
  have hpn : p n = b := by dsimp [p]; field_simp; ring
  refine ⟨n,p,p,hp,hp0,hpn,?_,?_⟩
  · intro j hj
    exact ⟨le_rfl, hp (Nat.le_of_lt hj) (Nat.succ_le_of_lt hj) (Nat.le_succ j)⟩
  · intro j hj
    have hstep : p (j+1) - p j = (b-a)/(n:ℝ) := by dsimp [p]; push_cast; ring
    rw [hstep,div_lt_iff₀ hnp]
    have hlt := (div_lt_iff₀ hδ).mp hn
    nlinarith

omit [NormedSpace ℝ E] [CompleteSpace E] in
/-- Classical tagged contour integrals have a unique value. -/
theorem HasTaggedContourIntegral.unique {f : ℝ → ℂ} {H : ℂ → E} {a b : ℝ} {I J : E}
    (hI : HasTaggedContourIntegral f H a b I) (hJ : HasTaggedContourIntegral f H a b J) : I = J := by
  apply eq_of_forall_dist_le
  intro ε hε
  obtain ⟨δI,hδI,hctlI⟩ := hI.2 (ε/2) (by positivity)
  obtain ⟨δJ,hδJ,hctlJ⟩ := hJ.2 (ε/2) (by positivity)
  obtain ⟨n,p,q,hp,hp0,hpn,htag,hmesh⟩ :=
    exists_tagged_partition hI.1 (lt_min hδI hδJ)
  have hSI := hctlI n p q hp hp0 hpn htag (fun j hj ↦ (hmesh j hj).trans_le (min_le_left _ _))
  have hSJ := hctlJ n p q hp hp0 hpn htag (fun j hj ↦ (hmesh j hj).trans_le (min_le_right _ _))
  have htri := dist_triangle I (taggedSum f H p q n) J
  have hSI' : dist I (taggedSum f H p q n) < ε/2 := by
    simpa only [dist_eq_norm,norm_sub_rev] using hSI
  have hSJ' : dist (taggedSum f H p q n) J < ε/2 := by simpa only [dist_eq_norm] using hSJ
  linarith

/-- The classical contour integral defined by its unique limit of all tagged
Riemann–Stieltjes sums; zero is only the undefined-case convention. -/
def taggedContourIntegral (f : ℝ → ℂ) (H : ℂ → E) (a b : ℝ) : E := by
  classical
  exact if h : ∃ I, HasTaggedContourIntegral f H a b I then Classical.choose h else 0

omit [NormedSpace ℝ E] [CompleteSpace E] in
/-- A genuine all-tagged-partitions limit identifies the classical integral. -/
theorem HasTaggedContourIntegral.taggedContourIntegral_eq {f : ℝ → ℂ} {H : ℂ → E}
    {a b : ℝ} {I : E} (hI : HasTaggedContourIntegral f H a b I) :
    taggedContourIntegral f H a b = I := by
  classical
  have hex : ∃ J, HasTaggedContourIntegral f H a b J := ⟨I,hI⟩
  simp only [taggedContourIntegral,dite_eq_left hex]
  exact (Classical.choose_spec hex).unique hI

/-- Original continuous rectifiable contours integrate by the constructed
arclength velocity, as a proved comparison of two distinct definitions. -/
theorem taggedContourIntegral_eq_velocity_of_rectifiable {f : ℝ → ℂ} {H : ℂ → E}
    (hv : BoundedVariationOn f (Icc (0:ℝ) 1))
    (hc : ContinuousOn f (Icc (0:ℝ) 1))
    (hH : ContinuousOn H (f '' Icc (0:ℝ) 1)) :
    taggedContourIntegral f H 0 1 =
      ∫ s : ℝ in (0:ℝ)..1, coordinateVelocity (unitIntervalPath f) s • H (unitIntervalPath f s) :=
  (hasTaggedContourIntegral_of_rectifiable hv hc hH).taggedContourIntegral_eq

open Komorebi.PaperII.ReleaseAnalyticContour
open Komorebi.PaperII.ReleaseRectifiableCycle

/-- Sum of the original classical rectifiable contour integrals equals the
actual constructed IntegralCycle line integral, retaining each occurrence. -/
theorem sum_taggedContourIntegral_eq_lineIntegral (n : ℕ) (f : Fin n → ℝ → ℂ)
    (hv : ∀ i, BoundedVariationOn (f i) (Icc (0:ℝ) 1))
    (hc : ∀ i, ContinuousOn (f i) (Icc (0:ℝ) 1))
    (hclosed : ∀ i, f i 1 = f i 0) {H : ℂ → E}
    (hH : ∀ i, ContinuousOn H (f i '' Icc (0:ℝ) 1)) :
    (∑ i : Fin n, taggedContourIntegral (f i) H 0 1) =
      (cycleOfRectifiable n f hv hc hclosed).lineIntegral H := by
  unfold IntegralCycle.lineIntegral
  apply Finset.sum_congr rfl
  intro i hi
  rw [taggedContourIntegral_eq_velocity_of_rectifiable (hv i) (hc i) (hH i)]
  change (∫ s : ℝ in (0:ℝ)..1, coordinateVelocity (unitIntervalPath (f i)) s • H (unitIntervalPath (f i) s)) =
    ∫ s : ℝ in (0:ℝ)..1, coordinateVelocity (unitIntervalPath (f i)) s •
      H ((cycleOfRectifiable n f hv hc hclosed).curve i s)
  apply intervalIntegral.integral_congr
  intro s hs
  exact congrArg (fun z : ℂ ↦ coordinateVelocity (unitIntervalPath (f i)) s • H z)
    (curve_cycleOfRectifiable n f hv hc hclosed i s
      (by simpa only [uIcc_of_le (by norm_num : (0:ℝ) ≤ 1)] using hs)).symm

end Komorebi.PaperII.ReleaseRectifiableRSError
