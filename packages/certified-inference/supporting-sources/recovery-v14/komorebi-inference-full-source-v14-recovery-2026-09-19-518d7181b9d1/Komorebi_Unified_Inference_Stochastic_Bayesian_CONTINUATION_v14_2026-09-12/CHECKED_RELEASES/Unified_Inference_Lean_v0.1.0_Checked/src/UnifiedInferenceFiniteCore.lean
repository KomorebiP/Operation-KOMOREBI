module

public import Mathlib.Basic.Real.Basic
public import Mathlib.Data.Matrix.Mul
public import Mathlib.Tactic.FieldSimp
public import Mathlib.Tactic.Ring

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

end Komorebi.UnifiedInference

#print axioms Komorebi.UnifiedInference.bayesPacketUpdate_sequential
#print axioms Komorebi.UnifiedInference.posteriorPacketMass_factorization
#print axioms Komorebi.UnifiedInference.posteriorFine_over_packet
#print axioms Komorebi.UnifiedInference.intertwines_pow
#print axioms Komorebi.UnifiedInference.strongLumpable_iff_exists_intertwiner
#print axioms Komorebi.UnifiedInference.blockRespecting_of_twoSidedInverse
#print axioms Komorebi.UnifiedInference.kalman_block_closure_of_twoSided_inverse
