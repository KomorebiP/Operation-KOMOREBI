import AVOC.ExactRateDistortion
import Mathlib.Data.Finset.Max
import Mathlib.Data.Nat.Find
import Mathlib.Tactic.Linarith

namespace Komorebi.AVOC

/-- A finite set of scalar points is covered at radius `η` by a finite set of
reconstruction centers. -/
def PointCenterCover (η : ℚ) (P C : Finset ℚ) : Prop :=
  ∀ x ∈ P, ∃ c ∈ C, |x - c| ≤ η

/-- Using each point as its own center always covers at nonnegative radius. -/
theorem pointCenterCover_self
    (η : ℚ) (hη : 0 ≤ η) (P : Finset ℚ) :
    PointCenterCover η P P := by
  intro x hx
  exact ⟨x, hx, by simpa using hη⟩

/-- A point-center cover with exactly `k` centers. -/
def HasPointCenterCoverCard (η : ℚ) (P : Finset ℚ) (k : ℕ) : Prop :=
  ∃ C : Finset ℚ, PointCenterCover η P C ∧ C.card = k

/-- A finite point set always has some finite cover cardinality at nonnegative
radius. -/
theorem exists_pointCenterCover_card
    (η : ℚ) (hη : 0 ≤ η) (P : Finset ℚ) :
    ∃ k, HasPointCenterCoverCard η P k := by
  exact ⟨P.card, P, pointCenterCover_self η hη P, rfl⟩

/-- Exact minimum number of radius-`η` intervals/centers needed to cover a
finite set of rational points. -/
noncomputable def pointCoverNumber
    (η : ℚ) (hη : 0 ≤ η) (P : Finset ℚ) : ℕ := by
  classical
  exact Nat.find (exists_pointCenterCover_card η hη P)

/-- The minimum point cover is attained. -/
theorem pointCoverNumber_spec
    (η : ℚ) (hη : 0 ≤ η) (P : Finset ℚ) :
    HasPointCenterCoverCard η P (pointCoverNumber η hη P) := by
  classical
  simpa [pointCoverNumber] using
    (Nat.find_spec (exists_pointCenterCover_card η hη P))

/-- The minimum point-cover number is no larger than any explicit cover. -/
theorem pointCoverNumber_le_cover_card
    (η : ℚ) (hη : 0 ≤ η) (P C : Finset ℚ)
    (hcover : PointCenterCover η P C) :
    pointCoverNumber η hη P ≤ C.card := by
  classical
  unfold pointCoverNumber
  exact Nat.find_min' (exists_pointCenterCover_card η hη P) ⟨C, hcover, rfl⟩

/-- The residual after the canonical greedy interval centered at `min(P)+η`:
all points strictly to the right of `min(P)+2η`. -/
def greedyResidual
    (η : ℚ) (P : Finset ℚ) (hP : P.Nonempty) : Finset ℚ :=
  P.filter (fun x => P.min' hP + 2 * η < x)

/-- Every point retained by the greedy first interval lies within radius `η`
of the canonical center `min(P)+η`. -/
theorem greedy_center_covers_nonresidual
    (η : ℚ) (P : Finset ℚ) (hP : P.Nonempty)
    {x : ℚ} (hxP : x ∈ P)
    (hx : ¬ P.min' hP + 2 * η < x) :
    |x - (P.min' hP + η)| ≤ η := by
  have hmin : P.min' hP ≤ x := Finset.min'_le P x hxP
  have hmax : x ≤ P.min' hP + 2 * η := le_of_not_gt hx
  rw [abs_le]
  constructor <;> linarith

/-- A center that covers the leftmost point cannot cover any point in the
greedy residual. -/
theorem center_covering_min_excludes_residual
    (η : ℚ) (P : Finset ℚ) (hP : P.Nonempty)
    {c x : ℚ}
    (hminc : |P.min' hP - c| ≤ η)
    (hxR : x ∈ greedyResidual η P hP) :
    ¬ |x - c| ≤ η := by
  intro hxc
  have hxgt : P.min' hP + 2 * η < x := (Finset.mem_filter.mp hxR).2
  have hminbounds := (abs_le.mp hminc)
  have hxbounds := (abs_le.mp hxc)
  linarith

/-- If `c` is a center covering the leftmost point, then deleting `c` leaves a
valid cover of the greedy residual. -/
theorem erase_min_center_covers_residual
    (η : ℚ) (P C : Finset ℚ) (hP : P.Nonempty)
    (hcover : PointCenterCover η P C)
    {c : ℚ}
    (hminc : |P.min' hP - c| ≤ η) :
    PointCenterCover η (greedyResidual η P hP) (C.erase c) := by
  intro x hxR
  have hxP : x ∈ P := (Finset.mem_filter.mp hxR).1
  obtain ⟨d, hdC, hxd⟩ := hcover x hxP
  have hdc : d ≠ c := by
    intro hEq
    subst d
    exact center_covering_min_excludes_residual η P hP hminc hxR hxd
  exact ⟨d, Finset.mem_erase.mpr ⟨hdc, hdC⟩, hxd⟩

/-- Any cover of the greedy residual extends to a cover of the whole point set
by inserting the canonical greedy center `min(P)+η`. -/
theorem insert_greedy_center_covers
    (η : ℚ) (P D : Finset ℚ) (hP : P.Nonempty)
    (hres : PointCenterCover η (greedyResidual η P hP) D) :
    PointCenterCover η P (insert (P.min' hP + η) D) := by
  intro x hxP
  by_cases hxR : x ∈ greedyResidual η P hP
  · obtain ⟨d, hdD, hxd⟩ := hres x hxR
    exact ⟨d, Finset.mem_insert_of_mem hdD, hxd⟩
  · have hnot : ¬ P.min' hP + 2 * η < x := by
      intro hgt
      exact hxR (Finset.mem_filter.mpr ⟨hxP, hgt⟩)
    exact ⟨P.min' hP + η, Finset.mem_insert_self _ _,
      greedy_center_covers_nonresidual η P hP hxP hnot⟩

/-- Lower half of greedy optimality: every cover of a nonempty point set must
pay for the leftmost cluster plus enough centers to cover the residual. -/
theorem one_add_residual_coverNumber_le
    (η : ℚ) (hη : 0 ≤ η) (P : Finset ℚ) (hP : P.Nonempty) :
    1 + pointCoverNumber η hη (greedyResidual η P hP) ≤
      pointCoverNumber η hη P := by
  obtain ⟨C, hcover, hcard⟩ := pointCoverNumber_spec η hη P
  have hminMem : P.min' hP ∈ P := P.min'_mem hP
  obtain ⟨c, hcC, hminc⟩ := hcover (P.min' hP) hminMem
  have hresCover := erase_min_center_covers_residual η P C hP hcover hminc
  have hresMin := pointCoverNumber_le_cover_card
    η hη (greedyResidual η P hP) (C.erase c) hresCover
  have hcardErase : (C.erase c).card + 1 = C.card := Finset.card_erase_add_one hcC
  omega

/-- Upper half of greedy optimality: an optimal residual cover plus the
canonical leftmost greedy center covers the whole point set. -/
theorem coverNumber_le_one_add_residual
    (η : ℚ) (hη : 0 ≤ η) (P : Finset ℚ) (hP : P.Nonempty) :
    pointCoverNumber η hη P ≤
      1 + pointCoverNumber η hη (greedyResidual η P hP) := by
  obtain ⟨D, hresCover, hDcard⟩ :=
    pointCoverNumber_spec η hη (greedyResidual η P hP)
  have hwhole := insert_greedy_center_covers η P D hP hresCover
  have hmin := pointCoverNumber_le_cover_card η hη P
    (insert (P.min' hP + η) D) hwhole
  have hcard := Finset.card_insert_le (P.min' hP + η) D
  omega

/-- Exact one-dimensional greedy recurrence. Choosing the leftmost uncovered
point, placing a center at `min(P)+η`, deleting all points through
`min(P)+2η`, and recursing is globally cardinality-optimal. -/
theorem pointCoverNumber_greedy_recurrence
    (η : ℚ) (hη : 0 ≤ η) (P : Finset ℚ) (hP : P.Nonempty) :
    pointCoverNumber η hη P =
      1 + pointCoverNumber η hη (greedyResidual η P hP) := by
  apply le_antisymm
  · exact coverNumber_le_one_add_residual η hη P hP
  · exact one_add_residual_coverNumber_le η hη P hP

end Komorebi.AVOC

namespace Komorebi.AVOC

/-- A value-function center cover is exactly a point cover of its finite set of
distinct values. -/
theorem valueCenterCover_iff_pointCenterCover_image
    {S : Type*} [Fintype S]
    (V : S → ℚ) (η : ℚ) (C : Finset ℚ) :
    ValueCenterCover V η C ↔
      PointCenterCover η (Finset.univ.image V) C := by
  constructor
  · intro h x hx
    obtain ⟨s, -, rfl⟩ := Finset.mem_image.mp hx
    exact h s
  · intro h s
    exact h (V s) (by simp)

/-- The abstract exact scalar context number equals the exact interval-cover
number of the distinct raw values. -/
theorem exactValueCodeNumber_eq_pointCoverNumber
    {S : Type*} [Fintype S]
    (V : S → ℚ) (η : ℚ) (hη : 0 ≤ η) :
    exactValueCodeNumber V η hη =
      pointCoverNumber η hη (Finset.univ.image V) := by
  apply le_antisymm
  · obtain ⟨C, hcoverP, hcard⟩ :=
      pointCoverNumber_spec η hη (Finset.univ.image V)
    have hcoverV : ValueCenterCover V η C :=
      (valueCenterCover_iff_pointCenterCover_image V η C).2 hcoverP
    calc
      exactValueCodeNumber V η hη ≤ C.card :=
        exactValueCodeNumber_le_cover_card V η hη C hcoverV
      _ = pointCoverNumber η hη (Finset.univ.image V) := hcard
  · obtain ⟨C, hcoverV, hcard⟩ := exactValueCodeNumber_spec V η hη
    have hcoverP : PointCenterCover η (Finset.univ.image V) C :=
      (valueCenterCover_iff_pointCenterCover_image V η C).1 hcoverV
    calc
      pointCoverNumber η hη (Finset.univ.image V) ≤ C.card :=
        pointCoverNumber_le_cover_card η hη (Finset.univ.image V) C hcoverP
      _ = exactValueCodeNumber V η hη := hcard

/-- The greedy residual is a strict subset whenever the input point set is
nonempty and the radius is nonnegative. -/
theorem greedyResidual_ssubset
    (η : ℚ) (hη : 0 ≤ η) (P : Finset ℚ) (hP : P.Nonempty) :
    greedyResidual η P hP ⊂ P := by
  rw [Finset.ssubset_iff_subset_ne]
  constructor
  · exact Finset.filter_subset _ _
  · intro heq
    have hminR : P.min' hP ∈ greedyResidual η P hP := by
      rw [heq]
      exact P.min'_mem hP
    have hgt := (Finset.mem_filter.mp hminR).2
    linarith

/-- The greedy residual has strictly smaller cardinality. -/
theorem greedyResidual_card_lt
    (η : ℚ) (hη : 0 ≤ η) (P : Finset ℚ) (hP : P.Nonempty) :
    (greedyResidual η P hP).card < P.card :=
  Finset.card_lt_card (greedyResidual_ssubset η hη P hP)

/-- The exact cover number of the empty point set is zero. -/
theorem pointCoverNumber_empty
    (η : ℚ) (hη : 0 ≤ η) :
    pointCoverNumber η hη ∅ = 0 := by
  apply Nat.eq_zero_of_le_zero
  exact pointCoverNumber_le_cover_card η hη ∅ ∅ (by
    intro x hx
    simp at hx)

/-- Recursive greedy cover count: select the leftmost uncovered point, place a
center `η` to its right, delete the covered prefix, and repeat. -/
noncomputable def greedyPointCoverCount
    (η : ℚ) (hη : 0 ≤ η) (P : Finset ℚ) : ℕ :=
  if hP : P.Nonempty then
    1 + greedyPointCoverCount η hη (greedyResidual η P hP)
  else 0
termination_by P.card
decreasing_by
  exact greedyResidual_card_lt η hη P hP

/-- The recursive greedy algorithm computes the exact minimum interval-cover
cardinality. -/
theorem greedyPointCoverCount_eq_pointCoverNumber
    (η : ℚ) (hη : 0 ≤ η) (P : Finset ℚ) :
    greedyPointCoverCount η hη P = pointCoverNumber η hη P := by
  induction P using Finset.strongInductionOn with
  | _ P ih =>
      by_cases hP : P.Nonempty
      · rw [greedyPointCoverCount]
        simp only [hP, ↓reduceDIte]
        rw [ih (greedyResidual η P hP) (greedyResidual_ssubset η hη P hP)]
        exact (pointCoverNumber_greedy_recurrence η hη P hP).symm
      · have hEmpty : P = ∅ := Finset.not_nonempty_iff_eq_empty.mp hP
        subst P
        simp [greedyPointCoverCount, pointCoverNumber_empty η hη]

/-- Therefore the greedy interval algorithm computes the exact minimum scalar
context cardinality for any finite value function. -/
theorem greedy_computes_exactValueCodeNumber
    {S : Type*} [Fintype S]
    (V : S → ℚ) (η : ℚ) (hη : 0 ≤ η) :
    greedyPointCoverCount η hη (Finset.univ.image V) =
      exactValueCodeNumber V η hη := by
  rw [greedyPointCoverCount_eq_pointCoverNumber]
  exact (exactValueCodeNumber_eq_pointCoverNumber V η hη).symm

end Komorebi.AVOC
