import KomorebiLSM.PositivePackets
import KomorebiLSM.TestCones

/-! P39: nonnegative coefficient witnesses are constructed from invariance of
an actual finitely generated cone. The synthesis map need not be injective. -/
set_option autoImplicit false
namespace Komorebi.LSM.PositiveLift
open scoped BigOperators
open FiniteInstruments FiniteBayes
variable {E J : Type*} [AddCommGroup E] [Module ℝ E] [Fintype J] [DecidableEq J]

noncomputable def hull (V : (J → ℝ) →ₗ[ℝ] E) : Set E :=
  {x | ∃ a : J → ℝ, (∀ j, 0 ≤ a j) ∧ V a = x}

noncomputable def generator (V : (J → ℝ) →ₗ[ℝ] E) (j : J) : E := V (pointMass j)

noncomputable def normalizedHull (V : (J → ℝ) →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) : Set E :=
  {x | x ∈ hull V ∧ l x = 1}

omit [DecidableEq J] in
theorem normalized_mass (V : (J → ℝ) →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (hn : l.comp V = mass) (a : J → ℝ) : l (V a) = ∑ j, a j := by
  simpa only [LinearMap.comp_apply,mass_apply] using
    congrArg (fun F : (J → ℝ) →ₗ[ℝ] ℝ => F a) hn

theorem mass_generator (V : (J → ℝ) →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (hn : l.comp V = mass) (j : J) : l (generator V j) = 1 := by
  simpa only [generator,← mass_apply,mass_pointMass] using normalized_mass V l hn (pointMass j)

theorem generator_mem (V : (J → ℝ) →ₗ[ℝ] E) (j : J) : generator V j ∈ hull V :=
  ⟨pointMass j,(point_prior j).1,rfl⟩

omit [Fintype J] [DecidableEq J] in
theorem hull_zero (V : (J → ℝ) →ₗ[ℝ] E) : (0 : E) ∈ hull V :=
  ⟨0,fun _ => le_rfl,map_zero V⟩

omit [Fintype J] [DecidableEq J] in
theorem hull_add (V : (J → ℝ) →ₗ[ℝ] E) {x y : E} (hx : x ∈ hull V) (hy : y ∈ hull V) :
    x+y ∈ hull V := by
  obtain ⟨a,ha,rfl⟩ := hx
  obtain ⟨b,hb,rfl⟩ := hy
  exact ⟨a+b,fun j => add_nonneg (ha j) (hb j),map_add V a b⟩

omit [Fintype J] [DecidableEq J] in
theorem hull_smul (V : (J → ℝ) →ₗ[ℝ] E) {c : ℝ} (hc : 0 ≤ c)
    {x : E} (hx : x ∈ hull V) : c • x ∈ hull V := by
  obtain ⟨a,ha,rfl⟩ := hx
  exact ⟨c • a,fun j => mul_nonneg hc (ha j),map_smul V c a⟩

omit [Fintype J] [DecidableEq J] in
theorem hull_convex (V : (J → ℝ) →ₗ[ℝ] E) : Convex ℝ (hull V) := by
  intro x hx y hy a b ha hb _
  exact hull_add V (hull_smul V ha hx) (hull_smul V hb hy)

omit [DecidableEq J] in
theorem hull_mass_nonneg (V : (J → ℝ) →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (hn : l.comp V = mass) {x : E} (hx : x ∈ hull V) : 0 ≤ l x := by
  obtain ⟨a,ha,rfl⟩ := hx
  rw [normalized_mass V l hn]
  exact Finset.sum_nonneg (fun j _ => ha j)

omit [DecidableEq J] in
theorem hull_mass_zero (V : (J → ℝ) →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (hn : l.comp V = mass) {x : E} (hx : x ∈ hull V) (hm : l x = 0) : x = 0 := by
  obtain ⟨a,ha,rfl⟩ := hx
  rw [normalized_mass V l hn] at hm
  have he : a = 0 := by
    funext j
    exact (Finset.sum_eq_zero_iff_of_nonneg (fun j _ => ha j)).mp hm j (Finset.mem_univ j)
  simp [he]

omit [DecidableEq J] in
theorem hull_strict_mass (V : (J → ℝ) →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (hn : l.comp V = mass) : PositivePackets.StrictMass (hull V) l := by
  intro x hx hne
  have hnonneg := hull_mass_nonneg V l hn hx
  have hmass : l x ≠ 0 := fun hm => hne (hull_mass_zero V l hn hx hm)
  exact lt_of_le_of_ne hnonneg (Ne.symm hmass)

omit [DecidableEq J] in
theorem hull_pointed (V : (J → ℝ) →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (hn : l.comp V = mass) {x : E} (hx : x ∈ hull V) (hmx : -x ∈ hull V) : x = 0 := by
  apply hull_mass_zero V l hn hx
  have h₁ := hull_mass_nonneg V l hn hx
  have h₂ := hull_mass_nonneg V l hn hmx
  rw [map_neg] at h₂
  exact le_antisymm (neg_nonneg.mp h₂) h₁

theorem synthesis_sum (V : (J → ℝ) →ₗ[ℝ] E) (a : J → ℝ) :
    V a = ∑ j, a j • generator V j := by
  conv_lhs => rw [vector_eq_sum_pointMass a]
  simp only [map_sum,map_smul,generator]

theorem hull_spans (V : (J → ℝ) →ₗ[ℝ] E) (hs : Function.Surjective V) :
    Submodule.span ℝ (hull V) = ⊤ := by
  apply top_unique
  intro x _
  obtain ⟨a,rfl⟩ := hs x
  rw [synthesis_sum]
  exact Submodule.sum_mem _ (fun j _ => Submodule.smul_mem _ _
    (Submodule.subset_span (generator_mem V j)))

omit [DecidableEq J] in
theorem normalizedHull_eq_prior_image (V : (J → ℝ) →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (hn : l.comp V = mass) : normalizedHull V l = V '' {a | IsPrior a} := by
  ext x
  constructor
  · rintro ⟨⟨a,ha,rfl⟩,hm⟩
    exact ⟨a,⟨ha,by simpa only [normalized_mass V l hn] using hm⟩,rfl⟩
  · rintro ⟨a,ha,rfl⟩
    exact ⟨⟨a,ha.1,rfl⟩,by simpa only [normalized_mass V l hn] using ha.2⟩

/-- Images of the finitely many generators suffice for invariance of the whole cone. -/
theorem invariant_iff_generators (V : (J → ℝ) →ₗ[ℝ] E) (B : E →ₗ[ℝ] E) :
    (∀ x ∈ hull V, B x ∈ hull V) ↔ ∀ j, B (generator V j) ∈ hull V := by
  constructor
  · intro h j; exact h _ (generator_mem V j)
  · intro h x hx
    obtain ⟨a,ha,rfl⟩ := hx
    rw [synthesis_sum,map_sum]
    have hsum : ∀ t : Finset J, (∑ j ∈ t, B (a j • generator V j)) ∈ hull V := by
      intro t
      induction t using Finset.induction_on with
      | empty => simpa using hull_zero V
      | @insert j t hj ih =>
        rw [Finset.sum_insert hj]
        apply hull_add V _ ih
        rw [map_smul]
        exact hull_smul V (ha j) (h j)
    simpa using hsum Finset.univ

/-- The nonnegative matrix is constructed column by column, not assumed. -/
theorem positive_lift_iff (V : (J → ℝ) →ₗ[ℝ] E) (B : E →ₗ[ℝ] E) :
    (∀ x ∈ hull V, B x ∈ hull V) ↔
      ∃ M : Matrix J J ℝ, (∀ i j, 0 ≤ M i j) ∧ B.comp V = V.comp M.mulVecLin := by
  classical
  constructor
  · intro hi
    have hg := (invariant_iff_generators V B).mp hi
    choose a ha he using hg
    let M : Matrix J J ℝ := fun i j => a j i
    refine ⟨M,fun i j => ha j i, ?_⟩
    apply LinearMap.ext
    intro x
    rw [vector_eq_sum_pointMass x]
    simp only [map_sum,map_smul]
    apply Finset.sum_congr rfl
    intro j _
    congr 1
    have hm : M.mulVecLin (pointMass j) = a j := by
      funext i
      change (∑ k, a k i * pointMass j k) = a j i
      simp [pointMass]
    simpa only [LinearMap.comp_apply,hm,generator] using (he j).symm
  · rintro ⟨M,hn,he⟩ x ⟨a,ha,rfl⟩
    refine ⟨M.mulVec a, (PositivePackets.orthant_preserving_iff M).mpr hn a ha, ?_⟩
    exact (congrArg (fun F : (J → ℝ) →ₗ[ℝ] E => F a) he).symm

section Instruments
variable {A O : Type*} [Fintype O]
variable (B : A × O → E →ₗ[ℝ] E) (V : (J → ℝ) →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
variable (hn : l.comp V = mass) (hm : ∀ a x, ∑ o, l (B (a,o) x) = l x)
variable (M : A × O → Matrix J J ℝ)
variable (he : ∀ s, (B s).comp V = V.comp (M s).mulVecLin)
include hn hm he

/-- Mass normalization is inherited by every nonnegative lift, even a redundant one. -/
theorem lifted_mass (a : A) (j : J) : ∑ o, ∑ i, M (a,o) i j = 1 := by
  have hc : ∀ o, l (B (a,o) (generator V j)) = ∑ i, M (a,o) i j := by
    intro o
    have he' := congrArg (fun F : (J → ℝ) →ₗ[ℝ] E => F (pointMass j)) (he (a,o))
    have hp : (M (a,o)).mulVecLin (pointMass j) = fun i => M (a,o) i j := by
      funext i
      change (∑ k, M (a,o) i k * pointMass j k) = M (a,o) i j
      simp [pointMass]
    change B (a,o) (generator V j) = V ((M (a,o)).mulVecLin (pointMass j)) at he'
    rw [he',hp,normalized_mass V l hn]
  calc
    ∑ o, ∑ i, M (a,o) i j = ∑ o, l (B (a,o) (generator V j)) :=
      Finset.sum_congr rfl (fun o _ => (hc o).symm)
    _ = l (generator V j) := hm a _
    _ = 1 := mass_generator V l hn j

noncomputable def liftedInstrument (hp : ∀ s i j, 0 ≤ M s i j) : Instrument J A O where
  matrix a o := M (a,o)
  nonneg a o i j := hp (a,o) i j
  mass_one := lifted_mass B V l hn hm M he

omit hn hm [DecidableEq J] [Fintype O] in
theorem lifted_word (w : List (A × O)) (a : J → ℝ) :
    wordAction B w (V a) = V (wordAction (fun s => (M s).mulVecLin) w a) := by
  have hw := word_intertwining (fun s => (M s).mulVecLin) B V he w
  exact congrArg (fun F : (J → ℝ) →ₗ[ℝ] E => F a) hw

omit hm in
theorem lifted_word_probability (w : List (A × O)) (a : J → ℝ) :
    l (wordAction B w (V a)) = mass (wordAction (fun s => (M s).mulVecLin) w a) := by
  rw [lifted_word B V M he]
  exact congrArg (fun F : (J → ℝ) →ₗ[ℝ] ℝ => F _) hn

/-- All word probabilities are those of the constructed nonnegative instrument. -/
theorem finite_positive_lift_certificate (hp : ∀ s i j, 0 ≤ M s i j)
    (a₀ : J → ℝ) (ha₀ : IsPrior a₀) :
    (∀ a j, ∑ o, ∑ i, M (a,o) i j = 1) ∧
    (∀ w, l (wordAction B w (V a₀)) =
      mass (wordAction (liftedInstrument B V l hn hm M he hp).branch w a₀)) ∧
    (∀ w, 0 ≤ l (wordAction B w (V a₀)) ∧ l (wordAction B w (V a₀)) ≤ 1) := by
  refine ⟨lifted_mass B V l hn hm M he,?_,?_⟩
  · intro w; exact lifted_word_probability B V l hn M he w a₀
  · intro w
    rw [lifted_word_probability B V l hn M he]
    exact (liftedInstrument B V l hn hm M he hp).word_probability w a₀ ha₀

end Instruments
end Komorebi.LSM.PositiveLift
