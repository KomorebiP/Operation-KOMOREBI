import PaperX.DirectedSeeds
import Mathlib.Tactic

/-! Consequences of actual directed reachability; no arithmetic transport is postulated. -/
set_option autoImplicit false
namespace PaperX.SeedConsequences

open PaperX.DirectedSeeds
universe u
variable {V : Type u} (E : V → V → Prop)

/-- Any choice of one representative of each source component is optimal. -/
theorem arbitrary_representatives [Finite V] (s : Source E → V)
    (hs : ∀ c, component E (s c) = c.val) :
    ∃ S : Finset V, (∀ v, v ∈ S ↔ ∃ c, s c = v) ∧ Covers E S ∧
      S.card = seedRank E := by
  classical
  let S := Finset.univ.image s
  have hinj : Function.Injective s := by
    intro a b hab
    apply Subtype.ext
    exact (hs a).symm.trans ((congrArg (component E) hab).trans (hs b))
  refine ⟨S, ?_, ?_, ?_⟩
  · intro v
    simp [S]
  · apply (covers_iff_meets_sources E S).2
    intro c
    exact ⟨s c, Finset.mem_image.mpr ⟨c, Finset.mem_univ c, rfl⟩, hs c⟩
  · rw [directed_minimum_seed]
    simp [S, Finset.card_image_of_injective _ hinj, Nat.card_eq_fintype_card]

/-- No new admissible edges can increase the minimum number of seeds. -/
theorem seedRank_antitone [Finite V] (F : V → V → Prop)
    (hEF : ∀ a b, E a b → F a b) : seedRank F ≤ seedRank E := by
  obtain ⟨S, hS, hcard⟩ := seedRank_realized E
  rw [← hcard]
  apply seedRank_le F S
  intro v
  obtain ⟨s, hs, hsv⟩ := hS v
  exact ⟨s, hs, Relation.ReflTransGen.mono hEF s v hsv⟩

/-- Directed transport preserves a supplied property only when every edge does. -/
theorem transfer_along_path (P : V → Prop)
    (hP : ∀ a b, E a b → P a → P b) {a b : V} (h : Reach E a b) :
    P a → P b := by
  induction h with
  | refl => exact id
  | @tail b c _ hbc ih => exact fun ha => hP b c hbc (ih ha)

theorem transfer_from_seeds (P : V → Prop)
    (hP : ∀ a b, E a b → P a → P b) (S : Finset V)
    (hcover : Covers E S) (hseed : ∀ s ∈ S, P s) : ∀ v, P v := by
  intro v
  obtain ⟨s, hs, hsv⟩ := hcover v
  exact transfer_along_path E P hP hsv (hseed s hs)

/-- A finite graph has rank zero precisely when it has no vertices. -/
theorem rank_zero_iff [Finite V] : seedRank E = 0 ↔ IsEmpty V := by
  classical
  constructor
  · intro h
    obtain ⟨S, hS, hc⟩ := seedRank_realized E
    have hnil : S = ∅ := Finset.card_eq_zero.mp (hc.trans h)
    refine ⟨fun v => ?_⟩
    obtain ⟨s, hs, _⟩ := hS v
    simp [hnil] at hs
  · intro h
    let : IsEmpty V := h
    apply Nat.eq_zero_of_le_zero
    simpa using seedRank_le E ∅ (fun v => isEmptyElim v)

/-- One universal seed exists exactly when the independently minimized rank is one. -/
theorem rank_one_iff [Finite V] :
    seedRank E = 1 ↔ ∃ s : V, ∀ v, Reach E s v := by
  classical
  constructor
  · intro h
    obtain ⟨S, hS, hc⟩ := seedRank_realized E
    obtain ⟨s, rfl⟩ := Finset.card_eq_one.mp (hc.trans h)
    refine ⟨s, fun v => ?_⟩
    obtain ⟨t, ht, htv⟩ := hS v
    have hts : t = s := Finset.mem_singleton.mp ht
    exact hts ▸ htv
  · rintro ⟨s, hs⟩
    have hupper : seedRank E ≤ 1 := by
      simpa using seedRank_le E {s} (fun v => ⟨s, by simp, hs v⟩)
    have hnonzero : seedRank E ≠ 0 := by
      intro hzero
      exact ((rank_zero_iff E).1 hzero).false s
    omega

theorem one_source_iff_universal_seed [Finite V] :
    Nat.card (Source E) = 1 ↔ ∃ s : V, ∀ v, Reach E s v := by
  rw [← directed_minimum_seed, rank_one_iff]

end PaperX.SeedConsequences
