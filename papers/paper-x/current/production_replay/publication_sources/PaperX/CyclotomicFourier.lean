module
public import PaperX.CyclotomicPrimeBoundary

/-! Exact Fourier inversion on the actual unramified prime-ideal family. -/
@[expose] public section
noncomputable section
open NumberField Chebotarev Filter Set
open PaperX.ArtinLocalFactors PaperX.CyclotomicPrimeBoundary
open scoped Topology
namespace PaperX.CyclotomicFourier
variable (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
  [Algebra K L] [IsGalois K L]

def unramifiedSet : Set (Ideal (𝓞 K)) := {p | p.IsPrime ∧ UnramifiedIn K L p}
def ramifiedSet : Set (Ideal (𝓞 K)) := {p | p.IsPrime ∧ p ≠ ⊥ ∧ ¬UnramifiedIn K L p}
def classSet (σ : Gal(L/K)) : Set (Ideal (𝓞 K)) :=
  {p | p.IsPrime ∧ UnramifiedIn K L p ∧ frobeniusClass K L p = ConjClasses.mk σ}

/-- Complex prime weights are the casts of the real norm weights. -/
theorem weight_cast (n : ℕ) (s : ℝ) :
    (((n : ℝ) ^ (-s) : ℝ) : ℂ) = (n : ℂ) ^ (-(s : ℂ)) := by
  rw [Complex.ofReal_cpow (Nat.cast_nonneg n) (-s)]
  simp only [Complex.ofReal_natCast, Complex.ofReal_neg]

def unramifiedEquiv : UPrime K L ≃
    {p : Ideal (𝓞 K) // p ∈ unramifiedSet K L ∧ p.IsPrime ∧ p ≠ ⊥} where
  toFun p := ⟨p.1, p.2, p.2.1, p.2.2.ne_bot⟩
  invFun p := ⟨p.1, p.2.1⟩
  left_inv _ := rfl
  right_inv _ := rfl

theorem trivial_prime_sum (s : ℝ) :
    twistedPrimeSum K L 1 s = (primeIdealZetaSum (unramifiedSet K L) s : ℂ) := by
  rw [primeIdealZetaSum, Complex.ofReal_tsum]
  rw [← (unramifiedEquiv K L).tsum_eq
    (fun p ↦ (((Ideal.absNorm p.1 : ℝ) ^ (-s) : ℝ) : ℂ))]
  apply tsum_congr
  intro p
  simp [EulerLogBoundary.term, characterWeight, primeNorm, unramifiedEquiv, weight_cast]

theorem unramified_density : HasDirichletDensity (unramifiedSet K L) 1 := by
  have hdisj : Disjoint (unramifiedSet K L) (ramifiedSet K L) :=
    Set.disjoint_left.mpr (fun _ hu hr ↦ hr.2.2 hu.2)
  have heq {s : ℝ} (hs : 1 < s) :
      primeIdealZetaSum (unramifiedSet K L) s + primeIdealZetaSum (ramifiedSet K L) s =
        normalizer K s := by
    rw [← primeIdealZetaSum_union_of_disjoint hdisj hs]
    exact primeIdealZetaSum_eq_univ_of_forall_prime_mem (fun p hp hn ↦ by
      by_cases h : UnramifiedIn K L p
      · exact Or.inl ⟨hp, h⟩
      · exact Or.inr ⟨hp, hn, h⟩) s
  have hr := hasDirichletDensity_of_finite K (finite_ramifiedIn K L)
  have h : Tendsto (fun s ↦ 1 - primeIdealZetaSum (ramifiedSet K L) s / normalizer K s)
      (𝓝[>] 1) (𝓝 (1 : ℝ)) := by
    simpa only [sub_zero, HasDirichletDensity, ramifiedSet, normalizer] using
      (tendsto_const_nhds (x := (1 : ℝ))).sub hr
  apply h.congr'
  filter_upwards [self_mem_nhdsWithin,
    (primeIdealZetaSum_univ_tendsto_atTop K).eventually_gt_atTop 0] with s hs hn
  have he := heq hs
  change 1 - primeIdealZetaSum (ramifiedSet K L) s / normalizer K s =
    primeIdealZetaSum (unramifiedSet K L) s / normalizer K s
  have hn' : normalizer K s ≠ 0 := ne_of_gt hn
  calc 1 - primeIdealZetaSum (ramifiedSet K L) s / normalizer K s
      = (normalizer K s - primeIdealZetaSum (ramifiedSet K L) s) / normalizer K s := by
          rw [sub_div, div_self hn']
    _ = _ := congrArg (· / normalizer K s) (by linarith [he])

theorem trivial_prime_normalized :
    Tendsto (fun s ↦ twistedPrimeSum K L 1 s / (normalizer K s : ℂ))
      (𝓝[>] 1) (𝓝 1) := by
  have h := (Complex.continuous_ofReal.tendsto 1).comp (unramified_density K L)
  simpa only [Function.comp_def, Complex.ofReal_div, Complex.ofReal_one,
    trivial_prime_sum, normalizer, HasDirichletDensity] using h

variable [IsMulCommutative Gal(L/K)]

/-- In this abelian setting, specifying the class specifies its representative. -/
theorem out_eq_iff (p : Ideal (𝓞 K)) (σ : Gal(L/K)) :
    (frobeniusClass K L p).out = σ ↔ frobeniusClass K L p = ConjClasses.mk σ := by
  have h : ConjClasses.mk (frobeniusClass K L p).out = frobeniusClass K L p := Quotient.out_eq _
  constructor
  · intro he; rw [← h, he]
  · intro he
    let : CommMonoid Gal(L/K) := IsMulCommutative.instCommMonoid
    exact isConj_iff_eq.mp (ConjClasses.mk_eq_mk_iff_isConj.mp (h.trans he))

def classEquiv (σ : Gal(L/K)) :
    {p : UPrime K L // (frobeniusClass K L p.1).out = σ} ≃
      {p : Ideal (𝓞 K) // p ∈ classSet K L σ ∧ p.IsPrime ∧ p ≠ ⊥} where
  toFun p := ⟨p.1.1, ⟨p.1.2.1, p.1.2.2, (out_eq_iff K L _ σ).mp p.2⟩,
    p.1.2.1, p.1.2.2.ne_bot⟩
  invFun p := ⟨⟨p.1, p.2.1.1, p.2.1.2.1⟩, (out_eq_iff K L _ σ).mpr p.2.1.2.2⟩
  left_inv _ := rfl
  right_inv _ := rfl

theorem class_prime_sum (σ : Gal(L/K)) (s : ℝ) :
    (∑' p : {p : UPrime K L // (frobeniusClass K L p.1).out = σ},
      (Ideal.absNorm p.1.1 : ℂ) ^ (-(s : ℂ))) =
        (primeIdealZetaSum (classSet K L σ) s : ℂ) := by
  rw [primeIdealZetaSum, Complex.ofReal_tsum,
    ← (classEquiv K L σ).tsum_eq (fun p ↦ (((Ideal.absNorm p.1 : ℝ) ^ (-s) : ℝ) : ℂ))]
  exact tsum_congr (fun p ↦ (weight_cast (Ideal.absNorm p.1.1) s).symm)

local instance characterFintype : Fintype (Character K L) := Fintype.ofFinite _

omit [IsGalois K L] in
open Classical in
theorem character_column (σ τ : Gal(L/K)) :
    (∑ χ : Character K L, ((χ σ : ℂ)⁻¹ * (χ τ : ℂ))) =
      if τ = σ then (Nat.card Gal(L/K) : ℂ) else 0 := by
  classical
  let : CommGroup Gal(L/K) := { mul_comm := mul_comm' }
  have : NeZero (Monoid.exponent Gal(L/K)) := ⟨Monoid.exponent_ne_zero_of_finite⟩
  by_cases h : τ = σ
  · subst h
    simp only [inv_mul_cancel₀ (Units.ne_zero _), Finset.sum_const,
      Finset.card_univ, nsmul_eq_mul, mul_one, ← Nat.card_eq_fintype_card]
    exact congrArg Nat.cast (CommGroup.card_monoidHom_of_hasEnoughRootsOfUnity Gal(L/K) ℂ)
  · rw [ite_eq_right h]
    have he : ∀ χ : Character K L, (χ σ : ℂ)⁻¹ * (χ τ : ℂ) = (χ (σ⁻¹ * τ) : ℂ) := by
      intro χ; simp only [map_mul, map_inv, Units.val_mul, Units.val_inv_eq_inv_val]
    rw [Finset.sum_congr rfl (fun χ _ ↦ he χ)]
    exact sum_char_apply_eq_zero_of_ne_one (fun hh ↦ h (inv_mul_eq_one.mp hh).symm)

set_option backward.isDefEq.respectTransparency false in
/-- Exact Fourier inversion, with complex phases retained. -/
theorem fourier_identity (σ : Gal(L/K)) {s : ℝ} (hs : 1 < s) :
    (∑ χ : Character K L, (χ σ : ℂ)⁻¹ * twistedPrimeSum K L χ s) =
      (Nat.card Gal(L/K) : ℂ) * (primeIdealZetaSum (classSet K L σ) s : ℂ) := by
  classical
  let W : UPrime K L → ℂ := fun p ↦ (Ideal.absNorm p.1 : ℂ) ^ (-(s : ℂ))
  have hswap : (∑ χ : Character K L, ∑' p : UPrime K L,
      (χ σ : ℂ)⁻¹ * ((χ (frobeniusClass K L p.1).out : ℂ) * W p)) =
      ∑' p : UPrime K L, ∑ χ : Character K L,
        (χ σ : ℂ)⁻¹ * ((χ (frobeniusClass K L p.1).out : ℂ) * W p) :=
    (Summable.tsum_finsetSum (s := (Finset.univ : Finset (Character K L)))
      (fun χ _ ↦ (twistedPrimeSum_summable K L χ hs).mul_left ((χ σ : ℂ)⁻¹))).symm
  calc (∑ χ : Character K L, (χ σ : ℂ)⁻¹ * twistedPrimeSum K L χ s)
      = ∑ χ : Character K L, ∑' p : UPrime K L,
          (χ σ : ℂ)⁻¹ * ((χ (frobeniusClass K L p.1).out : ℂ) * W p) := by
        unfold twistedPrimeSum EulerLogBoundary.primeSum EulerLogBoundary.term characterWeight primeNorm
        simp only [tsum_mul_left, W]
    _ = ∑' p : UPrime K L, (Nat.card Gal(L/K) : ℂ) *
        (if (frobeniusClass K L p.1).out = σ then W p else 0) := by
        rw [hswap]; apply tsum_congr; intro p
        simp_rw [← mul_assoc]
        rw [← Finset.sum_mul, character_column K L σ (frobeniusClass K L p.1).out]
        split_ifs <;> simp
    _ = (Nat.card Gal(L/K) : ℂ) *
        ∑' p : {p : UPrime K L // (frobeniusClass K L p.1).out = σ}, W p.1 := by
        rw [tsum_mul_left]
        congr 1
        exact (tsum_subtype
          {p : UPrime K L | (frobeniusClass K L p.1).out = σ} W).symm
    _ = _ := by rw [class_prime_sum K L σ s]

end PaperX.CyclotomicFourier
