import Komorebi.Foundation.TowerObstruction
import Komorebi.Foundation.ResidualAudit

/-!
# Finite-support failure and the countable-support threshold

The finite-prefix difference maps are surjective, so their cokernels vanish. Their
commuting squares with the global difference give well-defined restriction maps on
cokernels. Thus a nonzero global obstruction is missed by every finite prefix.

The residual systems below are explicit test cases, not an admissibility definition
for a new set-theoretic axiom. The degree-1 invariant is the explicit cokernel model.
-/

namespace Komorebi.IntegerTower

/-- The actual finite-prefix operator has finitely many variables and equations. -/
def prefixDelta (N : ℕ) : (Fin (N + 1) → ℤ) →+ (Fin N → ℤ) where
  toFun a i := a i.castSucc - 3 * a i.succ
  map_zero' := by ext i; simp
  map_add' a b := by ext i; simp only [Pi.add_apply]; ring

/-- Backward substitution for an arbitrary inhomogeneous sequence. -/
def backward (b : Sequence) : ℕ → ℕ → ℤ
  | 0, _ => 0
  | k + 1, n => b n + 3 * backward b k (n + 1)

def finiteLift (b : Sequence) (N : ℕ) : Fin (N + 1) → ℤ :=
  fun i => backward b (N - i.val) i.val

theorem finiteLift_solves (b : Sequence) (N : ℕ) :
    prefixDelta N (finiteLift b N) = fun i => b i.val := by
  funext i
  change backward b (N - i.val) i.val -
    3 * backward b (N - (i.val + 1)) (i.val + 1) = b i.val
  have hsub : N - i.val = (N - (i.val + 1)) + 1 := by omega
  rw [hsub, backward]
  ring

/-- Every finite right-hand side is solvable, not only the constant one. -/
theorem prefixDelta_surjective (N : ℕ) : Function.Surjective (prefixDelta N) := by
  intro b
  let extension : Sequence := fun n => if h : n < N then b ⟨n, h⟩ else 0
  refine ⟨finiteLift extension N, ?_⟩
  rw [finiteLift_solves]
  funext i
  simp [extension, i.isLt]

abbrev PrefixObstructionGroup (N : ℕ) := (Fin N → ℤ) ⧸ (prefixDelta N).range

def prefixOnes (N : ℕ) : Fin N → ℤ := fun _ => 1

def prefixObstruction (N : ℕ) : PrefixObstructionGroup N :=
  QuotientAddGroup.mk (prefixOnes N)

/-- The entire finite-prefix cokernel vanishes. -/
theorem prefix_class_eq_zero (N : ℕ) (b : Fin N → ℤ) :
    QuotientAddGroup.mk b = (0 : PrefixObstructionGroup N) := by
  rw [QuotientAddGroup.eq_zero_iff]
  exact prefixDelta_surjective N b

theorem prefix_obstruction_eq_zero (N : ℕ) : prefixObstruction N = 0 :=
  prefix_class_eq_zero N (prefixOnes N)

/-- Restriction of output coordinates. -/
def restrictRows (N : ℕ) : Sequence →+ (Fin N → ℤ) where
  toFun a i := a i.val
  map_zero' := rfl
  map_add' _ _ := rfl

/-- Restriction of variable coordinates includes the right endpoint. -/
def restrictVariables (N : ℕ) : Sequence →+ (Fin (N + 1) → ℤ) where
  toFun a i := a i.val
  map_zero' := rfl
  map_add' _ _ := rfl

/-- Restriction is a chain map for the two-term difference complexes. -/
theorem restriction_commutes (N : ℕ) :
    (restrictRows N).comp delta = (prefixDelta N).comp (restrictVariables N) := by
  rfl

/-- The induced restriction on the cokernel is well defined. -/
def restrictObstruction (N : ℕ) : ObstructionGroup →+ PrefixObstructionGroup N :=
  QuotientAddGroup.map delta.range (prefixDelta N).range (restrictRows N) (by
    rintro b ⟨a, rfl⟩
    exact ⟨restrictVariables N a, rfl⟩)

theorem restrict_obstruction (N : ℕ) :
    restrictObstruction N obstruction = prefixObstruction N := by
  rfl

/-- A nonzero global class restricts to zero at every finite prefix. -/
theorem nonzero_residual_invisible_on_prefixes :
    obstruction ≠ 0 ∧ ∀ N, restrictObstruction N obstruction = 0 := by
  exact ⟨obstruction_ne_zero, fun N => (restrict_obstruction N).trans
    (prefix_obstruction_eq_zero N)⟩

/-- Degree zero tests finite solvability; degree one tests the actual finite cokernel.
There are no degrees above one in this explicit two-term complex. -/
def prefixDetects (q N : ℕ) : Prop :=
  (q = 0 ∧ ¬ ∃ a, prefixDelta N a = prefixOnes N) ∨
  (q = 1 ∧ prefixObstruction N ≠ 0)

theorem no_prefix_detection (q N : ℕ) : ¬ prefixDetects q N := by
  rintro (⟨_, h⟩ | ⟨_, h⟩)
  · exact h (prefixDelta_surjective N (prefixOnes N))
  · exact h (prefix_obstruction_eq_zero N)

/-- A natural test of the earlier finite-support schema. -/
def finitePrefixSystem : ResidualSystem where
  Piece := ℕ
  Small := fun _ => True
  Exact := ∃ a : Sequence, delta a = ones
  Obstruct := prefixDetects

theorem finitePrefixSystem_sound : finitePrefixSystem.Sound := by
  intro q N _ h
  exact (no_prefix_detection q N h).elim

/-- Adding degree one does not restore finite-support reflection in this example. -/
theorem finitePrefixSystem_not_krr : ¬ finitePrefixSystem.KRR := by
  intro h
  obtain ⟨q, N, _, ho⟩ := h no_global_lift
  exact no_prefix_detection q N ho

/-- For the support-threshold experiment, `some N` means a finite prefix and `none`
means the whole countable tower. This family of pieces is explicitly fixed. -/
def supportedSystem : SizedResidualSystem where
  Piece := Option ℕ
  size := fun p => match p with
    | some N => (N + 1 : ℕ)
    | none => Cardinal.aleph0
  Exact := ∃ a : Sequence, delta a = ones
  Obstruct := fun q p => match p with
    | some N => prefixDetects q N
    | none => q = 1 ∧ obstruction ≠ 0

/-- For this one fixed tower and family of pieces, the exact support threshold is
countable: a witness is allowed precisely when `aleph0 < κ`. This is not a
large-cardinal theorem and not a statement about all residual systems. -/
theorem supportedSystem_krr_iff (κ : Cardinal) :
    supportedSystem.KRRAt κ ↔ Cardinal.aleph0 < κ := by
  constructor
  · intro h
    obtain ⟨q, p, hp, ho⟩ := h no_global_lift
    cases p with
    | none => exact hp
    | some N => exact (no_prefix_detection q N ho).elim
  · intro hk _
    exact ⟨1, none, hk, rfl, obstruction_ne_zero⟩

theorem supportedSystem_not_krr_aleph0 :
    ¬ supportedSystem.KRRAt Cardinal.aleph0 := by
  rw [supportedSystem_krr_iff]
  exact lt_irrefl _

end Komorebi.IntegerTower
