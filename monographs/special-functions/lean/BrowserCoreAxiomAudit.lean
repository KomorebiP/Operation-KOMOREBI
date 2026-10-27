import Mathlib.LinearAlgebra.Span.Basic
import Mathlib.Data.Matrix.Mul
import Mathlib.Algebra.BigOperators.Pi
import Mathlib.Analysis.Complex.Exponential
import Mathlib.Tactic.Ring

/-!
# Komorebi Projector Calculus — browser-safe formal core v1.2.2

This file is intentionally conservative.  It contains the foundational theorem
tranche only.  The larger source-claim ledger is included in the companion
`..._Full_Fixed.lean` file as data, not as theorem assumptions.
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 4000000
set_option autoImplicit false

namespace Komorebi

/-! ## Proof-status vocabulary -/

inductive ClaimKind where
  | definitionClaim
  | theoremClaim
  | propositionClaim
  | lemmaClaim
  | corollaryClaim
  | exampleClaim
  | remarkClaim
  | algorithmClaim
  | numericalCertificate
  | classicalInput
  | conjecture
  | boundary
  deriving Repr, DecidableEq, BEq, Inhabited

inductive FormalizationStatus where
  | kernelChecked
  | proofTermPresent
  | partialFormalization
  | encodedDefinition
  | queued
  | blockedByLibrary
  | numericalOnly
  | conjectural
  | externalInput
  | contextOnly
  | boundaryOnly
  deriving Repr, DecidableEq, BEq, Inhabited

structure ClaimRecord where
  id : String
  corpus : String
  volume : String
  source : String
  ordinal : Nat
  title : String
  heading : String
  statement : String
  kind : ClaimKind
  status : FormalizationStatus
  sourceStatus : String := ""
  phase : String := ""
  targetNamespace : String := ""
  difficulty : String := ""
  notes : String := ""
  deriving Repr, Inhabited

def ClaimRecord.dependencySafe (claim : ClaimRecord) : Bool :=
  claim.status == .kernelChecked

def ClaimRecord.isOpenOrBoundary (claim : ClaimRecord) : Bool :=
  claim.kind == .conjecture || claim.kind == .boundary

/-! ## A browser-safe operator grammar -/

namespace Seed

universe u v

inductive OperatorExpr (Atom : Type u) where
  | id
  | atom (f : Atom)
  | comp (f g : OperatorExpr Atom)
  deriving Repr

namespace OperatorExpr

variable {Atom : Type u} {X : Type v}

def eval (interpret : Atom → X → X) : OperatorExpr Atom → X → X
  | .id => fun x => x
  | .atom f => interpret f
  | .comp f g => fun x => eval interpret g (eval interpret f x)

@[simp] theorem eval_id (interpret : Atom → X → X) (x : X) :
    eval interpret .id x = x := rfl

@[simp] theorem eval_atom (interpret : Atom → X → X) (f : Atom) (x : X) :
    eval interpret (.atom f) x = interpret f x := rfl

@[simp] theorem eval_comp
    (interpret : Atom → X → X) (f g : OperatorExpr Atom) (x : X) :
    eval interpret (.comp f g) x = eval interpret g (eval interpret f x) := rfl

end OperatorExpr

structure OperatorRelation (Atom : Type u) where
  lhs : OperatorExpr Atom
  rhs : OperatorExpr Atom

namespace OperatorRelation

variable {Atom : Type u} {X : Type v}

def Satisfied (interpret : Atom → X → X) (r : OperatorRelation Atom) : Prop :=
  ∀ x, OperatorExpr.eval interpret r.lhs x = OperatorExpr.eval interpret r.rhs x

@[simp] theorem satisfied_refl
    (interpret : Atom → X → X) (f : OperatorExpr Atom) :
    Satisfied interpret ⟨f, f⟩ := by
  intro x
  rfl

theorem satisfied_symm
    (interpret : Atom → X → X) {r : OperatorRelation Atom}
    (h : Satisfied interpret r) :
    Satisfied interpret ⟨r.rhs, r.lhs⟩ := by
  intro x
  exact (h x).symm

theorem satisfied_trans
    (interpret : Atom → X → X) {f g h : OperatorExpr Atom}
    (hfg : Satisfied interpret ⟨f, g⟩)
    (hgh : Satisfied interpret ⟨g, h⟩) :
    Satisfied interpret ⟨f, h⟩ := by
  intro x
  exact (hfg x).trans (hgh x)

theorem satisfied_postcomp
    (interpret : Atom → X → X) {r : OperatorRelation Atom}
    (h : Satisfied interpret r) (g : OperatorExpr Atom) :
    Satisfied interpret ⟨.comp r.lhs g, .comp r.rhs g⟩ := by
  intro x
  simp only [OperatorExpr.eval_comp]
  rw [h x]

end OperatorRelation

universe w

variable {R : Type u} {M : Type v}
variable [Semiring R] [AddCommMonoid M] [Module R M]

def algebraicHull (S : Set M) : Submodule R M :=
  Submodule.span R S

@[simp] theorem seed_subset_hull (S : Set M) :
    S ⊆ algebraicHull (R := R) S :=
  Submodule.subset_span

theorem hull_le {S : Set M} {P : Submodule R M} (h : S ⊆ P) :
    algebraicHull (R := R) S ≤ P :=
  Submodule.span_le.2 h

@[simp] theorem hull_empty :
    algebraicHull (R := R) (∅ : Set M) = ⊥ := by
  simp [algebraicHull]

@[simp] theorem hull_univ :
    algebraicHull (R := R) (Set.univ : Set M) = ⊤ := by
  apply le_antisymm le_top
  intro x hx
  exact Submodule.subset_span (Set.mem_univ x)

end Seed

/-! ## Complete finite projector families -/

namespace Foundation

universe u v w x y

structure LinearProjectorFamily
    (R : Type u) (M : Type v) (ι : Type w)
    [Semiring R] [AddCommMonoid M] [Module R M] [Fintype ι] where
  proj : ι → Module.End R M
  idempotent : ∀ i x, proj i (proj i x) = proj i x
  orthogonal : ∀ {i j}, i ≠ j → ∀ x, proj i (proj j x) = 0
  complete : ∀ x, (∑ i, proj i x) = x

namespace LinearProjectorFamily

variable {R : Type u} {M : Type v} {ι : Type w}
variable [Semiring R] [AddCommMonoid M] [Module R M] [Fintype ι]


def analyze (P : LinearProjectorFamily R M ι) (x : M) : ι → M :=
  fun i => P.proj i x


def synthesize (_P : LinearProjectorFamily R M ι) (packets : ι → M) : M :=
  ∑ i, packets i

@[simp] theorem synthesize_analyze
    (P : LinearProjectorFamily R M ι) (x : M) :
    P.synthesize (P.analyze x) = x := by
  simpa [synthesize, analyze] using P.complete x

theorem eq_of_projectors_eq
    (P : LinearProjectorFamily R M ι) {x y : M}
    (h : ∀ i, P.proj i x = P.proj i y) : x = y := by
  calc
    x = ∑ i, P.proj i x := (P.complete x).symm
    _ = ∑ i, P.proj i y := by
      apply Finset.sum_congr rfl
      intro i hi
      exact h i
    _ = y := P.complete y

end LinearProjectorFamily

variable {R : Type u} {M : Type v} {N : Type w} {L : Type x}
variable {ι : Type y} {κ : Type*} {τ : Type*}
variable [Semiring R]
variable [AddCommMonoid M] [Module R M]
variable [AddCommMonoid N] [Module R N]
variable [AddCommMonoid L] [Module R L]
variable [Fintype ι] [Fintype κ] [Fintype τ]


def transferBlock
    (P : LinearProjectorFamily R M ι)
    (Q : LinearProjectorFamily R N κ)
    (T : M →ₗ[R] N) (j : κ) (i : ι) : M →ₗ[R] N :=
  (Q.proj j).comp (T.comp (P.proj i))


theorem transferBlock_reconstruction
    (P : LinearProjectorFamily R M ι)
    (Q : LinearProjectorFamily R N κ)
    (T : M →ₗ[R] N) (x : M) :
    (∑ j, ∑ i, Q.proj j (T (P.proj i x))) = T x := by
  calc
    (∑ j, ∑ i, Q.proj j (T (P.proj i x))) =
        ∑ j, Q.proj j (T (∑ i, P.proj i x)) := by
          apply Finset.sum_congr rfl
          intro j hj
          simp only [map_sum]
    _ = ∑ j, Q.proj j (T x) := by rw [P.complete x]
    _ = T x := Q.complete (T x)


theorem transferBlock_comp
    (P : LinearProjectorFamily R M ι)
    (Q : LinearProjectorFamily R N κ)
    (S : LinearProjectorFamily R L τ)
    (T : M →ₗ[R] N) (U : N →ₗ[R] L)
    (k : τ) (i : ι) (x : M) :
    S.proj k (U (T (P.proj i x))) =
      ∑ j, S.proj k (U (Q.proj j (T (P.proj i x)))) := by
  have h := (Q.complete (T (P.proj i x))).symm
  calc
    S.proj k (U (T (P.proj i x))) =
        S.proj k (U (∑ j, Q.proj j (T (P.proj i x)))) :=
          congrArg (fun y => S.proj k (U y)) h
    _ = ∑ j, S.proj k (U (Q.proj j (T (P.proj i x)))) := by
          simp only [map_sum]

end Foundation

/-! ## Fibre and coordinate packets -/

namespace Packet

universe u v w

variable {α : Type u} {β : Type v} {M : Type w}


def fibreProj [DecidableEq β] [Zero M]
    (address : α → β) (b : β) (x : α → M) : α → M :=
  fun a => if address a = b then x a else 0

@[simp] theorem fibreProj_apply_same
    [DecidableEq β] [Zero M]
    (address : α → β) (b : β) (x : α → M) (a : α)
    (h : address a = b) :
    fibreProj address b x a = x a := by
  simp [fibreProj, h]

@[simp] theorem fibreProj_apply_ne
    [DecidableEq β] [Zero M]
    (address : α → β) (b : β) (x : α → M) (a : α)
    (h : address a ≠ b) :
    fibreProj address b x a = 0 := by
  simp [fibreProj, h]


theorem fibreProj_idempotent
    [DecidableEq β] [Zero M]
    (address : α → β) (b : β) (x : α → M) :
    fibreProj address b (fibreProj address b x) = fibreProj address b x := by
  funext a
  by_cases h : address a = b <;> simp [fibreProj, h]


theorem fibreProj_orthogonal
    [DecidableEq β] [Zero M]
    (address : α → β) {b c : β} (hbc : b ≠ c) (x : α → M) :
    fibreProj address b (fibreProj address c x) = 0 := by
  funext a
  by_cases h : address a = b <;> simp [fibreProj, h, hbc]


theorem fibreProj_reconstruction
    [DecidableEq β] [Fintype β] [AddCommMonoid M]
    (address : α → β) (x : α → M) :
    (∑ b, fibreProj address b x) = x := by
  funext a
  simp [fibreProj]


def coordinateProj {ι : Type u} [DecidableEq ι] [Zero M]
    (i : ι) (x : ι → M) : ι → M :=
  fun j => if j = i then x j else 0


theorem coordinateProj_reconstruction
    {ι : Type u} [DecidableEq ι] [Fintype ι] [AddCommMonoid M]
    (x : ι → M) :
    (∑ i, coordinateProj i x) = x := by
  funext j
  simp [coordinateProj]

end Packet

/-! ## Block and factor-first operators -/

namespace Operator

universe u v w

variable {ι : Type u} {κ : Type v} {M : Type w}


def blockApply
    [Fintype κ] [AddCommMonoid M]
    (T : ι → κ → M →+ M) (x : κ → M) : ι → M :=
  fun i => ∑ j, T i j (x j)

@[simp] theorem blockApply_zero
    [Fintype κ] [AddCommMonoid M]
    (T : ι → κ → M →+ M) :
    blockApply T (0 : κ → M) = 0 := by
  funext i
  simp [blockApply]

variable {ρ : Type*} {R : Type*}


def lowRankApply
    [Fintype κ] [Fintype ρ] [CommSemiring R]
    (U : ι → ρ → R) (V : κ → ρ → R) (x : κ → R) : ι → R :=
  fun i => ∑ r, U i r * (∑ j, V j r * x j)

@[simp] theorem lowRankApply_zero_vector
    [Fintype κ] [Fintype ρ] [CommSemiring R]
    (U : ι → ρ → R) (V : κ → ρ → R) :
    lowRankApply U V (0 : κ → R) = 0 := by
  funext i
  simp [lowRankApply]

end Operator

/-! ## Relation-supported matrix algebra -/

namespace Algebra

universe u v


def MatrixSupported {ι : Type u} {A : Type v} [Zero A]
    (rel : ι → ι → Prop) (M : Matrix ι ι A) : Prop :=
  ∀ i j, ¬ rel i j → M i j = 0


theorem matrixSupported_zero
    {ι : Type u} {A : Type v} [Zero A]
    (rel : ι → ι → Prop) :
    MatrixSupported rel (0 : Matrix ι ι A) := by
  intro i j h
  rfl


theorem MatrixSupported.add
    {ι : Type u} {A : Type v} [AddMonoid A]
    {rel : ι → ι → Prop} {M N : Matrix ι ι A}
    (hM : MatrixSupported rel M) (hN : MatrixSupported rel N) :
    MatrixSupported rel (M + N) := by
  intro i j h
  simp [hM i j h, hN i j h]


theorem MatrixSupported.neg
    {ι : Type u} {A : Type v} [AddGroup A]
    {rel : ι → ι → Prop} {M : Matrix ι ι A}
    (hM : MatrixSupported rel M) :
    MatrixSupported rel (-M) := by
  intro i j h
  simp [hM i j h]


theorem MatrixSupported.mul
    {ι : Type u} {A : Type v}
    [Fintype ι] [DecidableEq ι] [Semiring A]
    {rel : ι → ι → Prop}
    (htrans : ∀ i j k, rel i j → rel j k → rel i k)
    {M N : Matrix ι ι A}
    (hM : MatrixSupported rel M) (hN : MatrixSupported rel N) :
    MatrixSupported rel (M * N) := by
  intro i j hij
  rw [Matrix.mul_apply]
  apply Finset.sum_eq_zero
  intro k hk
  by_cases hik : rel i k
  · by_cases hkj : rel k j
    · exact (hij (htrans i k j hik hkj)).elim
    · simp [hN k j hkj]
  · simp [hM i k hik]


def IsLowerTriangular {ι : Type u} {A : Type v}
    [Preorder ι] [Zero A] (M : Matrix ι ι A) : Prop :=
  ∀ i j, i < j → M i j = 0


def IsUpperTriangular {ι : Type u} {A : Type v}
    [Preorder ι] [Zero A] (M : Matrix ι ι A) : Prop :=
  ∀ i j, j < i → M i j = 0


theorem IsLowerTriangular.add
    {ι : Type u} {A : Type v} [Preorder ι] [AddMonoid A]
    {M N : Matrix ι ι A}
    (hM : IsLowerTriangular M) (hN : IsLowerTriangular N) :
    IsLowerTriangular (M + N) := by
  intro i j hij
  simp [hM i j hij, hN i j hij]


theorem IsUpperTriangular.add
    {ι : Type u} {A : Type v} [Preorder ι] [AddMonoid A]
    {M N : Matrix ι ι A}
    (hM : IsUpperTriangular M) (hN : IsUpperTriangular N) :
    IsUpperTriangular (M + N) := by
  intro i j hij
  simp [hM i j hij, hN i j hij]

end Algebra

/-! ## Finite-difference and weighted-shift calculus -/

namespace FiniteDifference

universe u

variable {R : Type u}


def forwardDiff [Ring R] (f : ℕ → R) (n : ℕ) : R :=
  f (n + 1) - f n


def iteratedDiff [Ring R] : ℕ → (ℕ → R) → (ℕ → R)
  | 0, f => f
  | k + 1, f => forwardDiff (iteratedDiff k f)


theorem forwardDiff_add [CommRing R]
    (f g : ℕ → R) (n : ℕ) :
    forwardDiff (fun j => f j + g j) n = forwardDiff f n + forwardDiff g n := by
  simp [forwardDiff]
  ring


theorem forwardDiff_neg [CommRing R]
    (f : ℕ → R) (n : ℕ) :
    forwardDiff (fun j => -f j) n = -forwardDiff f n := by
  simp [forwardDiff]
  ring


theorem iteratedDiff_two [CommRing R]
    (f : ℕ → R) (n : ℕ) :
    iteratedDiff 2 f n = f (n + 2) - 2 * f (n + 1) + f n := by
  simp [iteratedDiff, forwardDiff]
  ring


theorem iteratedDiff_three [CommRing R]
    (f : ℕ → R) (n : ℕ) :
    iteratedDiff 3 f n =
      f (n + 3) - 3 * f (n + 2) + 3 * f (n + 1) - f n := by
  simp [iteratedDiff, forwardDiff]
  ring


def weightedDiff [Ring R] (q : R) (f : ℕ → R) (n : ℕ) : R :=
  f n - q * f (n + 1)


def iteratedWeightedDiff [Ring R] (q : R) : ℕ → (ℕ → R) → (ℕ → R)
  | 0, f => f
  | k + 1, f => weightedDiff q (iteratedWeightedDiff q k f)


theorem iteratedWeightedDiff_geometric [CommRing R]
    (q r : R) (k n : ℕ) :
    iteratedWeightedDiff q k (fun j => r ^ j) n =
      (1 - q * r) ^ k * r ^ n := by
  induction k generalizing n with
  | zero => simp [iteratedWeightedDiff]
  | succ k ih =>
      simp [iteratedWeightedDiff, weightedDiff, ih, pow_succ]
      ring

end FiniteDifference

/-! ## Polyphase coefficient sections -/

namespace Polyphase

universe u

variable {A : Type u}


def coeffSection (m r : ℕ) (f : ℕ → A) (n : ℕ) : A :=
  f (m * n + r)

@[simp] theorem coeffSection_one_zero (f : ℕ → A) :
    coeffSection 1 0 f = f := by
  funext n
  simp [coeffSection]


theorem coeffSection_comp
    (l s m r : ℕ) (f : ℕ → A) (n : ℕ) :
    coeffSection m r (coeffSection l s f) n =
      coeffSection (l * m) (l * r + s) f n := by
  simp [coeffSection, Nat.mul_add, Nat.mul_assoc, Nat.add_assoc]

end Polyphase

/-! ## Finite diagonal quantum coordinates -/

namespace Quantum

universe u


def diagonalApply {ι : Type u} {R : Type*} [Mul R]
    (diagonal : ι → R) (x : ι → R) : ι → R :=
  fun i => diagonal i * x i

@[simp] theorem diagonalApply_one
    {ι : Type u} {R : Type*} [Monoid R] (x : ι → R) :
    diagonalApply (fun _ => 1) x = x := by
  funext i
  simp [diagonalApply]

noncomputable def logPhase {ι : Type u}
    (energy : ι → ℝ) (t : ℝ) : ι → ℂ :=
  fun i => Complex.exp (-Complex.I * ((energy i * t : ℝ) : ℂ))

@[simp] theorem logPhase_zero {ι : Type u} (energy : ι → ℝ) :
    logPhase energy 0 = fun _ => 1 := by
  funext i
  simp [logPhase]

noncomputable def finiteAmplitude {ι : Type u} [Fintype ι]
    (weight sign : ι → ℂ) (energy : ι → ℝ) (t : ℝ) : ℂ :=
  ∑ i, weight i * sign i * logPhase energy t i

@[simp] theorem finiteAmplitude_zero {ι : Type u} [Fintype ι]
    (weight sign : ι → ℂ) (energy : ι → ℝ) :
    finiteAmplitude weight sign energy 0 = ∑ i, weight i * sign i := by
  simp [finiteAmplitude, logPhase]

end Quantum

end Komorebi

/-! ## Browser smoke checks -/

#check Komorebi.Foundation.LinearProjectorFamily.synthesize_analyze
#check Komorebi.Foundation.transferBlock_reconstruction
#check Komorebi.Foundation.transferBlock_comp
#check Komorebi.Packet.fibreProj_reconstruction
#check Komorebi.Algebra.MatrixSupported.mul
#check Komorebi.FiniteDifference.iteratedWeightedDiff_geometric
#check Komorebi.Polyphase.coeffSection_comp
#check Komorebi.Quantum.finiteAmplitude_zero

#eval "Komorebi Projector Calculus browser-safe core v1.2.2 loaded"

/- Fresh axiom audit of the named finite-core theorems. -/
#print axioms Komorebi.Seed.OperatorExpr.eval_id
#print axioms Komorebi.Seed.OperatorExpr.eval_atom
#print axioms Komorebi.Seed.OperatorExpr.eval_comp
#print axioms Komorebi.Seed.OperatorRelation.satisfied_refl
#print axioms Komorebi.Seed.OperatorRelation.satisfied_symm
#print axioms Komorebi.Seed.OperatorRelation.satisfied_trans
#print axioms Komorebi.Seed.OperatorRelation.satisfied_postcomp
#print axioms Komorebi.Seed.seed_subset_hull
#print axioms Komorebi.Seed.hull_le
#print axioms Komorebi.Seed.hull_empty
#print axioms Komorebi.Seed.hull_univ
#print axioms Komorebi.Foundation.LinearProjectorFamily.synthesize_analyze
#print axioms Komorebi.Foundation.LinearProjectorFamily.eq_of_projectors_eq
#print axioms Komorebi.Foundation.transferBlock_reconstruction
#print axioms Komorebi.Foundation.transferBlock_comp
#print axioms Komorebi.Packet.fibreProj_apply_same
#print axioms Komorebi.Packet.fibreProj_apply_ne
#print axioms Komorebi.Packet.fibreProj_idempotent
#print axioms Komorebi.Packet.fibreProj_orthogonal
#print axioms Komorebi.Packet.fibreProj_reconstruction
#print axioms Komorebi.Packet.coordinateProj_reconstruction
#print axioms Komorebi.Operator.blockApply_zero
#print axioms Komorebi.Operator.lowRankApply_zero_vector
#print axioms Komorebi.Algebra.matrixSupported_zero
#print axioms Komorebi.Algebra.MatrixSupported.add
#print axioms Komorebi.Algebra.MatrixSupported.neg
#print axioms Komorebi.Algebra.MatrixSupported.mul
#print axioms Komorebi.Algebra.IsLowerTriangular.add
#print axioms Komorebi.Algebra.IsUpperTriangular.add
#print axioms Komorebi.FiniteDifference.forwardDiff_add
#print axioms Komorebi.FiniteDifference.forwardDiff_neg
#print axioms Komorebi.FiniteDifference.iteratedDiff_two
#print axioms Komorebi.FiniteDifference.iteratedDiff_three
#print axioms Komorebi.FiniteDifference.iteratedWeightedDiff_geometric
#print axioms Komorebi.Polyphase.coeffSection_one_zero
#print axioms Komorebi.Polyphase.coeffSection_comp
#print axioms Komorebi.Quantum.diagonalApply_one
#print axioms Komorebi.Quantum.logPhase_zero
#print axioms Komorebi.Quantum.finiteAmplitude_zero
