/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import Mathlib.Data.Finset.Basic
import Mathlib.Logic.Function.Basic

/-!
# Nonlinear operation trees and obstruction packets

This file establishes a deliberately modest nonlinear foundation.  An
operation tree is syntax with arbitrary unary and binary semantics; no
linearity, differentiability, convergence, or closure theorem is assumed.
Lean proves that evaluation depends only on the inputs that occur in the tree.

The obstruction API is likewise local and fail-closed.  A nonzero residual at
one packet rules out one proposed global solution.  It does not, without added
hypotheses, prove that every candidate is obstructed or classify all solutions.
-/

set_option autoImplicit false

namespace Komorebi.PaperIII.NonlinearObstructions

universe u v w x y

/-! ## Nonlinear operation trees -/

/--
Finite syntax for constants, inputs, unary operations, and binary operations.
The operation labels carry no unadvertised algebraic laws.
-/
inductive OperationTree
    (Input : Type u) (Constant : Type v) (Unary : Type w) (Binary : Type x)
    where
  | input : Input → OperationTree Input Constant Unary Binary
  | constant : Constant → OperationTree Input Constant Unary Binary
  | unary : Unary → OperationTree Input Constant Unary Binary →
      OperationTree Input Constant Unary Binary
  | binary : Binary → OperationTree Input Constant Unary Binary →
      OperationTree Input Constant Unary Binary →
      OperationTree Input Constant Unary Binary

namespace OperationTree

variable {Input : Type u} {Constant : Type v} {Unary : Type w} {Binary : Type x}
variable {Value : Type y}

/-- Evaluate an operation tree under completely explicit operation semantics. -/
def eval
    (inputValue : Input → Value)
    (constantValue : Constant → Value)
    (unaryValue : Unary → Value → Value)
    (binaryValue : Binary → Value → Value → Value) :
    OperationTree Input Constant Unary Binary → Value
  | .input i => inputValue i
  | .constant c => constantValue c
  | .unary op child => unaryValue op (eval inputValue constantValue unaryValue binaryValue child)
  | .binary op left right =>
      binaryValue op
        (eval inputValue constantValue unaryValue binaryValue left)
        (eval inputValue constantValue unaryValue binaryValue right)

/-- The finite set of input packets actually read by a tree. -/
def inputs [DecidableEq Input] :
    OperationTree Input Constant Unary Binary → Finset Input
  | .input i => {i}
  | .constant _ => ∅
  | .unary _ child => inputs child
  | .binary _ left right => inputs left ∪ inputs right

/--
Locality theorem for arbitrary nonlinear semantics: agreement on all input
packets named by the syntax forces equal evaluation.
-/
theorem eval_congr_on_inputs [DecidableEq Input]
    (tree : OperationTree Input Constant Unary Binary)
    (first second : Input → Value)
    (constantValue : Constant → Value)
    (unaryValue : Unary → Value → Value)
    (binaryValue : Binary → Value → Value → Value)
    (hagree : ∀ i ∈ tree.inputs, first i = second i) :
    tree.eval first constantValue unaryValue binaryValue =
      tree.eval second constantValue unaryValue binaryValue := by
  induction tree with
  | input i =>
      exact hagree i (by simp [inputs])
  | constant c =>
      rfl
  | unary op child ih =>
      simp only [eval]
      congr 1
      exact ih fun i hi ↦ hagree i (by simpa [inputs] using hi)
  | binary op left right ihLeft ihRight =>
      simp only [eval]
      congr 1
      · exact ihLeft fun i hi ↦ hagree i (by simp [inputs, hi])
      · exact ihRight fun i hi ↦ hagree i (by simp [inputs, hi])

/-- A tree with no named input packets has environment-independent value. -/
theorem eval_eq_of_inputs_eq_empty [DecidableEq Input]
    (tree : OperationTree Input Constant Unary Binary)
    (first second : Input → Value)
    (constantValue : Constant → Value)
    (unaryValue : Unary → Value → Value)
    (binaryValue : Binary → Value → Value → Value)
    (hempty : tree.inputs = ∅) :
    tree.eval first constantValue unaryValue binaryValue =
      tree.eval second constantValue unaryValue binaryValue := by
  apply tree.eval_congr_on_inputs first second constantValue unaryValue binaryValue
  intro i hi
  rw [hempty] at hi
  simp at hi

end OperationTree

/-! ## Candidate-specific obstruction packets -/

section Obstructions

variable {Packet : Type u} {Candidate : Type v} {Residual : Type w}
variable [Zero Residual]

/-- A global solution is a candidate whose residual vanishes at every packet. -/
def IsSolution (residual : Candidate → Packet → Residual) (candidate : Candidate) : Prop :=
  ∀ packet, residual candidate packet = 0

/-- A local certificate naming one packet with a nonzero residual. -/
structure ObstructionPacket
    (residual : Candidate → Packet → Residual) (candidate : Candidate) where
  packet : Packet
  nonzero : residual candidate packet ≠ 0

/-- A certified obstruction packet rules out its specific candidate. -/
theorem ObstructionPacket.not_isSolution
    {residual : Candidate → Packet → Residual} {candidate : Candidate}
    (certificate : ObstructionPacket residual candidate) :
    ¬ IsSolution residual candidate := by
  intro hsolution
  exact certificate.nonzero (hsolution certificate.packet)

/-- A non-solution exposes an obstruction packet, classically and without finiteness. -/
theorem obstructionPacket_of_not_isSolution
    {residual : Candidate → Packet → Residual} {candidate : Candidate}
    (h : ¬ IsSolution residual candidate) :
    Nonempty (ObstructionPacket residual candidate) := by
  classical
  by_contra hnone
  apply h
  intro packet
  by_contra hnonzero
  exact hnone ⟨⟨packet, hnonzero⟩⟩

/-- Candidate failure is equivalent to the existence of a local obstruction packet. -/
theorem not_isSolution_iff_nonempty_obstructionPacket
    {residual : Candidate → Packet → Residual} {candidate : Candidate} :
    ¬ IsSolution residual candidate ↔
      Nonempty (ObstructionPacket residual candidate) := by
  constructor
  · exact obstructionPacket_of_not_isSolution
  · rintro ⟨certificate⟩
    exact certificate.not_isSolution

end Obstructions

end Komorebi.PaperIII.NonlinearObstructions
