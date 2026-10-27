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
public import Mathlib.MeasureTheory.Integral.IntervalIntegral.FundThmCalculus
public import Mathlib.Analysis.Calculus.Deriv.Mul

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

end KalmanBlockClosure


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

end Komorebi.UnifiedInference







#print axioms Komorebi.UnifiedInference.bayesPacketUpdate_sequential
#print axioms Komorebi.UnifiedInference.posteriorFine_over_packet
#print axioms Komorebi.UnifiedInference.strongLumpable_iff_exists_intertwiner
#print axioms Komorebi.UnifiedInference.kalman_block_closure_of_twoSided_inverse
#print axioms Komorebi.UnifiedInference.packetMomentClosure
#print axioms Komorebi.UnifiedInference.continuousLinearMap_caputoFromDerivative
#print axioms Komorebi.UnifiedInference.ContinuousProjectorFamily.volterraMemory_packet_reconstruction
#print axioms Komorebi.UnifiedInference.operatorKernelConvolution_packet_path
#print axioms Komorebi.UnifiedInference.finiteExponentialKernelMemory_eq_sum_states
#print axioms Komorebi.UnifiedInference.exponentialMemoryState_hasDerivAt
