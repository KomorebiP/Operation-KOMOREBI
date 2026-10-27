module

public import Mathlib.Basic.Real.Basic
public import Mathlib.Data.Matrix.Mul
public import Mathlib.Tactic.FieldSimp
public import Mathlib.Tactic.Ring
public import Mathlib.MeasureTheory.Integral.IntervalIntegral.Basic
public import Mathlib.MeasureTheory.Integral.Bochner.ContinuousLinearMap
public import Mathlib.Analysis.SpecialFunctions.Gamma.Basic
public import Mathlib.Analysis.SpecialFunctions.Exp
public import Mathlib.Analysis.SpecialFunctions.ExpDeriv
public import Mathlib.Analysis.SpecialFunctions.Exponential
public import Mathlib.Analysis.Calculus.Deriv.Add
public import Mathlib.Analysis.Calculus.Deriv.Comp
public import Mathlib.MeasureTheory.Integral.IntervalIntegral.FundThmCalculus
public import Mathlib.Analysis.Calculus.Deriv.Mul
public import Mathlib.Analysis.SpecialFunctions.Integrals.Basic
public import Mathlib.Analysis.Normed.Group.FunctionSeries
public import Mathlib.Analysis.SpecificLimits.Normed
public import Mathlib.Analysis.Normed.Algebra.Exponential
public import Mathlib.Analysis.Normed.Operator.NormedSpace
public import Mathlib.Probability.Distributions.Gaussian.HasGaussianLaw.Independence
public import Mathlib.Probability.BrownianMotion.Basic
public import Mathlib.Probability.Moments.Variance
public import Mathlib.Probability.Distributions.Gaussian.HasGaussianLaw.Basic
public import Mathlib.Analysis.CStarAlgebra.Basic

@[expose] public section

noncomputable section
set_option autoImplicit false

namespace Komorebi.UnifiedInference

open scoped BigOperators

/-! ## 1. Finite Bayesian packet normalization -/

universe u

variable {ι : Type u} [Fintype ι]

/-- Total finite packet evidence.  This is the finite packet-mass analogue of
`Z = ∑ᵢ pᵢ ℓᵢ`. -/
def evidenceNormalizer (p ℓ : ι → ℝ) : ℝ :=
  ∑ i, p i * ℓ i

/-- Bayesian update of finite packet masses. -/
def bayesPacketUpdate (p ℓ : ι → ℝ) (i : ι) : ℝ :=
  p i * ℓ i / evidenceNormalizer p ℓ

/-- The updated packet masses normalize exactly when the evidence is nonzero. -/
theorem bayesPacketUpdate_sum
    (p ℓ : ι → ℝ) (hZ : evidenceNormalizer p ℓ ≠ 0) :
    ∑ i, bayesPacketUpdate p ℓ i = 1 := by
  unfold bayesPacketUpdate
  simp only [div_eq_mul_inv]
  rw [← Finset.sum_mul]
  change evidenceNormalizer p ℓ * (evidenceNormalizer p ℓ)⁻¹ = 1
  exact mul_inv_cancel₀ hZ

/-- Positivity of the finite Bayesian packet update. -/
theorem bayesPacketUpdate_nonneg
    (p ℓ : ι → ℝ)
    (hp : ∀ i, 0 ≤ p i) (hℓ : ∀ i, 0 ≤ ℓ i)
    (hZ : 0 < evidenceNormalizer p ℓ) (i : ι) :
    0 ≤ bayesPacketUpdate p ℓ i := by
  unfold bayesPacketUpdate
  exact div_nonneg (mul_nonneg (hp i) (hℓ i)) (le_of_lt hZ)

/-- The first-step normalizer factors out of the second evidence calculation. -/
theorem sequential_evidence_normalizer
    (p ℓ₁ ℓ₂ : ι → ℝ) :
    evidenceNormalizer (bayesPacketUpdate p ℓ₁) ℓ₂ =
      evidenceNormalizer p (fun i => ℓ₁ i * ℓ₂ i) /
        evidenceNormalizer p ℓ₁ := by
  classical
  calc
    evidenceNormalizer (bayesPacketUpdate p ℓ₁) ℓ₂ =
        ∑ i, (p i * ℓ₁ i * ℓ₂ i) / evidenceNormalizer p ℓ₁ := by
      unfold evidenceNormalizer bayesPacketUpdate
      apply Finset.sum_congr rfl
      intro i hi
      simp only [evidenceNormalizer]
      ring
    _ = (∑ i, p i * ℓ₁ i * ℓ₂ i) / evidenceNormalizer p ℓ₁ := by
      simp only [div_eq_mul_inv]
      rw [← Finset.sum_mul]
    _ = evidenceNormalizer p (fun i => ℓ₁ i * ℓ₂ i) /
          evidenceNormalizer p ℓ₁ := by
      congr 1
      unfold evidenceNormalizer
      apply Finset.sum_congr rfl
      intro i hi
      ring

/-- Sequential finite Bayesian evidence is associative: updating by `ℓ₁` and
then `ℓ₂` is exactly the same as one update by the pointwise product. -/
theorem bayesPacketUpdate_sequential
    (p ℓ₁ ℓ₂ : ι → ℝ)
    (hZ₁ : evidenceNormalizer p ℓ₁ ≠ 0)
    (hZ₁₂ : evidenceNormalizer p (fun i => ℓ₁ i * ℓ₂ i) ≠ 0) :
    bayesPacketUpdate (bayesPacketUpdate p ℓ₁) ℓ₂ =
      bayesPacketUpdate p (fun i => ℓ₁ i * ℓ₂ i) := by
  funext i
  change (bayesPacketUpdate p ℓ₁ i * ℓ₂ i) /
      evidenceNormalizer (bayesPacketUpdate p ℓ₁) ℓ₂ =
    (p i * (ℓ₁ i * ℓ₂ i)) /
      evidenceNormalizer p (fun j => ℓ₁ j * ℓ₂ j)
  rw [sequential_evidence_normalizer p ℓ₁ ℓ₂]
  unfold bayesPacketUpdate
  field_simp [hZ₁, hZ₁₂]

/-- Multiplying all likelihoods by the same nonzero scalar does not change the
normalized posterior packet masses. -/
theorem bayesPacketUpdate_scale_evidence
    (p ℓ : ι → ℝ) (c : ℝ)
    (hc : c ≠ 0) (hZ : evidenceNormalizer p ℓ ≠ 0) :
    bayesPacketUpdate p (fun i => c * ℓ i) = bayesPacketUpdate p ℓ := by
  funext i
  have hnorm : evidenceNormalizer p (fun i => c * ℓ i) =
      c * evidenceNormalizer p ℓ := by
    unfold evidenceNormalizer
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro j hj
    ring
  unfold bayesPacketUpdate
  rw [hnorm]
  field_simp [hc, hZ]


/-! ## 1b. Finite Bayesian packet factorization with internal states -/

universe uσ

section FinitePacketBayes

variable {σ : Type uσ} [Fintype σ]

/-- Prior mass carried by one packet. -/
def packetMass (μ : ι → σ → ℝ) (i : ι) : ℝ :=
  ∑ x, μ i x

/-- Unnormalized evidence contributed by one packet. -/
def packetFineEvidence (μ L : ι → σ → ℝ) (i : ι) : ℝ :=
  ∑ x, μ i x * L i x

/-- Conditional evidence within a packet. -/
def packetLikelihood (μ L : ι → σ → ℝ) (i : ι) : ℝ :=
  packetFineEvidence μ L i / packetMass μ i

/-- Total evidence across all packets and internal states. -/
def globalFineEvidence (μ L : ι → σ → ℝ) : ℝ :=
  ∑ i, packetFineEvidence μ L i

/-- Fine-state posterior mass. -/
def posteriorFineMass (μ L : ι → σ → ℝ) (i : ι) (x : σ) : ℝ :=
  μ i x * L i x / globalFineEvidence μ L

/-- Posterior mass of one packet, obtained by summing its fine states. -/
def posteriorPacketMass (μ L : ι → σ → ℝ) (i : ι) : ℝ :=
  ∑ x, posteriorFineMass μ L i x

/-- Conditional posterior distribution inside one packet. -/
def posteriorConditionalMass (μ L : ι → σ → ℝ) (i : ι) (x : σ) : ℝ :=
  μ i x * L i x / packetFineEvidence μ L i

omit [Fintype ι] in
/-- Packet mass times packet likelihood recovers the packet's unnormalized
fine-state evidence. -/
theorem packetMass_mul_packetLikelihood
    (μ L : ι → σ → ℝ) (i : ι) (hp : packetMass μ i ≠ 0) :
    packetMass μ i * packetLikelihood μ L i = packetFineEvidence μ L i := by
  unfold packetLikelihood
  field_simp [hp]

/-- Under nonzero prior mass in every packet, the global evidence decomposes as
`∑ᵢ pᵢ ℓᵢ`. -/
theorem globalFineEvidence_eq_sum_packet_evidence
    (μ L : ι → σ → ℝ) (hp : ∀ i, packetMass μ i ≠ 0) :
    globalFineEvidence μ L = ∑ i, packetMass μ i * packetLikelihood μ L i := by
  unfold globalFineEvidence
  apply Finset.sum_congr rfl
  intro i hi
  exact (packetMass_mul_packetLikelihood μ L i (hp i)).symm

/-- Summing the fine posterior inside one packet gives its fine evidence divided
by the global normalizer. -/
theorem posteriorPacketMass_eq_evidence_div
    (μ L : ι → σ → ℝ) (i : ι) :
    posteriorPacketMass μ L i =
      packetFineEvidence μ L i / globalFineEvidence μ L := by
  unfold posteriorPacketMass posteriorFineMass packetFineEvidence
  simp only [div_eq_mul_inv]
  rw [← Finset.sum_mul]

/-- Finite exact Bayesian packet factorization:
`pᵢ⁺ = pᵢ ℓᵢ / ∑ⱼ pⱼ ℓⱼ`. -/
theorem posteriorPacketMass_factorization
    (μ L : ι → σ → ℝ) (hp : ∀ i, packetMass μ i ≠ 0) (i : ι) :
    posteriorPacketMass μ L i =
      packetMass μ i * packetLikelihood μ L i /
        (∑ j, packetMass μ j * packetLikelihood μ L j) := by
  rw [posteriorPacketMass_eq_evidence_div]
  rw [← packetMass_mul_packetLikelihood μ L i (hp i)]
  rw [← globalFineEvidence_eq_sum_packet_evidence μ L hp]

/-- The finite fine-state posterior is globally normalized when its evidence is
nonzero. -/
theorem posteriorFineMass_sum
    (μ L : ι → σ → ℝ) (hZ : globalFineEvidence μ L ≠ 0) :
    ∑ i, ∑ x, posteriorFineMass μ L i x = 1 := by
  unfold posteriorFineMass
  simp only [div_eq_mul_inv]
  calc
    (∑ i, ∑ x, μ i x * L i x * (globalFineEvidence μ L)⁻¹) =
        ∑ i, (∑ x, μ i x * L i x) * (globalFineEvidence μ L)⁻¹ := by
      apply Finset.sum_congr rfl
      intro i hi
      rw [← Finset.sum_mul]
    _ = (∑ i, ∑ x, μ i x * L i x) * (globalFineEvidence μ L)⁻¹ := by
      rw [← Finset.sum_mul]
    _ = globalFineEvidence μ L * (globalFineEvidence μ L)⁻¹ := by
      rfl
    _ = 1 := mul_inv_cancel₀ hZ

/-- Conditioning the fine posterior on a packet recovers the packetwise
Bayesian law. -/
theorem posteriorFine_over_packet
    (μ L : ι → σ → ℝ) (i : ι) (x : σ)
    (hZ : globalFineEvidence μ L ≠ 0)
    (hEi : packetFineEvidence μ L i ≠ 0) :
    posteriorFineMass μ L i x / posteriorPacketMass μ L i =
      posteriorConditionalMass μ L i x := by
  rw [posteriorPacketMass_eq_evidence_div]
  unfold posteriorFineMass posteriorConditionalMass
  field_simp [hZ, hEi]

end FinitePacketBayes


/-! ## 2. Algebraic core of strong Markov lumpability -/

universe v w

variable {R : Type*} [CommSemiring R]
variable {α : Type v} {β : Type w}
variable [Fintype α] [Fintype β] [DecidableEq α] [DecidableEq β]

/-- The algebraic intertwining relation underlying exact Markov lumpability. -/
def Intertwines
    (Q : Matrix α α R) (C : Matrix α β R) (Qbar : Matrix β β R) : Prop :=
  Q * C = C * Qbar

/-- An intertwiner propagates through every natural power. -/
theorem intertwines_pow
    (Q : Matrix α α R) (C : Matrix α β R) (Qbar : Matrix β β R)
    (h : Intertwines Q C Qbar) (n : ℕ) :
    Q ^ n * C = C * Qbar ^ n := by
  induction n with
  | zero => simp
  | succ n ih =>
      simp only [pow_succ]
      calc
        (Q ^ n * Q) * C = Q ^ n * (Q * C) := Matrix.mul_assoc _ _ _
        _ = Q ^ n * (C * Qbar) := by rw [h]
        _ = (Q ^ n * C) * Qbar := (Matrix.mul_assoc _ _ _).symm
        _ = (C * Qbar ^ n) * Qbar := by rw [ih]
        _ = C * (Qbar ^ n * Qbar) := Matrix.mul_assoc _ _ _

/-- A finite polynomial in an intertwined generator also intertwines. -/
theorem intertwines_finset_polynomial
    (Q : Matrix α α R) (C : Matrix α β R) (Qbar : Matrix β β R)
    (h : Intertwines Q C Qbar)
    (s : Finset ℕ) (a : ℕ → R) :
    (∑ n ∈ s, a n • (Q ^ n)) * C =
      C * (∑ n ∈ s, a n • (Qbar ^ n)) := by
  calc
    (∑ n ∈ s, a n • (Q ^ n)) * C =
        ∑ n ∈ s, (a n • (Q ^ n)) * C := by
          simp only [Matrix.sum_mul]
    _ = ∑ n ∈ s, a n • ((Q ^ n) * C) := by
      apply Finset.sum_congr rfl
      intro n hn
      rw [Matrix.smul_mul]
    _ = ∑ n ∈ s, a n • (C * (Qbar ^ n)) := by
      apply Finset.sum_congr rfl
      intro n hn
      rw [intertwines_pow Q C Qbar h n]
    _ = C * (∑ n ∈ s, a n • (Qbar ^ n)) := by
      simp only [Matrix.mul_sum, Matrix.mul_smul]

/-- Exact coarse propagation for a row state follows from the intertwining
identity for every discrete power. -/
theorem coarse_propagation_pow
    (Q : Matrix α α R) (C : Matrix α β R) (Qbar : Matrix β β R)
    (h : Intertwines Q C Qbar) (p : Matrix (Fin 1) α R) (n : ℕ) :
    (p * (Q ^ n)) * C = (p * C) * (Qbar ^ n) := by
  calc
    (p * (Q ^ n)) * C = p * ((Q ^ n) * C) := Matrix.mul_assoc _ _ _
    _ = p * (C * (Qbar ^ n)) := by rw [intertwines_pow Q C Qbar h n]
    _ = (p * C) * (Qbar ^ n) := (Matrix.mul_assoc _ _ _).symm



/-- Recursive exact accumulation of an intertwining residual under repeated
propagation.  `n=0` has no accumulated defect; one further step appends the
current defect after transporting the previous one by the coarse dynamics. -/
def intertwiningResidualAccum
    (Q : Matrix α α R) (E : Matrix α β R) (Qbar : Matrix β β R) :
    ℕ → Matrix α β R
  | 0 => 0
  | n + 1 => intertwiningResidualAccum Q E Qbar n * Qbar + Q ^ n * E

/-- Exact discrete Duhamel/telescoping identity for an approximate intertwiner.
No norm estimate or asymptotics are used. -/
theorem intertwining_power_residual_identity
    (Q : Matrix α α R) (C : Matrix α β R) (Qbar : Matrix β β R)
    (E : Matrix α β R) (hE : Q * C = C * Qbar + E) :
    ∀ n : ℕ,
      Q ^ n * C = C * Qbar ^ n + intertwiningResidualAccum Q E Qbar n := by
  intro n
  induction n with
  | zero => simp [intertwiningResidualAccum]
  | succ n ih =>
      rw [pow_succ, pow_succ]
      calc
        (Q ^ n * Q) * C = Q ^ n * (Q * C) := Matrix.mul_assoc _ _ _
        _ = Q ^ n * (C * Qbar + E) := by rw [hE]
        _ = Q ^ n * (C * Qbar) + Q ^ n * E := by rw [Matrix.mul_add]
        _ = (Q ^ n * C) * Qbar + Q ^ n * E := by rw [Matrix.mul_assoc]
        _ = (C * Qbar ^ n + intertwiningResidualAccum Q E Qbar n) * Qbar + Q ^ n * E := by
          rw [ih]
        _ = C * (Qbar ^ n * Qbar) +
            (intertwiningResidualAccum Q E Qbar n * Qbar + Q ^ n * E) := by
          rw [Matrix.add_mul, Matrix.mul_assoc]
          abel
        _ = C * (Qbar ^ n * Qbar) + intertwiningResidualAccum Q E Qbar (n + 1) := by
          rfl

omit [DecidableEq β] in
/-- The exact intertwining theorem is recovered by setting the defect to zero. -/
theorem intertwiningResidualAccum_zero
    (Q : Matrix α α R) (Qbar : Matrix β β R) :
    ∀ n, intertwiningResidualAccum Q (0 : Matrix α β R) Qbar n = 0 := by
  intro n
  induction n with
  | zero => rfl
  | succ n ih => simp [intertwiningResidualAccum, ih]


/-! ## 2b. Continuous-operator exponential intertwining -/

section ContinuousIntertwining

open NormedSpace

universe uCV uCW

variable {CV : Type uCV} {CW : Type uCW}
variable [NormedAddCommGroup CV] [NormedSpace ℝ CV] [CompleteSpace CV]
variable [NormedAddCommGroup CW] [NormedSpace ℝ CW] [CompleteSpace CW]

/-- Intertwining for bounded linear generators in composition orientation. -/
def ContinuousIntertwines
    (Q : CV →L[ℝ] CV) (C : CW →L[ℝ] CV) (Qbar : CW →L[ℝ] CW) : Prop :=
  Q.comp C = C.comp Qbar

omit [CompleteSpace CV] [CompleteSpace CW] in
/-- Bounded-operator intertwining propagates through every natural power. -/
theorem continuousIntertwines_pow
    (Q : CV →L[ℝ] CV) (C : CW →L[ℝ] CV) (Qbar : CW →L[ℝ] CW)
    (h : ContinuousIntertwines Q C Qbar) :
    ∀ n : ℕ, (Q ^ n).comp C = C.comp (Qbar ^ n) := by
  intro n
  induction n with
  | zero => ext x; simp
  | succ n ih =>
    ext x
    rw [pow_succ', pow_succ']
    simp only [mul_apply_eq_comp, ContinuousLinearMap.comp_apply]
    have ihx := congrArg (fun F : CW →L[ℝ] CV => F x) ih
    simp only [ContinuousLinearMap.comp_apply] at ihx
    rw [ihx]
    have hx := congrArg (fun F : CW →L[ℝ] CV => F ((Qbar ^ n) x)) h
    simpa only [ContinuousLinearMap.comp_apply] using hx

/-- Analytic Markov-semigroup bridge: an exact bounded-operator intertwiner
commutes with the full operator exponential. -/
theorem continuousIntertwines_exp
    (Q : CV →L[ℝ] CV) (C : CW →L[ℝ] CV) (Qbar : CW →L[ℝ] CW)
    (h : ContinuousIntertwines Q C Qbar) :
    (NormedSpace.exp Q).comp C = C.comp (NormedSpace.exp Qbar) := by
  ext x
  let f : ℕ → CV := fun n => (((n.factorial : ℝ)⁻¹) • (Q ^ n)) (C x)
  have hQ := NormedSpace.exp_series_hasSum_exp' (𝕂 := ℝ) Q
  have hleft0 := hQ.map ((ContinuousLinearMap.apply ℝ CV) (C x))
    ((ContinuousLinearMap.apply ℝ CV) (C x)).continuous
  have hleft : HasSum f ((NormedSpace.exp Q) (C x)) := by
    simpa [f, Function.comp_def] using hleft0
  have hQbar := NormedSpace.exp_series_hasSum_exp' (𝕂 := ℝ) Qbar
  have heval := hQbar.map ((ContinuousLinearMap.apply ℝ CW) x)
    ((ContinuousLinearMap.apply ℝ CW) x).continuous
  have hright0 := heval.map C C.continuous
  have hright : HasSum f (C ((NormedSpace.exp Qbar) x)) := by
    refine hright0.congr_fun ?_
    intro n
    dsimp [f]
    change (((n.factorial : ℝ)⁻¹) • (Q ^ n)) (C x) =
      C ((((n.factorial : ℝ)⁻¹) • (Qbar ^ n)) x)
    rw [smul_apply]
    rw [smul_apply]
    rw [C.map_smul]
    have hp := congrArg (fun F : CW →L[ℝ] CV => F x)
      (continuousIntertwines_pow Q C Qbar h n)
    simpa only [ContinuousLinearMap.comp_apply] using congrArg
      (fun y : CV => (n.factorial : ℝ)⁻¹ • y) hp
  exact hleft.unique hright

/-- Time-scaled form used for semigroups `exp(tQ)`. -/
theorem continuousIntertwines_exp_smul
    (Q : CV →L[ℝ] CV) (C : CW →L[ℝ] CV) (Qbar : CW →L[ℝ] CW)
    (h : ContinuousIntertwines Q C Qbar) (t : ℝ) :
    (NormedSpace.exp (t • Q)).comp C = C.comp (NormedSpace.exp (t • Qbar)) := by
  apply continuousIntertwines_exp
  unfold ContinuousIntertwines at h ⊢
  ext x
  simpa using congrArg (fun y : CV => t • y)
    (congrArg (fun F : CW →L[ℝ] CV => F x) h)



/-! ### Continuous Duhamel identity and approximate lumpability certificate -/

/-- Continuous intertwining defect in composition orientation. -/
def continuousIntertwiningDefect
    (Q : CV →L[ℝ] CV) (C : CW →L[ℝ] CV) (Qbar : CW →L[ℝ] CW) : CW →L[ℝ] CV :=
  Q.comp C - C.comp Qbar

/-- The standard Duhamel interpolation path
`exp(sQ) C exp((t-s)Qbar) x`. -/
def continuousDuhamelPath
    (Q : CV →L[ℝ] CV) (C : CW →L[ℝ] CV) (Qbar : CW →L[ℝ] CW)
    (t s : ℝ) (x : CW) : CV :=
  (NormedSpace.exp (s • Q)) (C ((NormedSpace.exp ((t - s) • Qbar)) x))

/-- Pointwise Duhamel integrand generated by the intertwining defect. -/
def continuousDuhamelIntegrand
    (Q : CV →L[ℝ] CV) (C : CW →L[ℝ] CV) (Qbar : CW →L[ℝ] CW)
    (t s : ℝ) (x : CW) : CV :=
  (NormedSpace.exp (s • Q))
    ((continuousIntertwiningDefect Q C Qbar)
      ((NormedSpace.exp ((t - s) • Qbar)) x))

/-- The Duhamel interpolation path differentiates to the transported defect. -/
theorem continuousDuhamelPath_hasDerivAt
    (Q : CV →L[ℝ] CV) (C : CW →L[ℝ] CV) (Qbar : CW →L[ℝ] CW)
    (t s : ℝ) (x : CW) :
    HasDerivAt (fun r => continuousDuhamelPath Q C Qbar t r x)
      (continuousDuhamelIntegrand Q C Qbar t s x) s := by
  let A : ℝ → (CV →L[ℝ] CV) := fun r => NormedSpace.exp (r • Q)
  let B : ℝ → (CW →L[ℝ] CW) := fun r => NormedSpace.exp ((t - r) • Qbar)
  let y : ℝ → CW := fun r => B r x
  let z : ℝ → CV := fun r => C (y r)
  have hA : HasDerivAt A (NormedSpace.exp (s • Q) * Q) s := by
    simpa [A] using hasDerivAt_exp_smul_const Q s
  have hsub : HasDerivAt (fun r : ℝ => t - r) (-1) s := by
    simpa only [id_eq] using (hasDerivAt_id s).const_sub t
  have hB0 : HasDerivAt (fun u : ℝ => NormedSpace.exp (u • Qbar))
      (Qbar * NormedSpace.exp ((t - s) • Qbar)) (t - s) :=
    hasDerivAt_exp_smul_const' Qbar (t - s)
  have hB : HasDerivAt B
      ((-1 : ℝ) • (Qbar * NormedSpace.exp ((t - s) • Qbar))) s := by
    simpa [B, Function.comp_def] using hB0.scomp s hsub
  have hy : HasDerivAt y
      (((-1 : ℝ) • (Qbar * NormedSpace.exp ((t - s) • Qbar))) x) s := by
    simpa [y] using hB.clm_apply (hasDerivAt_const s x)
  have hz : HasDerivAt z
      (C (((-1 : ℝ) • (Qbar * NormedSpace.exp ((t - s) • Qbar))) x)) s := by
    simpa [z] using (hasDerivAt_const s C).clm_apply hy
  have hout := hA.clm_apply hz
  change HasDerivAt (fun r => continuousDuhamelPath Q C Qbar t r x)
    (continuousDuhamelIntegrand Q C Qbar t s x) s
  convert hout using 1 <;>
    simp [continuousDuhamelPath, continuousDuhamelIntegrand,
      continuousIntertwiningDefect, A, B, y, z,
      ContinuousLinearMap.comp_apply, mul_apply_eq_comp, sub_eq_add_neg]

/-- The pointwise Duhamel integrand is continuous in time. -/
theorem continuousDuhamelIntegrand_continuous
    (Q : CV →L[ℝ] CV) (C : CW →L[ℝ] CV) (Qbar : CW →L[ℝ] CW)
    (t : ℝ) (x : CW) :
    Continuous (fun s => continuousDuhamelIntegrand Q C Qbar t s x) := by
  have hQ : Continuous (fun s : ℝ => NormedSpace.exp (s • Q)) :=
    (differentiable_exp_smul_const ℝ Q).continuous
  have hsub : Continuous (fun s : ℝ => t - s) := continuous_const.sub continuous_id
  have hQbar0 : Continuous (fun u : ℝ => NormedSpace.exp (u • Qbar)) :=
    (differentiable_exp_smul_const ℝ Qbar).continuous
  have hQbar : Continuous (fun s : ℝ => NormedSpace.exp ((t - s) • Qbar)) := by
    simpa [Function.comp_def] using hQbar0.comp hsub
  have hv : Continuous (fun s : ℝ => (NormedSpace.exp ((t - s) • Qbar)) x) :=
    hQbar.clm_apply continuous_const
  have hE : Continuous (fun s : ℝ =>
      (continuousIntertwiningDefect Q C Qbar)
        ((NormedSpace.exp ((t - s) • Qbar)) x)) :=
    continuous_const.clm_apply hv
  simpa [continuousDuhamelIntegrand] using hQ.clm_apply hE

/-- Continuous Duhamel formula for an approximate intertwiner, pointwise on the
coarse state space.  This is the analytic counterpart of the discrete residual
accumulation theorem above. -/
theorem continuousDuhamel_identity_pointwise
    (Q : CV →L[ℝ] CV) (C : CW →L[ℝ] CV) (Qbar : CW →L[ℝ] CW)
    (t : ℝ) (x : CW) :
    (NormedSpace.exp (t • Q)) (C x) - C ((NormedSpace.exp (t • Qbar)) x) =
      ∫ s in (0 : ℝ)..t, continuousDuhamelIntegrand Q C Qbar t s x := by
  have hderiv : ∀ s ∈ Set.uIcc (0 : ℝ) t,
      HasDerivAt (fun r => continuousDuhamelPath Q C Qbar t r x)
        (continuousDuhamelIntegrand Q C Qbar t s x) s := by
    intro s hs
    exact continuousDuhamelPath_hasDerivAt Q C Qbar t s x
  have hint : IntervalIntegrable (fun s => continuousDuhamelIntegrand Q C Qbar t s x)
      MeasureTheory.volume 0 t :=
    (continuousDuhamelIntegrand_continuous Q C Qbar t x).intervalIntegrable 0 t
  have hFTC := intervalIntegral.integral_eq_sub_of_hasDerivAt hderiv hint
  rw [hFTC]
  simp [continuousDuhamelPath]

omit [CompleteSpace CV] [CompleteSpace CW] in
/-- Under contraction bounds for both semigroups, the Duhamel integrand is
controlled exactly by the intertwining defect times the input norm. -/
theorem continuousDuhamelIntegrand_norm_le_of_contractions
    (Q : CV →L[ℝ] CV) (C : CW →L[ℝ] CV) (Qbar : CW →L[ℝ] CW)
    {t s : ℝ} (hs : s ∈ Set.Icc (0 : ℝ) t) (x : CW)
    (hQ : ∀ u ∈ Set.Icc (0 : ℝ) t, ‖NormedSpace.exp (u • Q)‖ ≤ 1)
    (hQbar : ∀ u ∈ Set.Icc (0 : ℝ) t, ‖NormedSpace.exp (u • Qbar)‖ ≤ 1) :
    ‖continuousDuhamelIntegrand Q C Qbar t s x‖ ≤
      ‖continuousIntertwiningDefect Q C Qbar‖ * ‖x‖ := by
  have hts : t - s ∈ Set.Icc (0 : ℝ) t := by
    constructor <;> linarith [hs.1, hs.2]
  have h1 := ContinuousLinearMap.le_of_opNorm_le (NormedSpace.exp (s • Q)) (hQ s hs)
    ((continuousIntertwiningDefect Q C Qbar)
      ((NormedSpace.exp ((t - s) • Qbar)) x))
  have h2 := ContinuousLinearMap.le_opNorm (continuousIntertwiningDefect Q C Qbar)
    ((NormedSpace.exp ((t - s) • Qbar)) x)
  have h3 := ContinuousLinearMap.le_of_opNorm_le (NormedSpace.exp ((t - s) • Qbar))
    (hQbar (t - s) hts) x
  unfold continuousDuhamelIntegrand
  calc
    ‖(NormedSpace.exp (s • Q))
        ((continuousIntertwiningDefect Q C Qbar)
          ((NormedSpace.exp ((t - s) • Qbar)) x))‖
        ≤ 1 * ‖(continuousIntertwiningDefect Q C Qbar)
          ((NormedSpace.exp ((t - s) • Qbar)) x)‖ := h1
    _ ≤ 1 * (‖continuousIntertwiningDefect Q C Qbar‖ *
          ‖(NormedSpace.exp ((t - s) • Qbar)) x‖) := by gcongr
    _ ≤ 1 * (‖continuousIntertwiningDefect Q C Qbar‖ * (1 * ‖x‖)) := by gcongr
    _ = ‖continuousIntertwiningDefect Q C Qbar‖ * ‖x‖ := by ring

/-- Continuous approximate-lumpability certificate.  If both exact semigroups
are contractions on `[0,t]`, the semigroup-level intertwining error is bounded
by elapsed time times the generator-level defect. -/
theorem continuousDuhamel_contraction_bound
    (Q : CV →L[ℝ] CV) (C : CW →L[ℝ] CV) (Qbar : CW →L[ℝ] CW)
    {t : ℝ} (ht : 0 ≤ t)
    (hQ : ∀ u ∈ Set.Icc (0 : ℝ) t, ‖NormedSpace.exp (u • Q)‖ ≤ 1)
    (hQbar : ∀ u ∈ Set.Icc (0 : ℝ) t, ‖NormedSpace.exp (u • Qbar)‖ ≤ 1) :
    ‖(NormedSpace.exp (t • Q)).comp C - C.comp (NormedSpace.exp (t • Qbar))‖
      ≤ t * ‖continuousIntertwiningDefect Q C Qbar‖ := by
  apply ContinuousLinearMap.opNorm_le_bound _ (mul_nonneg ht (norm_nonneg _))
  intro x
  have hid := continuousDuhamel_identity_pointwise Q C Qbar t x
  have hInt : ‖∫ s in (0 : ℝ)..t, continuousDuhamelIntegrand Q C Qbar t s x‖
      ≤ (‖continuousIntertwiningDefect Q C Qbar‖ * ‖x‖) * |t - 0| := by
    apply intervalIntegral.norm_integral_le_of_norm_le_const
    intro s hs
    have hs' : s ∈ Set.Icc (0 : ℝ) t := by
      have hso : 0 < s ∧ s ≤ t := by simpa [Set.uIoc_of_le ht] using hs
      exact ⟨le_of_lt hso.1, hso.2⟩
    exact continuousDuhamelIntegrand_norm_le_of_contractions Q C Qbar hs' x hQ hQbar
  calc
    ‖((NormedSpace.exp (t • Q)).comp C - C.comp (NormedSpace.exp (t • Qbar))) x‖ =
        ‖(NormedSpace.exp (t • Q)) (C x) - C ((NormedSpace.exp (t • Qbar)) x)‖ := by
          rfl
    _ = ‖∫ s in (0 : ℝ)..t, continuousDuhamelIntegrand Q C Qbar t s x‖ := by rw [hid]
    _ ≤ (‖continuousIntertwiningDefect Q C Qbar‖ * ‖x‖) * |t - 0| := hInt
    _ = (t * ‖continuousIntertwiningDefect Q C Qbar‖) * ‖x‖ := by
      rw [sub_zero, abs_of_nonneg ht]
      ring



/-- Pointwise version of the continuous approximate-lumpability bound. -/
theorem continuousDuhamel_state_bound
    (Q : CV →L[ℝ] CV) (C : CW →L[ℝ] CV) (Qbar : CW →L[ℝ] CW)
    {t : ℝ} (ht : 0 ≤ t)
    (hQ : ∀ u ∈ Set.Icc (0 : ℝ) t, ‖NormedSpace.exp (u • Q)‖ ≤ 1)
    (hQbar : ∀ u ∈ Set.Icc (0 : ℝ) t, ‖NormedSpace.exp (u • Qbar)‖ ≤ 1)
    (x : CW) :
    ‖(NormedSpace.exp (t • Q)) (C x) - C ((NormedSpace.exp (t • Qbar)) x)‖
      ≤ (t * ‖continuousIntertwiningDefect Q C Qbar‖) * ‖x‖ := by
  have h := ContinuousLinearMap.le_of_opNorm_le
    ((NormedSpace.exp (t • Q)).comp C - C.comp (NormedSpace.exp (t • Qbar)))
    (continuousDuhamel_contraction_bound Q C Qbar ht hQ hQbar) x
  simpa only [sub_apply, ContinuousLinearMap.comp_apply] using h

/-- For an initial state of norm at most one (in particular a probability state
under a compatible probability norm), the coarse error is at most `t‖E‖`. -/
theorem continuousDuhamel_unit_state_bound
    (Q : CV →L[ℝ] CV) (C : CW →L[ℝ] CV) (Qbar : CW →L[ℝ] CW)
    {t : ℝ} (ht : 0 ≤ t)
    (hQ : ∀ u ∈ Set.Icc (0 : ℝ) t, ‖NormedSpace.exp (u • Q)‖ ≤ 1)
    (hQbar : ∀ u ∈ Set.Icc (0 : ℝ) t, ‖NormedSpace.exp (u • Qbar)‖ ≤ 1)
    (x : CW) (hx : ‖x‖ ≤ 1) :
    ‖(NormedSpace.exp (t • Q)) (C x) - C ((NormedSpace.exp (t • Qbar)) x)‖
      ≤ t * ‖continuousIntertwiningDefect Q C Qbar‖ := by
  calc
    ‖(NormedSpace.exp (t • Q)) (C x) - C ((NormedSpace.exp (t • Qbar)) x)‖
        ≤ (t * ‖continuousIntertwiningDefect Q C Qbar‖) * ‖x‖ :=
          continuousDuhamel_state_bound Q C Qbar ht hQ hQbar x
    _ ≤ (t * ‖continuousIntertwiningDefect Q C Qbar‖) * 1 := by
      gcongr
    _ = t * ‖continuousIntertwiningDefect Q C Qbar‖ := by ring

end ContinuousIntertwining

/-! ## 3. Strong lumpability from partition rates -/

/-- State-to-cell indicator matrix of a finite partition map. -/
def partitionIndicator (cell : α → β) : Matrix α β R :=
  fun i b => if cell i = b then 1 else 0

/-- Total transition coefficient from one microstate into one target cell. -/
def cellRate (Q : Matrix α α R) (cell : α → β) (i : α) (b : β) : R :=
  ∑ j, if cell j = b then Q i j else 0

/-- Row-rate definition of strong lumpability: states in the same source cell
have identical total transition coefficients into every target cell. -/
def StrongLumpable (Q : Matrix α α R) (cell : α → β) : Prop :=
  ∀ i i', cell i = cell i' → ∀ b, cellRate Q cell i b = cellRate Q cell i' b

omit [Fintype β] [DecidableEq α] in
/-- Multiplication by the partition indicator computes cell rates. -/
theorem mul_partitionIndicator_apply
    (Q : Matrix α α R) (cell : α → β) (i : α) (b : β) :
    ((Q * partitionIndicator cell : Matrix α β R) i b) = cellRate Q cell i b := by
  classical
  simp [Matrix.mul_apply, partitionIndicator, cellRate]

omit [Fintype α] [DecidableEq α] in
/-- Multiplying a coarse matrix on the right of the indicator simply selects the
row indexed by the source cell. -/
theorem partitionIndicator_mul_apply
    (cell : α → β) (Qbar : Matrix β β R) (i : α) (b : β) :
    ((partitionIndicator cell * Qbar : Matrix α β R) i b) = Qbar (cell i) b := by
  classical
  simp [Matrix.mul_apply, partitionIndicator]

/-- Choose one microstate representative of every nonempty cell. -/
noncomputable def cellRepresentative
    (cell : α → β) (hcell : Function.Surjective cell) (b : β) : α :=
  Classical.choose (hcell b)

omit [Fintype α] [Fintype β] [DecidableEq α] [DecidableEq β] in
theorem cell_cellRepresentative
    (cell : α → β) (hcell : Function.Surjective cell) (b : β) :
    cell (cellRepresentative cell hcell b) = b :=
  Classical.choose_spec (hcell b)

/-- Canonical coarse matrix obtained from any chosen representative in each
cell.  Strong lumpability guarantees independence of that representative. -/
noncomputable def lumpedMatrix
    (Q : Matrix α α R) (cell : α → β) (hcell : Function.Surjective cell) :
    Matrix β β R :=
  fun a b => cellRate Q cell (cellRepresentative cell hcell a) b

omit [DecidableEq α] in
/-- Strong lumpability constructs an exact intertwining coarse matrix. -/
theorem intertwines_lumpedMatrix_of_strongLumpable
    (Q : Matrix α α R) (cell : α → β) (hcell : Function.Surjective cell)
    (hL : StrongLumpable Q cell) :
    Intertwines Q (partitionIndicator cell) (lumpedMatrix Q cell hcell) := by
  unfold Intertwines
  ext i b
  rw [mul_partitionIndicator_apply, partitionIndicator_mul_apply]
  unfold lumpedMatrix
  apply hL i (cellRepresentative cell hcell (cell i))
  exact (cell_cellRepresentative cell hcell (cell i)).symm

omit [DecidableEq α] in
/-- Any exact intertwiner forces the row-rate strong-lumpability condition. -/
theorem strongLumpable_of_intertwines
    (Q : Matrix α α R) (cell : α → β) (Qbar : Matrix β β R)
    (h : Intertwines Q (partitionIndicator cell) Qbar) :
    StrongLumpable Q cell := by
  intro i i' hii b
  calc
    cellRate Q cell i b = ((Q * partitionIndicator cell : Matrix α β R) i b) :=
      (mul_partitionIndicator_apply Q cell i b).symm
    _ = ((partitionIndicator cell * Qbar : Matrix α β R) i b) := by
      exact congrFun (congrFun h i) b
    _ = Qbar (cell i) b := partitionIndicator_mul_apply cell Qbar i b
    _ = Qbar (cell i') b := by rw [hii]
    _ = ((partitionIndicator cell * Qbar : Matrix α β R) i' b) :=
      (partitionIndicator_mul_apply cell Qbar i' b).symm
    _ = ((Q * partitionIndicator cell : Matrix α β R) i' b) := by
      exact (congrFun (congrFun h i') b).symm
    _ = cellRate Q cell i' b := mul_partitionIndicator_apply Q cell i' b

omit [DecidableEq α] in
/-- The finite exact theorem used by strong Markov lumpability: for a surjective
partition, the row-rate condition is equivalent to existence of a coarse matrix
satisfying `Q C = C Qbar`. -/
theorem strongLumpable_iff_exists_intertwiner
    (Q : Matrix α α R) (cell : α → β) (hcell : Function.Surjective cell) :
    StrongLumpable Q cell ↔
      ∃ Qbar : Matrix β β R, Intertwines Q (partitionIndicator cell) Qbar := by
  constructor
  · intro hL
    exact ⟨lumpedMatrix Q cell hcell,
      intertwines_lumpedMatrix_of_strongLumpable Q cell hcell hL⟩
  · rintro ⟨Qbar, hQbar⟩
    exact strongLumpable_of_intertwines Q cell Qbar hQbar


/-! ## 4. Direct-sum / block-diagonal Kalman algebra -/

universe uRow uMid uCol uPkt uObs uK

/-- A rectangular matrix respects a packet decomposition when it has no entries
between differently labelled source/target packets. -/
def BlockRespecting
    {S : Type*} [Zero S]
    {ρ : Type uRow} {κ : Type uCol} {π : Type uPkt}
    (rowPacket : ρ → π) (colPacket : κ → π) (M : Matrix ρ κ S) : Prop :=
  ∀ i j, rowPacket i ≠ colPacket j → M i j = 0

section BlockAlgebra

variable {S : Type*} [Semiring S]
variable {ρ : Type uRow} {μ : Type uMid} {κ : Type uCol} {π : Type uPkt}
variable [Fintype μ]
variable (rpacket : ρ → π) (mpacket : μ → π) (cpacket : κ → π)

omit [Fintype μ] in
/-- Zero is block respecting. -/
theorem BlockRespecting.zero :
    BlockRespecting rpacket cpacket (0 : Matrix ρ κ S) := by
  intro i j hij
  rfl

omit [Fintype μ] in
/-- Block-respecting matrices are closed under addition. -/
theorem BlockRespecting.add
    {A B : Matrix ρ κ S}
    (hA : BlockRespecting rpacket cpacket A)
    (hB : BlockRespecting rpacket cpacket B) :
    BlockRespecting rpacket cpacket (A + B) := by
  intro i j hij
  simp [hA i j hij, hB i j hij]

/-- Block-respecting matrices are closed under compatible matrix composition. -/
theorem BlockRespecting.mul
    {A : Matrix ρ μ S} {B : Matrix μ κ S}
    (hA : BlockRespecting rpacket mpacket A)
    (hB : BlockRespecting mpacket cpacket B) :
    BlockRespecting rpacket cpacket (A * B) := by
  intro i k hik
  rw [Matrix.mul_apply]
  apply Finset.sum_eq_zero
  intro j hj
  by_cases hmid : rpacket i = mpacket j
  · have hright : mpacket j ≠ cpacket k := by
      intro hEq
      exact hik (hmid.trans hEq)
    rw [hB j k hright]
    simp
  · rw [hA i j hmid]
    simp

omit [Fintype μ] in
/-- Transpose reverses the packet typing and remains block respecting. -/
theorem BlockRespecting.transpose
    {A : Matrix ρ κ S}
    (hA : BlockRespecting rpacket cpacket A) :
    BlockRespecting cpacket rpacket A.transpose := by
  intro j i hji
  exact hA i j (Ne.symm hji)

end BlockAlgebra

section RingBlockAlgebra

variable {S : Type*} [Ring S]
variable {ρ : Type uRow} {κ : Type uCol} {π : Type uPkt}
variable (rpacket : ρ → π) (cpacket : κ → π)

/-- Block-respecting matrices are closed under subtraction. -/
theorem BlockRespecting.sub
    {A B : Matrix ρ κ S}
    (hA : BlockRespecting rpacket cpacket A)
    (hB : BlockRespecting rpacket cpacket B) :
    BlockRespecting rpacket cpacket (A - B) := by
  intro i j hij
  simp [hA i j hij, hB i j hij]

end RingBlockAlgebra

section SquareBlockAlgebra

variable {S : Type*} [Semiring S]
variable {ρ : Type uRow} {π : Type uPkt}
variable [Fintype ρ] [DecidableEq ρ]
variable (packet : ρ → π)

omit [Fintype ρ] in
/-- Identity is block respecting for every packet labelling. -/
theorem BlockRespecting.one :
    BlockRespecting packet packet (1 : Matrix ρ ρ S) := by
  intro i j hij
  have hne : i ≠ j := by
    intro hij'
    subst j
    exact hij rfl
  simp [hne]

end SquareBlockAlgebra


/-! ### Inverse closure of packet-block matrices -/

section BlockInverseClosure

variable {S : Type*} [Semiring S]
variable {ρ : Type uRow} {π : Type uPkt}
variable [Fintype ρ] [DecidableEq ρ]
variable (packet : ρ → π)

/-- Diagonal projector selecting one packet label. -/
noncomputable def packetDiagonalProjector (b : π) : Matrix ρ ρ S := by
  classical
  exact Matrix.diagonal (fun i => if packet i = b then 1 else 0)

/-- A block-respecting square matrix commutes with every packet diagonal
projector. -/
theorem BlockRespecting.commute_packetDiagonalProjector
    {M : Matrix ρ ρ S} (hM : BlockRespecting packet packet M) (b : π) :
    packetDiagonalProjector (S := S) packet b * M =
      M * packetDiagonalProjector (S := S) packet b := by
  classical
  ext i j
  simp only [packetDiagonalProjector, Matrix.diagonal_mul, Matrix.mul_diagonal]
  by_cases hij : packet i = packet j
  · by_cases hi : packet i = b
    · have hj : packet j = b := by simpa [← hij] using hi
      simp [hi, hj]
    · have hj : packet j ≠ b := by
        intro h
        exact hi (hij.trans h)
      simp [hi, hj]
  · have hzero := hM i j hij
    simp [hzero]

/-- Commutation with all packet diagonal projectors forces the matrix to be
block respecting. -/
theorem blockRespecting_of_commute_packetDiagonalProjector
    {M : Matrix ρ ρ S}
    (hM : ∀ b : π,
      packetDiagonalProjector (S := S) packet b * M =
        M * packetDiagonalProjector (S := S) packet b) :
    BlockRespecting packet packet M := by
  classical
  intro i j hij
  have e := congrFun (congrFun (hM (packet i)) i) j
  simpa [packetDiagonalProjector, hij, Ne.symm hij] using e

/-- A two-sided inverse of a block-respecting square matrix is automatically
block respecting.  This closes the inverse step used by direct-sum Kalman
filters. -/
theorem blockRespecting_of_twoSidedInverse
    (M N : Matrix ρ ρ S)
    (hM : BlockRespecting packet packet M)
    (hMN : M * N = 1) (hNM : N * M = 1) :
    BlockRespecting packet packet N := by
  apply blockRespecting_of_commute_packetDiagonalProjector (S := S) packet
  intro b
  let D := packetDiagonalProjector (S := S) packet b
  have hDM : D * M = M * D := by
    exact hM.commute_packetDiagonalProjector packet b
  calc
    D * N = (N * M) * (D * N) := by rw [hNM]; simp
    _ = N * (M * (D * N)) := Matrix.mul_assoc _ _ _
    _ = N * ((M * D) * N) := by rw [Matrix.mul_assoc M D N]
    _ = N * ((D * M) * N) := by rw [hDM.symm]
    _ = N * (D * (M * N)) := by rw [Matrix.mul_assoc D M N]
    _ = (N * D) * (M * N) := (Matrix.mul_assoc N D (M * N)).symm
    _ = N * D := by rw [hMN]; simp

end BlockInverseClosure


section KalmanBlockClosure

variable {S : Type*} [CommRing S]
variable {state : Type uK} {obs : Type uObs} {π : Type uPkt}
variable [Fintype state] [Fintype obs]
variable [DecidableEq state] [DecidableEq obs]
variable (spacket : state → π) (opacket : obs → π)

/-- Covariance prediction `A P Aᵀ + Q`. -/
def kalmanPredCov
    (A P Q : Matrix state state S) : Matrix state state S :=
  A * P * A.transpose + Q

/-- Innovation covariance `H P⁻ Hᵀ + R`. -/
def kalmanInnovation
    (H : Matrix obs state S) (Ppred : Matrix state state S)
    (Robs : Matrix obs obs S) : Matrix obs obs S :=
  H * Ppred * H.transpose + Robs

/-- Kalman gain with an explicitly supplied innovation inverse. -/
def kalmanGain
    (Ppred : Matrix state state S) (H : Matrix obs state S)
    (Sinv : Matrix obs obs S) : Matrix state obs S :=
  Ppred * H.transpose * Sinv

/-- Standard covariance update `(I - K H) P⁻`. -/
def kalmanCovUpdate
    (K : Matrix state obs S) (H : Matrix obs state S)
    (Ppred : Matrix state state S) : Matrix state state S :=
  (1 - K * H) * Ppred

/-- Joseph-stabilized covariance update. -/
def kalmanJosephCovUpdate
    (K : Matrix state obs S) (H : Matrix obs state S)
    (Ppred : Matrix state state S) (Robs : Matrix obs obs S) : Matrix state state S :=
  let A := 1 - K * H
  A * Ppred * A.transpose + K * Robs * K.transpose

omit [DecidableEq state] in
/-- Block-diagonal prediction closes exactly. -/
theorem kalmanPredCov_block
    (A P Q : Matrix state state S)
    (hA : BlockRespecting spacket spacket A)
    (hP : BlockRespecting spacket spacket P)
    (hQ : BlockRespecting spacket spacket Q) :
    BlockRespecting spacket spacket (kalmanPredCov A P Q) := by
  unfold kalmanPredCov
  have hAP := BlockRespecting.mul spacket spacket spacket hA hP
  have hAT := BlockRespecting.transpose spacket spacket hA
  exact BlockRespecting.add spacket spacket
    (BlockRespecting.mul spacket spacket spacket hAP hAT) hQ

omit [Fintype obs] [DecidableEq state] [DecidableEq obs] in
/-- Innovation covariance remains block diagonal when observation and state
packet labels are compatible. -/
theorem kalmanInnovation_block
    (H : Matrix obs state S) (Ppred : Matrix state state S)
    (Robs : Matrix obs obs S)
    (hH : BlockRespecting opacket spacket H)
    (hP : BlockRespecting spacket spacket Ppred)
    (hR : BlockRespecting opacket opacket Robs) :
    BlockRespecting opacket opacket (kalmanInnovation H Ppred Robs) := by
  unfold kalmanInnovation
  have hHP := BlockRespecting.mul opacket spacket spacket hH hP
  have hHT := BlockRespecting.transpose opacket spacket hH
  exact BlockRespecting.add opacket opacket
    (BlockRespecting.mul opacket spacket opacket hHP hHT) hR

omit [DecidableEq state] [DecidableEq obs] in
/-- If the innovation inverse respects the same packet splitting, the exact
Kalman gain is packetwise.  Inverse-closure itself is intentionally a separate
obligation. -/
theorem kalmanGain_block
    (Ppred : Matrix state state S) (H : Matrix obs state S)
    (Sinv : Matrix obs obs S)
    (hP : BlockRespecting spacket spacket Ppred)
    (hH : BlockRespecting opacket spacket H)
    (hSinv : BlockRespecting opacket opacket Sinv) :
    BlockRespecting spacket opacket (kalmanGain Ppred H Sinv) := by
  unfold kalmanGain
  have hHT := BlockRespecting.transpose opacket spacket hH
  have hPH := BlockRespecting.mul spacket spacket opacket hP hHT
  exact BlockRespecting.mul spacket opacket opacket hPH hSinv

omit [DecidableEq obs] in
/-- The covariance correction step preserves the state packet splitting. -/
theorem kalmanCovUpdate_block
    (K : Matrix state obs S) (H : Matrix obs state S)
    (Ppred : Matrix state state S)
    (hK : BlockRespecting spacket opacket K)
    (hH : BlockRespecting opacket spacket H)
    (hP : BlockRespecting spacket spacket Ppred) :
    BlockRespecting spacket spacket (kalmanCovUpdate K H Ppred) := by
  unfold kalmanCovUpdate
  have hKH := BlockRespecting.mul spacket opacket spacket hK hH
  have hI := BlockRespecting.one (S := S) spacket
  have hIKH := BlockRespecting.sub spacket spacket hI hKH
  exact BlockRespecting.mul spacket spacket spacket hIKH hP

omit [DecidableEq obs] in
/-- The full Joseph covariance formula preserves exact packet block structure. -/
theorem kalmanJosephCovUpdate_block
    (K : Matrix state obs S) (H : Matrix obs state S)
    (Ppred : Matrix state state S) (Robs : Matrix obs obs S)
    (hK : BlockRespecting spacket opacket K)
    (hH : BlockRespecting opacket spacket H)
    (hP : BlockRespecting spacket spacket Ppred)
    (hR : BlockRespecting opacket opacket Robs) :
    BlockRespecting spacket spacket (kalmanJosephCovUpdate K H Ppred Robs) := by
  unfold kalmanJosephCovUpdate
  dsimp only
  have hKH := BlockRespecting.mul spacket opacket spacket hK hH
  have hI := BlockRespecting.one (S := S) spacket
  have hA := BlockRespecting.sub spacket spacket hI hKH
  have hAT := BlockRespecting.transpose spacket spacket hA
  have hAP := BlockRespecting.mul spacket spacket spacket hA hP
  have hAPA := BlockRespecting.mul spacket spacket spacket hAP hAT
  have hKR := BlockRespecting.mul spacket opacket opacket hK hR
  have hKT := BlockRespecting.transpose spacket opacket hK
  have hKRK := BlockRespecting.mul spacket opacket spacket hKR hKT
  exact BlockRespecting.add spacket spacket hAPA hKRK

omit [DecidableEq obs] in
/-- Combined finite direct-sum Kalman closure, conditional only on the explicit
innovation inverse carrying the same block structure. -/
theorem kalman_block_closure
    (A P Q : Matrix state state S)
    (H : Matrix obs state S) (Robs Sinv : Matrix obs obs S)
    (hA : BlockRespecting spacket spacket A)
    (hP : BlockRespecting spacket spacket P)
    (hQ : BlockRespecting spacket spacket Q)
    (hH : BlockRespecting opacket spacket H)
    (hR : BlockRespecting opacket opacket Robs)
    (hSinv : BlockRespecting opacket opacket Sinv) :
    let Ppred := kalmanPredCov A P Q
    let Sinnov := kalmanInnovation H Ppred Robs
    let K := kalmanGain Ppred H Sinv
    BlockRespecting spacket spacket Ppred ∧
    BlockRespecting opacket opacket Sinnov ∧
    BlockRespecting spacket opacket K ∧
    BlockRespecting spacket spacket (kalmanCovUpdate K H Ppred) := by
  dsimp only
  have hPred := kalmanPredCov_block spacket A P Q hA hP hQ
  have hInnov := kalmanInnovation_block spacket opacket H (kalmanPredCov A P Q) Robs hH hPred hR
  have hGain := kalmanGain_block spacket opacket (kalmanPredCov A P Q) H Sinv hPred hH hSinv
  have hUpd := kalmanCovUpdate_block spacket opacket
    (kalmanGain (kalmanPredCov A P Q) H Sinv) H (kalmanPredCov A P Q) hGain hH hPred
  exact ⟨hPred, hInnov, hGain, hUpd⟩


/-- Full finite block-Kalman closure from an actual two-sided innovation
inverse.  No block-structure assumption on the inverse is needed: it follows
from the inverse equations. -/
theorem kalman_block_closure_of_twoSided_inverse
    (A P Q : Matrix state state S)
    (H : Matrix obs state S) (Robs Sinv : Matrix obs obs S)
    (hA : BlockRespecting spacket spacket A)
    (hP : BlockRespecting spacket spacket P)
    (hQ : BlockRespecting spacket spacket Q)
    (hH : BlockRespecting opacket spacket H)
    (hR : BlockRespecting opacket opacket Robs)
    (hLeft : kalmanInnovation H (kalmanPredCov A P Q) Robs * Sinv = 1)
    (hRight : Sinv * kalmanInnovation H (kalmanPredCov A P Q) Robs = 1) :
    let Ppred := kalmanPredCov A P Q
    let Sinnov := kalmanInnovation H Ppred Robs
    let K := kalmanGain Ppred H Sinv
    BlockRespecting spacket spacket Ppred ∧
    BlockRespecting opacket opacket Sinnov ∧
    BlockRespecting spacket opacket K ∧
    BlockRespecting spacket spacket (kalmanCovUpdate K H Ppred) := by
  dsimp only
  have hPred := kalmanPredCov_block spacket A P Q hA hP hQ
  have hInnov := kalmanInnovation_block spacket opacket H (kalmanPredCov A P Q) Robs hH hPred hR
  have hSinv : BlockRespecting opacket opacket Sinv :=
    blockRespecting_of_twoSidedInverse (S := S) opacket
      (kalmanInnovation H (kalmanPredCov A P Q) Robs) Sinv hInnov hLeft hRight
  exact kalman_block_closure spacket opacket A P Q H Robs Sinv
    hA hP hQ hH hR hSinv

/-- Direct-sum Kalman closure with the actual two-sided innovation inverse and
the full Joseph covariance update. -/
theorem kalman_joseph_block_closure_of_twoSided_inverse
    (A P Q : Matrix state state S)
    (H : Matrix obs state S) (Robs Sinv : Matrix obs obs S)
    (hA : BlockRespecting spacket spacket A)
    (hP : BlockRespecting spacket spacket P)
    (hQ : BlockRespecting spacket spacket Q)
    (hH : BlockRespecting opacket spacket H)
    (hR : BlockRespecting opacket opacket Robs)
    (hLeft : kalmanInnovation H (kalmanPredCov A P Q) Robs * Sinv = 1)
    (hRight : Sinv * kalmanInnovation H (kalmanPredCov A P Q) Robs = 1) :
    let Ppred := kalmanPredCov A P Q
    let Sinnov := kalmanInnovation H Ppred Robs
    let K := kalmanGain Ppred H Sinv
    BlockRespecting spacket spacket Ppred ∧
    BlockRespecting opacket opacket Sinnov ∧
    BlockRespecting spacket opacket K ∧
    BlockRespecting spacket spacket (kalmanJosephCovUpdate K H Ppred Robs) := by
  dsimp only
  have hPred := kalmanPredCov_block spacket A P Q hA hP hQ
  have hInnov := kalmanInnovation_block spacket opacket H (kalmanPredCov A P Q) Robs hH hPred hR
  have hSinv : BlockRespecting opacket opacket Sinv :=
    blockRespecting_of_twoSidedInverse (S := S) opacket
      (kalmanInnovation H (kalmanPredCov A P Q) Robs) Sinv hInnov hLeft hRight
  have hGain := kalmanGain_block spacket opacket (kalmanPredCov A P Q) H Sinv hPred hH hSinv
  have hJoseph := kalmanJosephCovUpdate_block spacket opacket
    (kalmanGain (kalmanPredCov A P Q) H Sinv) H (kalmanPredCov A P Q) Robs
    hGain hH hPred hR
  exact ⟨hPred, hInnov, hGain, hJoseph⟩

end KalmanBlockClosure


/-! ## 4b. Packetwise Kalman mean reconstruction -/

section KalmanMeanPackets

variable {S : Type*} [CommRing S]
variable {state : Type uK} {obs : Type uObs} {π : Type uPkt}
variable [Fintype state] [Fintype obs] [DecidableEq π]
variable (spacket : state → π) (opacket : obs → π)

/-- Matrix-vector product with all cross-packet contributions explicitly
masked. -/
def packetMulVec
    {ρ κ : Type*} [Fintype κ]
    (rpacket : ρ → π) (cpacket : κ → π)
    (A : Matrix ρ κ S) (x : κ → S) (i : ρ) : S :=
  ∑ j, if rpacket i = cpacket j then A i j * x j else 0

/-- A block-respecting matrix-vector product is exactly its same-packet sum. -/
theorem BlockRespecting.mulVec_eq_packetMulVec
    {ρ κ : Type*} [Fintype κ]
    (rpacket : ρ → π) (cpacket : κ → π)
    (A : Matrix ρ κ S) (x : κ → S)
    (hA : BlockRespecting rpacket cpacket A) (i : ρ) :
    Matrix.mulVec A x i = packetMulVec rpacket cpacket A x i := by
  classical
  rw [Matrix.mulVec_apply_eq_sum]
  unfold packetMulVec
  apply Finset.sum_congr rfl
  intro j hj
  by_cases h : rpacket i = cpacket j
  · simp [h]
  · simp [h, hA i j h]

/-- Mean correction for a Kalman update. -/
def kalmanMeanUpdate
    (K : Matrix state obs S) (H : Matrix obs state S)
    (mpred : state → S) (y : obs → S) : state → S :=
  mpred + Matrix.mulVec K (y - Matrix.mulVec H mpred)

omit [Fintype obs] in
/-- Exact packetwise innovation prediction: observation component `a` only
uses state coordinates in the same packet as `a`. -/
theorem observationPrediction_packetwise
    (H : Matrix obs state S) (m : state → S)
    (hH : BlockRespecting opacket spacket H) (a : obs) :
    Matrix.mulVec H m a = packetMulVec opacket spacket H m a :=
  BlockRespecting.mulVec_eq_packetMulVec opacket spacket H m hH a

/-- Exact packetwise Kalman mean correction: a state coordinate receives
innovation contributions only from observation coordinates carrying the same
packet label. -/
theorem kalmanMeanUpdate_packetwise
    (K : Matrix state obs S) (H : Matrix obs state S)
    (mpred : state → S) (y : obs → S)
    (hK : BlockRespecting spacket opacket K) (i : state) :
    kalmanMeanUpdate K H mpred y i =
      mpred i + packetMulVec spacket opacket K
        (y - Matrix.mulVec H mpred) i := by
  unfold kalmanMeanUpdate
  rw [Pi.add_apply]
  rw [BlockRespecting.mulVec_eq_packetMulVec spacket opacket K
    (y - Matrix.mulVec H mpred) hK i]

end KalmanMeanPackets


/-! ## 5. Packet-resolved linear moment algebra -/

section MomentPacketAlgebra

universe uState uPacket

variable {K : Type*} [Field K]
variable {state : Type uState} {packetTy : Type uPacket}
variable [Fintype state] [DecidableEq state] [Fintype packetTy] [DecidableEq packetTy]

/-- Select one coordinate packet from a state vector. -/
def packetVector (packet : state → packetTy) (b : packetTy) (x : state → K) : state → K :=
  fun i => if packet i = b then x i else 0

omit [Fintype state] [DecidableEq state] in
/-- Complete reconstruction of a vector from its coordinate packets. -/
theorem packetVector_reconstruction
    (packet : state → packetTy) (x : state → K) :
    (fun i => ∑ b, packetVector packet b x i) = x := by
  funext i
  classical
  simp [packetVector]

/-- Matrix-vector multiplication in the finite coordinate model. -/
def matVec (A : Matrix state state K) (x : state → K) : state → K :=
  fun i => ∑ j, A i j * x j

/-- The contribution to row `i` coming from source packet `b`. -/
def matVecPacketContribution
    (packet : state → packetTy) (A : Matrix state state K)
    (x : state → K) (i : state) (b : packetTy) : K :=
  ∑ j, A i j * packetVector packet b x j

omit [DecidableEq state] in
/-- Every matrix-vector product decomposes exactly into source-packet
contributions.  This is the finite algebraic skeleton of the packet mean
equation `ṁ_i = Σ_j A_ij m_j + b_i`. -/
theorem matVec_packet_decomposition
    (packet : state → packetTy) (A : Matrix state state K) (x : state → K) (i : state) :
    matVec A x i = ∑ b, matVecPacketContribution packet A x i b := by
  classical
  unfold matVec matVecPacketContribution packetVector
  calc
    (∑ j, A i j * x j) = ∑ j, A i j * (∑ b, if packet j = b then x j else 0) := by
      apply Finset.sum_congr rfl
      intro j hj
      simp
    _ = ∑ j, ∑ b, A i j * (if packet j = b then x j else 0) := by
      apply Finset.sum_congr rfl
      intro j hj
      rw [Finset.mul_sum]
    _ = ∑ b, ∑ j, A i j * (if packet j = b then x j else 0) := by
      rw [Finset.sum_comm]

omit [DecidableEq state] in
/-- Mean-equation packet resolution.  Once the standard linear-SDE mean law
`ṁ = A m + b` is available, each coordinate row is exactly the sum of the
source-packet transfers plus the forcing coordinate. -/
theorem meanEquation_packet
    (packet : state → packetTy)
    (A : Matrix state state K) (m b mdot : state → K)
    (hmean : mdot = fun i => matVec A m i + b i)
    (i : state) :
    mdot i = (∑ q, matVecPacketContribution packet A m i q) + b i := by
  rw [hmean]
  change matVec A m i + b i = _
  have hdec := matVec_packet_decomposition (K := K) packet A m i
  rw [hdec]

/-- Covariance/Lyapunov right-hand side `A P + P Aᵀ + Q`. -/
def covarianceRHS
    (A P Q : Matrix state state K) : Matrix state state K :=
  A * P + P * A.transpose + Q

omit [DecidableEq state] in
/-- Entrywise finite packet expansion of the covariance/Lyapunov equation. -/
theorem covarianceRHS_apply
    (A P Q : Matrix state state K) (i j : state) :
    covarianceRHS A P Q i j =
      (∑ k, A i k * P k j) + (∑ k, P i k * A j k) + Q i j := by
  simp [covarianceRHS, Matrix.mul_apply]

omit [DecidableEq state] [Fintype packetTy] [DecidableEq packetTy] in
/-- If drift, covariance, and noise covariance respect a packet decomposition,
then the covariance derivative/tangent `A P + P Aᵀ + Q` respects it as well.
This is the exact algebraic invariant behind independent stochastic packets. -/
theorem covarianceRHS_block
    (packet : state → packetTy) (A P Q : Matrix state state K)
    (hA : BlockRespecting packet packet A)
    (hP : BlockRespecting packet packet P)
    (hQ : BlockRespecting packet packet Q) :
    BlockRespecting packet packet (covarianceRHS A P Q) := by
  unfold covarianceRHS
  have hAP := BlockRespecting.mul packet packet packet hA hP
  have hAT := BlockRespecting.transpose packet packet hA
  have hPA := BlockRespecting.mul packet packet packet hP hAT
  exact BlockRespecting.add packet packet (BlockRespecting.add packet packet hAP hPA) hQ

omit [DecidableEq state] [Fintype packetTy] [DecidableEq packetTy] in
/-- Off-diagonal covariance derivatives vanish under exact packet closure. -/
theorem covarianceRHS_offdiag_zero
    (packet : state → packetTy) (A P Q : Matrix state state K)
    (hA : BlockRespecting packet packet A)
    (hP : BlockRespecting packet packet P)
    (hQ : BlockRespecting packet packet Q)
    {i j : state} (hij : packet i ≠ packet j) :
    covarianceRHS A P Q i j = 0 := by
  exact covarianceRHS_block packet A P Q hA hP hQ i j hij

omit [DecidableEq state] [Fintype packetTy] [DecidableEq packetTy] in
/-- A supplied moment equation inherits exact packet closure immediately. -/
theorem packetMomentClosure
    (packet : state → packetTy)
    (A P Q Pdot : Matrix state state K)
    (hMoment : Pdot = covarianceRHS A P Q)
    (hA : BlockRespecting packet packet A)
    (hP : BlockRespecting packet packet P)
    (hQ : BlockRespecting packet packet Q) :
    BlockRespecting packet packet Pdot := by
  rw [hMoment]
  exact covarianceRHS_block packet A P Q hA hP hQ

end MomentPacketAlgebra


/-! ## 6. Constant linear projectors and Caputo-type memory -/

section CaputoMemory

open MeasureTheory intervalIntegral

universe uE uF

variable {E : Type uE} {F : Type uF}
variable [NormedAddCommGroup E] [NormedSpace ℝ E] [CompleteSpace E]
variable [NormedAddCommGroup F] [NormedSpace ℝ F] [CompleteSpace F]

/-- The unnormalised Caputo kernel applied to supplied derivative data.  This
separates the analytic memory integral from the derivative-existence theorem. -/
def caputoHistoryCore (α t : ℝ) (dx : ℝ → E) : E :=
  ∫ s in (0 : ℝ)..t, Real.rpow (t - s) (-α) • dx s

/-- Caputo memory applied to supplied derivative data, with the standard
`1 / Γ(1-α)` normalization. -/
def caputoFromDerivative (α t : ℝ) (dx : ℝ → E) : E :=
  (Real.Gamma (1 - α))⁻¹ • caputoHistoryCore α t dx

/-- A bounded time-independent linear map commutes exactly with the Caputo
history integral whenever the weighted derivative is interval-integrable. -/
theorem continuousLinearMap_caputoHistoryCore
    (B : E →L[ℝ] F) (α t : ℝ) (dx : ℝ → E)
    (hInt : IntervalIntegrable
      (fun s => Real.rpow (t - s) (-α) • dx s) volume 0 t) :
    B (caputoHistoryCore α t dx) =
      caputoHistoryCore α t (fun s => B (dx s)) := by
  unfold caputoHistoryCore
  have hcomm := B.intervalIntegral_comp_comm hInt
  calc
    B (∫ s in (0 : ℝ)..t, Real.rpow (t - s) (-α) • dx s) =
        ∫ s in (0 : ℝ)..t, B (Real.rpow (t - s) (-α) • dx s) := hcomm.symm
    _ = ∫ s in (0 : ℝ)..t, Real.rpow (t - s) (-α) • B (dx s) := by
      apply intervalIntegral.integral_congr
      intro s hs
      exact B.map_smul (Real.rpow (t - s) (-α)) (dx s)

/-- The full normalized Caputo memory commutes with every bounded constant
linear map.  In particular this applies to a bounded linear projector. -/
theorem continuousLinearMap_caputoFromDerivative
    (B : E →L[ℝ] F) (α t : ℝ) (dx : ℝ → E)
    (hInt : IntervalIntegrable
      (fun s => Real.rpow (t - s) (-α) • dx s) volume 0 t) :
    B (caputoFromDerivative α t dx) =
      caputoFromDerivative α t (fun s => B (dx s)) := by
  unfold caputoFromDerivative
  rw [B.map_smul]
  rw [continuousLinearMap_caputoHistoryCore B α t dx hInt]

/-- A constant bounded projector therefore preserves its own Caputo memory
packet. -/
theorem projector_caputoFromDerivative
    (B : E →L[ℝ] E)
    (hB : ∀ x, B (B x) = B x)
    (α t : ℝ) (dx : ℝ → E)
    (hInt : IntervalIntegrable
      (fun s => Real.rpow (t - s) (-α) • dx s) volume 0 t) :
    B (caputoFromDerivative α t (fun s => B (dx s))) =
      caputoFromDerivative α t (fun s => B (dx s)) := by
  rw [continuousLinearMap_caputoFromDerivative B α t (fun s => B (dx s))]
  · congr 1
    funext s
    rw [hB]
  · have hcomp : IntervalIntegrable
        (fun s => B (Real.rpow (t - s) (-α) • dx s)) volume 0 t := by
      constructor
      · exact B.integrable_comp hInt.1
      · exact B.integrable_comp hInt.2
    simpa only [B.map_smul] using hcomp

end CaputoMemory


/-! ## 7. Volterra packet reconstruction -/

section VolterraPackets

open MeasureTheory intervalIntegral

universe uV uLane

variable {V : Type uV} [NormedAddCommGroup V] [NormedSpace ℝ V] [CompleteSpace V]
variable {lane : Type uLane} [Fintype lane]

/-- A finite complete family of bounded linear packet projectors.  Orthogonality
is recorded because it is part of the projector calculus, although exact
Volterra reconstruction uses only completeness and linearity. -/
structure ContinuousProjectorFamily where
  proj : lane → V →L[ℝ] V
  idempotent : ∀ i x, proj i (proj i x) = proj i x
  orthogonal : ∀ {i j}, i ≠ j → ∀ x, proj i (proj j x) = 0
  complete : ∀ x, (∑ i, proj i x) = x

namespace ContinuousProjectorFamily

/-- Causal Volterra memory at time `t`. -/
def volterraMemory (K : ℝ → V →L[ℝ] V) (x : ℝ → V) (t : ℝ) : V :=
  ∫ s in (0 : ℝ)..t, K (t - s) (x s)

/-- One source-to-target packet contribution to Volterra memory. -/
def volterraPacketMemory
    (P : ContinuousProjectorFamily (V := V) (lane := lane))
    (K : ℝ → V →L[ℝ] V) (x : ℝ → V)
    (i j : lane) (t : ℝ) : V :=
  ∫ s in (0 : ℝ)..t, P.proj i (K (t - s) (P.proj j (x s)))

/-- Applying a bounded packet projector commutes with the global Volterra
integral. -/
theorem proj_volterraMemory
    (P : ContinuousProjectorFamily (V := V) (lane := lane))
    (K : ℝ → V →L[ℝ] V) (x : ℝ → V) (i : lane) (t : ℝ)
    (hInt : IntervalIntegrable (fun s => K (t - s) (x s)) volume 0 t) :
    P.proj i (volterraMemory K x t) =
      ∫ s in (0 : ℝ)..t, P.proj i (K (t - s) (x s)) := by
  unfold volterraMemory
  exact (P.proj i).intervalIntegral_comp_comm hInt |>.symm

omit [CompleteSpace V] in
/-- Pointwise insertion of the complete packet resolution inside a Volterra
kernel. -/
theorem volterra_integrand_packet_sum
    (P : ContinuousProjectorFamily (V := V) (lane := lane))
    (K : ℝ → V →L[ℝ] V) (x : ℝ → V) (i : lane) (t s : ℝ) :
    P.proj i (K (t - s) (x s)) =
      ∑ j, P.proj i (K (t - s) (P.proj j (x s))) := by
  calc
    P.proj i (K (t - s) (x s)) =
        P.proj i (K (t - s) (∑ j, P.proj j (x s))) := by
      rw [P.complete]
    _ = P.proj i (∑ j, K (t - s) (P.proj j (x s))) := by
      rw [map_sum]
    _ = ∑ j, P.proj i (K (t - s) (P.proj j (x s))) := by
      rw [map_sum]

/-- Exact Volterra packet reconstruction:
`Bᵢ ∫ K x = Σⱼ ∫ Bᵢ K Bⱼ x` under the explicit interval-integrability
hypotheses needed to exchange bounded maps and finite sums with the integral. -/
theorem volterraMemory_packet_reconstruction
    (P : ContinuousProjectorFamily (V := V) (lane := lane))
    (K : ℝ → V →L[ℝ] V) (x : ℝ → V) (i : lane) (t : ℝ)
    (hInt : IntervalIntegrable (fun s => K (t - s) (x s)) volume 0 t)
    (hPacketInt : ∀ j, IntervalIntegrable
      (fun s => P.proj i (K (t - s) (P.proj j (x s)))) volume 0 t) :
    P.proj i (volterraMemory K x t) =
      ∑ j, volterraPacketMemory P K x i j t := by
  rw [proj_volterraMemory P K x i t hInt]
  calc
    (∫ s in (0 : ℝ)..t, P.proj i (K (t - s) (x s))) =
        ∫ s in (0 : ℝ)..t,
          ∑ j, P.proj i (K (t - s) (P.proj j (x s))) := by
      apply intervalIntegral.integral_congr
      intro s hs
      exact volterra_integrand_packet_sum P K x i t s
    _ = ∑ j, ∫ s in (0 : ℝ)..t,
          P.proj i (K (t - s) (P.proj j (x s))) := by
      simpa using intervalIntegral.integral_finsetSum
        (s := (Finset.univ : Finset lane))
        (f := fun j s => P.proj i (K (t - s) (P.proj j (x s))))
        (by intro j hj; exact hPacketInt j)
    _ = ∑ j, volterraPacketMemory P K x i j t := by
      rfl

/-- Applying a packet projector to a global Volterra equation gives the exact
packet equation. -/
theorem volterraEquation_packet
    (P : ContinuousProjectorFamily (V := V) (lane := lane))
    (K : ℝ → V →L[ℝ] V) (x f : ℝ → V) (i : lane) (t : ℝ)
    (hEq : x t = f t + volterraMemory K x t)
    (hInt : IntervalIntegrable (fun s => K (t - s) (x s)) volume 0 t)
    (hPacketInt : ∀ j, IntervalIntegrable
      (fun s => P.proj i (K (t - s) (P.proj j (x s)))) volume 0 t) :
    P.proj i (x t) = P.proj i (f t) +
      ∑ j, volterraPacketMemory P K x i j t := by
  rw [hEq, map_add, volterraMemory_packet_reconstruction P K x i t hInt hPacketInt]

omit [CompleteSpace V] in
/-- Summing all packet equations reconstructs the original state value. -/
theorem volterraPacketState_reconstruction
    (P : ContinuousProjectorFamily (V := V) (lane := lane))
    (x : ℝ → V) (t : ℝ) :
    (∑ i, P.proj i (x t)) = x t :=
  P.complete (x t)

end ContinuousProjectorFamily

end VolterraPackets


/-! ## 8. Volterra path composition and finite exponential-memory output -/

section VolterraPathAndLift

open MeasureTheory intervalIntegral

universe uW uMode

variable {WSpace : Type uW}
variable [NormedAddCommGroup WSpace] [NormedSpace ℝ WSpace] [CompleteSpace WSpace]

/-- Operator-kernel convolution applied to a fixed vector. -/
def operatorKernelConvolutionApply
    (K L : ℝ → WSpace →L[ℝ] WSpace) (x : WSpace) (t : ℝ) : WSpace :=
  ∫ s in (0 : ℝ)..t, K (t - s) (L s x)

/-- One intermediate packet path inside an operator-kernel convolution. -/
def operatorKernelPacketPath
    {lane : Type*} [Fintype lane]
    (P : ContinuousProjectorFamily (V := WSpace) (lane := lane))
    (K L : ℝ → WSpace →L[ℝ] WSpace)
    (x : WSpace) (i k j : lane) (t : ℝ) : WSpace :=
  ∫ s in (0 : ℝ)..t,
    P.proj i (K (t - s) (P.proj k (L s (P.proj j x))))

/-- Memory-path contraction: after fixing source and target packets, convolution
is the sum over every intermediate packet. -/
theorem operatorKernelConvolution_packet_path
    {lane : Type*} [Fintype lane]
    (P : ContinuousProjectorFamily (V := WSpace) (lane := lane))
    (K L : ℝ → WSpace →L[ℝ] WSpace)
    (x : WSpace) (i j : lane) (t : ℝ)
    (hInt : IntervalIntegrable
      (fun s => K (t - s) (L s (P.proj j x))) volume 0 t)
    (hPathInt : ∀ k, IntervalIntegrable
      (fun s => P.proj i (K (t - s) (P.proj k (L s (P.proj j x))))) volume 0 t) :
    P.proj i (operatorKernelConvolutionApply K L (P.proj j x) t) =
      ∑ k, operatorKernelPacketPath P K L x i k j t := by
  unfold operatorKernelConvolutionApply
  rw [← (P.proj i).intervalIntegral_comp_comm hInt]
  calc
    (∫ s in (0 : ℝ)..t, P.proj i (K (t - s) (L s (P.proj j x)))) =
        ∫ s in (0 : ℝ)..t,
          ∑ k, P.proj i (K (t - s) (P.proj k (L s (P.proj j x)))) := by
      apply intervalIntegral.integral_congr
      intro s hs
      calc
        P.proj i (K (t - s) (L s (P.proj j x))) =
            P.proj i (K (t - s) (∑ k, P.proj k (L s (P.proj j x)))) := by
          rw [P.complete]
        _ = P.proj i (∑ k, K (t - s) (P.proj k (L s (P.proj j x)))) := by
          rw [map_sum]
        _ = ∑ k, P.proj i (K (t - s) (P.proj k (L s (P.proj j x)))) := by
          rw [map_sum]
    _ = ∑ k, ∫ s in (0 : ℝ)..t,
          P.proj i (K (t - s) (P.proj k (L s (P.proj j x)))) := by
      simpa using intervalIntegral.integral_finsetSum
        (s := (Finset.univ : Finset lane))
        (f := fun k s => P.proj i (K (t - s) (P.proj k (L s (P.proj j x)))))
        (by intro k hk; exact hPathInt k)
    _ = ∑ k, operatorKernelPacketPath P K L x i k j t := by
      rfl

variable {mode : Type uMode} [Fintype mode]

/-- Exponential memory state for one mode. -/
def exponentialMemoryState
    (rates : mode → ℝ) (x : ℝ → WSpace) (r : mode) (t : ℝ) : WSpace :=
  ∫ s in (0 : ℝ)..t, Real.exp (-rates r * (t - s)) • x s

/-- Memory output generated by a finite sum of exponential operator modes. -/
def finiteExponentialKernelMemory
    (W : mode → WSpace →L[ℝ] WSpace)
    (rates : mode → ℝ) (x : ℝ → WSpace) (t : ℝ) : WSpace :=
  ∫ s in (0 : ℝ)..t,
    ∑ r, Real.exp (-rates r * (t - s)) • W r (x s)

/-- Exact output half of the finite Markovian lift:
for a kernel `K(t)=Σᵣ Wᵣ exp(-λᵣt)`, the history term is exactly
`Σᵣ Wᵣ zᵣ(t)` with `zᵣ` the exponential memory state. -/
theorem finiteExponentialKernelMemory_eq_sum_states
    (W : mode → WSpace →L[ℝ] WSpace)
    (rates : mode → ℝ) (x : ℝ → WSpace) (t : ℝ)
    (hModeInt : ∀ r, IntervalIntegrable
      (fun s => Real.exp (-rates r * (t - s)) • x s) volume 0 t) :
    finiteExponentialKernelMemory W rates x t =
      ∑ r, W r (exponentialMemoryState rates x r t) := by
  unfold finiteExponentialKernelMemory exponentialMemoryState
  have hOutInt : ∀ r, IntervalIntegrable
      (fun s => Real.exp (-rates r * (t - s)) • W r (x s)) volume 0 t := by
    intro r
    have hc : IntervalIntegrable
        (fun s => W r (Real.exp (-rates r * (t - s)) • x s)) volume 0 t := by
      constructor
      · exact (W r).integrable_comp (hModeInt r).1
      · exact (W r).integrable_comp (hModeInt r).2
    simpa only [(W r).map_smul] using hc
  calc
    (∫ s in (0 : ℝ)..t, ∑ r, Real.exp (-rates r * (t - s)) • W r (x s)) =
        ∑ r, ∫ s in (0 : ℝ)..t, Real.exp (-rates r * (t - s)) • W r (x s) := by
      simpa using intervalIntegral.integral_finsetSum
        (s := (Finset.univ : Finset mode))
        (f := fun r s => Real.exp (-rates r * (t - s)) • W r (x s))
        (by intro r hr; exact hOutInt r)
    _ = ∑ r, W r (∫ s in (0 : ℝ)..t, Real.exp (-rates r * (t - s)) • x s) := by
      apply Finset.sum_congr rfl
      intro r hr
      have hcomm := (W r).intervalIntegral_comp_comm (hModeInt r)
      calc
        (∫ s in (0 : ℝ)..t, Real.exp (-rates r * (t - s)) • W r (x s)) =
            ∫ s in (0 : ℝ)..t, W r (Real.exp (-rates r * (t - s)) • x s) := by
          apply intervalIntegral.integral_congr
          intro s hs
          exact ((W r).map_smul (Real.exp (-rates r * (t - s))) (x s)).symm
        _ = W r (∫ s in (0 : ℝ)..t, Real.exp (-rates r * (t - s)) • x s) := hcomm

end VolterraPathAndLift


/-! ## 9. Differential law for finite exponential memory states -/

section ExponentialMemoryDerivative

open MeasureTheory intervalIntegral

universe uD

variable {D : Type uD}
variable [NormedAddCommGroup D] [NormedSpace ℝ D] [CompleteSpace D]

omit [CompleteSpace D] in
/-- Factor an exponential memory state into an integrating factor times an
ordinary variable-upper-limit integral. -/
theorem exponentialMemoryState_eq_factored
    {mode : Type*} [Fintype mode]
    (rates : mode → ℝ) (x : ℝ → D) (r : mode) (t : ℝ) :
    exponentialMemoryState rates x r t =
      Real.exp (-rates r * t) •
        (∫ s in (0 : ℝ)..t, Real.exp (rates r * s) • x s) := by
  unfold exponentialMemoryState
  calc
    (∫ s in (0 : ℝ)..t, Real.exp (-rates r * (t - s)) • x s) =
        ∫ s in (0 : ℝ)..t,
          Real.exp (-rates r * t) • (Real.exp (rates r * s) • x s) := by
      apply intervalIntegral.integral_congr
      intro s hs
      change Real.exp (-rates r * (t - s)) • x s =
        Real.exp (-rates r * t) • (Real.exp (rates r * s) • x s)
      have hscalar : Real.exp (-rates r * (t - s)) =
          Real.exp (-rates r * t) * Real.exp (rates r * s) := by
        rw [← Real.exp_add]
        congr 1
        ring
      rw [hscalar, mul_smul]
    _ = Real.exp (-rates r * t) •
        (∫ s in (0 : ℝ)..t, Real.exp (rates r * s) • x s) := by
      rw [intervalIntegral.integral_smul]

/-- Derivative of the scalar integrating factor. -/
theorem hasDerivAt_exp_neg_mul (rate t : ℝ) :
    HasDerivAt (fun u : ℝ => Real.exp (-rate * u))
      (-rate * Real.exp (-rate * t)) t := by
  have hlin : HasDerivAt (fun u : ℝ => -rate * u) (-rate) t := by
    simpa using (hasDerivAt_id t).const_mul (-rate)
  have h := (Real.hasDerivAt_exp (-rate * t)).comp t hlin
  simpa [Function.comp_def, mul_comm] using h

/-- Exact finite Markovian state law for one exponential memory mode.  The
weighted input is assumed interval-integrable and continuous at the endpoint,
which are precisely the FTC hypotheses used here. -/
theorem exponentialMemoryState_hasDerivAt
    {mode : Type*} [Fintype mode]
    (rates : mode → ℝ) (x : ℝ → D) (r : mode) (t : ℝ)
    (hInt : IntervalIntegrable
      (fun s => Real.exp (rates r * s) • x s) volume 0 t)
    (hMeas : StronglyMeasurableAtFilter
      (fun s => Real.exp (rates r * s) • x s) (nhds t) volume)
    (hCont : ContinuousAt (fun s => Real.exp (rates r * s) • x s) t) :
    HasDerivAt (fun u => exponentialMemoryState rates x r u)
      (x t - rates r • exponentialMemoryState rates x r t) t := by
  let F : ℝ → D := fun u => ∫ s in (0 : ℝ)..u, Real.exp (rates r * s) • x s
  have hF : HasDerivAt F (Real.exp (rates r * t) • x t) t := by
    exact intervalIntegral.integral_hasDerivAt_right hInt hMeas hCont
  have hg := hasDerivAt_exp_neg_mul (rates r) t
  have hprod : HasDerivAt
      (fun u => Real.exp (-rates r * u) • F u)
      (Real.exp (-rates r * t) • (Real.exp (rates r * t) • x t) +
        (-rates r * Real.exp (-rates r * t)) • F t) t :=
    hg.smul hF
  have hfun : (fun u => exponentialMemoryState rates x r u) =
      (fun u => Real.exp (-rates r * u) • F u) := by
    funext u
    exact exponentialMemoryState_eq_factored rates x r u
  rw [hfun]
  convert hprod using 1
  · simp only [smul_smul]
    have hexp : Real.exp (-rates r * t) * Real.exp (rates r * t) = 1 := by
      rw [← Real.exp_add]
      simp
    rw [hexp, one_smul]
    rw [exponentialMemoryState_eq_factored rates x r t]
    simp only [F]
    module

end ExponentialMemoryDerivative


/-! ## 10. Certified finite-horizon kernel approximation error -/

section KernelApproximationError

open MeasureTheory intervalIntegral

universe uE

variable {E : Type uE}
variable [NormedAddCommGroup E] [NormedSpace ℝ E] [CompleteSpace E]

/-- Causal scalar-kernel convolution against a Banach-space-valued history. -/
def scalarKernelMemory
    (k : ℝ → ℝ) (x : ℝ → E) (t : ℝ) : E :=
  ∫ s in (0 : ℝ)..t, k (t - s) • x s

omit [CompleteSpace E] in
/-- Exact finite-horizon `L¹-L∞` error certificate for replacing one causal
kernel by another.  The right side is the interval `L¹` error multiplied by a
uniform history bound. -/
theorem scalarKernelMemory_sub_bound
    (k kApprox : ℝ → ℝ) (x : ℝ → E) (t C : ℝ)
    (ht : 0 ≤ t)
    (hx : ∀ s ∈ Set.Ioc (0 : ℝ) t, ‖x s‖ ≤ C)
    (hIntK : IntervalIntegrable (fun s => k (t - s) • x s) volume 0 t)
    (hIntApprox : IntervalIntegrable (fun s => kApprox (t - s) • x s) volume 0 t)
    (hk : IntervalIntegrable (fun u => |k u - kApprox u|) volume 0 t) :
    ‖scalarKernelMemory k x t - scalarKernelMemory kApprox x t‖ ≤
      (∫ u in (0 : ℝ)..t, |k u - kApprox u|) * C := by
  have hdiff : scalarKernelMemory k x t - scalarKernelMemory kApprox x t =
      ∫ s in (0 : ℝ)..t, (k (t - s) - kApprox (t - s)) • x s := by
    unfold scalarKernelMemory
    rw [← intervalIntegral.integral_sub hIntK hIntApprox]
    apply intervalIntegral.integral_congr
    intro s hs
    simp only [sub_smul]
  rw [hdiff]
  have hkshift : IntervalIntegrable (fun s => |k (t - s) - kApprox (t - s)|) volume 0 t := by
    have h := (hk.comp_sub_left t).symm
    simpa using h
  have hbound : IntervalIntegrable
      (fun s => |k (t - s) - kApprox (t - s)| * C) volume 0 t :=
    hkshift.mul_const C
  calc
    ‖∫ s in (0 : ℝ)..t, (k (t - s) - kApprox (t - s)) • x s‖ ≤
        ∫ s in (0 : ℝ)..t, |k (t - s) - kApprox (t - s)| * C := by
      apply intervalIntegral.norm_integral_le_of_norm_le ht
      · filter_upwards with s hs
        rw [norm_smul, Real.norm_eq_abs]
        exact mul_le_mul_of_nonneg_left (hx s hs) (abs_nonneg _)
      · exact hbound
    _ = (∫ u in (0 : ℝ)..t, |k u - kApprox u|) * C := by
      rw [intervalIntegral.integral_mul_const]
      have hrev : (∫ s in (0 : ℝ)..t, |k (t - s) - kApprox (t - s)|) =
          ∫ u in (0 : ℝ)..t, |k u - kApprox u| := by
        simpa using (intervalIntegral.integral_comp_sub_left
          (fun u : ℝ => |k u - kApprox u|) t (a := (0 : ℝ)) (b := t))
      rw [hrev]


/-- Causal memory generated by an operator-valued kernel. -/
def operatorValuedKernelMemory
    (K : ℝ → E →L[ℝ] E) (x : ℝ → E) (t : ℝ) : E :=
  ∫ s in (0 : ℝ)..t, K (t - s) (x s)

omit [CompleteSpace E] in
/-- Operator-valued form of the finite-horizon kernel certificate, using the
operator norm exactly as stated in the manuscript. -/
theorem operatorValuedKernelMemory_sub_bound
    (K KApprox : ℝ → E →L[ℝ] E) (x : ℝ → E) (t C : ℝ)
    (ht : 0 ≤ t)
    (hx : ∀ s ∈ Set.Ioc (0 : ℝ) t, ‖x s‖ ≤ C)
    (hIntK : IntervalIntegrable (fun s => K (t - s) (x s)) volume 0 t)
    (hIntApprox : IntervalIntegrable (fun s => KApprox (t - s) (x s)) volume 0 t)
    (hKdiff : IntervalIntegrable (fun u => ‖K u - KApprox u‖) volume 0 t) :
    ‖operatorValuedKernelMemory K x t - operatorValuedKernelMemory KApprox x t‖ ≤
      (∫ u in (0 : ℝ)..t, ‖K u - KApprox u‖) * C := by
  have hdiff : operatorValuedKernelMemory K x t - operatorValuedKernelMemory KApprox x t =
      ∫ s in (0 : ℝ)..t, (K (t - s) - KApprox (t - s)) (x s) := by
    unfold operatorValuedKernelMemory
    rw [← intervalIntegral.integral_sub hIntK hIntApprox]
    apply intervalIntegral.integral_congr
    intro s hs
    rfl
  rw [hdiff]
  have hshift : IntervalIntegrable
      (fun s => ‖K (t - s) - KApprox (t - s)‖) volume 0 t := by
    have h := (hKdiff.comp_sub_left t).symm
    simpa using h
  have hbound : IntervalIntegrable
      (fun s => ‖K (t - s) - KApprox (t - s)‖ * C) volume 0 t :=
    hshift.mul_const C
  calc
    ‖∫ s in (0 : ℝ)..t, (K (t - s) - KApprox (t - s)) (x s)‖ ≤
        ∫ s in (0 : ℝ)..t, ‖K (t - s) - KApprox (t - s)‖ * C := by
      apply intervalIntegral.norm_integral_le_of_norm_le ht
      · filter_upwards with s hs
        exact (ContinuousLinearMap.le_opNorm (K (t - s) - KApprox (t - s)) (x s)).trans
          (mul_le_mul_of_nonneg_left (hx s hs) (norm_nonneg _))
      · exact hbound
    _ = (∫ u in (0 : ℝ)..t, ‖K u - KApprox u‖) * C := by
      rw [intervalIntegral.integral_mul_const]
      have hrev : (∫ s in (0 : ℝ)..t, ‖K (t - s) - KApprox (t - s)‖) =
          ∫ u in (0 : ℝ)..t, ‖K u - KApprox u‖ := by
        simpa using (intervalIntegral.integral_comp_sub_left
          (fun u : ℝ => ‖K u - KApprox u‖) t (a := (0 : ℝ)) (b := t))
      rw [hrev]

end KernelApproximationError


/-! ## 11. Factorial Volterra-iterate bound -/

section VolterraResolventBound

open MeasureTheory intervalIntegral

/-- Scalar causal Volterra convolution. -/
def scalarVolterraConvolution (f g : ℝ → ℝ) (t : ℝ) : ℝ :=
  ∫ s in (0 : ℝ)..t, f (t - s) * g s

/-- `scalarVolterraIterate k n` is the `(n+1)`-fold causal convolution power
of `k`; index zero is the original kernel. -/
def scalarVolterraIterate (k : ℝ → ℝ) : ℕ → ℝ → ℝ
  | 0 => k
  | n + 1 => fun t => scalarVolterraConvolution k (scalarVolterraIterate k n) t

/-- Manuscript factorial estimate in zero-based indexing:
`‖K^{*(n+1)}(t)‖ ≤ M^(n+1) t^n / n!` on a finite horizon. -/
theorem scalarVolterraIterate_bound
    (k : ℝ → ℝ) (M T : ℝ) (hM : 0 ≤ M)
    (hk : ∀ u, 0 ≤ u → u ≤ T → |k u| ≤ M) :
    ∀ n : ℕ, ∀ t : ℝ, 0 ≤ t → t ≤ T →
      ‖scalarVolterraIterate k n t‖ ≤
        M ^ (n + 1) * t ^ n / (n.factorial : ℝ) := by
  intro n
  induction n with
  | zero =>
      intro t ht hT
      simpa [scalarVolterraIterate] using hk t ht hT
  | succ n ih =>
      intro t ht hT
      unfold scalarVolterraIterate scalarVolterraConvolution
      let g : ℝ → ℝ := fun s =>
        (M ^ (n + 2) / (n.factorial : ℝ)) * s ^ n
      have hgInt : IntervalIntegrable g volume 0 t := by
        exact (continuous_const.mul (continuous_id.pow n)).intervalIntegrable 0 t
      have hle : ‖∫ s in (0 : ℝ)..t,
          k (t - s) * scalarVolterraIterate k n s‖ ≤ ∫ s in (0 : ℝ)..t, g s := by
        apply intervalIntegral.norm_integral_le_of_norm_le ht
        · filter_upwards with s hs
          have hs0 : 0 ≤ s := le_of_lt hs.1
          have hst : s ≤ t := hs.2
          have hts0 : 0 ≤ t - s := sub_nonneg.mpr hst
          have htsT : t - s ≤ T := by linarith
          have hk' := hk (t - s) hts0 htsT
          have ih' := ih s hs0 (hst.trans hT)
          calc
            ‖k (t - s) * scalarVolterraIterate k n s‖ =
                |k (t - s)| * ‖scalarVolterraIterate k n s‖ := by
              rw [norm_mul, Real.norm_eq_abs]
            _ ≤ M * (M ^ (n + 1) * s ^ n / (n.factorial : ℝ)) := by
              exact mul_le_mul hk' ih' (norm_nonneg _) hM
            _ = g s := by
              dsimp [g]
              ring
        · exact hgInt
      refine hle.trans_eq ?_
      dsimp [g]
      rw [intervalIntegral.integral_const_mul]
      rw [integral_pow]
      rw [Nat.factorial_succ, Nat.cast_mul, Nat.cast_succ]
      have hfac : (n.factorial : ℝ) ≠ 0 := by positivity
      have hn1 : (n : ℝ) + 1 ≠ 0 := by positivity
      field_simp [hfac, hn1]
      ring


/-- The factorial majorant itself is summable on every finite horizon. -/
theorem summable_volterra_majorant (M T : ℝ) :
    Summable (fun n : ℕ => M * ((M * T) ^ n / (n.factorial : ℝ))) :=
  (Real.summable_pow_div_factorial (M * T)).mul_left M

/-- Full finite-horizon resolvent conclusion: the series of causal convolution
powers converges uniformly on `[0,T]` by the factorial majorant. -/
theorem scalarVolterraIterate_tendstoUniformlyOn
    (k : ℝ → ℝ) (M T : ℝ) (hM : 0 ≤ M)
    (hk : ∀ u, 0 ≤ u → u ≤ T → |k u| ≤ M) :
    TendstoUniformlyOn
      (fun N : ℕ => fun t : ℝ => ∑ n ∈ Finset.range N, scalarVolterraIterate k n t)
      (fun t : ℝ => ∑' n : ℕ, scalarVolterraIterate k n t)
      Filter.atTop (Set.Icc (0 : ℝ) T) := by
  apply tendstoUniformlyOn_tsum_nat (summable_volterra_majorant M T)
  intro n t htIcc
  have hb := scalarVolterraIterate_bound k M T hM hk n t htIcc.1 htIcc.2
  refine hb.trans ?_
  have hpow : t ^ n ≤ T ^ n :=
    pow_le_pow_left₀ htIcc.1 htIcc.2 n
  have hcoef : 0 ≤ M ^ (n + 1) / (n.factorial : ℝ) := by positivity
  calc
    M ^ (n + 1) * t ^ n / (n.factorial : ℝ) =
        (M ^ (n + 1) / (n.factorial : ℝ)) * t ^ n := by ring
    _ ≤ (M ^ (n + 1) / (n.factorial : ℝ)) * T ^ n :=
      mul_le_mul_of_nonneg_left hpow hcoef
    _ = M * ((M * T) ^ n / (n.factorial : ℝ)) := by
      rw [mul_pow]
      rw [pow_succ]
      ring

end VolterraResolventBound




/-! ## 12. Augmented finite-memory Kalman synthesis -/

section AugmentedMemoryKalman

universe uAS uAM uAP uAO

variable {aState : Type uAS} {aMode : Type uAM} {aPacket : Type uAP} {aObs : Type uAO}
variable [Fintype aState] [Fintype aMode] [Fintype aObs]
variable [DecidableEq aState] [DecidableEq aMode] [DecidableEq aObs]

/-- Coordinates of the exact finite Markovian lift: the physical state plus
one state-sized memory copy for every exponential mode. -/
abbrev MemoryAugIndex (aState : Type uAS) (aMode : Type uAM) := Sum aState (aMode × aState)

/-- Memory coordinates inherit the packet label of their underlying physical
state coordinate. -/
def memoryAugPacket (spacket : aState → aPacket) : MemoryAugIndex aState aMode → aPacket
  | Sum.inl i => spacket i
  | Sum.inr (_, i) => spacket i

/-- Exact augmented drift corresponding to
`x' = A₀ x + Σᵣ Wᵣ zᵣ` and `zᵣ' = x - λᵣ zᵣ`. -/
def memoryAugDrift
    (A0 : Matrix aState aState ℝ)
    (W : aMode → Matrix aState aState ℝ)
    (rates : aMode → ℝ) : Matrix (MemoryAugIndex aState aMode) (MemoryAugIndex aState aMode) ℝ
  | Sum.inl i, Sum.inl j => A0 i j
  | Sum.inl i, Sum.inr (r, j) => W r i j
  | Sum.inr (_r, i), Sum.inl j => if i = j then 1 else 0
  | Sum.inr (r, i), Sum.inr (s, j) => if r = s ∧ i = j then -rates r else 0

/-- Lift a physical covariance/noise matrix to the augmented space with zero
memory covariance blocks. -/
def liftPhysicalCovariance
    (Q : Matrix aState aState ℝ) : Matrix (MemoryAugIndex aState aMode) (MemoryAugIndex aState aMode) ℝ
  | Sum.inl i, Sum.inl j => Q i j
  | _, _ => 0

/-- Observations acting only on the physical component of the augmented state. -/
def memoryAugObservation
    (H : Matrix aObs aState ℝ) : Matrix aObs (MemoryAugIndex aState aMode) ℝ
  | o, Sum.inl j => H o j
  | _, Sum.inr _ => 0

omit [Fintype aState] [Fintype aMode] in

/-- Assemble a physical state and its exponential-memory modes into one finite
augmented coordinate vector. -/
def memoryAugVector
    (x : aState → ℝ) (z : aMode → aState → ℝ) : MemoryAugIndex aState aMode → ℝ
  | Sum.inl i => x i
  | Sum.inr (r, i) => z r i

/-- The physical coordinates of the augmented drift are exactly
`A₀ x + Σᵣ Wᵣ zᵣ`. -/
theorem memoryAugDrift_mulVec_physical
    (A0 : Matrix aState aState ℝ)
    (W : aMode → Matrix aState aState ℝ) (rates : aMode → ℝ)
    (x : aState → ℝ) (z : aMode → aState → ℝ) (i : aState) :
    Matrix.mulVec (memoryAugDrift A0 W rates) (memoryAugVector x z) (Sum.inl i) =
      Matrix.mulVec A0 x i + ∑ r, Matrix.mulVec (W r) (z r) i := by
  simp_rw [Matrix.mulVec, dotProduct, Fintype.sum_sum_type, Fintype.sum_prod_type,
    memoryAugDrift, memoryAugVector]

/-- The memory coordinates of the augmented drift are exactly
`x - λᵣ zᵣ`. -/
theorem memoryAugDrift_mulVec_memory
    (A0 : Matrix aState aState ℝ)
    (W : aMode → Matrix aState aState ℝ) (rates : aMode → ℝ)
    (x : aState → ℝ) (z : aMode → aState → ℝ) (r : aMode) (i : aState) :
    Matrix.mulVec (memoryAugDrift A0 W rates) (memoryAugVector x z) (Sum.inr (r, i)) =
      x i - rates r * z r i := by
  simp_rw [Matrix.mulVec, dotProduct, Fintype.sum_sum_type, Fintype.sum_prod_type,
    memoryAugDrift, memoryAugVector]
  have hphys :
      (∑ j : aState, (if i = j then (1 : ℝ) else 0) * x j) = x i := by
    classical
    rw [Finset.sum_eq_single i]
    · simp
    · intro j hj hji
      simp [Ne.symm hji]
    · simp
  have hmem :
      (∑ s : aMode, ∑ j : aState,
        (if r = s ∧ i = j then -rates r else 0) * z s j) =
        -(rates r * z r i) := by
    classical
    rw [Finset.sum_eq_single r]
    · rw [Finset.sum_eq_single i]
      · simp
      · intro j hj hji
        simp [Ne.symm hji]
      · simp
    · intro s hs hsr
      apply Finset.sum_eq_zero
      intro j hj
      simp [Ne.symm hsr]
    · simp
  rw [hphys, hmem]
  ring

omit [Fintype aState] [Fintype aMode] in
/-- Packet alignment is preserved by the exact finite-memory augmented drift. -/
theorem memoryAugDrift_block
    (spacket : aState → aPacket)
    (A0 : Matrix aState aState ℝ)
    (W : aMode → Matrix aState aState ℝ)
    (rates : aMode → ℝ)
    (hA : BlockRespecting spacket spacket A0)
    (hW : ∀ r, BlockRespecting spacket spacket (W r)) :
    BlockRespecting (memoryAugPacket (aMode := aMode) spacket) (memoryAugPacket (aMode := aMode) spacket)
      (memoryAugDrift A0 W rates) := by
  intro i j hij
  cases i with
  | inl i =>
      cases j with
      | inl j =>
          exact hA i j hij
      | inr rj =>
          rcases rj with ⟨r, j⟩
          exact hW r i j hij
  | inr ri =>
      rcases ri with ⟨r, i⟩
      cases j with
      | inl j =>
          unfold memoryAugDrift
          by_cases hEq : i = j
          · subst j
            exact (hij rfl).elim
          · simp [hEq]
      | inr sj =>
          rcases sj with ⟨s, j⟩
          unfold memoryAugDrift
          by_cases hEq : i = j
          · subst j
            exact (hij rfl).elim
          · simp [hEq]

omit [Fintype aState] [Fintype aMode] [DecidableEq aState] [DecidableEq aMode] in
/-- Physical covariance/noise lifting preserves packet block structure. -/
theorem liftPhysicalCovariance_block
    (spacket : aState → aPacket)
    (Q : Matrix aState aState ℝ)
    (hQ : BlockRespecting spacket spacket Q) :
    BlockRespecting (memoryAugPacket (aMode := aMode) spacket) (memoryAugPacket (aMode := aMode) spacket)
      (liftPhysicalCovariance (aMode := aMode) Q) := by
  intro i j hij
  cases i <;> cases j
  · exact hQ _ _ hij
  · rfl
  · rfl
  · rfl

omit [Fintype aState] [Fintype aMode] [Fintype aObs] [DecidableEq aState] [DecidableEq aMode] [DecidableEq aObs] in
/-- A physical observation matrix remains packet-compatible after augmentation. -/
theorem memoryAugObservation_block
    (spacket : aState → aPacket) (opacket : aObs → aPacket)
    (H : Matrix aObs aState ℝ)
    (hH : BlockRespecting opacket spacket H) :
    BlockRespecting opacket (memoryAugPacket (aMode := aMode) spacket) (memoryAugObservation (aMode := aMode) H) := by
  intro o j hoj
  cases j with
  | inl j => exact hH o j hoj
  | inr rj => rfl


/-- Recursive augmented-filter closure: once a covariance on the physical-plus-memory
state respects the inherited packet labels, one full Joseph-form Kalman step
preserves that structure.  This version is suitable for induction over filter
time because `Paug` may already contain nonzero physical-memory covariances
inside each packet. -/
theorem finite_memory_augmented_kalman_recursive_closure
    (spacket : aState → aPacket) (opacket : aObs → aPacket)
    (A0 : Matrix aState aState ℝ)
    (W : aMode → Matrix aState aState ℝ) (rates : aMode → ℝ)
    (Paug Qaug : Matrix (MemoryAugIndex aState aMode) (MemoryAugIndex aState aMode) ℝ)
    (H : Matrix aObs aState ℝ) (Robs Sinv : Matrix aObs aObs ℝ)
    (hA : BlockRespecting spacket spacket A0)
    (hW : ∀ r, BlockRespecting spacket spacket (W r))
    (hPaug : BlockRespecting (memoryAugPacket (aMode := aMode) spacket)
      (memoryAugPacket (aMode := aMode) spacket) Paug)
    (hQaug : BlockRespecting (memoryAugPacket (aMode := aMode) spacket)
      (memoryAugPacket (aMode := aMode) spacket) Qaug)
    (hH : BlockRespecting opacket spacket H)
    (hR : BlockRespecting opacket opacket Robs)
    (hLeft : kalmanInnovation (memoryAugObservation (aMode := aMode) H)
        (kalmanPredCov (memoryAugDrift A0 W rates) Paug Qaug) Robs * Sinv = 1)
    (hRight : Sinv * kalmanInnovation (memoryAugObservation (aMode := aMode) H)
        (kalmanPredCov (memoryAugDrift A0 W rates) Paug Qaug) Robs = 1) :
    let Aaug := memoryAugDrift A0 W rates
    let Haug := memoryAugObservation (aMode := aMode) H
    let Ppred := kalmanPredCov Aaug Paug Qaug
    let Sinnov := kalmanInnovation Haug Ppred Robs
    let K := kalmanGain Ppred Haug Sinv
    BlockRespecting (memoryAugPacket (aMode := aMode) spacket)
      (memoryAugPacket (aMode := aMode) spacket) Ppred ∧
    BlockRespecting opacket opacket Sinnov ∧
    BlockRespecting (memoryAugPacket (aMode := aMode) spacket) opacket K ∧
    BlockRespecting (memoryAugPacket (aMode := aMode) spacket)
      (memoryAugPacket (aMode := aMode) spacket)
      (kalmanJosephCovUpdate K Haug Ppred Robs) := by
  dsimp only
  have hAaug := memoryAugDrift_block spacket A0 W rates hA hW
  have hHaug := memoryAugObservation_block (aMode := aMode) spacket opacket H hH
  exact kalman_joseph_block_closure_of_twoSided_inverse
    (memoryAugPacket (aMode := aMode) spacket) opacket
    (memoryAugDrift A0 W rates) Paug Qaug
    (memoryAugObservation (aMode := aMode) H) Robs Sinv
    hAaug hPaug hQaug hHaug hR hLeft hRight

/-- Exact structural synthesis for hereditary linear Gaussian models with a
finite exponential memory kernel: after the Markovian lift, aligned physical
and memory packets satisfy the same Joseph-form direct-sum Kalman closure as an
ordinary finite-dimensional system. -/
theorem finite_memory_augmented_kalman_closure
    (spacket : aState → aPacket) (opacket : aObs → aPacket)
    (A0 P Q : Matrix aState aState ℝ)
    (W : aMode → Matrix aState aState ℝ) (rates : aMode → ℝ)
    (H : Matrix aObs aState ℝ) (Robs Sinv : Matrix aObs aObs ℝ)
    (hA : BlockRespecting spacket spacket A0)
    (hW : ∀ r, BlockRespecting spacket spacket (W r))
    (hP : BlockRespecting spacket spacket P)
    (hQ : BlockRespecting spacket spacket Q)
    (hH : BlockRespecting opacket spacket H)
    (hR : BlockRespecting opacket opacket Robs)
    (hLeft : kalmanInnovation (memoryAugObservation (aMode := aMode) H)
        (kalmanPredCov (memoryAugDrift A0 W rates) (liftPhysicalCovariance (aMode := aMode) P)
          (liftPhysicalCovariance (aMode := aMode) Q)) Robs * Sinv = 1)
    (hRight : Sinv * kalmanInnovation (memoryAugObservation (aMode := aMode) H)
        (kalmanPredCov (memoryAugDrift A0 W rates) (liftPhysicalCovariance (aMode := aMode) P)
          (liftPhysicalCovariance (aMode := aMode) Q)) Robs = 1) :
    let Aaug := memoryAugDrift A0 W rates
    let Paug := liftPhysicalCovariance (aMode := aMode) P
    let Qaug := liftPhysicalCovariance (aMode := aMode) Q
    let Haug := memoryAugObservation (aMode := aMode) H
    let Ppred := kalmanPredCov Aaug Paug Qaug
    let Sinnov := kalmanInnovation Haug Ppred Robs
    let K := kalmanGain Ppred Haug Sinv
    BlockRespecting (memoryAugPacket (aMode := aMode) spacket) (memoryAugPacket (aMode := aMode) spacket) Ppred ∧
    BlockRespecting opacket opacket Sinnov ∧
    BlockRespecting (memoryAugPacket (aMode := aMode) spacket) opacket K ∧
    BlockRespecting (memoryAugPacket (aMode := aMode) spacket) (memoryAugPacket (aMode := aMode) spacket)
      (kalmanJosephCovUpdate K Haug Ppred Robs) := by
  dsimp only
  have hAaug := memoryAugDrift_block spacket A0 W rates hA hW
  have hPaug := liftPhysicalCovariance_block (aMode := aMode) spacket P hP
  have hQaug := liftPhysicalCovariance_block (aMode := aMode) spacket Q hQ
  have hHaug := memoryAugObservation_block (aMode := aMode) spacket opacket H hH
  exact kalman_joseph_block_closure_of_twoSided_inverse
    (memoryAugPacket (aMode := aMode) spacket) opacket
    (memoryAugDrift A0 W rates) (liftPhysicalCovariance (aMode := aMode) P) (liftPhysicalCovariance (aMode := aMode) Q)
    (memoryAugObservation (aMode := aMode) H) Robs Sinv
    hAaug hPaug hQaug hHaug hR hLeft hRight

end AugmentedMemoryKalman

/-! ## 12. Operator-valued Volterra resolvent convergence -/

section OperatorVolterraResolvent

open MeasureTheory intervalIntegral

universe uOV

variable {OV : Type uOV}
variable [NormedAddCommGroup OV] [NormedSpace ℝ OV] [CompleteSpace OV]

/-- Causal convolution of two operator-valued kernels. -/
def operatorVolterraConvolution
    (K L : ℝ → OV →L[ℝ] OV) (t : ℝ) : OV →L[ℝ] OV :=
  ∫ s in (0 : ℝ)..t, (K (t - s)).comp (L s)

/-- Zero-based operator-valued convolution powers: index zero is the kernel. -/
def operatorVolterraIterate (K : ℝ → OV →L[ℝ] OV) : ℕ → ℝ → OV →L[ℝ] OV
  | 0 => K
  | n + 1 => fun t => operatorVolterraConvolution K (operatorVolterraIterate K n) t

omit [CompleteSpace OV] in
/-- Operator-valued factorial Volterra estimate. -/
theorem operatorVolterraIterate_bound
    (K : ℝ → OV →L[ℝ] OV) (M T : ℝ) (hM : 0 ≤ M)
    (hK : ∀ u, 0 ≤ u → u ≤ T → ‖K u‖ ≤ M) :
    ∀ n : ℕ, ∀ t : ℝ, 0 ≤ t → t ≤ T →
      ‖operatorVolterraIterate K n t‖ ≤
        M ^ (n + 1) * t ^ n / (n.factorial : ℝ) := by
  intro n
  induction n with
  | zero =>
      intro t ht hT
      simpa [operatorVolterraIterate] using hK t ht hT
  | succ n ih =>
      intro t ht hT
      unfold operatorVolterraIterate operatorVolterraConvolution
      let g : ℝ → ℝ := fun s =>
        (M ^ (n + 2) / (n.factorial : ℝ)) * s ^ n
      have hgInt : IntervalIntegrable g volume 0 t := by
        exact (continuous_const.mul (continuous_id.pow n)).intervalIntegrable 0 t
      have hle : ‖∫ s in (0 : ℝ)..t,
          (K (t - s)).comp (operatorVolterraIterate K n s)‖ ≤
          ∫ s in (0 : ℝ)..t, g s := by
        apply intervalIntegral.norm_integral_le_of_norm_le ht
        · filter_upwards with s hs
          have hs0 : 0 ≤ s := le_of_lt hs.1
          have hst : s ≤ t := hs.2
          have hts0 : 0 ≤ t - s := sub_nonneg.mpr hst
          have htsT : t - s ≤ T := by linarith
          have hk' := hK (t - s) hts0 htsT
          have ih' := ih s hs0 (hst.trans hT)
          calc
            ‖(K (t - s)).comp (operatorVolterraIterate K n s)‖ ≤
                ‖K (t - s)‖ * ‖operatorVolterraIterate K n s‖ :=
              ContinuousLinearMap.opNorm_comp_le _ _
            _ ≤ M * (M ^ (n + 1) * s ^ n / (n.factorial : ℝ)) := by
              exact mul_le_mul hk' ih' (norm_nonneg _) hM
            _ = g s := by
              dsimp [g]
              ring
        · exact hgInt
      refine hle.trans_eq ?_
      dsimp [g]
      rw [intervalIntegral.integral_const_mul]
      rw [integral_pow]
      rw [Nat.factorial_succ, Nat.cast_mul, Nat.cast_succ]
      have hfac : (n.factorial : ℝ) ≠ 0 := by positivity
      have hn1 : (n : ℝ) + 1 ≠ 0 := by positivity
      field_simp [hfac, hn1]
      ring

/-- The operator-valued Volterra resolvent series converges uniformly on every
finite horizon under a uniform operator-norm bound. -/
theorem operatorVolterraIterate_tendstoUniformlyOn
    (K : ℝ → OV →L[ℝ] OV) (M T : ℝ) (hM : 0 ≤ M)
    (hK : ∀ u, 0 ≤ u → u ≤ T → ‖K u‖ ≤ M) :
    TendstoUniformlyOn
      (fun N : ℕ => fun t : ℝ => ∑ n ∈ Finset.range N, operatorVolterraIterate K n t)
      (fun t : ℝ => ∑' n : ℕ, operatorVolterraIterate K n t)
      Filter.atTop (Set.Icc (0 : ℝ) T) := by
  apply tendstoUniformlyOn_tsum_nat (summable_volterra_majorant M T)
  intro n t htIcc
  have hb := operatorVolterraIterate_bound K M T hM hK n t htIcc.1 htIcc.2
  refine hb.trans ?_
  have hpow : t ^ n ≤ T ^ n := pow_le_pow_left₀ htIcc.1 htIcc.2 n
  have hcoef : 0 ≤ M ^ (n + 1) / (n.factorial : ℝ) := by positivity
  calc
    M ^ (n + 1) * t ^ n / (n.factorial : ℝ) =
        (M ^ (n + 1) / (n.factorial : ℝ)) * t ^ n := by ring
    _ ≤ (M ^ (n + 1) / (n.factorial : ℝ)) * T ^ n :=
      mul_le_mul_of_nonneg_left hpow hcoef
    _ = M * ((M * T) ^ n / (n.factorial : ℝ)) := by
      rw [mul_pow]
      rw [pow_succ]
      ring

end OperatorVolterraResolvent

/-! ## 14. Gaussian packet independence -/

section GaussianPacketIndependence

open MeasureTheory ProbabilityTheory

universe uΩ uGI uGK

variable {Ω : Type uΩ} [MeasurableSpace Ω]
variable {Pmeasure : Measure Ω}
variable {packetIndex : Type uGI} [Finite packetIndex]
variable {packetCoord : packetIndex → Type uGK}
variable [∀ i, Finite (packetCoord i)]
variable {Xpacket : (i : packetIndex) → packetCoord i → Ω → ℝ}

/-- Semantic direct-sum bridge for Gaussian packets: if the entire finite packet
family is jointly Gaussian and every cross-packet coordinate covariance is zero,
then the packet-valued random variables are independent.  This is the exact
Gaussian fact needed to turn block covariance into probabilistic packet
independence; it is distinct from the still-open conditioning theorem
"Kalman update = Gaussian Bayes". -/
theorem gaussian_packets_independent_of_cross_covariance_zero
    (hX : HasGaussianLaw (fun ω i j => Xpacket i j ω) Pmeasure)
    (hcross : ∀ i j, i ≠ j → ∀ k l,
      cov[Xpacket i k, Xpacket j l; Pmeasure] = 0) :
    iIndepFun (fun i ω j => Xpacket i j ω) Pmeasure :=
  hX.iIndepFun_of_covariance_eval hcross

end GaussianPacketIndependence


section GaussianBlockSemanticClosure

open MeasureTheory ProbabilityTheory

universe uGS uGP uGO

variable {gState : Type uGS} [Finite gState]
variable {gPacket : Type uGP} [Finite gPacket]
variable {Ωg : Type uGO} [MeasurableSpace Ωg]
variable {μg : Measure Ωg}

/-- A block-respecting covariance matrix has a direct Gaussian semantic
interpretation.  If the packet-grouped coordinate family is jointly Gaussian
and its scalar coordinate covariances are represented by `Pcov`, then distinct
packet subvectors are independent. -/
theorem gaussian_packet_independence_of_block_covariance
    (packet : gState → gPacket)
    (X : gState → Ωg → ℝ)
    (Pcov : Matrix gState gState ℝ)
    (hblock : BlockRespecting packet packet Pcov)
    (hcov : ∀ i j, cov[X i, X j; μg] = Pcov i j)
    (hX : HasGaussianLaw
      (fun ω (p : gPacket) (s : {i : gState // packet i = p}) => X s.1 ω) μg) :
    iIndepFun
      (fun p ω (s : {i : gState // packet i = p}) => X s.1 ω) μg := by
  apply gaussian_packets_independent_of_cross_covariance_zero hX
  intro p q hpq i j
  rw [hcov]
  apply hblock
  intro heq
  apply hpq
  calc
    p = packet i.1 := i.2.symm
    _ = packet j.1 := heq
    _ = q := j.2

end GaussianBlockSemanticClosure


/-! ## 15. Genuine Brownian-driven affine Itô process -/

namespace Stochastic

open MeasureTheory ProbabilityTheory
open scoped NNReal ENNReal

universe uStochΩ

variable {Ω : Type uStochΩ} {mΩ : MeasurableSpace Ω}
variable {B : ℝ≥0 → Ω → ℝ} {P : Measure Ω}

/-- Constant-coefficient affine Itô process driven by a real Brownian motion. -/
def affineIto (B : ℝ≥0 → Ω → ℝ) (x0 drift vol : ℝ) (t : ℝ≥0) (ω : Ω) : ℝ :=
  x0 + drift * (t : ℝ) + vol * B t ω

/-- The exact one-time Gaussian law of the affine Itô process. -/
theorem affineIto_hasLaw
    (hB : IsPreBrownianReal B P) (x0 drift vol : ℝ) (t : ℝ≥0) :
    HasLaw (affineIto B x0 drift vol t)
      (ProbabilityTheory.gaussianReal (x0 + drift * (t : ℝ))
        ((Real.toNNReal (vol ^ 2)) * t)) P := by
  have h0 := hB.hasLaw_eval t
  have h1 := ProbabilityTheory.gaussianReal_const_mul h0 vol
  have h2 := ProbabilityTheory.gaussianReal_const_add h1 (x0 + drift * (t : ℝ))
  convert h2 using 1
  · funext ω
    simp [affineIto, add_comm, add_left_comm]
  · simp [Real.toNNReal_of_nonneg (sq_nonneg vol)]

/-- Mean of a constant-coefficient affine Itô process. -/
theorem affineIto_mean
    (hB : IsPreBrownianReal B P) (x0 drift vol : ℝ) (t : ℝ≥0) :
    P[affineIto B x0 drift vol t] = x0 + drift * (t : ℝ) := by
  have h := affineIto_hasLaw hB x0 drift vol t
  rw [h.integral_eq, ProbabilityTheory.integral_id_gaussianReal]

/-- Variance of a constant-coefficient affine Itô process. -/
theorem affineIto_variance
    (hB : IsPreBrownianReal B P) (x0 drift vol : ℝ) (t : ℝ≥0) :
    Var[affineIto B x0 drift vol t; P] = vol ^ 2 * (t : ℝ) := by
  have h := affineIto_hasLaw hB x0 drift vol t
  rw [h.variance_eq, ProbabilityTheory.variance_id_gaussianReal]
  rw [NNReal.coe_mul, Real.coe_toNNReal (vol ^ 2) (sq_nonneg vol)]

set_option linter.style.haveILetI false in
/-- Covariance kernel of a constant-coefficient affine Itô process. -/
theorem affineIto_covariance
    (hB : IsPreBrownianReal B P) (x0 drift vol : ℝ) (s t : ℝ≥0) :
    cov[affineIto B x0 drift vol s, affineIto B x0 drift vol t; P] =
      vol ^ 2 * (min s t : ℝ≥0) := by
  letI : IsProbabilityMeasure P := (hB.hasLaw_eval s).hasGaussianLaw.isProbabilityMeasure
  have hsB : Integrable (B s) P := hB.integrable_eval s
  have htB : Integrable (B t) P := hB.integrable_eval t
  have hs : Integrable (fun ω => vol * B s ω) P := hsB.const_mul vol
  have ht : Integrable (fun ω => vol * B t ω) P := htB.const_mul vol
  unfold affineIto
  rw [covariance_const_add_left hs, covariance_const_add_right ht,
    covariance_const_mul_left, covariance_const_mul_right, hB.covariance_eval]
  ring_nf

/-- Exact Gaussian law of every increment of the affine Itô process. -/
theorem affineIto_increment_hasLaw
    (hB : IsPreBrownianReal B P) (x0 drift vol : ℝ) (s t : ℝ≥0) :
    HasLaw (fun ω => affineIto B x0 drift vol s ω - affineIto B x0 drift vol t ω)
      (ProbabilityTheory.gaussianReal
        (drift * ((s : ℝ) - (t : ℝ)))
        ((Real.toNNReal (vol ^ 2)) * nndist (s : ℝ) (t : ℝ))) P := by
  have h0 := hB.hasLaw_sub s t
  have h1 := ProbabilityTheory.gaussianReal_const_mul h0 vol
  have h2 := ProbabilityTheory.gaussianReal_const_add h1
    (drift * ((s : ℝ) - (t : ℝ)))
  convert h2 using 1
  · funext ω
    simp [affineIto]
    ring
  · simp [Real.toNNReal_of_nonneg (sq_nonneg vol)]

/-- Mean of every affine Itô increment. -/
theorem affineIto_increment_mean
    (hB : IsPreBrownianReal B P) (x0 drift vol : ℝ) (s t : ℝ≥0) :
    P[fun ω => affineIto B x0 drift vol s ω - affineIto B x0 drift vol t ω] =
      drift * ((s : ℝ) - (t : ℝ)) := by
  have h := affineIto_increment_hasLaw hB x0 drift vol s t
  rw [h.integral_eq, ProbabilityTheory.integral_id_gaussianReal]

/-- Variance of every affine Itô increment. -/
theorem affineIto_increment_variance
    (hB : IsPreBrownianReal B P) (x0 drift vol : ℝ) (s t : ℝ≥0) :
    Var[fun ω => affineIto B x0 drift vol s ω - affineIto B x0 drift vol t ω; P] =
      vol ^ 2 * (nndist (s : ℝ) (t : ℝ) : ℝ≥0) := by
  have h := affineIto_increment_hasLaw hB x0 drift vol s t
  rw [h.variance_eq, ProbabilityTheory.variance_id_gaussianReal]
  rw [NNReal.coe_mul, Real.coe_toNNReal (vol ^ 2) (sq_nonneg vol)]


/-- The affine Itô process inherits independent increments from Brownian motion. -/
theorem affineIto_hasIndepIncrements
    (hB : IsPreBrownianReal B P) (x0 drift vol : ℝ) :
    HasIndepIncrements (affineIto B x0 drift vol) P := by
  intro n t ht
  have hInd := hB.hasIndepIncrements n t ht
  let g : Fin n → ℝ → ℝ := fun i z =>
    drift * (((t i.succ : ℝ≥0) : ℝ) - ((t i.castSucc : ℝ≥0) : ℝ)) + vol * z
  have hg : ∀ i, Measurable (g i) := by
    intro i
    fun_prop
  have hComp := hInd.comp g hg
  convert hComp using 1 with i ω
  simp [affineIto, g, Function.comp_def]
  ring_nf


/-- For an affine Itô process, the present state is independent of every future
increment. This is the constant-coefficient Markov/independent-increment bridge. -/
theorem affineIto_indepFun_state_futureIncrement
    (hB : IsPreBrownianReal B P) (x0 drift vol : ℝ)
    {s t : ℝ≥0} (hst : s ≤ t) :
    (affineIto B x0 drift vol s) ⟂ᵢ[P]
      (fun ω => affineIto B x0 drift vol t ω - affineIto B x0 drift vol s ω) := by
  have hBase := hB.hasIndepIncrements.indepFun_eval_sub
    (r := (0 : ℝ≥0)) (s := s) (t := t) (by simp) hst hB.eval_zero_ae_eq_zero
  let f : ℝ → ℝ := fun z => x0 + drift * (s : ℝ) + vol * z
  let g : ℝ → ℝ := fun z => drift * ((t : ℝ) - (s : ℝ)) + vol * z
  have hComp := hBase.comp (by fun_prop : Measurable f) (by fun_prop : Measurable g)
  convert hComp using 1
  · funext ω
    simp [affineIto, f]
  · funext ω
    simp [affineIto, g]
    ring_nf




/-- Exact finite-time mean evolution for the affine Itô process.  This is the
integrated scalar moment equation `m' = drift`. -/
theorem affineIto_mean_evolution
    (hB : IsPreBrownianReal B P) (x0 drift vol : ℝ) (s t : ℝ≥0) :
    P[affineIto B x0 drift vol t] - P[affineIto B x0 drift vol s] =
      drift * ((t : ℝ) - (s : ℝ)) := by
  rw [affineIto_mean hB x0 drift vol t, affineIto_mean hB x0 drift vol s]
  ring

/-- Exact finite-time variance evolution for the affine Itô process.  This is
the integrated scalar covariance equation `P' = vol²`. -/
theorem affineIto_variance_evolution
    (hB : IsPreBrownianReal B P) (x0 drift vol : ℝ) (s t : ℝ≥0) :
    Var[affineIto B x0 drift vol t; P] - Var[affineIto B x0 drift vol s; P] =
      vol ^ 2 * ((t : ℝ) - (s : ℝ)) := by
  rw [affineIto_variance hB x0 drift vol t, affineIto_variance hB x0 drift vol s]
  ring

end Stochastic


/-! ## Experimental theorem: stochastic covariance residual certificate -/

section CovarianceResidualCertificate

universe uResidualState uResidualPacket

variable {stateR : Type uResidualState} {packetR : Type uResidualPacket}
variable [Fintype stateR]

/-- Exact first-order residual identity for the covariance/Lyapunov drift.
For a fixed current covariance `P`, perturbing drift by `RA` and process-noise
covariance by `RQ` produces exactly the residual drift `RA P + P RAᵀ + RQ`.
There are no higher-order residual terms because the Lyapunov generator is
linear in `A` and `Q` when `P` is fixed. -/
theorem covarianceRHS_residual_exact
    (A0 RA P Q0 RQ : Matrix stateR stateR ℝ) :
    covarianceRHS (A0 + RA) P (Q0 + RQ) - covarianceRHS A0 P Q0 =
      covarianceRHS RA P RQ := by
  ext i j
  simp only [covarianceRHS, Matrix.add_apply, Matrix.sub_apply, Matrix.mul_apply,
    Matrix.transpose_apply, add_mul, mul_add, Finset.sum_add_distrib]
  ring


/-- If the baseline drift/noise and current covariance are exactly packet
respecting, then every off-packet covariance tangent is *exactly* the residual
Lyapunov drift generated by `RA` and `RQ`. -/
theorem covarianceRHS_offpacket_residual_exact
    (packet : stateR → packetR)
    (A0 RA P Q0 RQ : Matrix stateR stateR ℝ)
    (hA0 : BlockRespecting packet packet A0)
    (hP : BlockRespecting packet packet P)
    (hQ0 : BlockRespecting packet packet Q0)
    {i j : stateR} (hij : packet i ≠ packet j) :
    covarianceRHS (A0 + RA) P (Q0 + RQ) i j =
      covarianceRHS RA P RQ i j := by
  have hres := congrFun (congrFun
    (covarianceRHS_residual_exact A0 RA P Q0 RQ) i) j
  have hbase := covarianceRHS_offdiag_zero packet A0 P Q0 hA0 hP hQ0 hij
  simpa [hbase] using hres


/-- Pointwise quantitative certificate for covariance leakage generated by drift
and process-noise residuals.  The right side is completely explicit in the
residual entries and the current covariance. -/
theorem covarianceRHS_residual_entry_bound
    (RA P RQ : Matrix stateR stateR ℝ) (i j : stateR) :
    |covarianceRHS RA P RQ i j| ≤
      (∑ k, |RA i k| * |P k j|) +
      (∑ k, |P i k| * |RA j k|) + |RQ i j| := by
  rw [covarianceRHS_apply]
  calc
    |(∑ k, RA i k * P k j) + (∑ k, P i k * RA j k) + RQ i j| ≤
        |(∑ k, RA i k * P k j) + (∑ k, P i k * RA j k)| + |RQ i j| :=
      abs_add_le _ _
    _ ≤ (|(∑ k, RA i k * P k j)| + |(∑ k, P i k * RA j k)|) + |RQ i j| := by
      gcongr
      exact abs_add_le _ _
    _ ≤ ((∑ k, |RA i k * P k j|) + (∑ k, |P i k * RA j k|)) + |RQ i j| := by
      gcongr
      · exact Finset.abs_sum_le_sum_abs _ _
      · exact Finset.abs_sum_le_sum_abs _ _
    _ = (∑ k, |RA i k| * |P k j|) +
        (∑ k, |P i k| * |RA j k|) + |RQ i j| := by
      simp only [abs_mul]


/-- When the current covariance is packet respecting, each residual drift sum
localizes to the packet that can actually transmit covariance to the chosen
entry. -/
theorem covarianceRHS_residual_packet_expansion
    [DecidableEq packetR]
    (packet : stateR → packetR) (RA P RQ : Matrix stateR stateR ℝ)
    (hP : BlockRespecting packet packet P) (i j : stateR) :
    covarianceRHS RA P RQ i j =
      (∑ k ∈ (Finset.univ.filter (fun k => packet k = packet j)), RA i k * P k j) +
      (∑ k ∈ (Finset.univ.filter (fun k => packet k = packet i)), P i k * RA j k) +
      RQ i j := by
  classical
  rw [covarianceRHS_apply]
  have h1 : (∑ k, RA i k * P k j) =
      ∑ k ∈ (Finset.univ.filter (fun k => packet k = packet j)), RA i k * P k j := by
    symm
    rw [Finset.sum_filter]
    apply Finset.sum_congr rfl
    intro k hk
    by_cases hkj : packet k = packet j
    · simp [hkj]
    · have hzero : P k j = 0 := hP k j hkj
      simp [hkj, hzero]
  have h2 : (∑ k, P i k * RA j k) =
      ∑ k ∈ (Finset.univ.filter (fun k => packet k = packet i)), P i k * RA j k := by
    symm
    rw [Finset.sum_filter]
    apply Finset.sum_congr rfl
    intro k hk
    by_cases hki : packet k = packet i
    · simp [hki]
    · have hik : packet i ≠ packet k := by
        intro h
        exact hki h.symm
      have hzero : P i k = 0 := hP i k hik
      simp [hki, hzero]
  rw [h1, h2]

/-- **Off-packet covariance leakage certificate.**
If the baseline stochastic drift/noise and the current covariance exactly
respect the packet decomposition, then instantaneous covariance generated
between two distinct packets is controlled solely by the named drift/noise
residuals, and only through covariance entries in the two incident packets. -/
theorem offpacket_covariance_leakage_certificate
    [DecidableEq packetR]
    (packet : stateR → packetR)
    (A0 RA P Q0 RQ : Matrix stateR stateR ℝ)
    (hA0 : BlockRespecting packet packet A0)
    (hP : BlockRespecting packet packet P)
    (hQ0 : BlockRespecting packet packet Q0)
    {i j : stateR} (hij : packet i ≠ packet j) :
    |covarianceRHS (A0 + RA) P (Q0 + RQ) i j| ≤
      (∑ k ∈ (Finset.univ.filter (fun k => packet k = packet j)), |RA i k| * |P k j|) +
      (∑ k ∈ (Finset.univ.filter (fun k => packet k = packet i)), |P i k| * |RA j k|) +
      |RQ i j| := by
  classical
  rw [covarianceRHS_offpacket_residual_exact packet A0 RA P Q0 RQ hA0 hP hQ0 hij]
  rw [covarianceRHS_residual_packet_expansion packet RA P RQ hP i j]
  calc
    |(∑ k ∈ Finset.univ.filter (fun k => packet k = packet j), RA i k * P k j) +
        (∑ k ∈ Finset.univ.filter (fun k => packet k = packet i), P i k * RA j k) + RQ i j| ≤
      |(∑ k ∈ Finset.univ.filter (fun k => packet k = packet j), RA i k * P k j) +
        (∑ k ∈ Finset.univ.filter (fun k => packet k = packet i), P i k * RA j k)| + |RQ i j| :=
      abs_add_le _ _
    _ ≤ (|(∑ k ∈ Finset.univ.filter (fun k => packet k = packet j), RA i k * P k j)| +
          |(∑ k ∈ Finset.univ.filter (fun k => packet k = packet i), P i k * RA j k)|) + |RQ i j| := by
      gcongr
      exact abs_add_le _ _
    _ ≤ ((∑ k ∈ Finset.univ.filter (fun k => packet k = packet j), |RA i k * P k j|) +
          (∑ k ∈ Finset.univ.filter (fun k => packet k = packet i), |P i k * RA j k|)) + |RQ i j| := by
      gcongr
      · exact Finset.abs_sum_le_sum_abs _ _
      · exact Finset.abs_sum_le_sum_abs _ _
    _ = (∑ k ∈ Finset.univ.filter (fun k => packet k = packet j), |RA i k| * |P k j|) +
        (∑ k ∈ Finset.univ.filter (fun k => packet k = packet i), |P i k| * |RA j k|) + |RQ i j| := by
      simp only [abs_mul]


/-- The explicit instantaneous off-packet leakage budget associated with drift
residual `RA`, current covariance `P`, and process-noise residual `RQ`. -/
def offpacketCovarianceLeakageBudget
    [DecidableEq packetR]
    (packet : stateR → packetR) (RA P RQ : Matrix stateR stateR ℝ)
    (i j : stateR) : ℝ :=
  (∑ k ∈ (Finset.univ.filter (fun k => packet k = packet j)), |RA i k| * |P k j|) +
  (∑ k ∈ (Finset.univ.filter (fun k => packet k = packet i)), |P i k| * |RA j k|) +
  |RQ i j|


/-- Exact covariance-error decomposition around an exactly modelled baseline.
If `D = P - P0`, the baseline Lyapunov operator propagates `D`, while drift and
process-noise misspecification enter only through the named residual forcing. -/
theorem covarianceRHS_error_decomposition
    (A0 RA P P0 Q0 RQ : Matrix stateR stateR ℝ) :
    covarianceRHS (A0 + RA) P (Q0 + RQ) - covarianceRHS A0 P0 Q0 =
      covarianceRHS A0 (P - P0) 0 + covarianceRHS RA P RQ := by
  ext i j
  simp only [covarianceRHS, Matrix.add_apply, Matrix.sub_apply, Matrix.zero_apply,
    Matrix.mul_apply, Matrix.transpose_apply, add_mul, mul_add, sub_mul, mul_sub,
    Finset.sum_add_distrib]
  ring

/-- Supplied covariance moment equations inherit the exact error dynamics. -/
theorem covariance_error_dynamics
    (A0 RA P P0 Q0 RQ Pdot P0dot : Matrix stateR stateR ℝ)
    (hActual : Pdot = covarianceRHS (A0 + RA) P (Q0 + RQ))
    (hBase : P0dot = covarianceRHS A0 P0 Q0) :
    Pdot - P0dot =
      covarianceRHS A0 (P - P0) 0 + covarianceRHS RA P RQ := by
  rw [hActual, hBase]
  exact covarianceRHS_error_decomposition A0 RA P P0 Q0 RQ

omit [Fintype stateR] in
/-- Off-packet covariance is exactly the covariance error whenever the baseline
covariance is packet respecting. -/
theorem offpacket_covariance_eq_error
    (packet : stateR → packetR)
    (P P0 : Matrix stateR stateR ℝ)
    (hP0 : BlockRespecting packet packet P0)
    {i j : stateR} (hij : packet i ≠ packet j) :
    P i j = (P - P0) i j := by
  have hz : P0 i j = 0 := hP0 i j hij
  simp [hz]

/-- **Corrected stochastic packet-leakage theorem.**
For a packet-respecting baseline covariance `P0`, the cross-packet covariance
error evolves as the sum of (i) baseline propagation of already-created error
and (ii) explicit residual forcing from drift/noise misspecification.
This is the nontrivial replacement for the discarded finite-horizon statement. -/
theorem offpacket_covariance_error_dynamics
    (packet : stateR → packetR)
    (A0 RA P P0 Q0 RQ Pdot P0dot : Matrix stateR stateR ℝ)
    (hP0 : BlockRespecting packet packet P0)
    (hActual : Pdot = covarianceRHS (A0 + RA) P (Q0 + RQ))
    (hBase : P0dot = covarianceRHS A0 P0 Q0)
    {i j : stateR} (hij : packet i ≠ packet j) :
    (Pdot - P0dot) i j =
      (covarianceRHS A0 (P - P0) 0 + covarianceRHS RA P RQ) i j ∧
    P i j = (P - P0) i j := by
  constructor
  · exact congrFun (congrFun
      (covariance_error_dynamics A0 RA P P0 Q0 RQ Pdot P0dot hActual hBase) i) j
  · exact offpacket_covariance_eq_error packet P P0 hP0 hij


/-! ### Operator-norm covariance residual bound -/

section OperatorCovarianceResidual

variable {B : Type*} [NormedRing B] [StarRing B] [NormedStarGroup B]

/-- Lyapunov/covariance drift in a normed star algebra. -/
def covarianceOperatorRHS (A P Q : B) : B :=
  A * P + P * star A + Q

omit [NormedStarGroup B] in
/-- Exact operator-level covariance-error decomposition. -/
theorem covarianceOperator_error_decomposition
    (A0 RA P P0 Q0 RQ : B) :
    covarianceOperatorRHS (A0 + RA) P (Q0 + RQ) -
      covarianceOperatorRHS A0 P0 Q0 =
    covarianceOperatorRHS A0 (P - P0) 0 +
      covarianceOperatorRHS RA P RQ := by
  simp only [covarianceOperatorRHS, star_add, add_mul, mul_add, sub_mul, mul_sub,
    add_zero]
  noncomm_ring

/-- Universal norm estimate for a Lyapunov drift in a normed star algebra. -/
theorem covarianceOperatorRHS_norm_bound
    (A P Q : B) :
    ‖covarianceOperatorRHS A P Q‖ ≤ 2 * ‖A‖ * ‖P‖ + ‖Q‖ := by
  unfold covarianceOperatorRHS
  calc
    ‖A * P + P * star A + Q‖ ≤ ‖A * P + P * star A‖ + ‖Q‖ := norm_add_le _ _
    _ ≤ (‖A * P‖ + ‖P * star A‖) + ‖Q‖ := by
      gcongr
      exact norm_add_le _ _
    _ ≤ (‖A‖ * ‖P‖ + ‖P‖ * ‖star A‖) + ‖Q‖ := by
      gcongr
      · exact norm_mul_le _ _
      · exact norm_mul_le _ _
    _ = 2 * ‖A‖ * ‖P‖ + ‖Q‖ := by
      rw [norm_star]
      ring

/-- **Stochastic covariance residual stability inequality.**
The covariance-model error is bounded by a baseline propagation term plus the
fresh drift/noise residual forcing.  In particular, if `D = P-P0`, the first
term is linear in the already accumulated error and the second is linear in the
model residuals. -/
theorem covarianceOperator_error_norm_bound
    (A0 RA P P0 Q0 RQ : B) :
    ‖covarianceOperatorRHS (A0 + RA) P (Q0 + RQ) -
        covarianceOperatorRHS A0 P0 Q0‖ ≤
      2 * ‖A0‖ * ‖P - P0‖ + (2 * ‖RA‖ * ‖P‖ + ‖RQ‖) := by
  rw [covarianceOperator_error_decomposition]
  calc
    ‖covarianceOperatorRHS A0 (P - P0) 0 + covarianceOperatorRHS RA P RQ‖ ≤
        ‖covarianceOperatorRHS A0 (P - P0) 0‖ +
          ‖covarianceOperatorRHS RA P RQ‖ := norm_add_le _ _
    _ ≤ (2 * ‖A0‖ * ‖P - P0‖ + ‖(0 : B)‖) +
          (2 * ‖RA‖ * ‖P‖ + ‖RQ‖) := by
      gcongr
      · exact covarianceOperatorRHS_norm_bound A0 (P - P0) 0
      · exact covarianceOperatorRHS_norm_bound RA P RQ
    _ = 2 * ‖A0‖ * ‖P - P0‖ + (2 * ‖RA‖ * ‖P‖ + ‖RQ‖) := by
      simp

end OperatorCovarianceResidual

end CovarianceResidualCertificate

end Komorebi.UnifiedInference
