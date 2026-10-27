import KomorebiVerification.PacketNaturalityCompletion

set_option autoImplicit false
set_option maxHeartbeats 2000000

namespace Komorebi.PaperIRelease
open Komorebi.Foundation

universe u v w
variable {K : Type u} [Field K]
variable {X : Type v} [AddCommGroup X] [Module K X]
variable {I : Type w} [Fintype I]

/-- Lists are written in composition order: the rightmost operator acts first. -/
def operatorWord : List (Module.End K X) → Module.End K X
  | [] => 1
  | T :: ts => T.comp (operatorWord ts)

/-- Recursive expansion over all intermediate packet indices for a nonidentical word. -/
noncomputable def packetWordSum (P : LinearProjectorFamily K X I) :
    List (Module.End K X) → I → I → Module.End K X
  | [], b, a => transferBlock P P 1 b a
  | T :: ts, b, a => ∑ c, (transferBlock P P T b c).comp (packetWordSum P ts c a)

theorem transferBlock_word (P : LinearProjectorFamily K X I)
    (ts : List (Module.End K X)) (b a : I) :
    transferBlock P P (operatorWord ts) b a = packetWordSum P ts b a := by
  induction ts generalizing b a with
  | nil => rfl
  | cons T ts ih =>
    simp only [operatorWord, packetWordSum, transferBlock_comp_end, ih]

def packetSupport (P : LinearProjectorFamily K X I) (x : X) : Set I :=
  {i | P.proj i x ≠ 0}

def PacketPure (P : LinearProjectorFamily K X I) (x : X) : Prop :=
  (packetSupport P x).Subsingleton

/-- Zero vectors have empty support and are packet pure. -/
theorem packetPure_zero (P : LinearProjectorFamily K X I) : PacketPure P (0 : X) := by
  intro a ha
  exact (ha (map_zero _)).elim

/-- A vector in one projector range has no other packet component. -/
theorem packetPure_of_mem_range (P : LinearProjectorFamily K X I) {i : I} {x : X}
    (hx : x ∈ LinearMap.range (P.proj i)) : PacketPure P x := by
  rintro a ha b hb
  obtain ⟨y, rfl⟩ := hx
  have hai : a = i := by
    by_contra h
    exact ha (P.orthogonal h y)
  have hbi : b = i := by
    by_contra h
    exact hb (P.orthogonal h y)
  exact hai.trans hbi.symm

/-- Nonzero packet-pure vectors belong to their unique active packet. -/
theorem packetPure_mem_range (P : LinearProjectorFamily K X I) {x : X}
    (hx : PacketPure P x) {i : I} (hi : i ∈ packetSupport P x) :
    x ∈ LinearMap.range (P.proj i) := by
  classical
  have heq : x = P.proj i x := by
    calc
      x = ∑ j, P.proj j x := (P.complete x).symm
      _ = P.proj i x := by
        apply Finset.sum_eq_single i
        · intro j _ hji
          by_contra hj
          exact hji (hx hj hi)
        · simp
  exact ⟨x, heq.symm⟩

/-- Packet purity is exactly zero or membership in one actual packet range. -/
theorem packetPure_iff_zero_or_range (P : LinearProjectorFamily K X I) (x : X) :
    PacketPure P x ↔ x = 0 ∨ ∃ i, x ∈ LinearMap.range (P.proj i) := by
  classical
  constructor
  · intro hx
    by_cases h : ∃ i, P.proj i x ≠ 0
    · obtain ⟨i, hi⟩ := h
      exact Or.inr ⟨i, packetPure_mem_range P hx hi⟩
    · left
      apply P.eq_of_projectors_eq
      intro i
      have hi : P.proj i x = 0 := by by_contra hi; exact h ⟨i, hi⟩
      simpa only [map_zero] using hi
  · rintro (rfl | ⟨i, hi⟩)
    · exact packetPure_zero P
    · exact packetPure_of_mem_range P hi

def activeTargets (P : LinearProjectorFamily K X I) (T : Module.End K X) (x : X) : Set I :=
  {b | ∃ a, a ∈ packetSupport P x ∧ transferBlock P P T b a ≠ 0}

/-- Each target coordinate is the exact sum of source-coordinate contributions. -/
theorem target_coordinate_sum (P : LinearProjectorFamily K X I)
    (T : Module.End K X) (x : X) (b : I) :
    P.proj b (T x) = ∑ a, transferBlock P P T b a (P.proj a x) := by
  simp only [transferBlock, LinearMap.comp_apply, P.idempotent]
  rw [← map_sum, ← map_sum, P.complete]

theorem packetSupport_image_subset (P : LinearProjectorFamily K X I)
    (T : Module.End K X) (x : X) :
    packetSupport P (T x) ⊆ activeTargets P T x := by
  intro b hb
  by_contra h
  apply hb
  rw [target_coordinate_sum]
  apply Finset.sum_eq_zero
  intro a _
  by_cases ha : a ∈ packetSupport P x
  · have hzero : transferBlock P P T b a = 0 := by
      by_contra hne
      exact h ⟨a, ha, hne⟩
    rw [hzero, LinearMap.zero_apply]
  · have hzero : P.proj a x = 0 := not_not.mp ha
    rw [hzero, map_zero]

noncomputable def activeSources (P : LinearProjectorFamily K X I)
    (T : Module.End K X) (x : X) (b : I) : Finset I := by
  classical
  exact Finset.univ.filter (fun a => P.proj a x ≠ 0 ∧ transferBlock P P T b a ≠ 0)

theorem target_coordinate_active_sum (P : LinearProjectorFamily K X I)
    (T : Module.End K X) (x : X) (b : I) :
    P.proj b (T x) =
      ∑ a ∈ activeSources P T x b, transferBlock P P T b a (P.proj a x) := by
  classical
  rw [target_coordinate_sum]
  symm
  apply Finset.sum_subset (Finset.subset_univ _)
  intro a _ ha
  have hn : ¬ (P.proj a x ≠ 0 ∧ transferBlock P P T b a ≠ 0) := by
    simpa only [activeSources, Finset.mem_filter, Finset.mem_univ, true_and] using ha
  by_cases hx : P.proj a x = 0
  · rw [hx, map_zero]
  · have hzero : transferBlock P P T b a = 0 := by tauto
    rw [hzero, LinearMap.zero_apply]

/-- Equality holds precisely under the stated no-cancellation condition at each active target. -/
theorem packetSupport_image_eq_of_noncancellation (P : LinearProjectorFamily K X I)
    (T : Module.End K X) (x : X)
    (h : ∀ b ∈ activeTargets P T x,
      (∑ a ∈ activeSources P T x b, transferBlock P P T b a (P.proj a x)) ≠ 0) :
    packetSupport P (T x) = activeTargets P T x := by
  apply Set.Subset.antisymm (packetSupport_image_subset P T x)
  intro b hb
  change P.proj b (T x) ≠ 0
  rw [target_coordinate_active_sum]
  exact h b hb

/-- At most one active source with nonzero contribution is sufficient. -/
theorem packetSupport_image_eq_of_single_active (P : LinearProjectorFamily K X I)
    (T : Module.End K X) (x : X)
    (h : ∀ b ∈ activeTargets P T x, ∃ a,
      activeSources P T x b = {a} ∧ transferBlock P P T b a (P.proj a x) ≠ 0) :
    packetSupport P (T x) = activeTargets P T x := by
  classical
  apply packetSupport_image_eq_of_noncancellation
  intro b hb
  obtain ⟨a, ha, hne⟩ := h b hb
  simpa [ha] using hne

end Komorebi.PaperIRelease
