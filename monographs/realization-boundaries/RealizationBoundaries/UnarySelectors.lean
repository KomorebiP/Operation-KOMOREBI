import RealizationBoundaries.SubgroupSpectrum
import Mathlib.Data.Fintype.Pigeonhole

/-! # Genuine finite unary state machines and their selector groups -/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

/-- A unary deterministic finite automaton: one transition for each input symbol. -/
structure UnaryMachine where
  State : Type
  finite_state : Finite State
  start : State
  step : State → State
  accepting : Set State

attribute [instance] UnaryMachine.finite_state

/-- Acceptance after the unary word of length `n`. -/
def UnaryMachine.accepts (M : UnaryMachine) (n : ℕ) : Prop :=
  M.step^[n] M.start ∈ M.accepting

/-- A finite prefix followed by a repeated nonempty period. -/
def UltimatelyPeriodic (B : Set ℕ) : Prop :=
  ∃ N d : ℕ, 0 < d ∧ ∀ n, N ≤ n → (n + d ∈ B ↔ n ∈ B)

/-- A selector is realized by a finite unary automaton with its actual iterated transition. -/
def UnaryRecognizable (B : Set ℕ) : Prop :=
  ∃ M : UnaryMachine, ∀ n, M.accepts n ↔ n ∈ B

/-- Two equal orbit states force equality of all subsequent states. -/
theorem unary_iterate_propagates (M : UnaryMachine) {i j : ℕ}
    (h : M.step^[i] M.start = M.step^[j] M.start) (k : ℕ) :
    M.step^[i + k] M.start = M.step^[j + k] M.start := by
  rw [Nat.add_comm i k, Nat.add_comm j k, Function.iterate_add_apply, Function.iterate_add_apply]
  exact congrArg M.step^[k] h

/-- The pigeonhole principle gives eventual periodicity of the actual finite-state orbit. -/
theorem unaryMachine_ultimatelyPeriodic (M : UnaryMachine) :
    UltimatelyPeriodic {n | M.accepts n} := by
  classical
  have hnot : ¬ Function.Injective (fun n : ℕ => M.step^[n] M.start) := by
    intro hi
    let := Finite.of_injective _ hi
    exact not_finite ℕ
  obtain ⟨i, j, hij, hne⟩ := Function.not_injective_iff.mp hnot
  wlog hlt : i < j generalizing i j
  · exact this j i hij.symm hne.symm (by omega)
  refine ⟨i, j-i, by omega, ?_⟩
  intro n hn
  have he := unary_iterate_propagates M hij (n-i)
  have hi : i + (n-i) = n := Nat.add_sub_of_le hn
  have hj : j + (n-i) = n + (j-i) := by omega
  rw [hi, hj] at he
  exact Iff.of_eq (congrArg (fun q => q ∈ M.accepting) he.symm)

/-- The tail seen after a prefix is the future Boolean acceptance sequence. -/
def unaryTail (B : Set ℕ) (n : ℕ) : Set ℕ := {k | n+k ∈ B}

theorem unaryTail_periodic {B : Set ℕ} {N d : ℕ}
    (h : ∀ n, N ≤ n → (n+d ∈ B ↔ n ∈ B)) {n : ℕ} (hn : N ≤ n) :
    unaryTail B (n+d) = unaryTail B n := by
  ext k
  exact (show n+d+k ∈ B ↔ n+k ∈ B by
    simpa only [Nat.add_assoc, Nat.add_left_comm, Nat.add_comm] using h (n+k) (by omega))

/-- Every eventual-period tail is represented among the first `N+d` tails. -/
theorem unaryTail_bounded {B : Set ℕ} {N d : ℕ} (hd : 0 < d)
    (h : ∀ n, N ≤ n → (n+d ∈ B ↔ n ∈ B)) (n : ℕ) :
    ∃ m, m < N+d ∧ unaryTail B n = unaryTail B m := by
  induction n using Nat.strong_induction_on with
  | h n ih =>
    by_cases hn : n < N+d
    · exact ⟨n, hn, rfl⟩
    · have hlt : n-d < n := by omega
      obtain ⟨m, hm, he⟩ := ih (n-d) hlt
      refine ⟨m, hm, ?_⟩
      have hnd : N ≤ n-d := by omega
      have heq := unaryTail_periodic h hnd
      have hadd : n-d+d = n := by omega
      rw [hadd] at heq
      exact heq.trans he

theorem unaryTail_range_finite {B : Set ℕ} (hB : UltimatelyPeriodic B) :
    (Set.range (unaryTail B)).Finite := by
  obtain ⟨N, d, hd, h⟩ := hB
  apply ((Finset.range (N+d)).finite_toSet.image (unaryTail B)).subset
  rintro t ⟨n, rfl⟩
  obtain ⟨m, hm, he⟩ := unaryTail_bounded hd h n
  exact ⟨m, Finset.mem_range.mpr hm, he.symm⟩

/-- The finite set of tails is a DFA state space, with transition given by deleting one symbol. -/
def unaryTailMachine {B : Set ℕ} (hB : UltimatelyPeriodic B) : UnaryMachine where
  State := Set.range (unaryTail B)
  finite_state := (unaryTail_range_finite hB).to_subtype
  start := ⟨unaryTail B 0, ⟨0, rfl⟩⟩
  step t := ⟨{k | k+1 ∈ t.val}, by
    obtain ⟨n, hn⟩ := t.property
    refine ⟨n+1, ?_⟩
    ext k
    change n+1+k ∈ B ↔ k+1 ∈ t.val
    rw [← hn]
    change n+1+k ∈ B ↔ n+(k+1) ∈ B
    have he : n+1+k = n+(k+1) := by omega
    rw [he]⟩
  accepting := {t | 0 ∈ t.val}

theorem unaryTailMachine_orbit {B : Set ℕ} (hB : UltimatelyPeriodic B) (n : ℕ) :
    ((unaryTailMachine hB).step^[n] (unaryTailMachine hB).start).val = unaryTail B n := by
  induction n with
  | zero => rfl
  | succ n ih =>
    rw [Function.iterate_succ_apply']
    ext k
    change k+1 ∈ ((unaryTailMachine hB).step^[n] (unaryTailMachine hB).start).val ↔ n+1+k ∈ B
    rw [ih]
    change n+(k+1) ∈ B ↔ n+1+k ∈ B
    have he : n+(k+1) = n+1+k := by omega
    rw [he]

theorem unaryTailMachine_accepts {B : Set ℕ} (hB : UltimatelyPeriodic B) (n : ℕ) :
    (unaryTailMachine hB).accepts n ↔ n ∈ B := by
  change 0 ∈ ((unaryTailMachine hB).step^[n] (unaryTailMachine hB).start).val ↔ n ∈ B
  rw [unaryTailMachine_orbit]
  simp [unaryTail]

/-- Unary finite-state recognition is exactly ultimate periodicity. -/
theorem unaryRecognizable_iff_ultimatelyPeriodic (B : Set ℕ) :
    UnaryRecognizable B ↔ UltimatelyPeriodic B := by
  constructor
  · rintro ⟨M, hM⟩
    have hB : {n | M.accepts n} = B := Set.ext hM
    exact hB ▸ unaryMachine_ultimatelyPeriodic M
  · intro hB
    exact ⟨unaryTailMachine hB, unaryTailMachine_accepts hB⟩

/-- Prime-index selectors interpreted in the actual subgroup D_B. -/
def indexedSpectrum (B : Set ℕ) : Set Prime := primeAt '' B

theorem indexedSpectrum_injective : Function.Injective indexedSpectrum :=
  Set.image_injective.mpr primeAt_injective

/-- A unary-selector grammar may output a group isomorphic to its selected prime subgroup. -/
def UnaryGroupRealizable (B : Set ℕ) : Prop :=
  ∃ C : Set ℕ, UnaryRecognizable C ∧
    Nonempty (spectrumSubgroup (indexedSpectrum C) ≃+
      spectrumSubgroup (indexedSpectrum B))

/-- Monograph 3.5: abstract group isomorphism cannot hide a different unary selector. -/
theorem unary_selector_classification (B : Set ℕ) :
    UnaryGroupRealizable B ↔ UltimatelyPeriodic B := by
  constructor
  · rintro ⟨C, hC, he⟩
    have hCB : C = B := indexedSpectrum_injective
      ((spectrumSubgroup_isomorphic_iff _ _).mp he)
    exact hCB ▸ (unaryRecognizable_iff_ultimatelyPeriodic C).mp hC
  · intro hB
    exact ⟨B, (unaryRecognizable_iff_ultimatelyPeriodic B).mpr hB, ⟨AddEquiv.refl _⟩⟩

end RealizationBoundaries
