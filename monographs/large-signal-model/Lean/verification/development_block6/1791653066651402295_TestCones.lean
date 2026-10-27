import KomorebiLSM.FiniteInstrument
import Mathlib.Analysis.Convex.Basic

/-! P38: finite test hierarchies and the all-test cone. The stopping condition
is equality of sets of states, not successful testing of finitely many states. -/
set_option autoImplicit false
namespace Komorebi.LSM.TestDomains
open scoped BigOperators
open FiniteInstruments
variable {E S : Type*} [AddCommGroup E] [Module ℝ E]

noncomputable def observe (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) :
    E →ₗ[ℝ] (List S → ℝ) := LinearMap.pi (fun w => l.comp (wordAction B w))

@[simp] theorem observe_apply (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (x : E) (w : List S) : observe B l x w = l (wordAction B w x) := rfl

noncomputable def testLevel (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) (h : ℕ) : Set E :=
  {x | ∀ w, w.length ≤ h → 0 ≤ observe B l x w}

noncomputable def allTests (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) : Set E :=
  {x | ∀ w, 0 ≤ observe B l x w}

noncomputable def base (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) : Set E :=
  {x | x ∈ allTests B l ∧ l x = 1}

theorem allTests_zero (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) :
    (0 : E) ∈ allTests B l := by intro w; simp

theorem allTests_add (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    {x y : E} (hx : x ∈ allTests B l) (hy : y ∈ allTests B l) :
    x+y ∈ allTests B l := by
  intro w
  simpa only [map_add,Pi.add_apply] using add_nonneg (hx w) (hy w)

theorem allTests_smul (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    {c : ℝ} (hc : 0 ≤ c) {x : E} (hx : x ∈ allTests B l) :
    c • x ∈ allTests B l := by
  intro w
  simpa only [map_smul,Pi.smul_apply,smul_eq_mul] using mul_nonneg hc (hx w)

theorem allTests_convex (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) :
    Convex ℝ (allTests B l) := by
  intro x hx y hy a b ha hb _
  exact allTests_add B l (allTests_smul B l ha hx) (allTests_smul B l hb hy)

theorem base_convex (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) :
    Convex ℝ (base B l) := by
  intro x hx y hy a b ha hb hab
  refine ⟨allTests_convex B l hx.1 hy.1 ha hb hab, ?_⟩
  simpa only [map_add,map_smul,smul_eq_mul,hx.2,hy.2,mul_one] using hab

theorem allTests_invariant (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (s : S) {x : E} (hx : x ∈ allTests B l) : B s x ∈ allTests B l := by
  intro w
  exact hx (s::w)

theorem allTests_word (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (w : List S) {x : E} (hx : x ∈ allTests B l) : wordAction B w x ∈ allTests B l := by
  induction w generalizing x with
  | nil => exact hx
  | cons s w ih => exact ih (allTests_invariant B l s hx)

theorem allTests_mass_nonneg (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    {x : E} (hx : x ∈ allTests B l) : 0 ≤ l x := hx []

theorem testLevel_zero (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) :
    testLevel B l 0 = {x | 0 ≤ l x} := by
  ext x
  constructor
  · intro hx; exact hx [] (by simp)
  · intro hx w hw
    have he : w = [] := List.length_eq_zero_iff.mp (Nat.eq_zero_of_le_zero hw)
    subst w
    exact hx

/-- One more test step is a preimage refinement by every branch. -/
theorem testLevel_succ (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) (h : ℕ) :
    testLevel B l (h+1) = testLevel B l h ∩ ⋂ s, (B s) ⁻¹' testLevel B l h := by
  ext x
  constructor
  · intro hx
    refine ⟨fun w hw => hx w (hw.trans (Nat.le_succ h)), ?_⟩
    simp only [Set.mem_iInter,Set.mem_preimage]
    intro s w hw
    exact hx (s::w) (by simpa using Nat.succ_le_succ hw)
  · rintro ⟨hx,hs⟩ w hw
    cases w with
    | nil => exact hx [] (Nat.zero_le h)
    | cons s w =>
      have hmem := Set.mem_iInter.mp hs s
      exact hmem w (by simpa using hw)

theorem testLevel_antitone (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) :
    Antitone (testLevel B l) := by
  intro h k hhk x hx w hw
  exact hx w (hw.trans hhk)

theorem allTests_eq_inter (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) :
    allTests B l = ⋂ h, testLevel B l h := by
  ext x
  simp only [Set.mem_iInter]
  constructor
  · intro hx h w _; exact hx w
  · intro hx w; exact hx w.length w le_rfl

/-- Any invariant set with nonnegative mass is included in the all-test cone. -/
theorem allTests_greatest (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (C : Set E) (hm : ∀ x ∈ C, 0 ≤ l x)
    (hi : ∀ s x, x ∈ C → B s x ∈ C) : C ⊆ allTests B l := by
  intro x hx w
  have hw : wordAction B w x ∈ C := by
    induction w generalizing x with
    | nil => exact hx
    | cons s w ih => exact ih _ (hi s x hx)
  exact hm _ hw

/-- Exact equality of successive constraints is an all-horizon certificate. -/
theorem testLevel_stopping (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) (h : ℕ)
    (he : testLevel B l (h+1) = testLevel B l h) :
    testLevel B l h = allTests B l := by
  apply Set.Subset.antisymm
  · apply allTests_greatest B l (testLevel B l h)
    · intro x hx; exact hx [] (Nat.zero_le h)
    · intro s x hx
      have hx' : x ∈ testLevel B l (h+1) := by rwa [he]
      rw [testLevel_succ] at hx'
      exact Set.mem_iInter.mp hx'.2 s
  · intro x hx w _; exact hx w

/-- Observability eliminates the common kernel of all test half-spaces. -/
theorem allTests_pointed (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (ho : Function.Injective (observe B l)) {x : E}
    (hx : x ∈ allTests B l) (hn : -x ∈ allTests B l) : x = 0 := by
  apply ho
  funext w
  have hh := hn w
  simp only [map_neg,Pi.neg_apply] at hh
  have hz : observe B l x w = 0 := le_antisymm (neg_nonneg.mp hh) (hx w)
  simpa using hz

/-- Reachable cone vectors span whenever the realization is reachable. -/
theorem allTests_spans (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) (x₀ : E)
    (h₀ : x₀ ∈ allTests B l)
    (hr : Submodule.span ℝ (Set.range (fun w => wordAction B w x₀)) = ⊤) :
    Submodule.span ℝ (allTests B l) = ⊤ := by
  apply top_unique
  rw [← hr]
  apply Submodule.span_mono
  rintro _ ⟨w,rfl⟩
  exact allTests_word B l w h₀

section Causal
variable {A O : Type*} [Fintype O]
variable (B : A × O → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
variable (hm : ∀ a x, ∑ o, l (B (a,o) x) = l x)

/-- Causal normalization extends to every prefix and every linear state. -/
theorem test_sum_next (x : E) (w : List (A × O)) (a : A) :
    ∑ o, observe B l x (w ++ [(a,o)]) = observe B l x w := by
  simp only [observe_apply,wordAction_append,wordAction_cons,wordAction_nil,
    LinearMap.id_comp,LinearMap.comp_apply]
  exact hm a (wordAction B w x)

theorem test_next_le {x : E} (hx : x ∈ allTests B l) (w : List (A × O)) (s : A × O) :
    observe B l x (w ++ [s]) ≤ observe B l x w := by
  rw [← test_sum_next B l hm x w s.1]
  exact Finset.single_le_sum (fun o _ => hx (w ++ [(s.1,o)])) (Finset.mem_univ s.2)

theorem test_extension_le {x : E} (hx : x ∈ allTests B l) (w t : List (A × O)) :
    observe B l x (w ++ t) ≤ observe B l x w := by
  induction t generalizing w with
  | nil => simp
  | cons s t ih =>
    have h₁ := ih (w ++ [s])
    have h₂ := test_next_le B l hm hx w s
    simpa only [List.append_assoc,List.singleton_append] using h₁.trans h₂

theorem test_le_mass {x : E} (hx : x ∈ allTests B l) (w : List (A × O)) :
    observe B l x w ≤ l x := by
  simpa only [List.nil_append,observe_apply,wordAction_nil,LinearMap.id_apply] using
    test_extension_le B l hm hx [] w

theorem allTests_strict_mass (ho : Function.Injective (observe B l)) {x : E}
    (hx : x ∈ allTests B l) (hne : x ≠ 0) : 0 < l x := by
  have hnonneg := allTests_mass_nonneg B l hx
  by_contra hn
  have he : l x = 0 := le_antisymm (le_of_not_gt hn) hnonneg
  apply hne
  apply ho
  funext w
  have hl := test_le_mass B l hm hx w
  have hz : observe B l x w = 0 := le_antisymm (he ▸ hl) (hx w)
  simpa using hz

theorem base_test_bounds {x : E} (hx : x ∈ base B l) (w : List (A × O)) :
    0 ≤ observe B l x w ∧ observe B l x w ≤ 1 := by
  exact ⟨hx.1 w, hx.2 ▸ test_le_mass B l hm hx.1 w⟩

end Causal

/-- Positive-evidence normalization preserves the full test domain. -/
theorem base_posterior (B : S → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    {x : E} (hx : x ∈ allTests B l) (s : S) (hp : 0 < l (B s x)) :
    normalize l (B s x) ∈ base B l := by
  exact ⟨allTests_smul B l (inv_nonneg.mpr hp.le) (allTests_invariant B l s hx),
    normalize_mass l _ (ne_of_gt hp)⟩

end Komorebi.LSM.TestDomains
