/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import KomorebiPaperIII.EdgeOperators

/-!
# Finite endpoint and heterogeneous path expansions

This module strengthens the finite scalar edge model with the endpoint block
carried by a composable word, its coefficient-level walk expansion, and the
corresponding reachability obstructions.  It also gives a finite heterogeneous
matrix-factor expansion: the factors may vary from step to step, while their
packet index type remains fixed.
-/

set_option autoImplicit false

namespace Komorebi.PaperIII.EdgeOperators

open scoped BigOperators Matrix

universe u v w

namespace PacketGraph

variable {V : Type u} {E : Type v} {R : Type w}

/-- Two scalar packet blocks with a matched intermediate packet collapse. -/
theorem packetMatrix_mul_packetMatrix
    [Fintype V] [DecidableEq V] [Semiring R]
    (source middle target : V) (leftCoefficient rightCoefficient : R) :
    packetMatrix middle target leftCoefficient *
        packetMatrix source middle rightCoefficient =
      packetMatrix source target (leftCoefficient * rightCoefficient) := by
  ext row column
  by_cases hrow : row = target
  · by_cases hcolumn : column = source
    · simp [packetMatrix, Matrix.mul_apply, hrow, hcolumn]
    · simp [packetMatrix, Matrix.mul_apply, hrow, hcolumn]
  · simp [packetMatrix, Matrix.mul_apply, hrow]

namespace EdgeSystem

variable (G : PacketGraph V E) (S : EdgeSystem G R)

/-- Coefficients multiplied in operator order, hence reverse execution order. -/
def reverseCoefficient [One R] [Mul R] : List E → R
  | [] => 1
  | e :: rest => reverseCoefficient rest * S.coefficient e

/-- The target of the final edge in the nonempty word `first :: rest`. -/
def terminalTarget (first : E) : List E → V
  | [] => G.target first
  | next :: rest => terminalTarget next rest

/-- A word, including the empty word, connects the specified endpoints. -/
def Connects (source target : V) : List E → Prop
  | [] => source = target
  | first :: rest =>
      source = G.source first ∧
        target = terminalTarget G first rest ∧
          Composable G (first :: rest)

/-- Endpoint connectivity is used only to filter finite sums in this module. -/
noncomputable instance instDecidableConnects
    (source target : V) (word : List E) : Decidable (Connects G source target word) :=
  Classical.propDecidable _

/--
A nonempty composable word is one endpoint-supported packet block.  Its scalar
is the reverse-order product dictated by right-to-left operator composition.
-/
theorem wordOp_eq_packetMatrix_of_composable
    [Fintype V] [DecidableEq V] [Semiring R]
    (first : E) (rest : List E) (h : Composable G (first :: rest)) :
    wordOp G S (first :: rest) =
      packetMatrix (G.source first) (terminalTarget G first rest)
        (reverseCoefficient G S (first :: rest)) := by
  induction rest generalizing first with
  | nil =>
      simp [wordOp, edgeOp, terminalTarget, reverseCoefficient]
  | cons next tail ih =>
      change G.target first = G.source next ∧
        Composable G (next :: tail) at h
      rcases h with ⟨hmatch, htail⟩
      change wordOp G S (next :: tail) * edgeOp G S first = _
      rw [ih next htail]
      simp only [terminalTarget, reverseCoefficient]
      unfold edgeOp
      rw [← hmatch]
      exact packetMatrix_mul_packetMatrix
        (G.source first) (G.target first) (terminalTarget G next tail)
        (reverseCoefficient G S (next :: tail)) (S.coefficient first)

/-- The endpoint entry of one word is its coefficient exactly when it connects. -/
theorem wordOp_apply_eq_if_connects
    [Fintype V] [DecidableEq V] [Semiring R]
    (word : List E) (source target : V) :
    wordOp G S word target source =
      if Connects G source target word then reverseCoefficient G S word else 0 := by
  cases word with
  | nil =>
      by_cases h : source = target
      · subst target
        simp [wordOp, Connects, reverseCoefficient]
      · have hreverse : target ≠ source := fun h' => h h'.symm
        simp [wordOp, Connects, h, hreverse]
  | cons first rest =>
      by_cases hwalk : Composable G (first :: rest)
      · rw [wordOp_eq_packetMatrix_of_composable G S first rest hwalk]
        simp [packetMatrix, Connects, hwalk, and_comm]
      · rw [wordOp_eq_zero_of_not_composable G S (first :: rest) hwalk]
        simp [Connects, hwalk]

/-- The finite scalar sum over length-`n` walks with fixed endpoints. -/
noncomputable def endpointWalkCoefficientSum
    [Fintype E] [Semiring R]
    (n : ℕ) (source target : V) : R := by
  classical
  exact ∑ word : Fin n → E,
    if Connects G source target (List.ofFn word) then
      reverseCoefficient G S (List.ofFn word)
    else 0

/-- Every transfer-power entry is the coefficient sum over its endpoint walks. -/
theorem transferOp_pow_apply_eq_sum_walks
    [Fintype E] [Fintype V] [DecidableEq V] [Semiring R]
    (n : ℕ) (source target : V) :
    (transferOp G S ^ n) target source =
      endpointWalkCoefficientSum G S n source target := by
  classical
  rw [transferOp_pow_eq_explicitWordExpansion G S n]
  unfold explicitWordExpansion endpointWalkCoefficientSum tupleWordOp
  rw [Matrix.sum_apply]
  apply Finset.sum_congr rfl
  intro word _
  exact wordOp_apply_eq_if_connects G S (List.ofFn word) source target

/-- Absence of a fixed-length endpoint walk forces the corresponding entry to vanish. -/
theorem transferOp_pow_apply_eq_zero_of_no_walk
    [Fintype E] [Fintype V] [DecidableEq V] [Semiring R]
    (n : ℕ) (source target : V)
    (h : ∀ word : Fin n → E,
      ¬ Connects G source target (List.ofFn word)) :
    (transferOp G S ^ n) target source = 0 := by
  rw [transferOp_pow_apply_eq_sum_walks G S n source target]
  classical
  simp [endpointWalkCoefficientSum, h]

/-- Directed reachability, with the empty path witnessing reflexivity. -/
def Reachable (source target : V) : Prop :=
  ∃ word : List E, Connects G source target word

/-- An unreachable endpoint has zero coefficient in every finite transfer power. -/
theorem transferOp_pow_apply_eq_zero_of_not_reachable
    [Fintype E] [Fintype V] [DecidableEq V] [Semiring R]
    (n : ℕ) (source target : V) (h : ¬ Reachable G source target) :
    (transferOp G S ^ n) target source = 0 := by
  apply transferOp_pow_apply_eq_zero_of_no_walk G S n source target
  intro word hword
  exact h ⟨List.ofFn word, hword⟩

/--
If a seed is supported on vertices from which `target` is unreachable, every
finite transfer-power orbit vector has zero `target` coordinate.
-/
theorem transferOp_pow_mulVec_apply_eq_zero_of_unreachable_support
    [Fintype E] [Fintype V] [DecidableEq V] [Semiring R]
    (n : ℕ) (x : V → R) (support : Set V) (target : V)
    (hx : ∀ source, source ∉ support → x source = 0)
    (hunreachable : ∀ source, source ∈ support → ¬ Reachable G source target) :
    ((transferOp G S ^ n) *ᵥ x) target = 0 := by
  rw [Matrix.mulVec_apply_eq_sum]
  apply Finset.sum_eq_zero
  intro source _
  by_cases hsource : source ∈ support
  · rw [transferOp_pow_apply_eq_zero_of_not_reachable G S n source target
      (hunreachable source hsource)]
    simp
  · rw [hx source hsource]
    simp

end EdgeSystem
end PacketGraph

section Heterogeneous

variable {V : Type u} {R : Type w}

universe u0 u1 u2 u3

/-- The fully typed two-step expansion, allowing three different packet types. -/
theorem heterogeneousPacketPathExpansion_two
    {I0 : Type u0} {I1 : Type u1} {I2 : Type u2}
    [Fintype I1] [NonUnitalNonAssocSemiring R]
    (first : Matrix I1 I0 R) (second : Matrix I2 I1 R)
    (source : I0) (target : I2) :
    (second * first) target source =
      ∑ middle : I1, second target middle * first middle source := by
  rw [Matrix.mul_apply]

/-- The fully typed three-step expansion, allowing four different packet types. -/
theorem heterogeneousPacketPathExpansion_three
    {I0 : Type u0} {I1 : Type u1} {I2 : Type u2} {I3 : Type u3}
    [Fintype I1] [Fintype I2] [Semiring R]
    (first : Matrix I1 I0 R) (second : Matrix I2 I1 R)
    (third : Matrix I3 I2 R) (source : I0) (target : I3) :
    ((third * second) * first) target source =
      ∑ middle2 : I2, ∑ middle1 : I1,
        (third target middle2 * second middle2 middle1) * first middle1 source := by
  rw [Matrix.mul_apply]
  simp_rw [Matrix.mul_apply, Finset.sum_mul]
  rw [Finset.sum_comm]

/--
Compose a finite sequence of possibly different packet matrices in execution
order.  The head acts first and therefore appears on the right.
-/
def heterogeneousProduct
    [Fintype V] [DecidableEq V] [Semiring R] :
    List (Matrix V V R) → Matrix V V R
  | [] => 1
  | step :: rest => heterogeneousProduct rest * step

/--
The scalar path sum for a heterogeneous sequence of packet matrices.  Each
successive intermediate packet is summed independently.
-/
def heterogeneousPathSum
    [Fintype V] [DecidableEq V] [Semiring R] :
    List (Matrix V V R) → V → V → R
  | [], source, target => if target = source then 1 else 0
  | step :: rest, source, target =>
      ∑ middle : V, heterogeneousPathSum rest middle target * step middle source

/--
Finite heterogeneous packet-path expansion for a common finite packet index
type.  Unlike a matrix power, the factor at every step may be different.
-/
theorem heterogeneousPacketPathExpansion
    [Fintype V] [DecidableEq V] [Semiring R]
    (steps : List (Matrix V V R)) (source target : V) :
    heterogeneousProduct steps target source =
      heterogeneousPathSum steps source target := by
  induction steps generalizing source target with
  | nil =>
      by_cases h : source = target
      · subst target
        simp [heterogeneousProduct, heterogeneousPathSum]
      · have hreverse : target ≠ source := fun h' => h h'.symm
        simp [heterogeneousProduct, heterogeneousPathSum, hreverse]
  | cons step rest ih =>
      simp [heterogeneousProduct, heterogeneousPathSum, Matrix.mul_apply, ih]

/-- A matrix step together with its declared directed packet support. -/
structure SupportedStep
    [Zero R] where
  operator : Matrix V V R
  relation : V → V → Prop
  supported : ∀ source target, ¬ relation source target → operator target source = 0

/-- A path compatible with each declared support relation, including the empty path. -/
def SupportedPath
    [Zero R] :
    List (SupportedStep (V := V) (R := R)) → V → V → Prop
  | [], source, target => source = target
  | step :: rest, source, target =>
      ∃ middle, step.relation source middle ∧ SupportedPath rest middle target

/-- With no compatible declared packet path, the heterogeneous path sum is zero. -/
theorem heterogeneousPathSum_eq_zero_of_no_supportedPath
    [Fintype V] [DecidableEq V] [Semiring R]
    (steps : List (SupportedStep (V := V) (R := R))) (source target : V)
    (h : ¬ SupportedPath steps source target) :
    heterogeneousPathSum (steps.map SupportedStep.operator) source target = 0 := by
  induction steps generalizing source target with
  | nil =>
      have hreverse : target ≠ source := fun h' => h h'.symm
      simp [heterogeneousPathSum, hreverse]
  | cons step rest ih =>
      simp only [List.map_cons, heterogeneousPathSum]
      apply Finset.sum_eq_zero
      intro middle _
      by_cases hedge : step.relation source middle
      · have hrest : ¬ SupportedPath rest middle target := by
          intro hpath
          exact h ⟨middle, hedge, hpath⟩
        rw [ih middle target hrest]
        simp
      · rw [step.supported source middle hedge]
        simp

/-- The supported specialization of the heterogeneous packet-path expansion. -/
theorem supportedHeterogeneousPacketPathExpansion
    [Fintype V] [DecidableEq V] [Semiring R]
    (steps : List (SupportedStep (V := V) (R := R))) (source target : V) :
    heterogeneousProduct (steps.map SupportedStep.operator) target source =
      heterogeneousPathSum (steps.map SupportedStep.operator) source target :=
  heterogeneousPacketPathExpansion _ source target

/-- A heterogeneous supported product has zero endpoint entry without a compatible path. -/
theorem heterogeneousProduct_apply_eq_zero_of_no_supportedPath
    [Fintype V] [DecidableEq V] [Semiring R]
    (steps : List (SupportedStep (V := V) (R := R))) (source target : V)
    (h : ¬ SupportedPath steps source target) :
    heterogeneousProduct (steps.map SupportedStep.operator) target source = 0 := by
  rw [supportedHeterogeneousPacketPathExpansion steps source target]
  exact heterogeneousPathSum_eq_zero_of_no_supportedPath steps source target h

end Heterogeneous

end Komorebi.PaperIII.EdgeOperators
