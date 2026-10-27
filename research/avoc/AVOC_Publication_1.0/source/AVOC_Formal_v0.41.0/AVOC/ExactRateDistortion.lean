import AVOC.RateDistortionLower
import Mathlib.Data.Finset.Max
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

namespace Komorebi.AVOC

universe u v

/-- The finite states carried by a context code. -/
def valueFiberStates
    {S : Type u} [Fintype S]
    {Z : Type v} [DecidableEq Z]
    (φ : S → Z) (z : Z) : Finset S :=
  Finset.univ.filter (fun s => φ s = z)

/-- The finite set of scalar values carried by a context code. -/
def valueFiberValues
    {S : Type u} [Fintype S]
    {Z : Type v} [DecidableEq Z]
    (φ : S → Z) (V : S → ℚ) (z : Z) : Finset ℚ :=
  (valueFiberStates φ z).image V

/-- A code is fiber-diameter feasible at tolerance `η` when no two states it
merges differ in value by more than `2η`. -/
def ValueFiberDiameterBound
    {S : Type u} {Z : Type v}
    (φ : S → Z) (V : S → ℚ) (η : ℚ) : Prop :=
  ∀ s t, φ s = φ t → |V s - V t| ≤ 2 * η

/-- Every accurate value decoder necessarily has bounded value diameter on each
context fiber. -/
theorem valueApproximation_implies_fiberDiameter
    {S : Type u} {Z : Type v}
    (φ : S → Z) (V : S → ℚ) (Vbar : Z → ℚ) (η : ℚ)
    (h : ValueApproximation φ V Vbar η) :
    ValueFiberDiameterBound φ V η := by
  intro s t hst
  have hs := h s
  have ht := h t
  have htri : |V s - V t| ≤
      |V s - Vbar (φ s)| + |Vbar (φ t) - V t| := by
    calc
      |V s - V t|
          = |(V s - Vbar (φ s)) + (Vbar (φ t) - V t)| := by
              rw [hst]
              ring_nf
      _ ≤ |V s - Vbar (φ s)| + |Vbar (φ t) - V t| := abs_add_le _ _
  have ht' : |Vbar (φ t) - V t| ≤ η := by
    rw [abs_sub_comm]
    exact ht
  linarith

/-- Every state contributes its value to the value set of its own fiber. -/
theorem mem_valueFiberValues_self
    {S : Type u} [Fintype S]
    {Z : Type v} [DecidableEq Z]
    (φ : S → Z) (V : S → ℚ) (s : S) :
    V s ∈ valueFiberValues φ V (φ s) := by
  apply Finset.mem_image.mpr
  refine ⟨s, ?_, rfl⟩
  simp [valueFiberStates]

/-- The midpoint of the minimum and maximum value in a nonempty code fiber;
empty codes are assigned `0` because they are unreachable. -/
noncomputable def midpointValueDecoder
    {S : Type u} [Fintype S]
    {Z : Type v} [DecidableEq Z]
    (φ : S → Z) (V : S → ℚ) (z : Z) : ℚ :=
  if h : (valueFiberValues φ V z).Nonempty then
    ((valueFiberValues φ V z).min' h + (valueFiberValues φ V z).max' h) / 2
  else 0

/-- A finite fiber of diameter at most `2η` is reconstructed to tolerance `η`
by the midpoint of its extreme values. -/
theorem midpointValueDecoder_accurate
    {S : Type u} [Fintype S]
    {Z : Type v} [DecidableEq Z]
    (φ : S → Z) (V : S → ℚ) (η : ℚ)
    (hdiam : ValueFiberDiameterBound φ V η) :
    ValueApproximation φ V (midpointValueDecoder φ V) η := by
  intro s
  let vals := valueFiberValues φ V (φ s)
  have hsval : V s ∈ vals := by
    simpa [vals] using mem_valueFiberValues_self φ V s
  have hne : vals.Nonempty := ⟨V s, hsval⟩
  let mn : ℚ := vals.min' hne
  let mx : ℚ := vals.max' hne
  have hmnmem : mn ∈ vals := by
    simpa [mn] using vals.min'_mem hne
  have hmxmem : mx ∈ vals := by
    simpa [mx] using vals.max'_mem hne
  have hmns : mn ≤ V s := by
    simpa [mn] using Finset.min'_le vals (V s) hsval
  have hsmx : V s ≤ mx := by
    simpa [mx] using Finset.le_max' vals (V s) hsval
  rcases Finset.mem_image.mp hmnmem with ⟨smin, hsminFiber, hsminVal⟩
  rcases Finset.mem_image.mp hmxmem with ⟨smax, hsmaxFiber, hsmaxVal⟩
  have hsminCode : φ smin = φ s := by
    exact (Finset.mem_filter.mp hsminFiber).2
  have hsmaxCode : φ smax = φ s := by
    exact (Finset.mem_filter.mp hsmaxFiber).2
  have hsminmaxCode : φ smin = φ smax := hsminCode.trans hsmaxCode.symm
  have hdiam' := hdiam smin smax hsminmaxCode
  have hmnmx : mn ≤ mx := le_trans hmns hsmx
  have hspan : mx - mn ≤ 2 * η := by
    have habs : |mn - mx| ≤ 2 * η := by
      simpa [hsminVal, hsmaxVal] using hdiam'
    rw [abs_of_nonpos (sub_nonpos.mpr hmnmx)] at habs
    linarith
  have hmid :
      |V s - (mn + mx) / 2| ≤ η := by
    rw [abs_le]
    constructor <;> linarith
  simpa [midpointValueDecoder, vals, hne, mn, mx] using hmid

/-- Exact finite scalar rate-distortion characterization for a fixed context
partition: an `η`-accurate decoder exists exactly when every context fiber has
value diameter at most `2η`. -/
theorem exists_valueApproximation_iff_fiberDiameter
    {S : Type u} [Fintype S]
    {Z : Type v} [DecidableEq Z]
    (φ : S → Z) (V : S → ℚ) (η : ℚ) :
    (∃ Vbar : Z → ℚ, ValueApproximation φ V Vbar η) ↔
      ValueFiberDiameterBound φ V η := by
  constructor
  · rintro ⟨Vbar, h⟩
    exact valueApproximation_implies_fiberDiameter φ V Vbar η h
  · intro hdiam
    exact ⟨midpointValueDecoder φ V,
      midpointValueDecoder_accurate φ V η hdiam⟩

/-- At zero distortion, the exact condition reduces to constancy of value on
context fibers. -/
theorem exists_exact_value_decoder_iff_fiber_constant
    {S : Type u} [Fintype S]
    {Z : Type v} [DecidableEq Z]
    (φ : S → Z) (V : S → ℚ) :
    (∃ Vbar : Z → ℚ, ValueApproximation φ V Vbar 0) ↔
      ∀ s t, φ s = φ t → V s = V t := by
  rw [exists_valueApproximation_iff_fiberDiameter φ V 0]
  constructor
  · intro h s t hst
    have hh := h s t hst
    simp only [mul_zero, abs_nonpos_iff] at hh
    linarith
  · intro h s t hst
    have := h s t hst
    simp [this]

end Komorebi.AVOC

namespace Komorebi.AVOC

universe u v

/-- A finite collection of scalar reconstruction centers covers the value
function to tolerance `η` when every raw value lies within `η` of one center. -/
def ValueCenterCover
    {S : Type u}
    (V : S → ℚ) (η : ℚ) (C : Finset ℚ) : Prop :=
  ∀ s, ∃ c ∈ C, |V s - c| ≤ η

/-- The centers used by any finite code space form a value cover. -/
theorem valueCenterCover_of_valueApproximation
    {S : Type u} {Z : Type v} [Fintype Z] [DecidableEq Z]
    (φ : S → Z) (V : S → ℚ) (Vbar : Z → ℚ) (η : ℚ)
    (h : ValueApproximation φ V Vbar η) :
    ValueCenterCover V η (Finset.univ.image Vbar) := by
  intro s
  refine ⟨Vbar (φ s), ?_, h s⟩
  simp

/-- A finite code space contributes no more distinct reconstruction centers
than it has codes. -/
theorem decoder_center_card_le_code_card
    {Z : Type v} [Fintype Z] [DecidableEq Z]
    (Vbar : Z → ℚ) :
    (Finset.univ.image Vbar).card ≤ Fintype.card Z := by
  simpa using Finset.card_image_le (s := (Finset.univ : Finset Z)) (f := Vbar)

/-- Every finite accurate code induces a center cover with no larger cardinality. -/
theorem finite_code_gives_center_cover_card_bound
    {S : Type u} {Z : Type v} [Fintype Z] [DecidableEq Z]
    (φ : S → Z) (V : S → ℚ) (Vbar : Z → ℚ) (η : ℚ)
    (h : ValueApproximation φ V Vbar η) :
    ∃ C : Finset ℚ,
      ValueCenterCover V η C ∧ C.card ≤ Fintype.card Z := by
  refine ⟨Finset.univ.image Vbar,
    valueCenterCover_of_valueApproximation φ V Vbar η h,
    decoder_center_card_le_code_card Vbar⟩

/-- Chosen center used to realize a finite value cover as a context code. -/
noncomputable def chosenCoverCenter
    {S : Type u}
    (V : S → ℚ) (η : ℚ) (C : Finset ℚ)
    (hcover : ValueCenterCover V η C) (s : S) : ℚ :=
  Classical.choose (hcover s)

/-- The chosen center belongs to the cover. -/
theorem chosenCoverCenter_mem
    {S : Type u}
    (V : S → ℚ) (η : ℚ) (C : Finset ℚ)
    (hcover : ValueCenterCover V η C) (s : S) :
    chosenCoverCenter V η C hcover s ∈ C :=
  (Classical.choose_spec (hcover s)).1

/-- The chosen center approximates its state value. -/
theorem chosenCoverCenter_accurate
    {S : Type u}
    (V : S → ℚ) (η : ℚ) (C : Finset ℚ)
    (hcover : ValueCenterCover V η C) (s : S) :
    |V s - chosenCoverCenter V η C hcover s| ≤ η :=
  (Classical.choose_spec (hcover s)).2

/-- Any finite center cover can itself be used as the exact finite context code
space. Thus every cover of cardinality `k` realizes an accurate code with
exactly `k` available code symbols. -/
theorem center_cover_gives_finite_code
    {S : Type u}
    (V : S → ℚ) (η : ℚ) (C : Finset ℚ)
    (hcover : ValueCenterCover V η C) :
    ∃ φ : S → {c // c ∈ C},
      ValueApproximation φ V (fun z : {c // c ∈ C} => (z : ℚ)) η := by
  let φ : S → {c // c ∈ C} := fun s =>
    ⟨chosenCoverCenter V η C hcover s,
      chosenCoverCenter_mem V η C hcover s⟩
  refine ⟨φ, ?_⟩
  intro s
  simpa [φ] using chosenCoverCenter_accurate V η C hcover s

/-- The code type produced from a center cover has exactly the cover's
cardinality. -/
theorem center_code_card_eq
    (C : Finset ℚ) :
    Fintype.card {c // c ∈ C} = C.card := by
  simp

/-- Exact finite scalar rate-distortion duality at the cardinality level:
finite context codes and finite radius-`η` center covers simulate one another
without increasing the number of code symbols / centers. -/
theorem finite_code_center_cover_cardinality_duality
    {S : Type u} {Z : Type v} [Fintype Z] [DecidableEq Z]
    (φ : S → Z) (V : S → ℚ) (Vbar : Z → ℚ) (η : ℚ)
    (h : ValueApproximation φ V Vbar η) :
    ∃ C : Finset ℚ,
      ValueCenterCover V η C ∧
      C.card ≤ Fintype.card Z ∧
      ∃ ψ : S → {c // c ∈ C},
        ValueApproximation ψ V (fun z : {c // c ∈ C} => (z : ℚ)) η := by
  obtain ⟨C, hcover, hcard⟩ :=
    finite_code_gives_center_cover_card_bound φ V Vbar η h
  obtain ⟨ψ, hψ⟩ := center_cover_gives_finite_code V η C hcover
  exact ⟨C, hcover, hcard, ψ, hψ⟩

end Komorebi.AVOC

namespace Komorebi.AVOC

universe u v

/-- A finite center cover with exactly `k` centers. -/
def HasValueCenterCoverCard
    {S : Type u}
    (V : S → ℚ) (η : ℚ) (k : ℕ) : Prop :=
  ∃ C : Finset ℚ, ValueCenterCover V η C ∧ C.card = k

/-- The set of raw values always covers itself at every nonnegative tolerance. -/
theorem raw_value_image_is_centerCover
    {S : Type u} [Fintype S]
    (V : S → ℚ) (η : ℚ) (hη : 0 ≤ η) :
    ValueCenterCover V η (Finset.univ.image V) := by
  intro s
  refine ⟨V s, by simp, ?_⟩
  simpa using hη

/-- Every finite value problem at nonnegative tolerance has some finite center
cover cardinality. -/
theorem exists_valueCenterCover_card
    {S : Type u} [Fintype S]
    (V : S → ℚ) (η : ℚ) (hη : 0 ≤ η) :
    ∃ k, HasValueCenterCoverCard V η k := by
  let C : Finset ℚ := Finset.univ.image V
  refine ⟨C.card, C, ?_, rfl⟩
  simpa [C] using raw_value_image_is_centerCover V η hη

/-- Exact minimum number of scalar reconstruction centers needed at tolerance
`η`. Since finite context codes and finite center covers are cardinality-dual,
this is also the exact minimum finite context-code cardinality. -/
noncomputable def exactValueCodeNumber
    {S : Type u} [Fintype S]
    (V : S → ℚ) (η : ℚ) (hη : 0 ≤ η) : ℕ := by
  classical
  exact Nat.find (exists_valueCenterCover_card V η hη)

/-- The minimum center-cover cardinality is attained. -/
theorem exactValueCodeNumber_spec
    {S : Type u} [Fintype S]
    (V : S → ℚ) (η : ℚ) (hη : 0 ≤ η) :
    HasValueCenterCoverCard V η (exactValueCodeNumber V η hη) := by
  classical
  simpa [exactValueCodeNumber] using
    (Nat.find_spec (exists_valueCenterCover_card V η hη))

/-- The exact code number is no larger than any finite center cover. -/
theorem exactValueCodeNumber_le_cover_card
    {S : Type u} [Fintype S]
    (V : S → ℚ) (η : ℚ) (hη : 0 ≤ η)
    (C : Finset ℚ) (hcover : ValueCenterCover V η C) :
    exactValueCodeNumber V η hη ≤ C.card := by
  classical
  unfold exactValueCodeNumber
  exact Nat.find_min' (exists_valueCenterCover_card V η hη) ⟨C, hcover, rfl⟩

/-- Every finite accurate context code has at least the exact scalar
rate-distortion number of available code symbols. -/
theorem exactValueCodeNumber_le_finite_code_card
    {S : Type u} [Fintype S]
    {Z : Type v} [Fintype Z] [DecidableEq Z]
    (φ : S → Z) (V : S → ℚ) (Vbar : Z → ℚ)
    (η : ℚ) (hη : 0 ≤ η)
    (h : ValueApproximation φ V Vbar η) :
    exactValueCodeNumber V η hη ≤ Fintype.card Z := by
  obtain ⟨C, hcover, hcard⟩ :=
    finite_code_gives_center_cover_card_bound φ V Vbar η h
  exact (exactValueCodeNumber_le_cover_card V η hη C hcover).trans hcard

/-- The exact minimum is not merely a lower bound: it is realized by a finite
context code whose type has exactly that many elements. -/
theorem exactValueCodeNumber_attained_by_context
    {S : Type u} [Fintype S]
    (V : S → ℚ) (η : ℚ) (hη : 0 ≤ η) :
    ∃ C : Finset ℚ,
      C.card = exactValueCodeNumber V η hη ∧
      ∃ φ : S → {c // c ∈ C},
        ValueApproximation φ V (fun z : {c // c ∈ C} => (z : ℚ)) η := by
  obtain ⟨C, hcover, hcard⟩ := exactValueCodeNumber_spec V η hη
  obtain ⟨φ, hφ⟩ := center_cover_gives_finite_code V η C hcover
  exact ⟨C, hcard, φ, hφ⟩

/-- Optimality sandwich: every finite accurate code has at least `N` symbols,
and an accurate code with exactly `N` symbols exists, where
`N = exactValueCodeNumber`. -/
theorem exact_finite_scalar_rate_distortion_optimality
    {S : Type u} [Fintype S]
    (V : S → ℚ) (η : ℚ) (hη : 0 ≤ η) :
    (∀ {Z : Type v} [Fintype Z] [DecidableEq Z]
      (φ : S → Z) (Vbar : Z → ℚ),
      ValueApproximation φ V Vbar η →
      exactValueCodeNumber V η hη ≤ Fintype.card Z) ∧
    (∃ C : Finset ℚ,
      C.card = exactValueCodeNumber V η hη ∧
      ∃ φ : S → {c // c ∈ C},
        ValueApproximation φ V (fun z : {c // c ∈ C} => (z : ℚ)) η) := by
  constructor
  · intro Z instF instD φ Vbar h
    exact exactValueCodeNumber_le_finite_code_card φ V Vbar η hη h
  · exact exactValueCodeNumber_attained_by_context V η hη

end Komorebi.AVOC

namespace Komorebi.AVOC

universe u

/-- A center cover valid at a smaller tolerance remains valid at every larger
tolerance. -/
theorem valueCenterCover_mono_tolerance
    {S : Type u}
    (V : S → ℚ) {η₁ η₂ : ℚ} (hη : η₁ ≤ η₂)
    (C : Finset ℚ) (hcover : ValueCenterCover V η₁ C) :
    ValueCenterCover V η₂ C := by
  intro s
  obtain ⟨c, hc, hdist⟩ := hcover s
  exact ⟨c, hc, hdist.trans hη⟩

/-- Allowing more scalar distortion can never increase the exact minimum
number of context symbols. -/
theorem exactValueCodeNumber_antitone_tolerance
    {S : Type u} [Fintype S]
    (V : S → ℚ) {η₁ η₂ : ℚ}
    (hη₁ : 0 ≤ η₁) (hη₂ : 0 ≤ η₂) (h12 : η₁ ≤ η₂) :
    exactValueCodeNumber V η₂ hη₂ ≤ exactValueCodeNumber V η₁ hη₁ := by
  obtain ⟨C, hcover₁, hcard⟩ := exactValueCodeNumber_spec V η₁ hη₁
  have hcover₂ := valueCenterCover_mono_tolerance V h12 C hcover₁
  calc
    exactValueCodeNumber V η₂ hη₂ ≤ C.card :=
      exactValueCodeNumber_le_cover_card V η₂ hη₂ C hcover₂
    _ = exactValueCodeNumber V η₁ hη₁ := hcard

/-- At every nonnegative tolerance, the exact code number is no larger than
the number of distinct raw values. -/
theorem exactValueCodeNumber_le_distinct_value_card
    {S : Type u} [Fintype S]
    (V : S → ℚ) (η : ℚ) (hη : 0 ≤ η) :
    exactValueCodeNumber V η hη ≤ (Finset.univ.image V).card := by
  exact exactValueCodeNumber_le_cover_card V η hη
    (Finset.univ.image V) (raw_value_image_is_centerCover V η hη)

/-- Every zero-distortion center cover contains every distinct raw value. -/
theorem raw_values_subset_zero_centerCover
    {S : Type u} [Fintype S]
    (V : S → ℚ) (C : Finset ℚ)
    (hcover : ValueCenterCover V 0 C) :
    Finset.univ.image V ⊆ C := by
  intro x hx
  obtain ⟨s, -, rfl⟩ := Finset.mem_image.mp hx
  obtain ⟨c, hc, hdist⟩ := hcover s
  have heq : V s = c := by
    have : |V s - c| = 0 := le_antisymm hdist (abs_nonneg _)
    exact sub_eq_zero.mp (abs_eq_zero.mp this)
  simpa [heq] using hc

/-- Zero distortion has a closed form: the minimum context cardinality is
exactly the number of distinct scalar values. -/
theorem exactValueCodeNumber_zero_eq_distinct_value_card
    {S : Type u} [Fintype S]
    (V : S → ℚ) :
    exactValueCodeNumber V 0 (by norm_num) = (Finset.univ.image V).card := by
  apply le_antisymm
  · exact exactValueCodeNumber_le_distinct_value_card V 0 (by norm_num)
  · obtain ⟨C, hcover, hcard⟩ :=
      exactValueCodeNumber_spec V 0 (by norm_num)
    have hsub := raw_values_subset_zero_centerCover V C hcover
    have hle := Finset.card_le_card hsub
    simpa [hcard] using hle

/-- A single explicit reconstruction center yields a one-symbol upper bound. -/
theorem exactValueCodeNumber_le_one_of_center
    {S : Type u} [Fintype S]
    (V : S → ℚ) (η : ℚ) (hη : 0 ≤ η) (c : ℚ)
    (hc : ∀ s, |V s - c| ≤ η) :
    exactValueCodeNumber V η hη ≤ 1 := by
  let C : Finset ℚ := {c}
  have hcover : ValueCenterCover V η C := by
    intro s
    exact ⟨c, by simp [C], hc s⟩
  simpa [C] using exactValueCodeNumber_le_cover_card V η hη C hcover

end Komorebi.AVOC

namespace Komorebi.AVOC

universe u

/-- Any center cover of a nonempty state space is itself nonempty. -/
theorem valueCenterCover_nonempty
    {S : Type u} [Nonempty S]
    (V : S → ℚ) (η : ℚ) (C : Finset ℚ)
    (hcover : ValueCenterCover V η C) :
    C.Nonempty := by
  let s : S := Classical.choice ‹Nonempty S›
  obtain ⟨c, hc, -⟩ := hcover s
  exact ⟨c, hc⟩

/-- Every nonempty value problem needs at least one finite context symbol. -/
theorem exactValueCodeNumber_pos
    {S : Type u} [Fintype S] [Nonempty S]
    (V : S → ℚ) (η : ℚ) (hη : 0 ≤ η) :
    0 < exactValueCodeNumber V η hη := by
  obtain ⟨C, hcover, hcard⟩ := exactValueCodeNumber_spec V η hη
  have hC : 0 < C.card := Finset.card_pos.mpr (valueCenterCover_nonempty V η C hcover)
  simpa [hcard] using hC

/-- On a nonempty state space, an explicit one-center cover proves that the
exact code number is exactly one. -/
theorem exactValueCodeNumber_eq_one_of_center
    {S : Type u} [Fintype S] [Nonempty S]
    (V : S → ℚ) (η : ℚ) (hη : 0 ≤ η) (c : ℚ)
    (hc : ∀ s, |V s - c| ≤ η) :
    exactValueCodeNumber V η hη = 1 := by
  apply le_antisymm
  · exact exactValueCodeNumber_le_one_of_center V η hη c hc
  · exact Nat.succ_le_iff.mpr (exactValueCodeNumber_pos V η hη)

end Komorebi.AVOC

namespace Komorebi.AVOC

universe u

/-- The earlier pairwise-packing lower bound applies directly to the exact
minimum code number. -/
theorem separated_card_le_exactValueCodeNumber
    {S : Type u} [Fintype S] [DecidableEq S]
    (V : S → ℚ) (η : ℚ) (hη : 0 ≤ η)
    (K : Finset S) (hsep : PairwiseValueSeparated V η K) :
    K.card ≤ exactValueCodeNumber V η hη := by
  obtain ⟨C, hcard, φ, happrox⟩ :=
    exactValueCodeNumber_attained_by_context V η hη
  have h := separated_card_le_code_card φ V
    (fun z : {c // c ∈ C} => (z : ℚ)) η K happrox hsep
  simpa [hcard] using h

end Komorebi.AVOC
