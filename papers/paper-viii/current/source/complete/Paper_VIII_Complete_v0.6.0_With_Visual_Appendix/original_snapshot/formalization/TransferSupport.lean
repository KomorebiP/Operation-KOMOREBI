module
public import PacketIR
import all PacketIR
import all QuantumPacketCore
public import Lean.Elab.Tactic.Omega

/-!
Author: Komorebi P.
Paper VIII items 6.1, 6.2, 6.3. Paths retain their length and direction.
Zero-length paths are included explicitly, so the constant polynomial term
and diagonal reachability are not silently dropped.
-/

public section
set_option autoImplicit false
namespace KomorebiPaperVIII
open scoped BigOperators
open KomorebiPaperVII

variable {R I : Type*} [Ring R] [Fintype I] [DecidableEq I]
variable (P : PacketFamily R I)

/-- A path of n exact nonzero transfer blocks, source a and target b. -/
def TransferPath (A : R) : ℕ → I → I → Prop
  | 0, b, a => b = a
  | n + 1, b, a => ∃ c, P.block A b c ≠ 0 ∧ TransferPath A n c a

/-- Finite active-path evaluation. Zero edges are explicitly excluded. -/
noncomputable def activePathSum (A : R) : ℕ → I → I → R
  | 0, b, a => if b = a then P.proj a else 0
  | n + 1, b, a => by
      classical
      exact ∑ c, if P.block A b c ≠ 0 then
        P.block A b c * activePathSum A n c a else 0

/-- Theorem 6.1: the nested active-path sum equals the actual power block. -/
theorem power_path_expansion (A : R) (n : ℕ) (b a : I) :
    P.block (A ^ n) b a = activePathSum P A n b a := by
  classical
  induction n generalizing b a with
  | zero =>
      by_cases h : b = a
      · subst b
        simp [activePathSum, PacketFamily.block, P.mul_proj]
      · simp [activePathSum, PacketFamily.block, P.mul_proj, h]
  | succ n ih =>
      rw [pow_succ', P.compose_blocks]
      simp only [activePathSum]
      apply Finset.sum_congr rfl
      intro c _
      rw [ih]
      by_cases h : P.block A b c = 0 <;> simp [h]

/-- A recursive path sum vanishes when no contributing path exists. -/
theorem active_path_sum_zero (A : R) (n : ℕ) (b a : I)
    (h : ¬ TransferPath P A n b a) : activePathSum P A n b a = 0 := by
  classical
  induction n generalizing b a with
  | zero =>
      change ¬ b = a at h
      simp [activePathSum, h]
  | succ n ih =>
      simp only [activePathSum]
      apply Finset.sum_eq_zero
      intro c _
      by_cases hc : P.block A b c = 0
      · simp [hc]
      · have hn : ¬ TransferPath P A n c a := by
          intro hp
          exact h ⟨c, hc, hp⟩
        simp [hc, ih c a hn]

/-- Theorem 6.1: no directed path of the required length implies a zero block. -/
theorem power_block_zero_of_no_path (A : R) (n : ℕ) (b a : I)
    (h : ¬ TransferPath P A n b a) : P.block (A ^ n) b a = 0 := by
  rw [power_path_expansion P]
  exact active_path_sum_zero P A n b a h

theorem power_support_inclusion (A : R) (n : ℕ) (b a : I)
    (h : P.block (A ^ n) b a ≠ 0) : TransferPath P A n b a := by
  classical
  by_contra hn
  exact h (power_block_zero_of_no_path P A n b a hn)

/-- Corollary 6.3: a bound on path length gives nilpotence of the actual operator. -/
theorem nilpotent_of_path_bound (A : R) (h : ℕ)
    (hpaths : ∀ b a, ¬ TransferPath P A (h + 1) b a) : A ^ (h + 1) = 0 := by
  apply all_blocks_zero P
  intro b a
  exact power_block_zero_of_no_path P A (h + 1) b a (hpaths b a)

/-- A topological-level certificate yields an explicit path-length bound. -/
theorem path_level_bound (A : R) (level : I → ℕ)
    (hlevel : ∀ b a, P.block A b a ≠ 0 → level a < level b)
    (n : ℕ) (b a : I) (hp : TransferPath P A n b a) :
    level a + n ≤ level b := by
  induction n generalizing b a with
  | zero =>
      have he : b = a := hp
      subst b
      omega
  | succ n ih =>
      obtain ⟨c, hc, hp⟩ := hp
      have h1 := ih c a hp
      have h2 := hlevel b c hc
      omega

/-- Constructive acyclicity certificate: levels 0,...,h force A^(h+1)=0. -/
theorem nilpotent_of_topological_levels (A : R) (h : ℕ) (level : I → Fin (h + 1))
    (hlevel : ∀ b a, P.block A b a ≠ 0 → (level a).val < (level b).val) :
    A ^ (h + 1) = 0 := by
  apply nilpotent_of_path_bound P A h
  intro b a hp
  have hb := path_level_bound P A (fun i => (level i).val) hlevel (h + 1) b a hp
  have hbound := (level b).isLt
  omega

section Polynomial
variable {K : Type*} [CommSemiring K] [Algebra K R]

theorem block_smul (c : K) (A : R) (b a : I) :
    P.block (c • A) b a = c • P.block A b a := by
  simp only [PacketFamily.block, mul_smul_comm, smul_mul_assoc]

/-- Corollary 6.2: the support of an actual finite polynomial is contained in
    the union of power supports. Coefficients may be zero; degree zero is included. -/
theorem polynomial_support_inclusion (d : ℕ) (c : Fin (d + 1) → K) (A : R) (b a : I)
    (h : P.block (∑ j, c j • A ^ (j : ℕ)) b a ≠ 0) :
    ∃ j : Fin (d + 1), P.block (A ^ (j : ℕ)) b a ≠ 0 := by
  classical
  by_contra hn
  apply h
  rw [block_sum]
  apply Finset.sum_eq_zero
  intro j _
  have hj : P.block (A ^ (j : ℕ)) b a = 0 := by
    by_contra hj
    exact hn ⟨j, hj⟩
  rw [block_smul, hj, smul_zero]

/-- A useful compiler certificate obtained by composing polynomial and path support. -/
theorem polynomial_zero_of_no_paths (d : ℕ) (c : Fin (d + 1) → K) (A : R) (b a : I)
    (h : ∀ j : Fin (d + 1), ¬ TransferPath P A (j : ℕ) b a) :
    P.block (∑ j, c j • A ^ (j : ℕ)) b a = 0 := by
  classical
  by_contra hn
  obtain ⟨j, hj⟩ := polynomial_support_inclusion P d c A b a hn
  exact h j (power_support_inclusion P A (j : ℕ) b a hj)
end Polynomial

end KomorebiPaperVIII

#print axioms KomorebiPaperVIII.power_path_expansion
#print axioms KomorebiPaperVIII.active_path_sum_zero
#print axioms KomorebiPaperVIII.power_block_zero_of_no_path
#print axioms KomorebiPaperVIII.power_support_inclusion
#print axioms KomorebiPaperVIII.nilpotent_of_path_bound
#print axioms KomorebiPaperVIII.path_level_bound
#print axioms KomorebiPaperVIII.nilpotent_of_topological_levels
#print axioms KomorebiPaperVIII.block_smul
#print axioms KomorebiPaperVIII.polynomial_support_inclusion
#print axioms KomorebiPaperVIII.polynomial_zero_of_no_paths
