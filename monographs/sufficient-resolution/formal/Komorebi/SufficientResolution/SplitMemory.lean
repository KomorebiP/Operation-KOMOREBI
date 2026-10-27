import Komorebi.SufficientResolution.FiniteMemory

/-!
# Canonical hidden-state realization of any split compression

The hidden space is the actual kernel of compression, not an arbitrary added
space. Orthogonality is never assumed. This transports the memory certificate
back to the split-compression operators of the original block.
-/

set_option autoImplicit false
noncomputable section
namespace Komorebi.SufficientResolution.SplitCompression

universe uR uX uZ
variable {R : Type uR} [Field R]
variable {X : Type uX} [AddCommGroup X] [Module R X]
variable {Z : Type uZ} [AddCommGroup Z] [Module R Z]
variable (c : SplitCompression R X Z)

/-- The hidden coordinates are precisely the kernel of the observation. -/
abbrev HiddenSpace := LinearMap.ker c.compress

/-- The discarded-state map with its codomain restricted to the actual kernel. -/
def hiddenCoordinate : X →ₗ[R] c.HiddenSpace :=
  c.hidden.codRestrict (LinearMap.ker c.compress) (by
    intro x
    change c.compress (c.hidden x) = 0
    simp [map_sub])

@[simp] theorem hiddenCoordinate_val (x : X) :
    (c.hiddenCoordinate x : X) = c.hidden x := rfl

/-- Exact visible/hidden analysis. -/
def blockAnalysis : X →ₗ[R] (Z × c.HiddenSpace) :=
  c.compress.prod c.hiddenCoordinate

/-- Exact synthesis of visible and hidden coordinates. -/
def blockSynthesis : (Z × c.HiddenSpace) →ₗ[R] X :=
  (c.lift.comp (LinearMap.fst R Z c.HiddenSpace)) +
    ((LinearMap.ker c.compress).subtype.comp (LinearMap.snd R Z c.HiddenSpace))

@[simp] theorem blockSynthesis_apply (y : Z) (z : c.HiddenSpace) :
    c.blockSynthesis (y,z) = c.lift y + (z : X) := rfl

 theorem block_synthesis_analysis (x : X) :
    c.blockSynthesis (c.blockAnalysis x) = x := by
  change c.lift (c.compress x) + c.hidden x = x
  rw [c.hidden_apply]
  abel

 theorem block_analysis_synthesis (p : Z × c.HiddenSpace) :
    c.blockAnalysis (c.blockSynthesis p) = p := by
  rcases p with ⟨y,z⟩
  apply Prod.ext
  · change c.compress (c.lift y + (z : X)) = y
    rw [map_add, c.compress_lift_apply, (show c.compress (z : X) = 0 from z.property), add_zero]
  · apply Subtype.ext
    change c.hidden (c.lift y + (z : X)) = (z : X)
    rw [c.hidden_apply, map_add, c.compress_lift_apply,
      (show c.compress (z : X) = 0 from z.property), add_zero]
    abel

/-- Actual block dynamics induced by the original fine operator. -/
def toBlockDynamics (T : X →ₗ[R] X) : BlockDynamics R Z c.HiddenSpace where
  A := c.coarse T
  B := c.compress.comp (T.comp (LinearMap.ker c.compress).subtype)
  G := c.hiddenCoordinate.comp (T.comp c.lift)
  D := c.hiddenCoordinate.comp (T.comp (LinearMap.ker c.compress).subtype)

/-- The constructed full block transition is exactly conjugate to the original map. -/
 theorem block_step_eq (T : X →ₗ[R] X) (p : Z × c.HiddenSpace) :
    (c.toBlockDynamics T).step p = c.blockAnalysis (T (c.blockSynthesis p)) := by
  rcases p with ⟨y,z⟩
  apply Prod.ext
  · change c.compress (T (c.lift y)) + c.compress (T (z : X)) =
      c.compress (T (c.lift y + (z : X)))
    simp only [map_add]
  · apply Subtype.ext
    change c.hidden (T (c.lift y)) + c.hidden (T (z : X)) =
      c.hidden (T (c.lift y + (z : X)))
    simp only [map_add]

 theorem block_powers_eq (T : X →ₗ[R] X) (n : ℕ) (p : Z × c.HiddenSpace) :
    ((c.toBlockDynamics T).step^n) p = c.blockAnalysis ((T^n) (c.blockSynthesis p)) := by
  induction n with
  | zero => simpa using (c.block_analysis_synthesis p).symm
  | succ n ih =>
    rw [pow_succ', Module.End.mul_apply, ih, c.block_step_eq,
      c.block_synthesis_analysis, pow_succ', Module.End.mul_apply]

/-- The prepared block maps are exactly the original compressed powers. -/
 theorem block_prepared_eq_coarse (T : X →ₗ[R] X) (n : ℕ) :
    (c.toBlockDynamics T).prepared n = c.coarse (T^n) := by
  ext y
  change (((c.toBlockDynamics T).step^n) (y,0)).1 = c.compress ((T^n) (c.lift y))
  rw [c.block_powers_eq]
  change c.compress ((T^n) (c.lift y + 0)) = c.compress ((T^n) (c.lift y))
  rw [add_zero]

/-- Every split compression inherits the necessary-and-sufficient memory criterion. -/
 theorem exact_powers_iff_canonical_memory_zero (T : X →ₗ[R] X) :
    (∀ n, c.coarse (T^n) = (c.coarse T)^n) ↔
      (∀ k, (c.toBlockDynamics T).memory k = 0) := by
  have h := (c.toBlockDynamics T).prepared_powers_iff_memory_zero
  simp only [c.block_prepared_eq_coarse] at h
  exact h

/-- The certificate length is the dimension of ker C, not of the entire fine state. -/
 theorem exact_powers_iff_canonical_finite_memory (T : X →ₗ[R] X)
    [FiniteDimensional R c.HiddenSpace] :
    (∀ n, c.coarse (T^n) = (c.coarse T)^n) ↔
      (∀ k < Module.finrank R c.HiddenSpace, (c.toBlockDynamics T).memory k = 0) := by
  have h := (c.toBlockDynamics T).prepared_powers_iff_finrank_memory
  simp only [c.block_prepared_eq_coarse] at h
  exact h

/-- A correctly dimensioned finite-depth operator audit certifies every depth. -/
 theorem exact_powers_iff_canonical_finite_horizon (T : X →ₗ[R] X)
    [FiniteDimensional R c.HiddenSpace] :
    (∀ n, c.coarse (T^n) = (c.coarse T)^n) ↔
      (∀ n ≤ Module.finrank R c.HiddenSpace + 1,
        c.coarse (T^n) = (c.coarse T)^n) := by
  have h := (c.toBlockDynamics T).prepared_powers_iff_finite_horizon
  simp only [c.block_prepared_eq_coarse] at h
  exact h

end Komorebi.SufficientResolution.SplitCompression
