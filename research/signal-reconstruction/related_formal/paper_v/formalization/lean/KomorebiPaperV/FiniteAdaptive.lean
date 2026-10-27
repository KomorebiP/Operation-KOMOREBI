import Mathlib.MeasureTheory.Measure.Basic
import KomorebiPaperV.FiniteSelection

/-!
Author: Komorebi P.
Checked source; see the bundled build and axiom audit.
Finite trees with arbitrary positive finite branching, including unary branches.
Cuts are typed recursive prunings. CompletePrunings proves the set-valued
covering-antichain equivalence.
-/

open scoped BigOperators
namespace KomorebiPaperV.FiniteAdaptive

inductive Tree (A : Type*) where
  | leaf : A → Tree A
  | branch : (a : A) → (n : ℕ) → (Fin (n + 1) → Tree A) → Tree A

variable {A E : Type*}

def label : Tree A → A
  | .leaf a => a
  | .branch a _ _ => a

inductive Cut : Tree A → Type _ where
  | stop (t : Tree A) : Cut t
  | split {a : A} {n : ℕ} {children : Fin (n + 1) → Tree A} :
      (∀ i, Cut (children i)) → Cut (.branch a n children)

def cutSum [AddCommMonoid E] (p : A → E) : {t : Tree A} → Cut t → E
  | t, .stop _ => p (label t)
  | _, .split q => ∑ i, cutSum p (q i)

def conserves [AddCommMonoid E] (p : A → E) : Tree A → Prop
  | .leaf _ => True
  | .branch a _ children =>
      p a = ∑ i, p (label (children i)) ∧ ∀ i, conserves p (children i)

theorem cutSum_eq_root [AddCommMonoid E] (p : A → E) {t : Tree A} (q : Cut t) :
    conserves p t → cutSum p q = p (label t) := by
  induction q with
  | stop t => intro _; rfl
  | @split a n children q ih =>
    intro h
    rcases h with ⟨hroot, hchild⟩
    change (∑ i, cutSum p (q i)) = p a
    calc
      _ = ∑ i, p (label (children i)) :=
        Finset.sum_congr rfl (fun i _ => ih i (hchild i))
      _ = p a := hroot.symm

/-- This includes operator-valued packets: take E to be an additive space of maps. -/
theorem cutSum_eq_identity [AddCommMonoid E] (p : A → E) {t : Tree A}
    (q : Cut t) (h : conserves p t) (identity : E) (hroot : p (label t) = identity) :
    cutSum p q = identity := (cutSum_eq_root p q h).trans hroot

inductive Terminal : Tree A → Type _ where
  | here {a : A} : Terminal (.leaf a)
  | down {a : A} {n : ℕ} {children : Fin (n + 1) → Tree A}
      (i : Fin (n + 1)) : Terminal (children i) → Terminal (.branch a n children)

/-- Number of selected packets met by a typed root-to-terminal path. -/
def pathHits : {t : Tree A} → Cut t → Terminal t → ℕ
  | _, .stop _, _ => 1
  | _, .split q, .down i path => pathHits (q i) path

theorem pathHits_one {t : Tree A} (q : Cut t) :
    ∀ path : Terminal t, pathHits q path = 1 := by
  induction q with
  | stop t => intro _; rfl
  | split q ih =>
    intro path
    cases path with
    | down i path => exact ih i path

def leafCutEquiv (a : A) : Cut (.leaf a) ≃ Unit where
  toFun _ := ()
  invFun _ := .stop (.leaf a)
  left_inv q := by cases q; rfl
  right_inv u := by cases u; rfl

def branchCutEquiv (a : A) (n : ℕ) (children : Fin (n + 1) → Tree A) :
    Cut (.branch a n children) ≃ (Unit ⊕ (∀ i, Cut (children i))) where
  toFun q := match q with
    | .stop _ => .inl ()
    | .split childrenCuts => .inr childrenCuts
  invFun q := match q with
    | .inl _ => .stop (.branch a n children)
    | .inr childrenCuts => .split childrenCuts
  left_inv q := by cases q <;> rfl
  right_inv q := by cases q with
    | inl u => cases u; rfl
    | inr qs => rfl

/-- Finiteness of all admissible recursive cuts, not merely a sampled cut list. -/
@[instance_reducible]
noncomputable def cutFintype : (t : Tree A) → Fintype (Cut t)
  | .leaf a => Fintype.ofEquiv Unit (leafCutEquiv a).symm
  | .branch a n children =>
      letI : ∀ i, Fintype (Cut (children i)) := fun i => cutFintype (children i)
      Fintype.ofEquiv (Unit ⊕ (∀ i, Cut (children i)))
        (branchCutEquiv a n children).symm

noncomputable instance (t : Tree A) : Fintype (Cut t) := cutFintype t

/-- Arbitrary criteria need not be additive for finite attainment. -/
theorem arbitrary_objective_minimum (t : Tree A) (J : Cut t → ℝ) :
    ∃ q : Cut t, ∀ r : Cut t, J q ≤ J r := by
  classical
  obtain ⟨q, _, hq⟩ := KomorebiPaperV.finite_minimum J Finset.univ
    ⟨Cut.stop t, Finset.mem_univ _⟩
  exact ⟨q, fun r => hq r (Finset.mem_univ _)⟩

theorem strict_minimum_positive_gap (t : Tree A) (J : Cut t → ℝ) (q : Cut t)
    (hother : ∃ r : Cut t, r ≠ q) (hstrict : ∀ r : Cut t, r ≠ q → J q < J r) :
    ∃ γ : ℝ, 0 < γ ∧ ∀ r : Cut t, r ≠ q → γ ≤ J r - J q := by
  classical
  obtain ⟨r, hr⟩ := hother
  obtain ⟨γ, hγ, hgap⟩ := KomorebiPaperV.positive_gap Finset.univ J q
    ⟨r, Finset.mem_erase.mpr ⟨hr, Finset.mem_univ _⟩⟩
    (fun s _ hs => hstrict s hs)
  exact ⟨γ, hγ, fun s hs => hgap s (Finset.mem_univ _) hs⟩

noncomputable def value (c : A → ℝ) : Tree A → ℝ
  | .leaf a => c a
  | .branch a _ children => min (c a) (∑ i, value c (children i))

/-- Specification-level selector. The exact Python implementation caches children.
This definition alone is NOT a formal bound on Lean evaluation time. -/
noncomputable def best (c : A → ℝ) : (t : Tree A) → Cut t
  | .leaf a => .stop (.leaf a)
  | .branch a n children =>
      if c a ≤ ∑ i, value c (children i) then .stop (.branch a n children)
      else .split (fun i => best c (children i))

theorem value_le_cost (c : A → ℝ) {t : Tree A} (q : Cut t) :
    value c t ≤ cutSum c q := by
  induction q with
  | stop t =>
    cases t with
    | leaf a => exact le_rfl
    | branch a n children => exact min_le_left _ _
  | split q ih =>
    exact le_trans (min_le_right _ _) (Finset.sum_le_sum (fun i _ => ih i))

theorem best_cost (c : A → ℝ) (t : Tree A) : cutSum c (best c t) = value c t := by
  induction t with
  | leaf a => rfl
  | branch a n children ih =>
    by_cases h : c a ≤ ∑ i, value c (children i)
    · simp [best, h, cutSum, label, value]
    · have h' : (∑ i, value c (children i)) ≤ c a := le_of_lt (lt_of_not_ge h)
      simp only [best, ite_eq_right h, cutSum, value, min_eq_right h']
      exact Finset.sum_congr rfl (fun i _ => ih i)

theorem best_is_global_minimum (c : A → ℝ) {t : Tree A} (q : Cut t) :
    cutSum c (best c t) ≤ cutSum c q := by
  rw [best_cost]
  exact value_le_cost c q

theorem best_preserves_synthesis [AddCommMonoid E] (p : A → E) (c : A → ℝ)
    (t : Tree A) (h : conserves p t) : cutSum p (best c t) = p (label t) :=
  cutSum_eq_root p (best c t) h

theorem stop_on_tie (c : A → ℝ) (a : A) (n : ℕ) (children : Fin (n + 1) → Tree A)
    (h : c a = ∑ i, value c (children i)) :
    best c (.branch a n children) = Cut.stop (.branch a n children) := by
  simp [best, le_of_eq h]

noncomputable def envelope (e : A → ℝ) : Tree A → ℝ
  | .leaf a => e a
  | .branch a _ children => max (e a) (∑ i, envelope e (children i))

theorem root_le_envelope (e : A → ℝ) (t : Tree A) : e (label t) ≤ envelope e t := by
  cases t with
  | leaf a => exact le_rfl
  | branch a n children => exact le_max_left _ _

theorem cost_le_envelope (e : A → ℝ) {t : Tree A} (q : Cut t) :
    cutSum e q ≤ envelope e t := by
  induction q with
  | stop t => exact root_le_envelope e t
  | split q ih =>
    exact le_trans (Finset.sum_le_sum (fun i _ => ih i)) (le_max_right _ _)

/-- The envelope is attained by a pruning, so it is the exact worst cut weight. -/
theorem envelope_attained (e : A → ℝ) (t : Tree A) :
    ∃ q : Cut t, cutSum e q = envelope e t := by
  classical
  induction t with
  | leaf a => exact ⟨.stop (.leaf a), rfl⟩
  | branch a n children ih =>
    by_cases h : (∑ i, envelope e (children i)) ≤ e a
    · exact ⟨.stop (.branch a n children), (max_eq_left h).symm⟩
    · choose q hq using ih
      refine ⟨.split q, ?_⟩
      change (∑ i, cutSum e (q i)) = max (e a) (∑ i, envelope e (children i))
      rw [max_eq_right (le_of_lt (lt_of_not_ge h))]
      exact Finset.sum_congr rfl (fun i _ => hq i)

theorem cut_perturbation (c d e : A → ℝ) (h : ∀ a, |d a - c a| ≤ e a)
    {t : Tree A} (q : Cut t) : |cutSum d q - cutSum c q| ≤ envelope e t := by
  induction q with
  | stop t => exact le_trans (h (label t)) (root_le_envelope e t)
  | @split a n children q ih =>
    change |(∑ i, cutSum d (q i)) - ∑ i, cutSum c (q i)| ≤ _
    calc
      _ = |∑ i, (cutSum d (q i) - cutSum c (q i))| := by rw [Finset.sum_sub_distrib]
      _ ≤ ∑ i, |cutSum d (q i) - cutSum c (q i)| := Finset.abs_sum_le_sum_abs _ _
      _ ≤ ∑ i, envelope e (children i) := Finset.sum_le_sum (fun i _ => ih i)
      _ ≤ envelope e (.branch a n children) := le_max_right _ _

theorem value_perturbation (c d e : A → ℝ) (h : ∀ a, |d a - c a| ≤ e a)
    (t : Tree A) : |value d t - value c t| ≤ envelope e t := by
  have hc := abs_le.mp (cut_perturbation c d e h (best c t))
  have hd := abs_le.mp (cut_perturbation c d e h (best d t))
  have hminc := value_le_cost c (best d t)
  have hmind := value_le_cost d (best c t)
  rw [best_cost c t] at hc
  rw [best_cost d t] at hd
  exact abs_le.mpr ⟨by linarith, by linarith⟩

theorem best_unchanged_of_gap (c d e : A → ℝ) (h : ∀ a, |d a - c a| ≤ e a)
    (t : Tree A) (γ : ℝ)
    (hgap : ∀ q : Cut t, q ≠ best c t → γ ≤ cutSum c q - cutSum c (best c t))
    (hmargin : 2 * envelope e t < γ) : best d t = best c t := by
  by_contra hne
  have hfirst := abs_le.mp (cut_perturbation c d e h (best c t))
  have hsecond := abs_le.mp (cut_perturbation c d e h (best d t))
  have hsep := hgap (best d t) hne
  have hmin := best_is_global_minimum d (best c t)
  linarith

/-- Logical bottom-up comparison recurrence, excluding arithmetic and cut copying. -/
def comparisonCount : Tree A → ℕ
  | .leaf _ => 0
  | .branch _ _ children => 1 + ∑ i, comparisonCount (children i)

def internalNodes : Tree A → ℕ
  | .leaf _ => 0
  | .branch _ _ children => (∑ i, internalNodes (children i)) + 1

theorem one_comparison_per_internal_node (t : Tree A) : comparisonCount t = internalNodes t := by
  induction t with
  | leaf a => rfl
  | branch a n children ih =>
    dsimp [comparisonCount, internalNodes]
    rw [Finset.sum_congr rfl (fun i _ => ih i)]
    omega

/-- Probability is transferred from a joint local-error event by set inclusion. -/
theorem selector_probability {Ω : Type*} [MeasurableSpace Ω]
    (μ : MeasureTheory.Measure Ω) (good : Set Ω) (δ : ENNReal)
    (c e : A → ℝ) (d : Ω → A → ℝ) (t : Tree A) (γ : ℝ)
    (hgood : ∀ ω ∈ good, ∀ a, |d ω a - c a| ≤ e a)
    (hgap : ∀ q : Cut t, q ≠ best c t → γ ≤ cutSum c q - cutSum c (best c t))
    (hmargin : 2 * envelope e t < γ) (hprob : 1 - δ ≤ μ good) :
    1 - δ ≤ μ {ω | best (d ω) t = best c t} := by
  apply hprob.trans
  apply MeasureTheory.measure_mono
  intro ω hω
  exact best_unchanged_of_gap c (d ω) e (hgood ω hω) t γ hgap hmargin

end KomorebiPaperV.FiniteAdaptive
