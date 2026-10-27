import KomorebiPaperVI.FiniteBayes

/-! Author: Komorebi P. Literal finite fibers, zero-mass packets, and profile partitions. -/
namespace KomorebiPaperVI.Coarsening
open KomorebiPaperVI.FiniteBayes
open scoped BigOperators
variable {I A : Type*} [Fintype I] [Fintype A] [DecidableEq A]

def coarsen (f : I → A) (p : I → ℝ) (a : A) : ℝ :=
  ∑ i, if f i = a then p i else 0

noncomputable def effective (f : I → A) (p l : I → ℝ) (a : A) : ℝ :=
  coarsen f (fun i => l i*p i) a / coarsen f p a

theorem coarsen_mass (f : I → A) (p : I → ℝ) : mass (coarsen f p) = mass p := by
  simp only [mass, coarsen]
  rw [Finset.sum_comm]
  simp

omit [Fintype A] in
theorem coarsen_nonnegative (f : I → A) (p : I → ℝ) (hp : ∀ i, 0 ≤ p i) (a : A) :
    0 ≤ coarsen f p a := by
  apply Finset.sum_nonneg
  intro i _
  split_ifs
  · exact hp i
  · exact le_rfl

theorem coarsen_probability (f : I → A) (p : I → ℝ) (hp : IsProbability p) :
    IsProbability (coarsen f p) :=
  ⟨coarsen_nonnegative f p hp.1, (coarsen_mass f p).trans hp.2⟩

omit [Fintype A] in
theorem coarsen_div (f : I → A) (p : I → ℝ) (z : ℝ) :
    coarsen f (fun i => p i/z) = fun a => coarsen f p a/z := by
  funext a
  simp only [coarsen, Finset.sum_div]
  apply Finset.sum_congr rfl
  intro i _
  split_ifs <;> simp

omit [Fintype A] in
theorem coarsen_posterior (f : I → A) (p l : I → ℝ) :
    coarsen f (update p l) = fun a => coarsen f (fun i => l i*p i) a/evidence p l :=
  coarsen_div f _ _

omit [Fintype A] in
theorem zero_packet_component (f : I → A) (p : I → ℝ) (hp : ∀ i, 0 ≤ p i)
    (a : A) (ha : coarsen f p a = 0) (i : I) (hi : f i=a) : p i=0 := by
  have he : (if f i=a then p i else 0) ≤ coarsen f p a :=
    Finset.single_le_sum (f := fun j => if f j=a then p j else 0)
      (fun j _ => by split_ifs; exact hp j; exact le_rfl) (Finset.mem_univ i)
  rw [ite_eq_left hi, ha] at he
  exact le_antisymm he (hp i)

omit [Fintype A] in
theorem zero_packet_weighted (f : I → A) (p l : I → ℝ) (hp : ∀ i, 0 ≤ p i)
    (a : A) (ha : coarsen f p a=0) : coarsen f (fun i => l i*p i) a=0 := by
  apply Finset.sum_eq_zero
  intro i _
  by_cases hi : f i=a
  · simp [hi, zero_packet_component f p hp a ha i hi]
  · simp [hi]

omit [Fintype A] in
theorem effective_weight (f : I → A) (p l : I → ℝ) (hp : ∀ i, 0 ≤ p i) (a : A) :
    effective f p l a*coarsen f p a = coarsen f (fun i => l i*p i) a := by
  by_cases ha : coarsen f p a=0
  · simp [effective, ha, zero_packet_weighted f p l hp a ha]
  · exact div_mul_cancel₀ _ ha

omit [Fintype A] in
theorem effective_nonnegative (f : I → A) (p l : I → ℝ) (hp : ∀ i, 0 ≤ p i)
    (hl : ∀ i, 0 ≤ l i) (a : A) : 0 ≤ effective f p l a :=
  div_nonneg (coarsen_nonnegative f _ (fun i => mul_nonneg (hl i) (hp i)) a)
    (coarsen_nonnegative f p hp a)

theorem effective_evidence (f : I → A) (p l : I → ℝ) (hp : ∀ i, 0 ≤ p i) :
    evidence (coarsen f p) (effective f p l) = evidence p l := by
  simp only [evidence, effective_weight f p l hp]
  exact coarsen_mass f _

theorem effective_factorization (f : I → A) (p l : I → ℝ) (hp : ∀ i, 0 ≤ p i) :
    coarsen f (update p l) = update (coarsen f p) (effective f p l) := by
  rw [coarsen_posterior]
  funext a
  simp only [update, effective_weight f p l hp, effective_evidence f p l hp]

omit [Fintype A] in
theorem packet_reconstruction_point (f : I → A) (w : I → ℝ) (hw : ∀ i, 0 ≤ w i)
    (i : I) :
    (coarsen f w (f i)/mass w)*(w i/coarsen f w (f i)) = normalize w i := by
  by_cases ha : coarsen f w (f i)=0
  · have hi := zero_packet_component f w hw (f i) ha i rfl
    simp [ha, hi, FiniteBayes.normalize]
  · dsimp [FiniteBayes.normalize]
    field_simp

theorem packet_reconstruction (f : I → A) (w : I → ℝ) (hw : ∀ i, 0 ≤ w i) (i : I) :
    (∑ a, (coarsen f w a/mass w)*(if f i=a then w i/coarsen f w a else 0)) =
      normalize w i := by
  simpa [mul_ite] using
    packet_reconstruction_point f w hw i

omit [Fintype A] in
theorem blockwise_weight (f : I → A) (p : I → ℝ) (k : A → ℝ) (a : A) :
    coarsen f (fun i => k (f i)*p i) a = k a*coarsen f p a := by
  simp only [coarsen, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro i _
  split_ifs with hi
  · rw [hi]
  · simp

theorem blockwise_evidence (f : I → A) (p : I → ℝ) (k : A → ℝ) :
    evidence p (k ∘ f) = evidence (coarsen f p) k := by
  have h := coarsen_mass f (fun i => k (f i)*p i)
  simpa only [mass, blockwise_weight, evidence, Function.comp_apply] using h.symm

theorem blockwise_sufficiency (f : I → A) (p : I → ℝ) (k : A → ℝ) :
    coarsen f (update p (k ∘ f)) = update (coarsen f p) k := by
  rw [coarsen_posterior]
  funext a
  simp only [Function.comp_apply, blockwise_weight, blockwise_evidence, update]

theorem scaled_blockwise_sufficiency (f : I → A) (p : I → ℝ) (k : A → ℝ)
    (c : ℝ) (hc : c ≠ 0) (hz : evidence p (k ∘ f) ≠ 0) :
    coarsen f (update p (fun i => c*k (f i))) = update (coarsen f p) k := by
  have he := posterior_scale p (k ∘ f) c hc hz
  simp only [Function.comp_apply] at he
  rw [he]
  exact blockwise_sufficiency f p k

omit [DecidableEq A] in
theorem one_packet_posterior (p k : A → ℝ) [Unique A] (hz : evidence p k ≠ 0) (a : A) :
    update p k a=1 := by
  have ha : a = default := Subsingleton.elim a default
  simpa [mass, ha] using posterior_mass p k hz

end KomorebiPaperVI.Coarsening

namespace KomorebiPaperVI.Profiles
variable {I Y A : Type*}

def sameProfile (l : Y → I → ℝ) (i j : I) : Prop := ∀ y, l y i=l y j

theorem profile_equivalence (l : Y → I → ℝ) : Equivalence (sameProfile l) := by
  refine ⟨?_, ?_, ?_⟩
  · intro i y; rfl
  · intro i j h y; exact (h y).symm
  · intro i j k h h' y; exact (h y).trans (h' y)

theorem likelihood_resolving_iff_refines (l : Y → I → ℝ) (f : I → A) :
    (∀ y i j, f i=f j → l y i=l y j) ↔ (∀ i j, f i=f j → sameProfile l i j) := by
  constructor
  · intro h i j hij y; exact h y i j hij
  · intro h y i j hij; exact h i j hij y

theorem exact_profile_factorization (l : Y → I → ℝ) (y : Y) (i : I) :
    (fun profile : Y → ℝ => profile y) (fun z => l z i) = l y i := rfl

end KomorebiPaperVI.Profiles
