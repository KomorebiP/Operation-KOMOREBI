module

public import Mathlib.Topology.Algebra.InfiniteSum.Real

/-!
# Local discrete dynamics and global continuous reconstruction

This module isolates the refinement bridge required by the Komorebi Physics
programme.  Each finite resolution carries its own state type and evolution.
Exact adjacent-level intertwining sends coherent discrete histories to coherent
histories.  A reconstruction into a complete metric space has a canonical
continuous-limit state whenever its adjacent defects are bounded by a summable
series.

The theorem is structural.  It does not assert that the concrete Clifford walk
already supplies the required refinement embeddings or defect estimates.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics
namespace LocalDiscreteGlobalContinuum

open Filter
open scoped Topology BigOperators

universe u v

/-- A hierarchy of finite-resolution state spaces with levelwise dynamics.
`compatible` is the exact adjacent-level intertwining law
`U_(n+1) ∘ ι_n = ι_n ∘ U_n`. -/
structure ExactRefinementTower (Level : ℕ → Type u) where
  embed : (n : ℕ) → Level n → Level n.succ
  evolve : (n : ℕ) → Level n → Level n
  compatible : ∀ (n : ℕ) (x : Level n),
    evolve n.succ (embed n x) = embed n (evolve n x)

/-- A state represented coherently at every finite resolution. -/
structure CoherentState {Level : ℕ → Type u}
    (T : ExactRefinementTower Level) where
  state : (n : ℕ) → Level n
  coherent : ∀ n : ℕ, T.embed n (state n) = state n.succ

namespace ExactRefinementTower

variable {Level : ℕ → Type u} (T : ExactRefinementTower Level)

/-- Exact levelwise evolution preserves cross-resolution coherence. -/
def evolveState (ψ : CoherentState T) : CoherentState T where
  state n := T.evolve n (ψ.state n)
  coherent n := by
    calc
      T.embed n (T.evolve n (ψ.state n)) =
          T.evolve n.succ (T.embed n (ψ.state n)) :=
        (T.compatible n (ψ.state n)).symm
      _ = T.evolve n.succ (ψ.state n.succ) := by
        rw [ψ.coherent n]

@[simp] theorem evolveState_state (ψ : CoherentState T) (n : ℕ) :
    (T.evolveState ψ).state n = T.evolve n (ψ.state n) := rfl

/-- Embed a state through `k` successive refinement levels. -/
def iterEmbed (T : ExactRefinementTower Level) (n : ℕ) : (k : ℕ) → Level n → Level (n + k)
  | 0 => fun x => x
  | k + 1 => fun x => T.embed (n + k) (iterEmbed T n k x)

@[simp] theorem iterEmbed_zero (n : ℕ) (x : Level n) :
    iterEmbed T n 0 x = x := rfl

@[simp] theorem iterEmbed_succ (n k : ℕ) (x : Level n) :
    iterEmbed T n k.succ x = T.embed (n + k) (iterEmbed T n k x) := rfl

/-- Adjacent intertwining propagates to every finite refinement depth. -/
theorem evolve_iterEmbed (n k : ℕ) (x : Level n) :
    T.evolve (n + k) (iterEmbed T n k x) =
      iterEmbed T n k (T.evolve n x) := by
  induction k with
  | zero => rfl
  | succ k ih =>
      simp only [Nat.add_succ, iterEmbed]
      rw [T.compatible, ih]

/-- A coherent state agrees with its own iterated refinement at every finite
resolution depth. -/
theorem CoherentState.iterEmbed_state (ψ : CoherentState T) (n k : ℕ) :
    iterEmbed T n k (ψ.state n) = ψ.state (n + k) := by
  induction k with
  | zero => rfl
  | succ k ih =>
      simp only [Nat.add_succ, iterEmbed]
      rw [ih, ψ.coherent]

/-- A reconstruction of a coherent state in one common target space. -/
def reconstructedSequence {Y : Type v}
    (R : (n : ℕ) → Level n → Y) (ψ : CoherentState T) : ℕ → Y :=
  fun n => R n (ψ.state n)

/-- Exact reconstruction compatibility makes adjacent reconstructions equal. -/
theorem reconstructedSequence_succ {Y : Type v}
    (R : (n : ℕ) → Level n → Y)
    (hR : ∀ (n : ℕ) (x : Level n), R n.succ (T.embed n x) = R n x)
    (ψ : CoherentState T) (n : ℕ) :
    T.reconstructedSequence R ψ n.succ = T.reconstructedSequence R ψ n := by
  simp only [reconstructedSequence]
  rw [← ψ.coherent n, hR]

/-- Under exact reconstruction compatibility, every resolution reconstructs
exactly the level-zero state. -/
theorem reconstructedSequence_eq_zero {Y : Type v}
    (R : (n : ℕ) → Level n → Y)
    (hR : ∀ (n : ℕ) (x : Level n), R n.succ (T.embed n x) = R n x)
    (ψ : CoherentState T) (n : ℕ) :
    T.reconstructedSequence R ψ n = T.reconstructedSequence R ψ 0 := by
  induction n with
  | zero => rfl
  | succ n ih =>
      calc
        T.reconstructedSequence R ψ n.succ =
            T.reconstructedSequence R ψ n :=
          T.reconstructedSequence_succ R hR ψ n
        _ = T.reconstructedSequence R ψ 0 := ih

/-- Exact reconstruction compatibility also applies after evolution. -/
theorem evolved_reconstructedSequence_eq_zero {Y : Type v}
    (R : (n : ℕ) → Level n → Y)
    (hR : ∀ (n : ℕ) (x : Level n), R n.succ (T.embed n x) = R n x)
    (ψ : CoherentState T) (n : ℕ) :
    T.reconstructedSequence R (T.evolveState ψ) n =
      R 0 (T.evolve 0 (ψ.state 0)) := by
  simpa [reconstructedSequence] using
    T.reconstructedSequence_eq_zero R hR (T.evolveState ψ) n

end ExactRefinementTower

section SummableDefect

variable {Y : Type v} [MetricSpace Y]

/-- A quantitative certificate that adjacent reconstruction defects are
summable.  This is the analytic condition that turns a hierarchy of finite
approximants into one global continuous-limit state. -/
structure SummableDefect (f : ℕ → Y) where
  bound : ℕ → ℝ
  summable_bound : Summable bound
  step_le : ∀ n : ℕ, dist (f n) (f n.succ) ≤ bound n

namespace SummableDefect

variable {f : ℕ → Y} (D : SummableDefect f)
include D

/-- Summable adjacent defects force the approximation sequence to be Cauchy. -/
theorem cauchySeq : CauchySeq f :=
  cauchySeq_of_dist_le_of_summable D.bound D.step_le D.summable_bound

variable [CompleteSpace Y]

/-- Existence of a global continuous-limit state. -/
theorem exists_limit : ∃ y : Y, Tendsto f atTop (𝓝 y) :=
  cauchySeq_tendsto_of_complete D.cauchySeq

/-- Canonical global state selected from the unique metric limit. -/
noncomputable def limit : Y := Classical.choose D.exists_limit

/-- The finite-resolution reconstructions converge to the canonical state. -/
theorem tendsto_limit : Tendsto f atTop (𝓝 D.limit) :=
  Classical.choose_spec D.exists_limit

/-- Quantitative continuum error: the error at level `n` is bounded by the
remaining tail of the adjacent defect series. -/
theorem dist_limit_le_tail (n : ℕ) :
    dist (f n) D.limit ≤ ∑' m : ℕ, D.bound (n + m) :=
  dist_le_tsum_of_dist_le_of_tendsto D.bound D.step_le D.summable_bound
    D.tendsto_limit n

/-- The global state is independent of the choice used to present its proof. -/
theorem limit_eq_of_tendsto {y : Y} (hy : Tendsto f atTop (𝓝 y)) :
    D.limit = y :=
  tendsto_nhds_unique D.tendsto_limit hy

end SummableDefect

end SummableDefect

namespace ExactRefinementTower

variable {Level : ℕ → Type u} (T : ExactRefinementTower Level)
variable {Y : Type v} [MetricSpace Y]

/-- Reconstruction data certifying a global continuum state for every coherent
discrete history. -/
structure ContinuumRealization where
  reconstruct : (n : ℕ) → Level n → Y
  defect : (ψ : CoherentState T) →
    SummableDefect (T.reconstructedSequence reconstruct ψ)

namespace ContinuumRealization

variable [CompleteSpace Y]
variable (C : ContinuumRealization T (Y := Y))
include C

/-- The global state represented by one coherent hierarchy. -/
noncomputable def globalState (ψ : CoherentState T) : Y :=
  (C.defect ψ).limit

/-- Every coherent hierarchy converges to its global reconstructed state. -/
theorem tendsto_globalState (ψ : CoherentState T) :
    Tendsto (T.reconstructedSequence C.reconstruct ψ) atTop
      (𝓝 (globalState T C ψ)) :=
  (C.defect ψ).tendsto_limit

/-- Explicit resolution-tail bound for the global reconstruction. -/
theorem globalState_error_bound (ψ : CoherentState T) (n : ℕ) :
    dist (C.reconstruct n (ψ.state n)) (globalState T C ψ) ≤
      ∑' m : ℕ, (C.defect ψ).bound (n + m) :=
  (C.defect ψ).dist_limit_le_tail n

/-- Global dynamics obtained by evolving every local resolution and then taking
the compatible continuum limit. -/
noncomputable def globalEvolution (ψ : CoherentState T) : Y :=
  globalState T C (T.evolveState ψ)

/-- The discrete evolved states converge to the global evolved state. -/
theorem tendsto_globalEvolution (ψ : CoherentState T) :
    Tendsto
      (fun n => C.reconstruct n (T.evolve n (ψ.state n)))
      atTop (𝓝 (globalEvolution T C ψ)) := by
  change Tendsto (T.reconstructedSequence C.reconstruct (T.evolveState ψ))
    atTop (𝓝 (globalState T C (T.evolveState ψ)))
  exact tendsto_globalState T C (T.evolveState ψ)

/-- Tail bound for the finite-resolution approximation to global dynamics. -/
theorem globalEvolution_error_bound (ψ : CoherentState T) (n : ℕ) :
    dist (C.reconstruct n (T.evolve n (ψ.state n)))
        (globalEvolution T C ψ) ≤
      ∑' m : ℕ, (C.defect (T.evolveState ψ)).bound (n + m) := by
  simpa [globalEvolution] using
    globalState_error_bound T C (T.evolveState ψ) n

end ContinuumRealization

/-- Exact reconstruction compatibility is the zero-defect special case. -/
def exactDefect
    (R : (n : ℕ) → Level n → Y)
    (hR : ∀ (n : ℕ) (x : Level n), R n.succ (T.embed n x) = R n x)
    (ψ : CoherentState T) :
    SummableDefect (T.reconstructedSequence R ψ) where
  bound := fun _ => 0
  summable_bound := summable_zero
  step_le n := by
    rw [T.reconstructedSequence_succ R hR ψ n]
    simp

/-- Every exactly compatible reconstruction defines a continuum realization. -/
def exactContinuumRealization
    (R : (n : ℕ) → Level n → Y)
    (hR : ∀ (n : ℕ) (x : Level n), R n.succ (T.embed n x) = R n x) :
    ContinuumRealization T (Y := Y) where
  reconstruct := R
  defect := T.exactDefect R hR

variable [CompleteSpace Y]

/-- In the exact case, the canonical global state is already represented at
level zero. -/
theorem exact_globalState_eq_zero
    (R : (n : ℕ) → Level n → Y)
    (hR : ∀ (n : ℕ) (x : Level n), R n.succ (T.embed n x) = R n x)
    (ψ : CoherentState T) :
    ContinuumRealization.globalState T
      (T.exactContinuumRealization (Y := Y) R hR) ψ = R 0 (ψ.state 0) := by
  apply (T.exactDefect R hR ψ).limit_eq_of_tendsto
  have hconst : T.reconstructedSequence R ψ =
      (fun _ : ℕ => R 0 (ψ.state 0)) := by
    funext n
    exact T.reconstructedSequence_eq_zero R hR ψ n
  rw [hconst]
  exact tendsto_const_nhds

/-- In the exact case, global evolution is exactly the level-zero evolution
viewed through the level-zero reconstruction. -/
theorem exact_globalEvolution_eq_zero
    (R : (n : ℕ) → Level n → Y)
    (hR : ∀ (n : ℕ) (x : Level n), R n.succ (T.embed n x) = R n x)
    (ψ : CoherentState T) :
    ContinuumRealization.globalEvolution T
      (T.exactContinuumRealization (Y := Y) R hR) ψ =
      R 0 (T.evolve 0 (ψ.state 0)) := by
  simpa [ContinuumRealization.globalEvolution] using
    exact_globalState_eq_zero T R hR (T.evolveState ψ)

end ExactRefinementTower

end LocalDiscreteGlobalContinuum
end KomorebiPhysics
