module
public import Euler.SourceTranslation
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

/-- Coefficient construction for restriction to an affine dyadic disc. -/
def restrictedAffine (f : Series) (a s : D) : Series :=
  mk (fun n => s^n * rjet n f a)

@[simp] lemma coeff_restrictedAffine (f : Series) (a s : D) (n : ℕ) :
    coeff n (restrictedAffine f a s)=s^n*rjet n f a := by
  simp [restrictedAffine]

lemma restrictedAffine_restricted (f : Series) (a s : D) (hs : ‖s‖<1) :
    Restricted (restrictedAffine f a s) := by
  rw [restricted_iff]
  apply squeeze_zero (g := fun n => ‖s‖^n) (fun _ => norm_nonneg _)
  · intro n
    rw [coeff_restrictedAffine,norm_mul,norm_pow]
    exact mul_le_of_le_one_right (by positivity) (PadicInt.norm_le_one _)
  · exact tendsto_pow_atTop_nhds_zero_of_lt_one (norm_nonneg _) hs

lemma pair_add_tendsto_cofinite :
    Tendsto (fun p : ℕ×ℕ => p.1+p.2) cofinite atTop := by
  rw [← Nat.cofinite_eq_atTop]
  apply Filter.Tendsto.cofinite_of_finite_preimage_singleton
  intro n
  exact (Finset.antidiagonal n).finite_toSet.subset (by
    intro p hp
    simpa only [Set.mem_preimage,Set.mem_singleton_iff,Finset.mem_coe,
      Finset.mem_antidiagonal] using hp)

lemma summable_restricted_affine_double {f : Series} (hf : Restricted f)
    (a s x : D) :
    Summable (fun p : ℕ×ℕ => coeff (p.1+p.2) f *
      ((p.1+p.2).choose p.1:D) * (s*x)^p.1 * a^p.2) := by
  apply NonarchimedeanAddGroup.summable_of_tendsto_cofinite_zero
  rw [tendsto_zero_iff_norm_tendsto_zero]
  apply squeeze_zero (g := fun p : ℕ×ℕ => ‖coeff (p.1+p.2) f‖)
    (fun _ => norm_nonneg _)
  · intro p
    calc
      _ = ‖coeff (p.1+p.2) f *
        (((p.1+p.2).choose p.1:D)*(s*x)^p.1*a^p.2)‖ := by congr 1; ring
      _ ≤ ‖coeff (p.1+p.2) f‖ := by
        rw [norm_mul]
        exact mul_le_of_le_one_right (norm_nonneg _) (PadicInt.norm_le_one _)
  · exact ((restricted_iff f).mp hf).comp pair_add_tendsto_cofinite


/-- Affine localization evaluates the full original infinite function. -/
theorem restrictedAffine_reval {f : Series} (hf : Restricted f) (a s x : D) :
    reval (restrictedAffine f a s) x=reval f (a+s*x) := by
  let T : ℕ×ℕ → D := fun p => coeff (p.1+p.2) f *
    ((p.1+p.2).choose p.1:D)*(s*x)^p.1*a^p.2
  have hT : Summable T := summable_restricted_affine_double hf a s x
  have hh (n : ℕ) : coeff n (restrictedAffine f a s)*x^n=∑' m,T (n,m) := by
    rw [coeff_restrictedAffine,rjet,reval]
    simp only [coeff_hasseSeries]
    have hs := summable_reval (restricted_hasseSeries hf n) a
    simp only [coeff_hasseSeries] at hs
    rw [← hs.tsum_mul_left (s^n),← (hs.mul_left (s^n)).tsum_mul_right (x^n)]
    apply tsum_congr
    intro m
    dsimp [T]
    rw [Nat.add_comm m n]
    ring
  unfold reval
  simp_rw [hh]
  rw [← hT.tsum_prod,tsum_antidiagonal_of_summable hT]
  apply tsum_congr
  intro n
  have he : ∑ p ∈ Finset.antidiagonal n, T p =
      coeff n f * ∑ i ∈ Finset.range (n+1), (s*x)^i*a^(n-i)*(n.choose i:D) := by
    rw [Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk,Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro i hi
    have hin : i≤n := by simpa only [Finset.mem_range,Nat.lt_succ_iff] using hi
    dsimp [T]
    rw [Nat.add_sub_of_le hin]
    ring
  rw [he,← add_pow,add_comm (s*x) a]


/-- A proper dyadic affine restriction has constant complete binary reduction. -/
lemma restrictedAffine_red (f : Series) (a s : D) (hs : red s=0) (n : ℕ) :
    red (coeff n (restrictedAffine f a s)) =
      (Polynomial.C (red (reval f a))).coeff n := by
  cases n with
  | zero => simp [coeff_restrictedAffine,rjet_zero]
  | succ n => simp [coeff_restrictedAffine,map_mul,map_pow,hs]

lemma restrictedAffine_coeff_norm (f : Series) (a s : D) (n : ℕ) :
    ‖coeff n (restrictedAffine f a s)‖≤‖s‖^n := by
  rw [coeff_restrictedAffine,norm_mul,norm_pow]
  exact mul_le_of_le_one_right (by positivity) (PadicInt.norm_le_one _)

/-- The coefficient error gains one copy of the radius in each Taylor order. -/
lemma restrictedAffine_jet_error {f g : Series} (hf : Restricted f) (hg : Restricted g)
    (P n : ℕ) (h : ∀ m, redPow P (coeff m f)=redPow P (coeff m g)) (a s : D) :
    ‖coeff n (restrictedAffine f a s)-coeff n (restrictedAffine g a s)‖
      ≤ ‖s‖^n * (2:ℝ)^(-(P:ℤ)) := by
  have hz : redPow P (rjet n f a-rjet n g a)=0 := by
    have hc : ∀ m, redPow P (coeff m (hasseSeries n f-hasseSeries n g))=0 := by
      intro m
      simp only [map_sub,coeff_hasseSeries,map_mul,map_natCast,h]
      simp
    have hsub : Restricted (hasseSeries n f-hasseSeries n g) := by
      simpa only [sub_eq_add_neg] using
        PowerSeries.isRestricted.add 1 (restricted_hasseSeries hf n)
          (PowerSeries.isRestricted.neg 1 (restricted_hasseSeries hg n))
    have hh := reval_residue_polynomial hsub
      P (0:Polynomial (ZMod (2^P))) (by simpa using hc) a
    change redPow P (reval (hasseSeries n f) a-reval (hasseSeries n g) a)=0
    simpa only [reval_sub (restricted_hasseSeries hf n) (restricted_hasseSeries hg n),
      rjet,Polynomial.eval_zero] using hh
  have hb := (redPow_zero_iff_norm P _).mp hz
  rw [coeff_restrictedAffine,coeff_restrictedAffine,← mul_sub,norm_mul,norm_pow]
  exact mul_le_mul_of_nonneg_left hb (by positivity)

end Komorebi.Euler
