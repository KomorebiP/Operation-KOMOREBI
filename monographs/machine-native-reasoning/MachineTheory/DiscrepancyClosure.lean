import MachineTheory.CommonQuotientInterface
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas

/-!
# Finite construction of the propagated discrepancy space

Start from the sum of difference ranges, then add the images under each
reference action. The sequence is increasing, stays inside E, and has no plateau
before E. Finite dimension gives stabilization by dim(V) rounds. The code is an
algebraic construction, not a claim about efficient numerical subspace discovery.
-/
namespace Komorebi.MachineTheory.CommonQuotient

noncomputable section

variable {K V Y A Θ : Type*}
variable [Field K] [AddCommGroup V] [Module K V] [AddCommGroup Y] [Module K Y]

/-- Initial sum of all one-step difference ranges. -/
def seed (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) : Submodule K V :=
  ⨆ θ, ⨆ a, LinearMap.range (T θ a - T θ₀ a)

/-- One invariant-closure step. -/
def closureStep (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) (N : Submodule K V) : Submodule K V :=
  N ⊔ ⨆ a, N.map (T θ₀ a)

/-- The actual increasing construction, starting at the source's difference ranges. -/
def stage (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) : ℕ → Submodule K V
  | 0 => seed T θ₀
  | n + 1 => closureStep T θ₀ (stage T θ₀ n)

@[simp] theorem stage_zero (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) :
    stage T θ₀ 0 = seed T θ₀ := rfl

@[simp] theorem stage_succ (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) (n : ℕ) :
    stage T θ₀ (n + 1) = closureStep T θ₀ (stage T θ₀ n) := rfl

/-- Every input difference is already present at stage zero. -/
theorem difference_mem_seed (T : Θ → A → V →ₗ[K] V) (θ₀ θ : Θ) (a : A) (v : V) :
    (T θ a - T θ₀ a) v ∈ seed T θ₀ := by
  have h : LinearMap.range (T θ a - T θ₀ a) ≤ seed T θ₀ :=
    le_iSup_of_le θ (le_iSup_of_le a le_rfl)
  exact h ⟨v, rfl⟩

/-- The initial seed is contained in the propagated span. -/
theorem seed_le_discrepancy (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) :
    seed T θ₀ ≤ discrepancy T θ₀ := by
  apply iSup_le
  intro θ
  apply iSup_le
  intro a x hx
  obtain ⟨v, rfl⟩ := hx
  exact difference_mem T θ₀ a θ v

/-- Enlarging a submodule cannot shrink its closure step. -/
theorem closureStep_mono (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) :
    Monotone (closureStep T θ₀) := by
  intro N P h
  exact sup_le_sup h (iSup_mono fun a => Submodule.map_mono h)

/-- Each step contains the preceding stage. -/
theorem stage_le_succ (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) (n : ℕ) :
    stage T θ₀ n ≤ stage T θ₀ (n + 1) := le_sup_left

/-- The sequence is increasing over arbitrary stage indices. -/
theorem stage_mono (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) : Monotone (stage T θ₀) :=
  monotone_nat_of_le_succ (stage_le_succ T θ₀)

/-- No iteration introduces a vector outside the defined discrepancy span. -/
theorem stage_le_discrepancy (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) (n : ℕ) :
    stage T θ₀ n ≤ discrepancy T θ₀ := by
  induction n with
  | zero => exact seed_le_discrepancy T θ₀
  | succ n ih =>
    apply sup_le ih
    apply iSup_le
    intro a x hx
    obtain ⟨v, hv, rfl⟩ := hx
    exact reference_invariant T θ₀ a (ih hv)

/-- At a plateau every reference-action image remains in the same stage. -/
theorem plateau_invariant (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) (n : ℕ)
    (h : stage T θ₀ (n + 1) = stage T θ₀ n)
    (a : A) (x : V) (hx : x ∈ stage T θ₀ n) : T θ₀ a x ∈ stage T θ₀ n := by
  have hmap : (stage T θ₀ n).map (T θ₀ a) ≤ stage T θ₀ (n + 1) :=
    le_trans (le_iSup (fun b : A => (stage T θ₀ n).map (T θ₀ b)) a) le_sup_right
  have hx' := hmap ⟨x, hx, rfl⟩
  simpa only [h] using hx'

/-- The first plateau already equals E, without any finite-dimensional premise. -/
theorem plateau_eq_discrepancy (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) (n : ℕ)
    (h : stage T θ₀ (n + 1) = stage T θ₀ n) : stage T θ₀ n = discrepancy T θ₀ := by
  apply le_antisymm (stage_le_discrepancy T θ₀ n)
  apply discrepancy_le T θ₀
  · intro θ a v
    exact stage_mono T θ₀ (Nat.zero_le n) (difference_mem_seed T θ₀ θ a v)
  · exact plateau_invariant T θ₀ n h

/-- In finite dimension, a plateau occurs no later than the ambient dimension. -/
theorem bounded_plateau [FiniteDimensional K V] (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) :
    ∃ n ≤ Module.finrank K V, stage T θ₀ (n + 1) = stage T θ₀ n := by
  by_contra h
  push Not at h
  have hstrict : ∀ n, n ≤ Module.finrank K V → stage T θ₀ n < stage T θ₀ (n + 1) := by
    intro n hn
    exact lt_of_le_of_ne (stage_le_succ T θ₀ n) (Ne.symm (h n hn))
  have hgrowth : ∀ n, n ≤ Module.finrank K V + 1 → n ≤ Module.finrank K (stage T θ₀ n) := by
    intro n
    induction n with
    | zero => intro _; exact Nat.zero_le _
    | succ n ih =>
      intro hn
      have hn' : n ≤ Module.finrank K V := Nat.le_of_succ_le_succ hn
      have hp := ih (Nat.le_trans hn' (Nat.le_succ _))
      have hi := Submodule.finrank_lt_finrank_of_lt (hstrict n hn')
      omega
  have hbig := hgrowth (Module.finrank K V + 1) le_rfl
  have hupper := (stage T θ₀ (Module.finrank K V + 1)).finrank_le
  omega

/-- The source construction is complete by dim(V), not just at an unspecified limit. -/
theorem stage_finrank_eq [FiniteDimensional K V] (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) :
    stage T θ₀ (Module.finrank K V) = discrepancy T θ₀ := by
  obtain ⟨n, hn, heq⟩ := bounded_plateau T θ₀
  apply le_antisymm (stage_le_discrepancy T θ₀ _)
  rw [← plateau_eq_discrepancy T θ₀ n heq]
  exact stage_mono T θ₀ hn

/-- Every later stage remains the same constructed discrepancy space. -/
theorem stage_eq_of_finrank_le [FiniteDimensional K V] (T : Θ → A → V →ₗ[K] V)
    (θ₀ : Θ) (n : ℕ) (hn : Module.finrank K V ≤ n) : stage T θ₀ n = discrepancy T θ₀ := by
  apply le_antisymm (stage_le_discrepancy T θ₀ n)
  rw [← stage_finrank_eq T θ₀]
  exact stage_mono T θ₀ hn

/-- Core 2.4 with the finite-dimensional, finite-catalogue source assumptions.
The three equivalent conditions, canonical quotient, arbitrary switching and
finite discrepancy construction are tied to the same T, reference and readout. -/
theorem source_core24 [Fintype A] [Fintype Θ] [FiniteDimensional K V]
    (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) (Q : V →ₗ[K] Y) :
    (ObservableAgreement T θ₀ Q ↔ discrepancy T θ₀ ≤ LinearMap.ker Q) ∧
    (discrepancy T θ₀ ≤ LinearMap.ker Q ↔ Nonempty (CommonModel T Q)) ∧
    stage T θ₀ (Module.finrank K V) = discrepancy T θ₀ ∧
    (ObservableAgreement T θ₀ Q → ∀ (w : List (Θ × A)) (v : V),
      Q (switchedMap T w v) = Q (wordMap (T θ₀) (w.map Prod.snd) v)) :=
  ⟨agreement_iff_invisible T θ₀ Q, (commonModel_iff_invisible T θ₀ Q).symm,
    stage_finrank_eq T θ₀, switching_output T θ₀ Q⟩

/-- The source-facing raw reference operator family is tied to an actual candidate. -/
theorem source_core24_reference [Fintype A] [Fintype Θ] [FiniteDimensional K V]
    (T : Θ → A → V →ₗ[K] V) (R : A → V →ₗ[K] V) (θ₀ : Θ)
    (hR : T θ₀ = R) (Q : V →ₗ[K] Y) :
    ((∀ θ w, Q.comp (wordMap (T θ) w) = Q.comp (wordMap R w)) ↔
      Nonempty (CommonModel T Q)) ∧
    ((∀ θ w, Q.comp (wordMap (T θ) w) = Q.comp (wordMap R w)) →
      ∀ (w : List (Θ × A)) (v : V), Q (switchedMap T w v) = Q (wordMap R (w.map Prod.snd) v)) := by
  subst R
  exact ⟨agreement_iff_commonModel T θ₀ Q, switching_output T θ₀ Q⟩

end
end Komorebi.MachineTheory.CommonQuotient
